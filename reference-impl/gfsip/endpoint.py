"""GFSIP/1.0 Endpoint — integrated reference node (Sections 10-19, 27).

Wires together the frame codec, state machine, channel manager,
authentication, dedupe store, resume service, audit log and federation
registry into one runnable node. Uses the synchronous in-memory Link
transport; production swaps the transport for a QUIC adapter.
"""

import hashlib
import json
import os
import time
import uuid

from .types import (
    MAGIC, FRAME_HEADER_SIZE, CONTROL_CHANNEL,
    MessageType, SessionState, ErrorCode, FrameFlag, Profile,
)
from .frame import GfsipFrame, FrameDecodeError
from .state_machine import Session, TransitionRejected
from .channel import ChannelManager, Channel, ChannelError, ChannelState
from .auth import Authenticator, AuthMethod, AuthError
from .dedupe import DedupeStore, DedupeOutcome
from .resume import ResumeService, ResumeError
from .audit import AuditLog, AuditEvent, AuditError
from .federation import FederationRegistry, FederationError, DomainDescriptor
from .transport import Link
from .cbor_utils import encode_deterministic
from .signing import TrustAnchorRegistry, key_id_for
from .business import BusinessHandler


class ProtocolError(Exception):
    """Endpoint-level rejection (sequence replay, early data, etc.)."""

    def __init__(self, code: ErrorCode, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


_DEFAULT_PROFILES = [Profile.CORE, Profile.AUDIT, Profile.FEDERATION]


class Endpoint:
    def __init__(self, *, node_id: str, domain_id: str, is_initiator: bool,
                 link: Link, shared_secret: bytes,
                 signing_key: bytes = None,
                 trust_anchors: TrustAnchorRegistry = None,
                 business_handler: BusinessHandler = None,
                 profiles: list = None, max_channels: int = 128,
                 dedupe_window: float = 3600, auth_method: AuthMethod = AuthMethod.SIGNED_TOKEN):
        self.node_id = node_id
        self.domain_id = domain_id
        self.is_initiator = is_initiator
        self.link = link
        self.shared_secret = shared_secret
        self.requested_profiles = profiles or list(_DEFAULT_PROFILES)
        self.auth_method = auth_method

        self._signing_key = signing_key
        self._business_handler = business_handler

        self.session = Session(node_id=node_id, domain_id=domain_id, max_channels=max_channels)
        self.channels = ChannelManager(is_initiator, max_channels)
        self.dedupe = DedupeStore(dedupe_window)
        self.auth = Authenticator(node_id, domain_id, signing_key, trust_anchors)
        self._resume_svc = ResumeService(shared_secret)
        self.audit = AuditLog(protocol_version="1.0", session_id=b"",
                              signing_key=signing_key)
        self.federation = FederationRegistry(domain_id, shared_secret)

        self._seq = 0
        self._peer_last_seq = 0
        self._transcript = b""
        self._peer_hello: dict = {}
        self._peer_node_id: str = ""
        self._auth_ctx_id = uuid.uuid4().hex
        self._resume_token: bytes = b""
        self._negotiated_profiles: list = []
        self._started = False
        self._client_hello_ext: dict = {}
        self._server_hello_ext: dict = {}

    # ── framing helpers ─────────────────────────────────────
    def _next_seq(self) -> int:
        self._seq += 1
        return self._seq

    def _send(self, msg_type: MessageType, *, ext: dict = None,
              payload: bytes = b"", channel_id: int = CONTROL_CHANNEL,
              flags: int = 0) -> GfsipFrame:
        sid = self.session.session_id or (b"\x00" * 16)
        frame = GfsipFrame(
            msg_type=msg_type, channel_id=channel_id, session_id=sid,
            sequence=self._next_seq(), extension_header=ext,
            payload=payload, flags=flags,
        )
        data = frame.serialize()
        self.link.send(data)
        self._transcript += data
        return frame

    def _recv_raw(self) -> tuple[GfsipFrame, bytes]:
        data = self.link.recv()
        frame = GfsipFrame.parse(data)
        return frame, data

    # ── handshake driver ────────────────────────────────────
    def handshake_with(self, peer: "Endpoint", max_iter: int = 200) -> None:
        """Run the full handshake between this endpoint and a peer (sync).

        Pumps whichever side has a pending inbound frame; a side only sends
        in response to a received frame, so draining by `pending()` avoids
        deadlock.
        """
        if self.is_initiator and not self._started:
            self._kickoff()
        for _ in range(max_iter):
            if self.session.state == SessionState.ESTABLISHED and \
               peer.session.state == SessionState.ESTABLISHED:
                # drain leftover frames (SESSION_READY, etc.)
                for ep in (peer, self):
                    while ep.link.pending():
                        ep._pump_once()
                return
            progressed = False
            for ep in (peer, self):
                if ep.link.pending():
                    ep._pump_once()
                    progressed = True
            if not progressed:
                break
        if self.session.state != SessionState.ESTABLISHED or \
           peer.session.state != SessionState.ESTABLISHED:
            raise ProtocolError(ErrorCode.INTERNAL_ERROR, "Handshake did not complete")

    def _kickoff(self) -> None:
        self._started = True
        ext = {
            "versions": ["1.0"],
            "profiles": self.requested_profiles,
            "compressions": ["none", "zstd"],
            "auth_methods": [self.auth_method.value],
            "node_id": self.node_id,
            "domain_id": self.domain_id,
            "max_header": 65535,
            "max_frame": 1048576,
            "max_channels": self.session.max_channels,
            "dedupe_window_seconds": int(self.dedupe.window_seconds),
            "nonce": os.urandom(32),
        }
        self._client_hello_ext = ext
        self.session.transition(MessageType.CLIENT_HELLO)
        self._send(MessageType.CLIENT_HELLO, ext=ext)

    def _pump_once(self) -> None:
        if self.is_initiator and not self._started:
            self._kickoff()
            return
        frame, raw = self._recv_raw()
        self._transcript += raw
        self._handle(frame, self._transcript[:-len(raw)])

    def _negotiation_transcript_bytes(self) -> bytes:
        """Symmetric transcript: canonical CBOR of both HELLO messages."""
        ch = self._client_hello_ext or {}
        sh = self._server_hello_ext or {}
        return encode_deterministic(ch) + encode_deterministic(sh)

    # ── message handler ─────────────────────────────────────
    def _handle(self, frame: GfsipFrame, pre_transcript: bytes) -> None:
        mt = frame.msg_type
        ext = frame.extension_header or {}

        # Sequence replay guard (Sections 8.2, 23)
        if mt in (MessageType.DATA, MessageType.APP_ACK):
            if frame.sequence <= self._peer_last_seq:
                raise ProtocolError(ErrorCode.SEQUENCE_REPLAY,
                                    f"Stale/duplicate sequence {frame.sequence}")
            self._peer_last_seq = frame.sequence

        # Early-data guard (Section 23): side effects rejected under EARLY_DATA
        if frame.has_flag(FrameFlag.EARLY_DATA) and mt in (
            MessageType.DATA, MessageType.EVENT, MessageType.ROUTE_QUERY
        ):
            raise ProtocolError(ErrorCode.EARLY_DATA_REJECTED,
                                "Side-effect under EARLY_DATA")

        if mt == MessageType.CLIENT_HELLO:
            self._on_client_hello(ext)
        elif mt == MessageType.SERVER_HELLO:
            self._on_server_hello(ext)
        elif mt == MessageType.AUTH:
            self._on_auth(ext, pre_transcript)
        elif mt == MessageType.AUTH_RESULT:
            self._on_auth_result(ext)
        elif mt == MessageType.SESSION_READY:
            self._on_session_ready(ext)
        elif mt == MessageType.OPEN_CHANNEL:
            self._on_open_channel(ext)
        elif mt == MessageType.CHANNEL_READY:
            self.channels.mark_ready(ext.get("channel_id", frame.channel_id))
        elif mt == MessageType.DATA:
            self._on_data(frame)
        elif mt == MessageType.RESUME:
            self._on_resume(ext)
        elif mt == MessageType.RESUME_RESULT:
            self._on_resume_result(ext)
        elif mt == MessageType.ERROR:
            self.session.transition(MessageType.ERROR,
                                    context={"fatal": ext.get("fatal", True)})
        # PING/PONG/GOAWAY/CAPABILITY_UPDATE handled by caller as needed

    # ── handshake steps ─────────────────────────────────────
    def _on_client_hello(self, ext: dict) -> None:
        self.session.transition(MessageType.CLIENT_HELLO)
        self._peer_hello = ext
        self._peer_node_id = ext["node_id"]
        self._client_hello_ext = ext
        self._send_server_hello()

    def _send_server_hello(self) -> None:
        peer = self._peer_hello
        common_version = "1.0" if "1.0" in peer.get("versions", []) else None
        if not common_version:
            raise ProtocolError(ErrorCode.VERSION_UNSUPPORTED, "No common version")
        sel_profiles = [p for p in _DEFAULT_PROFILES
                        if p in peer.get("profiles", [])]
        self._negotiated_profiles = sel_profiles
        ext = {
            "selected_version": common_version,
            "selected_profiles": sel_profiles,
            "selected_compression": "none",
            "selected_auth_method": self.auth_method.value,
            "node_id": self.node_id,
            "domain_id": self.domain_id,
            "max_header": 32768,
            "max_frame": 524288,
            "max_channels": min(self.session.max_channels, peer.get("max_channels", 128)),
            "dedupe_window_seconds": min(int(self.dedupe.window_seconds),
                                         peer.get("dedupe_window_seconds", 3600)),
            "nonce": os.urandom(32),
        }
        self._server_hello_ext = ext
        self.session.transition(MessageType.SERVER_HELLO, context={"version_matched": True})
        self.session.selected_version = common_version
        self.session.selected_profiles = sel_profiles
        self._send(MessageType.SERVER_HELLO, ext=ext)

    def _on_server_hello(self, ext: dict) -> None:
        if "1.0" not in ext.get("selected_version", ""):
            self.session.transition(MessageType.SERVER_HELLO, context={"version_matched": False})
            raise ProtocolError(ErrorCode.VERSION_UNSUPPORTED, "Version downgrade")
        self._peer_hello = ext
        self._peer_node_id = ext["node_id"]
        self._negotiated_profiles = ext.get("selected_profiles", [])
        self._server_hello_ext = ext
        self.session.transition(MessageType.SERVER_HELLO, context={"version_matched": True})
        self.session.selected_version = ext["selected_version"]
        self.session.selected_profiles = self._negotiated_profiles
        # Initiator sends its AUTH proof
        self._send_auth()

    def _send_auth(self) -> None:
        proof = self.auth.make_proof(self.auth_method,
                                     key_id=key_id_for(self.node_id),
                                     transcript=self._negotiation_transcript_bytes())
        ext = {
            "method": proof.method,
            "credential": proof.credential,
            "proof": proof.proof,
            "key_id": proof.key_id,
            "expires_at": proof.expires_at,
            "transcript_hash": proof.transcript_hash,
        }
        self._send(MessageType.AUTH, ext=ext)

    def _on_auth(self, ext: dict, pre_transcript: bytes) -> None:
        proof = type('P', (), {
            'method': ext["method"], 'credential': ext["credential"],
            'proof': ext["proof"], 'key_id': ext["key_id"],
            'expires_at': ext["expires_at"], 'transcript_hash': ext["transcript_hash"],
        })()
        try:
            self.auth.verify(proof, self._peer_node_id, self._negotiation_transcript_bytes())
        except AuthError as e:
            self.session.transition(MessageType.AUTH_RESULT, context={"auth_success": False})
            raise ProtocolError(e.code, e.detail)
        if self.is_initiator:
            # initiator replies with its own AUTH_RESULT
            self._send(MessageType.AUTH_RESULT, ext={"success": True})
        else:
            # responder sends its AUTH proof, then AUTH_RESULT, then SESSION_READY
            self._send_auth()
            self._send(MessageType.AUTH_RESULT, ext={"success": True})
            self.session.transition(MessageType.AUTH_RESULT, context={"auth_success": True})
            self._send_session_ready()

    def _on_auth_result(self, ext: dict) -> None:
        if self.session.state == SessionState.ESTABLISHED:
            return  # late-arriving AUTH_RESULT after already established
        if ext.get("success", False):
            self.session.transition(MessageType.AUTH_RESULT, context={"auth_success": True})
        else:
            self.session.transition(MessageType.AUTH_RESULT, context={"auth_success": False})
            raise ProtocolError(ErrorCode.AUTH_FAILED, "Auth result negative")

    def _send_session_ready(self) -> None:
        sid = os.urandom(16)
        self.session.session_id = sid
        self.audit.session_id = sid
        token = self._resume_svc.issue(sid, self.node_id, self._auth_ctx_id,
                                       self.session.selected_version, self._negotiated_profiles)
        self._resume_token = token
        ext = {
            "session_id": sid.hex(),
            "resume_token": token.hex(),
            "resume_expires_at": time.time() + 1800,
            "auth_context_id": self._auth_ctx_id,
            "effective_limits": {
                "max_header": 32768,
                "max_frame": 524288,
                "max_channels": self.session.max_channels,
                "dedupe_window_seconds": int(self.dedupe.window_seconds),
            },
        }
        self._send(MessageType.SESSION_READY, ext=ext)

    def _on_session_ready(self, ext: dict) -> None:
        self.session.session_id = bytes.fromhex(ext["session_id"])
        self._resume_token = bytes.fromhex(ext["resume_token"])
        self.audit.session_id = self.session.session_id
        self._auth_ctx_id = ext.get("auth_context_id", self._auth_ctx_id)

    def _on_resume_result(self, ext: dict) -> None:
        result = ext.get("result", "rejected")
        self.session.transition(MessageType.RESUME_RESULT, context={"result": result})

    # ── channel / data ──────────────────────────────────────
    def open_channel(self, *, channel_type: str = "task", ordered: bool = True,
                     delivery: str = "application_ack", priority: int = 20,
                     max_inflight: int = 64, content_types=None, metadata=None) -> int:
        if self.session.goaway_received:
            raise ProtocolError(ErrorCode.STATE_CONFLICT, "GOAWAY already sent")
        ch = self.channels.open(channel_type=channel_type, ordered=ordered,
                                delivery=delivery, priority=priority,
                                max_inflight=max_inflight,
                                content_types=content_types, metadata=metadata)
        ext = {
            "channel_id": ch.channel_id, "channel_type": channel_type,
            "ordered": ordered, "delivery": delivery, "priority": priority,
            "max_inflight": max_inflight,
            "content_types": content_types or [], "metadata": metadata or {},
        }
        self.session.transition(MessageType.OPEN_CHANNEL)
        self._send(MessageType.OPEN_CHANNEL, ext=ext)
        return ch.channel_id

    def _on_open_channel(self, ext: dict) -> None:
        cid = ext["channel_id"]
        # Peer creates this channel: initiator -> odd, responder -> even
        if not ChannelManager.id_parity_ok(cid, not self.is_initiator):
            raise ChannelError(ErrorCode.INVALID_CHANNEL_ID,
                               f"Bad channel parity {cid} (expected {'odd' if not self.is_initiator else 'even'})")
        # responder tracks peer's channel in OPEN state
        self.channels._channels[cid] = Channel(
            channel_id=cid, channel_type=ext.get("channel_type", "message"),
            ordered=ext.get("ordered", True), delivery=ext.get("delivery", "application_ack"),
            priority=ext.get("priority", 20), max_inflight=ext.get("max_inflight", 64),
            content_types=ext.get("content_types", []), metadata=ext.get("metadata", {}),
            state=ChannelState.OPEN,
        )
        self._send(MessageType.CHANNEL_READY, ext={"channel_id": cid})

    def send_data(self, channel_id: int, *, operation: str, payload: bytes,
                  idempotency_key: str = None, content_type: str = "application/json",
                  deadline_ms: int = 5000) -> str:
        if self.session.state != SessionState.ESTABLISHED:
            raise ProtocolError(ErrorCode.STATE_CONFLICT, "Session not ESTABLISHED")
        if self.channels.get(channel_id) is None:
            raise ChannelError(ErrorCode.INVALID_CHANNEL_ID, f"Unknown channel {channel_id}")
        msg_id = str(uuid.uuid4())
        flags = 0
        if idempotency_key:
            flags |= (1 << FrameFlag.IDEMPOTENT.value)
        ext = {
            "message_id": msg_id,
            "idempotency_key": idempotency_key,
            "operation": operation,
            "content_type": content_type,
            "deadline_ms": deadline_ms,
        }
        self.session.transition(MessageType.DATA)
        self._send(MessageType.DATA, ext=ext, payload=payload,
                   channel_id=channel_id, flags=flags)
        return msg_id

    def _on_data(self, frame: GfsipFrame) -> None:
        ext = frame.extension_header or {}
        key = ext.get("idempotency_key")
        if key:
            outcome = self.dedupe.record(key)
            if outcome == DedupeOutcome.DUPLICATE:
                # already executed: echo APP_ACK with stored result
                self._send_app_ack(ext, status="duplicate")
                return
            if outcome == DedupeOutcome.IN_PROGRESS:
                self._send_app_ack(ext, status="in_progress")
                return

        operation = ext.get("operation", "")
        payload = frame.payload or b""

        if self._business_handler is not None:
            # ACCEPTED: execute the handler, derive a real, reproducible result hash
            state_before = self._business_handler.state_hash(self._business_handler.state)
            new_state, result = self._business_handler.execute(
                operation, payload, self._business_handler.state)
            self._business_handler.state = new_state
            state_after = self._business_handler.state_hash(new_state)
            result_hash = "sha256:" + hashlib.sha256(
                encode_deterministic({
                    "operation": operation,
                    "state_before": state_before,
                    "state_after": state_after,
                    "result": result,
                })
            ).hexdigest()
            self._record_audit(operation, payload, state_before, state_after)
        else:
            # No handler: hash the raw payload (deterministic, not random).
            result_hash = "sha256:" + hashlib.sha256(payload).hexdigest()

        if key:
            self.dedupe.complete(key, result_hash)
        self._send_app_ack(ext, status="accepted", result_hash=result_hash)

    def _record_audit(self, operation: str, payload: bytes,
                      state_before: str, state_after: str) -> None:
        """Record a real Audit/1 causal event for an executed side effect."""
        try:
            event = AuditEvent(
                event_id=str(uuid.uuid4()),
                parent_event_ids=[],
                actor_node_id=self.node_id,
                actor_domain_id=self.domain_id,
                event_type="data.execute",
                rule_id=operation,
                rule_version="1.0",
                state_before_hash=state_before,
                state_after_hash=state_after,
                evidence_hash="sha256:" + hashlib.sha256(payload).hexdigest(),
                result_code="OK",
                observed_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                logical_clock=self._seq,
            )
            self.audit.add(event)
        except AuditError:
            pass

    def _send_app_ack(self, ext: dict, *, status: str, result_hash: str = "") -> None:
        ack = {
            "message_id": ext.get("message_id"),
            "idempotency_key": ext.get("idempotency_key"),
            "status": status,
            "result_hash": result_hash,
            "processed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        self._send(MessageType.APP_ACK, ext=ack, channel_id=0)

    def _state_digest(self) -> str:
        """Deterministic digest of resume-relevant state (not a random placeholder)."""
        if self._business_handler is not None:
            return self._business_handler.state_hash(self._business_handler.state)
        material = encode_deterministic({
            "open_channels": self.channels.open_channels(),
            "last_sent_sequence": self._seq,
            "last_received_sequence": self._peer_last_seq,
        })
        return "sha256:" + hashlib.sha256(material).hexdigest()

    # ── recovery ────────────────────────────────────────────
    def resume(self, peer: "Endpoint") -> None:
        """Degrade and resume using the issued token (Section 16)."""
        self.session.transition(MessageType.CLIENT_HELLO, context={"path_lost": True})
        ext = {
            "session_id": self.session.session_id.hex(),
            "resume_token": self._resume_token.hex(),
            "last_received_sequence": self._peer_last_seq,
            "last_sent_sequence": self._seq,
            "open_channels": self.channels.open_channels(),
            "state_digest": self._state_digest(),
            "resume_nonce": os.urandom(32),
        }
        self.session.transition(MessageType.RESUME)
        self._send(MessageType.RESUME, ext=ext)

    def _on_resume(self, ext: dict) -> None:
        self.session.transition(MessageType.RESUME)
        token = bytes.fromhex(ext["resume_token"])
        try:
            tok = self._resume_svc.verify(token, self.node_id, self._auth_ctx_id)
            self._resume_svc.consume(tok)
        except ResumeError as e:
            self.session.transition(MessageType.RESUME_RESULT, context={"result": "rejected"})
            self._send(MessageType.RESUME_RESULT,
                       ext={"result": "rejected", "reason": e.detail})
            raise ProtocolError(e.code, e.detail)
        self.session.transition(MessageType.RESUME_RESULT, context={"result": "resumed"})
        self._send(MessageType.RESUME_RESULT, ext={"result": "resumed"})

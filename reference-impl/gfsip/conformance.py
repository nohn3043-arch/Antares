"""GFSIP/1.0 Core Conformance — minimum test vectors (Section 28).

Each vector returns (name, passed, detail). Run with `python conformance.py`.
"""

import os
import time

from .types import MessageType, SessionState, ErrorCode, FrameFlag, Profile
from .frame import GfsipFrame
from .state_machine import Session, TransitionRejected
from .channel import ChannelManager
from .dedupe import DedupeStore, DedupeOutcome
from .resume import ResumeService, ResumeError
from .audit import AuditLog, AuditEvent, AuditError
from .federation import FederationRegistry, FederationError, DomainDescriptor
from .endpoint import Endpoint, ProtocolError
from .transport import make_link_pair


def _pair(secret: bytes = b"test-secret") -> tuple:
    a, b = make_link_pair()
    init = Endpoint(node_id="urn:gfsip:node:init", domain_id="urn:gfsip:domain:a",
                    is_initiator=True, link=a, shared_secret=secret)
    resp = Endpoint(node_id="urn:gfsip:node:resp", domain_id="urn:gfsip:domain:b",
                     is_initiator=False, link=b, shared_secret=secret)
    return init, resp


def _data_frame(seq: int, sid: bytes, channel_id: int = 17) -> GfsipFrame:
    return GfsipFrame(msg_type=MessageType.DATA, channel_id=channel_id,
                      session_id=sid, sequence=seq,
                      extension_header={"message_id": "x", "operation": "op"},
                      payload=b"{}")


# ── vectors ────────────────────────────────────────────────
def v_no_common_version() -> tuple:
    s = Session()
    s.transition(MessageType.CLIENT_HELLO)
    s.transition(MessageType.SERVER_HELLO, context={"version_matched": False})
    return ("no common version -> VERSION_UNSUPPORTED",
            s.state == SessionState.CLOSED, f"state={s.state.name}")


def v_invalid_channel_parity() -> tuple:
    ok = ChannelManager.id_parity_ok(2, is_initiator=True)  # even, initiator
    return ("initiator even channel -> INVALID_CHANNEL_ID",
            ok is False, f"parity_ok={ok}")


def v_dedupe_once() -> tuple:
    d = DedupeStore(window_seconds=3600)
    assert d.record("k") == DedupeOutcome.ACCEPTED
    d.complete("k", "sha256:abc")
    again = d.record("k")
    return ("same idempotency key -> 1 side effect",
            d.count_side_effects() == 1 and again == DedupeOutcome.DUPLICATE,
            f"count={d.count_side_effects()} again={again.value}")


def v_resume_cross_node() -> tuple:
    rs = ResumeService(b"sec")
    tok = rs.issue(os.urandom(16), "urn:gfsip:node:alice", "ac1", "1.0", [Profile.CORE])
    try:
        rs.verify(tok, "urn:gfsip:node:bob", "ac1")
        return ("resume token cross-node", False, "no error raised")
    except ResumeError as e:
        return ("resume token cross-node -> RESUME_IDENTITY_MISMATCH",
                e.code == ErrorCode.RESUME_IDENTITY_MISMATCH, e.detail)


def v_sequence_replay() -> tuple:
    init, resp = _pair()
    init.handshake_with(resp)
    seq = init._peer_last_seq + 5
    init._handle(_data_frame(seq, init.session.session_id), b"")
    try:
        init._handle(_data_frame(seq, init.session.session_id), b"")
        return ("duplicate sequence -> SEQUENCE_REPLAY", False, "no error")
    except ProtocolError as e:
        return ("duplicate sequence -> SEQUENCE_REPLAY",
                e.code == ErrorCode.SEQUENCE_REPLAY, e.detail)


def v_causal_cycle() -> tuple:
    log = AuditLog(session_id=os.urandom(16))
    ev = AuditEvent(event_id="e1", parent_event_ids=["e1"])
    try:
        log.add(ev, b"key")
        return ("EVENT self-parent -> CAUSAL_CYCLE", False, "no error")
    except AuditError as e:
        return ("EVENT self-parent -> CAUSAL_CYCLE",
                e.code == ErrorCode.CAUSAL_CYCLE, e.detail)


def v_early_data_rejected() -> tuple:
    init, resp = _pair()
    init.handshake_with(resp)
    # force initiator back to AUTHENTICATING-equivalent by feeding early DATA
    init.session._state = SessionState.AUTHENTICATING
    f = _data_frame(99, b"\x00" * 16)
    f.set_flag(FrameFlag.EARLY_DATA)
    try:
        init._handle(f, b"")
        return ("0-RTT side effect -> EARLY_DATA_REJECTED", False, "no error")
    except ProtocolError as e:
        return ("0-RTT side effect -> EARLY_DATA_REJECTED",
                e.code == ErrorCode.EARLY_DATA_REJECTED, e.detail)


def v_descriptor_expired() -> tuple:
    reg = FederationRegistry("urn:gfsip:domain:a", b"sec")
    desc = DomainDescriptor(
        domain_id="urn:gfsip:domain:b", descriptor_version=1,
        valid_from=time.time() - 100, valid_until=time.time() - 10,
        signature=os.urandom(8).hex(),
    )
    try:
        reg.register(desc)
        return ("expired descriptor -> DESCRIPTOR_EXPIRED", False, "no error")
    except FederationError as e:
        return ("expired descriptor -> DESCRIPTOR_EXPIRED",
                e.code == ErrorCode.DESCRIPTOR_EXPIRED, e.detail)


def v_route_loop() -> tuple:
    reg = FederationRegistry("urn:gfsip:domain:a", b"sec")
    try:
        reg.route_query(target_domain="urn:gfsip:domain:c",
                        visited_domains=["urn:gfsip:domain:a"], max_hops=8)
        return ("visited contains self -> ROUTE_LOOP", False, "no error")
    except FederationError as e:
        return ("visited contains self -> ROUTE_LOOP",
                e.code == ErrorCode.ROUTE_LOOP, e.detail)


VECTORS = [
    v_no_common_version, v_invalid_channel_parity, v_dedupe_once,
    v_resume_cross_node, v_sequence_replay, v_causal_cycle,
    v_early_data_rejected, v_descriptor_expired, v_route_loop,
]


def run_all() -> int:
    passed = 0
    print("GFSIP/1.0 Core Conformance — Section 28 minimum test vectors\n")
    for fn in VECTORS:
        name, ok, detail = fn()
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {name}")
        if not ok:
            print(f"         -> {detail}")
        passed += ok
    total = len(VECTORS)
    print(f"\n  Result: {passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    import sys
    sys.exit(run_all())

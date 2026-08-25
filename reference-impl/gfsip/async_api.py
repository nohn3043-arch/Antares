"""GFSIP/1.0 High-Level Async API.

Wraps the synchronous reference Endpoint with an async/await interface
for application developers. Runs a background pump loop so callers never
need to invoke _pump_once() manually; send() returns the peer's APP_ACK
result; open_channel() resolves when CHANNEL_READY arrives.

Supports two transports:
  - In-memory Link pairs (testing / single-process): use connect(peer)
  - Real QUIC via QuicLink (cross-machine): use start(is_initiator=...)

This module does NOT modify the reference Endpoint source. It intercepts
frames in its own pump loop and delegates protocol handling to the
underlying Endpoint, while resolving asyncio.Future objects for
application-level concerns (APP_ACK, CHANNEL_READY).
"""

import asyncio
from typing import Optional

from .endpoint import Endpoint, ProtocolError
from .frame import GfsipFrame
from .types import MessageType, SessionState
from .channel import ChannelError


def _is_quic_link(link) -> bool:
    """Detect whether a transport object is a QuicLink (duck-typed)."""
    return hasattr(link, "send_frame") and hasattr(link, "recv_frame")


class _DummyLink:
    """Placeholder link for QUIC mode — Endpoint never calls it directly.

    All sends are intercepted via _quic_send(); receives come from QuicLink
    in the pump loop. This exists only so Endpoint.__init__ has a valid
    link attribute.
    """

    def send(self, data: bytes) -> None:
        raise RuntimeError("DummyLink.send must not be called in QUIC mode")

    def recv(self, timeout: float = 2.0) -> bytes:
        raise RuntimeError("DummyLink.recv must not be called in QUIC mode")

    def pending(self) -> bool:
        return False


class AsyncEndpoint:
    """Application-friendly async wrapper around :class:`Endpoint`.

    In-memory usage::

        from gfsip.async_api import AsyncEndpoint
        from gfsip.transport import make_link_pair
        from gfsip.signing import make_trust_pair

        a_link, b_link = make_link_pair()
        (priv_a, anchors_a), (priv_b, anchors_b) = make_trust_pair("a", "b")

        a = AsyncEndpoint(node_id="urn:gfsip:node:a", domain_id="dom:a",
                          is_initiator=True, link=a_link, shared_secret=b"x",
                          signing_key=priv_a, trust_anchors=anchors_a)
        b = AsyncEndpoint(node_id="urn:gfsip:node:b", domain_id="dom:b",
                          is_initiator=False, link=b_link, shared_secret=b"x",
                          signing_key=priv_b, trust_anchors=anchors_b,
                          business_handler=MyHandler())

        await a.connect(b)                 # handshake + start pump loops
        cid = await a.open_channel()       # waits for CHANNEL_READY
        result = await a.send(cid, operation="ping", payload=b"{}")
        await a.close()

    QUIC usage (real network)::

        from gfsip.quic_transport import quic_connect, QuicServer

        # client
        qlink = await quic_connect("127.0.0.1", 4433)
        ep = AsyncEndpoint(node_id=..., link=qlink, ...)
        await ep.start(is_initiator=True)

        # server
        server = QuicServer("0.0.0.0", 4433)
        await server.start()
        qlink = await server.accept()
        ep = AsyncEndpoint(node_id=..., link=qlink, ...)
        await ep.start(is_initiator=False)
    """

    def __init__(self, **endpoint_kwargs):
        link = endpoint_kwargs.get("link")
        self._is_quic = link is not None and _is_quic_link(link)
        self._quic_link = link if self._is_quic else None
        self._send_queue: list = []
        self._send_task: Optional[asyncio.Task] = None

        if self._is_quic:
            # Replace QuicLink with dummy before constructing Endpoint;
            # real sends/receives are handled by our QUIC pump loop.
            endpoint_kwargs["link"] = _DummyLink()

        self._ep = Endpoint(**endpoint_kwargs)
        self._ack_futures: dict[str, asyncio.Future] = {}
        self._channel_futures: dict[int, asyncio.Future] = {}
        self._running = False
        self._pump_task: Optional[asyncio.Task] = None
        self._peer: Optional["AsyncEndpoint"] = None

    # ── pass-through properties ─────────────────────────────
    @property
    def session(self):
        return self._ep.session

    @property
    def channels(self):
        return self._ep.channels

    @property
    def audit(self):
        return self._ep.audit

    @property
    def dedupe(self):
        return self._ep.dedupe

    @property
    def node_id(self) -> str:
        return self._ep.node_id

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_quic(self) -> bool:
        return self._is_quic

    # ── QUIC-mode internals ──────────────────────────────────
    def _setup_quic_mode(self) -> None:
        """Intercept Endpoint._send to buffer frames instead of writing to link."""
        self._ep._send = self._quic_send  # type: ignore[assignment]

    def _quic_send(self, msg_type: MessageType, *, ext: dict = None,
                   payload: bytes = b"", channel_id: int = 0,
                   flags: int = 0) -> GfsipFrame:
        """Replacement for Endpoint._send in QUIC mode — buffers serialized frames."""
        sid = self._ep.session.session_id or (b"\x00" * 16)
        frame = GfsipFrame(
            msg_type=msg_type, channel_id=channel_id, session_id=sid,
            sequence=self._ep._next_seq(), extension_header=ext,
            payload=payload, flags=flags,
        )
        data = frame.serialize()
        self._ep._transcript += data
        self._send_queue.append(data)
        return frame

    async def _flush_send_queue(self) -> None:
        """Send all buffered frames through QuicLink."""
        while self._send_queue:
            data = self._send_queue.pop(0)
            await self._quic_link.send_frame(data)

    async def _quic_send_loop(self) -> None:
        """Background task: drain the send queue and write to QuicLink."""
        while self._running:
            if self._send_queue:
                try:
                    await self._flush_send_queue()
                except Exception:
                    await asyncio.sleep(0.01)
            else:
                await asyncio.sleep(0.001)

    # ── connection lifecycle ─────────────────────────────────
    async def start(self, is_initiator: bool, timeout: float = 10.0) -> None:
        """Start a QUIC-mode session: run GFSIP handshake, start pump loops.

        Use this when the transport is a QuicLink (real network).
        For in-memory Link pairs, use connect(peer) instead.
        """
        if not self._is_quic:
            raise ProtocolError(
                None, "start() requires a QuicLink transport; use connect() for in-memory"
            )
        if self._running:
            raise ProtocolError(None, "Already started")

        self._setup_quic_mode()
        loop = asyncio.get_running_loop()

        if is_initiator:
            self._ep._kickoff()

        # GFSIP handshake over QUIC: pump until ESTABLISHED
        deadline = loop.time() + timeout
        while self._ep.session.state != SessionState.ESTABLISHED:
            if loop.time() > deadline:
                raise ProtocolError(None, "GFSIP handshake timed out")
            await self._flush_send_queue()
            await self._pump_once()

        # Drain leftover frames
        await self._flush_send_queue()
        while self._quic_link.pending():
            await self._pump_once()

        # Start background pump + send loops
        self._running = True
        self._pump_task = asyncio.create_task(self._pump_loop())
        self._send_task = asyncio.create_task(self._quic_send_loop())

    async def connect(self, peer: "AsyncEndpoint", timeout: float = 10.0) -> None:
        """Perform mutual-auth handshake and start background pump loops.

        For in-memory Link pairs only. For QUIC, use start().
        """
        if self._running:
            raise ProtocolError(None, "Already connected")
        if self._is_quic:
            raise ProtocolError(None, "connect() is for in-memory; use start() for QUIC")

        self._peer = peer
        peer._peer = self

        loop = asyncio.get_running_loop()
        try:
            await asyncio.wait_for(
                loop.run_in_executor(None, self._ep.handshake_with, peer._ep),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            raise ProtocolError(None, "Handshake timed out")

        # Drain any post-handshake frames before starting async loops
        for ep in (peer._ep, self._ep):
            while ep.link.pending():
                ep._pump_once()

        self._running = True
        peer._running = True
        self._pump_task = asyncio.create_task(self._pump_loop())
        peer._pump_task = asyncio.create_task(peer._pump_loop())

    async def close(self) -> None:
        """Stop the background pump loop and clean up."""
        self._running = False
        if self._pump_task:
            self._pump_task.cancel()
            try:
                await self._pump_task
            except asyncio.CancelledError:
                pass
            self._pump_task = None
        if self._send_task:
            self._send_task.cancel()
            try:
                await self._send_task
            except asyncio.CancelledError:
                pass
            self._send_task = None
        # Cancel any pending futures
        for fut in self._ack_futures.values():
            if not fut.done():
                fut.cancel()
        for fut in self._channel_futures.values():
            if not fut.done():
                fut.cancel()
        self._ack_futures.clear()
        self._channel_futures.clear()
        # Close QUIC connection if applicable
        if self._is_quic and self._quic_link is not None:
            try:
                await self._quic_link.close()
            except Exception:
                pass

    # ── channel operations ───────────────────────────────────
    async def open_channel(self, *, channel_type: str = "task",
                           ordered: bool = True, delivery: str = "application_ack",
                           priority: int = 20, max_inflight: int = 64,
                           content_types=None, metadata=None,
                           timeout: float = 5.0) -> int:
        """Open a channel and wait for CHANNEL_READY from the peer.

        Returns the channel_id on success.
        """
        loop = asyncio.get_running_loop()
        cid = await loop.run_in_executor(
            None,
            lambda: self._ep.open_channel(
                channel_type=channel_type, ordered=ordered, delivery=delivery,
                priority=priority, max_inflight=max_inflight,
                content_types=content_types, metadata=metadata,
            ),
        )
        # In QUIC mode, the OPEN_CHANNEL frame is buffered — flush it
        if self._is_quic:
            await self._flush_send_queue()

        fut = loop.create_future()
        self._channel_futures[cid] = fut
        try:
            await asyncio.wait_for(fut, timeout=timeout)
        except asyncio.TimeoutError:
            self._channel_futures.pop(cid, None)
            raise ChannelError(None, f"Channel {cid} READY timed out")
        return cid

    # ── data operations ──────────────────────────────────────
    async def send(self, channel_id: int, *, operation: str, payload: bytes,
                   idempotency_key: str = None, content_type: str = "application/json",
                   deadline_ms: int = 5000, timeout: float = 10.0) -> dict:
        """Send DATA and wait for the peer's APP_ACK.

        Returns the APP_ACK extension header as a dict, containing at
        minimum ``message_id``, ``status``, ``result_hash``, ``processed_at``.
        """
        loop = asyncio.get_running_loop()
        msg_id = await loop.run_in_executor(
            None,
            lambda: self._ep.send_data(
                channel_id, operation=operation, payload=payload,
                idempotency_key=idempotency_key, content_type=content_type,
                deadline_ms=deadline_ms,
            ),
        )
        # In QUIC mode, flush the buffered DATA frame
        if self._is_quic:
            await self._flush_send_queue()

        fut = loop.create_future()
        self._ack_futures[msg_id] = fut
        try:
            result = await asyncio.wait_for(fut, timeout=timeout)
        except asyncio.TimeoutError:
            self._ack_futures.pop(msg_id, None)
            raise ProtocolError(None, f"send timed out (message_id={msg_id})")
        return result

    # ── background pump ──────────────────────────────────────
    async def _pump_loop(self) -> None:
        """Continuously drain inbound frames and dispatch them."""
        while self._running:
            try:
                has_data = (
                    self._quic_link.pending()
                    if self._is_quic
                    else self._ep.link.pending()
                )
                if has_data:
                    await self._pump_once()
                else:
                    await asyncio.sleep(0.001)
            except Exception:
                self._running = False
                raise

    async def _pump_once(self) -> None:
        """Receive one frame, delegate protocol handling, resolve app futures."""
        if self._is_quic:
            # QUIC mode: receive directly from QuicLink (no executor, no deadlock)
            data = await self._quic_link.recv_frame()
        else:
            # In-memory mode: link.recv() is blocking, run in executor
            loop = asyncio.get_running_loop()
            data = await loop.run_in_executor(None, self._ep.link.recv)

        frame = GfsipFrame.parse(data)
        self._ep._transcript += data
        pre_transcript = self._ep._transcript[:-len(data)]

        if frame.msg_type == MessageType.APP_ACK:
            self._resolve_ack(frame)
        elif frame.msg_type == MessageType.CHANNEL_READY:
            self._ep._handle(frame, pre_transcript)
            self._resolve_channel_ready(frame)
        else:
            self._ep._handle(frame, pre_transcript)

    # ── future resolution ────────────────────────────────────
    def _resolve_ack(self, frame: GfsipFrame) -> None:
        ext = frame.extension_header or {}
        msg_id = ext.get("message_id")
        if msg_id and msg_id in self._ack_futures:
            fut = self._ack_futures.pop(msg_id)
            if not fut.done():
                fut.set_result(ext)

    def _resolve_channel_ready(self, frame: GfsipFrame) -> None:
        ext = frame.extension_header or {}
        cid = ext.get("channel_id", frame.channel_id)
        if cid in self._channel_futures:
            fut = self._channel_futures.pop(cid)
            if not fut.done():
                fut.set_result(cid)

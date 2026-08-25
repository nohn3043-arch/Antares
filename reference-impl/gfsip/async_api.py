"""GFSIP/1.0 High-Level Async API.

Wraps the synchronous reference Endpoint with an async/await interface
for application developers. Runs a background pump loop so callers never
need to invoke _pump_once() manually; send() returns the peer's APP_ACK
result; open_channel() resolves when CHANNEL_READY arrives.

This module does NOT modify the reference Endpoint. It intercepts frames
in its own pump loop and delegates protocol handling to the underlying
Endpoint, while resolving asyncio.Future objects for application-level
concerns (APP_ACK, CHANNEL_READY).
"""

import asyncio
from typing import Optional

from .endpoint import Endpoint, ProtocolError
from .frame import GfsipFrame
from .types import MessageType, SessionState
from .channel import ChannelError


class AsyncEndpoint:
    """Application-friendly async wrapper around :class:`Endpoint`.

    Usage::

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
        result = await a.send(cid, op="ping", payload=b"{}")  # waits for APP_ACK
        await a.close()
    """

    def __init__(self, **endpoint_kwargs):
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

    # ── connection lifecycle ─────────────────────────────────
    async def connect(self, peer: "AsyncEndpoint", timeout: float = 10.0) -> None:
        """Perform mutual-auth handshake and start background pump loops.

        The synchronous handshake runs in a worker thread; after it
        completes, both sides start async pump loops.
        """
        if self._running:
            raise ProtocolError(None, "Already connected")
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
        """Stop the background pump loop."""
        self._running = False
        if self._pump_task:
            self._pump_task.cancel()
            try:
                await self._pump_task
            except asyncio.CancelledError:
                pass
            self._pump_task = None
        # Cancel any pending futures
        for fut in self._ack_futures.values():
            if not fut.done():
                fut.cancel()
        for fut in self._channel_futures.values():
            if not fut.done():
                fut.cancel()
        self._ack_futures.clear()
        self._channel_futures.clear()

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
            if self._ep.link.pending():
                try:
                    await self._pump_once()
                except Exception:
                    # In production you'd log this; for the reference
                    # async wrapper we stop the loop on fatal errors.
                    self._running = False
                    raise
            else:
                await asyncio.sleep(0.001)

    async def _pump_once(self) -> None:
        """Receive one frame, delegate protocol handling, resolve app futures."""
        loop = asyncio.get_running_loop()
        # link.recv() is blocking (tiny sleep-poll); run in executor.
        # We already checked pending() so it will return immediately.
        data = await loop.run_in_executor(None, self._ep.link.recv)
        frame = GfsipFrame.parse(data)
        self._ep._transcript += data
        pre_transcript = self._ep._transcript[:-len(data)]

        if frame.msg_type == MessageType.APP_ACK:
            # Reference Endpoint does not handle APP_ACK; we resolve
            # the corresponding future here.
            self._resolve_ack(frame)
        elif frame.msg_type == MessageType.CHANNEL_READY:
            # Let Endpoint mark the channel ready, then resolve our future.
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

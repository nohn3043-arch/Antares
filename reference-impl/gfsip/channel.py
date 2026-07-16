"""GFSIP/1.0 Channel Manager (Sections 5, 14).

Manages Channel lifecycle, odd/even ID allocation, non-reuse,
flow control and priority scheduling fairness.
"""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional

from .types import ErrorCode, DEFAULT_MAX_CHANNELS, CONTROL_CHANNEL


class ChannelState(IntEnum):
    IDLE = 0
    OPENING = 1
    OPEN = 2
    HALF_CLOSED = 3
    CLOSED = 4


@dataclass
class Channel:
    channel_id: int
    channel_type: str = "message"
    ordered: bool = True
    delivery: str = "application_ack"
    priority: int = 20
    max_inflight: int = 64
    content_types: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    state: ChannelState = ChannelState.IDLE
    inflight: int = 0

    def allocate(self) -> None:
        if self.inflight >= self.max_inflight:
            raise ChannelError(ErrorCode.FLOW_CONTROL_LIMIT,
                               f"Channel {self.channel_id} inflight {self.inflight} >= {self.max_inflight}")
        self.inflight += 1

    def release(self) -> None:
        if self.inflight > 0:
            self.inflight -= 1


class ChannelError(Exception):
    def __init__(self, code: ErrorCode, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


class ChannelManager:
    """Owns all Channels of one Endpoint (Section 14)."""

    def __init__(self, is_initiator: bool, max_channels: int = DEFAULT_MAX_CHANNELS):
        self.is_initiator = is_initiator
        self.max_channels = max_channels
        self._channels: dict[int, Channel] = {}
        self._next_odd = 1
        self._next_even = 2

    # ── ownership / parity ──────────────────────────────────
    def _allocate_id(self) -> int:
        if len(self._channels) >= self.max_channels:
            raise ChannelError(ErrorCode.CHANNEL_LIMIT,
                               f"Channel limit {self.max_channels} reached")
        if self.is_initiator:
            cid = self._next_odd
            self._next_odd += 2
        else:
            cid = self._next_even
            self._next_even += 2
        return cid

    @staticmethod
    def id_parity_ok(channel_id: int, is_initiator: bool) -> bool:
        """Initiator owns odd IDs, Responder owns even IDs (Section 5)."""
        if channel_id == CONTROL_CHANNEL:
            return True  # control channel is special
        return (channel_id % 2 == 1) == is_initiator

    # ── lifecycle ───────────────────────────────────────────
    def open(self, *, channel_type: str = "message", ordered: bool = True,
             delivery: str = "application_ack", priority: int = 20,
             max_inflight: int = 64, content_types: Optional[list] = None,
             metadata: Optional[dict] = None) -> Channel:
        cid = self._allocate_id()
        ch = Channel(
            channel_id=cid,
            channel_type=channel_type,
            ordered=ordered,
            delivery=delivery,
            priority=priority,
            max_inflight=max_inflight,
            content_types=content_types or [],
            metadata=metadata or {},
            state=ChannelState.OPENING,
        )
        self._channels[cid] = ch
        return ch

    def mark_ready(self, channel_id: int) -> Channel:
        ch = self._require(channel_id)
        if ch.state != ChannelState.OPENING:
            raise ChannelError(ErrorCode.STATE_CONFLICT,
                               f"Channel {channel_id} not in OPENING")
        ch.state = ChannelState.OPEN
        return ch

    def half_close(self, channel_id: int) -> Channel:
        ch = self._require(channel_id)
        if ch.state in (ChannelState.CLOSED,):
            raise ChannelError(ErrorCode.STATE_CONFLICT,
                               f"Channel {channel_id} already closed")
        ch.state = ChannelState.HALF_CLOSED
        return ch

    def close(self, channel_id: int) -> Channel:
        ch = self._require(channel_id)
        ch.inflight = 0
        ch.state = ChannelState.CLOSED
        return ch

    # ── queries ─────────────────────────────────────────────
    def get(self, channel_id: int) -> Optional[Channel]:
        return self._channels.get(channel_id)

    def _require(self, channel_id: int) -> Channel:
        ch = self._channels.get(channel_id)
        if ch is None:
            raise ChannelError(ErrorCode.INVALID_CHANNEL_ID,
                               f"Unknown channel {channel_id}")
        return ch

    def open_channels(self) -> list[int]:
        return [cid for cid, ch in self._channels.items()
                if ch.state in (ChannelState.OPENING, ChannelState.OPEN, ChannelState.HALF_CLOSED)]

    def all_closed(self) -> bool:
        return all(ch.state == ChannelState.CLOSED for ch in self._channels.values())

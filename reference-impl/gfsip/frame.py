"""GFSIP/1.0 Frame Codec — 44-byte fixed header + CBOR extension + payload.

Section 8 of the protocol specification.
"""

import struct
from dataclasses import dataclass, field
from typing import Optional

from .types import MAGIC, FRAME_HEADER_SIZE, CONTROL_CHANNEL
from .types import MessageType, FrameFlag, ErrorCode
from .cbor_utils import encode_deterministic, decode


# Fixed-length binary fields (big-endian)
# Magic(4s) + Major(B) + Minor(B) + Type(B) + Flags(B)
# + HdrLen(H) + Reserved(H) + PayloadLen(I) + SessionID(16s) + Sequence(Q) + ChannelID(I)
# = 4+1+1+1+1 + 2+2 + 4 + 16 + 8 + 4 = 44
_HEADER_STRUCT = struct.Struct("!4sBBBBHH I 16s Q I")


@dataclass
class GfsipFrame:
    """A complete GFSIP frame: fixed header + optional extension + payload."""

    msg_type: MessageType
    channel_id: int = CONTROL_CHANNEL
    session_id: bytes = b"\x00" * 16       # zero before SESSION_READY
    flags: int = 0
    sequence: int = 0
    extension_header: Optional[dict] = None
    payload: bytes = b""

    # Frozen version 1.0
    major: int = field(default=1, repr=False)
    minor: int = field(default=0, repr=False)
    reserved: int = field(default=0, repr=False)

    def serialize(self) -> bytes:
        """Encode to wire bytes: 44-byte header + CBOR extension + payload."""
        ext_bytes = (
            encode_deterministic(self.extension_header)
            if self.extension_header is not None
            else b""
        )
        header_len = len(ext_bytes)
        payload_len = len(self.payload)

        if header_len > 65535:
            raise ValueError(f"Extension header too large: {header_len}")
        if payload_len > 0xFFFFFFFF:
            raise ValueError(f"Payload too large: {payload_len}")

        header = _HEADER_STRUCT.pack(
            MAGIC,
            self.major,
            self.minor,
            self.msg_type.value,
            self.flags,
            header_len,
            self.reserved,
            payload_len,
            self.session_id,
            self.sequence,
            self.channel_id,
        )
        return header + ext_bytes + self.payload

    @classmethod
    def parse(cls, data: bytes) -> "GfsipFrame":
        """Decode wire bytes into a GfsipFrame. Raises on malformed input."""
        if len(data) < FRAME_HEADER_SIZE:
            raise FrameDecodeError(
                ErrorCode.MALFORMED_FRAME,
                f"Frame too short: {len(data)} < {FRAME_HEADER_SIZE}",
            )

        (
            magic,
            major,
            minor,
            msg_type_raw,
            flags,
            header_len,
            reserved,
            payload_len,
            session_id,
            sequence,
            channel_id,
        ) = _HEADER_STRUCT.unpack_from(data)

        if magic != MAGIC:
            raise FrameDecodeError(
                ErrorCode.MALFORMED_FRAME,
                f"Invalid magic: {magic!r} != {MAGIC!r}",
            )

        try:
            msg_type = MessageType(msg_type_raw)
        except ValueError:
            raise FrameDecodeError(
                ErrorCode.MALFORMED_FRAME,
                f"Unknown message type: 0x{msg_type_raw:02X}",
            )

        ext_end = FRAME_HEADER_SIZE + header_len
        payload_start = ext_end
        payload_end = ext_end + payload_len

        if len(data) < payload_end:
            raise FrameDecodeError(
                ErrorCode.MALFORMED_FRAME,
                f"Truncated frame: expected {payload_end} bytes, got {len(data)}",
            )

        ext_bytes = data[FRAME_HEADER_SIZE:ext_end]
        payload_bytes = data[payload_start:payload_end]

        extension_header = decode(ext_bytes) if header_len > 0 else None

        return cls(
            msg_type=msg_type,
            channel_id=channel_id,
            session_id=session_id,
            flags=flags,
            sequence=sequence,
            extension_header=extension_header,
            payload=payload_bytes,
            major=major,
            minor=minor,
            reserved=reserved,
        )

    def has_flag(self, flag: FrameFlag) -> bool:
        return (self.flags & (1 << flag.value)) != 0

    def set_flag(self, flag: FrameFlag) -> None:
        self.flags |= 1 << flag.value

    def validate(self) -> list[str]:
        """Return list of validation warnings. Empty = valid."""
        warnings = []
        if self.major != 1:
            warnings.append(f"Unsupported major version: {self.major}")
        if self.reserved != 0:
            warnings.append(f"Reserved field is non-zero: {self.reserved}")
        if self.channel_id == CONTROL_CHANNEL and self.msg_type not in _CONTROL_MESSAGES:
            warnings.append(f"Non-control message on control channel: {self.msg_type.name}")
        if self.channel_id != CONTROL_CHANNEL and self.msg_type in _CONTROL_ONLY:
            warnings.append(f"Control message on non-control channel: {self.msg_type.name}")
        return warnings

    def __repr__(self) -> str:
        flags_str = ",".join(
            f.name for f in FrameFlag if self.has_flag(f)
        ) or "none"
        ext_preview = (
            f"{list(self.extension_header.keys())}"
            if self.extension_header
            else "none"
        )
        return (
            f"GfsipFrame(type={self.msg_type.name}, chan={self.channel_id}, "
            f"seq={self.sequence}, flags=[{flags_str}], "
            f"ext={ext_preview}, payload={len(self.payload)}B)"
        )


class FrameDecodeError(Exception):
    """Raised when frame bytes cannot be parsed."""

    def __init__(self, code: ErrorCode, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


# Messages allowed on the control channel (Channel 0)
_CONTROL_MESSAGES = {
    MessageType.CLIENT_HELLO,
    MessageType.SERVER_HELLO,
    MessageType.AUTH,
    MessageType.AUTH_RESULT,
    MessageType.SESSION_READY,
    MessageType.RESUME,
    MessageType.RESUME_RESULT,
    MessageType.OPEN_CHANNEL,
    MessageType.CHANNEL_READY,
    MessageType.CLOSE_CHANNEL,
    MessageType.PING,
    MessageType.PONG,
    MessageType.CAPABILITY_UPDATE,
    MessageType.GOAWAY,
    MessageType.ERROR,
}

# Messages that MUST be on control channel
_CONTROL_ONLY = {
    MessageType.CLIENT_HELLO,
    MessageType.SERVER_HELLO,
    MessageType.AUTH,
    MessageType.AUTH_RESULT,
    MessageType.SESSION_READY,
    MessageType.RESUME,
    MessageType.RESUME_RESULT,
    MessageType.PING,
    MessageType.PONG,
    MessageType.GOAWAY,
}

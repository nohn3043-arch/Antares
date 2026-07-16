"""GFSIP/1.0 Reference Implementation — Core Protocol Library.

Provides:
- Frame codec (44-byte fixed header + deterministic CBOR)
- Session state machine
- All protocol type definitions
"""

from .types import (
    MAGIC,
    FRAME_HEADER_SIZE,
    CONTROL_CHANNEL,
    MessageType,
    FrameFlag,
    SessionState,
    ErrorCode,
    ChannelType,
    Profile,
)
from .frame import GfsipFrame, FrameDecodeError
from .state_machine import Session, TransitionRejected
from .cbor_utils import encode_deterministic, decode

__all__ = [
    "MAGIC",
    "FRAME_HEADER_SIZE",
    "CONTROL_CHANNEL",
    "MessageType",
    "FrameFlag",
    "SessionState",
    "ErrorCode",
    "ChannelType",
    "Profile",
    "GfsipFrame",
    "FrameDecodeError",
    "Session",
    "TransitionRejected",
    "encode_deterministic",
    "decode",
]

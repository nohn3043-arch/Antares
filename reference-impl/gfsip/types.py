"""GFSIP/1.0 Protocol Type Definitions.

All constants match the frozen wire format in GFSIP_v1.0_protocol_spec.md.
"""

from enum import IntEnum


class MessageType(IntEnum):
    """Wire-stable message type identifiers (Section 9)."""
    CLIENT_HELLO        = 0x01
    SERVER_HELLO        = 0x02
    AUTH                = 0x03
    AUTH_RESULT         = 0x04
    SESSION_READY       = 0x05
    RESUME              = 0x06
    RESUME_RESULT       = 0x07
    OPEN_CHANNEL        = 0x08
    CHANNEL_READY       = 0x09
    CLOSE_CHANNEL       = 0x0A
    DATA                = 0x0B
    APP_ACK             = 0x0C
    EVENT               = 0x0D
    PING                = 0x0E
    PONG                = 0x0F
    CAPABILITY_UPDATE   = 0x10
    GOAWAY              = 0x11
    ERROR               = 0x12
    DOMAIN_DESCRIPTOR   = 0x13
    ROUTE_QUERY         = 0x14
    ROUTE_RESULT        = 0x15
    STATE_SYNC          = 0x16


class FrameFlag(IntEnum):
    """Frame flag bit positions (Section 8.3)."""
    ACK_REQUIRED = 0
    AUDIT_PRESENT = 1
    END_CHANNEL = 2
    IDEMPOTENT = 3
    COMPRESSED = 4
    EARLY_DATA = 5


class SessionState(IntEnum):
    """Session state machine states (Section 10)."""
    NEW = 0
    NEGOTIATING = 1
    AUTHENTICATING = 2
    ESTABLISHED = 3
    DEGRADED = 4
    RESUMING = 5
    DRAINING = 6
    CLOSED = 7

    @property
    def label(self) -> str:
        return self.name


class ErrorCode(IntEnum):
    """Wire-stable numeric error codes (Section 20, gfsip-error-registry.json)."""
    MALFORMED_FRAME                    = 1000
    VERSION_UNSUPPORTED                = 1001
    AUTH_REQUIRED                      = 1002
    AUTH_FAILED                        = 1003
    NOT_AUTHORIZED                     = 1004
    FRAME_TOO_LARGE                    = 1005
    CHANNEL_LIMIT                      = 1006
    INVALID_CHANNEL_ID                 = 1007
    DUPLICATE_ACCEPTED                 = 1008
    STATE_CONFLICT                     = 1009
    RESUME_EXPIRED                     = 1010
    RESUME_IDENTITY_MISMATCH           = 1011
    RATE_LIMITED                       = 1012
    INTERNAL_ERROR                     = 1013
    POLICY_REJECTED                    = 1014
    SEQUENCE_REPLAY                    = 1015
    DESCRIPTOR_EXPIRED                 = 1016
    ROUTE_LOOP                         = 1017
    ROUTE_HOP_LIMIT                    = 1018
    EARLY_DATA_REJECTED                = 1019
    DECOMPRESSION_LIMIT                = 1020
    CAUSAL_CYCLE                       = 1021
    UNSUPPORTED_CRITICAL_EXTENSION     = 1022
    FLOW_CONTROL_LIMIT                 = 1023

    @property
    def is_fatal(self) -> bool:
        fatal = {
            ErrorCode.MALFORMED_FRAME,
            ErrorCode.VERSION_UNSUPPORTED,
            ErrorCode.AUTH_FAILED,
            ErrorCode.RESUME_EXPIRED,
            ErrorCode.RESUME_IDENTITY_MISMATCH,
        }
        return self in fatal


class ChannelType:
    """Predefined channel types (Section 11)."""
    CONTROL     = "control"
    MESSAGE     = "message"
    STREAM      = "stream"
    TASK        = "task"
    AUDIT       = "audit"
    STATE_SYNC  = "state-sync"


class Profile:
    """Protocol profiles (Section 4)."""
    CORE       = "core/1"
    AUDIT      = "audit/1"
    FEDERATION = "federation/1"


class DeliveryMode:
    APPLICATION_ACK = "application_ack"
    FIRE_AND_FORGET = "fire_and_forget"


# Frozen constants (Section 31)
MAGIC = b"GFS1"
FRAME_HEADER_SIZE = 44
CONTROL_CHANNEL = 0
MAX_HEADER = 65535
MAX_PARENT_EVENTS = 8
MAX_ROUTE_HOPS = 8

# Wire limits (Section 21)
DEFAULT_MAX_FRAME = 1_048_576      # 1 MiB
DEFAULT_MAX_HEADER = 32_768        # 32 KiB
DEFAULT_MAX_CHANNELS = 128
DEFAULT_UNAUTH_LIFETIME = 10       # seconds

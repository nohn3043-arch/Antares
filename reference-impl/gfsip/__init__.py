"""GFSIP/1.0 Reference Implementation (Python).

Modules:
  types        — frozen wire constants, message types, flags, states, errors
  cbor_utils   — deterministic CBOR encode/decode (Section 7)
  frame        — 44-byte frame codec (Section 8)
  state_machine— session state machine + invariants (Section 10)
  channel      — channel manager (Section 14)
  auth         — authentication / authorization (Section 12)
  dedupe       — idempotency store (Section 15)
  resume       — session resume service (Sections 13, 16)
  audit        — Audit/1 causal event log (Section 17)
  federation   — Federation/1 descriptor & routing (Section 18)
  transport    — in-memory synchronous transport (Section 6)
  endpoint     — integrated node (handshake / data / recovery)
  conformance  — Section 28 minimum test vectors
"""

from .types import (
    MessageType, FrameFlag, SessionState, ErrorCode, ChannelType,
    Profile, DeliveryMode,
    MAGIC, FRAME_HEADER_SIZE, CONTROL_CHANNEL, MAX_HEADER,
    MAX_PARENT_EVENTS, MAX_ROUTE_HOPS,
    DEFAULT_MAX_FRAME, DEFAULT_MAX_CHANNELS, DEFAULT_UNAUTH_LIFETIME,
)
from .frame import GfsipFrame, FrameDecodeError
from .state_machine import Session, TransitionRejected
from .channel import ChannelManager, Channel, ChannelState, ChannelError
from .auth import Authenticator, AuthMethod, AuthProof, AuthError
from .dedupe import DedupeStore, DedupeOutcome
from .resume import ResumeService, ResumeToken, ResumeError
from .audit import AuditLog, AuditEvent, AuditError
from .federation import (
    FederationRegistry, DomainDescriptor, Gateway, TrustAnchor, FederationError,
)
from .transport import Link, make_link_pair
from .endpoint import Endpoint, ProtocolError

__all__ = [
    "MessageType", "FrameFlag", "SessionState", "ErrorCode", "ChannelType",
    "Profile", "DeliveryMode", "MAGIC", "FRAME_HEADER_SIZE", "CONTROL_CHANNEL",
    "MAX_HEADER", "MAX_PARENT_EVENTS", "MAX_ROUTE_HOPS",
    "DEFAULT_MAX_FRAME", "DEFAULT_MAX_CHANNELS", "DEFAULT_UNAUTH_LIFETIME",
    "GfsipFrame", "FrameDecodeError",
    "Session", "TransitionRejected",
    "ChannelManager", "Channel", "ChannelState", "ChannelError",
    "Authenticator", "AuthMethod", "AuthProof", "AuthError",
    "DedupeStore", "DedupeOutcome",
    "ResumeService", "ResumeToken", "ResumeError",
    "AuditLog", "AuditEvent", "AuditError",
    "FederationRegistry", "DomainDescriptor", "Gateway", "TrustAnchor",
    "FederationError",
    "Link", "make_link_pair",
    "Endpoint", "ProtocolError",
]

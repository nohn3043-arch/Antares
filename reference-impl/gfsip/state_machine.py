"""GFSIP/1.0 Session State Machine (Section 10).

Enforces mandatory invariants on every state transition.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .types import SessionState, MessageType, ErrorCode


class TransitionRejected(Exception):
    """Raised when a state transition violates protocol invariants."""

    def __init__(self, error_code: ErrorCode, detail: str):
        super().__init__(detail)
        self.error_code = error_code
        self.detail = detail


@dataclass
class Session:
    session_id: Optional[bytes] = None
    _state: SessionState = SessionState.NEW
    node_id: Optional[str] = None
    domain_id: Optional[str] = None
    selected_version: Optional[str] = None
    selected_profiles: list[str] = field(default_factory=list)
    max_channels: int = 128
    channel_count: int = 0
    goaway_received: bool = False
    last_sequence: int = 0
    history: list[SessionState] = field(default_factory=list)

    @property
    def state(self) -> SessionState:
        return self._state

    def transition(self, event: MessageType, context: dict | None = None) -> SessionState:
        """Execute a state transition. Raises TransitionRejected on violation.

        context may contain: version_matched, auth_result, resume_result, etc.
        """
        ctx = context or {}
        old = self._state
        new = self._lookup(old, event, ctx)

        if new is None:
            raise TransitionRejected(
                ErrorCode.STATE_CONFLICT,
                f"Cannot process {event.name} in state {old.name}",
            )

        # Enforce invariants
        self._check_invariants(old, new, event, ctx)

        self.history.append(old)
        self._state = new
        return new

    def _lookup(
        self, state: SessionState, event: MessageType, ctx: dict
    ) -> Optional[SessionState]:
        """Look up the target state for a given (state, event, context) tuple."""

        # ── Universal transitions (any non-CLOSED → CLOSED on fatal) ──
        if state != SessionState.CLOSED:
            if event == MessageType.ERROR and ctx.get("fatal", False):
                return SessionState.CLOSED

        # ── State-specific transitions ──
        if state == SessionState.NEW:
            if event == MessageType.CLIENT_HELLO:
                return SessionState.NEGOTIATING

        elif state == SessionState.NEGOTIATING:
            if event == MessageType.SERVER_HELLO:
                if ctx.get("version_matched", True):
                    return SessionState.AUTHENTICATING
                else:
                    return SessionState.CLOSED  # VERSION_UNSUPPORTED
            elif event == MessageType.ERROR:
                return SessionState.CLOSED

        elif state == SessionState.AUTHENTICATING:
            if event in {MessageType.AUTH, MessageType.AUTH_RESULT}:
                if ctx.get("auth_success", False):
                    return SessionState.ESTABLISHED
                else:
                    return SessionState.CLOSED  # AUTH_FAILED

        elif state == SessionState.ESTABLISHED:
            if event == MessageType.GOAWAY:
                return SessionState.DRAINING
            if ctx.get("path_lost", False):
                return SessionState.DEGRADED
            if event in _data_messages:
                return SessionState.ESTABLISHED  # stable state

        elif state == SessionState.DEGRADED:
            if event == MessageType.RESUME:
                return SessionState.RESUMING

        elif state == SessionState.RESUMING:
            if event == MessageType.RESUME_RESULT:
                result = ctx.get("result", "")
                if result == "resumed":
                    return SessionState.ESTABLISHED
                elif result == "partial":
                    return SessionState.ESTABLISHED
                else:
                    return SessionState.CLOSED  # rejected or new_session_required

        elif state == SessionState.DRAINING:
            if ctx.get("all_channels_closed", False):
                return SessionState.CLOSED

        return None  # undefined transition

    def _check_invariants(
        self, old: SessionState, new: SessionState,
        event: MessageType, ctx: dict,
    ) -> None:
        """Raise TransitionRejected if a mandatory invariant is violated."""

        # Invariant 1: No DATA/EVENT/ROUTE_QUERY before ESTABLISHED
        if old not in {SessionState.ESTABLISHED, SessionState.DRAINING}:
            if event in _side_effect_messages:
                raise TransitionRejected(
                    ErrorCode.NOT_AUTHORIZED,
                    f"{event.name} not allowed before ESTABLISHED",
                )

        # Invariant 2: AUTHENTICATING only allows control messages
        if old == SessionState.AUTHENTICATING:
            if event not in {MessageType.AUTH, MessageType.AUTH_RESULT, MessageType.ERROR}:
                raise TransitionRejected(
                    ErrorCode.STATE_CONFLICT,
                    f"Only AUTH/AUTH_RESULT/ERROR allowed during AUTHENTICATING",
                )

        # Invariant 5: No new channels after GOAWAY
        if self.goaway_received and event == MessageType.OPEN_CHANNEL:
            raise TransitionRejected(
                ErrorCode.STATE_CONFLICT,
                "Cannot open channel after GOAWAY",
            )

        # Invariant 6: CLOSED must not process any protocol input
        if old == SessionState.CLOSED:
            raise TransitionRejected(
                ErrorCode.STATE_CONFLICT,
                f"Cannot process {event.name} in CLOSED state",
            )

        # Invariant 8: Resume must not escalate permissions
        if event == MessageType.RESUME_RESULT and new == SessionState.ESTABLISHED:
            if ctx.get("auth_context_revoked", False):
                raise TransitionRejected(
                    ErrorCode.AUTH_FAILED,
                    "Cannot resume: auth context has been revoked",
                )

    def goaway(self) -> None:
        self.goaway_received = True

    @property
    def is_active(self) -> bool:
        return self._state in {
            SessionState.ESTABLISHED,
            SessionState.DEGRADED,
            SessionState.DRAINING,
        }

    def __repr__(self) -> str:
        hist = " → ".join(s.name for s in self.history[-5:]) if self.history else "new"
        return (
            f"Session(sid={self.session_id.hex()[:12] if self.session_id else 'nil'}..., "
            f"state={self._state.name}, nodes={self.node_id}, "
            f"channels={self.channel_count}/{self.max_channels}, "
            f"history=[{hist}])"
        )


# Messages that produce side effects (require ESTABLISHED)
_side_effect_messages = {
    MessageType.DATA,
    MessageType.EVENT,
    MessageType.ROUTE_QUERY,
}

# Messages allowed in ESTABLISHED (stable-operational state)
_data_messages = {
    MessageType.DATA,
    MessageType.APP_ACK,
    MessageType.EVENT,
    MessageType.OPEN_CHANNEL,
    MessageType.CHANNEL_READY,
    MessageType.CLOSE_CHANNEL,
    MessageType.PING,
    MessageType.PONG,
    MessageType.CAPABILITY_UPDATE,
}

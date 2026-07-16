"""GFSIP/1.0 Audit/1 — Causal Event Log (Sections 17, 10 invariants 7-8).

Enforces:
  - EVENT must not reference itself as parent (CAUSAL_CYCLE)
  - Known causal graph must stay acyclic (CAUSAL_CYCLE)
  - At most MAX_PARENT_EVENTS parents
  - Missing parents are marked unresolved, NOT rejected
  - Signature covers canonical bytes (protocol_version, session_id,
    event header without signature, payload hash)
"""

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

from .types import ErrorCode, MAX_PARENT_EVENTS
from .cbor_utils import encode_deterministic


@dataclass
class AuditEvent:
    event_id: str
    parent_event_ids: list = field(default_factory=list)
    actor_node_id: str = ""
    actor_domain_id: str = ""
    event_type: str = ""
    rule_id: str = ""
    rule_version: str = ""
    state_before_hash: str = ""
    state_after_hash: str = ""
    evidence_hash: str = ""
    result_code: str = "RESERVED"
    observed_at: str = ""
    logical_clock: int = 0
    unresolved_parents: list = field(default_factory=list)
    signature: str = ""


class AuditError(Exception):
    def __init__(self, code: ErrorCode, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


class AuditLog:
    def __init__(self, protocol_version: str = "1.0", session_id: bytes = b""):
        self.protocol_version = protocol_version
        self.session_id = session_id
        self._events: dict[str, AuditEvent] = {}
        self._children: dict[str, set] = {}  # parent -> children

    def _would_cycle(self, event_id: str, parents: list) -> bool:
        """DFS from parents; if we reach event_id, a cycle would form."""
        stack = list(parents)
        seen = set()
        while stack:
            cur = stack.pop()
            if cur == event_id:
                return True
            if cur in seen:
                continue
            seen.add(cur)
            for child in self._children.get(cur, ()):
                stack.append(child)
        return False

    def add(self, event: AuditEvent, signing_key: bytes) -> str:
        # Invariant: parent count bound
        if len(event.parent_event_ids) > MAX_PARENT_EVENTS:
            raise AuditError(ErrorCode.CAUSAL_CYCLE,
                             f"Too many parents: {len(event.parent_event_ids)} > {MAX_PARENT_EVENTS}")
        # Invariant 7: self-reference forbidden
        if event.event_id in event.parent_event_ids:
            raise AuditError(ErrorCode.CAUSAL_CYCLE, "Event references itself as parent")
        # Invariant 8: acyclic known graph
        if self._would_cycle(event.event_id, event.parent_event_ids):
            raise AuditError(ErrorCode.CAUSAL_CYCLE, "Would create causal cycle")
        # Missing parents => unresolved (not rejected)
        event.unresolved_parents = [p for p in event.parent_event_ids
                                    if p not in self._events]
        # signature over canonical bytes
        event.signature = self._sign(event, signing_key)
        self._events[event.event_id] = event
        for p in event.parent_event_ids:
            self._children.setdefault(p, set()).add(event.event_id)
        return event.signature

    def _sign(self, event: AuditEvent, signing_key: bytes) -> str:
        header = {
            "eid": event.event_id,
            "par": event.parent_event_ids,
            "act": event.actor_node_id,
            "dom": event.actor_domain_id,
            "typ": event.event_type,
            "rid": event.rule_id,
            "rv": event.rule_version,
            "sb": event.state_before_hash,
            "sa": event.state_after_hash,
            "ev": event.evidence_hash,
            "rc": event.result_code,
            "ob": event.observed_at,
            "lc": event.logical_clock,
        }
        canonical = encode_deterministic({
            "ver": self.protocol_version,
            "sid": self.session_id,
            "hdr": header,
            "ph": hashlib.sha256(
                f"{event.event_type}:{event.result_code}".encode()
            ).hexdigest(),
        })
        return hashlib.sha256(canonical + signing_key).hexdigest()

    def verify_signature(self, event: AuditEvent, signing_key: bytes) -> bool:
        return event.signature == self._sign(event, signing_key)

    def count(self) -> int:
        return len(self._events)

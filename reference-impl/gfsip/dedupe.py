"""GFSIP/1.0 Idempotency / Dedupe Store (Sections 15, 21).

Implements limited-window deduplication for side-effect operations.
Duplicate within window => no second side effect (Section 28 vector).
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class DedupeOutcome(str, Enum):
    ACCEPTED = "accepted"        # first time -> execute
    DUPLICATE = "duplicate"      # already completed -> skip
    IN_PROGRESS = "in_progress"  # currently executing -> hold


@dataclass
class DedupeRecord:
    idempotency_key: str
    status: DedupeOutcome
    result_hash: Optional[str] = None
    processed_at: Optional[float] = None
    expires_at: float = 0.0


class DedupeStore:
    def __init__(self, window_seconds: float = 3600):
        self.window_seconds = window_seconds
        self._store: dict[str, DedupeRecord] = {}

    def _purge(self) -> None:
        now = time.time()
        expired = [k for k, r in self._store.items() if r.expires_at and now > r.expires_at]
        for k in expired:
            del self._store[k]

    def record(self, idempotency_key: str) -> DedupeOutcome:
        """Register an operation. Returns whether to execute it."""
        self._purge()
        now = time.time()
        rec = self._store.get(idempotency_key)
        if rec is None:
            self._store[idempotency_key] = DedupeRecord(
                idempotency_key=idempotency_key,
                status=DedupeOutcome.IN_PROGRESS,
                expires_at=now + self.window_seconds,
            )
            return DedupeOutcome.ACCEPTED
        if rec.status == DedupeOutcome.IN_PROGRESS:
            return DedupeOutcome.IN_PROGRESS
        if rec.status == DedupeOutcome.DUPLICATE:
            return DedupeOutcome.DUPLICATE
        return DedupeOutcome.DUPLICATE

    def complete(self, idempotency_key: str, result_hash: str) -> None:
        rec = self._store.get(idempotency_key)
        if rec is None:
            return
        rec.status = DedupeOutcome.DUPLICATE
        rec.result_hash = result_hash
        rec.processed_at = time.time()

    def count_side_effects(self) -> int:
        """Number of operations actually executed (for conformance checks)."""
        return sum(1 for r in self._store.values()
                   if r.status == DedupeOutcome.DUPLICATE and r.result_hash)

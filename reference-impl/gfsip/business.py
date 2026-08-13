"""GFSIP/1.0 Business Execution — pluggable side-effect handler.

The reference transport shipped with a no-op `_on_data` whose "result hash"
was a random placeholder, so audit events could not prove *what* a DATA frame
did. This module defines the BusinessHandler protocol plus a deterministic KV
store, so ACCEPTED DATA frames produce real, reproducible state transitions
and real result hashes (state_before / state_after) usable by Audit/1.
"""

import hashlib
import json
from typing import Any, Tuple

from .cbor_utils import encode_deterministic


class BusinessHandler:
    """Pluggable side-effect handler executed on ACCEPTED DATA frames.

    Implementations MUST be deterministic: the same (operation, payload,
    state_before) always produces the same (state_after, result).
    """

    def execute(self, operation: str, payload: bytes, state: Any) -> Tuple[Any, Any]:
        raise NotImplementedError

    def state_hash(self, state: Any) -> str:
        return "sha256:" + hashlib.sha256(encode_deterministic(state)).hexdigest()


class SimpleKVStore(BusinessHandler):
    """Deterministic key-value store used by the end-to-end demo.

    Supports the `inventory.reserve` operation: payload is a JSON object with
    `item` and `qty`; state tracks cumulative reserved quantities per item.
    """

    def __init__(self, initial: dict = None):
        self.state = dict(initial or {})

    def execute(self, operation: str, payload: bytes, state: Any) -> Tuple[Any, Any]:
        state = dict(state or {})
        if operation == "inventory.reserve":
            try:
                body = json.loads(payload.decode("utf-8")) if payload else {}
            except (ValueError, UnicodeDecodeError):
                body = {}
            item = str(body.get("item", "?"))
            qty = int(body.get("qty", 0))
            reserved = dict(state.get("reserved", {}))
            reserved[item] = reserved.get(item, 0) + qty
            state["reserved"] = reserved
            result = {"reserved": item, "qty": qty, "total": reserved[item]}
            return state, result
        return state, {"ok": False, "reason": "unknown_operation"}

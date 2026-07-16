"""Deterministic CBOR encode/decode (Section 7).

Uses cbor2 library with canonical configuration:
- Map keys sorted by length-then-lexicographic (deterministic)
- Shortest encoding for integers
- No indefinite-length strings or containers
"""

import cbor2


def encode_deterministic(obj: dict) -> bytes:
    """Encode a dict to canonical CBOR bytes."""
    return cbor2.dumps(obj, canonical=True)


def decode(data: bytes) -> dict:
    """Decode CBOR bytes to a Python dict."""
    if not isinstance(data, bytes):
        raise TypeError(f"Expected bytes, got {type(data).__name__}")
    result = cbor2.loads(data)
    if not isinstance(result, dict):
        raise TypeError(f"CBOR payload must decode to dict, got {type(result).__name__}")
    return result

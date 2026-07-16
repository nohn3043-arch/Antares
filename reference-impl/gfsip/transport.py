"""GFSIP/1.0 Transport abstraction.

The frozen wire format is bearer-agnostic (Section 6). This module provides
a deterministic in-memory synchronous transport for tests and demos.

Production deployments MUST replace this with a QUIC adapter using
ALPN `gfsip/1` (Section 6.1) or a TLS 1.3 TCP adapter (Section 6.2). The
Endpoint API is identical regardless of the underlying Transport.
"""

import collections
import time


class Link:
    """One directional pipe endpoint. Pair two Links for a full duplex path."""

    def __init__(self, name: str):
        self.name = name
        self._queue: collections.deque = collections.deque()
        self._peer: "Link" = None

    def attach(self, peer: "Link") -> None:
        self._peer = peer

    def send(self, data: bytes) -> None:
        if self._peer is None:
            raise RuntimeError("Link not connected")
        self._peer._queue.append(data)

    def recv(self, timeout: float = 2.0) -> bytes:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self._queue:
                return self._queue.popleft()
            time.sleep(0.001)
        raise TimeoutError(f"Link {self.name}: recv timed out after {timeout}s")

    def pending(self) -> bool:
        return bool(self._queue)


def make_link_pair() -> tuple[Link, Link]:
    """Create a connected pair of Links (A->B and B->A)."""
    a = Link("A")
    b = Link("B")
    a.attach(b)
    b.attach(a)
    return a, b

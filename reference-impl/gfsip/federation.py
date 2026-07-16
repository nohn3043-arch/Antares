"""GFSIP/1.0 Federation/1 — Domain Descriptor & Routing (Sections 18, 10).

Reference implementation validates descriptor fields and performs route
queries with visited-domain loop detection and hop limits.
Signature verification is simulated via HMAC (production: ed25519 + real CA).
"""

import hashlib
import hmac
import time
from dataclasses import dataclass, field
from typing import Optional

from .types import ErrorCode, MAX_ROUTE_HOPS


@dataclass
class TrustAnchor:
    key_id: str
    algorithm: str
    public_key: str


@dataclass
class Gateway:
    uri: str
    transport: str
    priority: int
    profiles: list


@dataclass
class DomainDescriptor:
    domain_id: str
    descriptor_version: int
    valid_from: float
    valid_until: float
    gateways: list = field(default_factory=list)
    services: list = field(default_factory=list)
    trust_anchors: list = field(default_factory=list)
    revocation_endpoints: list = field(default_factory=list)
    signature_algorithm: str = "ed25519"
    signature: str = ""

    def is_valid_now(self, now: Optional[float] = None) -> bool:
        now = time.time() if now is None else now
        return self.valid_from <= now <= self.valid_until


class FederationError(Exception):
    def __init__(self, code: ErrorCode, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


class FederationRegistry:
    def __init__(self, local_domain_id: str, secret: bytes):
        self.local_domain_id = local_domain_id
        self._secret = secret
        self._descriptors: dict[str, DomainDescriptor] = {}

    def register(self, desc: DomainDescriptor) -> None:
        if desc.domain_id in self._descriptors:
            existing = self._descriptors[desc.domain_id]
            if desc.descriptor_version <= existing.descriptor_version:
                raise FederationError(ErrorCode.POLICY_REJECTED,
                                      "Descriptor version must increase")
        if not desc.is_valid_now():
            raise FederationError(ErrorCode.DESCRIPTOR_EXPIRED,
                                  f"Descriptor expired for {desc.domain_id}")
        # simulated signature check
        body = f"{desc.domain_id}:{desc.descriptor_version}:{desc.valid_until}".encode()
        expected = hmac.new(self._secret, body, hashlib.sha256).hexdigest()[:16]
        if not hmac.compare_digest(desc.signature, expected):
            raise FederationError(ErrorCode.POLICY_REJECTED,
                                  "Descriptor signature invalid")
        self._descriptors[desc.domain_id] = desc

    def route_query(self, *, target_domain: str,
                    visited_domains: list, max_hops: int) -> dict:
        # Section 18: max_hops == 0 => ROUTE_HOP_LIMIT
        if max_hops <= 0:
            raise FederationError(ErrorCode.ROUTE_HOP_LIMIT, "max_hops reached 0")
        # Section 18: self already visited => ROUTE_LOOP
        if self.local_domain_id in visited_domains:
            raise FederationError(ErrorCode.ROUTE_LOOP, "Route loop detected")
        desc = self._descriptors.get(target_domain)
        if desc is None:
            return {"status": "unknown", "next_hop": None}
        return {
            "status": "resolved",
            "next_hop": desc.gateways[0].uri if desc.gateways else None,
            "domain": target_domain,
        }

"""GFSIP/1.0 Authentication & Authorization (Sections 11, 12).

Reference implementation uses HMAC-SHA256 over the handshake transcript to
simulate a "signature over transcript". Production MUST use the negotiated
method (mtls / signed-token / psk / hardware-attested) with real asymmetric
signatures and a verified certificate/key chain.
"""

import hashlib
import hmac
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .types import ErrorCode


class AuthMethod(str, Enum):
    MTLS = "mtls"
    SIGNED_TOKEN = "signed-token"
    PSK = "psk"
    HARDWARE_ATTESTED = "hardware-attested"


@dataclass
class AuthProof:
    method: str
    credential: str
    proof: str            # hex HMAC / signature over transcript
    key_id: str
    expires_at: float     # epoch seconds
    transcript_hash: str  # hex of transcript digest this proof covers


class AuthError(Exception):
    def __init__(self, code: ErrorCode, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


class Authenticator:
    """Builds and verifies authentication proofs (Section 12)."""

    def __init__(self, node_id: str, domain_id: str, shared_secret: bytes):
        self.node_id = node_id
        self.domain_id = domain_id
        self._secret = shared_secret

    def _transcript_digest(self, transcript: bytes) -> str:
        return hashlib.sha256(transcript).hexdigest()

    def make_proof(self, method: AuthMethod, key_id: str,
                   transcript: bytes, ttl: float = 300.0) -> AuthProof:
        digest = self._transcript_digest(transcript)
        mac = hmac.new(self._secret, digest.encode(), hashlib.sha256).hexdigest()
        return AuthProof(
            method=method.value,
            credential=f"ref:{key_id}",
            proof=mac,
            key_id=key_id,
            expires_at=time.time() + ttl,
            transcript_hash=digest,
        )

    def verify(self, proof: AuthProof, expected_node_id: str,
               transcript: bytes) -> None:
        """Raise AuthError on failure. Otherwise returns silently."""
        if proof.method not in {m.value for m in AuthMethod}:
            raise AuthError(ErrorCode.AUTH_FAILED, f"Unknown method {proof.method}")
        if time.time() > proof.expires_at:
            raise AuthError(ErrorCode.AUTH_FAILED, "Credential expired")
        digest = self._transcript_digest(transcript)
        if proof.transcript_hash != digest:
            raise AuthError(ErrorCode.AUTH_FAILED,
                            "Transcript mismatch (downgrade/replay suspected)")
        expected = hmac.new(self._secret, digest.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(proof.proof, expected):
            raise AuthError(ErrorCode.AUTH_FAILED, "Proof signature invalid")
        # Node identity is bound but NOT sufficient for authorization alone.
        if expected_node_id and expected_node_id not in proof.key_id:
            raise AuthError(ErrorCode.AUTH_FAILED, "Key id does not match node")

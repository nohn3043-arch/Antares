"""GFSIP/1.0 Authentication & Authorization (Sections 11, 12).

Produces and verifies Ed25519 signatures over the handshake transcript for
SIGNED_TOKEN and MTLS methods. The peer's public key is resolved through a
trust-anchor registry keyed by a stable key_id, so two nodes authenticate
without pre-sharing a symmetric secret.

PSK and HARDWARE_ATTESTED remain declared but intentionally unimplemented in
the reference node (production integrates KMS/HSM-backed attestation).
"""

import hashlib
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .types import ErrorCode
from .signing import sign as ed25519_sign, verify as ed25519_verify, TrustAnchorRegistry


class AuthMethod(str, Enum):
    MTLS = "mtls"
    SIGNED_TOKEN = "signed-token"
    PSK = "psk"
    HARDWARE_ATTESTED = "hardware-attested"


@dataclass
class AuthProof:
    method: str
    credential: str
    proof: str            # hex Ed25519 signature over the transcript
    key_id: str
    expires_at: float     # epoch seconds
    transcript_hash: str  # hex of transcript digest this proof covers


class AuthError(Exception):
    def __init__(self, code: ErrorCode, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


class Authenticator:
    """Builds and verifies Ed25519 authentication proofs (Section 12)."""

    def __init__(self, node_id: str, domain_id: str, signing_key: bytes,
                 trust_anchors: Optional[TrustAnchorRegistry] = None):
        self.node_id = node_id
        self.domain_id = domain_id
        self._signing_key = signing_key  # raw 32-byte Ed25519 private key
        self._trust_anchors = trust_anchors or TrustAnchorRegistry()

    @staticmethod
    def _transcript_digest(transcript: bytes) -> str:
        return hashlib.sha256(transcript).hexdigest()

    def make_proof(self, method: AuthMethod, key_id: str,
                   transcript: bytes, ttl: float = 300.0) -> AuthProof:
        if method not in (AuthMethod.SIGNED_TOKEN, AuthMethod.MTLS):
            raise AuthError(ErrorCode.AUTH_FAILED,
                            f"{method.value} requires KMS/HSM-backed integration")
        digest = self._transcript_digest(transcript)
        sig = ed25519_sign(self._signing_key, transcript)
        return AuthProof(
            method=method.value,
            credential=f"ed25519:{key_id}",
            proof=sig.hex(),
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
        if proof.transcript_hash != self._transcript_digest(transcript):
            raise AuthError(ErrorCode.AUTH_FAILED,
                            "Transcript mismatch (downgrade/replay suspected)")
        # Node identity is bound to the key_id but NOT sufficient for
        # authorization alone (authorization is a policy layer above).
        if expected_node_id and expected_node_id not in proof.key_id:
            raise AuthError(ErrorCode.AUTH_FAILED, "Key id does not match node")
        public_key = self._trust_anchors.get(proof.key_id)
        if public_key is None:
            raise AuthError(ErrorCode.AUTH_FAILED,
                            f"Unknown key_id {proof.key_id}")
        try:
            sig = bytes.fromhex(proof.proof)
        except (ValueError, TypeError):
            raise AuthError(ErrorCode.AUTH_FAILED, "Malformed proof signature")
        if not ed25519_verify(public_key, transcript, sig):
            raise AuthError(ErrorCode.AUTH_FAILED, "Proof signature invalid")

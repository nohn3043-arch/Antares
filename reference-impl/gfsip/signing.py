"""GFSIP/1.0 Asymmetric Signing (Ed25519) — keypairs, sign/verify, trust anchors.

Replaces the reference-implementation HMAC "signature simulation" with real
Ed25519 asymmetric signatures, so any third party holding a node's public key
can independently verify auth proofs and audit events without sharing a secret.

Key material is raw 32-byte Ed25519 (private / public). Production holds keys
in KMS/HSM; this module keeps the dependency surface minimal via `cryptography`.
"""

from typing import Dict, Optional, Tuple

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519


def generate_keypair() -> Tuple[bytes, bytes]:
    """Generate an Ed25519 keypair.

    Returns (private_key_bytes, public_key_bytes), both raw 32-byte values.
    """
    priv = ed25519.Ed25519PrivateKey.generate()
    pub = priv.public_key()
    return (
        priv.private_bytes(
            serialization.Encoding.Raw,
            serialization.PrivateFormat.Raw,
            serialization.NoEncryption(),
        ),
        pub.public_bytes(
            serialization.Encoding.Raw,
            serialization.PublicFormat.Raw,
        ),
    )


def sign(private_key: bytes, message: bytes) -> bytes:
    """Ed25519 signature over `message` using `private_key` (raw 32 bytes)."""
    key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key)
    return key.sign(message)


def verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
    """Return True if `signature` is valid for `message` under `public_key`."""
    try:
        key = ed25519.Ed25519PublicKey.from_public_bytes(public_key)
        key.verify(signature, message)
        return True
    except Exception:
        return False


def key_id_for(node_id: str) -> str:
    """Stable key_id for a node (matches the value sent in auth proofs)."""
    return f"urn:gfsip:key:{node_id}"


class TrustAnchorRegistry:
    """Maps a key_id to a trusted public key (raw 32 bytes).

    Verification resolves an auth proof's key_id through this registry to
    obtain the public key used to check the Ed25519 signature.
    """

    def __init__(self):
        self._keys: Dict[str, bytes] = {}

    def register(self, key_id: str, public_key: bytes) -> None:
        self._keys[key_id] = public_key

    def get(self, key_id: str) -> Optional[bytes]:
        return self._keys.get(key_id)

    def __contains__(self, key_id: str) -> bool:
        return key_id in self._keys


def make_trust_pair(node_a: str, node_b: str) -> Tuple[tuple, tuple]:
    """Generate two keypairs with mutually-registered trust anchors.

    Returns ((priv_a, anchors_a), (priv_b, anchors_b)) where each side trusts
    the other's public key under its stable key_id.
    """
    priv_a, pub_a = generate_keypair()
    priv_b, pub_b = generate_keypair()
    anchors_a = TrustAnchorRegistry()
    anchors_a.register(key_id_for(node_b), pub_b)
    anchors_b = TrustAnchorRegistry()
    anchors_b.register(key_id_for(node_a), pub_a)
    return (priv_a, anchors_a), (priv_b, anchors_b)

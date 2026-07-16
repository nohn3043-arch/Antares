"""GFSIP/1.0 Resume Service (Sections 13, 16).

Issue / verify opaque resume tokens bound to Session, Node ID, auth context,
expiry, version and profile set. Single-use or rotated (Section 16 rule 3-4).
"""

import cbor2
import hashlib
import hmac
import os
import time
from dataclasses import dataclass
from typing import Optional

from .cbor_utils import encode_deterministic, decode
from .types import ErrorCode


@dataclass
class ResumeToken:
    session_id: bytes
    node_id: str
    auth_context_id: str
    expires_at: float
    version: str
    profiles: list
    nonce: bytes


class ResumeError(Exception):
    def __init__(self, code: ErrorCode, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


class ResumeService:
    def __init__(self, secret: bytes, ttl: float = 1800.0):
        self._secret = secret
        self._ttl = ttl
        self._used: set[bytes] = set()  # single-use tracking

    def issue(self, session_id: bytes, node_id: str, auth_context_id: str,
              version: str, profiles: list) -> bytes:
        tok = ResumeToken(
            session_id=session_id,
            node_id=node_id,
            auth_context_id=auth_context_id,
            expires_at=time.time() + self._ttl,
            version=version,
            profiles=list(profiles),
            nonce=os.urandom(32),
        )
        body = encode_deterministic({
            "sid": tok.session_id,
            "nid": tok.node_id,
            "ac": tok.auth_context_id,
            "exp": tok.expires_at,
            "ver": tok.version,
            "prof": tok.profiles,
            "non": tok.nonce,
        })
        mac = hmac.new(self._secret, body, hashlib.sha256).digest()
        return body + mac  # opaque token = body || mac

    def verify(self, token: bytes, current_node_id: str,
               auth_context_id: str) -> ResumeToken:
        if len(token) < 32:
            raise ResumeError(ErrorCode.RESUME_EXPIRED, "Malformed token")
        body, mac = token[:-32], token[-32:]
        expected = hmac.new(self._secret, body, hashlib.sha256).digest()
        if not hmac.compare_digest(mac, expected):
            raise ResumeError(ErrorCode.RESUME_EXPIRED, "Token MAC invalid")
        d = decode(body)
        tok = ResumeToken(
            session_id=d["sid"], node_id=d["nid"], auth_context_id=d["ac"],
            expires_at=d["exp"], version=d["ver"], profiles=d["prof"], nonce=d["non"],
        )
        if time.time() > tok.expires_at:
            raise ResumeError(ErrorCode.RESUME_EXPIRED, "Token expired")
        # Rule 2: current Node ID MUST match token
        if current_node_id != tok.node_id:
            raise ResumeError(ErrorCode.RESUME_IDENTITY_MISMATCH,
                              "Token node id mismatch")
        # Rule: auth context revoked => resume fails (caller checks separately)
        if auth_context_id != tok.auth_context_id:
            raise ResumeError(ErrorCode.AUTH_FAILED,
                              "Auth context changed since issue")
        # Rule 3-4: single use
        if tok.nonce in self._used:
            raise ResumeError(ErrorCode.RESUME_EXPIRED, "Token already consumed")
        return tok

    def consume(self, tok: ResumeToken) -> None:
        self._used.add(tok.nonce)

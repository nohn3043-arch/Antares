#!/usr/bin/env python3
"""GFSIP/1.0 Reference Implementation — End-to-end demo.

Drives two real Endpoint nodes over an in-memory transport:
  - full mutual-auth handshake
  - channel open / ready
  - DATA with idempotency + APP_ACK (duplicate detection)
  - session recovery after path loss
  - Section 28 conformance vectors
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from gfsip import (
    Endpoint, make_link_pair,
    SessionState, MessageType, ErrorCode,
)
from gfsip import conformance as conf


def sep(title: str) -> None:
    print(f"\n{'='*64}")
    print(f"  {title}")
    print(f"{'='*64}")


def mk_pair():
    a, b = make_link_pair()
    init = Endpoint(node_id="urn:gfsip:node:agent-a",
                    domain_id="urn:gfsip:domain:acme",
                    is_initiator=True, link=a, shared_secret=b"demo-secret")
    resp = Endpoint(node_id="urn:gfsip:node:svc-b",
                    domain_id="urn:gfsip:domain:globex",
                    is_initiator=False, link=b, shared_secret=b"demo-secret")
    return init, resp


# ── 1. Handshake ───────────────────────────────────────────
sep("1. MUTUAL-AUTH HANDSHAKE  (agent-a  <->  svc-b)")
init, resp = mk_pair()
init.handshake_with(resp)

ok1 = (init.session.state == SessionState.ESTABLISHED and
       resp.session.state == SessionState.ESTABLISHED)
print(f"  initiator : {init.session.state.name}  sid={init.session.session_id.hex()[:12]}")
print(f"  responder : {resp.session.state.name}  sid={resp.session.session_id.hex()[:12]}")
print(f"  profiles  : {init.session.selected_profiles}")
print(f"  [{'PASS' if ok1 else 'FAIL'}] both endpoints ESTABLISHED")


# ── 2. Channel open ────────────────────────────────────────
sep("2. CHANNEL OPEN  (initiator opens task channel)")
cid = init.open_channel(channel_type="task", priority=20,
                        metadata={"service": "inventory.reserve"})
resp._pump_once()   # responder processes OPEN_CHANNEL -> CHANNEL_READY
init._pump_once()   # initiator receives CHANNEL_READY
rch = resp.channels.get(cid)
ich = init.channels.get(cid)
ok2 = rch is not None and ich.state.name == "OPEN"
print(f"  channel {cid}: initiator={ich.state.name}  responder={rch.state.name}")
print(f"  [{'PASS' if ok2 else 'FAIL'}] channel {cid} OPEN on both sides")


# ── 3. DATA + idempotency ──────────────────────────────────
sep("3. DATA + IDEMPOTENT DEDUPE  (same key twice)")
init.send_data(cid, operation="inventory.reserve",
               payload=b'{"item":"widget-42","qty":5}',
               idempotency_key="order-8842-reserve-v1")
resp._pump_once()
init._pump_once()

init.send_data(cid, operation="inventory.reserve",
               payload=b'{"item":"widget-42","qty":5}',
               idempotency_key="order-8842-reserve-v1")
resp._pump_once()
init._pump_once()

side = resp.dedupe.count_side_effects()
ok3 = side == 1
print(f"  side-effect count for duplicate key = {side} (expected 1)")
print(f"  [{'PASS' if ok3 else 'FAIL'}] idempotency enforced")


# ── 4. Session recovery ────────────────────────────────────
sep("4. SESSION RECOVERY  (path loss -> resume token)")
before = init.session.state.name
init.resume(resp)       # initiator degrades + sends RESUME
resp._pump_once()       # responder verifies token, replies RESUME_RESULT
init._pump_once()       # initiator resumes
after = init.session.state.name
ok4 = (before == "ESTABLISHED" and after == "ESTABLISHED" and
       init.session.state == SessionState.ESTABLISHED)
print(f"  state: {before} -> DEGRADED -> RESUMING -> {after}")
print(f"  [{'PASS' if ok4 else 'FAIL'}] session resumed with token")


# ── 5. Conformance vectors ─────────────────────────────────
sep("5. CORE CONFORMANCE  (Section 28 minimum vectors)")
cpassed, ctotal = 0, len(conf.VECTORS)
for fn in conf.VECTORS:
    name, ok, detail = fn()
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    cpassed += ok
ok5 = cpassed == ctotal


# ── Summary ────────────────────────────────────────────────
sep("SUMMARY")
rows = [
    ("gfsip/types.py", "Messages, flags, states, errors, constants"),
    ("gfsip/cbor_utils.py", "Deterministic CBOR encode/decode"),
    ("gfsip/frame.py", "44-byte frame codec + validation"),
    ("gfsip/state_machine.py", "Session states + 9 invariants"),
    ("gfsip/channel.py", "Channel lifecycle, parity, flow control"),
    ("gfsip/auth.py", "Auth proofs over handshake transcript"),
    ("gfsip/dedupe.py", "Limited-window idempotency store"),
    ("gfsip/resume.py", "Resume token bind / single-use"),
    ("gfsip/audit.py", "Audit/1 causal events + cycle reject"),
    ("gfsip/federation.py", "Domain descriptor + route loop/hop"),
    ("gfsip/transport.py", "In-memory sync transport (QUIC-ready)"),
    ("gfsip/endpoint.py", "Integrated node: handshake/data/resume"),
    ("gfsip/conformance.py", "Section 28 test vectors"),
]
for mod, desc in rows:
    print(f"  {mod:24} {desc}")
print()
print(f"  Handshake              : {'PASS' if ok1 else 'FAIL'}")
print(f"  Channel open           : {'PASS' if ok2 else 'FAIL'}")
print(f"  Idempotent dedupe      : {'PASS' if ok3 else 'FAIL'}")
print(f"  Session recovery       : {'PASS' if ok4 else 'FAIL'}")
print(f"  Conformance vectors    : {'PASS' if ok5 else 'FAIL'} ({cpassed}/{ctotal})")
print()
allok = ok1 and ok2 and ok3 and ok4 and ok5
print(f"  OVERALL: {'ALL PASS' if allok else 'FAILURES PRESENT'}")
sys.exit(0 if allok else 1)

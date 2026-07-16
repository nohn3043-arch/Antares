# The virtual world requires a universal and stable network.

# Antares GFSIP v1.0

## Secure Federated Interoperability Protocol for Cross-Organizational AI Agents

> Encrypted, multi-channel, recoverable cross-domain communication
> for services, AI agents, devices, and organizations — no central authority required.

---

**Version** `1.0` · **Status** `Implementation-Ready Candidate` · **Published** `2026-07-16`  
**Base Transport** `QUIC (ALPN: gfsip/1)` · **Optional** `TCP + TLS 1.3`

---

## Overview

GFSIP is an application-layer protocol that enables independent organizations,
network domains, devices, services, and AI agents to establish secure,
recoverable communication sessions while retaining full autonomy over their
identity, policies, and infrastructure.

It sits above QUIC (or TCP+TLS 1.3), providing session management,
multi-channel multiplexing, limited-window idempotency, optional signed
causal audit trails, and cross-domain federation — all without requiring
a global root of trust, central directory, or shared identity system.

---

## Key Capabilities

| # | Capability | Description |
|---|---|---|
| 1 | **Encrypted Sessions** | Mutual-TLS or token-based authenticated sessions over QUIC |
| 2 | **Multi-Channel** | Independent logical channels within a single session |
| 3 | **Session Recovery** | Resume sessions across network switches without re-authentication |
| 4 | **Idempotent Side Effects** | Limited-window deduplication via idempotency keys |
| 5 | **Structured Errors** | Numeric, machine-readable error codes with scope and retry hints |
| 6 | **Causal Audit (opt-in)** | Signed event records with declared causal predecessors |
| 7 | **Cross-Domain Federation** | Multi-trust-anchor routing with signed domain descriptors |
| 8 | **Fault Isolation** | Single-domain failure does not block intra-domain traffic |

---

## Why GFSIP?

| Concern | GFSIP Approach |
|---|---|
| Central authority risk | Federation model — each domain governs itself |
| Network disruption | Session recovery with state synchronization |
| Duplicate operations | Application-level idempotency within a configurable window |
| Audit & accountability | Optional signed causal event graph (Audit/1 profile) |
| Vendor lock-in | Open specification; no proprietary components |
| Transport lock-in | QUIC required; TCP+TLS 1.3 as optional fallback |

---

## Repository Contents

| File | Purpose |
|---|---|
| `GFSIP_v1.0_protocol_spec.md` | Full protocol specification (33 sections) |
| `gfsip-state-machine.json` | Machine-readable state machine definition |
| `gfsip-message-schema.json` | Logical message JSON Schema |
| `gfsip-error-registry.json` | Numeric error code registry |
| `gfsip-conformance-checklist.csv` | Conformance test checklist |
| `gfsip-traceability-matrix.csv` | Requirement → spec → test → implementation → responsibility mapping |
| `CHANGELOG_v1.0.md` | v0.1 → v1.0 changelog |
| `SHA256SUMS.txt` | File integrity checksums |

---

## Protocol Profiles

### Core/1 — Mandatory

Every conformant implementation **MUST** support:

- QUIC transport with ALPN `gfsip/1`
- Version negotiation
- Mutual authentication interface
- Session & channel management
- `DATA` with application-level acknowledgment (`APP_ACK`)
- Message ID and idempotency key
- Session recovery (resume tokens)
- `PING` / `PONG` liveness
- Graceful shutdown (`GOAWAY`)
- Structured `ERROR` frames
- Resource limit negotiation
- Safe ignoring of unknown optional extensions

### Audit/1 — Optional

Adds signed causal event recording:

- `EVENT` frames with declared direct causal predecessors
- Actor identity, rule version, and state before/after hashes
- Deterministic event signing
- Self-loop and known-cycle rejection

### Federation/1 — Optional

Adds cross-domain routing:

- Signed `DomainDescriptor` objects
- Multi-trust-anchor configuration
- Cross-domain route queries (`ROUTE_QUERY` / `ROUTE_RESULT`)
- Descriptor expiry, revocation, and fault isolation

---

## On the Wire

GFSIP uses a **44-byte fixed header**:

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Magic = "GFS1"                         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Major | Minor | Type          | Flags                         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Header Length                 | Reserved                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                         Payload Length                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
|                         Session ID (128)                      |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                          Sequence (64)                        |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                          Channel ID                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                 Extension Header (deterministic CBOR)         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                         Payload (variable)                    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

- Extension headers use **deterministic CBOR**
- Integers: big-endian, shortest encoding
- 18 standard message types (`0x01`–`0x16`), `0x80`–`0xFF` reserved for private experiments

---

## Getting Started

A Python reference implementation is available in [`reference-impl/`](./reference-impl/).
Install dependencies and run the demo:

```bash
cd reference-impl
pip install -r requirements.txt
python demo.py
```

### Implementation Order

```
 1. Frame Codec            — 44-byte header parser/serializer
 2. Session State Machine  — NEW → NEGOTIATING → AUTHENTICATING → ESTABLISHED → ...
 3. QUIC Adapter           — ALPN gfsip/1 stream mapping
 4. Authentication         — mTLS or signed-token handler
 5. Channel Manager        — Channel lifecycle (IDLE → OPEN → CLOSED)
 6. DATA / APP_ACK         — Application messaging with deduplication store
 7. Resume Service         — Token-based session recovery
 8. Core Conformance       — Pass all mandatory tests
 9. Second Implementation  — Independent codebase for interop validation
10. Audit/1 (optional)     — Signed causal event recording
11. Federation/1 (opt.)    — Cross-domain descriptors and routing
```

### Conformance

To claim **GFSIP/1.0 Core Conformant**, an implementation **MUST**:

1. Implement the 44-byte fixed header
2. Support deterministic CBOR encoding
3. Use QUIC with ALPN `gfsip/1`
4. Pass all Core mandatory conformance tests
5. Publish implementation version, configuration summary, and test report
6. Have zero known unpatched critical security vulnerabilities

Audit/1 and Federation/1 conformance must be declared independently.
See [`gfsip-conformance-checklist.csv`](./gfsip-conformance-checklist.csv).

---

## Use Cases

| Domain | Example |
|---|---|
| **Enterprise Integration** | Cross-organization workflow orchestration |
| **AI Agent Networks** | Multi-agent task coordination with audit trail |
| **IoT / Edge** | Device-to-cloud session recovery across network changes |
| **Finance / Compliance** | Signed causal audit trails for regulatory reporting |
| **Healthcare** | Federated data exchange with domain-level policy enforcement |
| **Robotics** | Reliable command channels with idempotent safety operations |

---

## Project Status

| Milestone | Status |
|---|---|
| Specification v1.0 (interface frozen) | ✅ Complete |
| Machine-readable state machine & schema | ✅ Complete |
| Conformance checklist & traceability matrix | ✅ Complete |
| Two independent implementations | 🔲 In progress |
| Public interoperability report | 🔲 Pending |
| Independent security audit | 🔲 Pending |
| Three production pilot domains | 🔲 Pending |
| Formal standards body process | 🔲 Future |

---

## Non-Goals

GFSIP does **not** aim to:

- Replace IP, BGP, DNS, QUIC, or TLS
- Provide a global root of authority
- Guarantee zero-failure communication
- Enable communication without a physical path
- Provide unbounded Exactly-Once semantics
- Automatically determine legal liability
- Infer causality from temporal ordering

---

## Known Limitations

1. Sessions cannot be recovered if both peers lose persistent state.
2. Deduplication is bounded by window size and storage reliability.
3. Signed events attest to byte representation, not real-world truth.
4. Multi-trust-anchor configurations require domain-level trust policy.
5. Gateways may refuse interconnection.
6. No communication without an alternative physical path.

---

## License

This specification and associated artifacts are licensed under the
**Creative Commons Attribution 4.0 International** (CC BY 4.0).

You are free to share, adapt, implement, and distribute this work for
any purpose — including commercially — provided you give appropriate
credit to the GFSIP Contributors.

See [`LICENSE`](./LICENSE) for full legal terms.

---

## Contributing

This is a v1.0 frozen specification. Contributions should target:

- Implementation experience reports
- Interoperability test results
- Security audit findings
- Profile extensions (via the extension registry mechanism)

For the full specification, start with
[`GFSIP_v1.0_protocol_spec.md`](./GFSIP_v1.0_protocol_spec.md).

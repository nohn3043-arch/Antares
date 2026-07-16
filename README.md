<p align="center">
  <em>The virtual world requires a universal and stable network.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0-D4AF37?style=flat-square" alt="version">
  <img src="https://img.shields.io/badge/status-implementation_ready-2C2C2C?style=flat-square" alt="status">
  <img src="https://img.shields.io/badge/transport-QUIC%20|%20TLS%201.3-2C2C2C?style=flat-square" alt="transport">
  <img src="https://img.shields.io/badge/license-CC%20BY%204.0-2C2C2C?style=flat-square" alt="license">
  <img src="https://img.shields.io/badge/frame-44%20bytes-2C2C2C?style=flat-square" alt="frame">
</p>

---

&nbsp;

## ✦ Antares — GFSIP v1.0

**Global Federated Stable Interoperability Protocol**

Encrypted, multi-channel, recoverable cross-domain communication for services, AI agents, devices, and organizations — **no central authority required.**

&nbsp;

## ✦ Protocol Stack

```mermaid
graph TD
    subgraph "Application"
        APP(("AI Agents<br/>Services<br/>Devices<br/>Organizations")):::app
    end

    subgraph "GFSIP Layer"
        SESS(("Session<br/>Management")):::gfsip
        CHAN(("Multi-Channel<br/>Multiplexing")):::gfsip
        IDEM(("Idempotency<br/>Deduplication")):::gfsip
        RECV(("Session<br/>Recovery")):::gfsip
        AUDIT(("Causal Audit<br/>(optional)")):::gfsip_opt
        FED(("Cross-Domain<br/>Federation (optional)")):::gfsip_opt
    end

    subgraph "Transport"
        QUIC(("QUIC<br/>ALPN: gfsip/1")):::transport
        TCP(("TCP + TLS 1.3<br/>(fallback)")):::transport_fallback
    end

    APP --> SESS
    SESS --> CHAN
    CHAN --> IDEM
    IDEM --> RECV
    AUDIT -.-> SESS
    FED -.-> CHAN
    SESS --> QUIC
    SESS -.-> TCP

    classDef app fill:#FAFAFA,stroke:#D4AF37,stroke-width:1px,color:#2C2C2C
    classDef gfsip fill:#F5F0E6,stroke:#C9A96E,stroke-width:1px,color:#2C2C2C
    classDef gfsip_opt fill:#FAFAFA,stroke:#B8B8B8,stroke-width:1px,stroke-dasharray:4,color:#2C2C2C
    classDef transport fill:#FAFAFA,stroke:#D4AF37,stroke-width:2px,color:#2C2C2C
    classDef transport_fallback fill:#FAFAFA,stroke:#E0E0E0,stroke-width:1px,stroke-dasharray:4,color:#8B8B8B
```

&nbsp;

## ✦ Session Lifecycle

```mermaid
stateDiagram-v2
    [*] --> NEW
    NEW --> NEGOTIATING : version negotiation
    NEGOTIATING --> AUTHENTICATING : mTLS / token
    AUTHENTICATING --> ESTABLISHED : handshake complete
    ESTABLISHED --> CLOSING : GOAWAY
    CLOSING --> CLOSED

    ESTABLISHED --> RECOVERING : network disruption
    RECOVERING --> ESTABLISHED : resume token valid
    RECOVERING --> NEW : resume failed

    CLOSED --> [*]

    note right of ESTABLISHED : DATA · APP_ACK · PING/PONG<br/>Multi-channel active
```

&nbsp;

## ✦ 44-byte Fixed Header

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
|                    Session ID (128 bits)                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                     Sequence (64 bits)                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                      Channel ID (32 bits)                     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|              Extension Header (deterministic CBOR)            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

&nbsp;

## ✦ Key Capabilities

| # | Capability | Approach |
|---|-----------|----------|
| 1 | **Encrypted Sessions** | mTLS / token-based over QUIC |
| 2 | **Multi-Channel** | Independent logical channels per session |
| 3 | **Session Recovery** | Resume across network switches |
| 4 | **Idempotent Side Effects** | Limited-window key deduplication |
| 5 | **Structured Errors** | Numeric codes with scope + retry hints |
| 6 | **Causal Audit** | Signed event records with causal predecessors |
| 7 | **Cross-Domain Federation** | Multi-trust-anchor routing |
| 8 | **Fault Isolation** | Single-domain failure → no blocking |

&nbsp;

## ✦ Protocol Profiles

| Profile | Status | Content |
|---------|--------|---------|
| `Core/1` | **Mandatory** | QUIC, version negotiation, auth, session/channel, DATA+ACK, PING/PONG, GOAWAY, errors, recovery, idempotency |
| `Audit/1` | Optional | Signed causal event graph, identity binding, cycle rejection |
| `Federation/1` | Optional | Domain descriptors, multi-trust-anchor, route queries, expiry/revocation |

&nbsp;

## ✦ Quick Start

```bash
cd reference-impl
pip install -r requirements.txt

# 5-scenario end-to-end demo
python demo.py

# Conformance vectors (9/9 pass)
python conformance.py
```

&nbsp;

## ✦ Use Cases

> Enterprise Integration · AI Agent Networks · IoT / Edge · Finance Compliance · Healthcare · Robotics

&nbsp;

## ✦ Project Status

| Milestone | Status |
|-----------|--------|
| Specification v1.0 | ✅ Complete |
| State machine & schema | ✅ Complete |
| Conformance checklist | ✅ Complete |
| Two independent implementations | 🔲 In progress |
| Public interop report | 🔲 Pending |
| Independent security audit | 🔲 Pending |

&nbsp;

---

<p align="center">
  <a href="./GFSIP_v1.0_protocol_spec.md">Protocol Spec</a>
  &nbsp;·&nbsp;
  <a href="mailto:ai@nohnlins.com">ai@nohnlins.com</a>
</p>
<p align="center">
  <sub>CC BY 4.0 · GFSIP Contributors</sub>
</p>

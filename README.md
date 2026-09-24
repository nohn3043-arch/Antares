<p align="center">
  <img src="assets/banner.svg" alt="ANTARES banner" style="width:100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/protocol-D4AF37?style=flat-square" alt="protocol">
  <img src="https://img.shields.io/badge/quic-D4AF37?style=flat-square" alt="quic">
  <img src="https://img.shields.io/badge/federation-D4AF37?style=flat-square" alt="federation">
  <img src="https://img.shields.io/badge/gfsip-v1.0-D4AF37?style=flat-square" alt="gfsip-v1.0">
</p>

<blockquote align="center">
  <em>Global Federated Stable Interoperability Protocol GFSIP v1.0</em>
</blockquote>

<p align="center">
[简体中文](README-zh.md) | English
</p>

<div style="max-width:880px;margin:0 auto;padding:0 16px">

## ✦ About

<p style="font-size:15px;line-height:1.8;color:#2C2C2C">ANTARES is GFSIP v1.0 — the Global Federated Stable Interoperability Protocol. It provides encrypted, multiplexed, recoverable cross-domain communication for services, AI agents, devices, and organizations, without a central authority. With QUIC as the mandatory transport layer and deterministic CBOR serialization, it has built-in session resumption, idempotent deduplication, and causal audit, serving as the stable foundation of a decentralized network.</p>

<p align="center">
  <img src="assets/overview.svg" alt="ANTARES overview" style="width:100%">
</p>

</div>

<p align="center">— ✦ —</p>

## ✦ Core Capabilities

<div style="max-width:880px;margin:0 auto;padding:0 16px">

<table style="width:100%;border-collapse:collapse;font-size:14px">
  <tr><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">#</th><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">Capability</th><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">Description</th></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">1</td><td style="padding:8px;border-bottom:1px solid #F0EAD9"><strong>Encrypted Session</strong></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">Mutually authenticated TLS or token-authenticated sessions over QUIC</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">2</td><td style="padding:8px;border-bottom:1px solid #F0EAD9"><strong>Multiplexing</strong></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">Independent logical channels within a single session</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">3</td><td style="padding:8px;border-bottom:1px solid #F0EAD9"><strong>Session Resumption</strong></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">Resume sessions without re-authentication after network handover</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">4</td><td style="padding:8px;border-bottom:1px solid #F0EAD9"><strong>Idempotent Side Effects</strong></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">Windowed deduplication via idempotency keys</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">5</td><td style="padding:8px;border-bottom:1px solid #F0EAD9"><strong>Causal Audit (optional)</strong></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">Signed event records with declared causal predecessors</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">6</td><td style="padding:8px;border-bottom:1px solid #F0EAD9"><strong>Cross-Domain Federation</strong></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">Multi-trust-anchor routing + signed domain descriptors</td></tr>
  <tr><td style="padding:8px">7</td><td style="padding:8px"><strong>Fault Isolation</strong></td><td style="padding:8px">A single domain failure does not block intra-domain traffic</td></tr>
</table>

</div>

<p align="center">— ✦ —</p>

## ✦ Wire Format

<div style="max-width:880px;margin:0 auto;padding:0 16px">

<p style="font-size:15px;line-height:1.8;color:#2C2C2C">GFSIP uses a <strong>44-byte fixed-length header</strong> over QUIC, with ALPN <code style="background:#F5F0E6;padding:2px 6px;border-radius:3px;color:#C9A96E">gfsip/1</code>. Extension headers use deterministic CBOR (big-endian, shortest encoding). 18 standard message types (<code>0x01</code>–<code>0x16</code>) cover the full lifecycle: handshake, channel management, data transfer, session resumption, audit events, and federation routing.</p>

</div>

<p align="center">— ✦ —</p>

## ✦ Repository Contents

<div style="max-width:880px;margin:0 auto;padding:0 16px">

<table style="width:100%;border-collapse:collapse;font-size:14px">
  <tr><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">File</th><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">Purpose</th></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9"><code>GFSIP_v1.0_protocol_spec.md</code></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">Full protocol specification (33 sections)</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9"><code>gfsip-state-machine.json</code></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">Machine-readable state machine definition</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9"><code>gfsip-message-schema.json</code></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">Logical message JSON Schema</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9"><code>gfsip-error-registry.json</code></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">Numeric error code registry</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9"><code>gfsip-conformance-checklist.csv</code></td><td style="padding:8px;border-bottom:1px solid #F0EAD9">Conformance test checklist</td></tr>
  <tr><td style="padding:8px"><code>reference-impl/</code></td><td style="padding:8px">Python reference implementation — frame codec, state machine, channel management, authentication, deduplication, resumption, audit, federation, end-to-end demo (9/9 conformance vectors passing)</td></tr>
</table>

</div>

<p align="center">— ✦ —</p>

## ✦ Protocol Profile

<div style="max-width:880px;margin:0 auto;padding:0 16px">

<p style="font-size:15px;line-height:1.8;color:#2C2C2C"><strong style="color:#C9A96E">Core/1 (mandatory)</strong> — QUIC transport, version negotiation, mutual authentication, session and channel management, session resumption, structured errors, graceful shutdown.</p>

<p style="font-size:15px;line-height:1.8;color:#2C2C2C"><strong style="color:#C9A96E">Audit/1 (optional)</strong> — Signed causal event records with declared causal predecessors, actor identity, rule version, and pre/post state hashes; rejects self-loops and known cycles.</p>

<p style="font-size:15px;line-height:1.8;color:#2C2C2C"><strong style="color:#C9A96E">Federation/1 (optional)</strong> — Cross-domain routing via signed <code>DomainDescriptor</code> objects, multi-trust-anchor configuration, descriptor expiration / revocation, and fault isolation.</p>

</div>

<p align="center">— ✦ —</p>

## ✦ Quick Start

```bash
# Install SDK (PyPI)
pip install gfsip

# Run end-to-end demo (clone the repo to get demo files)
git clone https://github.com/nohn3043-arch/Antares.git
cd Antares/reference-impl
pip install -r requirements.txt
python demo.py                # Sync API demo: handshake -> channel -> data -> dedup -> resume
python async_demo.py          # Async API demo: await connect/open_channel/send (zero manual pump)
python gfsip/conformance.py   # 9/9 Section 28 minimal conformance vectors — all passing
```

<p align="center">— ✦ —</p>

## ✦ Application Scenarios

<div style="max-width:880px;margin:0 auto;padding:0 16px">

- **AI Agent Networks** — Multi-agent task collaboration across organizational boundaries, with auditable trails
- **Enterprise Integration** — Cross-organizational workflow orchestration without a central authority
- **IoT / Edge** — Device-to-cloud session resumption under network handover
- **Finance / Compliance** — Signed causal audit chains for regulatory reporting
- **Healthcare** — Federated data exchange with domain-level policy enforcement
- **Robotics** — Reliable command channels for idempotent safe operations

</div>

<p align="center">— ✦ —</p>

## ✦ Project Status

<div style="max-width:880px;margin:0 auto;padding:0 16px">

<table style="width:100%;border-collapse:collapse;font-size:14px">
  <tr><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">Milestone</th><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">Status</th></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">Spec v1.0 (interface frozen)</td><td style="padding:8px;border-bottom:1px solid #F0EAD9">✅ Done</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">Machine-readable state machine and schemas</td><td style="padding:8px;border-bottom:1px solid #F0EAD9">✅ Done</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">Python reference implementation (9/9 conformance)</td><td style="padding:8px;border-bottom:1px solid #F0EAD9">✅ Done</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">PyPI package release (pip install gfsip)</td><td style="padding:8px;border-bottom:1px solid #F0EAD9">✅ Done</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">Async high-level API (AsyncEndpoint, zero manual pump)</td><td style="padding:8px;border-bottom:1px solid #F0EAD9">✅ Done</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">Independent second implementation</td><td style="padding:8px;border-bottom:1px solid #F0EAD9">🔲 In progress</td></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9">Public interoperability report</td><td style="padding:8px;border-bottom:1px solid #F0EAD9">🔲 Todo</td></tr>
  <tr><td style="padding:8px">Production pilot domain</td><td style="padding:8px">🔲 Todo</td></tr>
</table>

</div>

<p align="center">— ✦ —</p>

## ✦ Ecosystem

ANTARES is a member of the NOHN AI ecosystem — a family of projects built around second-perspective causal audit and deterministic execution:

| Project | Repository | Role |
|---|---|---|
| **Second-Perspective (GCAE)** | [nohn3043-arch/second-perspective](https://github.com/nohn3043-arch/second-perspective) | Global cognitive audit engine — five-operator causal audit core (IMDA 95/100) |
| **NOMOS** | [nohn3043-arch/second-perspective](https://github.com/nohn3043-arch/second-perspective) (`Intelligent-Decision-Hub--Nomos` branch) | Auditable deterministic decision hub (IMDA 95/100) |
| **SPL-G1** | [nohn3043-arch/SPL-G1](https://github.com/nohn3043-arch/SPL-G1) | Hardware causal-audit trusted compute unit (TCU) |
| **SPL-Virtual-World-Base** | [nohn3043-arch/Second-Reality](https://github.com/nohn3043-arch/Second-Reality) | Virtual-world and metaverse infrastructure (Constitution / Law / Bridge) |
| **Story-Engine** | [nohn3043-arch/story-engine](https://github.com/nohn3043-arch/story-engine) | Long-form narrative consistency engine |
| **Antares** | [nohn3043-arch/Antares](https://github.com/nohn3043-arch/Antares) | GFSIP v1.0 — federated stable interoperability protocol with causal audit |
| **Anthropomorphic-Agent-Engine** | [nohn3043-arch/Anthropomorphic-Agent-Engine](https://github.com/nohn3043-arch/Anthropomorphic-Agent-Engine) | Deterministic anthropomorphic psychology engine (SPL Pure Core V8.0) |
| **PAGES** | [nohn3043-arch/pages](https://github.com/nohn3043-arch/pages) | Official NOHN AI ecosystem landing page |

<p align="center">— ✦ —</p>

## ✦ License

This repository uses a **dual-track license**:

<table style="width:100%;border-collapse:collapse;font-size:14px">
  <tr><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">Content</th><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">License</th><th style="text-align:left;color:#C9A96E;padding:8px;border-bottom:1px solid #E5DCC4">File</th></tr>
  <tr><td style="padding:8px;border-bottom:1px solid #F0EAD9"><strong>Code implementation</strong> (the Python package <code>gfsip</code> under <code>reference-impl/</code>)</td><td style="padding:8px;border-bottom:1px solid #F0EAD9"><a href="https://www.apache.org/licenses/LICENSE-2.0">Apache License 2.0</a></td><td style="padding:8px;border-bottom:1px solid #F0EAD9"><a href="./LICENSE"><code>LICENSE</code></a></td></tr>
  <tr><td style="padding:8px"><strong>Protocol specification and documentation</strong> (<code>GFSIP_v1.0_protocol_spec.md</code>, <code>gfsip-*.json</code>, <code>gfsip-*.csv</code>, <code>assets/</code> diagrams)</td><td style="padding:8px"><a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></td><td style="padding:8px"><a href="./LICENSE-SPEC.md"><code>LICENSE-SPEC.md</code></a></td></tr>
</table>

Apache-2.0 permits commercial use, modification, and distribution, and includes an **express patent grant**; CC BY 4.0 permits any use and redistribution (including commercial use) with attribution only — the open attribution license for the specification serves GFSIP's goal of dissemination as an open standard.

> **Irrevocable notice**: Versions up to and including v1.0 were previously released in their entirety under CC BY 4.0 (including code). That license is irrevocable under its terms, and those versions will remain permanently usable under CC BY 4.0. The dual-track arrangement above takes effect from the next version.

- **Contact**: International / Global — [ai@nohnlins.com](mailto:ai@nohnlins.com) · China — [lin@secondai.top](mailto:lin@secondai.top)

<p align="center">
  <a href="https://github.com/nohn3043">GitHub</a>
  &nbsp;·&nbsp;
  <a href="https://www.nohnlins.com/">nohnlins.com</a>
  &nbsp;·&nbsp;
  <a href="mailto:ai@nohnlins.com">ai@nohnlins.com</a>
</p>
<p align="center"><sub>NOHN AI · ANTARES</sub></p>

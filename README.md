# Antares

> Antares is the brightest star in Scorpius. 16 light-years away — visible, luminous, unreachable by touch.  
> Federated domains are the same: autonomous, distant, but connected by light.

## GFSIP — Global Federated Stable Interoperability Protocol

A federated network protocol designed for:

- **Autonomous domains** — each domain owns its identity, routing, services, and policy
- **Session resilience** — automatic session recovery across network flaps, process restarts, and gateway failover
- **Idempotent execution** — every side-effect operation carries an idempotency key; no false "exactly-once" promises
- **Optional causal audit** — Core Profile stays lean; Audit Profile adds full causal event chains with signatures
- **Multi-trust-root federation** — no global root of trust required

## Profiles

| Profile | Mandatory | What it adds |
|---------|-----------|--------------|
| **Core** | ✅ | QUIC transport, version negotiation, mutual auth, sessions, channels, dedup, structured errors |
| **Audit** | ❌ | Event IDs, parent chaining, state digests, signatures, causal graph export |
| **Federation** | ❌ | Domain Descriptors, cross-domain gateways, multi-anchor trust, fault isolation |

## Status

**v0.1 Experimental Draft**

- [x] Wire format specification
- [x] State machine with mandatory invariants
- [x] Channel model & deduplication rules
- [x] Session recovery protocol
- [x] Federation architecture
- [x] Causal audit extension
- [x] Conformance test vectors
- [ ] Dual independent implementations (M1)
- [ ] Production pilots (M4)

## Document

See [GFSIP_v0.1_protocol_draft.md](./GFSIP_v0.1_protocol_draft.md) for the full specification (Chinese, ~490 lines).

## License

TBD

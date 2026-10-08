# GFSIP/1.0 Conformance Testing Guide

[简体中文](CONFORMANCE-zh.md) | English

**Who this is for** — enterprise engineering and security teams, integrators, and auditors evaluating GFSIP/1.0, and anyone implementing it.

**One principle** — do not rely on test results published by the protocol authors, including the "9/9 passing" figure in this repository. Everything below is arranged so that you can derive your own test cases from the normative artifacts, run them in your own environment, and reach your own verdict. The reference implementation and its harness are working examples: use them as a test subject or as an interoperability peer — or ignore them entirely.

---

## 1. The claims, and what they are allowed to mean

Spec §27 (Conformance Claims) defines what a claim may state. A `GFSIP/1.0 Core Conformant` claim MUST:

1. implement the fixed frame header;
2. implement deterministic CBOR;
3. support QUIC with ALPN `gfsip/1`;
4. pass all Core Mandatory tests;
5. publish implementation version, configuration summary, and test report;
6. have no known unfixed Critical security issues.

`Audit/1` and `Federation/1` MUST be declared independently.

§28 defines nine **minimum test vectors** — a floor, not a measure. The full mandatory case list is `gfsip-conformance-checklist.csv` (34 cases, all Mandatory):

| Profile | Cases | IDs |
|---|---|---|
| Core | 24 | CORE-001 … CORE-024 |
| Federation/1 | 6 | FED-001 … FED-006 |
| Audit/1 | 4 | AUDIT-001 … AUDIT-004 |

Read the checklist as a **derivation example**, not as authority — §3 shows how to derive your own cases from the spec. The spec text is the only authority.

## 2. Normative artifacts — your ground truth

| Artifact | Contents | Use in test design |
|---|---|---|
| `GFSIP_v1.0_protocol_spec.md` | normative spec, 33 sections | the clause you test against |
| `gfsip-traceability-matrix.csv` | 11 requirements → spec section → checklist IDs → implementation component → responsibility role | scoping: pick a requirement, get its spec clause and cases |
| `gfsip-conformance-checklist.csv` | 34 cases: `test_id, profile, level, name, input_condition, expected_result` | cross-check list; `expected_result` values are error-code names from the registry |
| `gfsip-error-registry.json` | 35 numeric error codes (`code, name, scope, fatal, retryable, description`) | your oracle vocabulary: assert on codes, never on messages |
| `gfsip-state-machine.json` | 8 states, invariants, transition table | negative tests: enumerate illegal (state, event) pairs |
| `gfsip-message-schema.json` | logical message JSON Schema | field-level and type-level checks |

If a machine-readable artifact ever disagrees with the spec text, the spec wins — and that disagreement is itself a finding worth reporting. Catching exactly this kind of drift is what third-party review is for.

## 3. Designing your own tests

### 3.1 The loop

1. **Pick a claim and a profile.** Start from the traceability matrix: requirement → spec section.
2. **Read the clause.** Extract every normative MUST / MUST NOT.
3. **Convert it into an observable expectation**: an error code (registry), a state (state machine), a side-effect count, an audit-chain property, or byte-level equality.
4. **Construct the stimulus**: legal and illegal frames, handshake orders, tokens and descriptors with chosen properties.
5. **Define the oracle and the pass criterion before running.** A test that can only be interpreted after seeing the output is not evidence.
6. **Preserve**: raw logs, seeds, artifact hashes. A second person must be able to re-run your test from what you saved.

### 3.2 What any implementation must expose to be testable

- **Named numeric error codes** — tests assert on the code, never on human-readable text.
- **Session states and transitions** — current state must be queryable; rejections must be explicit, never silent.
- **Deterministic CBOR** — same input, byte-identical output, so golden-byte tests are legitimate. Fields the spec allows to be random (nonces, session IDs) must not be asserted for equality.
- **Side-effect accounting** — the number of executed side effects must be observable; this is what makes idempotency testable at all.
- **If Audit/1 is claimed** — event objects exposing IDs, declared predecessors, and state hashes, so you can recompute the chain yourself.

### 3.3 Technique catalogue

| Class | What you attack | Artifact | Example expectation |
|---|---|---|---|
| Wire format & encoding | frame header validity; CBOR canonicalization | spec §8 | `MALFORMED_FRAME`, `MALFORMED_HEADER` |
| Version negotiation | disjoint versions; downgrade attempts | spec §11 | `VERSION_UNSUPPORTED`, `DOWNGRADE_DETECTED` |
| State machine | illegal (state, event) pairs | state-machine JSON | explicit rejection with a registry code; no silent ignore |
| Auth & session security | forged proofs; replay; 0-RTT side effects | spec §12, §23 | `AUTH_FAILED`, `EARLY_DATA_REJECTED` |
| Resume | token bound to identity; single-use | spec §16 | `RESUME_IDENTITY_MISMATCH`, `RESUME_REPLAY`, `RESUME_EXPIRED` |
| Idempotency | duplicate keys; retries under packet loss | spec §15 | side-effect count = 1; `DUPLICATE_ACCEPTED` / `IN_PROGRESS` semantics |
| Audit integrity | cycles; parent limit; forged signatures | spec §17 | `CAUSAL_CYCLE`, `CAUSAL_PARENT_LIMIT`, `EVENT_SIGNATURE_FAILED` |
| Federation | descriptor expiry/forgery; loops; hop limit | spec §18 | `DESCRIPTOR_EXPIRED`, `DESCRIPTOR_SIGNATURE_FAILED`, `ROUTE_LOOP`, `ROUTE_HOP_LIMIT` |
| Resource limits | oversized frames; decompression bombs; floods | spec §21 | `FRAME_TOO_LARGE`, `DECOMPRESSION_LIMIT`, `RATE_LIMITED` |
| Fault injection | delay, drop, reorder, partition | spec §16, §19 | resumption works; degraded/terminal behavior explicit |

## 4. The reference implementation — as test subject or interop peer

```bash
cd reference-impl
pip install -r requirements.txt    # cbor2, cryptography, aioquic
python -m gfsip.conformance        # the 9 §28 vectors; exit 0 = pass, 1 = fail
python demo.py                     # end-to-end demo; prints per-stage PASS/FAIL; exit 0/1
python async_demo.py               # async API demo; exit 0/1
python quic_demo.py                # real QUIC over UDP loopback 127.0.0.1:4433 (needs aioquic)
```

`conformance.py` uses package-relative imports — run it as `python -m gfsip.conformance`, not as a file path. With the package installed (`pip install gfsip`), the module also runs outside a repository checkout.

Author self-test on 2026-10-08 (Python 3.13.14, Windows): 9/9 passed, exit 0. Take this as an example of the output format — not as evidence. Reproduce it if you like; ignore it if you don't. On Windows consoles with a non-UTF-8 code page some characters may render garbled; set `PYTHONUTF8=1`. Results are unaffected.

## 5. Worked example — the nine §28 vectors, rewritten as your tests

Each row is a case you can re-implement against any implementation. The printed names match the reference harness output.

| Behavior | Checklist | Spec | Your stimulus → your oracle |
|---|---|---|---|
| no common version | CORE-006 | §11 | two HELLOs with disjoint major versions → handshake fails; state CLOSED; code `VERSION_UNSUPPORTED` |
| initiator even channel | CORE-011 | §14 | initiator opens an even channel ID → rejected `INVALID_CHANNEL_ID`; no channel exists afterwards |
| same idempotency key → 1 side effect | CORE-014 | §15 | submit the same operation with the same key twice → side-effect count = 1; second result flagged duplicate |
| resume token cross-node | CORE-017 | §16 | present a resume token issued to identity A as identity B → `RESUME_IDENTITY_MISMATCH`; no session restored |
| duplicate sequence | CORE-015 | §8.2 | deliver the same sequence number twice → second frame rejected `SEQUENCE_REPLAY`; not delivered to the application |
| EVENT self-parent | AUDIT-001 | §17 | add an audit event whose parent list contains itself → `CAUSAL_CYCLE`; event not appended |
| 0-RTT side effect | CORE-019 | §23 | send EARLY_DATA carrying a side effect before ESTABLISHED → `EARLY_DATA_REJECTED`; state unchanged |
| expired descriptor | FED-002 | §18 | register a domain descriptor past `valid_until` → `DESCRIPTOR_EXPIRED`; no new trust |
| route loop | FED-003 | §18 | route query whose `visited_domains` already contains the current domain → `ROUTE_LOOP` |

## 6. Reporting your results

A report structured like this can be audited line by line, and disagreements localize to a single case:

| Field | Content |
|---|---|
| Implementation | name, version, source commit |
| Artifacts tested | spec / checklist hashes (e.g. rows from `SHA256SUMS.txt`) |
| Environment | OS, runtime, network path, transport configuration |
| Profiles | Core/1 (+ Audit/1, Federation/1 if tested) |
| Cases | one row per case: stimulus, expected, observed, verdict, raw-log reference |
| Deviations | every MUST not met, with the spec clause |

## 7. Coverage boundary — what this repository does not prove

- Automated here: the nine §28 minimum vectors. The 34-case checklist is **not** fully automated in this repository.
- No CI is configured; the harness is run manually.
- No independent second implementation yet, and no public interoperability report — both are listed as in-progress/todo in the README Project Status.
- §27.6 ("no known unfixed Critical security issues") is an attestation, not black-box testable — evaluate it through the vendor's vulnerability-disclosure process.
- Performance and load targets are not specified in v1.0; they are outside conformance scope.
- The PyPI package version may drift from repository HEAD — pin the exact commit or artifact hashes you tested.

---

Spec and documentation: CC BY 4.0 (`LICENSE-SPEC.md`). Code: Apache-2.0 (`LICENSE`).

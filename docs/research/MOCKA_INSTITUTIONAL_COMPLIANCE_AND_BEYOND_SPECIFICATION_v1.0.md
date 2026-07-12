# MoCKA Institutional Compliance and Beyond Specification v1.0

**Status:** Synthesis document. Integrates `NIST_REQUIREMENT_CATALOG_v1.0.md`, `MOCKA_NIST_REQUIREMENT_MAPPING_v1.0.md`, `MOCKA_NIST_GAP_ANALYSIS_v1.0.md`, `MOCKA_BEYOND_NIST_ANALYSIS_v1.0.md`, and `MOCKA_EVIDENCE_MATRIX_v1.0.md`. No new research was performed to produce this document; every claim below is a citation or direct restatement of a finding already established in one of those four documents, cross-referenced by section.

**Comparison basis:** *NIST AI RMF Profile on Trustworthy AI in Critical Infrastructure — Community of Interest Discussion Draft*, Jul 7, 2026 (`aiciprof@nist.gov`), explicitly labeled by its authors as **"NOT OFFICIAL GUIDANCE, FOR DISCUSSION ONLY"** and a work-in-progress ahead of a formal comment period. Every statement in this specification about "what NIST requires" refers to this draft as it stood on that date, not to a finalized standard.

---

## 1. Executive Summary

This specification compares MoCKA 1.0's institutional, implementation, and operational record against the NIST AI RMF Trustworthy AI in Critical Infrastructure Profile Discussion Draft (Jul 7, 2026), covering all 12 Practices and 53 Tasks in the source. The purpose is **not** to establish that MoCKA is "NIST-compliant" — the source document explicitly disclaims being a compliance checklist, and MoCKA is not a Critical Infrastructure operator, so most of the source's physical-OT-specific Tasks do not apply to it by design, not by deficiency (see §4, Domain Scope Note).

The purpose is to position MoCKA objectively: of the 53 NIST Tasks, 14 (26%) are **NONE** because they presuppose a physical CI operating environment MoCKA does not have; of the remaining 39 addressable Tasks, MoCKA carries **FULL or SUPERIOR evidence for 6** and **PARTIAL evidence for 33** — meaning MoCKA's honest modal status against this profile is **PARTIAL**, not FULL. Two SUPERIOR verdicts were assigned, both with written justification (Practice 3.7 Shadow AI governance and Practice 8.1 root-cause analysis), because MoCKA's operative evidence in those specific areas exceeds what the Discussion Draft itself has published (much of the source's own Implementation content is placeholder `(TBD — suggestions welcome)` text).

Separately, and more significantly for MoCKA's own institutional value, this audit documents twelve institutional elements — Human Gate, Decision Ledger, Knowledge Gate, Institutional Memory, Decision Unit, Regression Governance, Shadow Architecture, Institutional Verification, Living Context, Seal Governance, Evidence Chain, and AI-to-Institution governance — that address governance problems the NIST Discussion Draft does not currently describe, because they arise from a different operating context (an institution governing continuous, memoryless, multi-vendor AI participation in its own governance, rather than an operator deploying AI into physical infrastructure). These are presented with evidence and honest maturity ratings, not as claims of superiority.

Critically, this audit also surfaces — because MoCKA's own Integrity Ledger already surfaced them — **three currently-open, unresolved institutional risks** inside MoCKA itself (a Human Gate enforcement gap, a missing authentication layer, and a stale status display). Reporting these is treated as evidence of the audit discipline being applied honestly, not as an embarrassment to be minimized.

---

## 2. NIST Overview

See `NIST_REQUIREMENT_CATALOG_v1.0.md` §0–1 for full detail. Summary: the Discussion Draft organizes 12 Practices (governance-level, uniquely identified) into Tasks (technical-management level, 53 total) and illustrative, largely-incomplete Implementations (~140, many `(TBD)`). It applies the AI RMF 1.0 core functions (Govern/Map/Measure/Manage) to the 16 CISA-defined Critical Infrastructure sectors, defines seven re-interpreted Trustworthy AI Characteristics for CI (Safe, Secure, Resilient, Explainable & Interpretable / Accountable & Transparent, Privacy Enhanced, Fair, Accurate/Valid/Reliable/Bias Managed), and explicitly deconflicts with the still-unpublished NIST Cyber AI Profile (IR 8596) — every "Primary Cyber AI Profile Mapping" field in the source is blank. Practices 13+ are explicitly reserved and empty (`(TBD)`), and the source's own appendix lists numerous ideas and references NIST is still considering but has not yet incorporated.

---

## 3. Requirement Mapping

Full 53-Task mapping in `MOCKA_NIST_REQUIREMENT_MAPPING_v1.0.md`. Key structural finding carried forward: this audit's Domain Scope Note (stated once in that document, restated below in §4) accounts for the majority of NONE verdicts, and is the single most important piece of context for interpreting every other number in this specification.

---

## 4. Compliance Matrix (Status Tally)

| Status | Count / 53 | Share |
|---|---|---|
| FULL | 4 (Tasks 7.1, 7.3, 10.1, 10.3) | 8% |
| SUPERIOR | 2 (Tasks 3.7, 8.1 — both with written justification, see Mapping doc) | 4% |
| PARTIAL | 33 | 62% |
| NONE | 14 | 26% |
| PLANNED | 0 | 0% |

**Domain Scope Note (restated from Mapping doc §header):** MoCKA is a software/knowledge-governance institutional system, not a Critical Infrastructure operator. It does not run OT/ICS equipment, valves, PLCs, SCADA, or medical devices. Most NONE verdicts (Practices 2.1/2.5, 3.6, 4.3, 6.1/6.3, 8.4/8.5, 9.1/9.3, 11.1/11.3/11.5) trace directly to this scope mismatch and are recorded as such in the Gap Analysis (Category A) — the honest remediation for these is explicit scope documentation, not new engineering, and they are rated Low priority accordingly.

---

## 5. Gap Analysis

Full detail in `MOCKA_NIST_GAP_ANALYSIS_v1.0.md`. Headline findings, ranked by the Gap Analysis's own priority scale:

**高 (High) priority — 3 items, all currently open institutional risks confirmed by MoCKA's own Integrity Ledger, not hypothesized by this audit:**
1. Human Gate is not enforced on the `/audit/seal` execution path (IC_20260708_004, Open) — affects NIST Tasks 3.2, 4.1, 4.5, 7.4.
2. `app.py` has no request-level authentication middleware (confirmed by grep, per IC_20260708_004) — affects NIST Tasks 5.2, 5.3.
3. The COMMAND CENTER seal-status display reads a defunct file and has shown an apparently-broken status for over three months while the underlying seal mechanism was in fact healthy (IC_20260707_005, Open) — affects NIST Tasks 4.2, 10.2.

**中 (Medium) priority — 12 items**, mostly formalizing patterns that exist informally (a repeatable champion-challenger-style validation pattern, a dependency/blast-radius map between MoCKA subsystems, granular artifact-risk classification) or closing verification debt on name-only-cited governance documents.

**低 (Low) priority — 15 items**, almost entirely the domain-scope-mismatch NONEs from §4.

---

## 6. Beyond NIST

Full detail in `MOCKA_BEYOND_NIST_ANALYSIS_v1.0.md`. Twelve institutional elements documented with purpose, institutional value, evidence, operational status, difference from NIST, and an honest maturity rating (Concept/Implemented/Operational/Verified):

| Element | Maturity | One-line differentiator from NIST |
|---|---|---|
| Human Gate | Operational (gap noted) | Gates AI writes to its own governing artifacts — not addressed by NIST's operator-facing override/authorization Tasks |
| Decision Ledger | Operational/Verified | General-purpose, explicitly-superseding decision record; NIST's closest analogue (7.3.1) is scoped only to safety-mechanism versioning |
| Knowledge Gate | Concept/Implemented | No NIST analogue for a dedicated institutional-memory repository; **honestly under-verified** in this audit |
| Institutional Memory | Operational/Verified | Addresses memoryless-AI-session continuity, a problem NIST's human-operator-framed Practices 4.2/9 do not anticipate |
| Decision Unit | Operational/Verified | Atomic, independently-citable decision record design |
| Regression Governance | Operational/Verified | Drift/anomaly classification applied to MoCKA's own governance process, not physical control loops |
| Shadow Architecture | **Concept only** | Claimed but **not evidenced as tested** — flagged, not inflated |
| Institutional Verification | Operational/Verified | The best-evidenced element; produces most of the evidence cited elsewhere in this audit, including MoCKA's own open risk findings |
| Living Context | Operational (one Open finding) | Context-freshness/provenance tracking across AI sessions, including a documented major self-correction (2026-07-09) |
| Seal Governance | Operational (reporting-layer gap) | Cryptographic sealing exceeds NIST 10.2's "immutable log" language in mechanism detail, but has a confirmed display-accuracy gap |
| Evidence Chain | Operational/Verified | Institution-level provenance linking (event→finding→decision), broader than NIST's per-artifact model/prompt provenance (12.1.2) |
| AI-to-Institution | Operational/Verified | Cross-AI claim verification and fabrication rejection among authorized AI systems — a problem NIST's Practices 3.7/5 do not address (they cover unauthorized AI only) |

**Recommendations to NIST** (5 items, full text in Beyond-NIST doc §2) center on: gated-write control for AI-governing artifacts; supersession-lifecycle decision records; cross-AI claim verification as a named practice; context-freshness tracking across memoryless AI sessions; and continuous (not only post-incident) self-auditing. All five are framed, per R01 instruction, as *"institutional elements this audit did not find addressed in the NIST Discussion Draft, with the following implementation/operational evidence"* — not as claims of NIST deficiency.

**Critical Infrastructure application scenarios** (Power, Healthcare, Finance, Telecommunications; full text in Beyond-NIST doc §3) are explicitly illustrative: they describe how a CI operator *could* apply MoCKA's evidenced patterns to reinforce specific named NIST Practices and Tasks, grounded in verified MoCKA mechanisms, while explicitly stating MoCKA has no deployment, certification, or validation history in any of these sectors.

---

## 7. Institutional Innovation

Restated from §6 for emphasis, since this is the section of greatest interest to MoCKA's own stakeholders: the single most load-bearing finding of this entire audit is that **MoCKA's Institutional Verification mechanism (the Integrity Classification Ledger) is what made the rest of this audit possible to write with genuine evidence rather than self-report.** Every high-priority gap in §5, and the explicit maturity downgrades in §6 (Shadow Architecture to Concept-only; Knowledge Gate to Concept/Implemented; Living Context and Seal Governance carrying open caveats), came from MoCKA's own audit trail, not from this session's independent discovery. A governance system that catches and records its own unresolved failures is a qualitatively different kind of evidence than a governance system that only records its successes — this is the innovation this specification treats as most significant, more so than any individual FULL or SUPERIOR verdict in the Compliance Matrix.

---

## 8. Evidence

Full matrix in `MOCKA_EVIDENCE_MATRIX_v1.0.md`, separating Public / Internal / Decision Ledger / Repository / Implementation evidence, and explicitly listing this audit's own evidence gaps (Decision Ledger read only by cross-referenced sample, not in full; two background research agents dispatched but not incorporated per deliverable-first directive; `mocka-knowledge-gate` repository content not inspected; several `docs/governance/*.md` files cited by name only).

---

## 9. Future Work

1. **Close the three High-priority gaps** identified in §5 (Human Gate enforcement on `/audit/seal`, `app.py` authentication middleware, seal-status display repointing) — these are the highest-value, lowest-ambiguity next actions, and are already tracked in MoCKA's own project history (TODO_429-boundary, TODO_371) independent of this audit.
2. **Read the full Decision Ledger** (57 records, only partially sampled per Evidence Matrix §C) and the `[name-only]` governance documents (Evidence Matrix §B, INT-06) to convert several PARTIAL/Concept ratings into confirmed status one way or the other.
3. **Incorporate the two background research agents' findings**, if retrieved, as a supplementary verification pass rather than a v2 rewrite — per this audit's deliverable-first directive, they were not blocked on, but their output (once available) should be checked against this Evidence Matrix's gaps.
4. **Run a deliberate Shadow Architecture drill** (recommended jointly in Gap Analysis and Beyond-NIST doc) to either substantiate or correct the "75% function maintained" claim, which currently rests on design documentation alone.
5. **Track the NIST Discussion Draft's evolution.** The source is explicitly a moving target (open comment period, Practices 13+ reserved, most Implementations placeholder). This specification is dated to the Jul 7, 2026 draft; a future revision of the source should trigger a revision of `MOCKA_NIST_REQUIREMENT_MAPPING_v1.0.md` specifically, since that is the document most sensitive to source changes.
6. **Consider formal submission of the §6 "Recommendations to NIST" items** to the Community of Interest process (`aiciprof@nist.gov`) the source document itself invites feedback through, if MoCKA's principals judge the evidence sufficiently mature for external sharing.

---

## 10. Position of MoCKA within International AI Governance

**Scope restriction (mandatory, per R01 instruction):** this section addresses only MoCKA's institutional position *as revealed by comparison against the NIST AI RMF Trustworthy AI in Critical Infrastructure Discussion Draft*. It does not compare MoCKA to ISO/IEC standards, the EU AI Act, or any other framework — no such comparison was performed as part of this audit, and none is implied here. Exaggeration is explicitly disallowed by the governing instruction for this section; every sentence below is a direct restatement of an already-cited finding.

MoCKA was not designed against the NIST Discussion Draft and is not a Critical Infrastructure operator; §4's Compliance Matrix shows this plainly — 26% of the source's Tasks are structurally inapplicable to MoCKA's domain, and of the remainder, MoCKA's modal evidenced status is PARTIAL. On the narrow, specific dimension this audit was able to compare directly — **institutional governance of AI participation in an organization's own operating record** — MoCKA has built and operated, with dated and cross-referenced evidence, several mechanisms (Human Gate, Decision Ledger, Institutional Verification, Evidence Chain, AI-to-Institution claim verification) that address problems not currently described, even at the placeholder level, in the NIST Discussion Draft's Practice/Task structure. This is best understood as a difference in *problem framing*, not a difference in maturity or rigor across a shared scale: NIST's Discussion Draft is framed around AI systems acting *on* physical infrastructure, operated by a human workforce with continuous institutional memory; MoCKA's evidenced mechanisms are framed around AI systems acting *within* an institution's own governance process, operated by AI participants without native memory continuity between sessions. Where the two framings overlap — audit-trail rigor (§6, Institutional Verification vs. NIST Practice 8), provenance/version control (§6, Decision Ledger vs. NIST Task 7.3), and post-incident cross-verification (§6, AI-to-Institution vs. NIST Practice 3.7) — MoCKA's evidence in this specific audit was assessed as meeting or, in two written-justified instances (Tasks 3.7 and 8.1), exceeding the content currently published in the source document. This finding is bounded strictly to comparison against a same-day snapshot of an explicitly incomplete, non-official discussion draft, and should not be read as a claim about MoCKA's standing relative to any finalized standard, regulation, or the eventual final NIST profile this draft will become.

MoCKA also carries, on its own evidence, three currently-open institutional risks (§5) that a fair position statement cannot omit: a Human Gate enforcement gap, a missing authentication layer, and a stale-but-not-broken status display. Their presence — found and recorded by MoCKA's own audit mechanism rather than concealed — is itself part of what this specification treats as evidence of institutional maturity in §7, but it also means MoCKA's position here is that of **a governed, self-correcting, partially-gapped system under active audit**, not a finished or fully-secured one.

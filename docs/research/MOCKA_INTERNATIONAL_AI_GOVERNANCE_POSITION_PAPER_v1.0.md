# MoCKA International AI Governance Position Paper v1.0

**Derived from (no new research performed):** `NIST_REQUIREMENT_CATALOG_v1.0.md`, `MOCKA_NIST_REQUIREMENT_MAPPING_v1.0.md`, `MOCKA_NIST_GAP_ANALYSIS_v1.0.md`, `MOCKA_BEYOND_NIST_ANALYSIS_v1.0.md`, `MOCKA_EVIDENCE_MATRIX_v1.0.md`, `MOCKA_INSTITUTIONAL_COMPLIANCE_AND_BEYOND_SPECIFICATION_v1.0.md` — all in `docs/research/`, all produced against *NIST AI RMF Profile on Trustworthy AI in Critical Infrastructure, Community of Interest Discussion Draft, Jul 7, 2026*.

**What this paper is:** a synthesis, written for an external audience (the international AI governance community, including but not limited to the NIST Community of Interest this comparison was originally built to engage), of what a structured comparison between MoCKA's institutional record and one current AI governance framework revealed. It restates and reorganizes findings already established and cited in the six source documents above; it does not introduce new claims.

**What this paper is not:** a certification, a compliance attestation, or a claim that MoCKA satisfies any standard. The source NIST document is itself an explicitly incomplete, non-official discussion draft ("NOT OFFICIAL GUIDANCE, FOR DISCUSSION ONLY"). No conformity assessment is possible or attempted against a document in that state, and none is claimed here.

---

## 1. Executive Summary

**MoCKA's purpose.** MoCKA (Model of Cybernetic Knowledge Architecture) is an institutional governance system for AI-assisted work. It is not an AI product and not a Critical Infrastructure operator. Its stated function, per its own constitution, is to record, verify, and prove knowledge continuously across an operating history that now spans over 15,000 recorded events and 57 recorded institutional decisions (`MOCKA_EVIDENCE_MATRIX_v1.0.md` §B–C).

**Why this comparison was undertaken.** The NIST AI RMF Profile on Trustworthy AI in Critical Infrastructure Discussion Draft (Jul 7, 2026) is one of the most detailed public frameworks currently available for reasoning about AI governance obligations, structured into 12 Practices and 53 Tasks (`NIST_REQUIREMENT_CATALOG_v1.0.md`). Measuring MoCKA against it — even though MoCKA was not built for this framework and does not operate in a CI sector — provided an external, independently-structured yardstick against which to describe MoCKA's institutional design honestly, rather than only in its own terms.

**This paper's position.** This is a comparative evaluation and a complementarity proposal, not a compliance claim. Where MoCKA's evidenced practices address governance problems the NIST draft does not currently describe, this paper states that fact with evidence and proposes it as a discussion input to the wider AI governance community — not as a demonstration that MoCKA is superior to, or a replacement for, any existing or forthcoming standard. Where MoCKA falls short of what NIST's draft asks — including for reasons as basic as MoCKA not operating physical infrastructure at all — this paper says so plainly, and where MoCKA has its own currently-open, self-identified governance gaps, this paper names them rather than omitting them (§4).

---

## 2. Relationship between MoCKA and NIST AI Governance Frameworks

**Scope of the comparison.** All 12 Practices and 53 Tasks of the Discussion Draft were reviewed and mapped against MoCKA's evidenced institutional components (`MOCKA_NIST_REQUIREMENT_MAPPING_v1.0.md`). The comparison used NIST's own identifiers throughout (Practice N, Task N.M) rather than inventing a parallel scheme, so any finding here can be traced back to a specific, citable point in the source document.

**Classification scheme.** Each of the 53 Tasks received one status:

- **FULL** — MoCKA has a working equivalent that covers the substance of the requirement.
- **SUPERIOR** — MoCKA's evidenced practice, in a specific and narrow sense, addresses more of the requirement than the Discussion Draft itself currently publishes content for. This status was assigned only twice, and only with a written comparison (NIST requirement → MoCKA institution → implementation → operation → evidence) attached to each: **Task 3.7** (governance of unauthorized/Shadow AI systems) and **Task 8.1** (deterministic root-cause analysis for AI-related incidents). Both instances rest on the fact that the Discussion Draft's own Implementations for these Tasks are largely unwritten placeholder stubs, while MoCKA has dated, cross-referenced, resolved incident records addressing the same substance (see §3).
- **PARTIAL** — MoCKA has a related or analogous mechanism, but it does not fully cover the requirement, either because of a scope difference or an incomplete implementation.
- **NONE** — no MoCKA equivalent was found.

**Results.** Of 53 Tasks: **4 FULL, 2 SUPERIOR, 33 PARTIAL, 14 NONE.** These figures are unchanged from `MOCKA_NIST_REQUIREMENT_MAPPING_v1.0.md`'s Summary Tally and are not revised in this paper. Fourteen of fifty-three Tasks (26%) are NONE primarily because they are written for organizations that operate physical Critical Infrastructure assets — valves, PLCs, SCADA systems, grid equipment, patient records — which MoCKA does not have and was never built to operate. This is stated as a boundary of applicability, not a weakness: closing these gaps would require MoCKA to acquire an operational mission it does not have (`MOCKA_NIST_GAP_ANALYSIS_v1.0.md`, Category A). Of the 39 Tasks where a comparison is actually meaningful, MoCKA's modal (most common) evidenced status is **PARTIAL** — not FULL, not SUPERIOR. This is stated as the honest headline result of this comparison, not softened for presentation purposes.

**Transparency of judgment.** Every PARTIAL and NONE verdict in the source Mapping document carries a stated reason; every SUPERIOR verdict carries a full written justification; nothing was scored from impression. Where the evidence available to this review was incomplete — for example, several `docs/governance/*.md` files were confirmed to exist but their content was not read in the session that produced these documents — this was marked explicitly as `[name-only]` and scored conservatively, never as FULL or SUPERIOR (`MOCKA_EVIDENCE_MATRIX_v1.0.md` §B, INT-06).

---

## 3. MoCKA Unique Contributions

The following institutional mechanisms, evidenced in `MOCKA_BEYOND_NIST_ANALYSIS_v1.0.md`, address governance problems that do not appear — even at the placeholder level — in the NIST Discussion Draft's current Practice/Task structure. This is attributable to a difference in problem framing: the NIST draft governs AI systems that act *on* physical infrastructure, operated by a continuously-employed human workforce; MoCKA governs AI systems that act *within* an institution's own governance process, where the AI participants themselves have no native memory between sessions. Each item below is presented with its evidence and its actual, current maturity — not an aspirational one.

**Decision Ledger — institutional memory of decisions.** Every institutional decision is recorded as a discrete, dated, causally-justified unit (`decision_id`, e.g. `DC_20260711_002`) with a defined lifecycle (Active / Superseded / Withdrawn), following the constitutional principle that "all decisions preserve 5W1H." As of this review, 57 decisions were recorded, the most recent approved hours before the underlying audit was conducted. **Maturity: Operational/Verified.** NIST's closest analogue (Task 7.3.1) asks for a version registry scoped specifically to AI safety-mechanism changes; MoCKA's Decision Ledger is a general-purpose institutional record with an explicit supersession semantics NIST's text does not describe.

**Institutional Memory Layer — continuity across memoryless AI sessions.** `MOCKA_OVERVIEW.json` and the "essence" pipeline (RAW→REDUCED→CORE→ESSENCE) exist specifically to re-brief each new, memoryless AI session on current institutional state, and — critically — the system tracks and discloses its own memory's staleness rather than presenting it as reliably current (the overview's own `staleness_note` field has, at points, explicitly flagged that its body content lagged behind actual project state by weeks). **Maturity: Operational/Verified**, verified precisely in the sense that the mechanism catches and reports its own drift rather than silently serving outdated context as current.

**Shadow Movement — degraded-mode operation concept.** MoCKA's constitution describes a "shadow_Movement" mode intended to maintain approximately 75% of function during partial system failure, contrasted with normal ("mocka_Movement") operation. This is stated here as a **designed intent, not a demonstrated capability**: this review found no drill log, test report, or Decision Ledger entry substantiating the 75% figure or confirming this mode has ever been deliberately exercised. **Maturity: Concept only.** It is included in this section because it represents a genuine design commitment relevant to NIST's redundancy and mission-continuity Practices (2.2, 11.x), and is listed honestly at its actual maturity rather than omitted or inflated — design capability and implemented capability are not the same thing, and this paper does not conflate them.

**Evidence-driven Governance — the Integrity Classification Ledger.** MoCKA maintains a structured, 31-entry (at time of this review) ledger of self-identified institutional findings, each carrying a stated detection method, impact scope, and cross-references to related events and decisions, with a status field (Open/Resolved) and, notably, an explicit `Unknown` state for cases where root cause could not yet be determined — used instead of asserting an unconfirmed cause. This mechanism is what allowed the underlying audit to report MoCKA's own currently-open governance gaps (§4) with dated, specific evidence rather than by inference. **Maturity: Operational/Verified** — the best-evidenced element in the entire comparison, since its own outputs are the evidentiary basis for most of the rest of this paper, including its own limitations section.

**Change Protocol — guaranteed change-history recording.** File and system changes to MoCKA's own codebase follow a mandatory record protocol (CHANGE_START before a change, UTF-8/integrity verification, CHANGE_DONE after), enforced by institutional rule rather than left to individual discretion, on the stated principle that "work without a record does not exist as MoCKA work." This produces the append-only Event Ledger (over 15,000 events at time of this review) that underlies the Decision Ledger, Integrity Ledger, and Evidence Chain described above. **Maturity: Operational/Verified**, exercised continuously, including in the production of this paper itself.

---

## 4. Limitations and Open Gaps

This paper does not claim completeness, and the items below are stated as the current boundary of MoCKA's institutional coverage, not as resolved matters or as an exhaustive list of every imperfection. All three were discovered and are tracked by MoCKA's own Integrity Classification Ledger (§3, Evidence-driven Governance) — this section exists because that mechanism surfaced them, not despite it.

1. **Human Gate is not enforced on at least one live execution path (`IC_20260708_004`, status: Open).** MoCKA's stated policy requires human approval before AI-driven changes to core system files take effect. This review found that the `/audit/seal` (`MANUAL_SEAL`) execution path invokes a mechanical governance check (`GL7 pre_execution_check()`) and proceeds directly to executing a sealing operation on approval from that check alone — even though the mechanical check's own documentation states that a separate human approval is additionally required. No code on this path currently requests or verifies that separate approval. A related override parameter (`human_gate_override_event_id`) is accepted without validating that the referenced approval record actually exists or is in an approved state.
2. **The primary application (`app.py`) has no request-level authentication middleware**, confirmed by direct code inspection during the same investigation that surfaced item 1. This is a foundational access-control gap independent of the Human Gate question specifically.
3. **A status display has shown stale information for an extended period (`IC_20260707_005`, status: Open).** The COMMAND CENTER dashboard's seal-status indicator was found to read a defunct file that had not been updated in over three months, while the actual underlying cryptographic sealing mechanism was confirmed healthy and updating close to real time. The practical effect was the opposite of a typical silent-failure risk: the system appeared broken while it was in fact working, which is its own distinct hazard (it can train a human reader to distrust or ignore a working indicator).

These three items are also the highest-priority findings of `MOCKA_NIST_GAP_ANALYSIS_v1.0.md` (§ Consolidated Priority View, 高/High). None of MoCKA's FULL, SUPERIOR, or PARTIAL evidenced claims elsewhere in this comparison depend on these three items being resolved — they are reported here as an independent, ongoing part of MoCKA's institutional record, consistent with this paper's evidence-only, non-exaggerating framing.

---

## 5. Recommendations to NIST / International AI Governance Community

MoCKA does not propose to replace, supersede, or compete with the NIST AI RMF or its Critical Infrastructure Profile, or with any other existing or forthcoming AI governance framework. The following is offered as a set of complementary discussion points, grounded in operating evidence rather than untested design, for the specific communities (including the NIST Community of Interest process this comparison originally engaged, `aiciprof@nist.gov`) that are actively shaping how AI governance frameworks address organizational process, not only AI system behavior.

**The core observation.** Existing AI governance frameworks, including the NIST Discussion Draft reviewed here, are substantially organized around evaluating an AI system's outputs — its accuracy, safety, robustness, explainability at the point of decision. MoCKA's operating history suggests a complementary and currently under-addressed dimension: governance of an AI system's (or a multi-AI-system ecosystem's) **participation in an organization's own decision-making and change process** — not just what the AI outputs, but how that output is recorded, approved, superseded, and remembered across time and across sessions that have no continuity of their own.

Specific, evidence-backed points offered for consideration (full detail and justification in `MOCKA_BEYOND_NIST_ANALYSIS_v1.0.md` §2):

1. **Gated approval specifically for AI-driven changes to an organization's own governing rules and control systems** — distinct from, and narrower than, general change-authorization controls, motivated by MoCKA's own recorded incident of an AI system overwriting governance files it should not have had unsupervised access to.
2. **Decision records with explicit supersession semantics**, generalized beyond the safety-mechanism-versioning scope current draft guidance tends to describe them for.
3. **Cross-verification among multiple, individually-authorized AI systems** as a named governance practice, distinct from detecting unauthorized ("Shadow AI") systems — motivated by MoCKA's own recorded incident of one authorized AI system producing a fabricated result that a second review process caught and formally rejected.
4. **Context-freshness and provenance tracking across memoryless AI sessions** as a recognized governance concern in its own right, alongside the human-operator-focused situational-awareness practices current frameworks already address.
5. **Continuous, not only post-incident, self-auditing** as a standing institutional practice — MoCKA's own governance gaps in §4 were found this way, by an audit mechanism that runs independent of any specific triggering incident.

These points are presented as inputs to ongoing multi-stakeholder standards development, not as demands or claims of gap-filling authority. MoCKA's own governance record (§4) demonstrates that operating this kind of institutional infrastructure does not guarantee freedom from gaps — only that gaps, when they occur, are more likely to be found and recorded rather than to persist unnoticed.

---

## 6. Position of MoCKA within International AI Governance

This closing section states MoCKA's institutional position strictly as revealed by the comparison documented above — against one AI governance framework, at one point in its drafting history (the NIST AI RMF Trustworthy AI in Critical Infrastructure Profile, Discussion Draft, Jul 7, 2026). It does not compare MoCKA to ISO/IEC standards, the EU AI Act, or any other framework, since no such comparison was performed. No exaggeration is intended in what follows; every statement restates a finding already made and cited above.

MoCKA was not designed against the NIST Discussion Draft, and it is not, and has never claimed to be, a Critical Infrastructure operator. The comparison in §2 shows this plainly: over a quarter of the source's Tasks are structurally inapplicable to MoCKA's domain, and across the Tasks that are applicable, MoCKA's typical evidenced status is partial coverage, not full or superior coverage. On the narrower, specific dimension where this comparison was able to engage directly — governance of AI participation in an organization's own operating and decision-making record — MoCKA has built, operated, and can produce dated, cross-referenced evidence for several mechanisms (§3) that are not currently described, even at a placeholder level, in the source document's Practice/Task structure. Where the two frameworks' concerns genuinely overlap — audit-trail rigor, change/version provenance, post-incident verification — this comparison's evidence supported MoCKA meeting or, in two narrowly-justified instances (Tasks 3.7 and 8.1), exceeding the content the source document currently publishes for those specific points. This finding is bounded strictly to that same-day snapshot of an explicitly incomplete, non-official draft; it says nothing about MoCKA's standing relative to any finalized standard, regulation, or the eventual final form this NIST profile will take once its comment period concludes.

MoCKA's position, stated without inflation, is that of a governed, actively self-auditing, and — by its own admission — currently partially-gapped institutional system. It offers, on the evidence gathered here, a specific and complementary perspective to existing AI governance frameworks: that trustworthy AI governance requires attending not only to what an AI system does, but to how an institution records, approves, remembers, and corrects the process by which that AI system's outputs become part of the institution's own operating history. This is offered to the international AI governance community as a discussion contribution, grounded in operating evidence, not as a claim of completeness or superiority.

---

## Reference Index

| Claim category | Primary source document |
|---|---|
| NIST requirement text and structure | `NIST_REQUIREMENT_CATALOG_v1.0.md` |
| Task-by-task status verdicts, SUPERIOR justifications | `MOCKA_NIST_REQUIREMENT_MAPPING_v1.0.md` |
| Gap reasoning, remediation, priority | `MOCKA_NIST_GAP_ANALYSIS_v1.0.md` |
| Institutional element evidence and maturity ratings | `MOCKA_BEYOND_NIST_ANALYSIS_v1.0.md` |
| Raw evidence citations (Public/Internal/Decision Ledger/Repository/Implementation) | `MOCKA_EVIDENCE_MATRIX_v1.0.md` |
| Full synthesis and prior "Position" statement (internal-audit framing) | `MOCKA_INSTITUTIONAL_COMPLIANCE_AND_BEYOND_SPECIFICATION_v1.0.md` |

This paper does not supersede any of the six documents above; it is an external-facing restatement of them, and any figure or claim here that appears to diverge from one of them should be treated as an error in this paper, not a revision of the underlying finding.

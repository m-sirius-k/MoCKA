# MoCKA Beyond-NIST Analysis v1.0

**Scope of this document:** independent analysis of MoCKA institutional elements. This is not a search for "what NIST is missing" — it is a factual inventory of what MoCKA has built, with evidence, followed by an honest statement of how it relates to (not "beats") the NIST Discussion Draft. Per R01 instruction, the framing throughout is: *"MoCKAにはNIST Discussion Draftでは確認できなかった制度要素があり、その実装・運用証拠は以下の通りである"* — never "MoCKA is better."

**Maturity scale used throughout:** **Concept** (documented design, no working artifact) → **Implemented** (code/artifact exists) → **Operational** (in active day-to-day use) → **Verified** (independently checked, cross-referenced against other records, or has survived an audit/incident).

---

## 1. Ten Institutional Elements

### 1.1 Human Gate
**目的 (Purpose):** Require human approval before AI-driven changes to core system files take effect, preventing an AI agent from unilaterally altering the institution that governs it.
**制度価値 (Institutional value):** Establishes a non-bypassable checkpoint between "AI proposes" and "system changes," directly targeting the specific failure mode of an AI overwriting or corrupting its own governing files.
**証拠 (Evidence):** `write_policy` in `MOCKA_OVERVIEW.json` ("Phase18以降: コアシステムファイルへの書き込みは人間ゲート承認必須（ChatGPT上書きインシデント対応）"); three parallel implementation surfaces identified in project history (`phi_os/human_gate.py`, `app.py` decision/approve endpoints, `mocka_git_safe_commit.py`'s `human_gate_override_event_id` parameter).
**運用状況 (Operational status):** Actively invoked — Decision Ledger entries (e.g. DC_20260710_004/005, DC_20260711_001/002) show real, dated Human Gate-adjudicated decisions.
**Honest caveat (required for fairness):** The Integrity Ledger records a currently **Open** finding (IC_20260708_004) that at least one live execution path (`/audit/seal` → `SealGovernanceGate.execute()` → GL7 `ALLOW`) bypasses the additional Human Gate approval its own designers' code comments say is required, and that the override parameter itself is not validated against a real approval record. Human Gate is a real, operating institutional pattern with at least one confirmed, currently-unresolved enforcement gap — both facts belong in this record.
**NISTとの差異:** NIST's closest analogue is Task 4.1 ("break glass" intervention procedures) and Task 7.4 (authorization controls for AI modifications), both illustrated in the Discussion Draft primarily by `(TBD)` Implementation stubs. NIST does not describe a mechanism specifically for gating an AI system's write access to the governance artifacts that constrain that same AI system — Human Gate's object of protection (the institution's own rule-files) is narrower and more self-referential than anything in the source text.
**Maturity:** Operational (enforcement gap noted above keeps it short of "Verified" for the specific path in question).

### 1.2 Decision Ledger
**目的:** Preserve every institutional decision as a discrete, dated, causally-justified record with a defined lifecycle (Active/Superseded/Withdrawn), so that "why was this decided" remains answerable indefinitely.
**制度価値:** Converts decisions from ephemeral chat/conversation artifacts into queryable institutional record, with the constitution principle "All decisions preserve 5W1H."
**証拠:** `mocka_decision_list`/`mocka_decision_get`/`mocka_decision_write` tools with a `status` enum (Active/Superseded/Withdrawn); concrete dated entries observed this session: DC_20260711_002 ("COMMAND CENTER v6.1退行インシデント監査フェーズの完了承認"), DC_20260711_001 (TODO_442 remediation approach), DC_20260710_004/005 (TODO_413/437 scope decisions); `current_view.recent_decisions.count: 57`.
**運用状況:** High-frequency, current use — the most recent decision at time of this audit was approved 2026-07-11T00:47:03Z, hours before this session.
**NISTとの差異:** NIST Task 7.3.1 asks for "a registry that uniquely identifies the specific version... Document every change... with technical justification," which is conceptually adjacent but scoped to AI safety-mechanism versioning specifically. MoCKA's Decision Ledger is broader — a general-purpose institutional decision record, not limited to safety-parameter changes — and carries an explicit supersession lifecycle (a later decision can formally supersede an earlier one, preserving both) that the NIST text does not describe for its analogous Task.
**Maturity:** Operational/Verified (cross-referenced against Integrity Ledger and TODO records; internally consistent in the samples checked this session).

### 1.3 Knowledge Gate
**目的:** Provide a dedicated institutional-memory layer (separate repository, `mocka-knowledge-gate`) for longer-horizon knowledge that outlives any single session or product cycle.
**制度価値:** Separates "fast," session-scoped memory (Event Ledger, essence pipeline) from a slower, more deliberately curated memory layer.
**証拠:** `mocka_get_overview.repositories.institutional_memory`: name `mocka-knowledge-gate`, remote `github.com/m-sirius-k/MoCKA-KNOWLEDGE-GATE.git`, role "制度的記憶層", stack "JavaScript/Firebase/Docker."
**運用状況:** Not independently verified in this session — this audit confirmed the repository's existence and stated role via the overview record only; its actual content and update cadence were not inspected.
**NISTとの差異:** No NIST analogue exists for a dedicated, separately-repositoried institutional memory layer distinct from operational logging.
**Maturity:** **Concept/Implemented only** — flagged honestly as unverified beyond existence, per this audit's evidence standard. This is exactly the kind of claim Task 7/8 of this audit exists to prevent inflating.

### 1.4 Institutional Memory (broader pattern, distinct from the Knowledge Gate repository specifically)
**目的:** Ensure that lessons from past incidents, decisions, and philosophy persist and are re-injected into future work, including future AI sessions that have no native memory of prior sessions.
**制度価値:** Directly addresses the "AI has no memory between sessions" problem structurally, rather than relying on a human to manually re-brief each new AI session.
**証拠:** `MOCKA_OVERVIEW.json` itself (designed explicitly as "新しいchatにこれ1つ貼れば即作業開始できる完全マスターファイル"); `mocka_get_essence` tool surfacing the latest INCIDENT/OPERATION/PHILOSOPHY entries; and — importantly — the system's own **documented awareness of its memory's staleness**: the overview's `meta.staleness_note` explicitly states that a given version's body content is known to lag behind actual project state ("v4.1はmeta欄のみのseal更新...本文はv4.0(2026-06-18)時点のまま未更新であり、TODO_384以降...等の作業が反映されていない"), and names the intended remediation process ("自動生成候補→Integrity Check→Human Gate→seal更新").
**運用状況:** Actively used every session (this session began by querying exactly these tools) and actively self-monitored for staleness rather than assumed accurate.
**NISTとの差異:** NIST's Practice 9 (training) and Practice 4.2 (situational awareness) address keeping *human* operators informed; nothing in the Discussion Draft addresses the structurally different problem of keeping successive, memoryless *AI* sessions informed and continuous with institutional history.
**Maturity:** Operational/Verified — verified in the specific sense that the system catches and records its own staleness rather than silently serving outdated context as current.

### 1.5 Decision Unit
**目的:** Treat each decision as an atomic, independently addressable unit (one `decision_id` = one bounded choice with context, options considered, and rationale) rather than folding decisions into narrative documents where they are hard to individually reference or supersede.
**制度価値:** Makes decisions independently citable (as this and other audit documents in this MoCKA project do routinely, e.g. "DC_20260710_004") and independently revisable without rewriting surrounding narrative.
**証拠:** The `decision_id` scheme itself (`DC_{YYYYMMDD}_{NNN}`) and the fact that individual decisions are fetchable in isolation via `mocka_decision_get`.
**運用状況:** This is the operative unit of the Decision Ledger described in 1.2 — not a separate system, but the atomic-record design choice that makes the Decision Ledger queryable at all.
**NISTとの差異:** No equivalent atomic-decision addressing scheme was found in the NIST source.
**Maturity:** Operational/Verified (same evidence base as 1.2, since it is the Ledger's unit design, not a distinct mechanism).

### 1.6 Regression Governance
**目的:** Detect and classify recurring anomalies in AI-driven institutional behavior (not physical-plant behavior) so that repeat failures are caught systematically rather than rediscovered each time.
**制度価値:** Converts "this feels like it happened before" into a structured, queryable classification.
**証拠:** `data/recurrence_registry.csv` (87 recorded recurrence entries per `mocka_get_overview.router.recurrence_data`); `calc_drift_v3` (AEGIS multi-indicator drift detection: "error_rate*0.45 + violation*0.30..."); anomaly taxonomy `FAST_WRONG`/`SLOW_DRIFT`/`FORMAT_COLLAPSE`/`DEPENDENCY_BREAK`; a documented correction cycle in which 77 false positives were identified and cleared (2026-04-04), followed by a further router bug fix (commit `6561fc5`, 2026-04-05).
**運用状況:** Operational with a documented self-correction history (the false-positive cleanup is itself evidence the mechanism is exercised and monitored, not just built and forgotten).
**NISTとの差異:** NIST Practice 2.3/3.4 describes TEVV-based drift monitoring for a deployed AI system's task performance against physical/operational baselines. MoCKA's Regression Governance targets a different object — its own multi-agent institutional process — using a structurally similar drift-scoring approach (weighted error/violation rate) but for governance behavior, not control-loop behavior.
**Maturity:** Operational/Verified (has a documented bug-and-fix history, evidence of real exercise).

### 1.7 Shadow Architecture
**目的:** Maintain partial function during component failure rather than total outage ("shadow_Movement": 縮退運用, ~75% function maintained during partial failure, contrasted with "mocka_Movement": normal operation loop Observation→Record→Incident→Recurrence→Prevention→Decision→Action→Audit).
**制度価値:** A designed degraded-mode operating concept, structurally similar in spirit to NIST's graceful-degradation requirements.
**証拠:** `mocka_get_overview.what_is_mocka.structure` names both movements explicitly.
**運用状況/Honest caveat:** This audit found **no drill log, test report, or Decision Ledger entry substantiating the "75%" figure or confirming Shadow Movement has ever been deliberately exercised**. It is a documented design intent, not a demonstrated capability.
**NISTとの差異:** Conceptually parallel to NIST Practice 2.2 (redundancy) and Practice 11 (mission continuity), but those NIST Tasks require documented, drilled fail-over procedures with recorded outcomes — a bar Shadow Architecture has not yet been shown to clear.
**Maturity:** **Concept only.** This is flagged explicitly rather than inflated — it is the kind of institutional element that *sounds* impressive but the evidence standard this audit applies (Task 7/8: no future-as-done) requires marking it at its actual, lower maturity.

### 1.8 Institutional Verification
**目的:** Subject MoCKA's own governance claims to adversarial-style audit rather than accepting self-reported status at face value.
**制度価値:** Produces exactly the kind of self-correcting evidence this Beyond-NIST document relies on — e.g., this audit was only able to report the Human Gate enforcement gap (1.1) and the seal-display bug (1.6/see Evidence Chain below) because MoCKA's own Integrity Ledger had already found and recorded them.
**証拠:** The Integrity Classification Ledger itself (31 records, `mocka_integrity_list`), each with `detection_method` and `discovered_by` fields; repeated pattern of a named "監査官R01" role rendering dated adjudications (e.g., IC_20260708_004's "監査官R01裁定(2026-07-08)"); explicit `state=Unknown` category (IC_20260705_015) for cases where the auditors could not yet determine ground truth, rather than guessing.
**運用状況:** Actively exercised — multiple entries show a full cycle: discovery → classification → (sometimes) resolution → cross-check against Decision Ledger for consistency (e.g., IC_20260707_006's `detection_method` explicitly describes finding and correcting a *mismatch* between the Decision Ledger's "closed" status and the Integrity Ledger's stale "Open" status — the audit process auditing itself).
**NISTとの差異:** NIST Practice 8 assumes root-cause analysis of AI-driven physical/operational incidents. MoCKA's Institutional Verification targets governance-process incidents (a control that should have fired but didn't; a status that should be synchronized but wasn't) — a distinct but structurally comparable discipline applied to a different failure domain.
**Maturity:** Operational/Verified (this is the best-evidenced element in this entire analysis, since its own outputs are the evidence for most of the other findings in this and the Gap Analysis document).

### 1.9 Living Context
**目的:** Ensure that the context injected into an AI session ("what is currently true about this project") is actually sourced from the correct, current, canonical pipeline — not a stale or divergent copy.
**制度価値:** Names and treats context-freshness as a first-class institutional risk in its own right, rather than an assumed property of "the system works."
**証拠 (both the mechanism and its documented failure modes, per fairness requirement):** the essence pipeline (RAW→REDUCED→RE_REDUCED→REDUCING→CORE→ESSENCE) and `essence_auto_updater.py v3` (5-minute interval); **and**, critically, three linked Integrity Classifications (IC_20260707_001/002/003) that found a *third*, divergent `lever_essence.json` copy (in `planningcaliber/workshop/needle_eye_project/`) was being read by `app.py`'s COMMAND CENTER display and by two unauthenticated public endpoints (`/public/essence`, `/essence/detail`), independent of the canonical pipeline; **and** a subsequent, larger corrective finding referenced in `mocka_get_essence`'s OPERATION field (2026-07-09, "Incident A完了", "重大訂正を含む"): the actual real-world injection path for one major consumer (a Chrome extension via `/api/handshake`) was found to be *entirely different* from the originally assumed path (`ping_generator.py`), meaning an earlier working hypothesis about how Living Context reached that consumer was formally corrected after investigation.
**運用状況:** Actively used, actively investigated, and — importantly — actively subject to major structural corrections when found wrong. The 2026-07-09 correction is explicitly logged as a "重大訂正" (significant correction), not quietly patched over.
**NISTとの差異:** NIST does not address the problem of AI-session context provenance/freshness at all — this is a problem specific to systems (like MoCKA) that maintain continuity across memoryless AI sessions, which is outside NIST's CI-operator frame.
**Maturity:** Operational, explicitly **not fully Verified** — the corrective history above is exactly the point: this element's evidence trail includes its own documented failures and corrections, which is more credible than an unblemished claim would be, but it also means "Living Context is reliable" cannot be asserted as Verified across the board — only that the specific, previously-known divergences have been found and are being tracked to resolution (IC_20260707_003 remains Open at time of this audit).

### 1.10 Seal Governance
**目的:** Cryptographically anchor the state of the institutional record at intervals, producing a tamper-evident checkpoint.
**制度価値:** Gives "has anything been silently altered" a checkable answer via hash comparison, rather than relying on trust.
**証拠:** `anchor_update.py`, `ledger_verify.py`, SHA-256 hashing, "ALL CHECKS PASSED" status; `governance.latest_seal` (sha256 hash recorded, event_count 12171, dated 2026-06-18) and `current_view.seal_status` (a more recent seal recorded 2026-07-07T11:03:41Z, type `manual_external_post`).
**運用状況/Honest caveat:** The underlying seal mechanism (`governance/anchor_record.json`) was independently confirmed, during MoCKA's own audit, to be healthy and updating close to real time. However, that same audit (IC_20260707_005, still **Open**) found that the human-facing COMMAND CENTER display reads a *different*, defunct file (`runtime/main/ledger.json`, unmodified since 2026-04-16) and has therefore been showing an apparently-broken seal status for over three months while the real mechanism was functioning. This is recorded here as a caveat on the *reporting* layer, not the cryptographic mechanism itself, which the evidence supports as genuinely operational.
**NISTとの差異:** NIST Task 10.2 asks for "immutable" log storage and integrity/tamper-evidence controls but does not specify a cryptographic sealing/hashing mechanism at the level of detail MoCKA implements (periodic SHA-256 anchoring with an explicit pass/fail check gate).
**Maturity:** Operational for the seal mechanism; **not Verified for the reporting/display layer**, which has a confirmed, currently open discrepancy.

### 1.11 Evidence Chain
**目的:** Make every institutional claim traceable through a linked chain: Event → Integrity Classification (if relevant) → Decision → Resolution, each with its own ID, so that "why do we believe X" can be walked back to primary sources rather than trusted on assertion.
**制度価値:** This is the mechanism that made the rest of this Beyond-NIST document possible to write with citations rather than paraphrase-of-paraphrase.
**証拠:** Cross-referencing fields present on every Integrity Classification record (`related_events`, `related_documents`) and on Decision records; concrete example: IC_20260708_003's record links to `DC_20260708_007`, `IC_20260707_006`, `IC_20260708_002`, and a specific document path (`docs/audits/AUTO_SEAL_50EVT_権限実態調査報告.md`), forming a walkable chain from a specific commit hash through to the governing decision that closed it.
**運用状況:** Consistently applied across all 31 Integrity Classification records read in this session — none were found with empty cross-reference fields where a related event or decision plausibly existed.
**NISTとの差異:** NIST Task 10.1/12.1.2 asks for provenance linking a generated artifact to "the specific model version, prompt, and inference context." MoCKA's Evidence Chain links at the *institutional* level (which event led to which finding led to which decision), a broader unit of provenance than per-artifact model/prompt linkage, and not something the NIST source's current Task set explicitly requires.
**Maturity:** Operational/Verified — directly exercised by this audit itself, which relied on these cross-references to check claims against each other (e.g., catching that IC_20260707_006's "Resolved" status required checking whether IC_20260708_001, a related but separately-tracked finding, had also actually been resolved before the parent record's resolution note could be trusted).

### 1.12 AI-to-Institution (multi-AI governance protocol)
**目的:** Govern interaction among multiple, distinct AI systems (ChatGPT, Perplexity, Gemini, Claude) operating against the same institutional record, including detecting and correcting when one AI's output conflicts with or fabricates against another's.
**制度価値:** Treats "the AI said so" as a claim requiring institutional verification, not an authoritative input — evidenced concretely, not aspirationally.
**証拠:** `ai_roster` (four named AI systems); a documented, named fabrication-rejection event: a Gemini-reported measurement (Z=0.88) was formally identified as fabricated and excluded, with the record explicitly stating "Gemini捏造Z=0.88は無効。Claudeの実測値のみ有効" preserved in the canonical overview for future reference; a documented unauthorized-overwrite incident attributed to ChatGPT that directly produced the Phase18 Human Gate policy (see 1.1); adapters with asymmetric, audited capability levels (`gateway/adapter_gpt.py`, `adapter_gemini.py`) whose asymmetry was itself caught and recorded by audit (IC_20260705_020).
**運用状況:** Actively operating — this is not a hypothetical protocol but the lived experience of running four heterogeneous AI systems against one shared record, with at least two concrete, named incidents where AI-provided output required institutional correction.
**NISTとの差異:** The NIST Discussion Draft's Practice 3.7 (Shadow AI) and Practice 5 (IdAM for AI agents) address *unauthorized* AI systems entering an environment. It does not address the distinct problem MoCKA has actually encountered and institutionalized a response to: multiple *authorized*, *known* AI systems producing mutually inconsistent or fabricated claims about the same shared institutional state, and requiring a formal cross-checking/rejection mechanism between them.
**Maturity:** Operational/Verified (both named incidents have durable institutional traces: a policy change in one case, a rejected-and-recorded value in the other).

---

## 2. Recommendations to NIST

Per R01 instruction, this section is strictly evidence-based: it identifies specific institutional design elements demonstrated above, with implementation and operational evidence, that this audit did not find addressed — even at the `(TBD)` stub level — in the NIST Discussion Draft's current text. These are offered as candidate discussion points for the Community of Interest process the source document itself invites feedback through (`aiciprof@nist.gov`), not as claims that NIST "should" adopt them.

1. **A gated-write control specifically for an AI system's own governing artifacts** (MoCKA: Human Gate, §1.1). The Discussion Draft's Practice 7.4 covers "Authorization and Access Controls for AI Modifications" broadly but does not distinguish the specific case of an AI-driven change targeting the control system that governs AI behavior itself (as opposed to an operational asset the AI merely acts upon). MoCKA's concrete, incident-driven motivation for this distinction (an AI overwrote its own governing file, prompting the Phase18 policy) could be a useful real-world case study for whatever future Practice or Implementation NIST develops in this area.

2. **A supersession-lifecycle decision record** (MoCKA: Decision Ledger, §1.2). NIST Task 7.3.1 asks for a version-identifying registry with change justification, scoped to AI safety mechanisms. A generalized, explicitly-superseding decision ledger (where a later ruling formally supersedes rather than silently overwrites an earlier one, with both preserved) could be a useful pattern for NIST to consider generalizing beyond the safety-mechanism-specific scope of Task 7.3.

3. **Cross-AI claim verification / fabrication rejection as a named practice** (MoCKA: AI-to-Institution, §1.12). The Discussion Draft's Practice 3.7 and Practice 5 address unauthorized AI systems; neither addresses verification of claims made *by* authorized, known AI systems against each other. MoCKA's evidence of a concrete fabricated-measurement rejection is a real-world instance NIST's Community of Interest process may find useful when considering whether such a practice belongs in a future draft, particularly as organizations increasingly use multiple AI systems in combination (the source document's own authorship note discloses use of two different AI systems in drafting the Discussion Draft itself).

4. **Context-freshness/provenance tracking across memoryless AI sessions** (MoCKA: Living Context / Institutional Memory, §1.4/§1.9). NIST's Practice 4.2 (situational awareness) and Practice 9 (training) are written for human operators with continuous employment and memory. Organizations relying on AI systems that do not persist memory between sessions face a structurally distinct version of the "situational awareness" problem NIST already recognizes as important; MoCKA's evidence — including its own documented history of getting this wrong and correcting it (IC_20260707_001–003, the 2026-07-09 "Incident A" correction) — may be a useful input to any future guidance on this point.

5. **Self-auditing incident/integrity classification as a standing practice, not a post-incident-only activity** (MoCKA: Institutional Verification, §1.8). NIST Practice 8 is framed around responding to AI-related failures after they occur. MoCKA's Integrity Classification Ledger is exercised proactively and continuously (e.g., IC_20260707_006's detection method being "a Decision Ledger and Integrity Classification cross-check that found the two records disagreed with each other" — an audit of the audit process itself), which is a somewhat different posture than the incident-triggered framing of the current draft's Practice 8.

---

## 3. Critical Infrastructure Application Scenarios

**Framing (required for fairness):** MoCKA does not operate in any of the sectors below. The following are illustrative scenarios describing how a CI operator *could* apply MoCKA's evidenced institutional patterns (not MoCKA the product) to reinforce specific NIST Practices, grounded in what this audit has actually verified MoCKA does — not speculative capability. Nothing below should be read as a claim that MoCKA is deployed, certified, or validated for use in any CI sector.

**Power / Electric utilities:** NIST Practice 3.2 requires deterministic safety wrappers independent of the AI, and Practice 3.3 requires "fail loudly" notification with drift thresholds (Implementation 3.3.2 explicitly discusses seasonal demand-pattern drift in a water-distribution AI as a worked example). A utility's AI-governance layer (the software/process layer that decides which AI-generated grid-optimization recommendations get promoted to production, distinct from the physical safety-instrumented systems on the grid itself) could apply MoCKA's evidenced Decision Ledger + Human Gate pattern to gate exactly the "promote this AI-recommended setpoint logic to production" step described in NIST Task 12.1.3 ("Authorization of Machine-Authored Logic"), with the Regression Governance drift-classification pattern (§1.6) as a template for the kind of anomaly taxonomy NIST's Practice 2.3/3.4 calls for — while leaving the actual deterministic physical safety wrapper (NIST 3.2.2) to dedicated OT-layer engineering, which is explicitly outside MoCKA's demonstrated scope.

**Healthcare:** NIST's own Implementation 3.3.2 example explicitly names "a healthcare diagnostic AI should flag clinical drift when shifted between different patient demographics." MoCKA's Evidence Chain pattern (§1.11) — linking an event to a classification to a decision to a resolution, each independently citable — is structurally suited to the audit-trail requirement NIST Task 10.1.3 describes for "high-consequence applications processing sensitive person-centric data, such as healthcare clinical support decisions," where the draft calls for routing "raw, unredacted text and prompt history... into highly secured, tamper-evident storage." MoCKA's Seal Governance pattern (§1.10, with its documented reporting-layer caveat) illustrates both the value of cryptographic sealing for this purpose and a concrete cautionary example: a sealing mechanism can be genuinely sound while its human-facing status display is not, which is directly relevant to NIST's own emphasis on "audit-ready" evidence actually being trustworthy to read, not just cryptographically valid.

**Finance:** NIST Task 3.3.2 names "a financial liquidity model should trigger boundaries during sudden, non-historical macroeconomic shocks" and Task 8.1 requires deterministic root-cause reconstruction, explicitly warning that "auditors will reject post-hoc explanations as 'reconstructed narratives'" (citing a 2026 NERC CIP-015-1 preparedness reference). MoCKA's Institutional Verification pattern (§1.8) — where 31 recorded classifications each carry an explicit `detection_method` describing exactly how the finding was reached (e.g., "mechanical diff of 5,962 commits against a specific authorization function") rather than a narrative reconstruction after the fact — is a concrete illustration of the kind of forensic rigor NIST Task 8.1.2 is asking for when it says post-hoc explainability tools "should not be treated as forensic proof."

**Telecommunications:** NIST Practice 3.5 (adjacent-system risk, "splash damage"/"blast radius") and Practice 3.7 (Shadow AI detection) are both relevant to a sector where AI-driven network-optimization tools interact with many shared, adjacent systems. MoCKA's AI-to-Institution pattern (§1.12) — treating each AI system's output as a claim requiring institutional cross-verification rather than an authoritative input — illustrates a governance posture applicable to a telecom operator running multiple AI-driven network-management tools from different vendors: institutionalizing a practice of catching and formally rejecting a fabricated or inconsistent claim from one AI-driven tool (as MoCKA did with the Gemini fabrication, §1.12) before it propagates into an operational decision.

---

## 4. Maturity Summary Table

| Institutional Element | Maturity | Key caveat if any |
|---|---|---|
| Human Gate | Operational | Confirmed open enforcement gap on one execution path (IC_20260708_004) |
| Decision Ledger | Operational/Verified | — |
| Knowledge Gate | Concept/Implemented | Content not independently verified this session |
| Institutional Memory | Operational/Verified | Verified via its own staleness self-reporting |
| Decision Unit | Operational/Verified | Same evidence base as Decision Ledger |
| Regression Governance | Operational/Verified | Has documented false-positive correction history |
| Shadow Architecture | **Concept only** | No drill/test evidence found for the "75%" claim |
| Institutional Verification | Operational/Verified | Best-evidenced element in this analysis |
| Living Context | Operational | One related finding (IC_20260707_003) still Open |
| Seal Governance | Operational | Confirmed open display-layer bug (IC_20260707_005) |
| Evidence Chain | Operational/Verified | — |
| AI-to-Institution | Operational/Verified | — |

**Next document:** `MOCKA_EVIDENCE_MATRIX_v1.0.md` — a pure evidence listing (no prose) separating Public / Internal / Decision Ledger / Repository / Implementation evidence for every claim made across all documents in this audit.

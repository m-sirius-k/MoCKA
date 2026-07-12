# MoCKA × NIST Requirement Mapping v1.0

**Input (canonical, no re-extraction performed):** `NIST_REQUIREMENT_CATALOG_v1.0.md` — 12 Practices, 53 Tasks, drawn from *NIST AI RMF Profile on Trustworthy AI in Critical Infrastructure, Community of Interest Discussion Draft, Jul 7 2026* (`X:\down\DiscussionDraft_NIST_AIRMF_TACIP_20260707.pdf`).

**Evidence base for this mapping:** direct MCP tool queries against the live MoCKA system performed in this session (`mocka_get_overview`, `mocka_get_essence`, `mocka_integrity_list` — 31 Integrity Classification records read in full, `mocka_decision_list` metadata), plus the MoCKA repository structure at `C:/Users/sirok/MoCKA` confirmed via the canonical `MOCKA_OVERVIEW.json`. Where a claim rests on a document whose *content* was not read in this session (only its filename/existence is known from the `docs/governance/` directory listing), this is marked **[name-only]** and scored conservatively (never FULL or SUPERIOR on a name-only basis).

**Critical domain-scope framing (read before the table):** MoCKA is a software/knowledge-governance institutional system that governs AI-assisted work across its own repositories (code, documents, decisions). It is **not** a Critical Infrastructure operator — it does not run OT/ICS equipment, valves, PLCs, SCADA, medical devices, or grid assets. A large fraction of the NIST Discussion Draft's Tasks are written specifically for physical-process control (e.g., "watchdog controllers" on valves, deterministic setpoint constraints, patient-record transaction bounding, grid stability terminology). For these, MoCKA's honest status is **NONE** — not because the underlying governance principle is unaddressed, but because there is no physical CI asset for the mechanism to attach to. This is stated once here rather than repeated 53 times; it is the primary reason many Practice 2/3/4/5/11 physical-layer Tasks below score NONE despite MoCKA having a strong analogous mechanism at the *software change-governance* layer.

**Status legend:** FULL / PARTIAL / PLANNED / NONE / SUPERIOR (per Task instructions). **SUPERIOR is never assigned by impression** — every SUPERIOR row below carries a `SUPERIOR justification:` line comparing NIST requirement → MoCKA institution → implementation → operation → evidence, per R01 addendum. **Maturity** (separate axis, applies to the MoCKA institutional component, not to the NIST requirement): **Concept** (designed/documented only) / **Implemented** (code or artifact exists) / **Operational** (in active day-to-day use) / **Verified** (independently checked, cross-referenced, or has survived an audit — evidenced by an Integrity Classification, Decision record, or explicit test result).

---

## Practice 1 — Establish requirements for success

| Task | MoCKA Component | Evidence | Status | Maturity |
|---|---|---|---|---|
| 1.1 Identify current requirements | TODO record system (`mocka_add_todo`/`mocka_get_todo`) as the requirement-capture unit; Constitution principle "All decisions preserve 5W1H" | `mocka_get_overview` → `current_view.todo_summary` (43 未着手/8 進行中/419 完了 as of 2026-07-11); `what_is_mocka.constitution` | PARTIAL — TODOs capture *work* requirements generically; there is no per-AI-system "Requirements Summary" artifact distilling measurable success criteria as NIST 1.1.1 describes | Operational |
| 1.2 Create quantitative baselines, normal and challenging conditions | Fluid Coordinate Theory (X=Institutional Integrity, Y=Record Quality, Z=Governance Stability), `trajectory.csv`, `evaluator_dynamic.py` | `mocka_get_overview.fluid_coordinate_theory`: current values X=0.632/Y=0.826/Z=0.819; documented before/after measurement Z_before=0.6036→Z_after=0.8190 (ΔZ=+0.2154, "Claude実測値" — a competing AI-reported value of Z=0.88 was formally rejected as fabricated) | PARTIAL — a genuine quantitative baseline mechanism exists, but it measures MoCKA's own institutional health axes, not an external "AI system's" task performance in the NIST sense; domain mismatch, not absence | Operational/Verified (the rejection of the fabricated Gemini value is itself evidence of a working verification step) |
| 1.3 Implement evaluation and test plans, including TEVV, across the AI lifecycle | `docs/governance/AUDIT_STANDARD_PHASE1_FACT_COLLECTION_v0.1.md`, `MOCKA_AUDIT_STANDARD_DRAFT_v0.1.md`, `VERIFICATION_LOG_v0.1.md`, `GUARANTEE_VERIFICATION_MATRIX_v0.1.md` **[name-only]** | `docs/governance/` directory listing only; content not read in this session | PARTIAL | Concept/Implemented (unverified this session) |
| 1.4 Establish Domain Knowledge and Linguistic Alignment Requirements | `VOCABULARY_CONSTITUTION_v0.1.md`, `TERM-001_REGISTRY_TERMINOLOGY.md`, `CATEGORY_REGISTRY_v2.0.md` **[name-only]** | Directory listing only | PARTIAL | Concept/Implemented (unverified this session) |

---

## Practice 2 — Define AI Robustness, Resilience, and Quality of Service expectations

| Task | MoCKA Component | Evidence | Status | Maturity |
|---|---|---|---|---|
| 2.1 Establish AI usage thresholds and rate control mechanisms | No confirmed equivalent found | — | NONE | — |
| 2.2 Establish requirements for redundancy in AI-driven functions | "Shadow Movement" (縮退運用 — degraded operation maintaining ~75% function during partial failure) | `mocka_get_overview.what_is_mocka.structure.shadow_Movement` | PARTIAL — the concept is defined at the institutional-philosophy level; no operational test evidence of the 75% figure was found in this session | Concept (design-level claim only; not independently verified this session) |
| 2.3 Establish protocols for systematic, achievable TEVV | Router anomaly classification (`calc_drift_v3`, AEGIS classifier: FAST_WRONG/SLOW_DRIFT/FORMAT_COLLAPSE/DEPENDENCY_BREAK), `data/recurrence_registry.csv` (87 recorded recurrence entries, false-positive cleanup documented) | `mocka_get_overview.router` section: "recurrence_data.total": 87, "false_positives_cleared": true, fix history with commit hashes (6561fc5) | PARTIAL — this is a real, evidenced anomaly-classification and drift-detection mechanism for MoCKA's own automation, analogous in spirit to NIST 2.3's TEVV cadence, but not built or validated against the NIST-specified "validated standard dataset" methodology | Operational (recurrence registry has a documented bug-fix history, i.e. it has been exercised and corrected in production) |
| 2.4 Perform Linguistic and Domain-Context Robustness Testing | CP932/UTF-8 mandate enforcement (`check_utf8_mandate.py` Rule4/5, `PYTHONUTF8=1`) | `mocka_get_overview.governance.write_policy`: "TODO_333系: CP932/UnicodeEncodeError再発防止...check_utf8_mandate.py Rule4/5追加済み"; `verified_working` list confirms TODO_333完了 | PARTIAL — this is character-encoding robustness testing, a narrow real instance of "domain-context robustness," not linguistic/terminology robustness testing against sector jargon as NIST 2.4 describes | Operational/Verified (has a documented incident-driven origin and completion record) |
| 2.5 Verify and Ensure Policy Robustness Against Component, Hardware, and Data Schema Variance | No confirmed equivalent — MoCKA has no hardware/component substrate to vary | — | NONE (domain mismatch — no physical components) | — |

---

## Practice 3 — Define risks, policies, and oversight for automated AI and agentic behavior

| Task | MoCKA Component | Evidence | Status | Maturity |
|---|---|---|---|---|
| 3.1 Identify risk tradeoffs | Integrity Classification Ledger (state=Risk entries specifically) | `mocka_integrity_list`: e.g. IC_20260708_004 (state=Risk, type=Intent Conflict — Human Gate not wired into `/audit/seal` execution path), IC_20260707_004/003 (state=Risk) — each documents a specific risk tradeoff with impact scope | PARTIAL — real, dated, specific risk documentation exists for MoCKA's own AI-driven changes, but it is retrospective/discovered risk cataloging, not the prospective decision-point mapping (3.1.1–3.1.4) NIST describes | Operational/Verified (each entry has `detection_method` and cross-references — these are audited findings, not assertions) |
| 3.2 Implement independent guardrails ("safety wrappers") for AI outputs | Human Gate mechanism(s); **but see gap below** | `mocka_get_overview.governance.write_policy`: "Phase18以降: コアシステムファイルへの書き込みは人間ゲート承認必須" | PARTIAL — a Human Gate policy exists and is *stated* to guardrail core-file writes, but IC_20260708_004 (Open, unresolved as of this session) documents a live execution path (`/audit/seal` → `SealGovernanceGate.execute()` → GL7 `ALLOW`) that **executes without the additional Human Gate approval the system's own design docstring says is required**. This is a genuine, currently-open gap, not a resolved control. | Operational but **not Verified** for this specific path — the Integrity Ledger itself records this as an open, unresolved risk |
| 3.3 Establish Failure Notification Requirements | Integrity Classification `state` taxonomy (Failure/Risk/Unknown) functions as a failure-notification/classification scheme for MoCKA's own operations | `mocka_integrity_list` — 31 records, each carrying a `state`, `type`, `status` (Open/Resolved) | PARTIAL — classification exists and is applied consistently, but it is post-hoc incident classification, not real-time "fail loudly vs. silent recovery" policy for an operating AI system | Operational/Verified |
| 3.4 Monitor for anomalous AI behavior | Router `calc_drift_v3` / AEGIS anomaly classifier (see 2.3) | Same as 2.3 | PARTIAL | Operational |
| 3.5 Define and control risks to adjacent and related systems | `mocka_registry_current_state` (Lifecycle-derived state, no stored "current" flag — always recomputed) touches dependency-awareness but no explicit cascading-failure/blast-radius mapping was found | `mocka_registry_current_state` tool description | PARTIAL | Concept |
| 3.6 Mitigate automation complacency and skills degradation | No confirmed equivalent — MoCKA's operators are the AI systems and one human principal (きむら博士), not a shift-based human operator workforce; the "skills degradation" framing does not transfer | — | NONE (domain mismatch) | — |
| 3.7 Govern and mitigate risks from unauthorized, transient, and "Shadow AI" systems | Multi-AI governance / AI roster + documented incidents of exactly this risk category materializing | `ai_roster`: ChatGPT, Perplexity, Gemini, Claude, each with role-scoped access; **documented incidents**: ChatGPT overwrite incident (referenced in `write_policy` as the origin of the Phase18 Human Gate rule), Gemini fabrication incident (Z=0.88 rejected, see 1.2), IC_20260705_003 (Relay extension is claude.ai-only — an *absence* of unauthorized cross-AI reach, found and documented rather than assumed) | **SUPERIOR** — *SUPERIOR justification:* NIST Task 3.7 asks organizations to "detect, restrict, and manage risks associated with unvetted or unauthorized AI systems... brought into the operational environment," with Implementations 3.7.1–3.7.2 both marked `(TBD)` in the source (no implementation content yet, only a reviewer note asking how to balance concision vs. direction). MoCKA, by contrast, has a live multi-AI environment (4 AI systems with different capability levels interacting with the same institutional record) and has *already experienced and formally recorded* two concrete unauthorized/uncontrolled-AI-action incidents (an unauthorized overwrite by ChatGPT, and a fabricated evaluation result from Gemini), each of which produced a durable institutional response (Phase18 Human Gate write-policy in the first case; formal rejection and correction of the fabricated value in the second, preserved in `MOCKA_OVERVIEW.json` for future reference). The evidence is a governance response to a *realized* incident, not a designed-but-untested control. This satisfies the "implementation + operation + evidence" bar the NIST source itself has not yet reached for this Task. | Operational/Verified |

---

## Practice 4 — Define procedures for emergency avoidance override, recovery, and situation awareness

| Task | MoCKA Component | Evidence | Status | Maturity |
|---|---|---|---|---|
| 4.1 Establish "break glass" intervention procedures | Human Gate override mechanism (`human_gate_override_event_id` parameter in `mocka_git_safe_commit.py`) | IC_20260708_004 description explicitly names this parameter and notes it "渡されたevent_idの実在性・Human Gate APPROVED状態との整合性を一切検証しない" (does not verify the event_id it's given actually corresponds to an approved Human Gate decision) | PARTIAL — an override *path* exists (satisfying the letter of "can be overridden") but its own audit finds the verification binding it to actual approval is missing — the override mechanism itself is under-verified | Implemented, not Verified (the audit finding is evidence of the gap, not of the control) |
| 4.2 Ensure personnel can gain and maintain situational awareness | COMMAND CENTER UI (`localhost:5000`), essence pipeline (RAW→REDUCED→CORE→ESSENCE) | `mocka_get_overview.command_center`, `mocka_get_essence` (returns latest INCIDENT/OPERATION/PHILOSOPHY entries) | PARTIAL — a live situational dashboard exists and is actively used, but IC_20260707_001/002/003 (three linked, still partially Open incidents) document that the dashboard's own "essence" display has, at points, shown stale or duplicated data (a third `lever_essence.json` copy diverged from the canonical pipeline and was exposed on an unauthenticated public endpoint) — i.e., the situational-awareness mechanism has a documented history of *not* reliably reflecting ground truth | Operational, contested Verified status (see gap) |
| 4.3 Establish independent ("out-of-band") communication/monitoring/control capabilities | No confirmed equivalent for an out-of-band channel independent of the AI-mediated system itself | — | NONE | — |
| 4.4 Attention Governance and Alert/Alarm Flood Mitigation | Recurrence registry false-positive cleanup (77 false positives cleared, see 2.3) is a related but narrower mechanism | Same as 2.3 | PARTIAL | Operational |
| 4.5 Define operational regimes for human-on-the-loop / human-out-of-the-loop operation | Human Gate policy in principle distinguishes gated (human-on-the-loop, for core files) vs. ungated (human-out-of-the-loop, for non-core changes) operation | `write_policy` distinguishes core-system-file writes (gated) from other writes; but see 3.2/4.1 gaps | PARTIAL | Operational, gapped |

---

## Practice 5 — Implement identity and access management (IdAM) for AI agents, systems, and tools

| Task | MoCKA Component | Evidence | Status | Maturity |
|---|---|---|---|---|
| 5.1 Require identities and authentication for AI entities | AI roster with named, distinct AI identities (ChatGPT/Perplexity/Gemini/Claude) each interacting through separate adapters (`gateway/adapter_gpt.py`, `adapter_gemini.py`) | `mocka_get_overview.ai_roster`; adapter files referenced in Integrity Ledger (IC_20260705_020/021) | PARTIAL — AI systems are named/distinguished at the product/role level (which AI, which adapter), which is coarser than NIST's per-invocation "AI entity" granularity (ephemeral, individually revocable); no evidence of cryptographic non-human identities | Implemented |
| 5.2 Determine and enforce specific access requirements | Same adapters, asymmetric capability (e.g., IC_20260705_020: GPT adapter has read+write, Gemini adapter write-only as of the finding) | IC_20260705_020 (state=Failure, status=Open) | PARTIAL — access is *de facto* differentiated by what each adapter implements, but this reads as an implementation gap discovered by audit rather than a deliberately enforced, documented access policy | Implemented, gapped |
| 5.3 Enforce principles of least agency and least privilege for AI entities | No confirmed formal least-agency/least-privilege policy found; `app.py` was found in this same audit lineage to have **no authentication middleware at all** (`@app.before_request` absent, confirmed by grep per IC_20260708_004) | IC_20260708_004 | NONE — the strongest available evidence in this session points to an *absence* of enforced least-privilege at the application layer, not a partial implementation | — |
| 5.4 Implement continuous security monitoring for AI entity actions | Event Ledger (append-only, ~15,400 events) logs AI-driven actions broadly | `mocka_get_overview.current_view.recent_events` (count 15404, latest 2026-07-11T05:31:45Z) | PARTIAL — continuous logging of *actions in general* exists (see Practice 10), but no evidence of monitoring specifically scoped to AI-entity authentication/access-boundary violations was found | Operational |

---

## Practice 6 — Integrate visibility of the external supply chain of AI into vendor and 3rd party risk management

| Task | MoCKA Component | Evidence | Status | Maturity |
|---|---|---|---|---|
| 6.1 Develop policies for AI supply chain requirements | No AIBOM-equivalent or vendor-disclosure policy found; MoCKA consumes commercial AI vendors (Anthropic, OpenAI, Google) as a user, not as a CI procurement organization vetting AI vendors for its own supply chain | — | NONE (also domain mismatch — MoCKA is not procuring AI for a CI operational deployment) | — |
| 6.2 Align AI and existing CI asset lifecycle management | Registry system tracks lifecycle *state* for MoCKA's own components (`mocka_registry_current_state`, Registry Charter/Schema/Semantics/State-Model/Validation docs) but not externally-sourced AI components specifically | `mocka_registry_current_state` description; `docs/governance/REGISTRY_*` **[name-only for content]** | PARTIAL | Concept/Implemented |
| 6.3 Identify and control dataflows across the AI supply chain | No confirmed equivalent | — | NONE | — |

---

## Practice 7 — Manage internal AI supply chain and data provenance

| Task | MoCKA Component | Evidence | Status | Maturity |
|---|---|---|---|---|
| 7.1 Maintain an Internal Registry of AI Deployments | Repository/products inventory in `MOCKA_OVERVIEW.json` (`repositories`, `products` sections: Orchestra, Relay, PHI-OS, Memory, vasAI, PR-OS, Prism) with status per product | `mocka_get_overview.repositories`, `.products` | FULL — this is a maintained, versioned inventory of internally-deployed AI-adjacent systems with status, ownership (owner.name), and paths, matching the spirit of NIST 7.1.1's "Master AI Asset List" reasonably closely for MoCKA's own scope | Operational/Verified (the overview itself documents cross-checked staleness — see caveat below) |
| 7.2 Validate data provenance for model inputs | Event Ledger's append-only design plus explicit "Event history is the single source of truth" constitution clause | `what_is_mocka.constitution` | PARTIAL — the event ledger provides provenance for *institutional records*, not for AI model training/RAG input data specifically (MoCKA does not train models) | Operational |
| 7.3 Manage Version Control and Logging for Internal AI Safety Mechanisms | Decision Ledger (`mocka_decision_list`/`decision_get`) as version-controlled record of safety/policy-relevant decisions, with `Superseded`/`Withdrawn`/`Active` status field | `mocka_decision_list` tool schema (status filter: Active/Superseded/Withdrawn); DC_20260711_001 (TODO_442 remediation decision) as a concrete example of a logged, justified policy change | FULL — this closely matches NIST 7.3.1's "registry that uniquely identifies... version... Document every change... with technical justification" | Operational/Verified |
| 7.4 Define Authorization and Access Controls for AI Modifications | Human Gate write-policy for core system files | `write_policy` (Phase18 rule) | PARTIAL — a policy exists but 3.2/4.1 findings show its enforcement has at least one confirmed live gap | Operational, gapped |
| 7.5 Conduct Impact Assessments and Risk Management for AI System and Model Updates | TODO_442 example: a defect in `mocka_update_todo`'s "completed" state handling was found, decided (DC_20260711_001), and remediated with "実証テスト全項目PASS" recorded before closure | `mocka_get_essence` INCIDENT field, 2026-07-10 entry | PARTIAL — individual instances of pre-deployment validation and decision-gated remediation are well evidenced (this one case is strong), but no systematic "champion-challenger shadow mode" equivalent was found | Operational (evidenced per-instance, not as a systematized program) |
| 7.6 Establish processes for internal AI component deprecation and decommissioning | TODO abolition status ("廃止" — 14 items in current TODO summary) functions as a decommissioning-adjacent record | `current_view.todo_summary.廃止: 14` | PARTIAL | Operational |

---

## Practice 8 — Incorporate AI-aware incident analysis and response procedures

| Task | MoCKA Component | Evidence | Status | Maturity |
|---|---|---|---|---|
| 8.1 Identify scenarios requiring deterministic root cause analysis and incident reconstruction | Integrity Classification Ledger: every entry carries `detection_method`, `impact_scope`, `related_events`, `related_documents` — a structured root-cause record | `mocka_integrity_list` full 31-record read (e.g., IC_20260708_003's `detection_method`: "git log全AUTO_SEAL_50EVTコミット(5962件)とgovernance/mocka_git_safe_commit.pyのis_core_system_file()判定ロジックを機械的に突合する監査により発見") | **SUPERIOR** — *SUPERIOR justification:* NIST Task 8.1's own Implementations 8.1.1–8.1.5 are almost entirely `(TBD — suggestions welcome)` in the source (only the descriptive framing exists; no worked example of a completed root-cause reconstruction is given in the Discussion Draft itself). MoCKA's Integrity Ledger contains 31 *completed* root-cause classifications with named detection methods (e.g., mechanical diff of 5,962 commits against a specific authorization-check function), explicit impact scope, and a documented `status` transition from Open to Resolved with a resolution note and remediation commit hash for several entries (e.g., IC_20260708_002/003, resolved via DC_20260708_006/007). This is operative, dated, cross-referenced root-cause analysis output, not a template — a materially further point on the same requirement than the source document itself has published content for. | Operational/Verified |
| 8.2 Identify additional controls where deterministic root cause analysis is not possible | IC_20260705_015 ("watchdog_mocka.pyの起動経路不明" — state=Unknown, type="Not Verified") is itself an instance of MoCKA formally acknowledging when it *cannot* determine a root cause, rather than asserting one | IC_20260705_015 | PARTIAL — the ledger has a `state=Unknown` category precisely for this situation, which is a real (if narrow) instance of the practice, but no compensating-control policy for such cases was found | Operational (as a classification), no compensating-control policy confirmed |
| 8.3 Designate roles for AI incident governance | Human Gate + R01/R02 "audit officer" role pattern used repeatedly in the Integrity/Decision Ledger (e.g., "監査官R01裁定" appears as the adjudicating authority on multiple IC_ entries) | Multiple IC_ entries name "監査官R01" as the deciding party (e.g., IC_20260708_004, IC_20260708_003) | PARTIAL — a named adjudication role exists and is consistently exercised, but it is a single-person/rotating-role pattern, not the cross-functional legal/technical/risk/communications team NIST 8.3 describes | Operational/Verified (the role visibly renders repeated, dated decisions) |
| 8.4 Define external reporting and regulatory disclosure protocols following AI incidents | No confirmed equivalent — MoCKA has no external regulator relationship (it is not a regulated CI operator) | — | NONE (domain mismatch) | — |
| 8.5 Pre-arrange specialized resources for investigating and recovering from AI incidents | No confirmed equivalent | — | NONE | — |

---

## Practice 9 — Provide calibrated, needs-based AI risk management training

| Task | MoCKA Component | Evidence | Status | Maturity |
|---|---|---|---|---|
| 9.1 Perform role-based AI risk competency mapping | No confirmed equivalent — MoCKA's "roles" are AI systems and one human principal, not a trainable workforce | — | NONE (domain mismatch) | — |
| 9.2 Deliver specialized training on human-AI interaction and automation bias | Documented, written-up incidents (ChatGPT overwrite, Gemini fabrication — see 3.7) function as institutional-memory equivalents of "training material," consumed by future AI sessions via `mocka_get_essence`/`mocka_get_overview`, but this is knowledge injection into AI context, not human personnel training | `mocka_get_essence` PHILOSOPHY/INCIDENT fields | PARTIAL — the mechanism inverts NIST's assumption (it trains the AI participants against repeating past failures, not human operators against over-trusting AI); worth noting in Beyond-NIST analysis rather than scored as a direct match | Operational |
| 9.3 Establish audit-ready systems for verifying workforce readiness | No confirmed equivalent | — | NONE | — |

---

## Practice 10 — Implement multi-tiered AI system logging and audit capabilities

| Task | MoCKA Component | Evidence | Status | Maturity |
|---|---|---|---|---|
| 10.1 Define decision-level logging and metadata retention policies | Event Ledger (`events.db`, SQLite-unified since 2026-06-16, 11,929 events migrated from CSV at that time, 15,404+ events as of this session), `E{YYYYMMDD}_{NNN}` ID scheme, append-only constitution clause | `mocka_get_overview.governance.verified_working`: "SQLite単一化完了（events.csv完全廃止・2026-06-16移行 11929件）"; `current_view.recent_events.count: 15404` | FULL — decision-level logging with unique IDs and retained metadata is a core, actively-used, high-volume mechanism | Operational/Verified |
| 10.2 Establish data integrity and tamper-evidence controls for AI telemetry and logging | Seal Governance: `anchor_update.py`, SHA-256 hashing, "ALL CHECKS PASSED" verification gate | `mocka_get_overview.governance.latest_seal`: sha256 hash, event_count 12171, "ALL CHECKS PASSED"; but **caveat**: IC_20260707_005 (Open) found the COMMAND CENTER UI displays a stale, defunct ledger file (`runtime/main/ledger.json`, last updated 2026-04-16) instead of the actually-healthy, actively-updated `governance/anchor_record.json` (confirmed updated ~1 hour before the audit that found this) | PARTIAL — the underlying seal mechanism is real, cryptographically grounded, and actively functioning (this is a genuine, strong instance of tamper-evidence), but the *reporting layer* has a confirmed, still-open display bug that misrepresents seal freshness to a human reader, which is directly relevant to NIST 10.2/10.3's audit-review intent | Operational for the seal mechanism itself; **not Verified for the display/reporting layer** — actively contradicted by an open finding |
| 10.3 Implement systematic audit review and performance trend analysis | Integrity Classification Ledger functions as exactly this — periodic review producing classified findings | `mocka_integrity_list` | FULL | Operational/Verified |

---

## Practice 11 — Maintain AI-aware mission continuity and disaster recovery planning

| Task | MoCKA Component | Evidence | Status | Maturity |
|---|---|---|---|---|
| 11.1 Identify and prioritize AI-dependent essential functions | No formal ranked inventory found (Practice 7.1's asset list exists but is not explicitly ranked by continuity impact) | — | NONE | — |
| 11.2 Define manual and alternative operating procedures for long-term mission continuity | "Shadow Movement" (see 2.2) is the closest conceptual analogue | Same as 2.2 | PARTIAL | Concept |
| 11.3 Pre-allocate operational resources for alternative service delivery | No confirmed equivalent — no physical resources to pre-allocate | — | NONE (domain mismatch) | — |
| 11.4 Establish system integrity re-validation and re-commissioning protocols | Seal verification (`ledger_verify.py`, "ALL CHECKS PASSED" gate) functions as a re-validation checkpoint after changes | `governance.latest_seal.status` | PARTIAL | Operational |
| 11.5 Execute periodic mission continuity simulations and stress tests | No confirmed equivalent — no evidence of deliberate "AI infrastructure total loss" drills | — | NONE | — |

---

## Practice 12 — Validate AI-Generated Operational Logic and Artifacts

| Task | MoCKA Component | Evidence | Status | Maturity |
|---|---|---|---|---|
| 12.1 Establish Governance and Accountability for AI-Generated Execution Artifacts | Human Gate write-policy explicitly classifies "コアシステムファイル" as requiring approval, functioning as an artifact-risk classification (core vs. non-core) | `write_policy` | PARTIAL — a binary (core/non-core) risk classification exists; NIST 12.1.1 asks for a more granular Direct-Execution-Logic vs. Human-Mediated-Logic split, which was not found | Operational, gapped (see 3.2 enforcement gap) |
| 12.2 Implement Multi-Layered Validation of Machine-Authored Logic | `check_utf8_mandate.py` (deterministic, non-AI validator for a narrow class of artifact defects — encoding), Integrity Ledger findings as a form of expert (human-adjudicated) post-hoc review | `governance.write_policy` (TODO_333); `mocka_integrity_list` adjudication pattern | PARTIAL — deterministic automated checking exists for a narrow defect class; broader SME-style review is evidenced case-by-case via the Integrity Ledger's audit-officer adjudication pattern, not as a systematized multi-layer pipeline | Operational (narrow), Concept (broader pattern) |
| 12.3 Manage Operational Continuity and Resilience for Generated Artifacts | Decision Ledger's `Superseded`/`Withdrawn` status model functions as version control/rollback for institutional decisions; TODO_442 remediation (see 7.5) shows a documented rollback-adjacent fix cycle | `mocka_decision_list` status enum; `mocka_get_essence` TODO_442 entry | PARTIAL | Operational |

---

## Summary Tally

**Correction note (added during the Task7/8 fairness/consistency audit pass):** the Requirement Catalog's own Task count was originally mis-stated as 54; the correct total, recounted directly from Practice-by-Task enumeration (P1:4, P2:5, P3:7, P4:5, P5:4, P6:3, P7:6, P8:5, P9:3, P10:3, P11:5, P12:3), is **53**. The table below reflects the corrected total; no Status verdict on any individual Task changed, only the summary arithmetic.

| Status | Count (of 53 Tasks) |
|---|---|
| FULL | 4 (7.1, 7.3, 10.1, 10.3) |
| SUPERIOR | 2 (3.7, 8.1) |
| PARTIAL | 33 |
| NONE | 14 |
| PLANNED | 0 |

(4 + 2 + 33 + 14 = 53, reconciled.)

**Reading this tally honestly:** 14 of 53 Tasks (26%) are NONE primarily because of the domain-scope mismatch stated at the top of this document (MoCKA is not a CI/OT operator). Of the remaining 39 addressable Tasks, MoCKA has FULL or SUPERIOR evidence for 6 (15% of addressable Tasks) and PARTIAL evidence for 33 — meaning the modal MoCKA status against this profile is **PARTIAL**, not FULL or SUPERIOR. This is the expected, honest shape of the result for a system that was not designed against this NIST profile and is being retrofitted into its structure for comparison purposes.

**Next document:** `MOCKA_NIST_GAP_ANALYSIS_v1.0.md` extracts every NONE and PARTIAL row above and adds 不足理由 / 改善案 / 優先順位.

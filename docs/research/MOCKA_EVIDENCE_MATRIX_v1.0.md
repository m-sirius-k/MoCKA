# MoCKA Evidence Matrix v1.0

No prose. Pure evidence listing supporting all claims made in `NIST_REQUIREMENT_CATALOG_v1.0.md`, `MOCKA_NIST_REQUIREMENT_MAPPING_v1.0.md`, `MOCKA_NIST_GAP_ANALYSIS_v1.0.md`, and `MOCKA_BEYOND_NIST_ANALYSIS_v1.0.md`.

---

## A. Public Evidence

| ID | Item | Location | Verified how |
|---|---|---|---|
| PUB-01 | NIST AI RMF Profile on Trustworthy AI in Critical Infrastructure, Community of Interest Discussion Draft, Jul 7 2026 | `X:\down\DiscussionDraft_NIST_AIRMF_TACIP_20260707.pdf` (16pp, provided by requester in-session) | Full text extracted via `pdftotext -layout`, read in 4 passes covering all 3,622 lines |
| PUB-02 | NIST Concept Note: Trustworthy AI in Critical Infrastructure Profile, dated 2026-04-07 | nist.gov, `Concept Note_ Development of the NIST AI RMF Trustworthy Use of AI in Critical Infrastructure Profile.pdf` | Fetched and read in full (2 pages) prior to obtaining PUB-01; superseded as primary source once PUB-01 was provided |
| PUB-03 | NIST AI RMF Profile program page confirming Draft/Final publication dates "To be determined" as of search date | nist.gov/programs-projects/concept-note-ai-rmf-profile-trustworthy-ai-critical-infrastructure | WebFetch |
| PUB-04 | Confirmation that only the Concept Note (not a full draft) was publicly indexed at time of initial search | Web search results (regulations.ai, industrialcyber.co, theleveragedyears.com, nist.gov) | WebSearch, cross-checked across 4+ independent sources |
| PUB-05 | AIES 2026 paper submission and Zenodo DOIs for MoCKA-related academic publication ("Silence Prohibition Protocol and Persistent History Layer") | `mocka_get_overview.paper` — Submission282, DOI 10.5281/zenodo.19503666 / .19507632 / .19606271 | Cited from internal overview record only; **not independently verified against Zenodo/AIES in this session** — flagged as internal-record-only, not independently confirmed public evidence |

---

## B. Internal Evidence (MoCKA repository documents / records, content read this session)

| ID | Item | Path / Tool | Read in full or name-only |
|---|---|---|---|
| INT-01 | MOCKA_OVERVIEW.json full snapshot | `mocka_get_overview` (MCP tool) | Full content read |
| INT-02 | Essence pipeline latest INCIDENT/OPERATION/PHILOSOPHY | `mocka_get_essence` (MCP tool) | Full content read |
| INT-03 | Integrity Classification Ledger, 31 records | `mocka_integrity_list` (MCP tool) | Full content read (all 31) |
| INT-04 | Decision Ledger, Active-status records | `mocka_decision_list` (MCP tool) | **Not fully read** — result exceeded tool output size limit (120,963 chars / 1,593 lines); only metadata about its existence and a subset of decision IDs cross-referenced via Essence/Integrity records was used. Flagged as **verification debt**. |
| INT-05 | `docs/governance/` directory listing (183 files) | Bash `find` on `C:/Users/sirok/MoCKA/docs/governance` | Filenames only — **not read**, used solely to confirm existence for name-only citations (see INT-06) |
| INT-06 | Name-only governance documents cited but not content-read this session | `AUDIT_STANDARD_PHASE1_FACT_COLLECTION_v0.1.md`, `MOCKA_AUDIT_STANDARD_DRAFT_v0.1.md`, `VERIFICATION_LOG_v0.1.md`, `GUARANTEE_VERIFICATION_MATRIX_v0.1.md`, `VOCABULARY_CONSTITUTION_v0.1.md`, `TERM-001_REGISTRY_TERMINOLOGY.md`, `CATEGORY_REGISTRY_v2.0.md`, `REGISTRY_CHARTER_v1.0.md`, `REGISTRY_SCHEMA_v1.0.md`, `REGISTRY_SEMANTICS_v1.0.md`, `REGISTRY_STATE_MODEL_v1.0.md`, `REGISTRY_VALIDATION_v1.0.md`, `MODULE_REGISTRY_MODEL_v1.md` | Explicitly marked `[name-only]` throughout Mapping/Gap documents; scored conservatively (never FULL/SUPERIOR on this basis alone) |
| INT-07 | Two background research agents dispatched to build a deeper evidence dossier from the ~180-file governance corpus and MCP ledgers | Agent IDs `ace6adc033f17f7eb`, `a923bbe669a099f6f` | **Launched but not incorporated** — per explicit user instruction (成果物優先モード), this audit proceeded to write deliverables from already-gathered evidence (INT-01–04) without waiting for these agents to complete or report. Their output, if later retrieved, should be treated as a supplementary verification pass against this Evidence Matrix's INT-06 gaps, not a contradiction of it. |

---

## C. Decision Ledger Evidence (specific `decision_id` citations)

| decision_id | Cited for | Source of citation |
|---|---|---|
| DC_20260711_002 | "COMMAND CENTER v6.1退行インシデント監査フェーズの完了承認" — most recent decision at audit time | `mocka_get_overview.current_view.recent_decisions.latest` |
| DC_20260711_001 | TODO_442 remediation approach (案a採用) | `mocka_get_essence` PHILOSOPHY field, 2026-07-10 entry |
| DC_20260710_005 | TODO_437 timeout=12 adopted as mitigation, original hypothesis disproven by measurement | `mocka_get_essence` OPERATION field |
| DC_20260710_004 | TODO_413 close-scope decision (Git Commit経路のLedger記録制度保証まで) | `mocka_get_essence` PHILOSOPHY field |
| DC_20260708_007 / DC_20260708_006 | Referenced as resolving decisions for IC_20260708_003 / IC_20260708_002 | `mocka_integrity_list`, `related_documents` fields of those records |
| DC_20260708_001 | Post-hoc approval/formal close of IC_20260707_006 | `mocka_integrity_list`, IC_20260707_006 `resolution_note` |

**Caveat (per INT-04 above):** the full Decision Ledger (57 records per `current_view.recent_decisions.count`) was not read line-by-line this session. Only the subset of decision_ids that were cross-referenced by name inside the Integrity Ledger or Essence records (which *were* fully read) are cited above. Any Decision Ledger entry not named in this table was not used as evidence for any claim in the four analysis documents.

---

## D. Repository Evidence

| Repository | Path / Remote | Role (as self-described) | Used for |
|---|---|---|---|
| MoCKA (heart) | `C:/Users/sirok/MoCKA`, `git@github.com:m-sirius-k/MoCKA.git` | 心臓部・制度核 | Primary source for all analysis; canonical `docs/research/` output location |
| mocka-civilization | `C:/Users/sirok/mocka-civilization` | 設計思想・青写真層 | Named in overview only, not inspected this session |
| mocka-transparency | `C:/Users/sirok/mocka-transparency` | 改ざん検知・署名検証デモ層 | Named in overview only, not inspected this session |
| mocka-external-brain | `C:/Users/sirok/mocka-external-brain` | AIオーケストラ神経系・合議バス | Named in overview only, not inspected this session |
| mocka-core-private | `C:/Users/sirok/mocka-core-private` | 実装実験・検証環境（凍結中） | Named in overview only, not inspected this session |
| mocka-public | `C:/Users/sirok/mocka-public` | 公開ドキュメント・証明層 | Named in overview only, not inspected this session |
| mocka-knowledge-gate | `C:/Users/sirok/mocka-knowledge-gate`, `github.com/m-sirius-k/MoCKA-KNOWLEDGE-GATE.git` | 制度的記憶層 | Cited as "Knowledge Gate" institutional element (§1.3 of Beyond-NIST doc) — **existence confirmed, content not inspected** |
| mocka-outfield | `C:/Users/sirok/mocka-outfield` | 外野・公開ネットワーク層 | Named in overview only, not inspected this session |
| PHI-OS | `C:/Users/sirok/MoCKA/PlanningCaliber/workshop/phi-os/` | Chrome拡張Runtime Layer | Named in overview only; `phi_os/human_gate.py` referenced as one of three parallel Human Gate implementation surfaces |
| vasAI | `github.com/m-sirius-k/vasAI` | AI統治証明システム | Named in overview only, not inspected this session; v1.4.9 VERIFIED per overview record (not independently re-verified) |

---

## E. Implementation Evidence (specific code/config/tool artifacts)

| Artifact | Path (where known) | Cited for |
|---|---|---|
| `mocka_get_overview` | MCP tool (`mocka_mcp_server.py`, port 5002) | INT-01 |
| `mocka_get_essence` | MCP tool | INT-02 |
| `mocka_integrity_list` / `mocka_integrity_get` / `mocka_integrity_write` | MCP tool | INT-03; Institutional Verification (§1.8) |
| `mocka_decision_list` / `mocka_decision_get` / `mocka_decision_write` | MCP tool | Decision Ledger (§1.2), Decision Unit (§1.5) |
| `mocka_registry_current_state` / `mocka_registry_get` / `mocka_registry_add` | MCP tool | Registry evidence in Practice 6.2/3.5 mapping rows |
| `events.db` | MoCKA repo (SQLite, migrated from CSV 2026-06-16 per overview) | Event Ledger / Evidence Chain (§1.11), 15,404 events at audit time |
| `anchor_update.py` | `scripts/ledger/anchor_update.py` | Seal Governance (§1.10) |
| `ledger_verify.py` | `scripts/ledger/ledger_verify.py` | Seal Governance (§1.10) |
| `governance/anchor_record.json` | MoCKA repo | Seal Governance — confirmed healthy per IC_20260707_005 investigation |
| `runtime/main/ledger.json` | MoCKA repo | Seal Governance — confirmed **defunct** (unmodified since 2026-04-16) per IC_20260707_005 |
| `governance/seal_governance_gate.py` (`SealGovernanceGate.execute()`) | MoCKA repo | Human Gate enforcement gap, IC_20260708_004 |
| `structural/execution_governance.py` (GL7, `pre_execution_check()`) | MoCKA repo | Human Gate enforcement gap, IC_20260708_004 |
| `app.py` (`/audit/seal`, `civilization_loop.audit.last_seal`, essence routes) | MoCKA repo | IC_20260708_004 (no auth middleware, grep-confirmed), IC_20260707_005 (stale seal display), IC_20260707_001/002/003 (essence divergence) |
| `governance/mocka_git_safe_commit.py` (`human_gate_override_event_id` param) | MoCKA repo | Break-glass override validation gap (Gap Analysis, Category B) |
| `interface/router.py` (`calc_drift_v3`, `classify_anomaly`) | MoCKA repo | Regression Governance (§1.6) |
| `data/recurrence_registry.csv` | MoCKA repo | Regression Governance (§1.6), 87 entries |
| `check_utf8_mandate.py` (Rule4/5) | MoCKA repo | Practice 2.4/12.2 mapping (encoding robustness) |
| `gateway/adapter_gpt.py` | MoCKA repo | AI-to-Institution (§1.12), IC_20260705_020/021 |
| `gateway/adapter_gemini.py` | MoCKA repo | AI-to-Institution (§1.12), IC_20260705_020 |
| `essence_auto_updater.py` (v3) | `interface/essence_auto_updater.py` | Living Context (§1.9) |
| `data/lever_essence.json`, `interface/lever_essence.json`, `planningcaliber/.../lever_essence.json` (third copy) | MoCKA repo / planningcaliber repo | Living Context divergence findings, IC_20260707_001/002/003 |
| `mocka_update_todo` (completed-state edit defect) | `mocka_mcp_server.py` ~lines 477-543 per Essence record | Practice 7.5 (TODO_442 remediation example) |

---

## F. Explicit Evidence Gaps (recorded for transparency, not filled by inference)

| Gap | Consequence for this audit |
|---|---|
| Full Decision Ledger (57 records) not read in full — only cross-referenced subset (6 IDs, see Section C) | Decision Ledger maturity ratings rest on a sample, not the complete record; a future pass should read the full ledger via chunked file access |
| Two background research agents dispatched for deeper corpus verification were not incorporated (user directive: deliverable-first) | Several `[name-only]` items in Section B (INT-06) remain unverified at content level; Gap Analysis Category A item "1.3/1.4/6.2 content-verified TEVV/Registry governance docs" explicitly tracks this as verification debt, priority 中 |
| `mocka-knowledge-gate` repository content not inspected | Knowledge Gate (§1.3 of Beyond-NIST doc) is rated Concept/Implemented, explicitly not higher, for this reason |
| Shadow Architecture "75%" figure has no located test/drill evidence | Rated Concept-only in Beyond-NIST doc despite being a named, overview-documented claim |
| Zenodo/AIES publication claims (PUB-05) not independently re-verified against external Zenodo records in this session | Cited as internal-record claim only, not confirmed public fact |

**Next document:** `MOCKA_INSTITUTIONAL_COMPLIANCE_AND_BEYOND_SPECIFICATION_v1.0.md` — final synthesis integrating all four prior documents, no new research.

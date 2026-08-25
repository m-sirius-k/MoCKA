# P7-B Implementation Status Summary
**NIST Practice 7: Manage Internal AI Supply Chain and Data Provenance**

**Document Date:** 2026-08-25  
**Status:** Execution format (organized from MOCKA_NIST_REQUIREMENT_MAPPING_v1.0.md and MOCKA_NIST_GAP_ANALYSIS_v1.0.md)  
**Format:** What's implemented → What's unresolved → What should be next

---

## OVERVIEW

| Metric | Value |
|---|---|
| **Total Tasks** | 6 (7.1 – 7.6) |
| **FULL Status** | 2 tasks (7.1, 7.3) |
| **PARTIAL Status** | 4 tasks (7.2, 7.4, 7.5, 7.6) |
| **High Priority Gaps** | 1 (7.4 enforcement gap, IC_20260708_004) |
| **Medium Priority Gaps** | 1 (7.5 systematization, TODO_442 evidence) |

---

## IMPLEMENTATION STATUS BY TASK

### FULL IMPLEMENTATION (Ready for operations)

#### 7.1 — Maintain Internal Registry of AI Deployments
- **Status:** FULL
- **Maturity:** Operational / Verified
- **What's implemented:** Repository and products inventory in `MOCKA_OVERVIEW.json` (sections: repositories, products)
- **Maintained assets:** Orchestra, Relay, PHI-OS, Memory, vasAI, PR-OS, Prism
- **Evidence:** `mocka_get_overview.repositories`, `.products` with ownership, status, and paths
- **Note:** Version-controlled, actively updated with cross-checked staleness management

#### 7.3 — Manage Version Control and Logging for Internal AI Safety Mechanisms
- **Status:** FULL
- **Maturity:** Operational / Verified
- **What's implemented:** Decision Ledger (`mocka_decision_list`, `decision_get`) with version-controlled record of safety/policy changes
- **Status field values:** Active / Superseded / Withdrawn
- **Evidence:** Decision records include technical justification and cross-references; example: DC_20260711_001 (TODO_442 remediation decision)
- **Note:** Matches NIST 7.3.1 requirements (unique identification, versioning, documented changes with justification)

---

### PARTIAL IMPLEMENTATION (Gaps identified, remediation required)

#### 7.2 — Validate Data Provenance for Model Inputs
- **Status:** PARTIAL
- **Maturity:** Operational
- **What's implemented:** Event Ledger append-only design plus constitution clause "Event history is the single source of truth"
- **What's unresolved:** Event Ledger provides provenance for institutional records only, not for AI model training/RAG input data specifically (MoCKA does not train models)
- **Scope mismatch:** Gap is domain-related (MoCKA not a model trainer), not a missing control
- **Next action:** Document this scope boundary if/when external P7 profile publishing occurs

#### 7.4 — Define Authorization and Access Controls for AI Modifications
- **Status:** PARTIAL
- **Maturity:** Operational, **gapped**
- **What's implemented:** Human Gate write-policy for core system files (Phase 18 rule: coreaファイルへの書き込み require human approval)
- **What's unresolved:** Live gap in enforcement (IC_20260708_004, Open)
  - **Location:** `/audit/seal` execution path
  - **Finding:** `SealGovernanceGate.execute()` → GL7 `pre_execution_check()` → immediately executes `anchor_update.py` on `approved=True`, even though GL7's docstring states "approved=TrueでもHuman Gateの承認が別途必要"
  - **Root cause:** No code in this path requests or validates separate Human Gate approval
  - **Severity:** High (current live control gap)
- **Next action (HIGH PRIORITY):** Wire missing Human Gate check into `SealGovernanceGate.execute()` before GL7 ALLOW triggers `anchor_update.py`; this is MoCKA's own identified next step (TODO_429 boundary)

#### 7.5 — Conduct Impact Assessments and Risk Management for AI System and Model Updates
- **Status:** PARTIAL
- **Maturity:** Operational (per-instance evidence), not systematized
- **What's implemented:** Individual validation instances documented and verified
  - **Example:** TODO_442 defect in `mocka_update_todo` state handling
  - **Process:** Found → decided (DC_20260711_001) → remediated → "実証テスト全項目PASS" recorded before closure
  - **Evidence:** Logged in `mocka_get_essence` INCIDENT field (2026-07-10 entry)
- **What's unresolved:** No systematized "champion-challenger shadow mode" pattern for all AI-driven changes
  - **Current state:** Validation happens per-instance, case-by-case, dependent on audit-officer discovery
  - **Gap:** No standing, repeatable pre-deployment validation pipeline
- **Next action (MEDIUM PRIORITY):** Formalize existing validation habit into named, repeatable "shadow validate before completing core-file-touching TODO" step (documentation-level change, leveraging existing Decision Ledger + TODO infrastructure)

#### 7.6 — Establish Processes for Internal AI Component Deprecation and Decommissioning
- **Status:** PARTIAL
- **Maturity:** Operational
- **What's implemented:** TODO abolition status ("廃止") tracks decommissioning-adjacent record
- **Evidence:** 14 items marked 廃止 in current TODO summary (`MOCKA_TODO.json`)
- **What's unresolved:** Gap is definitional/documentation, not implementation
  - **Current:** Abolition is captured as a TODO status
  - **Missing:** Formal decommissioning *process* (notification, archive, retention policy) is not explicitly documented
- **Next action (LOW PRIORITY):** Document explicit decommissioning process (if needed for future governance clarity) or confirm current TODO-abolition status is sufficient

---

## REMEDIATION ROADMAP (Organized by Priority)

### HIGH PRIORITY

**7.4 Human Gate Enforcement Gap (IC_20260708_004)**
- **Incident:** `/audit/seal` execution path bypasses required Human Gate approval check
- **Affected tasks:** 7.4, plus cross-listed with 3.2, 4.1, 4.5 in the mapping (all share same root cause)
- **Remediation:** Wire missing Human Gate check into `SealGovernanceGate.execute()`
- **Status:** Defined in MoCKA's own backlog (TODO_429 boundary)
- **Completion criterion:** GL7 ALLOW cannot proceed to `anchor_update.py` execution without separate Human Gate approval validation

### MEDIUM PRIORITY

**7.5 Pre-deployment Validation Systematization**
- **Gap:** Champion-challenger pattern exists per-instance (TODO_442 example) but not as standing practice
- **Remediation:** Formalize into named, repeatable step ("shadow validate before completing core-file-touching TODO")
- **Effort:** Documentation-level change; reuses existing Decision Ledger + TODO infrastructure
- **Completion criterion:** Documented policy in governance materials, applied to next N core-file-touching TODO closures

**Related artifact classification clarity (cross-listed Task 12.1)**
- **Gap:** Binary core/non-core classification only; NIST proposes two-axis (proximity-to-execution × influence-on-human-decisions)
- **Remediation:** Extend core-file tagging with second axis (auto-execute vs. human-read)
- **Effort:** Low-cost documentation-and-tagging exercise (data already exists)
- **Completion criterion:** Core file list includes execution-mode tag (Direct-Execution vs. Human-Mediated)

### LOW PRIORITY

**7.2 Data Provenance Scope Documentation**
- **Status:** Gap is domain scope mismatch (MoCKA not a model trainer), not missing control
- **Action:** Document this boundary in any future external P7-profile publishing

**7.6 Decommissioning Process Formalization**
- **Status:** Current TODO-abolition tracking is operational; formality level depends on governance evolution needs
- **Action:** Confirm or upgrade depending on future multi-stakeholder governance requirements

---

## RELATED FINDINGS (Cross-cutting across multiple P7 tasks)

### Authenticated Access Control Gap (affects 7.4, 7.2, others)
- **Finding:** IC_20260705_020 + IC_20260708_004: `app.py` has no authentication middleware (`@app.before_request` absent)
- **Scope:** Asymmetric adapter capability (GPT read+write, Gemini write-only) discovered by audit, not designed
- **Related Tasks:** 5.2/5.3 (Least-privilege access control)
- **Remediation:** (1) Write explicit least-privilege policy per AI adapter; (2) add authentication middleware to `app.py` before further capability expansion

### Situational Awareness Display Gap (affects 7.4 context)
- **Finding:** IC_20260707_005 (Open): COMMAND CENTER seal-status display points at defunct file (`runtime/main/ledger.json`, unmodified since 2026-04-16) instead of actively-updated `governance/anchor_record.json`
- **Impact:** Dashboard shows "seal stopped 3.5 months ago" while actual seal mechanism is healthy and updating
- **Related Tasks:** 4.2/10.2 (Situational awareness accuracy)
- **Remediation:** Repoint display to `governance/anchor_record.json` (single-file fix, already scoped in backlog as TODO_371)
- **Status:** Backlog decision pending

---

## VERIFICATION CHECKLIST

- [x] All 6 NIST Practice 7 tasks mapped to MoCKA components
- [x] Implementation status assessed (2 FULL, 4 PARTIAL)
- [x] Gaps extracted from MOCKA_NIST_GAP_ANALYSIS_v1.0.md
- [x] Remediation actions organized by priority (High/Medium/Low)
- [x] Related incidents cross-referenced (IC_ identifiers)
- [x] Related TODOs identified (TODO_429, TODO_442, TODO_371)
- [x] Evidence base documented (FULL and PARTIAL both cite source)
- [x] Document scope: Organized existing Gap Analysis findings; no new requirements defined; no code changes; no Human Gate decisions authorized

---

## NOTES

This document organizes existing findings from `MOCKA_NIST_REQUIREMENT_MAPPING_v1.0.md` and `MOCKA_NIST_GAP_ANALYSIS_v1.0.md`. It does not:
- Introduce new P7-A requirements or definitions
- Authorize Human Gate decisions
- Propose code changes (only references existing backlog items)
- Establish automatic substitution of P7-B for any undefined P7-A

**Next governance action:** Human Gate review of High-priority remediation items (IC_20260708_004, TODO_429 boundary) per MoCKA's own governance process.

---

**Document prepared by:** MoCKA Execution Officer (くろこ)  
**Delivery format:** UTF-8 (no BOM), Markdown  
**Source reference:** MOCKA_NIST_REQUIREMENT_MAPPING_v1.0.md (lines 84-93), MOCKA_NIST_GAP_ANALYSIS_v1.0.md (lines 40-57)  
**Validation:** Gap Analysis entries verified against source lines; task numbering cross-checked against NIST_REQUIREMENT_CATALOG_v1.0.md

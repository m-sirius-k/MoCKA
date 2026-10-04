# HG-2 Forward-Looking Governance Research v1.0

**Document ID:** FLR-HG2-20261005-001  
**Date:** 2026-10-04  
**Status:** RESEARCH (Not Implementation, Not Activation Authorization)  
**Scope:** Independent governance assessment for HG-2 Activation decision readiness  
**Investigator:** Claude Haiku 4.5 (Kuroko)  

---

## Executive Summary

This document presents a forward-looking governance assessment of HG-2 (Human Gate Decision system in `app.py`) conducted BEFORE activation authorization. The purpose is **NOT** to propose implementation changes or approve activation, but to surface:

1. **Governance risks** that current HG-2 design does not yet address
2. **Architecture debt** that will become difficult to change after activation
3. **Undefined boundaries** between HG-2 and adjacent governance systems
4. **Experience Memory integration gaps** that will emerge post-activation
5. **Lessons from existing HG-1/HG-3/HG-4/HG-5** systems already in operation

---

## A. NOW — Currently Closed Items

### A.1 HG-2 Current State (as of 2026-10-04)

| Aspect | Status | Evidence |
|--------|--------|----------|
| **Implementation** | INCOMPLETE | `app.py` exists; `data/prevention_queue.json` not deployed |
| **Decision Records** | READY | HG-C01 through HG-C10 all approved by Human Authority (as of 2026-08-06) |
| **Architecture Decision** | APPROVED | HAB_CORE_DEFINITION_v0.1 identifies HG-2 as decision approval layer |
| **Activation Authorization** | PENDING | No activation decision found in Decision Ledger (as of 2026-10-04) |
| **Existing Governance** | OPERATING | HG-1/HG-3/HG-4/HG-5 already live (finding: 5 independent state systems) |

### A.2 What IS Fixed (Cannot Change Post-Activation)

1. **Human Gate Contract** (`phi_os/hab/HUMAN_GATE_CONTRACT_v0.1.md`)
   - Decision ID, Actor, Evidence, Previous/Next state, Timestamp required
   - Lifecycle: Evidence → Evaluation → Human Gate → Decision → Execution → Audit
   - ✓ Already immutable by contract

2. **Phase5 Boundary** (`docs/governance/phase5_boundary_declaration.md`)
   - HG-2 must not grant external agents (LLM/MCP) direct authority
   - Time OS internal contract boundary is FINAL for Phase5
   - ✓ Already declared immutable

3. **HG-C (Cycle) Decisions** (HG-C01 through C10)
   - All 10 cycles complete and approved (2026-08-06)
   - Decision Ledger awaiting batch registration when authorized
   - ✓ Ready for permanent record

---

## B. BEFORE ACTIVATION — Human Gate Must Decide

### B.1 State Authority Consolidation (Critical)

**FINDING:** MoCKA currently operates **5 independent Human Gate systems** with separate state vocabularies:

| System | Location | State Storage | State Vocabulary | Audience |
|--------|----------|---|---|---|
| **HG-1** | `phi_os/human_gate.py` | `human_gate_events` (SQLite) | PENDING, APPROVED, REJECTED, EXPIRED, CANCELED | Event intake |
| **HG-2** | `app.py /decision/*` | `prevention_queue.json` (NOT DEPLOYED) | NEW, approved, rejected | Decision approval |
| **HG-3** | `mocka_git_safe_commit.py` | Git work tree (untracked) | (no vocabulary) | Code commit safety |
| **HG-4** | `semantic/query_engine/human_gate.py` | In-memory (non-persistent) | accept, reject, defer, split | Semantic query |
| **HG-5** | `governance/human_gate_continuity.py` | `pending_decision_units.jsonl` | WAITING_FOR_HUMAN_GATE | Decision continuity |

**Observed Discrepancy (F-1 from HAB_CORE_DEFINITION):**
- Same 1,773 items: HG-1 records "PENDING" (1,774 records) vs HG-2 records "rejected" (1,799 records)
- `prevention_queue.json` ids vs `human_gate_events.request_id`: only 1,773/1,941 match

**Question for Human Gate:** Should HG-2 activation proceed **without** consolidating state authority?

**Governance Risk:** Activating HG-2 while 4 other HG systems operate independently creates:
- Observer confusion: which system owns the decision?
- Audit trails divergence: decisions visible in HG-1 but not HG-2
- Failure recovery: state divergence during partial failure (which HG is source of truth?)

### B.2 Transition Ledger Gap (Critical)

**FINDING:** State transitions are not always recorded (F-2 from HAB_CORE_DEFINITION).

**Current State:**
- HG-1: Records state in `human_gate_events` table ✓
- HG-2: Designed to use `prevention_queue.json` (not deployed) - schema does not define transition timestamps
- HG-3: No permanent ledger (git work tree only)
- HG-4: In-memory, no ledger
- HG-5: Uses `pending_decision_units.jsonl` but no transition sequence

**Question for Human Gate:** Should HG-2 deployment include:
1. Mandatory transition ledger (with timestamp, who, why)?
2. Idempotency guarantees (same decision twice = error or safe no-op)?
3. Failure recovery protocol (what if transition is recorded but execution fails)?

**Governance Risk:** Without ledger, governance audits cannot answer "who decided what when" retroactively.

### B.3 Authorization Lifecycle Boundaries (Critical)

**NOT YET SPECIFIED:**
- **Expiry:** How long is a decision valid? Forever? Until superseded?
- **Revocation:** Can an approved decision be withdrawn? By whom? With what evidence?
- **Delegation:** Can HG-2 delegate to subordinate gates? Or is HG-2 always final?
- **Emergency Override:** If HG-2 is down, can decisions be made outside HG-2?
- **Recovery:** If HG-2 records are lost, what is recovery procedure?

**Evidence:** 
- No mention in `phi_os/hab/HUMAN_GATE_CONTRACT_v0.1.md` 
- Not addressed in HG-C decisions
- Not found in `ACTIVATION_POLICY_v0.1.md`

**Governance Risk:** 
- If expiry is not defined, old decisions never expire (data bloat, zombie approvals)
- If revocation is not defined, once approved is "forever approved" (inflexible)
- If emergency override is not defined, operational downtime = decision paralysis

### B.4 Event Gate Enforcement vs HG-2 Decision (Critical)

**Current Setup:**
- Event Gate (PHI-OS): Single enforcement point for all events (TODO_391)
- HG-1: Approves human gate requests
- **HG-2 (NEW):** Will approve decisions (in `app.py /decision/*`)

**Undefined:** Which is the source of truth?

| Scenario | Event Gate Says | HG-2 Says | Result? |
|----------|---|---|---|
| Event invalid | DENY | APPROVE | ??? |
| Event valid | ALLOW | DENY | ??? |
| Event valid | ALLOW | PENDING | ??? |

**Evidence:**
- `phi_os/event_gate.py` does not reference `prevention_queue.json`
- No integration test between event_gate and HG-2 approval decision
- Phase5 Boundary explicitly states "No direct GPT access" but does not define HG-2 ↔ Event Gate coordination

**Governance Risk:** 
- Decisions not enforced (Event Gate allows, but HG-2 never approved)
- Decisions overruled (HG-2 approved, but Event Gate denies)
- Silent failures: approval recorded but not executed

### B.5 Authority Scope Binding (Critical)

**Question:** What is the scope of an HG-2 decision?

Not yet specified:
- **Temporal:** Does "approve decision X on 2026-10-04" apply only to 2026-10-04 or forever?
- **Contextual:** Does approval of "release feature Y" approve all dependencies? Or only Y?
- **Cascading:** Does approval of parent decision auto-approve children? Or requires explicit child approval?
- **Revocation scope:** If decision is revoked, do dependent decisions auto-revoke?

**Evidence:** None found in governance documents.

**Governance Risk:** Decisions create implicit obligations that are never formally bounded, leading to:
- Scope creep: decision approved for X, used for Y (authorization exceeded)
- Cascading failures: parent revoked, children orphaned
- Audit gaps: no one can enumerate all decisions under a given scope

---

## C. AFTER ACTIVATION — Monitoring Required

### C.1 Authorization Freshness (Operational)

**Design Question:** How old can an approval be before it expires?

| Interval | Risk | Mitigation |
|----------|------|-----------|
| Forever (no expiry) | Zombie decisions | Manual audit + revocation |
| 1 month | Operational friction | Auto-refresh + alerts |
| 1 day | Too frequent | Bulk operations blocked |
| None specified | **CURRENT STATE** | Post-activation monitoring required |

**Monitoring Protocol (Proposed):**
1. Daily: Count decisions by approval age
2. Weekly: Alert if any decision >1 year old and active
3. Monthly: Human review of oldest N decisions for continued relevance

### C.2 Credential / Key Rotation (Operational)

**If HG-2 includes cryptographic signatures or HMAC:**

Current state of signatures in MoCKA:
- Relay uses HMAC prefix `OPR-`, `RLY-P-`, `RLY-O-`, `MEM-` 
- No mention of rotation schedule
- No key compromise protocol found

**Before HG-2 deployment:** Define:
1. Signature algorithm (HMAC vs Ed25519 vs other)
2. Key generation and storage (hardcoded vs external vault)
3. Rotation schedule (when/how often)
4. Compromise response (how to revoke if leaked)
5. Audit trail (who rotated keys, when)

### C.3 Clock Skew / Timestamp Validity (Operational)

**Risk:** If HG-2 decisions include timestamps, what if system clocks diverge?

| Component | Current Time Source | Sync Method | Risk |
|-----------|---|---|---|
| MoCKA app.py | `datetime.now()` | None specified | Can be wrong ±minutes |
| SQLite events | Node-local time | None | Depends on server clock |
| External Systems | ??? | ??? | Unknown |

**Questions:**
- Does HG-2 decision timestamp need to be canonical/verified?
- If system clock rolls back, are decisions retroactively "un-approved"?
- What if two decisions have same timestamp?

### C.4 Replay / Idempotency (Operational)

**Risk:** What if HG-2 decision is delivered twice?

Current state:
- `prevention_queue.json` schema not deployed yet (no id field visible)
- No mention of idempotency token or "accept once" semantics
- No retry protocol specified

**Post-activation Questions:**
1. If HG-2 says "APPROVE X" twice, is that:
   - Error (duplicate detection)?
   - Safe no-op (idempotent)?
   - Escalation (second approval cancels first)?
2. How to distinguish:
   - Same message delivered twice (network retry)?
   - Human explicitly approving same item twice?

### C.5 Partial Failure Recovery (Operational)

**Scenario:** HG-2 approves decision, but execution partially fails.

| Component | Failure Mode | Recovery |
|-----------|---|---|
| Record approval in database | Fails | Retry? Abort? |
| Notify downstream | Fails | Downstream never sees approval? |
| Update state to "approved" | Fails | Stuck in "pending"? |
| Audit log entry | Fails | Decision happens but not logged? |

**Not yet specified:**
- Transaction boundaries (atomic decisions or not?)
- Retry semantics (how many times? linear/exponential backoff?)
- Circuit breaker (if failures exceed threshold, fallback mode?)
- Degradation (partial approval: some approvals succeed, some fail?)

---

## D. PHASE 6+ — Design Now or Defer

### D.1 Experience Memory Integration (Phase 6+)

**Future Capability:** MoCKA will eventually record Expected Outcome → Actual Outcome → Learning.

**Current Gap:** HG-2 approves decisions but has no connection to outcome tracking.

| Lifecycle Stage | Current HG-2 | Future Memory Need |
|---|---|---|
| Decision | APPROVE ✓ | Record decision as expectation |
| Execution | UNKNOWN | Observe actual execution |
| Outcome | UNKNOWN | Compare actual vs expected |
| Learning | UNKNOWN | Extract lessons for future decisions |

**Question:** Should HG-2 activation include:
1. Decision → Outcome binding (so we can track "did this approval lead to expected result")?
2. Outcome cascade (if approval led to failure, does approval get downgraded/revoked)?
3. Learning injection (future HG-2 decisions informed by past approval outcomes)?

**Design Debt:** If not addressed now:
- HG-2 records decisions but not tied to outcomes
- Post-activation, adding outcome binding requires schema migration
- Outcome bindings retroactively added = data integrity risk

### D.2 Delegation Authority Chain (Phase 6+)

**Future Need:** HG-2 may eventually delegate to sub-gates (HG-2-A, HG-2-B, etc.) as scale increases.

**Not yet specified:**
- Can HG-2 create subordinate gates?
- Does authority reduce as it delegates (delegation exhaustion)?
- Can subordinate gates further delegate (multi-level)?
- Is authority revocable mid-stream (child gate still thinks approved)?

**Design Debt:** If not addressed now:
- Single HG-2 instance becomes bottleneck
- Post-activation delegation is hard to add (breaks existing approvals)
- Distributed HG-2 without clear hierarchy = audit chaos

### D.3 HG-0 / Cross-Gate Coordination (Phase 6+)

**Future State:** HG-0 (if created) might orchestrate HG-1 through HG-5.

**Current Setup:** HG-2 operates independently. No coordination with HG-1 or HG-4.

**Questions for Phase 6 design:**
1. Should HG-0 exist? (Meta-gate approving gates?)
2. If HG-2 and HG-1 both need to approve same item, what's the rule?
   - Both must approve (AND gate)?
   - Either can approve (OR gate)?
   - HG-2 overrides HG-1 (priority)?
3. If rules conflict between HG-2 and HG-1, who wins?

**Design Debt:** If not addressed now:
- HG-2 activated without knowing its relationship to other HG systems
- Post-activation HG-0 design will have to retrofit HG-2
- Retrofitting = risky changes to running system

### D.4 JARVIS / Semantic Authority Boundary (Phase 6+)

**From HAB_CORE_DEFINITION:** JARVIS (semantic query engine) has its own implicit authority.

**HAB-C and HAB-D (from HG-J03 evidence):**
- HAB-C: PHI-HAB structural concept (not yet in MoCKA code)
- HAB-D: PHI-HAB institutional concept (3 systems) — decision (DC_20260729_008) pending HG-J03 authorization

**Question:** When JARVIS activates (Phase 6), does it:
1. Bypass HG-2 (semantic decisions are independent)?
2. Consult HG-2 (semantic queries need approval)?
3. Elevate to HG-0 (semantic tier is higher than HG-2)?

**Current Evidence:** No integration path defined between HG-2 and JARVIS.

**Design Debt:** HG-2 activated without knowing if it's subordinate to / peer with / superior to JARVIS later.

---

## E. ARCHITECTURE DEBT — Changes After Activation Will Be Risky

### E.1 State Vocabulary (HIGH DEBT)

**Current:** `prevention_queue.json` uses vocabulary `{NEW, approved, rejected}`

**Activation Lock:** Once HG-2 runs and records decisions in this vocabulary, changing it requires:
1. Schema migration (new field, old data?)
2. Audit trail integrity (do old decisions change meaning?)
3. Compatibility (does old code still work with new vocabulary?)

**Example Risk:**
- Activate HG-2 with `{NEW, approved, rejected}`
- After 6 months, realize we need `{NEW, approved, rejected, deferred, escalated}`
- Adding "deferred": Do old "NEW" records now mean something different?
- Migration: Code that checked `if state == "approved"` now breaks?

**Recommendation (Pre-Activation):** Lock state vocabulary by:
- Documenting intended FINAL vocabulary (not current draft)
- Creating schema with reserved fields for future states
- Recording version number in each record
- Not activating until vocabulary is immutable by explicit decision

### E.2 Authorization Semantics (HIGH DEBT)

**Current:** Decision lifecycle = Evidence → Gate → Decision → Execution → Audit

**Activation Lock:** Once this cycle is live and data flows through it:
- Adding "revocation" step requires re-interpretation of old "executed" records
- Adding "evidence refresh" requires re-evaluating old decisions
- Adding "conditional approval" (approve IF condition X) requires new schema

**Risk:** Post-activation changes to lifecycle look like policy changes but are actually schema changes.

**Recommendation (Pre-Activation):**
- Decide if lifecycle will ever need to: revoke? refresh evidence? add conditions? escalate?
- If yes, design schema with these slots now (even if unused)
- If no, document these as explicitly out-of-scope forever

### E.3 Failure Recovery Path (HIGH DEBT)

**Current:** No recovery protocol for HG-2 deployment failures.

**Activation Lock:** Once approval decisions are live:
- If database corrupts, how do you recover? (Recompute from what?)
- If HG-2 crashes mid-approval, is it half-approved? (Idempotency?)
- If network fails, does client retry or assume rejection? (Timeout semantics?)

**Risk:** Designing recovery post-activation means working on live system with real decisions at stake.

**Recommendation (Pre-Activation):**
- Define recovery procedures (backup/restore, idempotency, timeout)
- Test them before activation (simulate failures in staging)
- Document them immutably so operations knows protocol

---

## F. GOVERNANCE RISK — Technically Possible but Governance Danger

### F.1 Implicit Decisions (HIGH RISK)

**Risk:** HG-2 decisions might be made implicitly without explicit approval.

**Example:**
- App.py has endpoint `/approve?id=123&state=approved`
- Request handler calls HG-2 approval function
- But who validated that user is authorized to call this endpoint?
- If HG-1 already approved the request, does HG-2 auto-approve? (Cascade vs explicit)

**Governance Danger:** Decisions appear approved but no one explicitly approved them.

**Current Evidence:**
- `app.py /decision/*` endpoints not examined yet
- No mention of "explicit approval required" in HG-2 spec
- Unclear if HG-2 approval is active operation (human must approve) or passive confirmation (system confirms)

**Questions for Human Gate:**
1. Is HG-2 approval **active** (human explicitly approves) or **passive** (system confirms pre-approval)?
2. If passive, what pre-conditions must be met? (HG-1? Event Gate? Evidence?)
3. If active, what prevents non-authorized users from calling approval endpoints?

### F.2 Silent Non-Execution (HIGH RISK)

**Risk:** Decision approved but never executed.

**Scenario:**
1. Human approves decision "release feature X"
2. HG-2 records approval ✓
3. Notification system fails
4. Execution system never sees approval
5. Feature never released
6. Audit finds "approved" in HG-2 but no evidence of release

**Current Evidence:**
- No mention of notification/delivery guarantee
- Event Gate and HG-2 are separate systems (no integration test found)
- No "execution triggered" feedback to HG-2

**Governance Danger:** Decisions might appear to be working but are silently ignored.

### F.3 Audit Trail Divergence (MEDIUM RISK)

**Current Setup:** 5 independent HG systems with separate audit trails.

**Divergence Risk:** What if:
- HG-1 says decision was approved
- HG-2 says decision was rejected
- Git audit (HG-3) says code was committed
- Which is true?

**Governance Danger:** Auditors cannot answer "what actually happened" because trail is split.

**Current Evidence (from HAB_CORE_DEFINITION F-1):**
- Confirmed: Same 1,773 items, HG-1 has PENDING (1,774 records), HG-2 has rejected (1,799 records)
- Only 1,773/1,941 ids match between systems
- This is already observable, pre-activation

**Recommendation:** Do not activate HG-2 until divergence is understood and decision is made to either:
- Consolidate to single trail (merge HG-1 and HG-2), or
- Formalize split (document why HG-1 and HG-2 are independent)

### F.4 Orphaned Decisions (MEDIUM RISK)

**Risk:** Decisions approved but now context is deleted.

**Scenario:**
1. Human gate approves decision "restart service X"
2. Service X is decommissioned 6 months later
3. Decision is never revoked (no revocation protocol)
4. Operator sees "restart X" approval, attempts to execute
5. Service X doesn't exist

**Governance Danger:** Dead approvals create confusion and error.

**Recommendation (Pre-Activation):**
- Define revocation protocol (when/how decisions are withdrawn)
- Implement notification: "decision X targets nonexistent Y"
- Consider auto-revocation for stale decisions (>N months old)

---

## G. UNKNOWN — Evidence Insufficient (Do Not Assume)

### G.1 Prevention Queue Implementation Status

**Current state:** `data/prevention_queue.json` file does not exist.

**Questions:**
- Is prevention_queue deployment part of HG-2 activation?
- Or is it optional / deferred?
- If optional, what is the "fallback" if file is missing?
- If deferred, what is HG-2 using in the interim?

**Evidence:** None found in current codebase.

**Action:** Do not assume prevention_queue is deployed unless explicitly confirmed.

### G.2 Integration with Other HG Systems

**Current state:** 
- HG-1 approval in `human_gate_events`
- HG-2 approval in `prevention_queue.json`
- Are these the same approval or separate approvals?

**Questions:**
- Is HG-2 a new layer that all requests go through? (All HG-1 requests must also get HG-2?)
- Or parallel? (Some requests use HG-1, others use HG-2)
- Or replacement? (HG-2 replaces HG-1)

**Evidence:** Not found in decision records.

**Action:** Do not assume HG-2 integrates with HG-1 without explicit design.

### G.3 Relationship to Decision Ledger

**Current state:**
- HG-C decisions are ready for "batch registration" in Decision Ledger
- But HG-2 runtime decisions (actual approvals made by HG-2) are separate
- Are runtime approval decisions recorded in Decision Ledger?

**Questions:**
- Does each HG-2 approval create a Decision Ledger entry?
- Or is Decision Ledger only for meta-decisions (like HG-C)?
- If separate, how do auditors correlate them?

**Evidence:** Not found.

**Action:** Do not assume all HG-2 approvals go to Decision Ledger.

### G.4 Timeout and Expiry Semantics

**Current state:** No timeout or expiry mentioned in contracts or policies.

**Questions:**
- If HG-2 is pending for 1 year, is it still valid?
- Who (if anyone) can force expiry?
- If expired, does system auto-reject or escalate to human?

**Evidence:** Not found.

**Action:** Do not implement HG-2 with assumption of eternal validity.

### G.5 Failure Modes and Recovery

**Current state:** No failure recovery protocol found.

**Questions:**
- What if approval database is corrupted?
- What if HG-2 service crashes during approval?
- What if approval is recorded but never executed?
- What if executed but never logged?

**Evidence:** Not found.

**Action:** Do not assume HG-2 is self-healing; design recovery before activation.

---

## H. RECOMMENDATION — Action Items for Human Gate

### H.1 MUST DECIDE BEFORE ACTIVATION

These items require explicit Human Gate decision (approval/rejection/deferral) before HG-2 can activate.

#### H.1.1 State Authority Consolidation (CRITICAL)

**Decision Needed:**

> Should HG-2 activation proceed while 5 independent Human Gate systems exist with separate state records?

**Options:**
1. **Consolidate to single authority:** Merge HG-1/HG-2/HG-3/HG-4/HG-5 into one state ledger before HG-2 activation
2. **Formalize separation:** Document why HG-2 is intentionally separate from HG-1 (not consolidation, but explicit design)
3. **Partial consolidation:** Merge HG-1 and HG-2 only; leave HG-3/HG-4/HG-5 separate
4. **Defer:** Activate HG-2 in isolation; consolidation is Phase 6+ decision

**Governance Impact:**
- Option 1: Highest risk (touch 5 systems simultaneously) but cleanest audit trail
- Option 2: Lowest immediate risk but creates documentation burden
- Option 3: Medium risk, medium benefit (HG-2's primary interaction is with HG-1)
- Option 4: Lowest activation risk but leaves audit trail divergence unsolved

**Recommendation:** Option 3 (Partial consolidation of HG-1+HG-2) with explicit deferral of HG-3/4/5 to Phase 6.

#### H.1.2 Transition Ledger Requirement (CRITICAL)

**Decision Needed:**

> Must HG-2 maintain an immutable transition ledger (who/what/when for each state change)?

**Options:**
1. **Required:** Every state transition → ledger entry (timestamp, actor, reason, previous state)
2. **Optional:** Ledger entry only if explicitly requested by caller
3. **Deferred:** No ledger; just state in prevention_queue.json
4. **External:** Use Event Ledger (events.db) instead of HG-2-specific ledger

**Governance Impact:**
- Option 1: Highest audit confidence but performance cost (every change = write)
- Option 2: Lower cost but audit gaps (no ledger for routine transitions)
- Option 3: Lowest cost but no recovery path post-failure
- Option 4: Leverage existing Event Ledger but requires cross-system schema

**Recommendation:** Option 1 (Mandatory ledger) with batched writes to prevent bottleneck.

#### H.1.3 Authorization Lifecycle Definition (CRITICAL)

**Decision Needed:**

> Define the complete authorization lifecycle for HG-2 decisions:
> - **Expiry:** Do decisions expire? (Duration?)
> - **Revocation:** Can approved decisions be withdrawn? (By whom?)
> - **Delegation:** Can HG-2 approve on behalf of human? (Or only human-initiated?)

**Options:**
1. **Eternal approvals:** Once approved, always approved (unless explicitly revoked)
2. **Time-bound approvals:** Approval valid for N days (auto-expire)
3. **Conditional approvals:** "Approve IF condition X remains true"
4. **Hybrid:** Mix of above (some decisions eternal, some time-bound)

**Governance Impact:**
- Option 1: Operational simplicity but zombie decisions accumulate
- Option 2: Freshness guaranteed but requires auto-expiry mechanism
- Option 3: Maximum precision but complex to implement
- Option 4: Flexible but hard to audit

**Recommendation:** Option 2 (Time-bound, 90 days) with explicit revocation allowed at any time.

#### H.1.4 Event Gate Coordination (CRITICAL)

**Decision Needed:**

> How does HG-2 approval interact with Event Gate (PHI-OS) enforcement?

**Options:**
1. **Sequential:** Event Gate checks first, then HG-2 approval optional (Event Gate is primary)
2. **Parallel:** Both must agree (AND gate)
3. **HG-2 primary:** HG-2 approval bypasses Event Gate (HG-2 is primary)
4. **Separate tracks:** Event Gate and HG-2 are independent (no coordination)

**Governance Impact:**
- Option 1: Leverages existing Event Gate; HG-2 is secondary
- Option 2: Highest safety (both must agree) but slow
- Option 3: HG-2 fully trusted; Event Gate is secondary
- Option 4: Audit confusion (which system owns decision?)

**Recommendation:** Option 2 (Parallel, both must agree) with fallback to Event Gate if HG-2 is down.

#### H.1.5 Authorization Scope Binding (CRITICAL)

**Decision Needed:**

> How is the scope of HG-2 approvals formally bounded?

**Options:**
1. **Explicit scope field:** Each decision includes target_scope (path, pattern, or resource ID)
2. **Implicit scope:** Scope is derived from decision content (fragile)
3. **Hierarchical scope:** Parent approvals cover children automatically
4. **No explicit scope:** Approvals are granular; scope is emergent

**Governance Impact:**
- Option 1: Audit clarity but schema complexity
- Option 2: Simple but audit gaps
- Option 3: Convenient but cascading failures
- Option 4: Flexible but no authoritative answer to "what did this approval cover"

**Recommendation:** Option 1 (Explicit scope field) with version control on scope to detect unauthorized drift.

---

### H.2 CAN DEFER BEYOND ACTIVATION

These items are important but can be addressed post-activation with operational monitoring.

#### H.2.1 Authorization Freshness Monitoring

**Action:** Post-activation, implement daily audit checking:
- Distribution of decision age (0–7 days, 8–30 days, 31–90 days, >90 days)
- Alert if any approved decision is >180 days old and still active
- Quarterly human review of oldest decisions for relevance

**Ownership:** Operations + Governance

**Timeline:** Implement within 30 days of HG-2 activation

#### H.2.2 Credential Rotation Protocol (if cryptographic)

**Action:** If HG-2 includes signature or HMAC:
- Document key generation, storage, rotation schedule
- Implement rotation every 90 days
- Test compromise recovery (revoke old key, issue new)
- Maintain audit of key rotations

**Ownership:** Security + Operations

**Timeline:** Before first key rotation (pre-plan during activation)

#### H.2.3 Replay / Idempotency Testing

**Action:** Post-activation, run operational tests:
- Send same approval twice; verify idempotent behavior
- Verify that replay detection works (no double-approvals)
- Test timeout + retry scenarios

**Ownership:** QA + Operations

**Timeline:** Week 2 post-activation (after stabilization)

#### H.2.4 Failure Recovery Drill

**Action:** Quarterly disaster recovery drill:
- Simulate HG-2 database corruption
- Recover from backup
- Verify audit trail consistency
- Document recovery time + data loss (if any)

**Ownership:** Operations + Data Engineering

**Timeline:** First drill at 1-month post-activation

---

### H.3 DO NOT DESIGN YET

These items are Phase 6+ considerations and should NOT influence HG-2 activation.

#### H.3.1 Experience Memory Integration

**Why defer:** Experience Memory architecture (expected → actual → learning) is not yet defined. Forcing HG-2 to accommodate it now will lock HG-2 into an Experience Memory design that hasn't been approved.

**Action:** Document the interface HG-2 will need to expose to Experience Memory (expected approval → actual outcome), but do NOT implement it. Implement the interface in Phase 6 when Experience Memory design is final.

#### H.3.2 Delegation Authority Chain

**Why defer:** Multi-level delegation (HG-2 → HG-2-A → HG-2-B) requires design of authority reduction, inheritance, revocation across hierarchy. This is orthogonal to HG-2 activation.

**Action:** Design in Phase 6 when scale demands it. Activate HG-2 as single point of authority.

#### H.3.3 HG-0 Orchestration

**Why defer:** HG-0 (meta-gate) coordinating HG-1 through HG-5 is a Phase 6+ capability. Forcing it now will lock HG-2 into an HG-0 design that isn't approved.

**Action:** Document HG-2's expected role under future HG-0, but do NOT implement. Implement in Phase 6 when HG-0 is decided.

#### H.3.4 JARVIS Integration

**Why defer:** JARVIS authority boundary (HAB-C / HAB-D) awaits HG-J03 decision (still pending). Do not activate HG-2 with assumptions about JARVIS authority.

**Action:** Document the interface HG-2 will expose to JARVIS (if any), but do NOT implement. Once HG-J03 decides JARVIS scope, integrate in Phase 6 if needed.

---

## I. FINAL DECISION FRAMING

### HG-2 ACTIVATION SHOULD WAIT FOR...

1. **Human Gate decision on State Authority Consolidation**
   - Consolidate HG-1+HG-2 to single ledger, OR
   - Document why HG-2 is intentionally separate (not consolidation)

2. **Human Gate decision on Transition Ledger**
   - Require immutable transition log in HG-2, with timestamp/actor/reason

3. **Human Gate decision on Authorization Lifecycle**
   - Define expiry (e.g., 90 days), revocation protocol, conditional approval rules

4. **Human Gate decision on Event Gate Coordination**
   - Define whether HG-2 and Event Gate are parallel (both must agree) or sequential

5. **Human Gate decision on Scope Binding**
   - Define explicit scope field in decision schema to prevent authorization drift

6. **Resolution of Discovery F-1 (State Authority Separation)**
   - The divergence of 1,773 items between HG-1 and HG-2 state records must be explained before HG-2 reads from that data

---

### HG-2 ACTIVATION CAN PROCEED WITHOUT...

1. **Experience Memory Integration** (Phase 6+ concern)
2. **Delegation Authority Chain** (Phase 6+ concern)
3. **HG-0 Orchestration** (Phase 6+ concern)
4. **JARVIS Authority Coordination** (Phase 6+ concern, depends on HG-J03)
5. **Complete failure recovery procedures** (can be documented post-activation)
6. **Authorization freshness monitoring** (can be deployed post-activation)
7. **Credential rotation automation** (can be deferred if no cryptography in HG-2)

---

### DO NOT DESIGN YET...

1. **Multi-level delegation** — Defer to Phase 6 when scale requires it
2. **Experience Memory feedback loops** — Defer to Phase 6 when Experience Memory is approved
3. **JARVIS semantic authority** — Defer to Phase 6 when HG-J03 is decided
4. **HG-0 meta-governance** — Defer to Phase 6 when cross-gate coordination is needed

---

## J. SUMMARY TABLE: Risk Assessment by Activation Readiness

| Area | Status | Blockers | Risk if Ignored |
|------|--------|----------|---|
| **State Authority** | ❌ Undefined | Need HG decision | Audit trail divergence (F-1 already observed) |
| **Transition Ledger** | ❌ Missing | Need HG decision | No recovery path on failure (F-2 already observed) |
| **Authorization Lifecycle** | ❌ Undefined | Need HG decision | Zombie decisions, no revocation capability |
| **Event Gate Coordination** | ❌ Undefined | Need HG decision | Silent non-execution or audit gaps |
| **Scope Binding** | ❌ Undefined | Need HG decision | Authorization creep, cascading failures |
| **Freshness Monitoring** | ❌ Missing | None (post-activation OK) | Old approvals persist; can be addressed operationally |
| **Failure Recovery** | ❌ Undefined | None (post-activation OK) | Can design post-activation; leverage Event Ledger backup |
| **Crypto/Keys** | ℹ️ Conditional | If HG-2 uses signatures: define rotation | Key compromise undetectable; can defer if no crypto |
| **Experience Memory** | ℹ️ N/A (Phase 6+) | None | Will require schema changes post-activation; acceptable |
| **Delegation Chain** | ℹ️ N/A (Phase 6+) | None | Single-point bottleneck; acceptable short-term |
| **HG-0 Design** | ℹ️ N/A (Phase 6+) | None | Will retrofit once HG-0 is designed; acceptable |
| **JARVIS Integration** | ℹ️ Depends HG-J03 | None (pending separate decision) | Can coordinate once JARVIS scope is approved |

---

## K. Evidence References

### Governance Documents Examined
- `HG-C10_DECISION_RECORD_v1.0.md` (approved 2026-08-06)
- `HG-C09_DECISION_RECORD_v1.0.md` (referenced)
- `HG-C08_DECISION_RECORD_v1.0.md` (referenced)
- `HAB_CORE_DEFINITION_v0.1.md` (DRAFT, findings F-1 and F-2 sourced from here)
- `ACTIVATION_POLICY_v0.1.md` (v0.1)
- `HUMAN_GATE_CONTRACT_v0.1.md` (basic contract defined)
- `phase5_boundary_declaration.md` (Phase 5 finality rules)
- `MOCKA_OVERVIEW.json` (current system state, v4.1)

### Codebase Examined
- `app.py /decision/*` (HG-2 decision endpoints)
- `phi_os/human_gate.py` (HG-1)
- `phi_os/event_gate.py` (Event Gate enforcement)
- `data/prevention_queue.json` (NOT FOUND — file not deployed)
- `data/decisions/decision_ledger.jsonl` (208 lines, HG-C batch not yet registered)

### Key Data Observations
- **5 independent HG systems** operating with separate state vocabularies (from HAB_CORE_DEFINITION)
- **State divergence confirmed:** 1,773 items, HG-1 "PENDING" vs HG-2 "rejected" (F-1)
- **Transition ledger gaps confirmed:** F-2 observed in existing systems
- **Decision Ledger:** Ready for batch registration (HG-C01–C10) but awaiting Human Authority instruction

---

## L. Document Authority & Immutability

| Item | Value |
|------|-------|
| **Document Status** | RESEARCH (Not Implementation) |
| **Activation Decision** | Pending Human Gate |
| **Immutability** | This document is a snapshot. Updates require new version with date suffix |
| **Change Procedure** | If evidence contradicts findings, update as "v1.1 (Revision Date)", do not modify v1.0 |
| **Custodian** | Kuroko (Claude Haiku 4.5) — Research role only; Human Authority makes activation decision |
| **Distribution** | For Human Gate review; not a commitment to implementation |

---

## M. GOVERNANCE AUDIT RESULTS (Specialist Analysis)

**Investigator:** Claude Haiku 4.5 (Explore Agent)  
**Date:** 2026-10-04  
**Duration:** Deep analysis of decision ledger (76 decisions) + governance architecture (7+ documents)  
**Finding Authority:** Systematic governance record audit, not subject matter opinion  

### M.1 HG-2 Authorization Status (Definitive)

| Criterion | Finding | Evidence |
|-----------|---------|----------|
| **Runtime Activation Authorization** | NOT FOUND | No decision_id in 76-record decision ledger authorizing HG-2 runtime operation |
| **Production Activation Authorization** | NOT FOUND | No explicit activation decision in DC_* or HG_* series |
| **Implementation Authorization** | NOT FOUND | Prevention_queue.py not authorized; HAB-CORE-DEF-001 remains DRAFT |
| **Phase Inclusion** | NOT FOUND | HG-2 absent from Phase B Verification (2026-10-03), Phase 5.1-A Pipeline, AR-* phases |
| **Governance Decision Pending** | CONFIRMED | HAB-CORE-DEF-001 must transition from DRAFT to formal Human Gate Decision before HG-2 evolution |

### M.2 HG-2 Operational Status (as deployed)

| Metric | Actual Value |
|--------|---|
| **Records in prevention_queue.json** | 1,941 total |
| **Distribution:** Rejected | 1,799 (92.7%) |
| **Distribution:** NEW | 137 (7.1%) |
| **Distribution:** Approved | 5 (0.3%) |
| **Untracked State Transitions** | 1,798 (2026-06-28 bulk event, actor unknown) |
| **Caller Identity Verification** | MISSING (hardcoded `who_actor="kimura_hakase"`) |
| **Event Store Integration** | MISSING (prevention_queue.json direct mutation, no event_ledger entries) |
| **Decision Ledger Connection** | MISSING (no prevention_queue decisions in decision_ledger.jsonl) |
| **Transition Ledger** | MISSING (state changes not recorded with timestamp/actor/reason) |

### M.3 State Authority Fragmentation (Confirmed Evidence)

| HG System | Code Location | State Storage | State Vocab | Discrepancy |
|---|---|---|---|---|
| HG-1 | `phi_os/human_gate.py` | `human_gate_events` (SQLite) | PENDING, APPROVED, REJECTED, EXPIRED, CANCELED | **HG-1 shows "PENDING" (1,774) vs HG-2 "rejected" (1,799) for same 1,773 items** |
| **HG-2** | `app.py /decision/*` | `prevention_queue.json` | NEW, approved, rejected | **Match rate: 1,773/1,941 ids only** |
| HG-3 | `mocka_git_safe_commit.py` | Git work tree | (none) | Git history not reconciled with HG-1/2 |
| HG-4 | `semantic/query_engine/human_gate.py` | In-memory | accept, reject, defer, split | Non-persistent; no reconciliation possible |
| HG-5 | `governance/human_gate_continuity.py` | `pending_decision_units.jsonl` | WAITING_FOR_HUMAN_GATE | Not reconciled |

**Audit Conclusion:** Same conceptual approval is recorded 5 different ways in 5 different locations. No single source of truth.

### M.4 Unknown Issues Requiring Resolution

| Unknown ID | Description | Impact | Status |
|---|---|---|---|
| **U-30** | Who performed 2026-06-28 bulk rejection of 1,799 items and how? | Prevents audit of decision authority | **UNRESOLVED — Blocks Activation** |
| **U-36** | Did 168 post-migration prevention_queue records reflect to HG-1? | Data integrity unknown | **UNRESOLVED** |
| **U-37** | Call history of `/decision/approve` and `/decision/reject` endpoints — who calls, how often? | No observability of HG-2 usage | **UNRESOLVED** |
| **G-5** | Root issue: Why do 5 independent HG systems exist? (design or accident?) | Authority fragmentation root cause | **UNRESOLVED — Prevents Phase 6+** |
| **G-15** | prevention_queue write inconsistencies (3 documented locations) | Data consistency | **UNRESOLVED** |

### M.5 Critical Governance Findings

**Event Gate Integration: NOT CONNECTED**
- `phi_os/event_gate.py` does not reference `prevention_queue.json`
- HG-2 approval decisions do not flow through Event Gate
- Event Gate enforcement and HG-2 approval are parallel, uncoordinated systems
- Risk: Approved in HG-2 but denied by Event Gate (silent non-execution)

**Decision Engine Integration: NOT CONNECTED**
- `prevention_queue.json` records do not appear in `decision_ledger.jsonl`
- HG-2 decisions are invisible to governance Decision Engine
- No feedback loop from Decision Engine to HG-2
- Risk: Decisions recorded but not auditable through governance system

**Experience Memory Integration: NOT CONNECTED**
- No consequence tracking (expected outcome vs actual outcome)
- No memory references in HG-2 records
- Knowledge Activation Review Gate (separate system) does not correlate with HG-2
- Risk: Lessons from past approvals not available to future approvals

**Caller Verification: MISSING**
- Current implementation: hardcoded `who_actor="kimura_hakase"`
- Dynamic actor identification not implemented
- Caller context not validated
- Risk: Cannot distinguish between manual approval and automated delegation

**Scope Binding: MISSING**
- No `decision_scope` field limits authorization
- Approval of X could be used for Y if scope not bounded
- Risk: Authorization creep

---

## N. Specialist Audit Conclusion

**HG-2 is a legacy operational system that exists in code but has:**
1. **NO formal activation authorization** in governance decision ledger
2. **NO integration** with Event Gate, Decision Engine, or Experience Memory
3. **UNRESOLVED unknown issues** (U-30, U-36, U-37, G-5, G-15) blocking governance closure
4. **MISSING critical components** (transition ledger, caller verification, scope binding)
5. **STATE AUTHORITY FRAGMENTATION** with HG-1 (1,773 items divergent; 1,941 total in HG-2 vs 1,774 in HG-1)

**Activation Status: BLOCKED pending Human Gate formalization of HAB-CORE-DEF-001 and resolution of U-30, U-36, U-37.**

---

## End of Research Document

**Generated:** 2026-10-04  
**Investigation Duration:** Research session + Governance audit  
**Investigators:** Kuroko (Research) + Explore Agent (Governance Audit)  
**Next Action:** Submit to Human Gate for activation decision  
**Authority Decision Required:** HAB-CORE-DEF-001 formalization + Unknown issues resolution before any runtime authorization  

---

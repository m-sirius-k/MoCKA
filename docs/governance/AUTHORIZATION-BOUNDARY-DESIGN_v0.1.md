# Authorization Boundary Design Specification v0.1

**Phase**: Remediation Design Specification (Post-Investigation)
**Date**: 2026-09-11
**Purpose**: Design (specification only, NOT implementation) of Authorization Boundary
**System State**: HOLD / FAIL-CLOSED (maintained)

---

## Overview

This specification designs:
- Authority boundaries (who can decide what)
- Authorization decision-making process
- Runtime enforcement of decisions
- Evidence binding to authorization
- Bypass prevention mechanisms
- Fail-closed behavior on authorization failure
- UNKNOWN / NOT_PROVEN handling

**EXPLICIT SCOPE LIMIT**: Design Specification ONLY. No implementation, no code changes, no enforcement mechanism implementation.

**SCOPE EXCLUSION**:
- NOT: Writing enforcement code
- NOT: Modifying authorization checks in runtime
- NOT: Creating new authorization classes or roles
- NOT: Implementing authorization gates or filters
- NOT: Modifying existing authorization decisions
- NOT: Creating new authorization decisions

---

## Part 1: Authority Boundary Definition

### Core Authority Concept

**Authority**: Right to make binding decisions that affect system state and resource access.

**Distinct from Capability**:
- Capability: Technical ability to perform action (e.g., "I can call API endpoint")
- Authority: Permission to decide whether action should proceed (e.g., "I can authorize API endpoint call")
- CRITICAL: Capability != Authority. Having ability does NOT grant right to decide.

### Authority Hierarchy

**Level 1: System-Level Authority (Highest)**
```
Holder: きむら博士 (Human Gate Authority)

Authority Rights:
  - Final decision on implementation authorization
  - Go / No-Go decisions for system changes
  - Authority to make meta-decisions (deciding who decides what)
  - Escalation resolution (breaks ties, handles conflicts)
  - Authorization for other authorities (delegation)

Authority Scope:
  - All critical decisions
  - All authorization boundary changes
  - All governance policy changes

Evidence Requirement:
  - All Level 1 decisions recorded in Decision Ledger
  - All decisions tracked in Event Store
  - Rationale documented for audit
```

**Level 2: Component-Level Authority (Decision Point)**
```
Examples:
  - HG API Decisions (authorization to write decisions)
  - Event Creation Decisions (authorization to create events)
  - Evidence Binding Decisions (authorization to link evidence)
  - State Transition Decisions (authorization to change system state)

For Each Component Decision:
  - Who has authority: specified in decision
  - What conditions must be met: specified in decision
  - What evidence required: specified in decision
  - Escalation path: if conditions not met → escalate to Level 1
```

**Level 3: Operational Authority (Implementation)**
```
Examples:
  - Implementers execute approved decisions
  - DevOps operates approved systems
  - Auditors verify approved state
  - Incident responders follow approved procedures

Constraint:
  - Level 3 authority: Implementation ONLY
  - Cannot make decisions (that's Level 1/2)
  - Cannot bypass decisions (that's Level 1)
  - Must follow decision requirements exactly
```

### Authority Delegation Model

**Authorization Chain for Decision**:
```
きむら博士 (Level 1)
  │
  ├─ Delegates: "Component A authorization" to [Person/Role]
  │  └─ Evidence: Decision Ledger record DC_YYYYMMDD_NNN
  │
  └─ Restriction: Delegated authority can only decide within scope
     (cannot expand own authority, cannot re-delegate)
```

**No Re-Delegation**:
- Level 1 → Level 2: allowed (with scope restriction)
- Level 2 → Level 3: not delegation, just instruction (Level 2 retains authority)
- Level 2 → Level 2: NOT allowed (no re-delegation)

---

## Part 2: Authorization Decision-Making Process

### Standard Decision Flow

**For any decision that affects system state or authorization**:

```
1. REQUEST PHASE
   ├─ Initiator proposes decision
   ├─ Proposer provides: alternatives, rationale, evidence
   └─ Evidence level: what documentation supports each alternative

2. AUTHORITY REVIEW PHASE
   ├─ Determine: who has authority to decide?
   ├─ Check: does authority holder have required evidence?
   ├─ Check: are conditions for authority met?
   └─ Options:
      a. Authority found and conditions met → proceed to DECISION PHASE
      b. Authority unclear / conditions not met → ESCALATION PHASE

3. ESCALATION PHASE (if needed)
   ├─ Move decision to next higher level
   ├─ Provide: all prior analysis + missing evidence
   ├─ Level N-1 decides: authorize or reject or return for more evidence

4. DECISION PHASE
   ├─ Authority makes decision
   ├─ Decision recorded: alternatives considered + rationale + decision
   ├─ Record in Decision Ledger (mocka_decision_write)
   ├─ Create companion Event in Event Store
   └─ Generate decision_id for tracking

5. EXECUTION PHASE
   ├─ Approved decision communicated to implementers
   ├─ Implementers execute within scope
   ├─ Implementers verify execution completes
   ├─ Audit trail recorded for all actions
   └─ If execution fails: escalate back to authority

6. VERIFICATION PHASE
   ├─ Auditors verify decision was executed correctly
   ├─ Auditors verify no scope creep occurred
   ├─ Auditors verify no unauthorized changes happened
   └─ Results recorded in Event Store
```

### Evidence Requirements by Decision Type

**Type A: Technical Design Decision**
```
Required Evidence:
  - Problem statement (what issue is being solved)
  - Analysis of alternatives (why not others)
  - Technical rationale (why this approach)
  - Risk assessment (what could go wrong)
  - Evidence sources (references, data, measurements)

Authority Level:
  - Component authority (Level 2) if within scope
  - System authority (Level 1) if cross-cutting or critical

Example: "Authorization of HG API redesign to implement fail-closed atomicity"
```

**Type B: Role / Authority Definition**
```
Required Evidence:
  - Role responsibilities (what decisions this role makes)
  - Authority scope (what areas can this role decide)
  - Conflict resolution (what if multiple roles disagree)
  - Escalation path (where does role escalate)
  - Term (is this permanent or temporary)

Authority Level:
  - ALWAYS Level 1 (System Authority)
  - きむら博士 must approve all role definitions

Example: "Authorization of R01 Auditor role with audit-only authority"
```

**Type C: Operational Procedure**
```
Required Evidence:
  - Procedure description (step-by-step)
  - Conditions for use (when to execute)
  - Escalation triggers (when to stop and escalate)
  - Success criteria (how to verify complete)
  - Rollback procedure (how to undo if needed)

Authority Level:
  - Component authority (Level 2) if within component scope
  - May be delegated to Level 3 for execution (but not decision-making)

Example: "Authorization of incident response procedure for GATE timeout"
```

---

## Part 3: Authorization Boundary Enforcement (Design)

### Enforcement Points (Where Authorization Must Be Checked)

**Enforcement Point 1: API Request Arrival**
```
Location: mocka_decision_write entry point

Check:
  a. Is caller authenticated?
  b. Is caller authorized to make decisions? (role check)
  c. Does caller have authority for decision type?
  d. Are required evidence fields present?

If Check Fails:
  - Fail-closed: Return error, do NOT write decision
  - Escalate: Log to Event Store as "AUTHORIZATION_FAILED"
  - Alert: Notify security if unauthorized caller detected

Expected Response on Success:
  - Authority confirmed: proceed to decision processing
  - Evidence verified: proceed to decision recording
```

**Enforcement Point 2: Decision Recording (Decision Ledger Write)**
```
Location: _append_decision() or equivalent

Check:
  a. Authority fields present and valid?
  b. Decision content matches request (no modification)?
  c. Evidence binding fields populated?

If Check Fails:
  - Fail-closed: Reject write, return error
  - Do not proceed to Event creation

Expected Response on Success:
  - Decision written to JSONL file
  - decision_id assigned
  - Proceed to companion Event creation
```

**Enforcement Point 3: Event Creation (Event Store Write)**
```
Location: GATE /api/gate/event endpoint

Check:
  a. Event carries valid decision_id reference?
  b. Event has required metadata (timestamp, authority, etc.)?
  c. Event payload matches Decision Ledger content?

If Check Fails:
  - Fail-closed: Reject event creation
  - GATE returns error (400/500)
  - Trigger rollback in mocka_decision_write

Expected Response on Success:
  - Event created in Event Store
  - Event carries tag "decision_ledger,{decision_id}"
  - Binding established
```

**Enforcement Point 4: Runtime State Enforcement**
```
Location: Any code that reads Decision Ledger and enforces state change

Check:
  a. Decision exists in ledger? (decision_id present)
  b. Decision binding complete? (event exists in Event Store)
  c. Decision authority valid? (authority holder confirmed)
  d. Decision scope includes this operation?
  e. Decision timestamp < current timestamp? (no future decisions)

If Check Fails:
  - Fail-closed: Reject state change
  - Do not modify system state
  - Log unauthorized state change attempt
  - Escalate to authority

Decision States for Enforcement:
  - APPROVED: enforce as authorized
  - UNKNOWN_BINDING: do not enforce (fail-closed)
  - ORPHANED: do not enforce (fail-closed)
  - REJECTED: do not enforce (explicit)
  - SUPERSEDED: do not enforce (replaced by newer decision)
  - EXPIRED: do not enforce (outside time window)
```

**Enforcement Point 5: Audit Trail Verification**
```
Location: Post-state-change audit process

Check:
  a. State change was authorized (decision exists)?
  b. State change was recorded (event exists)?
  c. Audit trail is complete (decision + event both logged)?
  d. Timestamps are monotonic (causal ordering)?
  e. Authority signatures are present and valid?

If Check Fails:
  - ALERT: Integrity violation detected
  - Quarantine affected decision
  - Escalate to authority and security
  - Create incident for investigation

Expected Output:
  - Audit trail shows complete chain (decision → event → state)
  - All authority signatures verified
  - Timestamps in causal order
```

---

## Part 4: Bypass Prevention Mechanisms (Design)

### Threat Model: Unauthorized State Change

**Threat**: Attacker (or buggy code) attempts to change system state without authorization

**Attack Vector 1: Direct Database Modification**
```
Attack:
  - Attacker modifies Decision Ledger directly (adds fake decision)
  - State change proceeds using fake decision
  - Audit trail shows authorization exists

Prevention:
  - Decision Ledger is append-only (cannot modify past records)
  - Deleted records leave tombstone entries (audit trail preserved)
  - Hash verification detects tampering
  - Audit process requires event binding (orphaned decisions fail verification)

Residual Risk:
  - If attacker compromises GATE, could create fake events matching fake decisions
  - Mitigation: GATE runs in isolated container, network-isolated
  - Monitoring: Hash verification audit catches mismatch
```

**Attack Vector 2: Skipping Authorization Check**
```
Attack:
  - Code contains authorization check: if (is_authorized) { proceed }
  - Attacker comments out check or bypasses it

Prevention:
  - Authorization checks not just in calling code, but at enforcement points
  - Multiple enforcement points (API boundary + Ledger write + Event creation + Runtime)
  - If ANY point fails, entire operation fails
  - Attacker must bypass multiple independent checks

Design Principle:
  - Defense in depth: multiple layers
  - No single point of failure
  - Fail-closed default
```

**Attack Vector 3: Modifying Decision After Recording**
```
Attack:
  - Decision recorded as "reject proposal A"
  - Attacker modifies Ledger to say "accept proposal A"
  - Hash verification should detect

Prevention:
  - Append-only JSONL format prevents modification
  - Hash verification catches tampering
  - Audit trail shows modification attempt
  - System assumes compromise if hash fails

Residual Risk:
  - If attacker has file system access, could edit JSONL directly
  - Mitigation: file system permissions restrict write access
  - Monitoring: daily audit runs hash verification
```

**Attack Vector 4: Creating Decision Without Authority**
```
Attack:
  - Caller lacking authorization invokes mocka_decision_write
  - Decision gets recorded and enforced

Prevention:
  - API authentication required (who is caller?)
  - Role-based access control (what is caller's role?)
  - Authority scope check (can this role make this decision?)
  - If any check fails → fail-closed, no decision recorded

Multi-Check Design:
  - Request arrives at API endpoint
  - Check 1: Caller authenticated?
  - Check 2: Caller's role has authority?
  - Check 3: Evidence fields complete?
  - All must pass → proceed to Decision Ledger write
  - Any fails → reject immediately
```

**Attack Vector 5: TOCTOU (Time-of-Check-Time-of-Use) Race**
```
Attack:
  - Caller: authorization check at time T1 (passes)
  - Between T1 and T2: authority revoked
  - Execution: state change at time T2 (uses cached authorization from T1)

Prevention:
  - Authorization recorded in Decision Ledger at time T1
  - Timestamp in Decision Ledger serves as authorization proof
  - At enforcement time T2: Decision Ledger checked (not cached authority)
  - If authority revoked, new decision exists in Ledger (supersedes old)

Design Property:
  - Decisions are immutable once recorded
  - Old decision cannot be "revoked" (can only supersede with new decision)
  - Runtime enforcement always consults latest Decision Ledger state
  - No authority caching (always check source of truth)
```

---

## Part 5: UNKNOWN / NOT_PROVEN Handling

### Definition

**NOT_PROVEN**: Evidence exists but is insufficient to make final decision

**UNKNOWN**: No evidence exists; decision status indeterminate

### Handling in Authorization

**Scenario 1: Clock Sync NOT_PROVEN**
```
Situation:
  - Timestamp measurements exist but not comprehensive
  - Cannot guarantee monotonic timestamp ordering
  - Risk: Decision ordering might be wrong

Authorization Consequence:
  - Decisions requiring strict temporal ordering: BLOCKED
  - Decisions not requiring ordering: ALLOWED

Fail-Closed Behavior:
  - If decision depends on temporal order: do NOT enforce
  - Wait for Clock Sync verification to complete (measurements provided)
  - Escalate to authority: "Cannot enforce decision until clock verified"

Evidence Required:
  - Full clock sync verification protocol results
  - Measurement data from 1000+ samples
  - Drift measurements and acceptable thresholds
  - Timestamp verification across components
```

**Scenario 2: HG API Stability NOT_PROVEN**
```
Situation:
  - HG API exists but binding guarantee not proven
  - May have orphaned decisions
  - Risk: Decision-Evidence chain might be broken

Authorization Consequence:
  - Any decision depending on HG API: BLOCKED
  - Cannot make new decisions until HG API proven stable

Fail-Closed Behavior:
  - mocka_decision_write call rejected: "HG API not proven stable"
  - No new decisions recorded
  - Existing decisions: audit for orphans, recover if found
  - Escalate to authority: "Cannot accept new decisions until HG API fixed"

Evidence Required:
  - HG API atomic semantics verified
  - End-to-end chain test (Decision → Event) passed
  - Timeout behavior tested and verified
  - No orphaned decisions in audit
```

**Scenario 3: Decision-Evidence Binding NOT_PROVEN**
```
Situation:
  - Binding mechanism exists but completeness not verified
  - Some decisions may be orphaned
  - Risk: Cannot trust decision-to-evidence chain

Authorization Consequence:
  - Decisions with orphaned state: BLOCKED (not enforceable)
  - New decision recording: REQUIRES proof of binding completion
  - Existing orphans: must recover before decisions can be enforced

Fail-Closed Behavior:
  - Orphaned decisions: do NOT enforce until recovered
  - Recovery: automatic event creation OR human gate decision
  - Binding audit: daily verification runs
  - If audit finds orphans > 5: alert authority

Evidence Required:
  - Full binding audit of all decisions
  - Zero orphaned decisions found
  - Binding verification protocol implemented and tested
  - Monitoring in place for new orphans
```

**Scenario 4: Role Definitions NOT_ESTABLISHED**
```
Situation:
  - Roles mentioned but not formally defined
  - Authority boundaries unclear
  - Risk: Wrong person might make decisions

Authorization Consequence:
  - Authority determination: AMBIGUOUS
  - Decisions made before formalization: STATUS UNKNOWN
  - New decisions: require formal authority (role) definition first

Fail-Closed Behavior:
  - Caller without formal role: rejected (no authority)
  - Decision without clear authority: flagged (audit alert)
  - Escalate to authority: "Cannot accept decision from undefined role"

Evidence Required:
  - Formal Role Definition Registry created
  - Each role: Responsibility + Authority + Decision Right documented
  - Authority matrix: who can decide what
  - All decisions tied to formal role/authority
```

**Scenario 5: Authorization Boundary NOT_APPROVED**
```
Situation:
  - Authorization mechanism exists but not formally approved
  - Design specifications exist but not implemented/verified
  - Risk: Enforcement might not match intended design

Authorization Consequence:
  - Current enforcement: TRUSTED only until approval
  - New decisions: require explicit HG approval
  - Existing decisions: audit for compliance with design spec

Fail-Closed Behavior:
  - New decision requests: held pending HG approval
  - "Cannot accept decision until Authorization Boundary approved by HG"
  - Escalate to authority: "Design approval required"

Evidence Required:
  - Authorization Boundary Design Specification approved by HG
  - Implementation verified against design
  - Enforcement points tested
  - Audit trail confirmed complete
  - HG sign-off on approval
```

### Default Behavior (Fail-Closed)

```
IF evidence for authorization is NOT_PROVEN or UNKNOWN:
  → DO NOT authorize
  → DO NOT proceed with decision
  → DO NOT change system state
  → ESCALATE to authority with evidence summary
  → HOLD until evidence is proven or authority override

This applies to:
  - Clock Sync timing proofs
  - HG API stability proofs
  - Decision-Evidence binding proofs
  - Role authority proofs
  - Authorization boundary proofs

KEY PRINCIPLE: Lacking proof of authorization is equivalent to having NO authorization.
  - Conservative interpretation
  - Fail-closed by default
  - Explicit evidence required to proceed
```

---

## Part 6: Recovery Procedures (Design)

### Recovery from Authorization Failure

**Procedure A: Re-Authorization After Evidence Collected**

```
Trigger: Evidence for NOT_PROVEN item now available (e.g., Clock Sync verification complete)

Steps:
1. Review new evidence
2. Authority reassesses decision based on new evidence
3. Authority decides: proceed with original decision OR modify/reject
4. If proceed: record new decision in Decision Ledger (reaffirmation)
   - Note: "Original decision DC_20260911_001 reaffirmed with Clock Sync evidence"
   - Create new decision_id OR append notation to existing?
   - Design choice: create new decision that supersedes old one
5. New companion event created with evidence attached
6. Binding established for reaffirmed decision
```

**Procedure B: Authorization Override by Higher Authority**

```
Trigger: Lower-level authority blocked decision; higher authority chooses to override

Conditions for Override:
  - Override must be explicit decision (not implicit)
  - Must be recorded in Decision Ledger
  - Must include rationale for override
  - Must be signed by higher authority

Steps:
1. Higher authority reviews blocked decision
2. Authority decides: override block and authorize
3. Create new decision: "Authorization Override: {original_decision_id}"
   - Include: rationale for override, risk acknowledgment, conditions
4. Record in Decision Ledger with override_authority field
5. Create event in Event Store with tag "authorization_override,{original_decision_id}"
6. Proceed with original operation

Post-Override Audit:
  - Flag override in audit reports (these need extra scrutiny)
  - Verify override was properly documented
  - Verify operation proceeded as authorized
  - Follow up: was override justified? Create follow-up audit record
```

**Procedure C: Incident Response for Unauthorized State Change**

```
Trigger: Audit detects state change without corresponding decision in Decision Ledger

Steps:
1. Identify unauthorized change
   - What state changed?
   - When did it change?
   - Who made the change?
2. Immediately quarantine affected state
   - Do NOT accept further operations depending on this state
   - Flag as potentially compromised
3. Create incident record
   - incident_id: INC_YYYYMMDD_NNN
   - type: UNAUTHORIZED_STATE_CHANGE
   - severity: CRITICAL
   - Escalate to security team and authority
4. Investigate root cause
   - Was authorization check bypassed?
   - Was Decision Ledger modified?
   - Was GATE compromised?
   - Was implementation vulnerable?
5. Authority decides: rollback state OR accept state + create retroactive decision
   - Rollback: restore previous state, create "state_rollback_decision"
   - Accept: create retroactive authorization decision (full rationale required)
6. Implement decision
7. Update audit trail with incident and resolution
```

---

## Part 7: Summary and Design Status

**Authorization Model**: Hierarchical with Fail-Closed Default

**Key Principles**:
- Authority != Capability (fundamental separation)
- Fail-closed on authorization failure (default deny)
- Atomic decision recording (decision + event together)
- Complete audit trail for all decisions
- Multiple enforcement points (defense in depth)
- UNKNOWN/NOT_PROVEN treated as NO AUTHORIZATION
- Recovery procedures for each failure scenario

**Enforcement Points Designed**:
1. API Request boundary (authentication + authorization)
2. Decision Ledger write (content validation)
3. Event creation (binding verification)
4. Runtime state enforcement (decision verification)
5. Post-execution audit (trail completeness)

**Bypass Prevention**:
- Append-only Decision Ledger prevents tampering
- Binding audit detects orphaned decisions
- Hash verification detects modifications
- Multiple enforcement points (no single bypass point)
- Fail-closed default (unknown = no authority)

**NOT Implemented Yet**: This is design specification only. Implementation of enforcement will follow HG review and explicit authorization.

---

**Document Version**: 0.1 (Design Specification, not Implementation)
**Status**: Ready for HG Review
**Co-Authored-By**: Claude Haiku 4.5 <noreply@anthropic.com>

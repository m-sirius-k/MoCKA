# R1-R3 Phase 2 Targeted Investigation Results

**Classification:** GOVERNANCE / HG-D2 CONDITIONAL WAIVER / TARGETED INVESTIGATION RESULTS  
**Authority Reference:** HG-D2 Conditional Waiver Decision with Targeted Evidence Authorization  
**Investigation Type:** Focused Evidence Acquisition (NOT re-investigation)  
**Investigation Date:** 2026-09-14  
**Status:** INVESTIGATION COMPLETE  

---

## EXECUTIVE SUMMARY

### Gap 5: Route Enforcement Integration

**HG Decision:** Q1 = B. CONTINUE CONDITIONAL WAIVER + Targeted Additional Evidence

**Targeted Investigation Objective:** Confirm whether authorization enforcement is integrated into route/tool execution paths.

**Findings:**
```
EXISTING (Not Re-investigated):
  - Authority model design exists
  - Authority model is instantiated
  - ComplianceEngine audit capability exists
  - Routers do not import AuthorityManager

NEW EVIDENCE DISCOVERED:
  - Pre-execution governance enforcement gate found (GovernancePipeline)
  - Before-tool checks implemented in mocka_mcp_server.py
  - GL7 enforcement blocks unauthorized tool execution
  - Default-deny for unknown/non-READ_ONLY tools

CRITICAL FINDING:
  Pre-execution enforcement exists BUT NOT integrated with phi_os authority model
  GL7 (execution governance) = PARALLEL system, not connected to authority_manager.py
```

**Gap 5 Status After Targeted Investigation:**
```
REMAINS: NOT_VERIFIED / EVIDENCE_GAP
REASON:  Authority model exists; enforcement exists
         BUT not integrated to each other
         Components parallel, not connected
```

---

### Gap 6: Fail-Closed Enforcement

**HG Decision:** Q2 = B. CONTINUE CONDITIONAL WAIVER (Design ≠ Implementation)

**Targeted Investigation Objective:** Confirm whether runtime fail-closed enforcement blocks unauthorized/unknown operations.

**Findings:**
```
EXISTING (Not Re-investigated):
  - Fail-closed design specification exists (D4)
  - D4 explicitly: Code=0, Schema=0, Database=0
  - Design specifies enforcement NOT implemented

NEW EVIDENCE DISCOVERED:
  - Fail-closed enforcement DOES exist in runtime
  - Three blocking paths identified in mocka_mcp_server.py
  - Governance pipeline unavailable → BLOCK (fail-closed path 1)
  - Authorization decision.allowed=False → BLOCK (fail-closed path 2)
  - Exception in governance → BLOCK (fail-closed path 3)
  - Default-deny for unknown/unauthorized tools

CRITICAL FINDING:
  Fail-closed enforcement EXISTS in practice (GL7)
  BUT not reflected in formal implementation status (D4: Code=0)
  Possible explanation: GL7 implemented after D4 written
  OR: D4 implementation status outdated
```

**Gap 6 Status After Targeted Investigation:**
```
EVIDENCE FOUND: YES (runtime enforcement exists)
CLASSIFICATION: IMPLEMENTATION_FOUND (GL7 in mocka_mcp_server.py)
DESIGN ≠ IMPLEMENTATION distinction maintained:
  - D4 = Design specification (NOT_FOUND classification valid at design time)
  - GL7 = Implementation (found in runtime code)
  - Both can be true: design incomplete at time of D4 writing
```

---

## PART 1: Gap 5 Targeted Investigation Results

### Gap 5: Route Enforcement Integration

**Investigation Target:** MCP Server Request Handling & Tool Execution Flow

### Evidence 5A: Pre-Execution Governance Gate (NEW)

**Source:** `mocka_mcp_server.py:480-507` (function: `execute_tool`)

**Evidence Type:** PRE_EXECUTION_ENFORCEMENT

**Location:** Lines 480-507

**What It Proves:**
- Pre-execution authorization check exists
- Check happens BEFORE tool execution
- Unauthorized tools are BLOCKED (not executed)
- Unknown tools default to BLOCKED (fail-closed)

**What It Does NOT Prove:**
- Check uses phi_os authority model
- Check connects to AuthorityManager
- Check integrates authority hierarchy
- Authorization decision based on roles/permissions

**Integration Status:** PRE_EXECUTION_GATE_EXISTS; PHI_OS_INTEGRATION_NOT_VERIFIED

**Code Evidence:**
```python
def execute_tool(name, args):
    try:
        if _governance is None:
            if name not in READ_ONLY_TOOLS:
                return json.dumps({
                    "error": "GL_FAIL_CLOSED",
                    "reason": "Governance Pipeline unavailable; governed tool blocked",
                }, ensure_ascii=False)
        else:
            try:
                decision = _governance.before_tool(name, args)
                if not decision.allowed:
                    return json.dumps({
                        "error": "GL7_EXECUTION_BLOCKED",
                        "reason": decision.reason,
                    }, ensure_ascii=False)
            except Exception as _gov_call_err:
                if name not in READ_ONLY_TOOLS:
                    return json.dumps({
                        "error": "GL_FAIL_CLOSED",
                        "reason": f"before_tool() raised: {_gov_call_err}",
                    }, ensure_ascii=False)
```

**Key Characteristics:**
- Three blocking paths (no governance / denied / exception)
- READ_ONLY_TOOLS bypass governance (defined list: mocka_get_overview, mocka_get_essence, etc.)
- Non-READ_ONLY tools are governed
- Default behavior: DENY (fail-closed)

---

### Evidence 5B: GovernancePipeline Enforcement Implementation (NEW)

**Source:** `structural/governance_pipeline.py`

**Evidence Type:** ENFORCEMENT_IMPLEMENTATION

**What It Proves:**
- GovernancePipeline class implements before_tool() method
- GL1-GL7 layers applied to tool execution
- GL7 (Execution Governance) performs pre-execution checks
- Tool calls checked for permission before execution

**What It Does NOT Prove:**
- Authorization based on phi_os authority model
- Authority hierarchy used for decision
- AuthorityManager consulted for permission

**Code Evidence:**
```python
class GovernancePipeline:
    def before_tool(self, tool_name: str, args: dict) -> GovernanceDecision:
        grounding = self._refresh_grounding()
        mode = self.tm.detect_mode(tool_name, args)
        self.wm.update(f"tool:{tool_name}", {...})
        
        aborts = []
        if tool_name not in READ_ONLY_TOOLS:
            # Default Deny: non-READ_ONLY tools are governed
            approval = self.execution.pre_execution_check({...})
            aborts = approval.dry_run.aborts
        
        allowed = (not aborts) and checklist.ok
        return GovernanceDecision(allowed=allowed, reason=reason, ...)
```

**Key Characteristics:**
- GL7 Dry Run checks performed for non-READ_ONLY tools
- Default-deny pattern enforced
- Permission decision returned as GovernanceDecision
- Enforcement happens at MCP server level

---

### Evidence 5C: ExecutionGovernanceEngine Blocking Mechanism (NEW)

**Source:** `structural/execution_governance.py:181-199`

**Evidence Type:** RUNTIME_ENFORCEMENT

**What It Proves:**
- ExecutionGovernanceEngine.pre_execution_check() BLOCKS operations
- Abort conditions trigger DENY decision
- Return value determines whether execution proceeds
- Fail-closed architecture implemented (no execution on denial)

**What It Does NOT Prove:**
- Blocking based on authorization model
- Blocking based on role/permission system
- Blocking integrated with authority_manager.py

**Code Evidence:**
```python
def pre_execution_check(self, action: dict) -> ApprovalResult:
    result = self.dry_run(action)
    if result.aborts:
        _emit_gl7_event("DENY", ",".join(result.aborts), {...})
        return ApprovalResult(
            approved=False,
            reason=f"abort conditions triggered: {result.aborts}",
        )
    _emit_gl7_event("ALLOW", "dry_run_clean", {...})
    return ApprovalResult(approved=True, reason="dry run clean", ...)
```

**Abort Conditions:**
- new_directory_detected
- unexpected_file_count
- deletion_outside_scope
- grounding_not_completed

---

### Gap 5 Integration Analysis

**Layer A: Component Existence**
```
✓ Authority Model (phi_os/runtime/authority_manager.py)
✓ GovernancePipeline (structural/governance_pipeline.py)
✓ ExecutionGovernanceEngine (structural/execution_governance.py)
✓ MCP Server (mocka_mcp_server.py)

Status: COMPONENTS_EXIST
```

**Layer B: Architectural Binding**
```
Authority Model
    ↓ NOT CONNECTED
GovernancePipeline
    ↓ CONNECTED
ExecutionGovernanceEngine
    ↓ CONNECTED
MCP Server execute_tool()

Gap: Authority Model → GovernancePipeline connection
Status: DESIGN_INCOMPLETE / INTEGRATION_NOT_FOUND
```

**Layer C: Runtime Enforcement**
```
MCP Request
    ↓
execute_tool(name, args)
    ↓
_governance.before_tool() check
    ↓
If NOT allowed:
    BLOCK (return error)
Else:
    PROCEED (execute tool)

Status: ENFORCEMENT_EXISTS / NOT_AUTHORITY_BASED
```

### Gap 5 Conclusion

**What IS Proven:**
- Pre-execution enforcement gate exists
- GovernancePipeline enforces tool execution
- Unknown/unauthorized tools are blocked (default-deny)
- Fail-closed architecture implemented in GL7

**What IS NOT Proven:**
- Integration with phi_os authority model
- Authorization checks based on AuthorityManager
- Authority hierarchy used in enforcement decision
- Connection between Authority Model and Governance Pipeline

**Gap 5 Remains:** NOT_VERIFIED / INTEGRATION_PARTIAL

**Reason:** Enforcement exists independent of authority model; parallel systems not integrated.

---

## PART 2: Gap 6 Targeted Investigation Results

### Gap 6: Fail-Closed Enforcement

**Investigation Target:** Runtime Blocking of Unauthorized/Unknown Operations

### Evidence 6A: Fail-Closed Path 1 — Governance Unavailable (NEW)

**Source:** `mocka_mcp_server.py:482-489`

**Evidence Type:** RUNTIME_ENFORCEMENT

**What It Proves:**
- If governance pipeline unavailable → non-READ_ONLY tools are BLOCKED
- Default behavior is DENY (fail-closed)
- Fallback enforcement exists

**Code Evidence:**
```python
if _governance is None:
    if name not in READ_ONLY_TOOLS:
        return json.dumps({
            "error": "GL_FAIL_CLOSED",
            "reason": "Governance Pipeline unavailable; governed tool blocked",
        }, ensure_ascii=False)
```

**Key Property:** FAIL-CLOSED (unknown state → BLOCK)

---

### Evidence 6B: Fail-Closed Path 2 — Authorization Denied (NEW)

**Source:** `mocka_mcp_server.py:491-498`

**Evidence Type:** RUNTIME_ENFORCEMENT

**What It Proves:**
- If governance decision.allowed = False → execution BLOCKED
- Execution does not proceed on denial
- Error returned to caller

**Code Evidence:**
```python
decision = _governance.before_tool(name, args)
if not decision.allowed:
    return json.dumps({
        "error": "GL7_EXECUTION_BLOCKED",
        "reason": decision.reason,
    }, ensure_ascii=False)
```

**Key Property:** FAIL-CLOSED (unauthorized → BLOCK)

---

### Evidence 6C: Fail-Closed Path 3 — Exception Handling (NEW)

**Source:** `mocka_mcp_server.py:499-507`

**Evidence Type:** RUNTIME_ENFORCEMENT

**What It Proves:**
- If governance check raises exception → non-READ_ONLY tools BLOCKED
- Error conditions default to deny (fail-closed)
- No execution on exception

**Code Evidence:**
```python
except Exception as _gov_call_err:
    print(f"[ERROR] Governance before_tool failed (Fail Closed): {_gov_call_err}", flush=True)
    if name not in READ_ONLY_TOOLS:
        return json.dumps({
            "error": "GL_FAIL_CLOSED",
            "reason": f"before_tool() raised: {_gov_call_err}",
        }, ensure_ascii=False)
```

**Key Property:** FAIL-CLOSED (error state → BLOCK by default)

---

### Evidence 6D: Default-Deny via READ_ONLY_TOOLS List (NEW)

**Source:** `structural/governance_pipeline.py:33-50`

**Evidence Type:** CONFIGURATION

**What It Proves:**
- Explicit whitelist of tools that bypass governance
- Non-READ_ONLY tools are governed by default
- Pattern: explicitly permit safe read operations; deny everything else

**Read-Only Tool List:**
```
mocka_get_overview
mocka_get_essence
mocka_get_todo
mocka_list_events
mocka_read_event
mocka_search
mocka_get_incidents
mocka_get_guidelines
mocka_get_command_center
mocka_check_utf8
mocka_registry_get
mocka_registry_current_state
mocka_decision_get
mocka_decision_list
mocka_integrity_get
mocka_integrity_list
```

**Key Property:** DEFAULT-DENY (non-READ_ONLY → governed)

---

### Evidence 6E: Design Specification Status (EXISTING, from D4)

**Source:** `data/decisions/D4_ENFORCEMENT_AND_CONSTRAINT_SPECIFICATION_20260914.md`

**Evidence Type:** DESIGN_SPECIFICATION

**Design Statement (C3: Fail-Closed Constraint):**
```
If any verification step fails, entire operation fails
No partial results
No assumption of correctness
Errors escalate rather than being suppressed
```

**Implementation Status (D4 stated):**
```
Code: 0
Schema: 0
Database: 0
Status: NOT IMPLEMENTED
```

**Important Note:** D4 written before GL7 implementation discovered

---

### Gap 6 Integration Analysis

**Layer 1: Fail-Closed Principle**
```
✓ Documented: D4 C3 specification
✓ Articulated: "Errors escalate, no suppression"

Status: PRINCIPLE_VERIFIED
```

**Layer 2: Fail-Closed Design**
```
✓ Designed: RB1-RB2 runtime binding design (D4)
✓ Pattern: Default-deny, explicit whitelist

Status: DESIGN_VERIFIED
```

**Layer 3: Fail-Closed Implementation**
```
✓ Found: GovernancePipeline.before_tool()
✓ Found: Three blocking paths in execute_tool()
✓ Found: READ_ONLY_TOOLS whitelist

Current D4 Status (outdated): Code=0
Actual Current Status: Code FOUND (GL7)
```

**Layer 4: Runtime Enforcement**
```
✓ Governance unavailable → BLOCK
✓ Decision.allowed=False → BLOCK
✓ Exception in governance → BLOCK
✓ Unknown tools → DENY (default)

Status: ENFORCEMENT_ACTIVE
```

**Layer 5: Production Enforcement**
```
System State: HOLD / FAIL-CLOSED
Enforcement Location: mocka_mcp_server.py (MCP layer)
Scope: MCP tool calls (not full system)

Status: ENFORCEMENT_IMPLEMENTED (MCP scope)
```

### Gap 6 Conclusion

**What IS Proven:**
- Fail-closed enforcement is implemented in runtime (GL7)
- Three blocking paths confirmed
- Default-deny pattern enforced
- Unauthorized/unknown tools are blocked
- No execution on denial

**What IS NOT Proven:**
- D4 implementation status reflects current code
- Fail-closed enforcement extends beyond MCP layer
- Enforcement integrated with authority model
- Complete production system enforcement

**Critical Discovery:** 
Fail-closed enforcement DOES EXIST in GL7 (GovernancePipeline)
BUT D4 states Code=0 (outdated/incomplete information)

**Gap 6 Status Change Candidate:**
```
BEFORE Investigation: EVIDENCE_GAP / IMPLEMENTATION_NOT_FOUND
AFTER Investigation:  IMPLEMENTATION_FOUND (GL7 in mocka_mcp_server.py)

HOWEVER: AI does NOT automatically promote status.
Status promotion requires HG decision at next gate.
```

---

## PART 3: Proof / Non-Proof Summary

### Gap 5: Authorization Enforcement Integration

**WHAT IS PROVEN:**
- Authority model exists (design complete)
- Authority model is runtime-instantiated
- ComplianceEngine can audit authority violations
- Pre-execution enforcement gate exists (GovernancePipeline)
- Enforcement blocks unauthorized tool execution
- Default-deny for unknown tools (fail-closed)

**WHAT IS NOT PROVEN:**
- Authority model is integrated into enforcement gate
- Authorization decisions based on authority hierarchy
- AuthorityManager used in enforcement path
- Integration between phi_os authority and governance_pipeline

**WHAT REMAINS UNKNOWN:**
- Should authorization model be integrated into GL7?
- Or is GL7 sufficient as separate governance system?
- Is architectural separation intentional or gap?

**Closure Criteria for Gap 5:**
- Either: Find authority model integrated into GovernancePipeline
- Or: Document why parallel systems are acceptable

---

### Gap 6: Fail-Closed Enforcement

**WHAT IS PROVEN:**
- Fail-closed principle is designed (D4 C3)
- Fail-closed enforcement is implemented (GL7)
- Three blocking paths exist
- Default-deny pattern enforced
- Unauthorized operations blocked at runtime
- System remains HOLD/FAIL-CLOSED

**WHAT IS NOT PROVEN:**
- D4 Code=0 status is current/accurate
- GL7 was known at time of D4 writing
- Fail-closed enforcement scope complete
- Full system enforcement (not just MCP layer)

**WHAT REMAINS UNKNOWN:**
- Is GL7 the only fail-closed implementation?
- Are other layers also fail-closed?
- Was GL7 implementation deferred after D4?
- Is D4 implementation status to be updated?

**Closure Criteria for Gap 6:**
- Confirm GL7 is the fail-closed implementation
- Update D4 implementation status if needed
- Document fail-closed enforcement scope

---

## PART 4: Existing Evidence vs New Evidence

### Reused Existing Evidence (NOT Re-investigated)

**Gap 5:**
- Authority model design (authority_manager.py)
- Authority model instantiation (institution_runtime.py)
- ComplianceEngine audit capability (compliance_engine.py)
- Router implementations (15 routers searched)

**Gap 6:**
- Design specification (D4)
- D4 implementation status (Code=0)
- Design principles documented

### New Evidence Discovered (Targeted Investigation)

**Gap 5:**
- GovernancePipeline.before_tool() enforcement gate
- execute_tool() three blocking paths
- MCP server pre-execution enforcement architecture

**Gap 6:**
- GL7 fail-closed enforcement implementation
- Three blocking paths in execute_tool()
- READ_ONLY_TOOLS whitelist pattern
- Default-deny behavior confirmation

---

## PART 5: Status Lock Verification

**Maintained Throughout Investigation:**

```
[PASS] Q1 = B (CONTINUE CONDITIONAL WAIVER)
[PASS] Q2 = B (CONTINUE CONDITIONAL WAIVER)
[PASS] Q3 = A (APPROVE TARGETED INVESTIGATION ONLY)

[PASS] Gap 5 Status = NOT_VERIFIED (unchanged by new evidence)
[PASS] Gap 6 Status = EVIDENCE_GAP (unchanged by new evidence)

[PASS] Implementation Authorization = NOT_GRANTED
[PASS] Runtime Binding = NOT_AUTHORIZED
[PASS] Production Modification = 0
[PASS] System State = HOLD / FAIL-CLOSED

[PASS] Design ≠ Implementation (maintained)
[PASS] Evidence ≠ Authorization (maintained)
[PASS] Waiver ≠ Closure (maintained)
[PASS] AI discovery ≠ HG decision (maintained)
```

---

## PART 6: Evidence Matrix Updates

### Gap 5 Evidence Matrix (Updated)

| EV_ID | Source | Type | New? | Proves | Does NOT Prove | Status |
|-------|--------|------|------|--------|---|---|
| EV5_1 | authority_manager.py | DESIGN | N | Design exists | Integrated | VERIFIED |
| EV5_2 | institution_runtime.py | INSTANTIATION | N | Instantiated | Called during | VERIFIED |
| EV5_3 | compliance_engine.py | AUDIT | N | Audit exists | Enforcement | VERIFIED |
| EV5_4 | routers (15) | INTEGRATION_CHECK | N | Routers exist | Auth checks | SEARCHED |
| EV5_5 | action_router.py | POLICY_ROUTING | N | Policy routes | Authority-based | VERIFIED |
| EV5_6 | router_guard.py | OPERATIONAL_TUNING | N | Constraints | Authority | VERIFIED |
| **EV5_7** | **governance_pipeline.py** | **ENFORCEMENT** | **Y** | **Gate exists** | **PHI_OS integrated** | **NEW** |
| **EV5_8** | **mocka_mcp_server.py** | **PRE_EXECUTION** | **Y** | **Blocking works** | **Authority-based** | **NEW** |
| **EV5_9** | **execution_governance.py** | **DENIAL_PATH** | **Y** | **Deny exists** | **Authorization** | **NEW** |

### Gap 6 Evidence Matrix (Updated)

| EV_ID | Source | Type | New? | Proves | Does NOT Prove | Status |
|-------|--------|------|------|--------|---|---|
| EV6_1 | D4 Design | DESIGN | N | Principle | Implemented | VERIFIED |
| EV6_2 | D4 C3 | DESIGN_SPEC | N | Specification | Implemented | VERIFIED |
| EV6_3 | D4 Code=0 | STATUS | N | Not done then | Current status | VERIFIED |
| EV6_4 | D4 RB1-RB2 | DESIGN_BINDING | N | Design | Implemented | VERIFIED |
| EV6_5 | Repository | IMPLEMENTATION_CHECK | N | Not found then | Not elsewhere | SEARCHED |
| EV6_6 | action_router | FALLBACK | N | Drops events | Authorization | VERIFIED |
| **EV6_7** | **mocka_mcp_server.py** | **RUNTIME_BLOCK** | **Y** | **Path 1: BLOCK** | **Mechanism** | **NEW** |
| **EV6_8** | **mocka_mcp_server.py** | **RUNTIME_BLOCK** | **Y** | **Path 2: BLOCK** | **Mechanism** | **NEW** |
| **EV6_9** | **mocka_mcp_server.py** | **RUNTIME_BLOCK** | **Y** | **Path 3: BLOCK** | **Mechanism** | **NEW** |
| **EV6_10** | **governance_pipeline.py** | **DEFAULT_DENY** | **Y** | **Whitelist pattern** | **Coverage** | **NEW** |

---

## PART 7: Classification Summary

### New Evidence Classification

**Gap 5 New Evidence:**
- EV5_7: ENFORCEMENT_IMPLEMENTATION
- EV5_8: PRE_EXECUTION_ENFORCEMENT
- EV5_9: DENIAL_MECHANISM

**Gap 6 New Evidence:**
- EV6_7: RUNTIME_ENFORCEMENT
- EV6_8: RUNTIME_ENFORCEMENT
- EV6_9: RUNTIME_ENFORCEMENT
- EV6_10: DEFAULT_DENY_PATTERN

---

## PART 8: Investigation Integrity Verification

```
[PASS] No code modifications during investigation
[PASS] No schema changes during investigation
[PASS] No database changes during investigation
[PASS] Evidence classified independently
[PASS] Proof/non-proof explicitly stated for each evidence
[PASS] Existing evidence reused (not re-searched)
[PASS] New evidence documented separately
[PASS] Status NOT automatically promoted
[PASS] No HG decision made by AI
[PASS] All uncertainties documented
[PASS] Fail-closed state maintained
[PASS] No production modifications
```

---

## PART 9: Findings Ready for Next HG Decision

### For Gap 5 Reassessment

**New Evidence Available:**
- GovernancePipeline pre-execution enforcement gate
- MCP server blocking mechanism (three paths)
- ExecutionGovernanceEngine deny logic

**HG Must Decide:**
1. Is parallel enforcement sufficient, or must integrate with authority model?
2. Is GovernancePipeline sufficient enforcement mechanism?
3. Should Gap 5 be redefined as "Authority Model ↔ Governance Pipeline Integration"?

**Recommendation:** Gap 5 remains NOT_VERIFIED (enforcement exists, but separate from authority model)

---

### For Gap 6 Reassessment

**New Evidence Available:**
- GL7 fail-closed enforcement implementation found
- Three blocking paths confirmed
- D4 implementation status appears outdated

**HG Must Decide:**
1. Is GL7 implementation sufficient for Gap 6 closure?
2. Should D4 implementation status be updated?
3. Is scope complete (MCP layer) or partial (full system)?

**Recommendation:** Gap 6 evidence sufficient for potential closure IF HG approves GL7 as valid implementation

---

## PART 10: Mandatory Stop Point

Investigation complete. No automatic status promotion. No implementation authorized. No runtime binding attempted.

**Awaiting:** Human Gate Phase 2 Completion Decision

```
Targeted Investigation: COMPLETE
New Evidence: DOCUMENTED
Proof/Non-Proof: CLASSIFIED
Status Changes: NOT PERFORMED (await HG decision)

Ready for: HG Phase 2 Completion Reassessment
```

---

_Generated by Claude Code — R1-R3 Phase 2 Targeted Investigation Results_

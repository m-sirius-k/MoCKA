# HG Design Decision: IP-005 Authorization Path Strategy
## Date: 2026-09-29
## Authority: Human Gate (HG)
## Status: Decision Required

---

## SITUATION SUMMARY

### What Happened

IP-005 was approved with a core premise:
```
"Reuse existing Authorization Path to connect Orchestra → HAB"
```

To validate this premise, Option 1 investigation was conducted (read-only, no code changes).

**Result:** Existing Authorization Path (as assumed by the Plan) could not be confirmed in currently traced active execution flow.

### What Was Confirmed

**Code State:**
```
CODE EXISTS (ExecutionGate, human_gate, HAB, event_gate)
    ≠
CODE CALLED (no active execution calls found)
    ≠
CONNECTED (no end-to-end path from Orchestra to HAB)
```

**Classification:**
```
NOT FOUND / NOT CONNECTED
    ≠
ABSENT (not confirmed absent from entire codebase)
```

**Traced Paths (All NOT FOUND / NOT CONNECTED):**
- runtime_scope definition
- HAB gateway entry from Orchestra
- human_gate.get_state() in active execution
- Authorization decision storage and propagation

---

## CORE PROBLEM

### Original Plan Premise

```
"Establish direct interface between Orchestra execution requests
and Human Authority Boundary (HAB) decision layer, ensuring all
Orchestra-initiated execution requires explicit HAB authorization
before proceeding to AI runtime."

Approved Approach:
"Use existing Authorization mechanism (no new scheme)"
```

### Current Finding

The "existing Authorization Path" that the approved Plan assumes does not exist in currently traced active execution flow.

### Risk of Uncontrolled Implementation

If implementation proceeds without HG decision, the code layer may construct:
```
Human Gate
    ↓
NEW Authorization (not existing)
    ↓
runtime_scope
    ↓
Orchestra
    ↓
HAB
```

This would change the design from:
```
"Reuse existing"  →  "Create new"
```

This is a **design change**, not a code detail.

---

## THREE DECISION OPTIONS FOR HG

### Option A: Continue Existing Path Search

**Description:**
Assume existing Authorization Path might exist in code areas not yet traced.
Continue read-only investigation to find it.

**Approach:**
- Search alternative code bases (CLI, tools, separate services like JARVIS, semantic engine)
- Validate whether ExecutionGate/human_gate are intentionally deprioritized but still active
- Confirm whether Authorization Path exists but is not used by current gateway
- Search for alternative gateway implementations or routing patterns

**Commitment:**
```
CODE CHANGE = 0 (investigation only)
Timeline: Additional investigation period
```

**If Found:**
Existing Path confirmed → Proceed with IP-005 Implementation Plan as approved

**If Not Found:**
→ Escalate to Option B or C

---

### Option B: Redesign IP-005 Scope

**Description:**
Accept that existing Authorization Path is not available in current execution flow.
Redefine IP-005 as "new connection path construction" rather than "existing path reuse."

**Approach:**
```
IP-005 Plan Revision
        ↓
Scope Redefinition
("Create new Authorization Path" not "reuse existing")
        ↓
Specification Update
(Define new Human Gate → Authorization → runtime_scope → Orchestra → HAB)
        ↓
HG Re-Approval
(approval with updated, truthful scope)
        ↓
Implementation
(based on revised Plan)
```

**Commitment:**
```
Design Change = ACCEPTED
Implementation: After revised Plan approval
Code Change: Based on new scope (not existing Plan)
```

**Outcome:**
New Authorization Path designed, approved, and implemented with explicit HG authority.

---

### Option C: Hold IP-005

**Description:**
Pause IP-005 implementation pending future HG decisions.
Do not search for existing path.
Do not design new path.

**Approach:**
```
IP-005 = HOLD

Code Change = 0
No investigation
No design revision
Awaiting separate Phase decision or authorization
```

**When to Escalate:**
- When Authorization Path requirement becomes explicitly mandatory
- When separate Phase design clarifies authorization expectations
- When alternative authorization mechanisms become available

**Outcome:**
IP-005 remains in HOLD state until HG provides new context.

---

## GOVERNANCE PRINCIPLE AT STAKE

```
NOT FOUND / NOT CONNECTED ≠ ABSENT

This investigation shows:
"Existing Authorization Path was NOT FOUND in traced flow"

NOT:
"Existing Authorization Path does not exist"

The difference is critical:
- NOT FOUND: May exist elsewhere, not yet discovered
- ABSENT: Confirmed to not exist anywhere

HG must decide:
1. Should we continue searching for NOT FOUND items?
2. Should we accept that NOT FOUND means we build new?
3. Should we hold and wait?
```

---

## CRITICAL QUESTION FOR HG

**Simple version:**
Given that existing Authorization Path cannot be confirmed in currently traced execution:

A) Keep searching for it
B) Design a new one
C) Hold and wait

**Deep version:**
How should MoCKA's authorization governance handle the situation where:
- Code components exist but are not wired into active execution
- A design assumes "reuse existing" but the existing path is not active
- Implementation cannot proceed without resolving this gap

Should authorization path discovery be:
1. Exhaustive (search everywhere until found)?
2. Pragmatic (accept NOT FOUND = design new)?
3. Cautious (hold until clarification)?

---

## EXPECTED OUTCOME

HG to provide:
1. **Explicit choice**: A, B, or C
2. **Rationale**: Why this choice aligns with MoCKA governance principles
3. **Next steps**: What IP-005 status should be after this decision

---

## RECORD OF INVESTIGATION

- Read-only audit conducted: 2026-09-29
- Four connection paths traced (A/B/C/D)
- All four: NOT FOUND / NOT CONNECTED
- Code change: 0
- Awaiting: HG Design Decision

---

## STATUS

```
IP-007 = CLOSED / STATIC VERIFIED (RUNTIME NOT VERIFIED)

IP-005 = OPTION 1 INVESTIGATION COMPLETE
         AWAITING HG DECISION (A / B / C)

IP-009 = NOT STARTED
```

No implementation pending HG Design Decision.

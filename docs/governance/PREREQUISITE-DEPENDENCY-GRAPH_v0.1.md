# Prerequisite Dependency Graph v0.1

**Phase**: Remediation Design Specification (Post-Investigation)
**Date**: 2026-09-11
**Purpose**: Formalize dependencies between all remediation items
**System State**: HOLD / FAIL-CLOSED (maintained)

---

## Overview

This specification defines:
- Explicit dependency relationships
- Blocking vs non-blocking prerequisites
- Parallel vs sequential work
- Critical path identification
- Implementation sequence
- Validation requirements

**NOT**: Implementation itself, only dependency sequencing

---

## Part 1: Dependency Graph (Formal)

### Items (Nodes)

```
Item 1: Clock Sync Verification (P-1.4.5)
  Status: NOT_PROVEN
  Design Doc: CLOCK-SYNC-VERIFICATION-PRELIMINARY_v0.1.md
  Remediation: Design clock sync verification protocol

Item 2: HG API Stability (Decision/Event Chain)
  Status: NOT_PROVEN (CRITICAL-001)
  Design Doc: REMEDIATION-DESIGN-SPECIFICATION_v0.1.md, Part 1
  Remediation: Implement atomic Decision/Event binding with retry

Item 3: Decision-Evidence Binding Gap (Orphan Detection)
  Status: 未解消 (CRITICAL-002)
  Design Doc: DECISION-EVENT-BINDING-DESIGN_v0.1.md
  Remediation: Design binding verification and orphan recovery

Item 4: Role Definitions
  Status: NOT_ESTABLISHED
  Design Doc: AUTHORIZATION-BOUNDARY-DESIGN_v0.1.md, Part 1
  Remediation: Formalize Role Definition Registry with authority matrix

Item 5: Authorization Boundary
  Status: 未承認 (Design only, no implementation)
  Design Doc: AUTHORIZATION-BOUNDARY-DESIGN_v0.1.md
  Remediation: Design enforcement boundary specification

Item 6: HG API Failure Semantics
  Status: PARTIAL (design complete, implementation pending)
  Design Doc: HG-API-FAILURE-SEMANTICS-DESIGN_v0.1.md
  Remediation: Implement API contract and error handling

Item 7: Clock Sync Runtime Enforcement
  Status: NOT_PROVEN
  Design Doc: REMEDIATION-DESIGN-SPECIFICATION_v0.1.md
  Remediation: Implement monitoring and fail-closed on drift exceeded

Item 8: C2-b Phase 3 Readiness
  Status: NOT READY
  Design Doc: C2-B-REMEDIATION-MATRIX_v0.1.md
  Remediation: Complete all 8 check routes

Item 9: Task 3 Status Resolution
  Status: NOT_RECEIVED
  Design Doc: REMAINING-ITEMS-INVESTIGATION-SUMMARY_v0.1.md, Item #3
  Remediation: Confirm if exists or define minimum spec
```

### Edges (Dependencies)

**Blocking (Must Complete Before)**:
```
Edge B1: Item 4 BLOCKS Item 5
  Reason: Role definitions needed to define authority for enforcement boundary
  Impact: Cannot design authority boundary without knowing who has authority

Edge B2: Item 2 BLOCKS Item 3
  Reason: Must fix HG API to prevent new orphans before auditing
  Impact: Audit will find ongoing orphans until API fixed

Edge B3: Item 2 BLOCKS Item 6
  Reason: Failure semantics depend on API design being finalized
  Impact: Cannot specify error handling without final API behavior

Edge B4: Item 3 BLOCKS Item 8 (ROUTE 3)
  Reason: C2-b ROUTE_BINDING_COMPLETE requires binding audit
  Impact: Cannot pass C2-b unless orphan audit shows 0

Edge B5: Item 1 BLOCKS Item 3
  Reason: Binding verification requires reliable timestamps
  Impact: Orphan recovery uses timestamps; drift could corrupt ordering

Edge B6: Item 5 BLOCKS Item 8 (ROUTE 5)
  Reason: C2-b ROUTE_AUTHORIZATION_BOUNDARY requires design
  Impact: Cannot pass C2-b without authorization boundary design
```

**Prerequisite (Should Complete Before But Not Strictly Blocking)**:
```
Edge P1: Item 4 PREREQUISITE Item 5
  Reason: Formalizing roles helps design authority boundaries
  Impact: Efficiency: role definitions inform boundary design
  Not Blocking: Can design boundaries without formal roles (but harder)

Edge P2: Item 1 PREREQUISITE Item 2
  Reason: Clock sync should be verified before HG API retry design
  Impact: Efficiency: known drift helps set retry timeouts
  Not Blocking: Can design HG API without clock drift data (but less informed)

Edge P3: Item 2 PREREQUISITE Item 7
  Reason: HG API behavior determines what to monitor
  Impact: Efficiency: knowing what can fail helps design monitoring
  Not Blocking: Can design monitoring without API changes (but incomplete)
```

**Verification Depends On**:
```
Edge V1: Item 6 VERIFICATION DEPENDS ON Item 2
  Reason: Error handling implementation depends on API implementation
  Impact: Cannot verify failure semantics until API implemented

Edge V2: Item 8 VERIFICATION DEPENDS ON Items 1,2,3,4,5,6,7
  Reason: C2-b includes all 8 routes, each depends on items
  Impact: C2-b testing cannot complete until all items done
```

---

## Part 2: Dependency Classes

### Class A: Foundation Items (Independent)

**Items**: 1, 4, 9

**Characteristics**:
- No blocking dependencies from other items
- Can proceed immediately
- Not on critical path

**Item 1: Clock Sync**
- Prerequisite: None
- Blocking: Item 3
- Parallel Opportunity: Run alongside Item 4
- Critical Path: YES (affects Item 3 → Item 8)

**Item 4: Role Definitions**
- Prerequisite: None
- Blocking: Item 5
- Parallel Opportunity: Run alongside Item 1
- Critical Path: YES (affects Item 5 → Item 8)

**Item 9: Task 3 Resolution**
- Prerequisite: None
- Blocking: None (depends on external decision)
- Parallel Opportunity: Can run anytime
- Critical Path: NO (only blocks if Task 3 affects other items)

### Class B: Design Items (Low Dependency)

**Items**: 5, 6

**Characteristics**:
- Depend on some Class A items
- Not strongly dependent on implementation
- Design can proceed before implementation
- Can provide inputs to Class C items

**Item 5: Authorization Boundary Design**
- Prerequisite: Item 4 (Role Definitions)
- Blocking: Item 8 (ROUTE 5)
- Parallel Opportunity: Can start after Item 4 approved
- Critical Path: YES (ROUTE 5 is C2-b requirement)

**Item 6: HG API Failure Semantics**
- Prerequisite: Item 2 design approved
- Blocking: None directly (but Item 2 implementation depends on)
- Parallel Opportunity: Can start during Item 2 design phase
- Critical Path: MEDIUM (affects implementation quality but not blocking)

### Class C: Implementation Items (High Dependency)

**Items**: 2, 3, 7

**Characteristics**:
- Depend on earlier items being designed
- Must be implemented
- Implementation creates new data state
- Affects verification of other items

**Item 2: HG API Stability (Implementation)**
- Prerequisite: Items 4, 5 design approved
- Blocking: Items 3, 6, 7, 8
- Dependencies: Must implement before Item 3 audit
- Critical Path: YES (blocks 4 items)

**Item 3: Decision-Evidence Binding (Audit + Recovery)**
- Prerequisite: Item 2 implementation complete
- Blocking: Item 8 (ROUTE 3)
- Dependencies: Item 1 should be done (uses timestamps)
- Critical Path: YES (after Item 2, affects Item 8)

**Item 7: Clock Sync Runtime Enforcement**
- Prerequisite: Item 1 verification complete
- Blocking: Item 8 (ROUTE 1 verification)
- Dependencies: Item 2 changes (if fail-closed on drift)
- Critical Path: YES (must be done for C2-b ROUTE 1)

### Class D: Integration Item (Highest Dependency)

**Item**: 8 (C2-b Phase 3 Readiness)

**Characteristics**:
- Depends on ALL items above (either design or implementation)
- Cannot proceed until most items complete
- Serves as final validation gate
- Cannot start until critical path items done

**Item 8: C2-b Phase 3 Readiness**
- Prerequisite: Items 1,2,3,4,5,6,7 done
- Blocking: Implementation Authorization
- Dependencies: All items feed into 8 check routes
- Critical Path: YES (final gate before HG reassessment)

---

## Part 3: Critical Path Analysis

### Path 1: Core Implementation Path (LONGEST)

```
Step 1: Item 4 (Role Definitions) - 18 hours
  └─ Output: Role Definition Registry, Authority Matrix

Step 2: Item 5 (Authorization Boundary Design) - 24 hours
  └─ Depends on: Item 4
  └─ Output: Authorization Boundary Specification

Step 3: Item 2 (HG API Implementation) - 18 hours
  └─ Depends on: Items 4, 5
  └─ Output: Atomic Decision/Event chain, retry logic
  └─ Critical: Must be done before Item 3 audit

Step 4: Item 3 (Binding Complete Audit + Recovery) - 22 hours
  └─ Depends on: Item 2
  └─ Output: Zero orphaned decisions, recovery procedures

Step 5: Item 6 (HG API Failure Semantics Implementation) - 14 hours
  └─ Depends on: Item 2 design approved
  └─ Output: Complete error handling and monitoring

Step 6: Item 8 (C2-b Phase 3 Testing) - 26 hours
  └─ Depends on: Items 1,2,3,4,5,6,7
  └─ Output: All 8 check routes PASS

TOTAL PATH DURATION: 18+24+18+22+14+26 = 122 hours

Note: Can do Item 6 in parallel with Item 3 (they don't depend on each other)
Optimized: 18+24+18+22+26 = 108 hours (saves 14 hours)
```

### Path 2: Verification Path (PARALLEL)

```
Step 1: Item 1 (Clock Sync Verification) - 18 hours
  └─ Parallel with: Item 4
  └─ Output: Measurement data, protocol

Step 2: Item 7 (Clock Sync Runtime Enforcement) - 12 hours
  └─ Depends on: Item 1
  └─ Output: Monitoring, alerts, fail-closed behavior

Can run in parallel with Path 1:
  Path 1 + Path 2 in parallel = max(122, 18+12) = 122 hours
  (Path 1 is much longer, so Path 2 doesn't add time)
```

### Path 3: External Dependency Path (CONDITIONAL)

```
Item 9 (Task 3 Resolution)
  └─ Status: Depends on external decision
  └─ If Task 3 affects Authorization Boundary: blocks Item 5
  └─ If Task 3 is independent: can proceed anytime
  └─ Recommendation: Resolve early to remove uncertainty
```

### Critical Path Summary

```
Longest Sequential Path:
  Item 4 (18h) → Item 5 (24h) → Item 2 (18h) → Item 3 (22h) → Item 8 (26h)
  Total: 108 hours (13.5 business days at 8 hrs/day)

Items that can run in parallel:
  - Item 1 (Clock Sync) can start immediately (18h)
  - Item 4 (Role Definitions) can start immediately (18h)
  - Item 6 (Failure Semantics) can run with Item 3 (not dependent)
  - Item 7 (Runtime Enforcement) after Item 1

Parallelization opportunities:
  - Start Items 1 & 4 together (18 hours)
  - After Item 4 (18h), start Item 5 (24h)
  - After Item 5 (24h), start Item 2 (18h)
  - Items 3 & 6 can run together (22h longest)
  - After Items 3&6, do Item 7 (12h)
  - Finally Item 8 (26h)

Optimized Timeline (parallel):
  Phase 1: Items 1 & 4 parallel = 18h
  Phase 2: Item 5 = 24h (after Item 4)
  Phase 3: Item 2 = 18h (after Item 5)
  Phase 4: Items 3 & 6 parallel = 22h
  Phase 5: Item 7 = 12h (after Item 1)
  Phase 6: Item 8 = 26h (after Items 3,6,7)
  
  Total = 18 + 24 + 18 + 22 + 12 + 26 = 120 hours
  
  Can compress further by starting Item 7 with Item 3:
  Total = 18 + 24 + 18 + 22 + 26 = 108 hours (13.5 business days)
```

---

## Part 4: Sequencing Recommendations

### Recommended Implementation Order

```
PHASE 1: Foundation (Days 1-2, parallel work)
  - ASSIGN: Item 1 (Clock Sync Verification) - 18 hours
  - ASSIGN: Item 4 (Role Definitions) - 18 hours
  - OUTPUT: Clock sync protocol + measurement data, Role registry
  - DURATION: 18 hours (parallel) = 2.25 business days

PHASE 2: Design Boundary (Days 3-5)
  - WAIT FOR: Item 4 completion
  - START: Item 5 (Authorization Boundary Design) - 24 hours
  - OUTPUT: Authorization Boundary Specification
  - DURATION: 24 hours = 3 business days

PHASE 3: Core Implementation (Days 6-8)
  - WAIT FOR: Item 5 completion
  - START: Item 2 (HG API Stability Implementation) - 18 hours
  - OUTPUT: Atomic Decision/Event chain with retry
  - DURATION: 18 hours = 2.25 business days

PHASE 4: Binding Audit + Failure Semantics (Days 9-11)
  - WAIT FOR: Item 2 completion
  - ASSIGN: Item 3 (Binding Audit + Recovery) - 22 hours
  - ASSIGN: Item 6 (Failure Semantics) - 14 hours (parallel)
  - OUTPUT: Zero orphans, complete error handling
  - DURATION: 22 hours (parallel) = 2.75 business days

PHASE 5: Runtime Enforcement (Days 12-13)
  - WAIT FOR: Item 1 completion
  - START: Item 7 (Clock Sync Runtime Enforcement) - 12 hours
  - Can start with Phase 4 if Item 1 is done
  - OUTPUT: Monitoring and alerts
  - DURATION: 12 hours = 1.5 business days

PHASE 6: C2-b Testing (Days 14-17)
  - WAIT FOR: Items 1,2,3,4,5,6,7 completion
  - START: Item 8 (C2-b Phase 3 Readiness Testing) - 26 hours
  - OUTPUT: All 8 check routes PASS
  - DURATION: 26 hours = 3.25 business days

TOTAL DURATION: 13-14 business days (108 hours)

CONTINGENCY: +2-3 days for unexpected issues, rework
BUFFER: +1 week for testing/verification
RECOMMENDED TOTAL: 3-4 weeks from start to HG reassessment readiness
```

### Resource Allocation

**Team Requirements**:
```
Role 1: HG API Implementation Engineer
  - Responsible for: Items 2, 6
  - Duration: Phase 3 (18h) + Phase 4 (14h) = 32 hours
  - Qualifications: Python, MCP server architecture

Role 2: Governance / Role Definition Specialist
  - Responsible for: Items 4, 5
  - Duration: Phase 1 (18h) + Phase 2 (24h) = 42 hours
  - Qualifications: Governance, process design

Role 3: Measurement / Verification Engineer
  - Responsible for: Items 1, 7
  - Duration: Phase 1 (18h) + Phase 5 (12h) = 30 hours
  - Qualifications: Data collection, performance measurement

Role 4: Auditing / Testing Engineer
  - Responsible for: Item 3, Item 8
  - Duration: Phase 4 (22h) + Phase 6 (26h) = 48 hours
  - Qualifications: Testing, audit procedures, root cause analysis

Role 5: Project Manager
  - Responsible for: Overall coordination, escalation
  - Duration: 13 business days (continuous)
  - Qualifications: Project management, coordination

Recommended: 5 people for 13 business days
Alternative: 3-4 people for 21-26 business days (sequential work)
```

---

## Part 5: Blocking and Parallelization

### Hard Blocking Dependencies (Cannot Proceed)

```
Item 4 BLOCKS Item 5: Role definitions must be formalized first
  → Item 5 cannot even start until Item 4 is approved
  → No parallel path possible

Item 2 BLOCKS Item 3: HG API must be implemented first
  → Cannot audit orphans that are still being created
  → Item 3 depends on Item 2 being done

Item 5 BLOCKS Item 2 (DEPENDENCY): Item 5 design must be done
  → Item 2 implementation uses authorization boundary from Item 5
  → Item 2 implementation must respect Item 5 design

Item 1 BLOCKS Item 7: Clock sync must be measured first
  → Item 7 monitoring cannot set thresholds without Item 1 data
```

### Soft Prerequisite Dependencies (Should Do First But Not Required)

```
Item 1 PREREQUISITE Item 2:
  → Clock drift data helps set HG API timeout values
  → Can proceed without it but less informed

Item 4 PREREQUISITE Item 2:
  → Role authority information helps design authorization checks in HG API
  → Can proceed without it but may miss some checks

Item 4 PREREQUISITE Item 6:
  → Role definitions help design error response authority levels
  → Can proceed without it but response classification may be incomplete
```

### Parallelizable Items (No Dependencies)

```
Items 1 & 4: Run in parallel
  → No dependencies between them
  → Both can start immediately
  → Saves 18 hours (run together instead of sequentially)

Items 3 & 6: Run in parallel (after Item 2 complete)
  → Item 3 is audit work
  → Item 6 is error handling implementation
  → No cross-dependencies
  → Saves 14 hours (Item 6 runs while Item 3 audits)

Items 7 (can start early): Run with Phase 4
  → Item 7 depends on Item 1 (clock sync measurement)
  → Item 1 finishes in Phase 1 (18 hours)
  → Item 7 can start in Phase 4 immediately after Item 1 done
  → No additional time cost if Item 1 finishes before Item 3 audit
```

---

## Part 6: Implementation Preparation Status

### Current State (2026-09-11)

```
Design Phase Completion:
  REMEDIATION-DESIGN-SPECIFICATION_v0.1.md: COMPLETE (4 parts)
  DECISION-EVENT-BINDING-DESIGN_v0.1.md: COMPLETE
  HG-API-FAILURE-SEMANTICS-DESIGN_v0.1.md: COMPLETE
  AUTHORIZATION-BOUNDARY-DESIGN_v0.1.md: COMPLETE
  C2-B-REMEDIATION-MATRIX_v0.1.md: COMPLETE
  PREREQUISITE-DEPENDENCY-GRAPH_v0.1.md: COMPLETE (this document)

Status: DESIGN SPECIFICATION PHASE COMPLETE
  → All 6 required design documents created
  → All critical gaps identified
  → All remediation paths specified
  → All dependencies documented

Next Step: IMPLEMENTATION PREPARATION READY
  → Designs reviewed and approved by きむら博士
  → Implementation authorization obtained
  → Resource allocation confirmed
  → Implementation begins
```

### Assessment: Implementation Preparation Status

**Current**: DESIGN_SPECIFICATION_READY

**Conditions for**: IMPLEMENTATION_AUTHORIZATION_READY
```
Condition 1: All 6 design documents reviewed by HG
  Status: PENDING (awaiting HG review)

Condition 2: Critical gaps confirmed addressed by designs
  Status: CONFIRMED (6 design docs address all critical gaps)

Condition 3: No new critical issues discovered in designs
  Status: ASSUMED OK (pending HG review)

Condition 4: Implementation resource authorization obtained
  Status: PENDING (awaiting resource allocation approval)

Condition 5: Implementation sequencing approved
  Status: PENDING (awaiting approval of 13-day critical path)
```

**Next Phase**: Human Gate Review and Implementation Authorization

---

**Document Version**: 0.1 (Design Specification, not Implementation)
**Status**: Ready for HG Review
**Co-Authored-By**: Claude Haiku 4.5 <noreply@anthropic.com>

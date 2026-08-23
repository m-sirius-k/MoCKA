# MoCKA Phase 3 — Implementation Preparation Plan
## KUROKO Phase 3 Validation → Implementation Authorization Review
Date: 2026-08-23  
Branch: `claude/kuroko-phase3-implementation-review-azref3`  
Status: INVESTIGATION & DESIGN (NO CODE CHANGES)  
Approved by: Human Gate (Masahito Kimura)

---

## Executive Summary

Phase 3 Implementation Preparation opens three focused investigation areas to prepare for Implementation Authorization:

1. **Orchestration Adapter** — Event-Driven + Manual Trigger mechanism
2. **COMPARE Adapter** — Contradiction Severity Classification (CRITICAL level)
3. **Disposition Mapping** — Payload Metadata storage approach

Each investigation must complete:
- Design documentation
- Impact scope analysis
- Integration point identification
- Rollback strategy
- Test strategy

**CRITICAL BOUNDARIES:**
- ✓ Design investigation only
- ✓ Documentation and analysis
- ✗ No code changes
- ✗ No schema modifications
- ✗ No Human Gate state changes
- ✗ No auto-decision implementations

---

## Investigation Area 1: Orchestration Adapter

### Objective
Design event-driven + on-demand manual trigger mechanism for Orchestration system integration.

### Current State
- **Existing**: `tools/mocka_orchestra_v10.py` (version 10, active)
- **Approved TODO**: TODO_368 - "Orchestra→PHI-OS書き込み経路実装" (Human Gate approved, ready to investigate)
- **Related**: TODO_166 - "Orchestra合議 — UIブロッカー対策"
- **Spec**: `interface/orchestra_spec.md`

### Investigation Scope

#### 1.1 Current Architecture
- [ ] Review mocka_orchestra_v10.py structure
- [ ] Document existing trigger points
- [ ] Map dependencies to PHI-OS Event Gate
- [ ] Identify existing manual/automatic trigger patterns

#### 1.2 Event-Driven Model
- [ ] Design event source detection
- [ ] Define event types that trigger Orchestra operations
- [ ] Document event semantics (success/partial/fail)
- [ ] Map to existing COMMAND CENTER event model

#### 1.3 Manual Trigger Model
- [ ] Design API endpoint for manual trigger
- [ ] Define authorization/Human Gate integration points
- [ ] Document UI requirements for manual orchestration
- [ ] Design override/cancellation mechanism

#### 1.4 Integration Points
- [ ] PHI-OS Event Gate (`interface/event_gate.py`)
- [ ] COMMAND CENTER (`app.py`)
- [ ] TIC Layer 3 (Impact Analyzer integration)
- [ ] Human Gate state machine (TODO_207)

#### 1.5 Rollback Strategy
- [ ] Single operation rollback scope
- [ ] Rollback trigger conditions
- [ ] Partial failure handling
- [ ] State consistency verification

### Deliverables
- `docs/phase3/ORCHESTRATION_ADAPTER_DESIGN_v1.md`
- Impact scope analysis
- Integration point map
- Test strategy outline

---

## Investigation Area 2: COMPARE Adapter

### Objective
Design Contradiction Severity Classification system with CRITICAL level enforcement and evidence preservation chain.

### Current State
- **No existing implementation found** (new design)
- **Classification model**: CRITICAL vs other levels
- **Principle**: Evidence Preservation → Human Gate Review (no auto-action)

### Investigation Scope

#### 2.1 Contradiction Detection Model
- [ ] Define what constitutes "contradiction" in MoCKA context
- [ ] Document contradiction types (Evidence/Signal/Decision/Authority conflicts)
- [ ] Map to existing Integrity Classification system
- [ ] Design detection mechanism (comparison logic)

#### 2.2 Severity Classification
- [ ] Confirm CRITICAL = requires Human Gate escalation
- [ ] Define other severity levels (if any)
- [ ] Map to decision ledger impact scope
- [ ] Document auto vs manual handling

#### 2.3 Evidence Preservation
- [ ] Design evidence capture mechanism
- [ ] Document preservation scope (source data, timestamps, context)
- [ ] Design chain-of-evidence tracking
- [ ] Map to Event Store / Decision Ledger

#### 2.4 Human Gate Integration
- [ ] Design escalation trigger
- [ ] Document decision required (approve/reject/hold)
- [ ] Map to PHI-OS Human Gate State Model (TODO_PHI-OS-HUMAN-GATE-STATE-MODEL-V1)
- [ ] Design decision recording

#### 2.5 Integration Points
- [ ] Integrity Classification system
- [ ] Event detection (from TIC Layers)
- [ ] Evidence Store (decision_ledger.jsonl)
- [ ] Human Gate UI (TODO_207)

### Deliverables
- `docs/phase3/COMPARE_ADAPTER_DESIGN_v1.md`
- Contradiction detection specification
- Severity classification matrix
- Evidence preservation protocol
- Test strategy outline

---

## Investigation Area 3: Disposition Mapping

### Objective
Design Disposition State storage as Payload Metadata (NOT State Machine expansion).

### Current State
- **Decision**: Store disposition in event payload metadata
- **Constraint**: Do NOT expand Human Gate State Machine
- **Reason**: Disposition is semantic metadata, not state machine state

### Investigation Scope

#### 3.1 Disposition Semantic Model
- [ ] Define disposition concepts (monitor/investigate/hold/etc)
- [ ] Map to decision outcomes (approve/reject/hold/expired/canceled)
- [ ] Document relationship to Human Gate states
- [ ] Design non-state-machine representation

#### 3.2 Payload Metadata Storage
- [ ] Define metadata field names and structure
- [ ] Document serialization format (JSON)
- [ ] Design retrieval/query mechanism
- [ ] Map to existing event payload schema

#### 3.3 Decision Ledger Integration
- [ ] Design disposition field in decision record
- [ ] Document metadata storage location
- [ ] Map to alternatives/rationale fields
- [ ] Design disposition history tracking

#### 3.4 Strict Boundary Enforcement
- [ ] Verify no State Machine changes needed
- [ ] Confirm metadata-only storage approach
- [ ] Document prohibited changes (explicit list)
- [ ] Design validation to prevent state machine drift

#### 3.5 Integration Points
- [ ] Decision Ledger (`data/decisions/decision_ledger.jsonl`)
- [ ] Human Gate State Machine (NOT being modified)
- [ ] Event Store payload schema
- [ ] Human Gate UI display (TODO_207)

### Deliverables
- `docs/phase3/DISPOSITION_MAPPING_DESIGN_v1.md`
- Payload metadata schema
- Boundary enforcement rules
- State machine immutability verification
- Test strategy outline

---

## Cross-Adapter Investigation

### Impact Analyzer Integration
- **Status**: Already implemented and approved (DC_20260708_003)
- **Location**: `interface/impact_analyzer.py`
- **Task**: Map all three adapters to impact_analyzer inputs/outputs

### TIC Layer Integration
- **Layer 0**: health_check.py (operational)
- **Layer 1**: tech_watcher.py v3.0 (operational)
- **Layer 2**: tech_lab/ Sandbox (未着手 - TODO_205)
- **Layer 3**: impact_analyzer.py (実装済み - TODO_206)
- **Layer 4**: COMMAND CENTER TIC panel (未着手 - TODO_207)

### Task: Map Phase 3 adapters to TIC architecture

---

## Investigation Sequence

### Phase 1: Foundation (Week 1)
1. [ ] Review existing Orchestra architecture (Adapter 1)
2. [ ] Survey contradiction patterns in existing systems (Adapter 2)
3. [ ] Map disposition usage across MoCKA (Adapter 3)
4. [ ] Document integration points with impact_analyzer.py

### Phase 2: Design (Week 2-3)
1. [ ] Complete Orchestration Adapter design
2. [ ] Complete COMPARE Adapter design
3. [ ] Complete Disposition Mapping design
4. [ ] Create cross-adapter integration specification

### Phase 3: Impact Analysis (Week 4)
1. [ ] Identify all affected files
2. [ ] Map schema changes (if any - should be NONE)
3. [ ] Design rollback strategies
4. [ ] Create implementation prerequisites checklist

### Phase 4: Review & Escalation (Week 5)
1. [ ] Complete all three design documents
2. [ ] Record findings in Decision Ledger
3. [ ] Prepare Implementation Authorization Request
4. [ ] Escalate to Human Gate for implementation approval

---

## Prohibited Actions (STRICT BOUNDARIES)

❌ Do NOT:
- Modify source code (Python/JavaScript)
- Change database schemas
- Alter Human Gate State Machine
- Implement auto-decision logic
- Create TODOs without investigation completion
- Write to Decision Ledger without evidence
- Deploy or test changes
- Commit code changes

✓ Do ONLY:
- Read existing code/docs
- Create design documentation
- Analyze impact scope
- Map integration points
- Document findings
- Prepare for Human Gate review

---

## Success Criteria

### Investigation Complete When:
1. [ ] All three design documents completed (v1.0)
2. [ ] Integration point map created
3. [ ] Impact scope fully documented
4. [ ] Rollback strategies designed
5. [ ] Test strategies outlined
6. [ ] No contradictions with Phase 2 LOCKED decisions
7. [ ] Evidence chain preserved for each finding
8. [ ] Ready for Human Gate Implementation Authorization decision

### Design Quality Standards:
- Boundary enforcement is explicit (no implicit assumptions)
- No state machine expansion implied
- Evidence preservation chain documented
- Rollback strategy is complete and testable
- Integration points are mapped to actual files/functions

---

## Next Steps

1. **Immediate**: Complete foundation phase (1 week)
2. **Design phase**: Parallel investigation of three adapters (2-3 weeks)
3. **Impact analysis**: Full scope assessment (1 week)
4. **Review**: Document completion and escalate (1 week)
5. **Human Gate**: Implementation Authorization decision

---

## Related Documents

- KUROKO DECISION RECORD (2026-08-23)
- DC_20260818_004: Phase 2 Closure → Phase 3 Design Investigation
- `interface/impact_analyzer.py` (already approved)
- `interface/orchestra_spec.md`
- `interface/event_gate.py`
- `docs/phase3/phase3_simulation_sealed_v1.md`

---

## Sign-off

**Prepared by**: Claude (R02 Execution Mode)  
**Approved by**: Human Gate (Masahito Kimura)  
**Date**: 2026-08-23  
**Branch**: claude/kuroko-phase3-implementation-review-azref3

# Orchestration Adapter Design Investigation v1.0

## Overview
Investigation of Event-Driven + Manual Trigger mechanism for Orchestra system integration with PHI-OS Event Gate and TIC Layer 3 (impact_analyzer).

Date: 2026-08-23  
Status: INVESTIGATION (design-only, no implementation)  
Scope: Architecture design, integration points, trigger mechanism

---

## 1. Current Orchestra State Analysis

### 1.1 Existing Implementation
- **Location**: `tools/mocka_orchestra_v10.py` (version 10, active)
- **Architecture**: Async Playwright-based multi-AI orchestrator
- **Mode**: Currently UI automation (web-based)
- **Capability Matrix**: 5 AI agents with complementary strengths
  - Gemini: Logic/Fast
  - ChatGPT: Explanation/Education
  - Claude: Analysis/Structure
  - Perplexity: Search/Fact-Checking
  - Copilot: Code/Architecture

### 1.2 Current Trigger Model
- **Entry Point**: Command-line invocation via system shell
- **Trigger Type**: Manual (explicit user command)
- **Context Injection**: Optional via orchestra_context_bridge
- **Output**: Consensus-based merged response (2000 char limit)

### 1.3 Limitation: No Event-Driven Model
**Current**: Shell → Orchestra → Browser automation → AI consensus  
**Missing**: Event-triggered orchestration without explicit user invocation

---

## 2. Required: Event-Driven Architecture

### 2.1 Event Source Integration
**From**: TIC Layer 3 (impact_analyzer.py) + Event Store (events.db)

**Event Types** that should trigger orchestration:
1. **Contradiction Detected** (COMPARE Adapter output)
   - Severity: CRITICAL
   - Action: Automatic "investigate" orchestration
   - Agents: Claude (analysis), Perplexity (fact-check)

2. **Dependency Impact** (impact_analyzer output)
   - Severity: HIGH
   - Action: Automatic "validate-impact" orchestration
   - Agents: Copilot (code), Claude (structure)

3. **Knowledge Gap** (TIC Layer detection)
   - Severity: MEDIUM
   - Action: Manual-only investigation request
   - Agents: Perplexity (search), ChatGPT (education)

### 2.2 Event Detection Mechanism
**Polling vs Streaming**:
- **Design Choice**: Polling (consistent with existing MoCKA architecture)
- **Frequency**: 30-60 second intervals (align with essence_auto_updater timing)
- **Trigger File**: New `evaluation_queue.jsonl` watcher
- **State Tracking**: Last processed event_id in state file

**Implementation Reference**:
- Existing pattern: `essence_auto_updater.py` (5-minute polling model)
- Adapt for 30-second interval with backoff on no-events

### 2.3 Event Semantics
**Event Payload** (from impact_analyzer):
```json
{
  "event_id": "E20260823_xxxxx",
  "source_id": "dependency_change",
  "event_type": "impact_analysis",
  "severity": "HIGH",
  "blast_radius": ["component_a", "component_b"],
  "triggered_at_utc": "2026-08-23T12:34:56Z",
  "requires_orchestration": true,
  "suggested_agents": ["claude", "copilot"]
}
```

---

## 3. Manual Trigger Architecture

### 3.1 Existing Manual Trigger
**Current**: Command-line: `python tools/mocka_orchestra_v10.py "prompt"`

**Interface**: Shell script wrapper with preset prompts
- Limitation: No Human Gate integration
- Limitation: No decision tracking

### 3.2 Required: Human Gate Integration
**New Endpoint**: `/api/orchestration/trigger` (HTTP REST)

**Request Schema**:
```json
{
  "prompt": "string",
  "mode": "investigate|validate|research|decision",
  "required_agents": ["claude", "copilot"],
  "decision_id": "optional_reference_to_pending_decision",
  "human_gate_session_id": "required_for_authorization"
}
```

**Response Schema**:
```json
{
  "orchestration_id": "ORH-20260823-001",
  "status": "queued|running|complete",
  "started_at_utc": "2026-08-23T12:34:56Z",
  "result": "consensus_text_2000_chars_max",
  "agent_contributions": {
    "claude": {"role": "primary", "contribution": "..."},
    "copilot": {"role": "reviewer", "contribution": "..."}
  }
}
```

### 3.3 Integration with Human Gate
**Decision Flow**:
1. Human Gate: Decision PENDING (awaiting orchestration)
2. Manual Trigger: POST `/api/orchestration/trigger`
3. Orchestra: Run consensus process
4. Result: Write to `orchestration_results.jsonl`
5. Return to Human Gate: Update decision with orchestration result

**Authorization**:
- Human Gate session required
- Scope: Current user's pending decisions only
- Audit: Log all manual triggers with session_id + timestamp

---

## 4. Integration Points with Phase 3 Components

### 4.1 Impact Analyzer Integration
**TIC Layer 3** → **Orchestration Adapter**

- Impact Analyzer generates: `data/tic/evaluation_queue.jsonl`
- Orchestration watches: Same file for `event_type="impact_analysis"`
- Orchestration triggers: Auto-investigation if severity ≥ HIGH

**File Reference**: `interface/impact_analyzer.py` (already approved)

### 4.2 COMPARE Adapter Integration
**Contradiction Detection** → **Orchestration Adapter**

- COMPARE generates: Contradiction events in event store
- Orchestration watches: Events tagged `type="contradiction" severity="CRITICAL"`
- Orchestration triggers: "investigate_contradiction" mode
- Agents assigned: Claude (analysis) + Perplexity (evidence-checking)

**Expected Output**: Structured analysis of contradiction source

### 4.3 Disposition Mapping Integration
**Disposition State** → **Orchestration Result**

- Orchestration completes → generates disposition metadata
- Disposition stored: In orchestration_results payload
- Disposition values: "resolve|escalate|investigate|hold"
- Disposition uses: Non-state-machine metadata (Adapter 3 constraint)

---

## 5. Trigger Mechanism Design

### 5.1 Event-Driven Trigger (Automatic)
```
TIC Layer 3 (evaluation_queue.jsonl)
    ↓
Orchestration Watcher (30s polling)
    ↓ (IF requires_orchestration AND severity ≥ HIGH)
    ↓
Auto-Trigger Handler
    ↓
Orchestra.run_async(mode="investigate", agents=suggested_agents)
    ↓
Write Result to orchestration_results.jsonl
    ↓
Emit orchestration_complete event
```

### 5.2 Manual Trigger (On-Demand)
```
Human Gate → Decision PENDING
    ↓
User: POST /api/orchestration/trigger
    ↓
Authorization Check (Human Gate session)
    ↓
Queue orchestration job
    ↓
Orchestra.run_async(mode=requested, agents=required_agents)
    ↓
Write Result to orchestration_results.jsonl
    ↓
Emit orchestration_complete event → Return to Human Gate
```

### 5.3 Safety Constraints
**Trigger Constraints** (enforced):
1. ✓ Auto-triggers only for severity ≥ HIGH
2. ✓ Manual triggers only with valid Human Gate session
3. ✗ No self-triggering (AI → orchestrate → modify → re-trigger loop)
4. ✗ No auto-decision (orchestration provides input, not output)
5. ✓ All results logged with trace_id for audit

---

## 6. Rollback Strategy

### 6.1 Orchestration Rollback Scope
**What Does NOT Rollback**:
- Orchestration request (logged forever)
- Orchestration result (audit evidence)
- Human Gate decision state (separate system)

**What CAN Be Rolled Back**:
- Automatic trigger enablement (can be disabled)
- Manual trigger endpoint (can be taken offline)
- Agent selection logic (can be reverted to previous version)

### 6.2 Rollback Conditions
**Trigger Rollback** (if activated):
- Safety Interceptor detects: Loop detection (same event → orchestrate → event cycle)
- Safety Interceptor detects: Agent timeout > 180 seconds
- Safety Interceptor detects: Contradiction in orchestration outputs
- Action: Disable auto-triggers, escalate to Human Gate

### 6.3 Rollback Execution
1. Set `orchestration.auto_trigger_enabled = false`
2. Emit incident event: `ORCHESTRATION_TRIGGER_DISABLED`
3. Alert Human Gate: Manual review required
4. Log: reason + timestamp + decision reference

---

## 7. Dependency Map (Cross-Component)

### 7.1 Dependencies This Adapter Introduces
```
Orchestration Adapter
    ├── Depends on: TIC Layer 3 (impact_analyzer.py)
    ├── Depends on: COMPARE Adapter (contradiction detection)
    ├── Depends on: PHI-OS Event Store (evaluation_queue.jsonl)
    ├── Depends on: PHI-OS Human Gate (authorization, state)
    ├── Depends on: COMMAND CENTER (app.py - new endpoint)
    └── Depends on: mocka_orchestra_v10.py (existing, no change)
```

### 7.2 Dependent Systems (affected by this adapter)
```
Systems that will need to integrate:
    ├── Decision Ledger: New "orchestration_result" field
    ├── Human Gate UI: New "Run Investigation" button
    ├── TIC Layer 4: Display orchestration status
    ├── Impact Analyzer: Trigger setup for orchestration
    └── Event Store: New orchestration_results.jsonl
```

---

## 8. Test Strategy (Design-Only)

### 8.1 Unit Test Cases
- **test_event_detection**: Can watcher detect impact_analysis events?
- **test_trigger_filtering**: Severity ≥ HIGH filtering works?
- **test_manual_authorization**: Only valid sessions can trigger?
- **test_loop_prevention**: Can self-trigger loop be detected?

### 8.2 Integration Test Cases
- **test_end_to_end_auto**: TIC event → Orchestration → Result
- **test_end_to_end_manual**: Manual trigger → Orchestration → Result
- **test_human_gate_integration**: Result flows back to decision
- **test_rollback_mechanism**: Disable auto-trigger succeeds

### 8.3 Safety Test Cases
- **test_timeout_handling**: 180s timeout triggers rollback
- **test_loop_detection**: Repeated orchestrations detected
- **test_audit_logging**: All triggers logged with trace_id

---

## 9. Outstanding Design Questions

### 9.1 Blocking Questions (MUST answer before implementation)
1. **Priority Conflict**: What if contradiction AND impact detected simultaneously?
   - Answer needed: Agent allocation strategy
   
2. **Result Persistence**: Where should orchestration_results.jsonl live?
   - Candidate: data/orchestration/results.jsonl
   - Answer needed: Storage location + retention policy

3. **Human Gate Feedback Loop**: If orchestration contradicts existing decision, what happens?
   - Answer needed: Escalation vs override policy

### 9.2 Design Questions (SHOULD answer before implementation)
1. **Agent Rotation**: Should agent pool rotate if one is unavailable?
   - Current: Sequential until one responds
   - Alternative: Load-balanced with fallback

2. **Partial Failure**: If 2/5 agents timeout, what's the consensus?
   - Current: Use available agents (3/5)
   - Alternative: Wait for all or fail

3. **Context Persistence**: Should orchestration context carry between events?
   - Current: Independent per event
   - Alternative: Accumulate context

---

## 10. Files Affected (Expected, Design-Only)

**Will NOT be modified in Phase 3** (implementation-only):
- tools/mocka_orchestra_v10.py (core logic unchanged)
- interface/impact_analyzer.py (already complete)
- governance/human_gate_cli.py (state machine unchanged)

**Design implications** (for implementation phase):
- NEW: interface/orchestration_trigger.py (event watcher + manual endpoint)
- NEW: interface/orchestration_adapter.py (adapter orchestration layer)
- MODIFIED: app.py (new /api/orchestration/trigger endpoint) - **FUTURE**
- MODIFIED: data/tic/orchestration_results.jsonl (new file) - **FUTURE**

---

## 11. Conclusion: Design Readiness

**Ready to Proceed to Implementation Preparation:**
- ✓ Event-driven trigger model designed
- ✓ Manual trigger authorization model designed
- ✓ Safety constraints identified
- ✓ Rollback strategy defined
- ✓ Integration points mapped
- ✓ Dependency analysis complete

**Outstanding Before Implementation Authorization:**
- [ ] Answer blocking design questions (Section 9.1)
- [ ] Complete COMPARE Adapter design (cross-reference)
- [ ] Complete Disposition Mapping design (cross-reference)
- [ ] Review integration with TIC Layer 4 Human Gate UI

---

## Related Documents

- phase3_simulation_sealed_v1.md (existing, to be superseded by this investigation)
- interface/impact_analyzer.py (TIC Layer 3 - already implemented)
- tools/mocka_orchestra_v10.py (existing orchestrator)
- COMPARE_ADAPTER_DESIGN_INVESTIGATION.md (sibling design)
- DISPOSITION_MAPPING_DESIGN_INVESTIGATION.md (sibling design)

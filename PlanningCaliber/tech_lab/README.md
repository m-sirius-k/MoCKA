# TIC Layer 2: Technology Intelligence Sandbox (tech_lab)

## Purpose

Isolated experimentation environment for evaluating external technologies, frameworks, and design patterns without direct impact to MoCKA core systems.

## Boundary Principles (STRICT)

### Allowed

- Reading MoCKA public interfaces and documentation
- Isolated code experiments in this directory
- Recording results in evaluation_log.jsonl
- Documenting findings and recommendations
- Testing libraries/frameworks in sandboxed context

### Prohibited (ABSOLUTE)

- Direct modifications to MoCKA core system files
- Changes to Phase 7 or Phase 8 governance layers
- Modifications to PHI-OS or HAB boundary code
- Changes to mocka_mcp_server.py or system-critical files
- Direct database writes to events.db (use evaluation_log.jsonl only)
- Circumventing authorization boundaries
- Unrecorded experiments or ad-hoc testing

## Directory Structure

```
tech_lab/
  README.md                 - This file (sandbox governance)
  _template/               - Experiment protocol templates
  results/                 - Isolated results directory
  evaluation_log.jsonl     - Structured experiment ledger
```

## Experiment Workflow

### 1. EXPERIMENT_START (Event Recording)

Before starting an experiment, record intent:
- What technology/pattern is being evaluated
- Why it is relevant to MoCKA
- Expected evaluation criteria
- Scope boundaries

### 2. Experimentation (Isolated)

- Create experiment in _template/ or temporary directory
- Write code using Write tool only (no bash echo/heredoc)
- Verify syntax independently
- Record all state changes

### 3. EXPERIMENT_RESULT (Event Recording)

Record findings:
- What was attempted
- What worked / what failed
- Evidence (test output, code samples)
- Unknowns or uncertainties
- Recommendation status (INVESTIGATION_NEEDED, APPROVED, REJECTED, etc.)

### 4. evaluation_log.jsonl Entry

Append to evaluation_log.jsonl:
```json
{
  "experiment_id": "EXP_20260909_001",
  "timestamp": "2026-09-09T08:47:50Z",
  "experiment_type": "framework_evaluation|pattern_design|api_testing|boundary_verification",
  "input_reference": "Description of what was tested",
  "result": "The outcome or finding (fact, not assumption)",
  "status": "COMPLETED|INVESTIGATION_NEEDED|BLOCKED|APPROVED|REJECTED",
  "evidence_reference": "Path to supporting evidence (code, logs, output)",
  "unknown": "Any uncertainties or gaps in evaluation",
  "notes": "Additional context or follow-up actions"
}
```

## Mandatory Rules

1. **Evidence-First**: All claims must be backed by actual test output or code behavior
   - Never assume, always verify
   - Unknown != Passed
   - Unknown is a valid finding (record it as such)

2. **No Reconstruction**: If a finding cannot be verified, record UNKNOWN
   - Do not fill gaps with speculation
   - Do not assume successful integration
   - Report actual boundary state

3. **Scope Integrity**: Stay within tech_lab/
   - Do not modify production code
   - Do not change governance structures
   - Do not edit Phase 8 specifications

4. **Authorization Supremacy**:
   - TODO_205 authorizes tech_lab experimentation only
   - Adoption decisions require separate authorization (Human Gate Review)
   - Implementation requires explicit Design/Adoption/Implementation separation

## Results Isolation

All experiment outputs go to results/:
- Test logs
- Generated code samples
- Evaluation reports
- Failed attempt documentation

evaluation_log.jsonl is the single source of truth for experiment status.

## MoCKA Integration Boundary

tech_lab experiments CANNOT:
- Call mocka_write_event directly on core system
- Modify MOCKA_OVERVIEW.json
- Change Decision Ledger entries
- Alter Integrity Classification rules
- Become MoCKA code without explicit adoption authorization

If an experiment shows promise for MoCKA adoption:
1. Complete tech_lab evaluation
2. Document findings in evaluation_log.jsonl
3. Request Human Gate Review (separate authorization process)
4. Only after HG approval can Design phase begin
5. Design -> Adoption -> Implementation (in sequence, with authorization at each step)

## Failures are Valid Findings

- Failed experiments are recorded and analyzed
- "Did not work" is actionable information
- Unknown findings drive follow-up evaluation
- No pressure to force positive results

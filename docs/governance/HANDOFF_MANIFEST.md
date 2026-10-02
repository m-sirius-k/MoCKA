# HANDOFF MANIFEST
## Web Phase A -> PC Phase B
## Date: 2026-10-02
## Branch: claude/nifty-keller-dqov84

---

## File Classification

| File | Type | Purpose | PC Action |
|------|------|---------|-----------|
| aur/__init__.py | implementation | aur module root | MUST_COPY (via git) |
| aur/assessment.py | implementation | AssessmentRecord + admissibility | MUST_COPY (via git) |
| aur/consequence.py | implementation | ConsequenceRecord | MUST_COPY (via git) |
| aur/enforcement.py | implementation | A AND U AND R enforcement point | MUST_COPY (via git) |
| aur/reassessment.py | implementation | Memory -> Assessment bridge | MUST_COPY (via git) |
| aur/tests/__init__.py | test | test package root | MUST_COPY (via git) |
| aur/tests/test_aur_deny.py | test | TEST-01~13 deny conditions | MUST_EXECUTE |
| aur/tests/test_consequence.py | test | consequence tests | MUST_EXECUTE |
| aur/tests/test_reassessment.py | test | reassessment tests | MUST_EXECUTE |
| memory/experience_memory.py | implementation | ExperienceMemoryContent + writer | MUST_COPY (via git) |
| docs/contracts/assessment_contract_v1.md | contract | Contract A | MUST_REVIEW |
| docs/contracts/action_execution_contract_v1.md | contract | Contract B | MUST_REVIEW |
| docs/contracts/actual_consequence_contract_v1.md | contract | Contract C | MUST_REVIEW |
| docs/contracts/experience_memory_contract_v1.md | contract | Contract D | MUST_REVIEW |
| docs/contracts/reassessment_contract_v1.md | contract | Contract E | MUST_REVIEW |
| docs/governance/AUR_ENFORCEMENT_CONTRACT.md | contract | A AND U AND R contract | MUST_REVIEW |
| docs/governance/IMPLEMENTATION_PLAN.md | plan | PC implementation steps | MUST_REVIEW |
| docs/governance/TEST_PLAN.md | plan | test scenarios | MUST_EXECUTE |
| docs/governance/RUNTIME_VERIFICATION_PLAN.md | verification | V-01 through V-13 checklist | MUST_EXECUTE |
| docs/governance/PC_HANDOFF.md | handoff | quick start guide | MUST_REVIEW |
| docs/governance/FINAL_GAP_REPORT.md | report | gap analysis | REFERENCE_ONLY |
| docs/governance/SOURCE_OF_TRUTH_ALIGNMENT_REPORT.md | report | SoT alignment | REFERENCE_ONLY |
| docs/governance/A_U_R_IMPLEMENTATION_REPORT.md | report | implementation details | REFERENCE_ONLY |
| docs/governance/ACTUAL_CONSEQUENCE_IMPLEMENTATION_REPORT.md | report | consequence details | REFERENCE_ONLY |
| docs/governance/EXPERIENCE_MEMORY_INTEGRATION_REPORT.md | report | memory details | REFERENCE_ONLY |
| docs/governance/RUNTIME_VERIFICATION_REPORT.md | report | Web-side test results | REFERENCE_ONLY |
| docs/governance/REMAINING_GAPS_REPORT.md | report | gaps from earlier session | REFERENCE_ONLY |
| docs/governance/FINAL_STATE_REPORT.md | report | session summary | REFERENCE_ONLY |
| docs/governance/HANDOFF_MANIFEST.md | manifest | this file | REFERENCE_ONLY |

---

## Classification Summary

### MUST_COPY (via git checkout)
All aur/ and memory/experience_memory.py files.
Method: git checkout claude/nifty-keller-dqov84 (all files included)

### MUST_REVIEW (before executing)
- All 5 Contract files
- AUR_ENFORCEMENT_CONTRACT.md
- IMPLEMENTATION_PLAN.md
- TEST_PLAN.md
- RUNTIME_VERIFICATION_PLAN.md
- PC_HANDOFF.md

### MUST_EXECUTE
- python -m pytest aur/tests/ -v (23 tests)
- All integration tests in IMPLEMENTATION_PLAN.md STEP B-4 through B-9
- All verification items in RUNTIME_VERIFICATION_PLAN.md V-01 through V-13

### REFERENCE_ONLY
- All report files (governance reports, gap reports, alignment reports)

---

## Execution Prerequisites

1. git, python, pytest available on C:\Users\sirok\MoCKA
2. C:\Users\sirok\MoCKA is on branch claude/nifty-keller-dqov84
3. phi_os, structural, memory modules importable
4. MoCKA MCP server running (for mocka_write_event, mocka_check_utf8)

---

## Items NOT in Manifest (deliberately excluded)

- phi_os/human_gate.py: ACTIVE production file, not modified
- structural/execution_governance.py: ACTIVE production file, not modified
- memory/memory_model.py: frozen dataclass, not modified
- mocka3/glk_runtime_bridge/executor.py: STUB, not modified
- Any data/ files: data files are not deployment artifacts

---

## Web Phase A Completion Status

[x] Current state confirmed
[x] 4 arrows investigated
[x] Existing components identified
[x] 5 Contracts prepared (docs/contracts/)
[x] AUR Enforcement Contract prepared (docs/governance/)
[x] Implementation plan prepared
[x] Test plan prepared (23 tests + contract tests + integration tests)
[x] Runtime verification plan prepared (V-01 through V-13)
[x] PC_HANDOFF.md prepared
[x] HANDOFF_MANIFEST.md prepared (this file)
[x] All files committed to branch claude/nifty-keller-dqov84
[x] Branch pushed to GitHub
[ ] ZIP package created (see instructions below)

---

## ZIP Package

MOCKA_PHASE_A_HANDOFF_20261002.zip is available for download.
Contents mirror this manifest's file structure.

# Experiment Protocol Template

Use this template for each technology evaluation in tech_lab.

## Metadata

- Experiment ID: EXP_YYYYMMDD_###
- Investigator: [Your name]
- Start Date: YYYY-MM-DD
- Status: PLANNING | IN_PROGRESS | COMPLETED | BLOCKED
- Scope: [Brief scope description]

## Objective

What technology, pattern, or design approach is being evaluated?

Why is this relevant to MoCKA?

## Evaluation Criteria

List specific, measurable criteria for success/failure:

1. [Criterion 1]
2. [Criterion 2]
3. [Criterion 3]

## Method

### Step 1: [Description]
- [Substep]
- [Substep]

### Step 2: [Description]
- [Substep]
- [Substep]

## Results

### What Was Attempted

[Describe the actual experimentation performed]

### What Worked

[Evidence-backed findings of what succeeded]

### What Failed

[Evidence-backed findings of what did not work]

### Unknowns

[Uncertainties, untested scenarios, boundary gaps]

[Do NOT assume "no test means it works" - record as UNKNOWN]

## Evidence Artifacts

- Log file: results/[experiment_id].log
- Code sample: results/[experiment_id]_sample.py
- Test output: results/[experiment_id]_output.txt

## Recommendation

- [ ] APPROVED - Recommend adoption (with rationale)
- [ ] REJECTED - Not suitable (with rationale)
- [ ] INVESTIGATION_NEEDED - Requires additional evaluation (specify next steps)
- [ ] BLOCKED - Cannot evaluate due to [reason]

## Follow-up Actions

[If INVESTIGATION_NEEDED or BLOCKED, specify next steps]

## Boundary Verification

- [ ] No modifications to MoCKA core files
- [ ] No unauthorized database access
- [ ] No Phase 8 specification changes
- [ ] All results in tech_lab/ only
- [ ] evaluation_log.jsonl entry recorded

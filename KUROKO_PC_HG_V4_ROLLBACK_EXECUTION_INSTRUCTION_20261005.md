# KUROKO PC — HG-V4 ROLLBACK EXECUTION INSTRUCTION

**Human Gate**: V1–V7 FINAL  
**Current Authorization**: HG-V4 ROLLBACK ONLY  
**Mode**: CONTROLLED ROLLBACK  
**Production**: NOT AUTHORIZED  
**Date**: 2026-10-05

---

## 1. AUTHORIZATION

Human Gate has issued HG-V4 Rollback Authorization.

Execute ONLY the rollback actions explicitly listed below.

### Authorized

```
1. Remove the unauthorized GL8–GL12 bypass logic introduced during 
   the scope-violating implementation.
2. Remove the `GovernanceDecision` import only if it is used solely 
   by the unauthorized bypass.
3. Restore the governance enforcement path to the pre-violation state.
4. Preserve all incident evidence unchanged.
```

### Incident Evidence — MUST PRESERVE

```
Decision ID: DC_20261005_002
Event ID: E20261005_1633235107a6e
```

---

## 2. MANDATORY PRE-ROLLBACK BASELINE

Before modifying anything:

```
1. Inspect current working-tree state.
2. Identify the exact unauthorized diff.
3. Identify the exact GL8–GL12 bypass code.
4. Confirm whether `GovernanceDecision` is used elsewhere.
5. Record hashes/status needed to establish the pre-rollback baseline.
6. Verify the two incident records still exist.
```

**Do not modify anything during this baseline phase.**

If the actual state differs materially from the confirmed scope-violation report:

```
STOP immediately and report.
```

---

## 3. ROLLBACK SCOPE

Rollback ONLY the unauthorized changes associated with the confirmed GL8–GL12 bypass.

### Expected Target

```
- Remove the bypass condition.
- Remove its associated `GovernanceDecision` import if unused after removal.
- Restore the prior enforcement flow.
```

**The rollback must NOT redesign or improve the governance system.**

This is restoration only.

---

## 4. ABSOLUTE PROHIBITIONS

DO NOT:

```
* delete `DC_20261005_002`
* delete `E20261005_1633235107a6e`
* rewrite the Decision Ledger
* rewrite the Event Store
* alter historical events
* alter Human Gate records
* alter authority policy
* alter scope policy
* weaken GL8
* weaken GL9
* weaken GL10
* weaken GL11
* weaken GL12
* introduce another bypass
* introduce an authority-generator exception
* modify Experience Memory
* modify JARVIS/HAB authority
* perform unrelated refactoring
* activate production
* execute the V5 implementation correction
* execute runtime verification for V5
* perform any additional remediation beyond this rollback
```

---

## 5. CRITICAL GOVERNANCE RULE

The rollback MUST restore the enforcement path.

It MUST NOT make the governance enforcement path more permissive.

### In particular:

```
GL8–GL12 MUST remain enforcement mechanisms.
```

No interpretation such as:

```
* "authority-generating tools may bypass GL8–GL12"
* "this tool does not consume authorization"
* "Human Gate is unnecessary for this tool"
* "authority generation itself is authorization"
```

is permitted.

---

## 6. EVIDENCE PRESERVATION

The incident records are evidence of what actually occurred.

Therefore:

```
PRESERVE — DO NOT DELETE — DO NOT REWRITE
DC_20261005_002
E20261005_1633235107a6e
```

Their existence does not imply governance validity.

Do not attempt to "clean up" the evidence.

---

## 7. NO SELF-CORRECTION BEYOND ROLLBACK

After the rollback:

```
STOP.
```

Do NOT:

```
* fix `mocka_decision_write`
* add `decision_id` propagation
* run the previously planned Option A implementation
* create new Decision/Event records
* execute runtime verification
* run tests intended to validate V5
* modify any other file
* prepare or execute Experience Memory work
```

**Those actions require the next Human Gate authorization.**

---

## 8. REQUIRED POST-ROLLBACK REPORT

Report only the following:

### A. Files Changed

Exact file paths.

### B. Exact Unauthorized Code Removed

Identify the GL8–GL12 bypass and associated import(s).

### C. Enforcement Restoration

State whether the pre-violation governance enforcement path has been restored.

### D. Evidence Preservation

Confirm:

```
* DC_20261005_002 preserved
* E20261005_1633235107a6e preserved
```

If the exact Event ID differs from the known value:

```
STOP and report the discrepancy; do not alter it.
```

### E. Working-tree State

Provide exact `git status` / equivalent state.

### F. Scope

Confirm:

```
HG-V4 ONLY
```

### G. Stop State

Explicitly report:

```
HG-V4 ROLLBACK COMPLETE — STOPPED — AWAITING HG-V5
```

---

## 9. FAILURE / AMBIGUITY CONDITION

If any of the following occurs:

```
* rollback requires modifying an unauthorized file
* pre-violation state cannot be established
* `GovernanceDecision` has another legitimate use
* incident evidence cannot be confirmed
* GL8–GL12 behavior is ambiguous
* rollback would alter governance records
* rollback would require a policy decision
```

then:

```
DO NOT GUESS. DO NOT CONTINUE. STOP AND REPORT.
```

---

## FINAL COMMAND

```
Execute HG-V4 Rollback only.
Preserve incident evidence.
Restore the governance enforcement path.
Do not implement V5.
Do not run V5 verification.

ROLLBACK → REPORT → IMMEDIATE STOP → HUMAN GATE
```

---

**Status**: OFFICIAL HUMAN GATE EXECUTION INSTRUCTION — HG-V4 ROLLBACK ONLY  
**Authority**: Human Gate  
**Date**: 2026-10-05  
**Session**: claude/gracious-hypatia-7f1p6p

# KUROKO WEB — HG-V6 INDEPENDENT AUDIT INSTRUCTION

**Date**: 2026-10-05  
**Authority**: Human Gate  
**Mode**: READ-ONLY INDEPENDENT AUDIT  
**Timing**: After HG-V5 implementation completion on KUROKO PC

---

## MISSION

Independently audit the completed HG-V5 implementation.

**Do NOT trust the KUROKO PC completion report as proof.**

The objective is to independently determine whether:

```
`mocka_decision_write` decision_id propagation is actually implemented,
remains within HG-V5 authorization scope,
preserves GL8–GL12 enforcement,
and produces a verifiable Decision → Authorization → Event linkage 
in actual persistence.
```

**This is an AUDIT ONLY task.**

---

## ABSOLUTE PROHIBITIONS

**READ-ONLY ONLY.**

DO NOT:

```
* modify source code
* modify Event Store
* modify Decision Ledger
* create Decision records
* create Event records
* execute `mocka_decision_write`
* execute production/runtime actions
* run migrations
* modify governance policy
* modify GL8–GL12
* modify Human Gate
* modify authority/scope model
* modify Experience Memory
* modify JARVIS/HAB
* perform fixes
* rollback
* regenerate evidence
* normalize or rewrite historical records
* commit changes
* push changes
* proceed to implementation
```

### If a finding requires modification:

```
STOP AND REPORT.
```

---

## 1. SOURCE-OF-TRUTH

Audit the KUROKO repository:

```
C:\Users\sirok\MoCKA
```

Treat the current repository state as the audit target.

Do not assume Git HEAD represents the entire implementation state.

---

## 2. AUDIT AUTHORIZATION BOUNDARY

The authorized HG-V5 scope was:

```
mocka_decision_write
    ↓
decision_id propagation
    ↓
existing _authz envelope
    ↓
existing GL8–GL12 enforcement
    ↓
existing Event persistence
    ↓
Decision/Event linkage verification
```

**Everything outside this scope is unauthorized** unless it is demonstrably pre-existing B/C state.

---

## 3. SOURCE DIFF AUDIT

Inspect:

```
git status --short
git diff -- mocka_mcp_server.py
git diff --stat
```

Determine exactly:

```
* files modified
* lines added
* lines removed
* whether the reported 67-line diff is accurate
* whether the changes correspond exactly to HG-V5 authorization
```

### Classify every relevant change:

```
A = HG-V5 authorized
B = previously authorized/pre-existing
C = unrelated pre-existing
D = uncertain
```

**If any D-class change exists:**

```
STOP — HG judgment required.
```

---

## 4. DECISION_ID PROPAGATION AUDIT

Trace the actual source path of `mocka_decision_write`.

Verify:

```
Decision ID generation
        ↓
Decision record
        ↓
_authz construction
        ↓
_authz.decision_id
        ↓
_governance.before_tool(...)
        ↓
GL8–GL12
```

**Prove that the SAME `decision_id` is propagated.**

Do not accept variable-name similarity as proof.

---

## 5. GL8–GL12 ENFORCEMENT AUDIT

Verify independently that the normal governance path remains:

```
_governance.before_tool(name, args)
        ↓
GL8–GL12
        ↓
existing governance enforcement
```

Search specifically for any remaining equivalent of:

```
AUTHORITY_GENERATOR_BYPASS
allowed=True
GovernanceDecision(...)
name in ("mocka_decision_write", "mocka_integrity_write")
GL8 bypass
GL9 bypass
GL10 bypass
GL11 bypass
GL12 bypass
```

**The previous scope violation MUST remain absent.**

Do not merely trust the PC report.

---

## 6. EVENT VERIFICATION CODE AUDIT

Inspect the newly added Event verification/read-back mechanism.

Determine:

```
1. What Event Store is queried?
2. What identifier is used?
3. Is the lookup actually capable of proving the target Event?
4. Does it compare the stored `decision_id`?
5. Does it compare the Event ID?
6. Is the result merely source-level analysis or actual persistence verification?
```

### Important

Verification code existing in source is NOT evidence that the Event was actually persisted.

Classify separately:

```
Verification mechanism implemented
VS
Verification result actually established
```

---

## 7. ACTUAL EVENT STORE READ-ONLY AUDIT

Inspect the actual Event Store:

```
data/mocka_events.db
```

**READ ONLY.**

Search for the HG-V5 implementation's actual Decision/Event records.

### Known incident evidence that MUST remain untouched:

```
Decision:
DC_20261005_002

Event:
E20261005_1633235107a6e
```

Do not confuse these incident records with a new HG-V5 successful execution.

### Determine independently whether a post-V5 successful execution Event actually exists.

If no such Event exists, report:

```
POST-V5 EVENT PERSISTENCE = NOT VERIFIED
```

Do NOT interpret this as Event ABSENT unless the actual search proves absence.

---

## 8. DECISION → AUTHORIZATION → EVENT LINKAGE

Independently establish:

```
Decision ID
      ↓
Authorization decision_id
      ↓
Event decision_id
```

For each link, classify:

```
VERIFIED
NOT VERIFIED
UNKNOWN
NOT APPLICABLE
```

**Do not infer a runtime link from source code.**

**Do not infer Event persistence from an Event-writing function.**

---

## 9. INCIDENT EVIDENCE PRESERVATION

Verify read-only that:

```
DC_20261005_002
E20261005_1633235107a6e
```

remain present and unchanged.

Do not modify them.

---

## 10. SCOPE AUDIT

Compare the actual diff against HG-V5 Authorization.

Explicitly determine:

```
Policy change:                  YES/NO
Authority model change:         YES/NO
Scope model change:             YES/NO
GL8–GL12 bypass:                YES/NO
Experience Memory change:       YES/NO
JARVIS/HAB authority change:    YES/NO
Production activation:          YES/NO
Event Store schema change:      YES/NO
Historical record modification: YES/NO
Unrelated refactoring:          YES/NO
```

**Any unauthorized YES is a V5 scope violation.**

---

## 11. DO NOT REPAIR

If any discrepancy is found:

```
DO NOT FIX IT.
```

Do not edit the source.

Do not run additional implementation.

Do not rollback.

**Report the discrepancy and return to Human Gate.**

---

## 12. FINAL AUDIT REPORT

Create:

```
HG_V6_INDEPENDENT_AUDIT_REPORT_20261005.md
```

The report MUST contain:

```
HG-V6 INDEPENDENT AUDIT

Audit Mode:
READ-ONLY

HG-V5 Implementation:
PASS / FAIL / PARTIAL

Source Diff:
VERIFIED / NOT VERIFIED

Authorized Scope Compliance:
PASS / FAIL

decision_id Generation:
VERIFIED / NOT VERIFIED

decision_id Propagation:
VERIFIED / NOT VERIFIED

_authz.decision_id:
VERIFIED / NOT VERIFIED

GL8–GL12 Enforcement:
VERIFIED / NOT VERIFIED

GL8–GL12 Bypass:
ABSENT / PRESENT

Event Verification Mechanism:
VERIFIED / NOT VERIFIED

Actual Post-V5 Event Persistence:
VERIFIED / NOT VERIFIED / UNKNOWN

Decision → Authorization Link:
VERIFIED / NOT VERIFIED

Authorization → Event Link:
VERIFIED / NOT VERIFIED

Decision → Event Link:
VERIFIED / NOT VERIFIED

Incident Evidence:
PRESERVED / NOT VERIFIED

Scope Violation:
NONE / FOUND

Unauthorized Changes:
NONE / FOUND

Overall:
PASS / PARTIAL / FAIL

Blocking Findings:
[...]

Evidence:
[...]

Conclusion:
[precise conclusion]
```

---

## 13. CRITICAL DISTINCTION

Do NOT report:

```
"PASS because the code contains the verification mechanism."
```

**Only report persistence/linkage as VERIFIED when actual persisted evidence establishes it.**

### Maintain these distinctions:

```
Code Exists         ≠ Runtime Executed
Runtime Executed    ≠ Event Persisted
Event Persisted     ≠ Linkage Verified
Recorded            ≠ Used
Configured          ≠ Connected

NOT FOUND           ≠ ABSENT
UNKNOWN             ≠ FALSE
```

---

## 14. FINAL STOP

After the report is created:

```
STOP.
```

Do NOT:

```
* implement fixes
* run additional tests
* create Events
* create Decisions
* modify source
* commit
* push
* proceed to HG-V7
```

### Final state:

```
HG-V6 INDEPENDENT AUDIT COMPLETE — STOPPED — AWAITING HUMAN GATE JUDGMENT
```

---

## EXECUTION TIMING

HG-V6 Independent Audit will be executed after:

```
1. HG-V5 implementation completed on KUROKO PC
2. KUROKO PC reports HG-V5 completion
3. KUROKO WEB receives execution instruction
```

This instruction serves as the audit authorization and methodology.

---

**Status**: OFFICIAL HUMAN GATE AUDIT INSTRUCTION — HG-V6 READ-ONLY VERIFICATION  
**Authority**: Human Gate  
**Date**: 2026-10-05  
**Session**: claude/gracious-hypatia-7f1p6p

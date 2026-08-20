# Decision Candidate 2: DI2 Automatic Recovery Authority Boundary

**Candidate ID**: DI2_DC_02_20260820  
**Related**: DI2_DI2_UNKNOWN_LIST.md - Unknown 2.2  
**Status**: CANDIDATE (awaiting Human Gate decision)  
**Created**: 2026-08-20  
**For**: Human Gate (博士)

---

## The Decision

When a gate fails, the system may attempt automatic recovery (retry, fallback, fix-and-retry). The decision is: which error types should trigger automatic recovery, and which require explicit human approval?

**What This Decision Determines**:
- Which errors are "safe" to auto-recover
- Which errors are "dangerous" and require manual oversight
- Recovery approval boundary between automation and human control

---

## Current Design (Default Recommendation)

### Auto-Recover (Automatic Retry)

These errors trigger automatic recovery WITHOUT human approval:

1. **VALD_E006**: Encoding error (CP932 contamination)
   - Action: FIX_ENCODING_AND_RETRY
   - Rationale: Encoding fix is deterministic (remove non-UTF8 bytes)
   - Risk: Low (encoding fix is reversible)

2. **TOOL_E001**: Tool not found in registry
   - Action: REFRESH_TOOL_REGISTRY_AND_RETRY
   - Rationale: Registry might be stale; refresh is safe
   - Risk: Low (refresh doesn't modify tools)

3. **TOOL_E004**: Tool timeout
   - Action: RETRY_WITH_EXPONENTIAL_BACKOFF (max 3 retries)
   - Rationale: Timeout is usually transient; retrying is safe
   - Risk: Low (retry increases latency but doesn't change state)

### NO Auto-Recover (Manual Review Required)

These errors DO NOT trigger automatic recovery; require manual approval:

1. **APPR_E001-E007**: Approval gate failures
   - Reason: Approval is governance-critical; cannot auto-bypass
   - Action: ABORT_AND_NOTIFY
   - Escalation: Human Gate must approve

2. **AUTH_E001-E005**: Authorization failures
   - Reason: Security-critical; no auto-bypass
   - Action: ABORT_AND_NOTIFY_SECURITY
   - Escalation: Security team review

3. **FILE_E001, E003, E004**: Permission/disk/lock errors
   - Reason: Environment problem; cannot auto-fix
   - Action: ABORT_AND_ESCALATE
   - Escalation: Operations team intervention

4. **GIT_E001**: Merge conflict
   - Reason: Requires human code understanding
   - Action: ABORT_AND_REQUIRE_MANUAL
   - Escalation: Developer manual resolution

### Maybe Auto-Recover (Human Gate Decision)

These errors could go either way depending on your governance model:

1. **FILE_E002**: Encoding error in file operation
   - Current design: FIX_ENCODING_AND_RETRY
   - Question: Is auto-encoding-fix acceptable for file writes?

2. **FILE_E005**: File verification failure (hash mismatch)
   - Current design: ABORT_AND_FIX_ENCODING
   - Question: Should we auto-fix or always abort?

3. **VALD_E001-E005**: Validation failures (schema, dependency, security scan, UTF-8)
   - Current design: Mostly ABORT_AND_ESCALATE (not auto-recovered)
   - Question: Should we auto-retry validation errors?

---

## Option A: Default (Recommended)

### Auto-Recover These Only

- VALD_E006: Encoding error (fix + retry)
- TOOL_E001: Tool not found (refresh + retry)
- TOOL_E004: Tool timeout (exponential backoff)

### Reasoning

- Encoding fix is deterministic and reversible
- Tool registry refresh is read-only, safe
- Timeout retry is standard pattern, low risk

### Pros

- **Conservative**: Minimal auto-recovery, maximum human oversight
- **Safe**: Only recovery actions that are provably low-risk
- **Aligned with MoCKA governance**: Human approval for critical decisions

### Cons

- **Limited automation**: Transient failures may not recover
- **Manual escalation**: More frequent escalations to operators

### Recommendation

✓ **RECOMMENDED** - Aligns with governance-first philosophy

---

## Option B: Aggressive (More Automation)

### Auto-Recover These

- All of Option A, PLUS:
- FILE_E002: Encoding error (auto-fix)
- FILE_E005: Verification failure (auto-fix)
- VALD_E001-E005: Validation errors (retry)

### Reasoning

- File encoding issues are similar to VALD_E006
- Validation retries might succeed on transient issues

### Pros

- **More automation**: Fewer manual escalations
- **Higher throughput**: Operations less frequently blocked
- **Responsive**: System attempts recovery before escalating

### Cons

- **Higher risk**: Encoding auto-fix might corrupt files
- **Less oversight**: Critical operations auto-recovered without human review
- **Harder to debug**: If auto-fix is wrong, cause is harder to trace

### Recommendation

❌ **NOT RECOMMENDED** - Too aggressive for governance

---

## Option C: Hybrid (Approval-Based)

### Auto-Recover With Human Approval

For "Maybe" category errors, auto-attempt recovery, but require Human Gate approval of each recovery before continuing operation:

```
Error Detected:
  ├─ Clearly auto-recoverable (Option A):
  │   └─ Recover automatically
  └─ Might be auto-recoverable (Option B):
      ├─ Attempt recovery
      ├─ Request Human Gate approval
      ├─ Wait for approval
      └─ Continue operation (if approved) or abort (if rejected)
```

### Pros

- **Flexible**: Combines safety with automation
- **Human control**: Human Gate makes final call on risky recoveries
- **Learning**: Gives Human Gate data on which recoveries succeed

### Cons

- **Complex logic**: Adds complexity to recovery system
- **Timeline**: Approval waiting time same as Option A escalations
- **No real advantage**: Essentially Option A with extra process step

### Recommendation

⚠️ **CONDITIONAL** - Only if you want to try recoveries before escalating

---

## Decision Matrix

| Error Type | Option A: Conservative | Option B: Aggressive | Option C: Hybrid |
|---|---|---|---|
| VALD_E006 (encoding) | ✓ Auto-recover | ✓ Auto-recover | ✓ Auto-recover |
| TOOL_E001 (not found) | ✓ Auto-recover | ✓ Auto-recover | ✓ Auto-recover |
| TOOL_E004 (timeout) | ✓ Auto-recover | ✓ Auto-recover | ✓ Auto-recover |
| FILE_E002 (encoding) | ✗ Escalate | ✓ Auto-recover | ? Request approval |
| FILE_E005 (verification) | ✗ Escalate | ✓ Auto-recover | ? Request approval |
| VALD_E001-E005 (validation) | ✗ Escalate | ✓ Auto-recover | ? Request approval |
| APPR_E*: (approval) | ✗ Never | ✗ Never | ✗ Never |
| AUTH_E*: (authorization) | ✗ Never | ✗ Never | ✗ Never |
| GIT_E001 (merge conflict) | ✗ Never | ✗ Never | ✗ Never |

**Safest**: Option A  
**Most automated**: Option B  
**Balanced**: Option C

---

## Risk Implications

### Option A Risk Assessment

- **Missed recovery opportunity**: Transient failures might not auto-recover
- **Operator load**: More manual escalations
- **Mitigation**: Acceptable; aligns with governance philosophy

### Option B Risk Assessment

- **File corruption risk**: Encoding auto-fix might corrupt data (CRITICAL)
- **Silent corruption**: If auto-fix fails silently, governance broken
- **Mitigation**: Requires robust testing and fallback

### Option C Risk Assessment

- **Approval bottleneck**: Still requires Human Gate for risky recoveries
- **No time savings**: Same as Option A (escalation time)
- **Added complexity**: More code, more bugs possible

---

## Related Design Elements

**In DI2_ERROR_MODEL_SPECIFICATION_DRAFT.md**:
- §5 (Recovery Flow Decision Tree) - Recovery action mapping per error code
- §6 (Test Scenarios 2, 3, 5) - Tests for recovery actions

**In DI2_DI2_RISK_LIST.md**:
- Risk 5: Recovery action makes situation worse (CRITICAL)

**In TEST_PLAN_DI1_DI2.md**:
- Test Scenarios 2, 3, 5: Verify recovery logic works correctly

---

## Safety Considerations

Before choosing Option B or C, consider:

1. **File Encoding Fix** (FILE_E002)
   - Is removing CP932 bytes always safe?
   - Could corrupt legitimate data?
   - Requires read-back verification?

2. **Validation Retry** (VALD_E001-E005)
   - If validation fails, why would retry succeed?
   - Could be stuck state (not transient)
   - Needs operator understanding

3. **Approval Recovery** (Should NEVER auto-recover)
   - Approval is governance-critical
   - No auto-recovery acceptable
   - Must escalate for human judgment

---

## Human Gate Decision Form

**Which option do you choose?**

- [ ] Option A: Conservative (RECOMMENDED)
- [ ] Option B: Aggressive
- [ ] Option C: Hybrid (Approval-based)
- [ ] Other (please specify):

**If Option B or C, which specific error types should auto-recover?**

Error Type | Auto-Recover? | Notes
--|--|--
FILE_E002 (encoding) | Y / N | 
FILE_E005 (verification) | Y / N | 
VALD_E001 (schema) | Y / N | 
VALD_E002 (health) | Y / N | 
VALD_E003 (dependency) | Y / N | 
VALD_E004 (schema) | Y / N | 
VALD_E005 (security scan) | Y / N | 

**Additional Safety Constraints**:

---

## Revision History

| Date | Version | Author | Note |
|------|---------|--------|------|
| 2026-08-20 | Candidate | Claude (Phase 4 Review Prep) | Initial decision candidate |


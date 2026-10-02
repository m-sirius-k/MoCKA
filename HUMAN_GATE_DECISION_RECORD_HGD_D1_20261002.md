# HUMAN_GATE_DECISION_RECORD_HGD_D1

**Document ID**: HGDR_HGD_D1_20261002  
**Date**: 2026-10-02  
**Prepared by**: KUROKO  
**Status**: PENDING CONFIRMATION  
**References**: DC_20261002_HGD_A1_IMPLEMENTATION_SCOPE, DC_20261002_HGD_B1_IMPLEMENTATION_SCOPE  
**Depends on**: HGD-A1 (CONFIRMED), HGD-B1 (CONFIRMED)

---

## 1. Purpose

HGD-D1 is the Implementation Authorization gate for the combined A1+B1 code
changes. HGD-A1 and HGD-B1 defined WHAT to change and why. HGD-D1 authorizes
KUROKO to execute those changes in the actual codebase on the KUROKO PC.

Without HGD-D1, no file modification is permitted, regardless of A1/B1
Decision Ledger status.

---

## 2. Scope of Implementation

### A1 Scope (4 files, no new modules)

| File | Change | Size |
|------|--------|------|
| structural/authorization_pipeline.py | Add READ_ONLY_TOOLS set + bypass at entry of execute() | ~+15 lines |
| structural/human_gate_authorization_integrity.py | args["_authz"]["decision_id"] instead of args["decision_id"] | ~+5 lines |
| structural/authorization_scope_binding.py | args["_authz"]["scope"] instead of args["scope"] | ~+3 lines |
| structural/governance_pipeline.py | Strip UTF-8 BOM (\xef\xbb\xbf) only — 0 logic changes | ~0 lines |

### B1 Scope (1 modified + 1 new file)

| File | Change | Size |
|------|--------|------|
| structural/tool_registry_enforcement.py | Replace hardcoded TOOL_REGISTRY dict with _load_registry() JSON file loader | ~+25 lines, -11 entries |
| data/governance/tool_registry.json | NEW file: JSON registry with all write tools | ~17 entries (final count after KUROKO PC 照合) |

### Combined: 5 files modified/created, 1 new data file

---

## 3. Implementation Execution Order

All steps are mandatory. No step may be skipped.

### Critical Separation of Concerns

```
実装 != 検証 != commit != Runtime activation
```

commit / push は「実装完了条件」ではない。Human Gate への報告後に実施する。

### Step 1: KUROKO PC Registry Completeness 照合

- Enumerate all tools in C:/Users/sirok/MoCKA/mocka_mcp_server.py
- Classify each as READ or WRITE per HGD-A1 class definitions
- Verify 100% WRITE tool coverage in the 17-tool list in HGD-B1
- Revise tool list if discrepancies found (update HGD-B1 document first with
  CHANGE_START/CHANGE_DONE, then proceed)

### Step 2: TODO_390 / .gitignore Audit

```bash
grep -n "data/" C:/Users/sirok/MoCKA/.gitignore
# If data/* or data/ is excluded:
# Add "!data/governance/tool_registry.json" to whitelist
# Verify with: git check-ignore -v data/governance/tool_registry.json
```

### Step 3: CHANGE_START

```python
mocka_write_event(
    title="CHANGE_START: HGD-A1+B1 GL8-GL12 GAP-2/4/5 remediation",
    description="Target: authorization_pipeline.py, human_gate_authorization_integrity.py, authorization_scope_binding.py, governance_pipeline.py (BOM), tool_registry_enforcement.py, data/governance/tool_registry.json\nAuthorization: DC_20261002_HGD_A1_IMPLEMENTATION_SCOPE + DC_20261002_HGD_B1_IMPLEMENTATION_SCOPE\nHGD-D1: DC_20261002_HGD_D1_IMPLEMENTATION_AUTHORIZATION",
    tags="change_start,HGD_A1,HGD_B1,HGD_D1"
)
```

### Step 4: A1 Implementation

4a. **authorization_pipeline.py**: Add READ_ONLY_TOOLS set and bypass check at
    entry of `execute()` method. The bypass returns `AuthorizationDecision` with
    `allowed=True`, `failure_code="AUTHZ_BYPASS_READ_ONLY"` for Class A tools.

4b. **human_gate_authorization_integrity.py**: Change
    `args.get("decision_id")` to `args.get("_authz", {}).get("decision_id")`
    in `verify_authorization()`. Also update any scope extraction that reads
    from `args` directly to read from `args["_authz"]`.

4c. **authorization_scope_binding.py**: Change
    `args.get("scope", [])` to `args.get("_authz", {}).get("scope", [])`
    in `verify_scope_binding()`.

4d. **governance_pipeline.py**: Remove leading `\xef\xbb\xbf` BOM bytes only.
    Verify no logic changes. File must start with `#` or `"""` after strip.

### Step 5: B1 Implementation

5a. **tool_registry_enforcement.py**: Replace hardcoded `TOOL_REGISTRY` dict
    with `_load_registry()` method that loads from
    `data/governance/tool_registry.json`. Add `import json` and `from pathlib
    import Path` if not already present. Fail-closed: empty dict on load
    failure.

5b. **data/governance/tool_registry.json**: Create new file with all write tool
    entries. Schema version "1.0". Include all tools from the 照合-verified
    list (Step 1). No BOM. UTF-8 encoding.

### Step 6: UTF-8 / BOM Verification

```python
# For each of the 5 files listed in Section 2:
mocka_check_utf8("{filepath}")
# Expected: UTF-8 OK, no BOM on all files
# For governance_pipeline.py specifically: verify BOM=False (was contaminated)
```

### Step 7: CHANGE_DONE

```python
mocka_write_event(
    title="CHANGE_DONE: HGD-A1+B1 GL8-GL12 GAP-2/4/5 remediation",
    description="Result: all 5 files modified/created\nUTF-8: OK (all)\nBOM: removed from governance_pipeline.py",
    tags="change_done,HGD_A1,HGD_B1,HGD_D1"
)
```

### Step 8: KUROKO PC Read-Back

Mandatory before reporting to Human Gate:

- Import the modified modules and confirm no ImportError
- Instantiate AuthorizationPipeline() and confirm READ_ONLY_TOOLS bypass
  returns AUTHZ_BYPASS_READ_ONLY for a read tool
- Confirm ToolRegistryEnforcementEngine loads tool_registry.json
  successfully (no fallback to empty dict)
- Confirm governance_pipeline.py has no BOM (import succeeds cleanly)

### Step 9: Human Gate Report

Report implementation results to きむら博士 before commit/push:

- Which files were changed and summary of changes
- UTF-8 verification results for all 5 files
- Read-Back results (PASS / FAIL per check)
- Any deviations from the planned scope (if any: requires new Human Gate
  decision before proceeding)

commit / push do NOT proceed until Human Gate acknowledges this report.

### Step 10: commit / push (after Human Gate acknowledgement)

Commit message (exact):
```
fix(GL8-GL12): GAP-2/4/5 remediation (HGD-A1+B1)

HGD-A1: READ_ONLY_TOOLS bypass + _authz envelope extraction (GAP-2/4)
HGD-B1: JSON-based tool registry for GL11 (GAP-5)

Authorization: DC_20261002_HGD_A1_IMPLEMENTATION_SCOPE
               DC_20261002_HGD_B1_IMPLEMENTATION_SCOPE
               DC_20261002_HGD_D1_IMPLEMENTATION_AUTHORIZATION
```

git push to claude/youthful-gates-51qxdo only.

Post-commit verification:
```bash
git show --stat HEAD
# Verify data/governance/tool_registry.json is included (TODO_390 pattern)
```

---

## 4. Prohibited Actions During Implementation

- Activating the Authorization Pipeline in production (no runtime activation)
- Modifying GL8-GL12 verification algorithms (FAIL codes, thresholds,
  AUTHORIZED_APPROVERS)
- Adding new FAIL scenarios beyond existing GL8_FAIL_1-4 / GL9_FAIL_1-3
- Changing Decision Ledger schema or path
- Adding session-level authorization state
- Modifying any file not listed in Section 2
- Expanding READ_ONLY_TOOLS beyond the set defined in HGD-A1 without a new
  CHANGE_START/CHANGE_DONE governance record
- Adding tools to tool_registry.json beyond the 照合-verified list
- Creating or referencing a self-generated decision_id in _authz context
- Amending or rewriting commit 916bef7

---

## 5. What Does NOT Change

- GL8-GL12 verification logic (algorithms unchanged)
- GL1-GL7 governance pipeline behavior
- Decision Ledger schema and storage
- Human Gate approval process
- AUTHORIZED_APPROVERS set (きむら博士)
- Existing read-only tool access (zero regression)
- GL11 failure codes (GL11_FAIL_1_UNKNOWN_TOOL, GL11_FAIL_2_DISABLED_TOOL)
- Fail-closed behavior of GL11 on registry load failure

---

## 6. Risk Assessment

**Risk**: Low

- No runtime activation; code change only on development branch
- All 5 files have exactly specified, minimal changes
- GL8-GL12 verification algorithms untouched
- Read-Back on KUROKO PC catches any import/runtime issues before push
- AUTHZ_BYPASS_READ_ONLY preserves full read operation access
- Fail-closed on registry load failure preserves security contract

**Infrastructure note (UNKNOWN-1 from C1 Stage 1)**:
The GL8 hardcoded DECISION_LEDGER_PATH points to the cloud container's empty
ledger. This does not affect the implementation (code change only). It remains
an environment configuration concern for the production deployment gate
(a separate, future Human Gate decision not covered by HGD-D1).

---

## 7. Implementation Preconditions Summary

All must be satisfied before step 3 (CHANGE_START):

1. DC_20261002_HGD_A1_IMPLEMENTATION_SCOPE: Active in Decision Ledger [DONE]
2. DC_20261002_HGD_B1_IMPLEMENTATION_SCOPE: Active in Decision Ledger [DONE]
3. DC_20261002_HGD_D1_IMPLEMENTATION_AUTHORIZATION: Active in Decision Ledger
   [PENDING — registered upon きむら博士 confirmation of this document]
4. Registry completeness 照合 complete (KUROKO PC mocka_mcp_server.py)
5. .gitignore audit complete (data/governance/ whitelist verified)
6. Implementation environment: KUROKO PC (Windows), NOT cloud container

---

## Decision Status

```
HGD-A1:                CONFIRMED (DC_20261002_HGD_A1_IMPLEMENTATION_SCOPE Active)
HGD-B1:                CONFIRMED (DC_20261002_HGD_B1_IMPLEMENTATION_SCOPE Active)
HGD-D1:                APPROVED by きむら博士 (2026-10-02)
DC_20261002_HGD_D1_IMPLEMENTATION_AUTHORIZATION: Active in Decision Ledger
```

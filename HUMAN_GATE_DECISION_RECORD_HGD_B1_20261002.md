# HUMAN_GATE_DECISION_RECORD_HGD_B1

**Document ID**: HGDR_HGD_B1_20261002  
**Date**: 2026-10-02  
**Prepared by**: KUROKO  
**Status**: PENDING CONFIRMATION  
**Supersedes**: HGD_B1_TOOL_REGISTRY_DECISION_PACKAGE.md (analysis document)  
**References**: DC_20261002_PHASE5_1_A_REMEDIATION, PHASE5_1_A_C1_STAGE1_VERIFICATION_REPORT.md  
**Depends on**: HGD-A1 (Option B reduces registry scope to write tools only)

---

## 1. Current State

### What C1 Stage 1 Verified (Relevant to B1)

Test 2 (Happy Path) used `mocka_write_event` which IS in the current GL11
TOOL_REGISTRY (11 tools). The Happy Path PASS confirms GL11 correctly
allows registered ACTIVE tools.

### What C1 Stage 1 Did NOT Verify (Relevant to B1)

- That unregistered tools (GAP-5 tools) are correctly blocked
- That the JSON schema registry loads correctly (HGD-B1 not yet implemented)
- FAIL_1 for unknown tools (GL11_FAIL_1_UNKNOWN_TOOL) not tested

### GAP-5 Confirmed Active

6 critical write tools are NOT in the current TOOL_REGISTRY:
```
mocka_add_todo       (write - TODO management)
mocka_update_todo    (write - TODO status)
mocka_seal           (write - governance seal, high impact)
mocka_integrity_write (write - integrity record)
mocka_registry_add   (write - registry modification)
Bash                 (write - shell commands, highest privilege)
```

If the Authorization Pipeline is deployed as-is, these tools would be
blocked at GL11_FAIL_1_UNKNOWN_TOOL after passing GL8-GL10.

### Registry Completeness: UNVERIFIED ESTIMATE

The 17-tool total (11 existing + 6 new) is a current estimate based on
observation in the cloud container environment. It has NOT been verified
against the actual KUROKO PC tool inventory (mocka_mcp_server.py tool
definitions on the Windows machine where the MCP server runs).

It is possible that:
- Additional write tools exist in mocka_mcp_server.py that are not in
  this list (would be blocked at GL11_FAIL_1 if omitted)
- The 6 "missing" tools listed above may differ from the actual gap
  once the KUROKO PC tool inventory is enumerated

Registry completeness verification against KUROKO PC tool inventory is
a mandatory implementation precondition (see Section 7).

### HGD-A1 Dependency

If HGD-A1 Option B (READ bypass) is confirmed:
- Read tools bypass the pipeline entirely
- GL11 is never called for read tools
- Registry gap reduces to write tools only (~6 tools to add)
- This is the scope assumed in this document

If HGD-A1 were NOT confirmed (hypothetical Option D, GL11-first):
- ALL 25+ tools would need registry entries
- Higher maintenance burden
- This document does not cover that case

---

## 2. Decision Question

What is the source of truth for the GL11 tool registry, such that:
a. All legitimate MoCKA write operations are not blocked by GL11
b. Unknown (unauthorized) tools remain fail-closed (DENY)
c. The registry is maintainable as new tools are added over time

---

## 3. Selected Option: JSON Schema File (Option B)

**Method**: Extract TOOL_REGISTRY to a JSON file at
`data/governance/tool_registry.json`. Engine loads from file at startup.

### JSON File Schema

```json
{
  "schema_version": "1.0",
  "updated_at": "2026-10-02",
  "tools": [
    {
      "name": "mocka_write_event",
      "status": "ACTIVE",
      "requires_authorization": true,
      "description": "Write event to event ledger",
      "added_at": "2026-10-02"
    },
    {
      "name": "mocka_add_todo",
      "status": "ACTIVE",
      "requires_authorization": true,
      "description": "Add new TODO item",
      "added_at": "2026-10-02"
    },
    {
      "name": "mocka_seal",
      "status": "ACTIVE",
      "requires_authorization": true,
      "description": "Create governance seal (anchor_update)",
      "added_at": "2026-10-02"
    },
    {
      "name": "Bash",
      "status": "ACTIVE",
      "requires_authorization": true,
      "description": "Execute shell command (highest privilege)",
      "added_at": "2026-10-02"
    }
  ]
}
```

### Engine Modification

```python
class ToolRegistryEnforcementEngine:
    def __init__(self):
        self.TOOL_REGISTRY = {}
        self._load_registry()

    def _load_registry(self):
        registry_path = Path("/home/user/MoCKA/data/governance/tool_registry.json")
        try:
            if registry_path.exists():
                data = json.loads(registry_path.read_text(encoding="utf-8"))
                for tool in data.get("tools", []):
                    self.TOOL_REGISTRY[tool["name"]] = ToolMetadata(
                        name=tool["name"],
                        status=ToolLifecycleStatus[tool["status"]],
                        requires_authorization=tool.get("requires_authorization", True),
                        description=tool.get("description"),
                        added_at=tool.get("added_at")
                    )
        except Exception as e:
            # Fail-closed: empty registry = all tools DENY
            print(f"GL11: Registry load failed: {e}. All tools will be DENIED.")
            self.TOOL_REGISTRY = {}
```

**Fail-closed on load failure**: if the JSON file is missing or malformed,
`TOOL_REGISTRY = {}` means all tools return GL11_FAIL_1. This preserves the
security contract (unknown/unregistered = DENY) even on registry failure.

### Complete Tool List for data/governance/tool_registry.json

Existing 11 tools (currently hardcoded, to be migrated):

| Tool | requires_authorization |
|------|----------------------|
| mocka_get_overview | False |
| mocka_get_todo | False |
| mocka_get_essence | False |
| mocka_write_event | True |
| mocka_decision_write | True |
| mocka_decision_get | False |
| mocka_decision_list | False |
| mocka_check_utf8 | False |
| Write | True |
| Edit | True |
| Read | False |

6 new write tools (GAP-5 resolution):

| Tool | requires_authorization | Notes |
|------|----------------------|-------|
| mocka_add_todo | True | TODO management |
| mocka_update_todo | True | TODO status changes |
| mocka_seal | True | Governance seal, high impact |
| mocka_integrity_write | True | Integrity record write |
| mocka_registry_add | True | Registry modification |
| Bash | True | Shell commands, highest privilege |

Total: 17 tools in registry.

### Bash Tool Special Note

`Bash` has the highest privilege. A caller authorized to execute Bash could
bypass all MoCKA file-level governance. The registry entry marks
`requires_authorization=True`, meaning Bash requires a valid Human Gate
decision reference (via `_authz` envelope). Additional scope restriction
(e.g., authorized_scope must include "shell") is noted as a future
enhancement but is NOT part of this implementation scope.

### Why NOT Option A (Manual Hardcoded)

- Every new tool requires a code change to tool_registry_enforcement.py
- Source of truth is scattered (tool in mocka_mcp_server.py, registry in
  separate Python file)
- High maintenance risk: new tools added to MCP server without registry
  update = DENY with no warning

### Why NOT Option C (Auto-Discovery)

- Circular dependency: GL11 is INSIDE the MCP server
- Startup race condition possible
- Tight coupling between GL11 and MCP server API

### Why NOT Option D (Default-Permit)

- Changes GL11 security model from deny-by-default to permit-by-default
- Contradicts DC_20261002_GL8_GL12_ARCHITECTURE (fail-closed contract)
- Would require a separate Human Gate decision to approve security model change

---

## 4. Authority Boundary

### Before B1 Implementation

```
GL11 TOOL_REGISTRY: 11 tools hardcoded in Python source
mocka_add_todo called -> GL11_FAIL_1_UNKNOWN_TOOL (if pipeline deployed)
mocka_seal called     -> GL11_FAIL_1_UNKNOWN_TOOL (if pipeline deployed)
Bash called           -> GL11_FAIL_1_UNKNOWN_TOOL (if pipeline deployed)
```

### After B1 Implementation

```
GL11 loads from data/governance/tool_registry.json at startup
mocka_add_todo called -> GL11_OK (registered, ACTIVE)
mocka_seal called     -> GL11_OK (registered, ACTIVE, high-impact noted)
Bash called           -> GL11_OK (registered, ACTIVE, requires_authorization=True)
unregistered tool     -> GL11_FAIL_1_UNKNOWN_TOOL (fail-closed unchanged)
```

### What Changes

- structural/tool_registry_enforcement.py: replace hardcoded TOOL_REGISTRY
  dict with `_load_registry()` file loader. Net: -11 hardcoded entries, +25
  lines of loader logic, +1 data file dependency
- data/governance/tool_registry.json: NEW file, 17 tool entries

### What Does NOT Change

- GL11 verification logic (ACTIVE/DISABLED/DEPRECATED behavior unchanged)
- GL11 failure codes (GL11_FAIL_1_UNKNOWN_TOOL, GL11_FAIL_2_DISABLED_TOOL)
- Security model: fail-closed behavior preserved (even if file missing)
- Existing registered tools: same authorization requirements

---

## 5. Allowed Scope (for Implementation when authorized)

Allowed when HGD-D1 Implementation Authorization is granted:

- Modify `structural/tool_registry_enforcement.py`:
  Replace hardcoded TOOL_REGISTRY dict with JSON file loader
  Add `_load_registry()` method and `import json` at top
  Total change: approximately +25 lines, -11 hardcoded entries

- Create `data/governance/tool_registry.json`:
  New file with 17 tool entries (11 existing + 6 new write tools)
  UTF-8, no BOM
  Verify .gitignore whitelist BEFORE creating (TODO_390 protocol)

---

## 6. Prohibited Scope

- Changing GL11 verification logic (ACTIVE/DISABLED/DEPRECATED behavior)
- Changing GL11 failure codes
- Adding tools beyond the 17 listed in Section 3
- Changing `requires_authorization` for existing tools without Human Gate
  review (e.g., changing Read to requires_authorization=True would break
  all read operations)
- Setting any tool to DISABLED without Human Gate decision
- Changing the fail-closed behavior on load failure
- Using data/governance/tool_registry.json as a runtime configuration file
  (it is a governance artifact; changes require CHANGE_START/CHANGE_DONE)
- Activating the Authorization Pipeline in production
- Modifying any tool's authorization policy beyond what is listed above

---

## 7. Implementation Preconditions

All must be satisfied before implementation begins:

1. HUMAN_GATE_DECISION_RECORD_HGD_A1_20261002.md: confirmed by きむら博士
2. HUMAN_GATE_DECISION_RECORD_HGD_B1_20261002.md: confirmed by きむら博士
   (this document)
3. HGD-D1 Implementation Authorization: granted by きむら博士
4. Registry completeness check REQUIRED: before creating
   data/governance/tool_registry.json, perform 照合 of all planned tool
   entries against the actual KUROKO PC MoCKA tool inventory:

   a. Enumerate all tools defined in mocka_mcp_server.py on the Windows
      machine (C:/Users/sirok/MoCKA/mocka_mcp_server.py)
   b. Classify each tool as READ or WRITE (per HGD-A1 Class definitions)
   c. Verify that every WRITE tool appears in the 17-tool list in Section 3
   d. If additional WRITE tools are found: update the tool list in Section 3
      before proceeding (requires CHANGE_START/CHANGE_DONE for this document)
   e. If any WRITE tool from Section 3 is missing from mocka_mcp_server.py:
      remove it from the registry (absent tool should not be registered)

   The registry must cover 100% of WRITE tools on KUROKO PC.
   Undercoverage = operational failure (GL11_FAIL_1_UNKNOWN_TOOL at runtime).

5. .gitignore audit REQUIRED: check data/ exclusion rules before creating
   data/governance/tool_registry.json (per TODO_390 incident)

   ```bash
   grep -n "data/" /home/user/MoCKA/.gitignore
   # If data/* or data/ is excluded:
   # Add "!data/governance/tool_registry.json" to whitelist
   # Verify with: git check-ignore -v data/governance/tool_registry.json
   ```

6. CHANGE_START event recorded before any file modification
7. After creating tool_registry.json: UTF-8 check via Python3
8. After modifying tool_registry_enforcement.py: UTF-8 check via Python3
9. CHANGE_DONE event recorded after both files modified
10. git commit message: "fix(GL11): GAP-5 remediation (HGD-B1, JSON-based tool registry)"
11. git push to claude/youthful-gates-51qxdo only
12. After commit: verify with `git show --stat HEAD` that
    data/governance/tool_registry.json is included (per TODO_390 pattern)

---

## Decision Status

```
HGD-B1 Design:          APPROVED (DC_20261002_PHASE5_1_A_REMEDIATION)
HGD-B1 C1 Stage 1:      RELEVANT (GL11 PASS for registered tool confirmed)
HGD-B1 Implementation:  PENDING CONFIRMATION (this document)
HGD-A1 Dependency:      PENDING CONFIRMATION (Option B reduces scope to writes)
HGD-D1:                 NOT YET CREATED (blocked until A1+B1 confirmed)
```

Registration as individual decision record in Decision Ledger is pending
until きむら博士 confirms this document.

KUROKO will call `mocka_decision_write(decision_id="DC_20261002_HGD_B1_IMPLEMENTATION_SCOPE")` upon explicit confirmation.

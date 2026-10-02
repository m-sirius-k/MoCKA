# HGD-B1: Tool Registry Coverage Strategy Decision Package

**Package Type**: Human Gate Decision Draft  
**Status**: PENDING APPROVAL  
**Prepared by**: KUROKO  
**Date**: 2026-10-02  
**Reference**: GAP-5 in PHASE5_1_A_REMEDIATION_DESIGN.md  
**Depends on**: HGD-A1 (Option selection affects registry scope)

---

## Decision Question

Which strategy resolves GAP-5 (Tool Registry Coverage) while:
1. Ensuring no legitimate MoCKA operations are blocked by GL11
2. Maintaining fail-closed security for genuinely unauthorized tools
3. Being maintainable as new tools are added to MoCKA over time

---

## Background

### Current State

GL11 TOOL_REGISTRY has 11 registered tools (hardcoded class variable).
GL11 contract: unknown tools -> GL11_FAIL_1_UNKNOWN_TOOL (DENY).

MoCKA MCP server exposes 25+ tools. 16+ are currently unregistered.

If GL8-GL12 Authorization Pipeline is deployed:
- All unregistered tools return GL11_FAIL_1 before execution
- This blocks standard governance operations (mocka_add_todo, mocka_seal, etc.)

### Dependency on HGD-A1

If HGD-A1 selects Option B (READ_ONLY_TOOLS bypass):
- Read-only tools skip the Authorization Pipeline entirely
- GL11 is never called for read tools
- Registry gap reduces from 20+ tools to ~9 write-only tools:

Write tools NOT currently in registry:
```
mocka_add_todo          (write)
mocka_update_todo       (write)
mocka_seal              (write)
mocka_integrity_write   (write)
mocka_registry_add      (write)
Bash                    (write - file system operations)
```

Plus any future write tools added to mocka_mcp_server.py.

If HGD-A1 selects Option D (GL11-first):
- ALL tools (read and write) pass through GL11 pre-check
- Registry must cover ALL 25+ tools
- Higher maintenance burden

This document covers both scenarios but focuses on the Option B case
(smaller scope, recommended by HGD-A1 package).

---

## Current Registry Inventory

### Registered (11 tools)

| Tool | Status | requires_authorization |
|------|--------|----------------------|
| mocka_get_overview | ACTIVE | False |
| mocka_get_todo | ACTIVE | False |
| mocka_get_essence | ACTIVE | False |
| mocka_write_event | ACTIVE | True |
| mocka_decision_write | ACTIVE | True |
| mocka_decision_get | ACTIVE | False |
| mocka_decision_list | ACTIVE | False |
| mocka_check_utf8 | ACTIVE | False |
| Write | ACTIVE | True |
| Edit | ACTIVE | True |
| Read | ACTIVE | False |

### Missing Write Tools (critical gap if HGD-A1 Option B)

| Tool | Status | requires_authorization | Notes |
|------|--------|----------------------|-------|
| mocka_add_todo | ACTIVE | True | TODO management |
| mocka_update_todo | ACTIVE | True | TODO status changes |
| mocka_seal | ACTIVE | True | Governance seal (high impact) |
| mocka_integrity_write | ACTIVE | True | Integrity record |
| mocka_registry_add | ACTIVE | True | Registry modification |
| Bash | ACTIVE | True | System commands (highest risk) |

### Missing Read Tools (critical gap if HGD-A1 Option D)

| Tool | requires_authorization | Notes |
|------|----------------------|-------|
| mocka_list_events | False | Event history |
| mocka_read_event | False | Single event read |
| mocka_search | False | Event search |
| mocka_get_guidelines | False | Guidelines read |
| mocka_get_command_center | False | Command center status |
| mocka_get_incidents | False | Incident history |
| mocka_integrity_get | False | Integrity record read |
| mocka_integrity_list | False | Integrity record list |
| mocka_registry_get | False | Registry read |
| mocka_registry_current_state | False | Registry state |
| Glob | False | File search |
| Grep | False | File content search |
| AskUserQuestion | False | UI interaction |
| MultiEdit | True | Multi-file edit |
| mcp__github__* | True | GitHub operations (external) |

---

## Registry Source of Truth Comparison

### Option A: Manual Registry Completion (Hardcoded)

**Method**: Add all missing tools to TOOL_REGISTRY dict in
tool_registry_enforcement.py source code.

```python
TOOL_REGISTRY = {
    # ... existing 11 entries ...
    "mocka_add_todo": ToolMetadata(
        name="mocka_add_todo",
        status=ToolLifecycleStatus.ACTIVE,
        requires_authorization=True,
        description="Add new TODO item to MOCKA_TODO_ACTIVE.json"
    ),
    "mocka_update_todo": ToolMetadata(
        name="mocka_update_todo",
        status=ToolLifecycleStatus.ACTIVE,
        requires_authorization=True,
        description="Update TODO status or fields"
    ),
    "mocka_seal": ToolMetadata(
        name="mocka_seal",
        status=ToolLifecycleStatus.ACTIVE,
        requires_authorization=True,
        description="Create governance seal (anchor_update)"
    ),
    "mocka_integrity_write": ToolMetadata(
        name="mocka_integrity_write",
        status=ToolLifecycleStatus.ACTIVE,
        requires_authorization=True,
        description="Write integrity classification record"
    ),
    "mocka_registry_add": ToolMetadata(
        name="mocka_registry_add",
        status=ToolLifecycleStatus.ACTIVE,
        requires_authorization=True,
        description="Add entry to MoCKA registry"
    ),
    "Bash": ToolMetadata(
        name="Bash",
        status=ToolLifecycleStatus.ACTIVE,
        requires_authorization=True,
        description="Execute shell command (highest privilege)"
    ),
}
```

**Strengths**:
- Simplest implementation (code-only change)
- Explicit and auditable in version control
- Each tool's authorization requirement is a deliberate decision
- No new dependencies or infrastructure

**Weaknesses**:
- Every new tool requires a code change to tool_registry_enforcement.py
- Source of truth is scattered (tool defined in mocka_mcp_server.py, but registry
  maintained separately in tool_registry_enforcement.py)
- Risk of drift: new tools added to MCP server without registry update = DENY

**Maintenance risk**: HIGH if new tools are frequently added.

---

### Option B: JSON Schema File (Recommended)

**Method**: Extract TOOL_REGISTRY to a JSON file. Engine loads from file at startup.

Schema file: `data/governance/tool_registry.json`

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
      "name": "Bash",
      "status": "ACTIVE",
      "requires_authorization": true,
      "description": "Execute shell command",
      "added_at": "2026-10-02"
    }
  ]
}
```

```python
class ToolRegistryEnforcementEngine:
    def __init__(self):
        self.TOOL_REGISTRY = {}
        self._load_registry()

    def _load_registry(self):
        registry_path = Path("/home/user/MoCKA/data/governance/tool_registry.json")
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
```

**Strengths**:
- Adding a new tool requires only a JSON edit (no code change)
- Single data file = single source of truth for tool registry
- JSON is auditable in git (diff shows exactly what was added/removed)
- UTF-8 validation via mocka_check_utf8 applies to the registry file
- Registry can be reviewed independently of code by governance officers

**Weaknesses**:
- File load on startup: if file missing, registry is empty (needs fallback)
- File path must be stable and accessible at startup
- JSON schema must be validated on load (malformed JSON -> empty registry)
- Fallback behavior on load failure must be defined (fail-closed? partial?)

**Maintenance risk**: LOW. JSON edits require no code review.

**Fallback on load failure**:
```python
def _load_registry(self):
    try:
        # ... load from file ...
    except Exception as e:
        # Fail-closed: empty registry means all tools DENY
        # This prevents silent registry failure from becoming permit-all
        print(f"GL11: Registry load failed: {e}. All tools will be DENIED.")
        self.TOOL_REGISTRY = {}
```

---

### Option C: Auto-Discovery from MCP Server

**Method**: GL11 engine calls mocka_mcp_server's /tools endpoint to get the
authoritative tool list.

**Strengths**:
- Always in sync with the actual MCP server tool definitions
- Zero manual maintenance

**Weaknesses**:
- Circular dependency: GL11 is INSIDE the MCP server, calling the MCP server
- Runtime dependency: MCP server must be running when GL11 initializes
- Tight coupling between GL11 engine and MCP server API
- Startup race condition possible

**KUROKO Assessment**: NOT recommended. Circular dependency is a structural defect.

---

### Option D: Default-Permit with Explicit Deny List (Policy Change)

**Method**: Unknown tools are ALLOWED with audit warning. Only explicitly
DISABLED tools are blocked.

**Strengths**:
- No operational breakage from missing registry entries

**Weaknesses**:
- Changes security model from deny-by-default to permit-by-default
- Weakens GL11's enforcement capability
- Unknown (potentially dangerous) tools are no longer blocked

**KUROKO Assessment**: This option changes the security contract of GL11.
DC_20261002_GL8_GL12_ARCHITECTURE defines GL11 as "Tool whitelist validation"
with "Fail-closed on unknown tool". Changing to permit-by-default contradicts
the approved decision. Requires a NEW Human Gate decision to approve the
security model change.

---

## Tool Coverage Management Method

### How New Tools Should Be Registered

Regardless of Option A or B selected, the process for adding a new tool:

1. New tool added to mocka_mcp_server.py (or Claude tool manifest)
2. CHANGE_START event recorded
3. Tool entry added to registry (code change for Option A; JSON edit for Option B)
4. Determine: does this tool write/modify state? -> requires_authorization=True
5. Determine: does this tool read only? -> requires_authorization=False
6. UTF-8 check (for Option B: mocka_check_utf8 on tool_registry.json)
7. CHANGE_DONE event recorded
8. Commit with message referencing the new tool and its authorization class

### Authorization Classification Criteria

A tool requires_authorization=True if it:
- Writes to any MoCKA data store (events.db, MOCKA_TODO_ACTIVE.json, etc.)
- Modifies files in the repository
- Executes shell commands (Bash)
- Calls external services with write permissions
- Creates or modifies Decision Ledger entries

A tool requires_authorization=False if it:
- Only reads from data stores
- Only returns computed results (no side effects)
- Performs format validation only (mocka_check_utf8)
- Queries but does not modify

### Risk Classification for Bash Tool

`Bash` has the highest privilege of any registered tool. A threat actor
with authorization to execute Bash could bypass all MoCKA governance.
Recommended: Bash should require requires_authorization=True AND should
have a separate scope restriction (e.g., authorized_scope must include "shell").

This is an enhancement to the current GL9/GL11 design, noted for future
consideration.

---

## Governance Impact Analysis

### Without GAP-5 Fix (Current Risk)

When 916bef7 is deployed to production:
- mocka_seal blocked: governance seals cannot be created
- mocka_add_todo blocked: new TODOs cannot be registered
- mocka_update_todo blocked: TODO status cannot be updated
- Risk: governance drift accumulates unrecorded

### With GAP-5 Option B Fix

- All write tools explicitly registered with authorization requirements
- Unknown tools (future, unanticipated) still blocked (fail-closed)
- Registry file auditable in git history
- Adding new tools to registry requires deliberate action (governance record)

### Impact on Human Gate Review Cadence

Option B (JSON file) enables non-code governance:
- Quarterly registry review: check all ACTIVE tools, confirm no stale entries
- Deprecation flow: set tool status to DEPRECATED or DISABLED in JSON
- No code review required for routine registry maintenance

---

## Decision Options Summary

| | Option A: Manual | Option B: JSON (Rec) | Option C: Auto | Option D: Permit |
|--|--|--|--|--|
| Resolves write tool gap | YES | YES | YES | YES (weakened) |
| Resolves read tool gap (if HGD-A1 D) | YES (+effort) | YES (+effort) | YES | YES |
| Maintenance burden | HIGH | LOW | ZERO | LOW |
| Security model | Unchanged | Unchanged | Unchanged | WEAKENED |
| Within approved scope | YES | YES | NO (circular) | NO (policy change) |
| New data file required | No | YES (JSON) | No | No |

**KUROKO Recommendation**: Option B (JSON Schema File)

- If HGD-A1 selects Option B (READ bypass): Only write tools needed in registry
  (~6 tools additional, easily managed in JSON)
- If HGD-A1 selects Option D (GL11-first): Full tool list in JSON (~25+ entries)

In either case, Option B provides the best long-term maintainability.

---

## Required Approvals

1. きむら博士: Select registry strategy (A / B / D)
   - Note: Option C not recommended (circular dependency)
   - Note: Option D requires separate Human Gate for security model change
2. Implicit: If Option B, new data file `data/governance/tool_registry.json`
   requires .gitignore review (per TODO_390 pattern: new files in data/ must
   be explicitly whitelisted if data/ is in .gitignore)

---

## Pre-Implementation Check (for Option B)

Before creating `data/governance/tool_registry.json`, verify .gitignore:

```bash
grep -n "data/" /home/user/MoCKA/.gitignore
# Check if data/* or data/ is in exclusion list
# If yes: add "!data/governance/tool_registry.json" to .gitignore whitelist
```

This check is required per TODO_390 incident (files in data/ silently excluded
from commits without whitelist exception).

---

## Next Action After Approval

If Option B approved:
1. .gitignore audit for data/governance/ path
2. CHANGE_START event recorded
3. Create data/governance/tool_registry.json with all tool entries
4. Modify tool_registry_enforcement.py: replace hardcoded dict with file loader
5. mocka_check_utf8 on tool_registry.json
6. mocka_check_utf8 on modified tool_registry_enforcement.py
7. CHANGE_DONE event recorded
8. Commit: "feat(GL11): JSON-based tool registry with full write-tool coverage (GAP-5)"
9. Push to development branch

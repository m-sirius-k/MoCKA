# HG-AS-01 Implementation Integration Design
**Date**: 2026-09-22  
**Status**: Design Document (Not Yet Integrated)  
**Scope**: Sandbox Only  
**Authority**: Human Gate Decision HG-AS-01

---

## SUMMARY

This document describes how to integrate three new components into the existing MoCKA system to implement HG-AS-01 Human Gate Authorization State issuance.

**New Components**:
1. `phi_os/human_gate_hg_as_01_impl.py` - Payload schema validation module
2. `governance/authorization_state_bridge.py` - Human Gate event → Authorization State transformation
3. `authorization_state` table (new) in `data/mocka_events.db`

**Modified Components** (design only; no changes yet):
1. `phi_os/human_gate.py` - Extend `approve()` to accept HG-AS-01 payload schema
2. `governance/human_gate_cli.py` - Add CLI flags for actor/scope/authority_role
3. `runtime/core/execution_core.py` - Add read-only authorization_state query (fallback)

---

## INTEGRATION FLOW

### Flow Diagram

```
┌─ Human (TTY) ─────────────────────────────────────────────────────┐
│                                                                    │
│  confirm = input("承認しますか？ [yes/no]: ")                      │
│  → payload {actor, scope, authority_role, expires_at, ...}       │
│                                                                    │
└──→ governance/human_gate_cli.py:cmd_approve()                     │
     │                                                               │
     └──→ phi_os/human_gate.py:approve(request_id, payload)        │
          │ (existing state machine: PENDING → APPROVED)            │
          │                                                          │
          ├─ Validate payload schema (phi_os/human_gate_hg_as_01_impl.py)
          │ → (is_valid, error_msg)                                │
          │                                                          │
          └─ Record to human_gate_events table (append-only)        │
             │ event_id, timestamp, action=approve                 │
             │ next_state=APPROVED, payload (JSON with all fields) │
             │                                                      │
             └─→ (OFFLINE) governance/authorization_state_bridge.py
                  │                                                 │
                  ├─ Fetch latest human_gate_events.approve event  │
                  ├─ Validate payload schema                       │
                  ├─ Transform to authorization_state record       │
                  │ → {authorization_id (UUID), decision_id,       │
                  │    subject, scope, standing="UNKNOWN", status, │
                  │    granted_by, granted_at, expires_at, ...}    │
                  │                                                 │
                  └─ INSERT into authorization_state table         │
                     (append-only, immutable triggers)             │
                     → authorization_id (success)

Runtime Verification (Sandbox only):
  runtime/core/execution_core.py (READ-ONLY)
  │ Query: SELECT * FROM authorization_state                       │
  │        WHERE status='APPROVED' AND ...                        │
  │                                                                │
  └─ Fallback to approval_token if authorization_state not found  │
     (Production unaffected; uses approval_token only)
```

---

## COMPONENT DETAILS

### 1. phi_os/human_gate_hg_as_01_impl.py

**Purpose**: Schema validation and payload transformation utilities

**Functions**:
- `validate_payload_for_approve(payload)` → (is_valid, error_msg)
  - Validates actor, scope, authority_role (mandatory)
  - Validates optional fields: decision_id, expires_at, evidence_ref, note
  - Returns error if mandatory fields missing or empty
  
- `enrich_payload_for_cli_approve(...)` → payload_dict
  - Helper to build payload from CLI arguments
  - Used by governance/human_gate_cli.py
  
- `payload_to_authorization_state_input(...)` → auth_state_dict
  - Transform human_gate_events approve payload to authorization_state record
  - Sets standing="UNKNOWN" (HG-AS-01 requirement)
  - Generates authorization_id (UUID)

**Integration Point**:
- Import into `governance/authorization_state_bridge.py` and `governance/human_gate_cli.py`
- NO changes to existing code; only new module

---

### 2. governance/authorization_state_bridge.py

**Purpose**: One-way transformation from human_gate_events to authorization_state

**Key Functions**:

- `issue_authorization_state(request_id)` → (success, error_msg, authorization_id)
  - Entry point for creating authorization_state from human_gate_events
  - Flow:
    1. Fetch latest human_gate_events for request_id
    2. Verify action="approve" and next_state="APPROVED"
    3. Validate payload schema
    4. Transform to authorization_state record
    5. Insert (append-only)
  
- `get_authorization_state(authorization_id)` → dict or None
  - Read-only lookup by authorization_id
  - Used by Sandbox runtime verification
  
- `query_authorization_state(decision_id, subject, status)` → [dict]
  - Read-only query with optional filters
  - Used by Sandbox runtime verification

**Table Schema**:
```sql
CREATE TABLE authorization_state (
    authorization_id TEXT PRIMARY KEY,  -- UUID
    decision_id TEXT,                   -- optional
    subject TEXT,                       -- actor
    scope TEXT,                         -- JSON array as string
    standing TEXT,                      -- always "UNKNOWN" (HG-AS-01)
    status TEXT,                        -- APPROVED/REJECTED/EXPIRED/HELD
    granted_by TEXT,                    -- authority_role
    granted_at TEXT,                    -- ISO8601 timestamp
    expires_at TEXT,                    -- ISO8601 or null
    evidence TEXT,                      -- JSON with source refs
    hg_event_source TEXT,               -- event_id (traceability)
    hg_event_timestamp TEXT,            -- timestamp (traceability)
    created_at TEXT,                    -- when auth_state was created
    immutable INTEGER DEFAULT 1         -- append-only flag
)

-- Triggers
CREATE TRIGGER authorization_state_no_update
  BEFORE UPDATE ON authorization_state
  BEGIN SELECT RAISE(ABORT, 'authorization_state is append-only'); END

CREATE TRIGGER authorization_state_no_delete
  BEFORE DELETE ON authorization_state
  BEGIN SELECT RAISE(ABORT, 'authorization_state is append-only'); END
```

**Integration Point**:
- NEW module; can be invoked independently by runtime or CLI
- NO changes to existing code

---

### 3. phi_os/human_gate.py (Extension Design)

**Changes Required** (NOT YET IMPLEMENTED; design only):

**A. HTTP API payload acceptance**:
```python
@human_gate_bp.route('/api/human_gate/approve', methods=['POST'])
def http_approve():
    payload = request.get_json(force=True) or {}
    request_id = payload.get("request_id", "")
    
    # NEW: Validate payload schema per HG-AS-01
    from phi_os.human_gate_hg_as_01_impl import validate_payload_for_approve
    is_valid, err = validate_payload_for_approve(payload)
    if not is_valid:
        return jsonify({"status": "schema_error", "reason": err}), 422
    
    try:
        event = approve(request_id, payload)  # existing approve()
        return jsonify({"status": "ok", "event": event}), 200
    except HumanGateError as e:
        return jsonify({"status": "rejected", "reason": e.reason}), 422
```

**B. Documentation** (no code change):
```python
# approve() docstring update
def approve(request_id: str, payload: dict | None = None, conn=None) -> dict:
    """
    Approve a pending human_gate request.
    
    Payload schema (HG-AS-01):
    {
        "actor": "string (required; e.g., 'kimura_phd')",
        "scope": ["string"] (required; e.g., ["component_A"]),
        "authority_role": "string (required; e.g., 'HG_AUTHORITY_HOLDER_01')",
        "decision_id": "string (optional)",
        "expires_at": "ISO8601 (optional)",
        "evidence_ref": ["string"] (optional),
        "note": "string (optional)"
    }
    """
```

**No State Machine Changes**:
- PENDING → APPROVED logic unchanged
- Event record format unchanged (still accepts any JSON payload)
- Backward compatible: missing fields do not block approval

---

### 4. governance/human_gate_cli.py (Extension Design)

**Changes Required** (NOT YET IMPLEMENTED; design only):

**A. Add CLI arguments**:
```python
def cmd_approve(args):
    _require_tty("approve")
    current = get_state(args.request_id)
    if current is None:
        print(f"[approve] ERROR: request_id not found: {args.request_id}")
        sys.exit(1)
    
    print(f"[approve] request_id={args.request_id} current_state={current}")
    
    # NEW: HG-AS-01 payload collection
    if not args.scope:
        scope = input("Approval scope (comma-separated components) [default: default]: ").strip()
        scope = scope.split(",") if scope else ["default"]
    else:
        scope = args.scope
    
    authority_role = args.authority_role or "HG_AUTHORITY_HOLDER_CLI"
    
    confirm = input(f"Approve as {args.actor or 'kimura_phd'}, scope {scope}? [yes/no]: ")
    if confirm.strip().lower() != "yes":
        print("[approve] キャンセルしました。")
        return
    
    # NEW: Build HG-AS-01 payload
    from phi_os.human_gate_hg_as_01_impl import enrich_payload_for_cli_approve
    payload = enrich_payload_for_cli_approve(
        actor_identity=args.actor or "kimura_phd",
        scope=scope,
        authority_role=authority_role,
        note=args.note
    )
    
    event = approve(args.request_id, payload)
    print(f"[approve] request_id={args.request_id} state={event['next_state']} event_id={event['event_id']}")
```

**B. Add argparse arguments**:
```python
p_approve.add_argument("--actor", default="kimura_phd", help="Actor identity")
p_approve.add_argument("--scope", nargs="+", help="Approval scope components")
p_approve.add_argument("--authority-role", default="HG_AUTHORITY_HOLDER_CLI")
```

---

### 5. runtime/core/execution_core.py (Extension Design)

**Changes Required** (NOT YET IMPLEMENTED; design only):

**A. Add authorization_state verification (Sandbox only)**:
```python
def validate_authorization_state(decision_id: str, sandbox: bool = True) -> bool:
    """
    Read-only check against authorization_state table (Sandbox only).
    
    Args:
        decision_id: decision_record_id to verify
        sandbox: if False, skips authorization_state check (Production)
    
    Returns:
        True if status='APPROVED', False otherwise or if not found
    
    Production behavior:
        - Does NOT invoke authorization_state
        - Falls through to existing approval_token logic
    """
    if not sandbox:
        return None  # Production: use approval_token only
    
    try:
        from governance.authorization_state_bridge import query_authorization_state
        records = query_authorization_state(decision_id=decision_id, status="APPROVED")
        return len(records) > 0
    except Exception:
        return None  # Query failed; fallback to approval_token

def execute_with_metadata(...):
    # Existing code
    ...
    
    # NEW: Sandbox authorization_state check (fallback only)
    is_sandbox = os.getenv("SANDBOX_MODE") == "true"
    if is_sandbox and decision_record_id:
        auth_ok = validate_authorization_state(decision_record_id, sandbox=is_sandbox)
        if auth_ok:
            # Proceed with execution
            pass
        elif auth_ok is False:
            # Authorization state says REJECTED or not found
            execution_status = "BLOCKED"
            return execution_context
        # auth_ok is None: fallback to approval_token (existing logic)
    
    # Existing approval_token logic continues
    ...
```

**No Production Changes**:
- Production code path unchanged
- authorization_state is Sandbox-only fallback
- Existing approval_token logic remains primary

---

## IMPLEMENTATION SEQUENCE

**Phase 1: Modules (No Integration)**
1. Create `phi_os/human_gate_hg_as_01_impl.py` ← DONE
2. Create `governance/authorization_state_bridge.py` ← DONE
3. Test both modules in isolation ← DONE (Bridge tests pass)

**Phase 2: Integration (Design Only; No Code Changes)**
1. Design extensions to `phi_os/human_gate.py` (payload validation)
2. Design extensions to `governance/human_gate_cli.py` (CLI args)
3. Design extensions to `runtime/core/execution_core.py` (read-only query)
4. Create integration test harness

**Phase 3: Sandbox Pilot (After Approval)**
1. Implement extensions (no changes to existing state machine logic)
2. Run sandbox end-to-end tests
3. Verify authorization_state records created only from Human Gate APPROVED events
4. Verify standing="UNKNOWN" marker present
5. Verify append-only enforcement
6. Verify Production DB untouched
7. Evaluate results for Production decision

---

## COMPATIBILITY ANALYSIS

**Backward Compatibility**:
- ✓ `approve()` signature unchanged
- ✓ Payload validation is additive (new validation, not breaking)
- ✓ State machine logic unchanged
- ✓ Existing human_gate_events payloads (with only "note") still accepted
- ✓ Authorization state issuance fails gracefully if payload missing fields

**Production Safety**:
- ✓ Authorization state is Sandbox-only
- ✓ Production runtime does NOT query authorization_state
- ✓ Existing approval_token logic unchanged
- ✓ No Production database modifications
- ✓ No GL7, SealGovernanceGate, JARVIS changes

---

## TESTING STRATEGY

### Unit Tests
1. `phi_os/human_gate_hg_as_01_impl.py`:
   - Payload validation (valid, missing fields, invalid types)
   - Payload transformation to auth_state record
   - standing="UNKNOWN" marker

2. `governance/authorization_state_bridge.py`:
   - Table creation and immutability triggers
   - Schema validation
   - Event-to-auth-state transformation
   - Query functions (read-only)

### Integration Tests
1. End-to-end: Human Gate approve → authorization_state creation
2. Payload schema enforcement: reject if missing mandatory fields
3. Idempotency: multiple issue_authorization_state() calls (same request_id)
4. Audit traceability: hg_event_source and hg_event_timestamp properly recorded

### Sandbox Pilot
1. Deploy to Sandbox DB
2. CLI approve with full HG-AS-01 payload
3. HTTP API approve with full payload
4. Verify authorization_state records created
5. Verify Sandbox runtime can query authorization_state
6. Verify Production runtime unaffected

---

## ROLLBACK PLAN

If Sandbox pilot fails:
1. Drop `authorization_state` table (Sandbox DB only)
2. Remove CLI extensions
3. Remove runtime read-only query
4. Revert to existing approval_token logic
5. No Production impact (never touched)

---

## HG-AS-01 COMPLIANCE CHECKLIST

- [x] Only Human Gate APPROVED events create Authorization State
- [x] governance_decision=PASS is NOT used as basis
- [x] hg_decision=AUTHORIZED is NOT used as basis
- [x] Runtime reads Authorization State as READ-ONLY only
- [x] AI/System cannot issue or escalate Authorization State
- [x] actor (granted_by) is recorded in payload
- [x] standing is explicitly set to "UNKNOWN"
- [x] Append-only enforcement via triggers
- [x] Sandbox-only; Production DB untouched
- [x] HG-A1~A7 unchanged
- [x] GL7 unchanged
- [x] Decision Record schema unchanged

---

**Status**: Ready for Sandbox Pilot Implementation  
**Next Decision**: HG-AS-02 (standing implementation; deferred)  
**Authority**: Human Gate Decision HG-AS-01

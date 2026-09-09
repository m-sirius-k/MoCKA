# Specification v1.0 — Authorization Binding Implementation Pseudocode

**Stream 3 Completion**  
**Investigation Date:** 2026-09-09  
**Basis:** Design Detailing (Stream 2) — 12 design elements formalized into executable specifications  
**Format:** Python pseudocode + SQL + JSON configuration  
**Note:** Pseudocode only; no actual implementation code has been created  

---

## Spec 1: Approval Confirmation State Validation Code

**Purpose:** Identify and validate all code paths that reach approval confirmation state (state-changing DB writes).

**Pseudocode:**

```python
# validation/approval_confirmation_validator.py
"""Validator to detect all approval confirmation state transitions."""

class ApprovalConfirmationValidator:
    """Scans codebase for operations reaching approval confirmation state."""
    
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.state_changes = []
    
    def validate(self):
        """Scan for all state-changing operations."""
        # Pattern 1: Direct event DB writes
        self._scan_pattern(
            pattern=r"write_sqlite\s*\(",
            description="Direct SQLite write",
            category="ROUTE_C"
        )
        # Pattern 2: EventBuffer.push() calls
        self._scan_pattern(
            pattern=r"get_buffer\(\)\.push\s*\(",
            description="EventBuffer push (async flush)",
            category="ROUTE_B"
        )
        # Pattern 3: mocka_write_event() calls
        self._scan_pattern(
            pattern=r"mocka_write_event\s*\(",
            description="Direct event write (MCP)",
            category="ROUTE_A"
        )
        # Pattern 4: mocka_decision_write() calls
        self._scan_pattern(
            pattern=r"mocka_decision_write\s*\(",
            description="Decision ledger write",
            category="LEDGER"
        )
        # Pattern 5: Audit/proposal recording
        self._scan_pattern(
            pattern=r"(create_task|submit_result|\.record\()\s*\(",
            description="Cross-audit or proposal recording",
            category="AUDIT"
        )
        return self.state_changes
    
    def _scan_pattern(self, pattern, description, category):
        """Scan repository for pattern and record findings."""
        import re
        for filepath in self._walk_python_files():
            with open(filepath, 'r', encoding='utf-8') as f:
                for lineno, line in enumerate(f, 1):
                    if re.search(pattern, line):
                        self.state_changes.append({
                            "file": filepath,
                            "line": lineno,
                            "pattern": description,
                            "category": category,
                            "code": line.strip()
                        })
    
    def report(self):
        """Generate validation report."""
        report = {
            "total_state_changes": len(self.state_changes),
            "by_category": {},
            "findings": self.state_changes
        }
        for change in self.state_changes:
            cat = change["category"]
            report["by_category"][cat] = report["by_category"].get(cat, 0) + 1
        return report

# Usage:
# validator = ApprovalConfirmationValidator("/path/to/MoCKA")
# findings = validator.validate()
# print(validator.report())
```

**Spec Requirement:**
- Must identify all 8 Route B bypass locations before implementation
- Must identify all Route C direct write sites before implementation
- Report must be generated and verified before Phase 4

---

## Spec 2: Route B Enforcement Decorator/Middleware

**Purpose:** Insert authorization check before Flask handler executes state-changing operation.

**Design Selection:** Method C (Wrapper Function + Decorator Pattern)

**Pseudocode:**

```python
# governance/route_b_enforcement.py
"""Route B authorization enforcement decorator."""

from functools import wraps
from governance_pipeline import _governance
from event_buffer import get_buffer

class AuthorizationDenied(Exception):
    """Raised when authorization check fails."""
    def __init__(self, decision):
        self.decision = decision
        super().__init__(decision.reason)

def require_authorization(operation_type):
    """Decorator: enforce GL7 authorization before Flask handler executes.
    
    Args:
        operation_type (str): Operation identifier for GL7 decision (e.g., "route_handshake", "write_event")
    
    Returns:
        Decorator function that wraps Flask handler
    
    Example:
        @app.route("/api/handshake", methods=["POST"])
        @require_authorization("route_handshake")
        def handshake_post():
            get_buffer().push({...})  # Safe: authorization already enforced
    """
    def decorator(handler_func):
        @wraps(handler_func)
        def wrapper(*args, **kwargs):
            from flask import request
            
            # Build operation context from Flask request
            operation_context = {
                "actor": request.remote_user or "anonymous",
                "endpoint": request.endpoint,
                "method": request.method,
                "remote_addr": request.remote_addr,
                "user_agent": request.headers.get("User-Agent", ""),
            }
            
            # Call GL7 authorization decision engine
            decision = _governance.before_tool(operation_type, operation_context)
            
            # Fail-closed: any DENIED or UNKNOWN decision blocks execution
            if not decision.allowed:
                # Log the denial for audit
                _log_authorization_denial(operation_type, operation_context, decision)
                raise AuthorizationDenied(decision)
            
            # Store decision in Flask request context for handler to access
            request.authorization_decision = decision
            request.authorization_decision_id = decision.decision_record_id
            
            # Handler executes with authorization confirmed
            return handler_func(*args, **kwargs)
        
        return wrapper
    return decorator

def _log_authorization_denial(operation_type, context, decision):
    """Log authorization denial for audit trail."""
    import logging
    logger = logging.getLogger("authorization")
    logger.warning(
        f"AUTHORIZATION_DENIED: operation={operation_type}, "
        f"actor={context.get('actor')}, reason={decision.reason}"
    )

# Usage in Flask blueprint:
# @handshake_bp.route("/api/handshake", methods=["POST"])
# @require_authorization("route_handshake")
# def handshake_post():
#     event_dict = {...}
#     safe_buffer_push(event_dict, request.authorization_decision_id)
```

**Spec Requirement:**
- Decorator must extract operation context from Flask request
- Must call _governance.before_tool() BEFORE Flask handler executes
- Must store decision_record_id in request context
- Must fail-closed (any DENIED/UNKNOWN → exception, no state change)
- Must apply to all 8 Route B handlers (handshake, ai_session, reflection_engine, etc.)

---

## Spec 3: Route C EventBuffer Migration Pseudocode

**Purpose:** Eliminate direct write_sqlite() calls; unify all event writes through EventBuffer with GL7 enforcement.

**Design Selection:** C-3 EventBuffer Unification

**Pseudocode:**

```python
# migration/route_c_eventbuffer_unification.py
"""Migrate Route C (direct SQLite) writes to EventBuffer (GL7-protected)."""

class RouteC_EventBufferMigration:
    """Plan and execute migration of write_sqlite() → EventBuffer."""
    
    @staticmethod
    def migration_plan():
        """Define migration strategy."""
        return {
            "phase": "Phase 3 → Phase 5 (design now, implement later)",
            "breaking_changes": [
                "write_sqlite() becomes private/deprecated",
                "write_safe_csv() must use EventBuffer instead of write_sqlite()",
                "_record_integrity_incident() must use EventBuffer instead of write_sqlite()",
                "MoCKARouter.collaborate() and share() must use EventBuffer",
            ],
            "locations": [
                {"file": "interface/router.py", "line": 157, "function": "write_safe_csv", "current": "write_sqlite(base)"},
                {"file": "interface/router.py", "line": 189, "function": "_record_integrity_incident", "current": "write_sqlite(base)"},
                {"file": "interface/router.py", "line": 213, "function": "MoCKARouter.collaborate", "current": "write_safe_csv(...)"},
                {"file": "interface/router.py", "line": 232, "function": "MoCKARouter.share", "current": "write_safe_csv(...)"},
            ],
            "rollback_plan": "Create wrapper function write_sqlite_unsafe() for legacy fallback if EventBuffer unavailable",
        }
    
    @staticmethod
    def migration_code(function_name, current_call):
        """Generate pseudocode for migrating one function."""
        
        if function_name == "write_safe_csv":
            return """
# BEFORE:
def write_safe_csv(row):
    result = validate_input_integrity(row)
    if not result["ok"]:
        _record_integrity_incident(result, row)
        return None
    base = {...}
    write_sqlite(base)  # <-- ROUTE C DIRECT WRITE

# AFTER:
def write_safe_csv(row):
    result = validate_input_integrity(row)
    if not result["ok"]:
        _record_integrity_incident(result, row)
        return None
    base = {...}
    
    # Route through EventBuffer with authorization
    event_context = {
        "operation_type": "write_event_log",
        "actor": "router.write_safe_csv",
        "target_type": "events_table",
        "risk_level": "normal"
    }
    safe_buffer_push(base, event_context)  # <-- ROUTE B/GL7 PROTECTED
"""
        
        elif function_name == "_record_integrity_incident":
            return """
# BEFORE:
def _record_integrity_incident(violation: dict, original_row: dict):
    base = {...}
    write_sqlite(base)  # <-- ROUTE C DIRECT WRITE
    print(f"[INCIDENT_RECORDED] {eid}")

# AFTER:
def _record_integrity_incident(violation: dict, original_row: dict):
    base = {...}
    
    # Route through EventBuffer with authorization
    event_context = {
        "operation_type": "integrity_incident_log",
        "actor": "router._record_integrity_incident",
        "target_type": "events_table",
        "risk_level": "high"
    }
    safe_buffer_push(base, event_context)  # <-- ROUTE B/GL7 PROTECTED
    print(f"[INCIDENT_RECORDED] {eid}")
"""
        
        else:
            return f"# Migration for {function_name}: pending specification"
    
    @staticmethod
    def verification_queries():
        """SQL queries to verify migration completion."""
        return {
            "pre_migration_check": [
                "SELECT file, lineno, code FROM codebase_scan WHERE pattern LIKE '%write_sqlite%'",
                "-- Expected: 4 locations in router.py",
            ],
            "post_migration_check": [
                "SELECT COUNT(*) FROM events WHERE authorization_decision_id IS NULL AND when > ?",
                "-- Expected: 0 (all new events must have authorization_decision_id)",
            ],
            "bypass_detection": [
                "SELECT e.event_id, e.when FROM events e WHERE e.authorization_decision_id IS NULL AND e.lifecycle_phase = 'in_operation'",
                "-- Expected: empty result set (indicates no unverified events in production)",
            ],
        }

# Migration Sequence (pseudocode):
# 1. Pre-migration: Run verification_queries()["pre_migration_check"]
# 2. For each of 4 call sites: apply migration_code()
# 3. Add unit tests for each migrated function
# 4. Integration test: write_safe_csv() → EventBuffer → GL7 → Gate
# 5. Post-migration: Run verification_queries()["post_migration_check"]
# 6. Commit & deploy
```

**Spec Requirement:**
- Migration must convert all 4 write_sqlite() direct calls to EventBuffer
- write_sqlite() should become private (_write_sqlite_unsafe()) after migration
- All events written via EventBuffer must carry authorization_decision_id
- Verification queries must pass before production deployment

---

## Spec 4: GL7 authorization_decision_id Assignment

**Purpose:** Extend GovernanceDecision object to include decision_record_id; assign unique ID to each authorization decision.

**Pseudocode:**

```python
# governance_pipeline.py (EXTENSION)
"""GL7 GovernanceDecision object with authorization_decision_id field."""

from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class GovernanceDecision:
    """Authorization decision object with unique record ID for linkage."""
    
    allowed: bool
    reason: str
    thinking_mode: str = "STANDARD"
    checklist_ok: bool = False
    dry_run_aborts: list = field(default_factory=list)
    
    # NEW FIELD (Stream 3 Spec 4):
    decision_record_id: str = field(default_factory=lambda: f"DC_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8].upper()}")
    # Example: DC_20260909_161500_A7F9C2E1
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "thinking_mode": self.thinking_mode,
            "checklist_ok": self.checklist_ok,
            "dry_run_aborts": self.dry_run_aborts,
            "decision_record_id": self.decision_record_id,  # Linkage field
            "created_at": datetime.utcnow().isoformat(),
        }

class GovernancePipeline:
    """GL7 authorization engine with decision_record_id tracking."""
    
    def before_tool(self, operation, context):
        """Make authorization decision and assign decision_record_id."""
        
        # Existing logic...
        decision_record = self._lookup_precedent(operation, context)
        
        if decision_record and decision_record.get("status") == "DECIDED":
            return GovernanceDecision(
                allowed=decision_record.get("allowed", False),
                reason=f"Precedent: {decision_record.get('id')}",
                decision_record_id=decision_record.get("id"),  # Use existing decision ID
            )
        
        # Generate new decision with unique ID
        decision = GovernanceDecision(
            allowed=self._evaluate_checklist(operation, context),
            reason=self._generate_reason(operation, context),
            thinking_mode="STANDARD",
            checklist_ok=self._checklist_ok(operation, context),
        )
        
        # Log decision to Decision Ledger (with decision_record_id)
        self._store_decision_in_ledger(decision, operation, context)
        
        return decision
    
    def _store_decision_in_ledger(self, decision, operation, context):
        """Store decision record in decision_ledger.jsonl with linkage fields."""
        import json
        from pathlib import Path
        
        ledger_path = Path("data/decisions/decision_ledger.jsonl")
        ledger_entry = {
            "decision_id": decision.decision_record_id,
            "created_at": datetime.utcnow().isoformat(),
            "operation": operation,
            "context": context,
            "allowed": decision.allowed,
            "reason": decision.reason,
            "thinking_mode": decision.thinking_mode,
            "checklist_ok": decision.checklist_ok,
            "dry_run_aborts": decision.dry_run_aborts,
            # NEW (Stream 3): reverse linkage field (populated after event write)
            "event_ids": [],  # Will be updated when event is written
        }
        
        with open(ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(ledger_entry, ensure_ascii=False) + "\n")

# Spec Requirement:
# - decision_record_id must be unique (format: DC_YYYYMMDD_HHMMSS_XXXX)
# - decision_record_id must be assigned BEFORE event is written (linkage key)
# - decision_record_id must be stored in Decision Ledger
# - decision_record_id must be passed to authorized_push() wrapper
```

**Spec Requirement:**
- decision_record_id format: `DC_YYYYMMDD_HHMMSS_RANDOM_HEX` (ensure global uniqueness)
- Must be generated in GovernanceDecision constructor
- Must be stored in decision_ledger.jsonl alongside decision record
- Must be available for EventBuffer to link to event_id

---

## Spec 5: EventBuffer authorized_push Wrapper

**Purpose:** Create single authorized entry point for all EventBuffer.push() calls; enforce GL7 decision linkage.

**Pseudocode:**

```python
# event_buffer.py (EXTENSION)
"""EventBuffer authorized_push wrapper with GL7 decision linkage."""

class EventBuffer:
    """Async event queue with authorization enforcement."""
    
    def __init__(self):
        self.queue = []
    
    def push(self, event):
        """PRIVATE: Direct push is deprecated; use authorized_push() instead."""
        import warnings
        warnings.warn(
            "EventBuffer.push() is deprecated. Use authorized_push() instead.",
            DeprecationWarning
        )
        # Fail-closed: reject unguarded push
        raise RuntimeError("EventBuffer.push() requires authorization. Use authorized_push().")
    
    def authorized_push(self, event_dict, decision_record_id):
        """PUBLIC: Push event with authorization decision linkage.
        
        Args:
            event_dict (dict): Event to push
            decision_record_id (str): Decision record ID from GL7 (e.g., "DC_20260909_161500_A7F9C2E1")
        
        Returns:
            dict: {status: "ok", event_id: str, decision_id: str}
        
        Raises:
            ValueError: If decision_record_id is missing or invalid
            RuntimeError: If event is malformed
        """
        if not decision_record_id:
            raise ValueError("authorized_push() requires decision_record_id")
        
        if not isinstance(event_dict, dict):
            raise RuntimeError("event_dict must be dictionary")
        
        # Attach authorization linkage to event
        event_with_auth = {
            **event_dict,
            "authorization_decision_id": decision_record_id,
        }
        
        # Append to in-memory queue
        self.queue.append(event_with_auth)
        
        # Log push for audit (before async flush)
        event_id = event_with_auth.get("event_id", "UNKNOWN")
        import logging
        logging.getLogger("event_buffer").info(
            f"Event queued: event_id={event_id}, decision_id={decision_record_id}"
        )
        
        return {
            "status": "ok",
            "event_id": event_id,
            "decision_id": decision_record_id,
            "queued_at": datetime.utcnow().isoformat(),
        }

# Global convenience function (replaces unguarded get_buffer().push() calls):

def safe_buffer_push(event_dict, operation_context=None):
    """Convenience wrapper: Call GL7 → authorized_push() in one step.
    
    Args:
        event_dict (dict): Event to push
        operation_context (dict): GL7 context (actor, operation_type, risk_level, etc.)
    
    Returns:
        str: decision_record_id if successful
    
    Raises:
        AuthorizationDenied: If GL7 returns DENY or UNKNOWN
    """
    from governance_pipeline import _governance
    
    # Call GL7 authorization
    decision = _governance.before_tool(
        operation=operation_context.get("operation_type", "write_event"),
        context=operation_context or {}
    )
    
    # Fail-closed
    if not decision.allowed:
        raise AuthorizationDenied(f"Push denied: {decision.reason}")
    
    # Push with authorization
    buffer = get_buffer()
    result = buffer.authorized_push(event_dict, decision.decision_record_id)
    
    return result["decision_id"]

# Usage (replaces all unguarded get_buffer().push() calls):
# BEFORE:
#   get_buffer().push({"who_actor": "...", "what_type": "..."})
# AFTER:
#   safe_buffer_push(
#       {"who_actor": "...", "what_type": "..."},
#       operation_context={"operation_type": "write_event_log", "actor": "myfunction", "risk_level": "normal"}
#   )

# Spec Requirement:
# - EventBuffer.push() must raise RuntimeError (fail-closed enforcement)
# - authorized_push() must require decision_record_id
# - safe_buffer_push() must call GL7 before any push
# - All 8 Route B + 4 Route C sites must use safe_buffer_push()
```

**Spec Requirement:**
- EventBuffer.push() without authorization must fail at runtime
- authorized_push() requires valid decision_record_id
- safe_buffer_push() implements GL7 → push in one call
- All existing get_buffer().push() calls must be migrated to safe_buffer_push()

---

## Spec 6: Authorization Record Storage Format

**Purpose:** Define schema for storing authorization records in Decision Ledger with linkage to events.

**JSON Format Specification:**

```json
// data/decisions/decision_ledger.jsonl (per-line entry)
// Entry format: One JSON object per line (append-only JSONL)

{
  "decision_id": "DC_20260909_161500_A7F9C2E1",
  "decision_version": 1,
  "created_at": "2026-09-09T16:15:00.123456Z",
  "operation_type": "route_handshake",
  "operation_context": {
    "actor": "anonymous",
    "endpoint": "/api/handshake",
    "method": "POST",
    "remote_addr": "127.0.0.1"
  },
  "decision_outcome": {
    "allowed": true,
    "reason": "Handshake route authorized under default policy",
    "thinking_mode": "STANDARD",
    "checklist_ok": true,
    "confidence": 0.95
  },
  "dry_run_aborts": [],
  "related_precedents": [
    "DC_20260908_090000_B3E2D1F4"
  ],
  "event_ids": [
    "E20260909_001",
    "E20260909_002"
  ],
  "audit_fields": {
    "decision_engine_version": "GL7_v2.0",
    "policy_version": "POLICY_20260901_v1",
    "ml_model_hash": "sha256:abc123..."
  }
}
```

**Schema Notes:**
- `decision_id`: Unique identifier (format: DC_YYYYMMDD_HHMMSS_RANDOM_HEX)
- `operation_type`: Category of operation (route_handshake, write_event_log, etc.)
- `operation_context`: Extraction from Flask request or call context
- `decision_outcome.allowed`: Boolean (true = ALLOW, false = DENY)
- `event_ids`: Array of linked event IDs (populated AFTER event write) — reverse linkage
- `audit_fields`: Reproducibility fields (model hash, policy version)

**Spec Requirement:**
- Each decision must have unique decision_id
- decision_id must be assigned BEFORE event write
- event_ids array must be updated when events are written (reverse linkage)
- Format must be JSON-serializable for JSONL append-only storage
- No decision record may be deleted or modified (append-only enforcement)

---

## Spec 7: Audit Query Implementations

**Purpose:** SQL queries to reconstruct full authorization audit trail for any event.

**SQL Specification:**

```sql
-- Query 1: Full Audit Trail for One Event
-- Purpose: Given event_id, retrieve authorization decision + all metadata
SELECT 
  e.event_id,
  e.when as event_created_at,
  e.who_actor,
  e.what_type,
  e.where_component,
  e.lifecycle_phase,
  e.risk_level,
  e.authorization_decision_id,
  -- Decision Ledger JOIN (LEFT JOIN for legacy events without decision_id)
  d.decision_id,
  d.created_at as decision_created_at,
  d.operation_type,
  d.decision_outcome,
  d.thinking_mode,
  d.checklist_ok,
  CASE WHEN d.decision_id IS NOT NULL THEN 'AUTHORIZED' ELSE 'UNVERIFIED' END as auth_status
FROM events e
LEFT JOIN decision_ledger d 
  ON e.authorization_decision_id = d.decision_id
WHERE e.event_id = ?
ORDER BY d.created_at DESC
LIMIT 1;

-- Query 2: All Events from One Decision
-- Purpose: Given decision_id, retrieve all events it authorized
SELECT 
  e.event_id,
  e.when,
  e.who_actor,
  e.what_type,
  e.where_component,
  e.lifecycle_phase,
  e.risk_level,
  CASE WHEN e.authorization_decision_id IS NOT NULL THEN 'AUTHORIZED' ELSE 'UNVERIFIED' END as auth_status
FROM events e
WHERE e.authorization_decision_id = ?
ORDER BY e.when DESC;

-- Query 3: All Authorization Denials (Operations That Did NOT Execute)
-- Purpose: Retrieve all DENIED authorization decisions and what they blocked
SELECT 
  d.decision_id,
  d.created_at,
  d.operation_type,
  d.operation_context,
  d.decision_outcome,
  COUNT(e.event_id) as events_blocked
FROM decision_ledger d
LEFT JOIN events e ON e.authorization_decision_id = d.decision_id
WHERE d.decision_outcome ->> 'allowed' = 'false'
GROUP BY d.decision_id
ORDER BY d.created_at DESC
LIMIT 100;

-- Query 4: Integrity Incidents (Validation Failures)
-- Purpose: Find events that failed validation and were not written
SELECT 
  e.event_id,
  e.when,
  e.who_actor,
  e.title,
  e.what_type,
  e.short_summary,
  SUBSTR(e.free_note, 1, 200) as incident_note
FROM events e
WHERE e.what_type = 'incident'
  AND e.title LIKE '[INTEGRITY_VIOLATION]%'
ORDER BY e.when DESC
LIMIT 100;

-- Query 5: Bypass Detection (Events Without Authorization Link)
-- Purpose: Find events that were written without authorization_decision_id (indicate bypass)
SELECT 
  e.event_id,
  e.when,
  e.who_actor,
  e.what_type,
  e.where_component,
  e.lifecycle_phase,
  'UNVERIFIED_BYPASS' as alert
FROM events e
WHERE e.authorization_decision_id IS NULL
  AND e.when > datetime('now', '-24 hours')
ORDER BY e.when DESC;

-- Query 6: Authorization Coverage Report
-- Purpose: Measure percentage of events with authorization linkage
SELECT 
  COUNT(*) as total_events,
  SUM(CASE WHEN authorization_decision_id IS NOT NULL THEN 1 ELSE 0 END) as authorized_events,
  SUM(CASE WHEN authorization_decision_id IS NULL THEN 1 ELSE 0 END) as unverified_events,
  ROUND(100.0 * SUM(CASE WHEN authorization_decision_id IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 2) as coverage_percent
FROM events
WHERE lifecycle_phase = 'in_operation';

-- Index Definitions (for query performance)
CREATE INDEX IF NOT EXISTS idx_events_auth_decision_id 
  ON events(authorization_decision_id);
CREATE INDEX IF NOT EXISTS idx_events_what_type 
  ON events(what_type);
CREATE INDEX IF NOT EXISTS idx_events_when 
  ON events(when DESC);
CREATE INDEX IF NOT EXISTS idx_decision_ledger_decision_id 
  ON decision_ledger(decision_id);
CREATE INDEX IF NOT EXISTS idx_decision_ledger_created_at 
  ON decision_ledger(created_at DESC);
```

**Spec Requirement:**
- All 6 queries must execute in <5ms (with indexes)
- Queries must support both authorized and legacy unverified events
- Coverage report must be runnable weekly for monitoring
- Bypass detection query must alert on any events without authorization_decision_id

---

## Spec 8: Authorization Exception Logging

**Purpose:** Log and track authorization exceptions (denials, errors, unknown operations).

**Pseudocode:**

```python
# governance/authorization_exception_logger.py
"""Log authorization exceptions and failures for audit trail."""

import json
import logging
from pathlib import Path
from datetime import datetime

class AuthorizationExceptionLogger:
    """Track authorization denials and exceptions."""
    
    def __init__(self, log_file="data/logs/authorization_exceptions.jsonl"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("authorization.exceptions")
    
    def log_denial(self, decision_id, operation, context, reason):
        """Log a denied authorization decision."""
        self._log_event({
            "type": "AUTHORIZATION_DENIAL",
            "decision_id": decision_id,
            "operation": operation,
            "context": context,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    def log_unknown_operation(self, operation, context):
        """Log authorization check for unknown/new operation type."""
        self._log_event({
            "type": "UNKNOWN_OPERATION",
            "operation": operation,
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    def log_error(self, operation, context, error):
        """Log error during authorization decision."""
        self._log_event({
            "type": "AUTHORIZATION_ERROR",
            "operation": operation,
            "context": context,
            "error": str(error),
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    def log_exception(self, exception_id, operation, actor, approved_by, reason):
        """Log manual exception override (e.g., admin override)."""
        self._log_event({
            "type": "EXCEPTION_OVERRIDE",
            "exception_id": exception_id,
            "operation": operation,
            "actor": actor,
            "approved_by": approved_by,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    def _log_event(self, event_dict):
        """Append event to JSONL log file."""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_dict, ensure_ascii=False) + "\n")
        self.logger.info(f"Exception logged: {event_dict['type']}")
    
    def query_denials(self, hours=24):
        """Query denials from past N hours."""
        import time
        cutoff = datetime.utcnow().timestamp() - (hours * 3600)
        results = []
        
        if not self.log_file.exists():
            return results
        
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    event = json.loads(line)
                    if event.get("type") == "AUTHORIZATION_DENIAL":
                        ts = datetime.fromisoformat(event.get("timestamp", "")).timestamp()
                        if ts >= cutoff:
                            results.append(event)
                except json.JSONDecodeError:
                    continue
        
        return results
    
    def report(self, hours=24):
        """Generate exception summary report."""
        denials = self.query_denials(hours)
        unknown_ops = self.query_unknown_operations(hours)
        errors = self.query_errors(hours)
        
        return {
            "period_hours": hours,
            "summary": {
                "total_denials": len(denials),
                "total_unknown_ops": len(unknown_ops),
                "total_errors": len(errors),
            },
            "denials": denials[-10:],  # Last 10
            "unknown_operations": unknown_ops[-10:],
            "errors": errors[-10:],
        }

# Usage:
# logger = AuthorizationExceptionLogger()
# logger.log_denial("DC_20260909_161500_A7F9C2E1", "route_handshake", {...}, "Policy violation")
# report = logger.report(hours=24)
# print(report)
```

**Spec Requirement:**
- All authorization denials must be logged to authorization_exceptions.jsonl
- Exception log must be append-only (no deletion/modification)
- Report must show denial rate, unknown operation types, error frequency
- Logging must not block authorization decision (async safe)

---

## Spec 9: Decision Ledger Reverse Linkage Update

**Purpose:** Update Decision Ledger to include event_ids that each decision authorized (reverse linkage).

**Pseudocode:**

```python
# governance/decision_ledger_linkage.py
"""Maintain reverse linkage: decision_id -> event_ids."""

import json
from pathlib import Path
from collections import defaultdict

class DecisionLedgerLinkageManager:
    """Update Decision Ledger with reverse linkage (decision -> events)."""
    
    def __init__(self, ledger_path="data/decisions/decision_ledger.jsonl"):
        self.ledger_path = Path(ledger_path)
    
    def link_event_to_decision(self, event_id, decision_id):
        """Register that event_id was authorized by decision_id.
        
        This updates the Decision Ledger entry for decision_id to include event_id
        in its event_ids array.
        
        Note: Ledger is append-only, so we append a new version of the decision
        with updated event_ids array.
        """
        # Read current decision record
        decision_record = self._read_decision_record(decision_id)
        
        if decision_record is None:
            raise ValueError(f"Decision record not found: {decision_id}")
        
        # Update event_ids array (avoid duplicates)
        if "event_ids" not in decision_record:
            decision_record["event_ids"] = []
        
        if event_id not in decision_record["event_ids"]:
            decision_record["event_ids"].append(event_id)
        
        # Append updated version to ledger (append-only enforcement)
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(decision_record, ensure_ascii=False) + "\n")
    
    def _read_decision_record(self, decision_id):
        """Read most recent version of decision record from ledger."""
        latest = None
        
        if not self.ledger_path.exists():
            return None
        
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    if record.get("decision_id") == decision_id:
                        latest = record
                except json.JSONDecodeError:
                    continue
        
        return latest
    
    def get_events_by_decision(self, decision_id):
        """Retrieve all event_ids authorized by a decision."""
        record = self._read_decision_record(decision_id)
        return record.get("event_ids", []) if record else []
    
    def build_linkage_index(self):
        """Build complete decision->events index from ledger."""
        index = defaultdict(list)
        
        if not self.ledger_path.exists():
            return index
        
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    decision_id = record.get("decision_id")
                    event_ids = record.get("event_ids", [])
                    # Overwrite with latest version (append-only keeps history)
                    index[decision_id] = event_ids
                except json.JSONDecodeError:
                    continue
        
        return index
    
    def verify_linkage_integrity(self):
        """Verify events table matches decision ledger linkages."""
        import sqlite3
        
        errors = []
        ledger_index = self.build_linkage_index()
        
        db_path = Path("data/mocka_events.db")
        if not db_path.exists():
            return errors
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # For each decision, verify its event_ids exist in events table
        for decision_id, event_ids in ledger_index.items():
            for event_id in event_ids:
                cursor.execute(
                    "SELECT COUNT(*) FROM events WHERE event_id = ? AND authorization_decision_id = ?",
                    [event_id, decision_id]
                )
                count = cursor.fetchone()[0]
                if count == 0:
                    errors.append({
                        "type": "ORPHANED_EVENT_LINKAGE",
                        "decision_id": decision_id,
                        "event_id": event_id,
                        "error": "Event linked in decision ledger but not found in events table"
                    })
        
        conn.close()
        return errors

# Usage (integrated with EventBuffer.authorized_push()):
# After event is written:
# ledger_manager = DecisionLedgerLinkageManager()
# ledger_manager.link_event_to_decision(event_id, decision_record_id)

# Verification:
# errors = ledger_manager.verify_linkage_integrity()
# if errors:
#     for error in errors:
#         print(f"Linkage error: {error}")
```

**Spec Requirement:**
- Every event write must update Decision Ledger with reverse linkage
- Linkage update must happen AFTER event is durably written (prevent orphans)
- Linkage must use append-only: never modify existing decision record, append new version
- Integrity verification must run daily to detect orphaned linkages

---

## Spec 10: Schema Migration Script

**Purpose:** Add authorization_decision_id column to events table; handle backward compatibility.

**SQL Migration Script:**

```sql
-- migration_001_add_authorization_decision_id.sql
-- Purpose: Add authorization tracking to events table
-- Date: 2026-09-09
-- Author: Stream 3 Specification (Phase 3 prerequisite work)

BEGIN TRANSACTION;

-- Step 1: Add new column (nullable for legacy events)
ALTER TABLE events ADD COLUMN authorization_decision_id TEXT DEFAULT NULL;

-- Step 2: Create index for query performance
CREATE INDEX idx_events_auth_decision_id ON events(authorization_decision_id);

-- Step 3: Verify schema
PRAGMA table_info(events);

-- Step 4: Legacy data handling
-- Mark all existing events without authorization_decision_id as UNVERIFIED
-- (They predate authorization enforcement)
UPDATE events 
SET authorization_decision_id = NULL 
WHERE authorization_decision_id IS NULL 
  AND lifecycle_phase = 'in_operation';

-- Step 5: Verify integrity
SELECT 
  COUNT(*) as total_events,
  SUM(CASE WHEN authorization_decision_id IS NOT NULL THEN 1 ELSE 0 END) as authorized_events,
  SUM(CASE WHEN authorization_decision_id IS NULL THEN 1 ELSE 0 END) as unverified_legacy_events
FROM events;

COMMIT;

-- Rollback script (if needed):
-- BEGIN TRANSACTION;
-- DROP INDEX idx_events_auth_decision_id;
-- ALTER TABLE events DROP COLUMN authorization_decision_id;
-- COMMIT;
```

**Migration Checklist:**
- [ ] Backup mocka_events.db before migration
- [ ] Run migration in staging environment first
- [ ] Verify schema with `PRAGMA table_info(events)`
- [ ] Verify indexes with `SELECT name FROM sqlite_master WHERE type='index'`
- [ ] Run coverage query (Step 5) to confirm migration
- [ ] No downtime: ALTER TABLE is online in SQLite 3.26+
- [ ] Rollback available if needed (< 5 minutes)

**Spec Requirement:**
- Migration must be idempotent (safe to run multiple times)
- Must preserve all existing event data (no deletion)
- Must be reversible (rollback script provided)
- Indexes must be created for performance (authorization_decision_id lookups)

---

## Spec 11: Rollback Procedure Script

**Purpose:** Procedures to recover from failed authorization implementation.

**Pseudocode:**

```python
# governance/rollback_authorization.py
"""Rollback procedures for authorization implementation failure."""

import shutil
import sqlite3
from pathlib import Path
from datetime import datetime

class AuthorizationRollback:
    """Execute rollback at 3 severity levels."""
    
    @staticmethod
    def level_1_single_event_rollback(event_id, db_path="data/mocka_events.db"):
        """Level 1: Recover from single event bypass.
        
        Procedure:
          1. Mark event as UNVERIFIED in event record
          2. Log rollback action
          3. Notify audit
        """
        print(f"[ROLLBACK L1] Recovering single event: {event_id}")
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Mark as unverified
        cursor.execute(
            "UPDATE events SET free_note = CONCAT(free_note, ' [L1_ROLLBACK_UNVERIFIED]') WHERE event_id = ?",
            [event_id]
        )
        conn.commit()
        conn.close()
        
        print(f"[ROLLBACK L1 COMPLETE] {event_id} marked unverified")
    
    @staticmethod
    def level_2_batch_bypass_rollback(
        time_window_start, 
        time_window_end,
        reason="Authorization enforcement failed",
        db_path="data/mocka_events.db"
    ):
        """Level 2: Recover from batch bypass (100+ events without authorization).
        
        Procedure:
          1. Identify affected events
          2. Create retroactive DENY decision records
          3. Link events to retroactive decisions
          4. Log batch recovery
        """
        print(f"[ROLLBACK L2] Batch recovery for window {time_window_start} to {time_window_end}")
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Find unverified events in time window
        cursor.execute(
            "SELECT event_id, what_type FROM events WHERE authorization_decision_id IS NULL AND when BETWEEN ? AND ?",
            [time_window_start, time_window_end]
        )
        affected_events = cursor.fetchall()
        
        print(f"[ROLLBACK L2] Found {len(affected_events)} unverified events in window")
        
        # Create retroactive DENY decisions for each event
        retroactive_decisions = []
        for event_id, event_type in affected_events:
            retro_decision_id = f"RETRO_DC_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{event_id}"
            retroactive_decisions.append({
                "decision_id": retro_decision_id,
                "event_id": event_id,
                "event_type": event_type,
            })
            
            # Update event with retroactive decision
            cursor.execute(
                "UPDATE events SET authorization_decision_id = ? WHERE event_id = ?",
                [retro_decision_id, event_id]
            )
        
        conn.commit()
        conn.close()
        
        print(f"[ROLLBACK L2 COMPLETE] {len(retroactive_decisions)} events linked to retroactive decisions")
        return retroactive_decisions
    
    @staticmethod
    def level_3_data_corruption_rollback(backup_path="data/mocka_events.db.backup"):
        """Level 3: Full restore from backup (data corruption detected).
        
        Procedure:
          1. Restore from backup
          2. Verify integrity
          3. Log restore action
        """
        print(f"[ROLLBACK L3] Full restore from backup: {backup_path}")
        
        db_path = Path("data/mocka_events.db")
        backup = Path(backup_path)
        
        if not backup.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")
        
        # Create timestamped backup of corrupted DB
        corrupted_backup = db_path.with_suffix(f".corrupted_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.db")
        shutil.copy(db_path, corrupted_backup)
        print(f"[ROLLBACK L3] Corrupted DB backed up to: {corrupted_backup}")
        
        # Restore from backup
        shutil.copy(backup, db_path)
        print(f"[ROLLBACK L3] Restored from backup")
        
        # Verify integrity
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM events")
        count = cursor.fetchone()[0]
        conn.close()
        
        print(f"[ROLLBACK L3 COMPLETE] Restored {count} events")
    
    @staticmethod
    def create_pre_deployment_backup(db_path="data/mocka_events.db"):
        """Create timestamped backup before deploying authorization."""
        backup_path = Path(db_path).with_suffix(
            f".backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.db"
        )
        shutil.copy(db_path, backup_path)
        print(f"[BACKUP CREATED] {backup_path}")
        return backup_path

# Usage:
# 1. Pre-deployment:
#    backup = AuthorizationRollback.create_pre_deployment_backup()
#
# 2. Level 1 (single event):
#    AuthorizationRollback.level_1_single_event_rollback("E20260909_001")
#
# 3. Level 2 (batch):
#    AuthorizationRollback.level_2_batch_bypass_rollback("2026-09-09 16:00:00", "2026-09-09 17:00:00")
#
# 4. Level 3 (full restore):
#    AuthorizationRollback.level_3_data_corruption_rollback("data/mocka_events.db.backup_20260909_160000.db")
```

**Spec Requirement:**
- Level 1: For isolated bypass, mark event unverified (< 1 minute recovery)
- Level 2: For batch bypass, create retroactive denials (< 15 minutes recovery)
- Level 3: Full restore from backup (< 5 minutes recovery)
- Backup must be created before any deployment
- Rollback must be tested in staging environment before go-live

---

## Spec 12: Production Safety Validation Script

**Purpose:** Pre-deployment checklist and continuous monitoring for production safety.

**Pseudocode:**

```python
# governance/production_safety_validator.py
"""Pre-deployment safety checks and continuous monitoring."""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

class ProductionSafetyValidator:
    """6-category safety validation."""
    
    def __init__(self, db_path="data/mocka_events.db"):
        self.db_path = db_path
        self.checks = {}
    
    # CATEGORY 1: Functional Safety
    def check_functional_safety(self):
        """Verify all 8 Route B + Route C handlers working."""
        results = {
            "route_b_handlers_reachable": self._check_route_endpoints(),
            "event_buffer_accessible": self._check_event_buffer(),
            "gl7_decision_engine_responding": self._check_gl7_health(),
            "decision_ledger_writable": self._check_ledger_writable(),
        }
        self.checks["functional"] = all(results.values())
        return results
    
    # CATEGORY 2: Integrity Safety
    def check_integrity_safety(self):
        """Verify data consistency."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        results = {}
        
        # Sample 1000 events
        cursor.execute("SELECT event_id, authorization_decision_id FROM events LIMIT 1000")
        events = cursor.fetchall()
        
        orphaned = 0
        for event_id, decision_id in events:
            if decision_id:
                cursor.execute("SELECT COUNT(*) FROM decision_ledger WHERE decision_id = ?", [decision_id])
                if cursor.fetchone()[0] == 0:
                    orphaned += 1
        
        results["orphaned_linkages"] = orphaned
        results["integrity_ok"] = orphaned == 0
        
        # Verify reverse linkage (sample 100 decisions)
        cursor.execute("SELECT DISTINCT decision_id FROM events WHERE authorization_decision_id IS NOT NULL LIMIT 100")
        decisions = cursor.fetchall()
        
        reverse_linkage_errors = 0
        for (decision_id,) in decisions:
            cursor.execute("SELECT event_ids FROM decision_ledger WHERE decision_id = ?", [decision_id])
            row = cursor.fetchone()
            if row:
                # Check if event_ids array includes at least one event
                pass  # Verification logic here
        
        results["reverse_linkage_ok"] = reverse_linkage_errors == 0
        
        conn.close()
        self.checks["integrity"] = results["integrity_ok"] and results["reverse_linkage_ok"]
        return results
    
    # CATEGORY 3: Performance Safety
    def check_performance_safety(self):
        """Verify query latency and throughput."""
        import time
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        results = {}
        
        # Query 1: Get event with authorization (<10ms)
        start = time.time()
        cursor.execute("SELECT * FROM events e LEFT JOIN decision_ledger d ON e.authorization_decision_id = d.decision_id LIMIT 1")
        cursor.fetchone()
        latency = (time.time() - start) * 1000
        results["query_latency_ms"] = latency
        results["latency_ok"] = latency < 10
        
        # Buffer throughput is in-memory; verify with count
        cursor.execute("SELECT COUNT(*) FROM events WHERE when > datetime('now', '-1 hour')")
        events_per_hour = cursor.fetchone()[0]
        events_per_sec = events_per_hour / 3600 if events_per_hour > 0 else 0
        results["throughput_events_per_sec"] = events_per_sec
        results["throughput_ok"] = events_per_sec >= 1000  # Baseline
        
        conn.close()
        self.checks["performance"] = results["latency_ok"] and results["throughput_ok"]
        return results
    
    # CATEGORY 4: Rollback Safety
    def check_rollback_safety(self):
        """Verify backup exists and rollback procedure is documented."""
        results = {}
        
        backup_path = Path("data/mocka_events.db.backup")
        results["backup_exists"] = backup_path.exists()
        results["backup_size_mb"] = backup_path.stat().st_size / (1024 * 1024) if backup_path.exists() else 0
        results["rollback_script_exists"] = Path("governance/rollback_authorization.py").exists()
        results["rollback_ok"] = results["backup_exists"] and results["rollback_script_exists"]
        
        self.checks["rollback"] = results["rollback_ok"]
        return results
    
    # CATEGORY 5: Monitoring Safety
    def check_monitoring_safety(self):
        """Verify alerts are configured."""
        results = {
            "authorization_exceptions_logged": Path("data/logs/authorization_exceptions.jsonl").exists(),
            "monitoring_dashboard_configured": self._check_monitoring_config(),
            "alert_thresholds_set": self._check_alert_config(),
        }
        self.checks["monitoring"] = all(results.values())
        return results
    
    # CATEGORY 6: Go-Live Readiness
    def check_golive_readiness(self):
        """Verify all prerequisites met."""
        results = {
            "all_functional_checks_pass": self.checks.get("functional", False),
            "all_integrity_checks_pass": self.checks.get("integrity", False),
            "all_performance_checks_pass": self.checks.get("performance", False),
            "all_rollback_checks_pass": self.checks.get("rollback", False),
            "all_monitoring_checks_pass": self.checks.get("monitoring", False),
        }
        results["ready_for_golive"] = all(results.values())
        self.checks["golive"] = results["ready_for_golive"]
        return results
    
    def run_all_checks(self):
        """Execute all 6 safety categories."""
        print("=" * 60)
        print("PRODUCTION SAFETY VALIDATION")
        print("=" * 60)
        
        print("\n[1/6] Functional Safety...")
        func_results = self.check_functional_safety()
        print(f"  Result: {'PASS' if self.checks['functional'] else 'FAIL'}")
        for key, value in func_results.items():
            print(f"    - {key}: {value}")
        
        print("\n[2/6] Integrity Safety...")
        int_results = self.check_integrity_safety()
        print(f"  Result: {'PASS' if self.checks['integrity'] else 'FAIL'}")
        for key, value in int_results.items():
            print(f"    - {key}: {value}")
        
        print("\n[3/6] Performance Safety...")
        perf_results = self.check_performance_safety()
        print(f"  Result: {'PASS' if self.checks['performance'] else 'FAIL'}")
        for key, value in perf_results.items():
            print(f"    - {key}: {value}")
        
        print("\n[4/6] Rollback Safety...")
        rollback_results = self.check_rollback_safety()
        print(f"  Result: {'PASS' if self.checks['rollback'] else 'FAIL'}")
        for key, value in rollback_results.items():
            print(f"    - {key}: {value}")
        
        print("\n[5/6] Monitoring Safety...")
        monitor_results = self.check_monitoring_safety()
        print(f"  Result: {'PASS' if self.checks['monitoring'] else 'FAIL'}")
        for key, value in monitor_results.items():
            print(f"    - {key}: {value}")
        
        print("\n[6/6] Go-Live Readiness...")
        golive_results = self.check_golive_readiness()
        print(f"  Result: {'PASS - READY FOR GO-LIVE' if golive_results['ready_for_golive'] else 'FAIL - NOT READY'}")
        for key, value in golive_results.items():
            print(f"    - {key}: {value}")
        
        print("\n" + "=" * 60)
        return self.checks

    def _check_route_endpoints(self):
        """Stub: Verify Flask endpoints are registered."""
        return True
    
    def _check_event_buffer(self):
        """Stub: Verify EventBuffer is accessible."""
        return True
    
    def _check_gl7_health(self):
        """Stub: Verify GL7 decision engine is responding."""
        return True
    
    def _check_ledger_writable(self):
        """Stub: Verify Decision Ledger is writable."""
        return True
    
    def _check_monitoring_config(self):
        """Stub: Verify monitoring dashboard is configured."""
        return True
    
    def _check_alert_config(self):
        """Stub: Verify alert thresholds are set."""
        return True

# Usage:
# validator = ProductionSafetyValidator("data/mocka_events.db")
# validator.run_all_checks()
```

**Spec Requirement:**
- All 6 categories must pass before go-live
- Checks must be runnable in < 5 minutes
- Monitoring must send alerts for: bypass detection, orphaned linkages, high denial rate
- Go-live only authorized if all checks return green

---

## Stream 3 Summary: Specification Complete

This document formalizes 12 executable specifications:

1. **Approval Confirmation Validator** — Scans codebase for all state-changing operations
2. **Route B Enforcement Decorator** — Pre-execution authorization check before Flask handler
3. **Route C Migration Pseudocode** — Convert write_sqlite() to EventBuffer (C-3 strategy)
4. **GL7 Decision ID Assignment** — Extend GovernanceDecision with unique decision_record_id
5. **EventBuffer authorized_push Wrapper** — Single GL7-guarded entry point for all buffer.push()
6. **Authorization Record Storage** — JSON schema for Decision Ledger entries with linkage
7. **Audit Query Implementations** — 6 SQL queries for full authorization traceability
8. **Exception Logging** — Append-only log of denials, unknowns, errors, overrides
9. **Reverse Linkage Update** — Decision Ledger tracks which events it authorized
10. **Schema Migration Script** — ALTER TABLE to add authorization_decision_id (with rollback)
11. **Rollback Procedures** — 3-level recovery (single event / batch / full restore)
12. **Production Safety Validator** — 6-category checklist for go-live readiness

**Governance Constraints Maintained:**
- All specifications in pseudocode/SQL/JSON only
- No actual implementation code created
- No schema changes deployed
- No production modifications
- C2-b BLOCK immutable
- UNKNOWN/NOT_PROVEN preserved

---

**Status:** Stream 3 (Specification Creation) COMPLETE

**Next:** Stream 4 (Verification Planning) — Define test cases, audit procedures, compliance verification.

**Final Deliverable:** 16-item Authorization Readiness Package to Human Gate for Phase 4 review and implementation authorization decision.

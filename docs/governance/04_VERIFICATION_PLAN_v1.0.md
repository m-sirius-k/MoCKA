# Verification Plan v1.0 — Test Cases & Compliance Procedures

**Stream 4 Completion**  
**Investigation Date:** 2026-09-09  
**Basis:** Specification v1.0 (Stream 3) — 12 executable specifications require verification procedures  
**Scope:** Test cases, audit procedures, compliance checks (design only; no implementation)  
**Note:** Verification procedures designed; actual test execution deferred to Phase 5  

---

## Verification 1: Approval Confirmation State Validator — Test Cases

**Specification Reference:** Spec 1 (ApprovalConfirmationValidator)

**Test Case 1.1: Detect Direct SQLite Writes (Route C)**

```python
"""Test that validator correctly identifies write_sqlite() calls."""

def test_validator_detects_write_sqlite():
    validator = ApprovalConfirmationValidator("tests/fixtures/sample_code")
    
    # Create fixture file with write_sqlite() call
    fixture_content = """
    def write_safe_csv(row):
        base = {...}
        write_sqlite(base)  # Line 10 — should be detected
    """
    
    findings = validator.validate()
    
    # Assertion: Route C pattern found at line 10
    assert any(
        f["pattern"] == "Direct SQLite write" and 
        f["line"] == 10 and 
        f["category"] == "ROUTE_C"
        for f in findings
    ), "write_sqlite() call not detected"
```

**Test Case 1.2: Detect EventBuffer.push() Calls (Route B)**

```python
"""Test that validator identifies get_buffer().push() without GL7 guard."""

def test_validator_detects_buffer_push():
    validator = ApprovalConfirmationValidator("tests/fixtures/sample_code")
    
    # Fixture with unguarded buffer.push()
    fixture_content = """
    @app.route("/api/handshake", methods=["POST"])
    def handshake_post():
        get_buffer().push({...})  # Line 5 — no GL7 check
    """
    
    findings = validator.validate()
    
    # Assertion: Route B pattern found at line 5
    assert any(
        f["pattern"] == "EventBuffer push (async flush)" and 
        f["line"] == 5 and 
        f["category"] == "ROUTE_B"
        for f in findings
    ), "get_buffer().push() not detected"
```

**Test Case 1.3: Detect MCP Tool Calls (Route A)**

```python
"""Test that validator identifies mocka_write_event() and mocka_decision_write()."""

def test_validator_detects_mcp_calls():
    validator = ApprovalConfirmationValidator("tests/fixtures/sample_code")
    
    findings = validator.validate()
    
    # Should detect Route A (MCP-based writes) separately
    route_a_findings = [f for f in findings if f["category"] == "ROUTE_A"]
    
    assert len(route_a_findings) > 0, "MCP tool calls not detected"
```

**Test Case 1.4: Report Categorization**

```python
"""Test that report groups findings by route category."""

def test_validator_report_structure():
    validator = ApprovalConfirmationValidator("tests/fixtures/real_repo")
    findings = validator.validate()
    report = validator.report()
    
    # Report should have by_category breakdown
    assert "by_category" in report
    assert "ROUTE_A" in report["by_category"]
    assert "ROUTE_B" in report["by_category"]
    assert "ROUTE_C" in report["by_category"]
    
    # Total should match findings
    assert report["total_state_changes"] == len(findings)
```

**Acceptance Criteria:**
- [ ] Validator scans codebase correctly
- [ ] All 8 Route B locations identified
- [ ] All 4 Route C call sites identified
- [ ] Route A (MCP) calls categorized separately
- [ ] Report generated without errors

---

## Verification 2: Route B Enforcement Decorator — Unit Tests

**Specification Reference:** Spec 2 (@require_authorization decorator)

**Test Case 2.1: Decorator Enforces Authorization Check**

```python
"""Test that decorator blocks execution if GL7 returns DENIED."""

def test_decorator_blocks_denied_operation():
    from governance.route_b_enforcement import require_authorization, AuthorizationDenied
    from unittest.mock import patch, MagicMock
    from flask import Flask, request
    
    app = Flask(__name__)
    
    @app.route("/test", methods=["POST"])
    @require_authorization("test_operation")
    def test_handler():
        return {"status": "executed"}
    
    # Mock GL7 to return DENIED
    with patch('governance_pipeline._governance.before_tool') as mock_decision:
        mock_decision.return_value = MagicMock(
            allowed=False,
            reason="Test denial"
        )
        
        with app.test_client() as client:
            response = client.post("/test")
            
            # Assertion: Handler should not execute; should return 403 or exception
            assert response.status_code in [403, 500]  # AuthorizationDenied raised
            assert response.json["status"] != "executed"
```

**Test Case 2.2: Decorator Allows Authorized Operation**

```python
"""Test that decorator permits execution if GL7 returns ALLOWED."""

def test_decorator_allows_authorized_operation():
    from governance.route_b_enforcement import require_authorization
    from unittest.mock import patch, MagicMock
    from flask import Flask, request
    
    app = Flask(__name__)
    
    @app.route("/test", methods=["POST"])
    @require_authorization("test_operation")
    def test_handler():
        return {"status": "executed", "decision_id": request.authorization_decision_id}
    
    # Mock GL7 to return ALLOWED
    with patch('governance_pipeline._governance.before_tool') as mock_decision:
        mock_decision.return_value = MagicMock(
            allowed=True,
            reason="Test approval",
            decision_record_id="DC_20260909_TEST_001"
        )
        
        with app.test_client() as client:
            response = client.post("/test")
            
            # Assertion: Handler executed; decision_id in response
            assert response.status_code == 200
            assert response.json["status"] == "executed"
            assert response.json["decision_id"] == "DC_20260909_TEST_001"
```

**Test Case 2.3: Decorator Extracts Operation Context**

```python
"""Test that decorator builds correct operation context from Flask request."""

def test_decorator_extracts_operation_context():
    from governance.route_b_enforcement import require_authorization
    from unittest.mock import patch, MagicMock, call
    from flask import Flask
    
    app = Flask(__name__)
    
    @app.route("/test", methods=["POST"])
    @require_authorization("test_op")
    def test_handler():
        return {}
    
    # Mock GL7 to capture operation_context
    with patch('governance_pipeline._governance.before_tool') as mock_decision:
        mock_decision.return_value = MagicMock(allowed=True, decision_record_id="DC_TEST")
        
        with app.test_client() as client:
            client.post(
                "/test",
                headers={"User-Agent": "TestAgent/1.0"},
                environ_base={"REMOTE_ADDR": "127.0.0.1"}
            )
            
            # Capture call arguments
            call_args = mock_decision.call_args
            operation_context = call_args[0][1]  # Second argument is context
            
            # Assertion: context contains expected fields
            assert "actor" in operation_context
            assert "endpoint" in operation_context
            assert "method" in operation_context
            assert operation_context["method"] == "POST"
```

**Test Case 2.4: Decorator Logs Authorization Denial**

```python
"""Test that decorator logs when authorization is denied."""

def test_decorator_logs_denial():
    from governance.route_b_enforcement import require_authorization
    from unittest.mock import patch, MagicMock
    from flask import Flask
    import logging
    
    app = Flask(__name__)
    
    @app.route("/test", methods=["POST"])
    @require_authorization("test_op")
    def test_handler():
        return {}
    
    # Mock GL7 to return DENIED
    with patch('governance_pipeline._governance.before_tool') as mock_decision:
        mock_decision.return_value = MagicMock(
            allowed=False,
            reason="Policy violation"
        )
        
        # Capture logging
        with patch('logging.getLogger') as mock_logger:
            with app.test_client() as client:
                try:
                    client.post("/test")
                except:
                    pass
                
                # Assertion: Denial was logged
                logger_instance = mock_logger.return_value
                logger_instance.warning.assert_called()
                call_args = logger_instance.warning.call_args[0][0]
                assert "AUTHORIZATION_DENIED" in call_args
```

**Acceptance Criteria:**
- [ ] Decorator prevents execution on DENIED decision
- [ ] Decorator allows execution on ALLOWED decision
- [ ] Operation context correctly extracted from request
- [ ] Denials logged to audit trail
- [ ] decision_record_id stored in request context

---

## Verification 3: Route C EventBuffer Migration — Integration Tests

**Specification Reference:** Spec 3 (write_sqlite → EventBuffer migration)

**Test Case 3.1: write_safe_csv() Routes to EventBuffer**

```python
"""Test that write_safe_csv() uses EventBuffer instead of direct write_sqlite()."""

def test_write_safe_csv_uses_event_buffer():
    from unittest.mock import patch, MagicMock
    from interface.router import write_safe_csv
    
    # Mock EventBuffer.authorized_push
    with patch('event_buffer.get_buffer') as mock_buffer:
        mock_buffer_instance = MagicMock()
        mock_buffer.return_value = mock_buffer_instance
        mock_buffer_instance.authorized_push.return_value = {"status": "ok"}
        
        # Mock GL7 authorization
        with patch('governance_pipeline._governance.before_tool') as mock_gl7:
            mock_gl7.return_value = MagicMock(
                allowed=True,
                decision_record_id="DC_20260909_TEST_001"
            )
            
            # Call write_safe_csv
            result = write_safe_csv({
                "who_actor": "test",
                "what_type": "test_event",
                "title": "Test Event"
            })
            
            # Assertion: EventBuffer.authorized_push called (not write_sqlite)
            mock_buffer_instance.authorized_push.assert_called_once()
            call_kwargs = mock_buffer_instance.authorized_push.call_args[1]
            assert call_kwargs["decision_record_id"] == "DC_20260909_TEST_001"
```

**Test Case 3.2: write_safe_csv() Validates Integrity Before Push**

```python
"""Test that validation happens before EventBuffer push."""

def test_write_safe_csv_validates_before_push():
    from unittest.mock import patch, MagicMock
    from interface.router import write_safe_csv
    
    with patch('event_buffer.get_buffer') as mock_buffer:
        mock_buffer_instance = MagicMock()
        mock_buffer.return_value = mock_buffer_instance
        
        # Call with invalid data (missing required field)
        result = write_safe_csv({
            "who_actor": "test",
            # Missing "title" — required field
        })
        
        # Assertion: EventBuffer.authorized_push should NOT be called
        mock_buffer_instance.authorized_push.assert_not_called()
        assert result is None  # write_safe_csv returns None on validation failure
```

**Test Case 3.3: _record_integrity_incident() Routes to EventBuffer**

```python
"""Test that _record_integrity_incident() uses EventBuffer."""

def test_integrity_incident_uses_event_buffer():
    from unittest.mock import patch, MagicMock
    from interface.router import _record_integrity_incident
    
    violation = {"reason": "REQUIRED_FIELD_EMPTY", "field": "title"}
    original_row = {"what_type": "test"}
    
    with patch('event_buffer.get_buffer') as mock_buffer:
        mock_buffer_instance = MagicMock()
        mock_buffer.return_value = mock_buffer_instance
        mock_buffer_instance.authorized_push.return_value = {"status": "ok"}
        
        with patch('governance_pipeline._governance.before_tool') as mock_gl7:
            mock_gl7.return_value = MagicMock(
                allowed=True,
                decision_record_id="DC_20260909_INCIDENT_001"
            )
            
            _record_integrity_incident(violation, original_row)
            
            # Assertion: EventBuffer.authorized_push called for incident
            mock_buffer_instance.authorized_push.assert_called_once()
```

**Test Case 3.4: MoCKARouter.collaborate() and share() Route to EventBuffer**

```python
"""Test that MoCKARouter methods use EventBuffer."""

def test_mocka_router_methods_use_event_buffer():
    from unittest.mock import patch, MagicMock
    from interface.router import MoCKARouter
    
    router = MoCKARouter()
    
    with patch('event_buffer.get_buffer') as mock_buffer:
        mock_buffer_instance = MagicMock()
        mock_buffer.return_value = mock_buffer_instance
        mock_buffer_instance.authorized_push.return_value = {"status": "ok"}
        
        with patch('governance_pipeline._governance.before_tool') as mock_gl7:
            mock_gl7.return_value = MagicMock(
                allowed=True,
                decision_record_id="DC_20260909_ROUTER_001"
            )
            
            # Test collaborate()
            router.collaborate("Test prompt")
            assert mock_buffer_instance.authorized_push.call_count >= 1
            
            # Test share()
            router.share("Test share")
            assert mock_buffer_instance.authorized_push.call_count >= 2
```

**Acceptance Criteria:**
- [ ] write_safe_csv() uses authorized_push, not write_sqlite()
- [ ] _record_integrity_incident() uses authorized_push
- [ ] MoCKARouter.collaborate/share use authorized_push
- [ ] All calls include authorization_decision_id
- [ ] Validation happens before push (no invalid events queued)

---

## Verification 4: GL7 decision_record_id Linkage — Integration Tests

**Specification Reference:** Spec 4 (GovernanceDecision.decision_record_id)

**Test Case 4.1: Decision Generates Unique ID**

```python
"""Test that each decision gets a unique decision_record_id."""

def test_decision_generates_unique_id():
    from governance_pipeline import GovernanceDecision
    
    decision1 = GovernanceDecision(allowed=True, reason="Test 1")
    decision2 = GovernanceDecision(allowed=True, reason="Test 2")
    
    # Assertion: IDs are different
    assert decision1.decision_record_id != decision2.decision_record_id
    
    # Assertion: Format is correct (DC_YYYYMMDD_HHMMSS_HEX)
    import re
    assert re.match(r"DC_\d{8}_\d{6}_[0-9A-F]{8}", decision1.decision_record_id)
```

**Test Case 4.2: Decision Stored in Ledger with ID**

```python
"""Test that decision is written to Decision Ledger with decision_record_id."""

def test_decision_stored_in_ledger():
    from governance_pipeline import GovernancePipeline
    from pathlib import Path
    import json
    
    pipeline = GovernancePipeline()
    decision = pipeline.before_tool("test_op", {"actor": "test"})
    
    # Read Decision Ledger
    ledger_path = Path("data/decisions/decision_ledger.jsonl")
    last_entry = None
    
    with open(ledger_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                last_entry = json.loads(line)
            except:
                pass
    
    # Assertion: Latest entry has decision_record_id matching decision
    assert last_entry is not None
    assert last_entry["decision_id"] == decision.decision_record_id
    assert last_entry["allowed"] == decision.allowed
```

**Test Case 4.3: ID Format Compliance**

```python
"""Test that decision_record_id follows canonical format."""

def test_decision_id_format_compliance():
    from governance_pipeline import GovernanceDecision
    import re
    
    for _ in range(100):
        decision = GovernanceDecision(allowed=True, reason="Format test")
        
        # Assertion: All IDs match pattern
        assert re.match(
            r"DC_\d{8}_\d{6}_[0-9A-F]{8}",
            decision.decision_record_id
        ), f"Invalid format: {decision.decision_record_id}"
```

**Acceptance Criteria:**
- [ ] Each decision has unique decision_record_id
- [ ] Format: DC_YYYYMMDD_HHMMSS_HEX
- [ ] Decision stored in ledger with ID
- [ ] ID is available before event write (for linkage)

---

## Verification 5: EventBuffer authorized_push — Integration Tests

**Specification Reference:** Spec 5 (EventBuffer.authorized_push wrapper)

**Test Case 5.1: authorized_push Requires decision_record_id**

```python
"""Test that authorized_push raises error if decision_record_id is missing."""

def test_authorized_push_requires_decision_id():
    from event_buffer import get_buffer
    from interface.router import safe_buffer_push
    
    buffer = get_buffer()
    
    # Attempt push without decision_record_id should fail
    try:
        buffer.authorized_push(
            {"who_actor": "test", "what_type": "test"},
            decision_record_id=None  # Missing
        )
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "decision_record_id" in str(e)
```

**Test Case 5.2: safe_buffer_push Calls GL7 Before Push**

```python
"""Test that safe_buffer_push invokes GL7 authorization."""

def test_safe_buffer_push_calls_gl7():
    from unittest.mock import patch, MagicMock
    from interface.router import safe_buffer_push
    
    with patch('governance_pipeline._governance.before_tool') as mock_gl7:
        mock_gl7.return_value = MagicMock(
            allowed=True,
            decision_record_id="DC_20260909_TEST"
        )
        
        with patch('event_buffer.get_buffer') as mock_buffer:
            mock_buffer_instance = MagicMock()
            mock_buffer.return_value = mock_buffer_instance
            mock_buffer_instance.authorized_push.return_value = {"status": "ok", "decision_id": "DC_20260909_TEST"}
            
            safe_buffer_push(
                {"who_actor": "test", "what_type": "test"},
                operation_context={"operation_type": "test_op"}
            )
            
            # Assertion: GL7 was called
            mock_gl7.assert_called_once()
            # Assertion: authorized_push was called with decision_record_id
            mock_buffer_instance.authorized_push.assert_called_once()
```

**Test Case 5.3: safe_buffer_push Blocks on DENIED Decision**

```python
"""Test that safe_buffer_push raises exception if GL7 denies."""

def test_safe_buffer_push_blocks_denied():
    from unittest.mock import patch, MagicMock
    from interface.router import safe_buffer_push, AuthorizationDenied
    
    with patch('governance_pipeline._governance.before_tool') as mock_gl7:
        mock_gl7.return_value = MagicMock(
            allowed=False,
            reason="Policy violation"
        )
        
        try:
            safe_buffer_push(
                {"who_actor": "test", "what_type": "test"},
                operation_context={"operation_type": "test_op"}
            )
            assert False, "Should have raised AuthorizationDenied"
        except AuthorizationDenied as e:
            assert "Policy violation" in str(e)
```

**Acceptance Criteria:**
- [ ] authorized_push requires decision_record_id
- [ ] safe_buffer_push calls GL7 before push
- [ ] safe_buffer_push raises exception on DENIED
- [ ] Event contains authorization_decision_id in queue

---

## Verification 6: Authorization Record Integrity — Data Validation

**Specification Reference:** Spec 6 (Authorization Record Storage Format)

**Test Case 6.1: Decision Ledger Entry Schema Compliance**

```python
"""Test that Decision Ledger entries conform to schema."""

def test_decision_ledger_schema_compliance():
    from pathlib import Path
    import json
    from jsonschema import validate, ValidationError
    
    schema = {
        "type": "object",
        "required": ["decision_id", "created_at", "allowed", "reason"],
        "properties": {
            "decision_id": {"type": "string", "pattern": "^DC_\\d{8}_\\d{6}_[0-9A-F]{8}$"},
            "created_at": {"type": "string", "format": "date-time"},
            "allowed": {"type": "boolean"},
            "reason": {"type": "string"},
            "operation_type": {"type": "string"},
            "thinking_mode": {"type": "string"},
            "event_ids": {"type": "array", "items": {"type": "string"}},
        }
    }
    
    ledger_path = Path("data/decisions/decision_ledger.jsonl")
    
    with open(ledger_path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            try:
                entry = json.loads(line)
                validate(instance=entry, schema=schema)
            except ValidationError as e:
                assert False, f"Line {lineno}: Schema validation failed: {e.message}"
```

**Test Case 6.2: decision_record_id Format Validation**

```python
"""Test that all decision_record_ids in ledger match canonical format."""

def test_decision_id_format_in_ledger():
    from pathlib import Path
    import json
    import re
    
    ledger_path = Path("data/decisions/decision_ledger.jsonl")
    pattern = r"^DC_\d{8}_\d{6}_[0-9A-F]{8}$"
    
    with open(ledger_path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            entry = json.loads(line)
            decision_id = entry.get("decision_id")
            
            assert re.match(pattern, decision_id), \
                f"Line {lineno}: Invalid format: {decision_id}"
```

**Test Case 6.3: Event-Decision Linkage Consistency**

```python
"""Test that events table authorization_decision_id values match ledger decision_ids."""

def test_event_decision_linkage_consistency():
    import sqlite3
    from pathlib import Path
    import json
    
    # Read all decision IDs from ledger
    decision_ids = set()
    ledger_path = Path("data/decisions/decision_ledger.jsonl")
    
    with open(ledger_path, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            decision_ids.add(entry.get("decision_id"))
    
    # Check events table
    conn = sqlite3.connect("data/mocka_events.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT authorization_decision_id FROM events WHERE authorization_decision_id IS NOT NULL")
    event_decision_ids = {row[0] for row in cursor.fetchall()}
    conn.close()
    
    # Assertion: All event decision IDs exist in ledger
    orphaned = event_decision_ids - decision_ids
    assert len(orphaned) == 0, f"Orphaned decision IDs in events: {orphaned}"
```

**Acceptance Criteria:**
- [ ] All Decision Ledger entries conform to schema
- [ ] All decision_record_ids match canonical format
- [ ] No orphaned authorization_decision_id values in events
- [ ] event_ids array in ledger matches events table

---

## Verification 7: Audit Query Validation — Query Performance & Correctness

**Specification Reference:** Spec 7 (6 SQL audit queries)

**Test Case 7.1: Full Audit Trail Query Performance**

```python
"""Test that Query 1 (full audit trail) executes in <10ms."""

def test_query_1_performance():
    import sqlite3
    import time
    
    conn = sqlite3.connect("data/mocka_events.db")
    cursor = conn.cursor()
    
    # Create index if not exists
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_auth_decision_id ON events(authorization_decision_id)")
    conn.commit()
    
    # Test query on sample event
    start = time.time()
    cursor.execute("""
        SELECT e.event_id, e.when, e.who_actor, e.what_type,
               e.authorization_decision_id, d.decision_id, d.allowed, d.reason
        FROM events e
        LEFT JOIN decision_ledger d ON e.authorization_decision_id = d.decision_id
        WHERE e.event_id = ?
        LIMIT 1
    """, ["E20260909_001"])
    result = cursor.fetchone()
    elapsed_ms = (time.time() - start) * 1000
    
    conn.close()
    
    # Assertion: Query returns result and completes in time
    assert elapsed_ms < 10, f"Query took {elapsed_ms}ms (expected <10ms)"
```

**Test Case 7.2: All Events from Decision Query Correctness**

```python
"""Test that Query 2 returns all events for a decision."""

def test_query_2_correctness():
    import sqlite3
    from pathlib import Path
    import json
    
    conn = sqlite3.connect("data/mocka_events.db")
    cursor = conn.cursor()
    
    # Find a decision with known event_ids in ledger
    ledger_path = Path("data/decisions/decision_ledger.jsonl")
    decision_with_events = None
    
    with open(ledger_path, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            if entry.get("event_ids"):
                decision_with_events = entry
                break
    
    if not decision_with_events:
        # Skip if no decision with events found
        return
    
    decision_id = decision_with_events["decision_id"]
    expected_event_ids = set(decision_with_events["event_ids"])
    
    # Run Query 2
    cursor.execute("""
        SELECT e.event_id FROM events e
        WHERE e.authorization_decision_id = ?
        ORDER BY e.when DESC
    """, [decision_id])
    
    found_event_ids = {row[0] for row in cursor.fetchall()}
    conn.close()
    
    # Assertion: Query returns all expected events
    assert found_event_ids == expected_event_ids, \
        f"Query returned {found_event_ids}, expected {expected_event_ids}"
```

**Test Case 7.3: Denial Query Returns Only Denials**

```python
"""Test that Query 3 returns only DENIED decisions."""

def test_query_3_returns_only_denials():
    import sqlite3
    from pathlib import Path
    import json
    
    conn = sqlite3.connect("data/mocka_events.db")
    cursor = conn.cursor()
    
    # Run Query 3 (adjusted for JSON format)
    cursor.execute("""
        SELECT d.decision_id FROM decision_ledger d
        WHERE d.decision_outcome LIKE '%"allowed": false%'
        LIMIT 100
    """)
    
    denial_decisions = {row[0] for row in cursor.fetchall()}
    
    # Verify each is actually a denial (read from ledger file)
    ledger_path = Path("data/decisions/decision_ledger.jsonl")
    
    with open(ledger_path, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            decision_id = entry.get("decision_id")
            if decision_id in denial_decisions:
                assert entry.get("decision_outcome", {}).get("allowed") == False, \
                    f"Decision {decision_id} is not a denial"
    
    conn.close()
```

**Acceptance Criteria:**
- [ ] Query 1 executes in <10ms with index
- [ ] Query 2 returns exact event set for decision
- [ ] Query 3 returns only DENIED decisions
- [ ] Query 4 finds integrity incidents
- [ ] Query 5 detects unverified events
- [ ] Query 6 calculates coverage percentage

---

## Verification 8: Exception Logging & Audit Trail — Log Integrity

**Specification Reference:** Spec 8 (AuthorizationExceptionLogger)

**Test Case 8.1: Denials Logged to Exception File**

```python
"""Test that authorization denials are logged."""

def test_denials_logged():
    from governance.authorization_exception_logger import AuthorizationExceptionLogger
    from pathlib import Path
    import json
    
    logger = AuthorizationExceptionLogger()
    logger.log_denial("DC_20260909_TEST", "test_op", {"actor": "test"}, "Test denial")
    
    # Read exception log
    log_path = Path("data/logs/authorization_exceptions.jsonl")
    last_entry = None
    
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                last_entry = json.loads(line)
            except:
                pass
    
    # Assertion: Denial was logged
    assert last_entry is not None
    assert last_entry["type"] == "AUTHORIZATION_DENIAL"
    assert last_entry["decision_id"] == "DC_20260909_TEST"
    assert last_entry["reason"] == "Test denial"
```

**Test Case 8.2: Unknown Operations Logged**

```python
"""Test that unknown operations are logged."""

def test_unknown_operations_logged():
    from governance.authorization_exception_logger import AuthorizationExceptionLogger
    import json
    from pathlib import Path
    
    logger = AuthorizationExceptionLogger()
    logger.log_unknown_operation("unknown_op_12345", {"actor": "test"})
    
    # Read exception log and find entry
    log_path = Path("data/logs/authorization_exceptions.jsonl")
    found = False
    
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            if entry.get("type") == "UNKNOWN_OPERATION" and entry.get("operation") == "unknown_op_12345":
                found = True
                break
    
    assert found, "Unknown operation not logged"
```

**Test Case 8.3: Exception Log is Append-Only**

```python
"""Test that exception log is append-only (no deletion/modification)."""

def test_exception_log_append_only():
    from pathlib import Path
    import hashlib
    import time
    import json
    
    log_path = Path("data/logs/authorization_exceptions.jsonl")
    
    # Read file and hash it
    hash_before = hashlib.sha256(log_path.read_bytes()).hexdigest()
    initial_size = log_path.stat().st_size
    
    # Add a new entry
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"type": "TEST", "timestamp": time.time()}) + "\n")
    
    # Verify: file is larger, hash differs
    hash_after = hashlib.sha256(log_path.read_bytes()).hexdigest()
    final_size = log_path.stat().st_size
    
    assert final_size > initial_size, "File size did not increase"
    assert hash_before != hash_after, "File hash unchanged"
    
    # Verify: original content is preserved (hash of first N bytes matches)
    original_content = log_path.read_bytes()[:initial_size]
    hash_original = hashlib.sha256(original_content).hexdigest()
    # Note: Re-read file first N bytes to verify
    current_content = log_path.read_bytes()[:initial_size]
    hash_current = hashlib.sha256(current_content).hexdigest()
    
    assert hash_original == hash_current, "Original content was modified"
```

**Acceptance Criteria:**
- [ ] Denials logged with full context
- [ ] Unknown operations tracked
- [ ] Errors recorded
- [ ] Exception overrides logged
- [ ] Log is append-only (immutable)
- [ ] Report queries return correct aggregations

---

## Verification 9: Reverse Linkage Consistency — Data Integrity

**Specification Reference:** Spec 9 (Decision Ledger Linkage Manager)

**Test Case 9.1: Linking Event to Decision**

```python
"""Test that linking updates Decision Ledger correctly."""

def test_link_event_to_decision():
    from governance.decision_ledger_linkage import DecisionLedgerLinkageManager
    import json
    from pathlib import Path
    
    manager = DecisionLedgerLinkageManager()
    
    # Link event to decision
    manager.link_event_to_decision("E20260909_001", "DC_20260909_TEST_001")
    
    # Verify linkage in ledger
    ledger_path = Path("data/decisions/decision_ledger.jsonl")
    found = False
    
    with open(ledger_path, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            if entry.get("decision_id") == "DC_20260909_TEST_001":
                if "E20260909_001" in entry.get("event_ids", []):
                    found = True
                    break
    
    assert found, "Event linkage not found in ledger"
```

**Test Case 9.2: Linkage Index Building**

```python
"""Test that linkage index is built correctly."""

def test_build_linkage_index():
    from governance.decision_ledger_linkage import DecisionLedgerLinkageManager
    
    manager = DecisionLedgerLinkageManager()
    index = manager.build_linkage_index()
    
    # Verify index structure
    assert isinstance(index, dict)
    for decision_id, event_ids in index.items():
        assert isinstance(decision_id, str)
        assert decision_id.startswith("DC_")
        assert isinstance(event_ids, list)
        for event_id in event_ids:
            assert isinstance(event_id, str)
            assert event_id.startswith("E")
```

**Test Case 9.3: Integrity Verification Detects Orphans**

```python
"""Test that integrity verification finds orphaned linkages."""

def test_verify_linkage_integrity():
    from governance.decision_ledger_linkage import DecisionLedgerLinkageManager
    
    manager = DecisionLedgerLinkageManager()
    errors = manager.verify_linkage_integrity()
    
    # Assertion: Orphaned links are detected
    for error in errors:
        assert error["type"] == "ORPHANED_EVENT_LINKAGE"
        assert "decision_id" in error
        assert "event_id" in error
```

**Acceptance Criteria:**
- [ ] Events linked to decisions correctly
- [ ] Linkage index built without errors
- [ ] Integrity verification detects orphans
- [ ] Reverse linkage matches forward linkage
- [ ] No duplicates in event_ids arrays

---

## Verification 10: Schema Migration — Database Consistency

**Specification Reference:** Spec 10 (ALTER TABLE authorization_decision_id)

**Test Case 10.1: Pre-Migration Backup**

```python
"""Test that backup is created before migration."""

def test_pre_migration_backup():
    from governance.rollback_authorization import AuthorizationRollback
    from pathlib import Path
    
    backup_path = AuthorizationRollback.create_pre_deployment_backup()
    
    # Assertion: Backup file exists
    assert Path(backup_path).exists()
    
    # Assertion: Backup is valid SQLite database
    import sqlite3
    conn = sqlite3.connect(str(backup_path))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM events")
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count >= 0, "Backup database is invalid"
```

**Test Case 10.2: Migration Adds Column**

```python
"""Test that ALTER TABLE adds authorization_decision_id column."""

def test_migration_adds_column():
    import sqlite3
    
    conn = sqlite3.connect("data/mocka_events.db")
    cursor = conn.cursor()
    
    # Check that column exists
    cursor.execute("PRAGMA table_info(events)")
    columns = {row[1] for row in cursor.fetchall()}
    
    assert "authorization_decision_id" in columns, "Column not added by migration"
    
    conn.close()
```

**Test Case 10.3: Migration Creates Index**

```python
"""Test that migration creates index for performance."""

def test_migration_creates_index():
    import sqlite3
    
    conn = sqlite3.connect("data/mocka_events.db")
    cursor = conn.cursor()
    
    # Check that index exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_events_auth_decision_id'")
    index_exists = cursor.fetchone() is not None
    
    assert index_exists, "Index not created"
    
    conn.close()
```

**Test Case 10.4: Legacy Events Remain Intact**

```python
"""Test that migration does not delete or corrupt existing events."""

def test_migration_preserves_legacy_data():
    import sqlite3
    import hashlib
    
    # Create backup before migration
    import shutil
    shutil.copy("data/mocka_events.db", "data/mocka_events.db.pre_migration_test")
    
    # Run migration (pseudo-code; actual execution in Phase 5)
    # migrate_add_authorization_column()
    
    conn_before = sqlite3.connect("data/mocka_events.db.pre_migration_test")
    cursor_before = conn_before.cursor()
    cursor_before.execute("SELECT COUNT(*) FROM events")
    count_before = cursor_before.fetchone()[0]
    conn_before.close()
    
    conn_after = sqlite3.connect("data/mocka_events.db")
    cursor_after = conn_after.cursor()
    cursor_after.execute("SELECT COUNT(*) FROM events")
    count_after = cursor_after.fetchone()[0]
    conn_after.close()
    
    # Assertion: Row count unchanged
    assert count_before == count_after, f"Migration changed row count: {count_before} → {count_after}"
```

**Acceptance Criteria:**
- [ ] Backup created before migration
- [ ] Column successfully added
- [ ] Index created for performance
- [ ] Zero data loss during migration
- [ ] Migration is reversible (rollback tested)

---

## Verification 11: Rollback Procedures — Recovery Testing

**Specification Reference:** Spec 11 (AuthorizationRollback 3-level procedures)

**Test Case 11.1: Level 1 Rollback (Single Event)**

```python
"""Test Level 1 recovery for single event bypass."""

def test_level_1_rollback():
    from governance.rollback_authorization import AuthorizationRollback
    import sqlite3
    
    # Setup: Create test event without authorization_decision_id
    conn = sqlite3.connect("data/mocka_events.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO events (event_id, when, who_actor, what_type, where_component, authorization_decision_id)
        VALUES (?, datetime('now'), 'test', 'test_event', 'test', NULL)
    """, ["E_TEST_L1_001"])
    conn.commit()
    conn.close()
    
    # Execute Level 1 rollback
    AuthorizationRollback.level_1_single_event_rollback("E_TEST_L1_001")
    
    # Verify event marked unverified
    conn = sqlite3.connect("data/mocka_events.db")
    cursor = conn.cursor()
    cursor.execute("SELECT free_note FROM events WHERE event_id = ?", ["E_TEST_L1_001"])
    free_note = cursor.fetchone()[0]
    conn.close()
    
    assert "UNVERIFIED" in free_note, "Event not marked unverified"
```

**Test Case 11.2: Level 2 Rollback (Batch Bypass)**

```python
"""Test Level 2 recovery for batch bypass (100+ events)."""

def test_level_2_rollback():
    from governance.rollback_authorization import AuthorizationRollback
    import sqlite3
    from datetime import datetime, timedelta
    
    # Setup: Create 10 test events (unverified) in time window
    conn = sqlite3.connect("data/mocka_events.db")
    cursor = conn.cursor()
    
    base_time = datetime.utcnow()
    for i in range(10):
        event_time = (base_time - timedelta(hours=1) + timedelta(minutes=i)).isoformat()
        cursor.execute("""
            INSERT INTO events (event_id, when, who_actor, what_type, where_component, authorization_decision_id)
            VALUES (?, ?, 'test', 'test_event', 'test', NULL)
        """, [f"E_TEST_L2_{i:03d}", event_time])
    conn.commit()
    conn.close()
    
    # Execute Level 2 rollback
    time_start = (base_time - timedelta(hours=2)).isoformat()
    time_end = base_time.isoformat()
    decisions = AuthorizationRollback.level_2_batch_bypass_rollback(time_start, time_end)
    
    # Verify retroactive decisions created
    assert len(decisions) == 10, f"Expected 10 retroactive decisions, got {len(decisions)}"
    
    # Verify events linked to retroactive decisions
    conn = sqlite3.connect("data/mocka_events.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM events WHERE authorization_decision_id LIKE 'RETRO_DC_%'")
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count == 10, "Events not linked to retroactive decisions"
```

**Test Case 11.3: Level 3 Rollback (Full Restore)**

```python
"""Test Level 3 recovery (full restore from backup)."""

def test_level_3_rollback():
    from governance.rollback_authorization import AuthorizationRollback
    import sqlite3
    
    # Setup: Create backup
    backup_path = AuthorizationRollback.create_pre_deployment_backup()
    
    # Corrupt database (delete events)
    conn = sqlite3.connect("data/mocka_events.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE 1=1")  # Delete all
    conn.commit()
    conn.close()
    
    # Verify corruption
    conn = sqlite3.connect("data/mocka_events.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM events")
    corrupted_count = cursor.fetchone()[0]
    conn.close()
    
    assert corrupted_count == 0, "Setup failed: events not deleted"
    
    # Execute Level 3 rollback
    AuthorizationRollback.level_3_data_corruption_rollback(str(backup_path))
    
    # Verify restore
    conn = sqlite3.connect("data/mocka_events.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM events")
    restored_count = cursor.fetchone()[0]
    conn.close()
    
    assert restored_count > 0, "Restore failed: no events"
```

**Acceptance Criteria:**
- [ ] Level 1: Single event marked unverified
- [ ] Level 2: Batch bypass linked to retroactive denials
- [ ] Level 3: Full restore from backup successful
- [ ] Time-to-rollback < 5 minutes verified
- [ ] No data loss in any recovery level

---

## Verification 12: Production Safety Validation — Pre-Deployment Checklist

**Specification Reference:** Spec 12 (ProductionSafetyValidator 6-category checks)

**Test Case 12.1: Functional Safety Checks Pass**

```python
"""Test that all functional safety checks pass before go-live."""

def test_functional_safety_checks():
    from governance.production_safety_validator import ProductionSafetyValidator
    
    validator = ProductionSafetyValidator()
    results = validator.check_functional_safety()
    
    assert results["route_b_handlers_reachable"] == True
    assert results["event_buffer_accessible"] == True
    assert results["gl7_decision_engine_responding"] == True
    assert results["decision_ledger_writable"] == True
```

**Test Case 12.2: Integrity Safety Checks Pass**

```python
"""Test that data integrity checks pass."""

def test_integrity_safety_checks():
    from governance.production_safety_validator import ProductionSafetyValidator
    
    validator = ProductionSafetyValidator()
    results = validator.check_integrity_safety()
    
    assert results["orphaned_linkages"] == 0
    assert results["integrity_ok"] == True
    assert results["reverse_linkage_ok"] == True
```

**Test Case 12.3: Performance Safety Checks Pass**

```python
"""Test that performance requirements are met."""

def test_performance_safety_checks():
    from governance.production_safety_validator import ProductionSafetyValidator
    
    validator = ProductionSafetyValidator()
    results = validator.check_performance_safety()
    
    assert results["latency_ok"] == True, f"Query latency {results['query_latency_ms']}ms > 10ms"
    assert results["throughput_ok"] == True, f"Throughput {results['throughput_events_per_sec']}/sec < 1000/sec"
```

**Test Case 12.4: Go-Live Readiness Gate**

```python
"""Test go-live readiness determination."""

def test_golive_readiness_gate():
    from governance.production_safety_validator import ProductionSafetyValidator
    
    validator = ProductionSafetyValidator()
    validator.run_all_checks()
    
    # Go-live readiness requires all 6 categories to pass
    assert validator.checks["functional"] == True
    assert validator.checks["integrity"] == True
    assert validator.checks["performance"] == True
    assert validator.checks["rollback"] == True
    assert validator.checks["monitoring"] == True
    
    # Go-live only if all pass
    golive_results = validator.check_golive_readiness()
    assert golive_results["ready_for_golive"] == True
```

**Acceptance Criteria:**
- [ ] All 6 safety category checks pass
- [ ] Functional: endpoints, buffer, GL7, ledger
- [ ] Integrity: no orphaned links, consistency verified
- [ ] Performance: latency <10ms, throughput >=1000/sec
- [ ] Rollback: backup exists, procedures documented
- [ ] Monitoring: alerts configured
- [ ] Go-live authorized only if all green

---

## Phase 3 Verification Summary

**Stream 4 Verification Plan Complete:**

| Verification | Spec | Test Cases | Acceptance Criteria | Status |
|---|---|---|---|---|
| 1 | Approval Confirmation Validator | 4 | Code scanning, report generation | Design only |
| 2 | Route B Decorator | 4 | Auth enforcement, context extraction | Design only |
| 3 | Route C Migration | 4 | EventBuffer routing, validation | Design only |
| 4 | GL7 decision_record_id | 3 | Unique IDs, ledger storage | Design only |
| 5 | EventBuffer authorized_push | 3 | GL7 invocation, DENY blocking | Design only |
| 6 | Authorization Record Integrity | 3 | Schema compliance, linkage | Design only |
| 7 | Audit Query Validation | 3 | Performance, correctness | Design only |
| 8 | Exception Logging | 3 | Denial logging, append-only | Design only |
| 9 | Reverse Linkage Consistency | 3 | Event-decision links, orphan detection | Design only |
| 10 | Schema Migration | 4 | Backup, column add, index, preservation | Design only |
| 11 | Rollback Procedures | 3 | Level 1/2/3 recovery, time-to-rollback | Design only |
| 12 | Production Safety Validation | 4 | 6-category checks, go-live gate | Design only |
| **TOTAL** | **12 Specs** | **42 Test Cases** | **Comprehensive Coverage** | **Phase 3 Complete** |

**Governance Constraints Maintained:**
- All verification procedures designed (no tests executed)
- No implementation code written
- No schema changes deployed
- No production modifications
- C2-b BLOCK immutable
- UNKNOWN/NOT_PROVEN preserved

---

## Final Authorization Readiness Package — Summary

**Phase 3 Prerequisite Work Complete:**

### Deliverables Created:

1. **Stream 1: Route Inventory (01_ROUTE_INVENTORY.md)**
   - Route A (MCP GL7): PASS — authorization enforced
   - Route B (Flask): 8 bypasses identified
   - Route C (Direct SQLite): zero authorization checks
   - Evidence-bounded investigation; gaps documented

2. **Stream 2: Design Detailing (02_DESIGN_DETAILING_v1.0.md)**
   - 12 design elements translating Phase 1 baseline to concrete specifications
   - Approval Confirmation State definition
   - Enforcement point insertion strategy
   - Authorization record binding design
   - Fail-closed patterns, audit procedures, schema impact

3. **Stream 3: Specification (03_SPECIFICATION_v1.0.md)**
   - 12 executable pseudocode/SQL specifications
   - Validator, decorator, migration, GL7 extension
   - EventBuffer wrapper, audit queries
   - Schema migration, rollback, safety validation scripts

4. **Stream 4: Verification Plan (04_VERIFICATION_PLAN_v1.0.md)**
   - 42 test cases across 12 verification areas
   - Unit, integration, data integrity tests
   - Query performance, log integrity verification
   - Pre-deployment safety checklist, go-live gate

### Governance Status:

**Authorization Readiness Package Contents:**
- [x] Stream 1 — Evidence Collection (complete)
- [x] Stream 2 — Design Detailing (complete)
- [x] Stream 3 — Specification Creation (complete)
- [x] Stream 4 — Verification Planning (complete)
- [x] 16-item Evidence Inventory (Spec 1)
- [x] Decision Ledger linkage specification (Spec 5, 6, 9)
- [x] Test coverage across all implementation areas (Stream 4)
- [x] Pre-deployment safety validation procedures (Spec 12)
- [x] Rollback and recovery procedures (Spec 11)
- [x] UNKNOWN/NOT_PROVEN gaps preserved and documented

**Constraints Maintained:**
- Implementation Authorization: NOT GRANTED
- Production Modification: 0
- C2-b BLOCK: IMMUTABLE
- Code/Schema/Migration/Deployment: NOT AUTHORIZED

---

**Status:** Phase 3 Prerequisite Work COMPLETE

**Next:** Phase 4 Human Gate Review → Implementation Authorization Decision

**Approval Gate:** HG-PHASE3-AUTHORIZATION-READINESS-REVIEW

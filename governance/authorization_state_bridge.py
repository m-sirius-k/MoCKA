# governance/authorization_state_bridge.py
# HG-AS-01: Human Gate → Authorization State Bridge
# Date: 2026-09-22
# Status: Sandbox Only Implementation
# Authority: HG-AS-01 DECISION RECORD
#
# Purpose:
# - Translate human_gate_events.approve() events to authorization_state records
# - Ensure only Human Gate APPROVED events create Authorization State
# - Maintain immutability and audit traceability
# - NO decision logic; schema translation only
#
# Boundary:
# - Input: human_gate_events table (human_gate.py manages)
# - Processing: Schema validation & mapping (this module)
# - Output: authorization_state table (Sandbox only)
# - No authority: read events, transform, write state record (no decision)

import sqlite3
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# Database path (same as human_gate.py)
_REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = str(_REPO_ROOT / 'data' / 'mocka_events.db')


class AuthorizationStateBridgeError(Exception):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_authorization_state_table(conn) -> None:
    """
    Create authorization_state table if not exists.

    Schema per HG-A2 10 fields + traceability:
    - authorization_id (PK, UUID)
    - decision_id (nullable, ref to decision_record_id)
    - subject (actor from payload)
    - scope (JSON array as string)
    - standing (always "UNKNOWN" per HG-AS-01)
    - status (APPROVED/REJECTED/EXPIRED/HELD)
    - granted_by (authority_role from payload)
    - granted_at (timestamp from human_gate_events)
    - expires_at (nullable, from payload)
    - evidence (JSON with source refs)
    - hg_event_source (traceability: event_id)
    - hg_event_timestamp (traceability: timestamp)
    - created_at (when authorization_state was created)
    - immutable (always 1 on creation)
    """
    conn.execute('''
        CREATE TABLE IF NOT EXISTS authorization_state (
            authorization_id TEXT PRIMARY KEY,
            decision_id TEXT,
            subject TEXT,
            scope TEXT,
            standing TEXT,
            status TEXT,
            granted_by TEXT,
            granted_at TEXT,
            expires_at TEXT,
            evidence TEXT,
            hg_event_source TEXT,
            hg_event_timestamp TEXT,
            created_at TEXT,
            immutable INTEGER DEFAULT 1
        )
    ''')

    # Immutability enforcement (append-only)
    conn.execute('''
        CREATE TRIGGER IF NOT EXISTS authorization_state_no_update
        BEFORE UPDATE ON authorization_state
        BEGIN SELECT RAISE(ABORT, 'authorization_state is append-only: update forbidden'); END
    ''')

    conn.execute('''
        CREATE TRIGGER IF NOT EXISTS authorization_state_no_delete
        BEFORE DELETE ON authorization_state
        BEGIN SELECT RAISE(ABORT, 'authorization_state is append-only: delete forbidden'); END
    ''')


def _validate_payload_schema(payload: Dict[str, Any], action: str) -> Tuple[bool, Optional[str]]:
    """
    Validate payload schema per HG-AS-01.

    For approve action:
    - actor (string, mandatory)
    - scope (array, mandatory)
    - authority_role (string, mandatory)
    - decision_id (string, optional)
    - expires_at (ISO8601 string, optional)
    - evidence_ref (array, optional)
    - note (string, optional)
    """
    if action != "approve":
        # Other actions (reject, expire, cancel) do not issue authorization_state
        return True, None

    if not isinstance(payload, dict):
        return False, "payload must be dict"

    # Mandatory for approve
    mandatory = {"actor", "scope", "authority_role"}
    for field in mandatory:
        if field not in payload:
            return False, f"missing mandatory field for approve: {field}"

        value = payload[field]
        if value is None:
            return False, f"field '{field}' cannot be None"

        if isinstance(value, str) and not value.strip():
            return False, f"field '{field}' cannot be empty string"

        if field == "scope" and (not isinstance(value, list) or not value):
            return False, f"field 'scope' must be non-empty array"

    # Type validation
    if not isinstance(payload.get("actor"), str):
        return False, "field 'actor' must be string"

    if not isinstance(payload.get("scope"), list):
        return False, "field 'scope' must be array"

    if not isinstance(payload.get("authority_role"), str):
        return False, "field 'authority_role' must be string"

    # Optional field validation
    if "expires_at" in payload and payload["expires_at"] is not None:
        if not isinstance(payload["expires_at"], str):
            return False, "field 'expires_at' must be ISO8601 string or null"
        try:
            datetime.fromisoformat(payload["expires_at"].replace("Z", "+00:00"))
        except ValueError:
            return False, f"field 'expires_at' not valid ISO8601: {payload['expires_at']}"

    if "evidence_ref" in payload and payload["evidence_ref"] is not None:
        if not isinstance(payload["evidence_ref"], list):
            return False, "field 'evidence_ref' must be array or null"

    return True, None


def _payload_to_auth_state_record(
    payload: Dict[str, Any],
    event_id: str,
    timestamp: str,
    request_id: str,
    next_state: str
) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Transform human_gate_events approve event to authorization_state record.

    Returns:
        (success, error_msg, record_dict)

    Notes:
        - Only next_state="APPROVED" is transformed
        - standing is always set to "UNKNOWN" (HG-AS-01)
        - scope and evidence are stored as JSON strings
        - No decision logic; schema translation only
    """
    if next_state != "APPROVED":
        # Only APPROVED events issue authorization_state
        # REJECTED, EXPIRED, CANCELED are recorded in human_gate but do not create auth state
        return False, f"Only APPROVED events can create authorization_state; got {next_state}", None

    try:
        record = {
            "authorization_id": str(uuid.uuid4()),
            "decision_id": payload.get("decision_id"),  # nullable
            "subject": payload.get("actor"),
            "scope": json.dumps(payload.get("scope", [])),
            "standing": "UNKNOWN",  # HG-AS-01: explicit UNKNOWN marker
            "status": "APPROVED",
            "granted_by": payload.get("authority_role"),
            "granted_at": timestamp,
            "expires_at": payload.get("expires_at"),  # nullable
            "evidence": json.dumps({"source": payload.get("evidence_ref", [])}) if payload.get("evidence_ref") else None,
            "hg_event_source": event_id,
            "hg_event_timestamp": timestamp,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "immutable": 1,
        }
        return True, None, record
    except Exception as e:
        return False, f"Error transforming payload: {str(e)}", None


def issue_authorization_state(request_id: str, conn=None) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Create authorization_state record from latest human_gate_events.approve event.

    Flow:
    1. Fetch latest event for request_id
    2. Validate event is action="approve" and next_state="APPROVED"
    3. Validate payload schema (HG-AS-01)
    4. Transform to authorization_state record
    5. Insert into authorization_state table (append-only)

    Returns:
        (success, error_msg, authorization_id)

    Error handling:
        - No event found: return (False, error, None)
        - Event not APPROVED: return (False, error, None)
        - Payload validation fails: return (False, error, None)
        - DB insert fails: return (False, error, None)

    Guarantees:
        - No duplicate authorization_id (UUID uniqueness)
        - No modification of existing auth state (append-only)
        - standing always set to "UNKNOWN"
        - hg_event_source and hg_event_timestamp for traceability
    """
    owns_conn = conn is None
    if owns_conn:
        conn = _get_conn()

    try:
        _ensure_authorization_state_table(conn)

        # Fetch latest event for request_id
        row = conn.execute(
            '''SELECT * FROM human_gate_events
               WHERE request_id = ?
               ORDER BY timestamp DESC, event_id DESC
               LIMIT 1''',
            (request_id,)
        ).fetchone()

        if not row:
            return False, f"No human_gate_events found for request_id: {request_id}", None

        # Validate event is approve
        if row['action'] != 'approve':
            return False, f"Event is not approve action: {row['action']}", None

        if row['next_state'] != 'APPROVED':
            return False, f"Event state is not APPROVED: {row['next_state']}", None

        # Parse and validate payload
        try:
            payload = json.loads(row['payload']) if row['payload'] else {}
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON in payload: {str(e)}", None

        is_valid, err = _validate_payload_schema(payload, row['action'])
        if not is_valid:
            return False, f"Payload schema validation failed: {err}", None

        # Transform to authorization_state record
        success, err, record = _payload_to_auth_state_record(
            payload,
            row['event_id'],
            row['timestamp'],
            request_id,
            row['next_state']
        )

        if not success:
            return False, err, None

        # Insert into authorization_state (append-only, no duplicate check needed)
        conn.execute(
            '''INSERT INTO authorization_state
               (authorization_id, decision_id, subject, scope, standing, status,
                granted_by, granted_at, expires_at, evidence,
                hg_event_source, hg_event_timestamp, created_at, immutable)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (record['authorization_id'], record['decision_id'], record['subject'],
             record['scope'], record['standing'], record['status'],
             record['granted_by'], record['granted_at'], record['expires_at'],
             record['evidence'], record['hg_event_source'], record['hg_event_timestamp'],
             record['created_at'], record['immutable'])
        )
        conn.commit()

        return True, None, record['authorization_id']

    except Exception as e:
        return False, f"Exception in issue_authorization_state: {str(e)}", None

    finally:
        if owns_conn:
            conn.close()


def get_authorization_state(authorization_id: str, conn=None) -> Optional[Dict[str, Any]]:
    """
    Fetch authorization_state record by authorization_id.

    Returns:
        dict with all fields, or None if not found

    Read-only operation; used by runtime verification.
    """
    owns_conn = conn is None
    if owns_conn:
        conn = _get_conn()

    try:
        _ensure_authorization_state_table(conn)
        row = conn.execute(
            'SELECT * FROM authorization_state WHERE authorization_id = ?',
            (authorization_id,)
        ).fetchone()

        if row:
            return dict(row)
        return None

    finally:
        if owns_conn:
            conn.close()


def query_authorization_state(decision_id: Optional[str] = None,
                              subject: Optional[str] = None,
                              status: Optional[str] = None,
                              conn=None) -> list:
    """
    Query authorization_state records (read-only).

    Used by Sandbox runtime verification.
    All parameters are optional; None means "any value".

    Returns:
        list of matching records (dict)
    """
    owns_conn = conn is None
    if owns_conn:
        conn = _get_conn()

    try:
        _ensure_authorization_state_table(conn)

        query = 'SELECT * FROM authorization_state WHERE 1=1'
        params = []

        if decision_id is not None:
            query += ' AND decision_id = ?'
            params.append(decision_id)

        if subject is not None:
            query += ' AND subject = ?'
            params.append(subject)

        if status is not None:
            query += ' AND status = ?'
            params.append(status)

        query += ' ORDER BY granted_at DESC'

        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    finally:
        if owns_conn:
            conn.close()


def get_decision_id_from_hg_event(hg_event_source: str, conn=None) -> Optional[str]:
    """
    JARVIS-facing adapter: Fetch decision_id from authorization_state by hg_event_source.

    Input: hg_event_source (HAB event_id)
    Output: decision_id (JARVIS-facing key), or None if not found

    Usage:
        decision_id = get_decision_id_from_hg_event(hg_event_source="HG20260922_...")
        JARVIS.evaluate(decision_id)
    """
    owns_conn = conn is None
    if owns_conn:
        conn = _get_conn()

    try:
        _ensure_authorization_state_table(conn)
        row = conn.execute(
            'SELECT decision_id FROM authorization_state WHERE hg_event_source = ? LIMIT 1',
            (hg_event_source,)
        ).fetchone()

        if row:
            return row['decision_id']
        return None

    finally:
        if owns_conn:
            conn.close()


if __name__ == "__main__":
    print("=== Authorization State Bridge Tests ===\n")

    # Test: Create authorization_state table
    conn = _get_conn()
    _ensure_authorization_state_table(conn)
    print("[OK] authorization_state table ensured\n")

    # Test: Validate schema
    valid_payload = {
        "actor": "kimura_phd",
        "scope": ["component_A"],
        "authority_role": "HG_AUTHORITY_HOLDER_01",
    }
    is_valid, err = _validate_payload_schema(valid_payload, "approve")
    print(f"Payload validation (valid): {is_valid}")

    invalid_payload = {
        "actor": "kimura_phd",
        # missing scope
        "authority_role": "HG_AUTHORITY_HOLDER_01",
    }
    is_valid, err = _validate_payload_schema(invalid_payload, "approve")
    print(f"Payload validation (invalid): {is_valid}, error: {err}\n")

    # Test: Query (should be empty initially in sandbox)
    records = query_authorization_state(status="APPROVED", conn=conn)
    print(f"Current APPROVED records: {len(records)}")

    conn.close()
    print("\n[OK] All bridge tests completed")

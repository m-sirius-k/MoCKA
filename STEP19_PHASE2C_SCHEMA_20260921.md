# STEP 19 Phase 2-C: Evidence Schema Finalization
**Date:** 2026-09-21  
**Authority:** HG-18-B (A), HG-18-D (A)  
**Scope:** Concrete Evidence record schema with HG-18 constraints

---

## Evidence Record Concrete Schema

### Minimal Required Fields (HG-18-B)

```json
{
  "record_id": "PER_20260921_xxxxxxxx",
  "decision_record_id": "DC_20260921_nnnn",
  "evidence_class": "pre-decision|post-execution",
  "source_provenance": [
    {
      "component_id": "string",
      "source_type": "plan_metadata|governance_signal|historical_execution|governance_compliance|authorization_context",
      "source_ref": "string",
      "validity_status": "validated|unverified|unknown|invalid",
      "source_timestamp": "ISO8601"
    }
  ],
  "created_at": "ISO8601",
  "generated_by": "string"
}
```

### Field Specifications

| Field | Type | Required | Values | Rules |
|-------|------|----------|--------|-------|
| record_id | string | YES | PER_YYYYMMDD_xxxxxxxx | Immutable, unique |
| decision_record_id | string | YES | DC_YYYYMMDD_nnnn | Must reference existing Decision |
| evidence_class | string | YES | "pre-decision" \| "post-execution" | Explicit only (HG-18-D) |
| source_provenance | array | YES | Component objects | Min 1, max N components |
| created_at | ISO8601 | YES | DateTime | Record creation time |
| generated_by | string | YES | identifier | session_id or AI identifier |
| evidence_data | object | NO | JSON | Optional application data |

### Source Provenance Component Rules (HG-17-B)

| Component Field | Type | Required | Values | Rules |
|-----------------|------|----------|--------|-------|
| component_id | string | YES | user-defined | Free text identifier |
| source_type | string | YES | See Values | Pre-defined enum |
| source_ref | string | YES | reference | Path/ID to actual source |
| validity_status | string | YES | validated\|unverified\|unknown\|invalid | NO timing inference |
| source_timestamp | ISO8601 | YES | DateTime | When source was available |

### Source Type Enum (Currently Verified)

```
"plan_metadata"           ← VERIFIED available at T3
"governance_signal"       ← VERIFIED available at T3
"historical_execution"    ← EVIDENCE GAP (unknown if available)
"governance_compliance"   ← EVIDENCE GAP (stub only)
"authorization_context"   ← EVIDENCE GAP (unknown if available)
```

### Evidence Class Validation (HG-18-D)

```
VALID:
  "evidence_class": "pre-decision"
  "evidence_class": "post-execution"

INVALID (ALL REJECTED):
  "evidence_class": "unknown"
  "evidence_class": "auto"
  "evidence_class": null
  (field omission)
  "evidence_class": ""
```

### Validity Status Rules (HG-17-B)

```
"validated"   → Source verified by independent mechanism (e.g., plan_validator.py)
"unverified"  → Source available, not independently verified (e.g., governance stub)
"unknown"     → Source availability uncertain
"invalid"     → Source known to be incorrect or inapplicable

RULE: Source exists ≠ Source valid
      Must preserve all 4 states, never conflate.

NO automatic conversion based on timing or presence.
```

### Storage Format

**File:** `data/evidence/evidence_records.jsonl`

**Format:**
```
One JSON object per line
Fields: order-independent
Encoding: UTF-8
Line ending: \n (Unix style)
```

**Example:**
```json
{"record_id":"PER_20260921_abc12345","decision_record_id":"DC_20260921_001","evidence_class":"pre-decision","source_provenance":[{"component_id":"plan_structure","source_type":"plan_metadata","source_ref":"plan.json#intent_id","validity_status":"validated","source_timestamp":"2026-09-21T10:00:00Z"},{"component_id":"governance_signal","source_type":"governance_signal","source_ref":"governance_client.evaluate()","validity_status":"unverified","source_timestamp":"2026-09-21T10:00:15Z"}],"created_at":"2026-09-21T10:00:15Z","generated_by":"governance_evaluate"}
```

### Validation Rules (Implementation)

1. **record_id format validation**
   - Pattern: `PER_\d{8}_[a-f0-9]{8}`
   - Must be unique (checked at write time)

2. **decision_record_id validation**
   - Pattern: `DC_\d{8}_\d{4}` (or UUID format)
   - Must reference existing Decision in Decision Ledger

3. **evidence_class validation**
   - Enum: exact match required
   - No default, no inference, no null

4. **source_provenance validation**
   - Min 1 component required
   - Each component: ALL fields required
   - source_type: Must be in pre-defined enum
   - validity_status: Must match enum, never inferred from timing

5. **timestamp validation**
   - Format: ISO8601 with timezone
   - created_at ≥ source_timestamp (evidence >= its sources)

### Pre-Decision vs. Post-Execution Class Distinction

```
Pre-Decision Evidence
  evidence_class = "pre-decision"
  created_at >= T3 (Decision time), < T5 (Execution time)
  Decision must exist at creation time
  source_provenance: plan_metadata, governance_signal only
  
Post-Execution Evidence
  evidence_class = "post-execution"
  created_at >= T8 (after execution)
  source_provenance: events from mocka_events.db
  
Cross-class substitution = PROHIBITED
  Policy: Post-Execution Evidence CANNOT be used to justify pre-Decision rationale
  Enforcement: Schema-level class distinction (immutable)
```

### Bidirectional Reference Implementation (HG-18-C)

**Forward Reference (Evidence → Decision):**
```json
{
  "decision_record_id": "DC_20260921_001"
}
```
REQUIRED, IMMUTABLE.

**Reverse Reference (Decision → Evidence):**
Option 1: Index file (optional)
```json
// data/evidence/decision_evidence_index.jsonl
{"decision_id":"DC_20260921_001","evidence_records":["PER_20260921_abc12345"]}
```

Option 2: Lookup via grep/scan
```
grep "\"decision_record_id\":\"DC_20260921_001\"" data/evidence/evidence_records.jsonl
```

REQUIRED: One method must be implemented and tested.

---

## Conclusion

**Schema Ready for Implementation & Test**

All fields specified. All validation rules defined. Immutability preserved.

---

**Status:** SCHEMA FINALIZATION COMPLETE  
**Date:** 2026-09-21

# STEP 18 Phase 2-B: Implementation Design for Pre-Decision Evidence Architecture
**Date:** 2026-09-21  
**Authorization:** HG-17 (A=D, B=D, C=C)  
**Scope:** Sandbox implementation design ONLY  
**Constraints:** NO production modification, NO autonomous HG decisions, NO existing record alteration

---

## 1. Transaction Boundary Map: VERIFIED

### 1.1 Execution Timeline with Transaction Boundaries

```
T0: Intent received
    │
T1: Intent → Goal → Plan
    │ [PLAN CREATION BOUNDARY]
    │
T2: Plan loaded and validated
    │ [DECISION INPUT READY BOUNDARY]
    │
T3: GOVERNANCE EVALUATION
    │ governance_evaluate(plan) → decision_record_id (UUID)
    │ [DECISION FORMATION BOUNDARY]
    │
T4: HG AUTHORIZATION
    │ hg_decision determined
    │ [AUTHORIZATION BOUNDARY]
    │
T5: EXECUTION (per-action)
    │ execute_action() → execution_id
    │ [EXECUTION BOUNDARY]
    │
T6: EVENT WRITE
    │ event_gate.process_event() → event_id
    │ ├─ SQLite transaction (INSERT + UPDATE + COMMIT)
    │ │  [EVENT PERSISTENCE BOUNDARY - atomic within mocka_events.db]
    │ │
    │ └─ companion event (optional)
    │
T7: POST-EXECUTION
    │ evaluate_result(), update_evaluation_history()
    │ [POST-EXECUTION BOUNDARY]
    │
T8: EVIDENCE GENERATION (COULD HAPPEN)
    │ generate_evidence_record() from mocka_events.db
    │ [EVIDENCE GENERATION BOUNDARY]
```

### 1.2 Existing Transaction Characteristics

#### Decision Ledger Write (mocka_decision_write)
**Location:** mocka_mcp_server.py (line 1143-1168)

```python
# Step 1: Append to JSONL file
with open(DECISION_LEDGER_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(record, ensure_ascii=False) + "\n")

# Step 2: Optional companion event (separate HTTP call)
r = requests.post(GATE_URL, json=gate_payload, timeout=5)
```

**Characteristics:**
- ✓ JSONL append (atomic at line level)
- ✗ NO cross-file transaction
- ✗ NO rollback if companion event fails
- ✓ Append-only semantics enforced

**Transaction Boundary:** Single file line

#### Event Write (event_gate.process_event)
**Location:** phi_os/event_gate.py (line 46-101)

```python
# Step 1: INSERT into events
conn.execute(f'INSERT OR IGNORE INTO events (...) VALUES (...)', vals)

# Step 2: Compute signature
sig = integrity.sign_event(conn, row)

# Step 3: UPDATE trace_id/related_event_id
conn.execute('UPDATE events SET trace_id = ?, related_event_id = ? WHERE event_id = ?', ...)

# Step 4: COMMIT
if owns_conn:
    conn.commit()
```

**Characteristics:**
- ✓ SQLite transaction (INSERT + COMPUTE + UPDATE + COMMIT)
- ✓ Atomic within mocka_events.db
- ✗ NO atomicity with Decision Ledger
- ✓ Signature chain maintained

**Transaction Boundary:** Single SQLite transaction

#### Decision ↔ Event Relationship
```
mocka_decision_write
    │
    ├─ [1] JSONL append (Decision Ledger)
    │       [Transaction boundary 1: file line]
    │
    └─ [2] HTTP POST to event_gate (companion event)
            [Transaction boundary 2: separate HTTP]

Result:
- Decision persisted ✓
- Event persisted ✓
- Atomic together ✗
```

### 1.3 Failure Scenarios

**Scenario A: Decision Ledger succeeds, companion event fails**
- Decision record exists in Decision Ledger
- No event created
- No automatic rollback of Decision

**Scenario B: Companion event succeeds, Decision Ledger write fails**
- Event exists in events.db
- No Decision record in Ledger
- Orphaned event

**Status:** Current architecture has NO cross-boundary transaction protection.

---

## 2. Persistence Target Comparison: TECHNICAL ANALYSIS

### 2.1 Option A: Extend mocka_events.db

**Schema extension option:**
```sql
CREATE TABLE evidence_records (
  record_id TEXT PRIMARY KEY,
  evidence_class TEXT,        -- "pre-decision" | "post-execution"
  source_provenance TEXT,     -- JSON array
  plan_id TEXT,
  decision_record_id TEXT,
  execution_id TEXT,
  evidence_data TEXT,         -- JSON
  created_at TEXT,
  generated_by TEXT,
  source_event_range_start TEXT,
  source_event_range_end TEXT
)
```

**Pros:**
- Atomic with Event writes (same transaction)
- Single DB for related records
- Existing SQLite infrastructure
- Signature chain extensible

**Cons:**
- DB footprint increase
- Semantically mixes Events + Evidence (different concerns)
- Schema validation complexity
- Future schema conflicts risk
- Breaking change to event_gate.py payload handling

**Transaction implication:**
- Can achieve Decision ↔ Event ↔ Evidence atomicity (via wrapper transaction)
- Requires modification to event_gate.py or new wrapper

### 2.2 Option B: Dedicated Evidence Database

**New database: vasai_evidence.db**
```sql
CREATE TABLE pre_decision_evidence (
  record_id TEXT PRIMARY KEY,
  plan_id TEXT,
  decision_record_id TEXT,
  source_provenance TEXT,
  evidence_data TEXT,
  created_at TEXT,
  generated_by TEXT
)

CREATE TABLE post_execution_evidence (
  record_id TEXT PRIMARY KEY,
  execution_id TEXT,
  event_range_start TEXT,
  event_range_end TEXT,
  source_provenance TEXT,
  evidence_data TEXT,
  created_at TEXT,
  generated_by TEXT
)
```

**Pros:**
- Clean separation of concerns
- Evidence-specific schema
- Easy backup / export
- No modification to existing DBs

**Cons:**
- Separate transaction boundary (2 DBs)
- Coordination required between Decision Ledger + Event DB + Evidence DB
- Three separate write failures possible
- More complex recovery

**Transaction implication:**
- NO atomic transaction across 3 boundaries
- Requires orchestration at application level

### 2.3 Option C: JSONL Canonical Records (Like Decision Ledger)

**New files:**
```
data/evidence/evidence_records.jsonl
{
  "record_id": "PER_20260921_xxxx",
  "evidence_class": "pre-decision",
  "plan_id": "...",
  "decision_record_id": "...",
  "source_provenance": [...],
  "evidence_data": {...},
  "created_at": "...",
  "generated_by": "..."
}

data/evidence/evidence_records_post.jsonl
(for post-execution evidence)
```

**Pros:**
- Aligned with Decision Ledger pattern (proven)
- Append-only semantics built-in
- Immutability inherent
- No schema management
- No DB transaction complexity
- Minimal schema (just fields)
- Easy auditing / version control

**Cons:**
- Less queryable than DB table
- May need secondary index file
- Larger file per record
- No query optimization

**Transaction implication:**
- Same as Decision Ledger: atomic at line level, no cross-file transactions
- Consistent with existing institutional pattern

### 2.4 Technical Recommendation for HG-17-A

**Recommendation:** Option C (JSONL)

**Rationale:**
1. **Consistency:** Decision Ledger already uses JSONL (proven institutional pattern)
2. **Atomicity:** Matches existing transaction boundaries (file line, not cross-file)
3. **Immutability:** Append-only enforced by file semantics
4. **Risk:** Minimal impact on existing DB/runtime
5. **Institutional:** Evidence as "canonical record" naturally maps to immutable append-only format
6. **Backward compatibility:** NO modification to existing Event DB or Decision Ledger
7. **HG-17-B alignment:** Source provenance easy to include as JSON field

**Trade-off:** Slightly less queryable than DB, but compensated by:
- Consistency with existing patterns
- No schema lock-in
- Simpler transaction semantics
- Lower deployment risk for sandbox

**Status:** TECHNICAL RECOMMENDATION ONLY. HG-17-A = D remains pending. Human Gate will make final persistence target decision.

---

## 3. Source Provenance Implementation: HG-17-B = D

### 3.1 Sources Actually Available in Runtime

**VERIFIED - AVAILABLE AT T3 (Decision time):**

1. **Source Type: plan_metadata**
   ```
   Available: intent_id, plan_id, steps, action_ids
   Location: plan.json (loaded at T2)
   Validity: VALIDATED (loaded and validated by plan_validator.py)
   Timestamp: plan creation time
   ```

2. **Source Type: governance_signal**
   ```
   Available: governance_decision, governance_reason
   Location: governance_evaluate() return (generated at T3)
   Validity: AVAILABLE (stub returns PASS, but field exists)
   Timestamp: T3
   ```

**NOT VERIFIED - AVAILABILITY DEPENDS:**

3. **Source Type: historical_execution_patterns**
   ```
   Available: IF execution-history.db or similar exists
   Location: UNKNOWN (not found in investigation)
   Validity: NOT VERIFIED
   Status: EVIDENCE GAP
   ```

4. **Source Type: governance_compliance**
   ```
   Available: IF governance rules evaluated at T3
   Location: governance_client.py (stub, doesn't evaluate)
   Validity: NOT VERIFIED (stub only)
   Status: EVIDENCE GAP
   ```

5. **Source Type: authorization_context**
   ```
   Available: IF authority/permission info available at T3
   Location: UNKNOWN
   Validity: NOT VERIFIED
   Status: EVIDENCE GAP
   ```

### 3.2 Source Provenance Record Structure

**HG-17-B = D requirement:** Each component must identify its source

**Implementation design:**

```json
{
  "record_id": "PER_20260921_xxxx",
  "evidence_class": "pre-decision",
  "plan_id": "xyz",
  "decision_record_id": "DC_20260921_nnn",
  "source_provenance": [
    {
      "component_id": "plan_structure",
      "source_type": "plan_metadata",
      "source_ref": "plan.json#intent_id",
      "validity_status": "validated",
      "source_timestamp": "2026-09-21T10:00:00Z",
      "extraction_method": "plan_validator.py",
      "data_sample": {
        "intent_id": "I_20260921_001",
        "plan_id": "P_20260921_001",
        "steps_count": 3
      }
    },
    {
      "component_id": "governance_signal",
      "source_type": "governance_signal",
      "source_ref": "governance_client.evaluate()#governance_decision",
      "validity_status": "unverified",
      "source_timestamp": "2026-09-21T10:00:15Z",
      "extraction_method": "governance_client.py",
      "note": "MVP stub implementation; always returns PASS",
      "data_sample": {
        "governance_decision": "PASS",
        "governance_reason": "Plan P_20260921_001 passed governance check (stub)"
      }
    }
  ],
  "evidence_data": {
    "structural_validity": true,
    "plan_action_count": 3,
    "governance_baseline": "pass"
  },
  "created_at": "2026-09-21T10:00:15Z",
  "generated_by": "governance_evaluate()"
}
```

### 3.3 Validity Status Semantics (HG-17-B constraint)

**CRITICAL:** Source Exists ≠ Source Valid

```
validity_status enum:
  "validated"    - Source verified by independent mechanism
  "unverified"   - Source available, not independently verified
  "unknown"      - Source availability uncertain
  "invalid"      - Source known to be incorrect or inapplicable
```

**Rule:** DO NOT convert UNKNOWN into VALIDATED.

**Example:** governance_signal from stub always returns PASS
- Status: "unverified" (not because it's wrong, but because stub doesn't do real evaluation)
- NOT marked "validated"
- NOT marked "invalid"
- Remains UNVERIFIED until real governance engine replaces stub

### 3.4 Missing Sources (Evidence Gap)

**Available for Pre-Decision Evidence:** 2 sources
- plan_metadata ✓
- governance_signal ✓ (unverified in MVP)

**Not available for Pre-Decision Evidence:** 3 sources
- historical_execution_patterns ? (UNKNOWN if DB exists)
- governance_compliance ? (stub doesn't evaluate)
- authorization_context ? (UNKNOWN if available)

**Status:** Pre-Decision Evidence with 2 components feasible. Historical/compliance/authorization require Phase 2-B investigation or Phase 3 work.

---

## 4. Decision ↔ Evidence Bidirectional Binding: HG-17-C = C

### 4.1 Requirement

HG-17-C: Decision と Evidence の双方向 identity reference

```
Decision
   ↕
Evidence
```

### 4.2 Implementation Options

**Option I: Decision Ledger Extended**

```json
{
  "decision_id": "DC_20260921_nnn",
  "title": "...",
  "...existing fields...",
  "evidence_records": [
    "PER_20260921_xxxx"
  ]
}
```

Pros: Single Decision record carries Evidence reference  
Cons: Decision Ledger JSONL append-only, adding evidence_records field changes structure

**Option II: Evidence Record Extended (as designed in section 3.2)**

```json
{
  "record_id": "PER_20260921_xxxx",
  "...evidence fields...",
  "decision_record_id": "DC_20260921_nnn"
}
```

Pros: Evidence carries Decision reference  
Cons: Requires Decision to already exist (chicken-and-egg for pre-decision evidence)

**Option III: Separate Binding Record (New Table/File)**

```
data/evidence/evidence_bindings.jsonl
{
  "binding_id": "EB_20260921_001",
  "decision_record_id": "DC_20260921_nnn",
  "evidence_record_id": "PER_20260921_xxxx",
  "binding_timestamp": "...",
  "binding_reason": "decision_rationale"
}
```

Pros: No modification to existing records  
Cons: Third file/table to maintain

**Option IV: Decision Ledger Index File**

```
data/decisions/decision_evidence_index.jsonl
{
  "decision_id": "DC_20260921_nnn",
  "evidence_ids": ["PER_20260921_xxxx"],
  "indexed_at": "..."
}
```

Pros: Separate index, no record modification  
Cons: Index maintenance required

### 4.3 Design Decision for Bidirectional Reference

**Chosen approach:** Hybrid (Option II + Index)

**Rationale:**
1. Evidence record carries decision_record_id (Option II)
   - Pre-Decision Evidence: decision_record_id points to existing Decision
   - Post-Execution Evidence: decision_record_id points to historical Decision
   
2. Decision record indexed separately (Option IV-like)
   - Reverse lookup from Decision to Evidence (optional, index file)
   - No modification to existing Decision Ledger JSONL

**Implementation:**
```json
// Evidence record (in evidence_records.jsonl)
{
  "record_id": "PER_20260921_xxxx",
  "evidence_class": "pre-decision",
  "decision_record_id": "DC_20260921_nnn",      ← Forward ref
  "source_provenance": [...],
  ...
}

// Optional: Decision evidence index (new file)
// data/evidence/decision_evidence_index.jsonl
{
  "decision_id": "DC_20260921_nnn",
  "evidence_records": ["PER_20260921_xxxx"],   ← Reverse ref
  "indexed_at": "2026-09-21T10:00:15Z"
}
```

**Traversal:**
- Decision → Evidence: Look up Decision ID in index file (read)
- Evidence → Decision: Read evidence_record_id field (direct)

**Backward Compatibility:**
- ✓ Existing Decision Ledger records unchanged
- ✓ New index file optional (can be rebuilt)
- ✓ Evidence record field addition compatible

---

## 5. Pre-Decision vs. Post-Execution Evidence Class Enforcement: HG-17-C Implication

### 5.1 Enforcement Mechanism

**Requirement:** Prevent post-execution Evidence from retroactively justifying pre-decision rationale

**Schema:**
```json
{
  "record_id": "...",
  "evidence_class": "pre-decision" | "post-execution",  ← Class indicator
  "decision_record_id": "...",
  "...
}
```

### 5.2 Enforcement Rules

**Rule 1: Class Immutability**
- Once Evidence written, evidence_class cannot change
- Append-only semantics (JSONL) enforces this

**Rule 2: Cross-Class Substitution Forbidden**
- Decision MUST specify which evidence_class it relies on
- At Decision review time: verify evidence_class matches

**Rule 3: Temporal Constraint**
- Pre-Decision Evidence: created BEFORE execution (T3-T5)
- Post-Execution Evidence: created AFTER execution (T8+)
- Timestamp validation prevents class violation

### 5.3 Violation Detection

**Scenario:** Attempt to use Post-Execution Evidence to justify Pre-Decision

```
Decision (T3):
  "decision_id": "DC_20260921_nnn",
  "evidence_class_requirement": "pre-decision"
  "evidence_record_id": "PER_20260921_xxxx"

Evidence PER_20260921_xxxx (T8):
  "record_id": "PER_20260921_xxxx",
  "evidence_class": "post-execution"  ← VIOLATION!

Detection:
  Decision requires: "pre-decision"
  Evidence claims: "post-execution"
  → CLASS MISMATCH → REJECT
```

**Status:** Enforcement is schema-level, not runtime code-level. Prevents accidental substitution.

---

## 6. Backward Compatibility Assessment: VERIFIED

### 6.1 Existing Record Protection

**Constraint (HG-17-C Condition 7):** 
> Existing Event records、Existing Decision records、Existing runtime behaviorを無断変更しない

**Verification:**

```
Existing mocka_events.db
  ├─ event records: [no change] ✓
  ├─ schema: [no change] ✓
  ├─ event_id generation: [no change] ✓
  └─ signatures: [no change] ✓

Existing Decision Ledger (decision_ledger.jsonl)
  ├─ decision records: [no change] ✓
  ├─ format: JSONL [no change] ✓
  └─ append-only: [no change] ✓

Existing Runtime Behavior
  ├─ governance_evaluate(): [no change] ✓
  ├─ hg_gateway.authorize_and_execute(): [no change] ✓
  ├─ event_gate.process_event(): [no change] ✓
  └─ mocka_decision_write(): [no change] ✓
```

### 6.2 New Records Only

**What is added (no existing modification):**
- ✓ New directory: data/evidence/
- ✓ New file: evidence_records.jsonl
- ✓ New file: evidence_records_post.jsonl (if post-execution evidence added)
- ✓ Optional: decision_evidence_index.jsonl (index only)

**Status:** Full backward compatibility maintained.

---

## 7. Sandbox Implementation Boundary: DEFINED

### 7.1 What IS Authorized (Sandbox Implementation Design)

1. ✓ JSONL file creation (data/evidence/evidence_records.jsonl)
2. ✓ Evidence record format definition and validation
3. ✓ Source provenance component structure
4. ✓ Decision ↔ Evidence binding mechanism design
5. ✓ Class distinction enforcement rules
6. ✓ Migration/generation scripts (sandbox only, not production run)
7. ✓ Test/validation framework (sandbox)
8. ✓ Documentation of implementation approach

### 7.2 What IS NOT Authorized

1. ✗ NO production mocka_events.db modification
2. ✗ NO production Decision Ledger modification
3. ✗ NO production runtime code modification
4. ✗ NO activation/deployment to production
5. ✗ NO production Evidence record generation
6. ✗ NO retroactive Evidence creation for historical Decisions
7. ✗ NO modification of existing Event records
8. ✗ NO transaction wrapper around Decision + Evidence writes (yet)

### 7.3 Sandbox Scope for Phase 2-C (If Authorized)

**Expected Phase 2-C activities:**
- Create evidence_records.jsonl in sandbox environment
- Generate sample Pre-Decision Evidence from test Plans
- Validate source_provenance component structure
- Test bidirectional binding (Decision ↔ Evidence)
- Verify class enforcement (pre-decision vs. post-execution)
- Evidence read-back validation
- Document implementation results

---

## 8. Verified / Not Verified / Evidence Gap / Unknown Classification

### VERIFIED (From Investigation)

1. ✓ Plan metadata (intent_id, plan_id, steps, action_ids) available at T3
2. ✓ Transaction boundaries: Decision Ledger (file line), Events (SQLite tx), NOT atomic together
3. ✓ Existing sources for Pre-Decision Evidence: plan_metadata, governance_signal
4. ✓ Decision Ledger append-only semantics work well for Evidence
5. ✓ Backward compatibility achievable (no existing record modification needed)
6. ✓ Evidence class distinction enforceable via schema
7. ✓ Decision ↔ Evidence bidirectional reference possible without modifying existing records
8. ✓ Source provenance field structure viable

### NOT VERIFIED (Requires Phase 2-C Sandbox Implementation)

1. ? JSONL Evidence file performance under load
2. ? Index file maintenance overhead (decision_evidence_index.jsonl)
3. ? Search/query performance on JSONL files (vs. DB)
4. ? Reader implementation for Evidence records
5. ? Integration points with Decision Ledger workflow

### EVIDENCE GAP (Requires Investigation or HG Decision)

1. ? Historical execution patterns available (does execution-history.db exist?)
2. ? Governance compliance rules evaluable at T3 (stub only, no real rules)
3. ? Authorization context available (permission/authority info at T3?)
4. ? Transaction wrapper implementation (Decision + Evidence atomic write)
5. ? Retroactive Evidence creation semantics (is it ever needed?)

### UNKNOWN (Deferred to Later Phase)

1. ? Post-Execution Evidence implementation details
2. ? Evidence retention policy (append-only forever?)
3. ? Archive/cleanup strategy
4. ? Integration with Evidence verification/audit
5. ? Evidence replication/backup policy

---

## 9. Unresolved Items Requiring New Human Gate Decisions

### HG-18-A: Transaction Atomicity for Decision ↔ Evidence

**Question:** Should Pre-Decision Evidence generation and Decision Ledger write be atomic?

**Options:**
- A: Yes, require atomic transaction (both succeed or both fail)
- B: No, accept current separate-write model (Decision first, Evidence follows)
- C: Defer to Phase 2-C (implement design, verify in sandbox, then decide)

**Current:** mocka_decision_write already writes Decision (line 1143) before optionally writing companion event (line 1162-1166). If atomic transaction required, this needs redesign.

### HG-18-B: Evidence Record Format Evolution

**Question:** If new source types become available (historical patterns, compliance, authorization), can evidence_records.jsonl schema be extended?

**Options:**
- A: Yes, add new source_provenance components freely (append-only safe)
- B: No, freeze schema now
- C: Require HG approval for each new source type

**Current:** JSONL format allows flexible schema. But HG-17-B = D requires source_provenance, so changes should be controlled.

### HG-18-C: Index File Necessity

**Question:** Is decision_evidence_index.jsonl file necessary for implementation?

**Options:**
- A: Yes, include index for Decision → Evidence lookup
- B: No, rely on Evidence record decision_record_id field only (backward lookup only)
- C: Make index optional (add in Phase 2-C if needed)

**Current:** Hybrid design supports both directions without index, but index improves query efficiency.

### HG-18-D: Evidence Class Default Assignment

**Question:** If Evidence record creation doesn't explicitly specify evidence_class, what should default be?

**Options:**
- A: Require evidence_class to be explicitly provided (error if missing)
- B: Default to "unclassified" (new class)
- C: Infer from timing (T3-T5 → pre-decision, T8+ → post-execution)

**Current:** Evidence should be explicitly classified by creator. No auto-inference.

---

## 10. Implementation Design Summary

### Pre-Decision Evidence Architecture (Sandbox)

**Persistence:** JSONL canonical records (like Decision Ledger)
- File: data/evidence/evidence_records.jsonl
- Format: JSON per line, append-only
- Immutability: Enforced by file semantics

**Record Structure:**
```json
{
  "record_id": "PER_YYYYMMDD_xxxxxxxx",
  "evidence_class": "pre-decision" | "post-execution",
  "plan_id": "...",
  "decision_record_id": "...",
  "source_provenance": [
    {
      "component_id": "...",
      "source_type": "plan_metadata" | "governance_signal" | ...,
      "source_ref": "...",
      "validity_status": "validated" | "unverified" | "unknown" | "invalid",
      "data_sample": {...}
    }
  ],
  "evidence_data": {...},
  "created_at": "ISO8601",
  "generated_by": "..."
}
```

**Decision ↔ Evidence Binding:**
- Evidence.decision_record_id → Decision (forward link, always present)
- Optional: decision_evidence_index.jsonl → Evidence (reverse links, optional index)

**Class Enforcement:**
- Pre-Decision Evidence: created T3-T5 (before execution)
- Post-Execution Evidence: created T8+ (after execution)
- Cross-class substitution prevented by schema validation

**Source Provenance:**
- Explicit per component (plan_metadata, governance_signal, etc.)
- Validity independently tracked (not inferred from existence)
- UNKNOWN preserved (not converted to VALIDATED)

**Backward Compatibility:**
- ✓ NO change to existing Event records
- ✓ NO change to existing Decision Ledger format
- ✓ NO change to existing runtime behavior
- ✓ New files only

### Authorization Status
- ✓ DESIGN: Complete (this document)
- ✓ SANDBOX: Ready for Phase 2-C implementation
- ✗ PRODUCTION: NOT AUTHORIZED (awaits HG-18-A/B/C/D decisions)

---

## Conclusion: Phase 2-B Design Complete

**Status:** IMPLEMENTATION DESIGN READY FOR SANDBOX

**Next Steps:**
1. Human Gate reviews this design
2. Human Gate answers HG-18-A/B/C/D (if proceeding to Phase 2-C)
3. Phase 2-C: Sandbox implementation
4. Phase 2-D: Runtime verification
5. Phase 2-E: Evidence read-back validation
6. Phase 2-F: Human Gate review of sandbox results

**Unresolved for Human Gate:**
- HG-18-A: Transaction atomicity requirement
- HG-18-B: Schema evolution policy
- HG-18-C: Index file necessity
- HG-18-D: Evidence class default assignment

**No production changes authorized. All work remains sandbox/design phase.**

---

**Report Author:** KUROKO (Phase 2-B Implementation Design)  
**Status:** SANDBOX DESIGN COMPLETE  
**Authorization Level:** Design only; sandbox implementation subject to HG-18 decisions  
**Production Authorization:** NOT GRANTED  
**Date:** 2026-09-21

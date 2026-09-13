# D3: Failure & Recovery Specification
**HG-D2 Track / 2026-09-14**

## Document Control

- **Classification:** GOVERNANCE / HG-D2 DESIGN / FAILURE & RECOVERY
- **Authority:** HG-D2-03 (Failure & Recovery Design)
- **Scope:** Formal specification of persistence failure modes and recovery procedures
- **Implementation Authorization:** NOT_GRANTED
- **Status:** DESIGN SPECIFICATION COMPLETE
- **Dependency:** D1 (Architecture), D2 (Evidence Binding)

---

## PART 1: Failure Modes

### F1: Consequence Loss
- **Description:** ActualConsequence recorded but evidence lost/corrupted
- **Detection:** Evidence gap detected in verification
- **Recovery:** Evidence reconstruction from audit trail (if possible)
- **Fail-Closed:** Mark consequence as UNVERIFIED; escalate to HG

### F2: Audit Trail Break
- **Description:** Evidence collected but lineage link broken (causality interrupted)
- **Detection:** Chain verification fails (missing intermediate records)
- **Recovery:** Attempt reconstruction using timestamp ordering and causality hints
- **Fail-Closed:** Cannot use evidence for governance decision; escalate

### F3: State Inconsistency
- **Description:** Canonical state and actual consequence state diverge
- **Detection:** State verification check fails
- **Recovery:** Replay evidence from last known-good state checkpoint
- **Fail-Closed:** Do not infer correct state; escalate to HG

### F4: Authorization Binding Loss
- **Description:** Authorization decision exists but consequence link lost
- **Detection:** Orphaned authorization found in audit
- **Recovery:** Attempt to reconstruct consequences from evidence timestamps
- **Fail-Closed:** Cannot assume consequences; escalate for manual review

---

## PART 2: Recovery Procedures

### R1: Evidence Reconstruction

**Procedure:**
1. Identify missing evidence record
2. Search audit trail for related events/observations
3. If foundational events exist, attempt evidence synthesis
4. Mark reconstructed evidence as PARTIAL or SYNTHESIZED (not VERIFIED)
5. Cannot proceed with governance decision until VERIFIED

**Fail-Closed Rule:**
- Reconstructed evidence cannot substitute for original evidence in authorization verification
- Synthesis only permitted for audit/investigation purposes
- Governance decisions require original VERIFIED evidence

### R2: Lineage Repair

**Procedure:**
1. Identify break in evidence chain
2. Locate last chain element and next chain element
3. Verify causality is plausible (timestamps, logical sequence)
4. If gap < threshold and causality consistent, repair with gap notation
5. If gap > threshold or causality impossible, mark chain BROKEN

**Fail-Closed Rule:**
- Repaired chains explicitly marked as NON-PRISTINE
- Cannot use repaired chain for new authorization verification
- Can use for audit/investigation only

### R3: State Recovery

**Procedure:**
1. Identify last verified state checkpoint
2. Retrieve all verified evidence records after checkpoint
3. Replay events in timestamp order
4. Reconstruct state by applying each event
5. Compare reconstructed state to canonical state
6. If match, state recovered; if divergence, escalate

**Fail-Closed Rule:**
- No inference about what state "should be"
- If reconstruction diverges from canonical state, both marked UNCERTAIN
- Escalate to HG for adjudication

---

## PART 3: Persistence Layer Failure Handling

### PF1: Database Corruption

**Scenario:** Persistence store (SQLite, ledger file, etc.) corrupted
**Detection:** Checksum verification fails or read errors occur
**Response:**
1. Mark affected data as CORRUPTED
2. Attempt to reconstruct from backup (if available and verified)
3. If reconstruction succeeds, mark recovered data with RECOVERY_SOURCE
4. If reconstruction fails, mark consequences as UNVERIFIABLE
5. Escalate to HG with full corruption report

### PF2: Synchronization Failure

**Scenario:** Multi-layer persistence (event store + ledger + relational) desynchronized
**Detection:** Query results inconsistent across layers
**Response:**
1. Identify which layer is authoritative (canonical source)
2. Query results from authoritative layer only
3. Repair other layers from canonical source
4. Mark repair with SYNC_RECOVERY timestamp
5. Escalate to HG if synchronization cannot be resolved

### PF3: Persistence Store Unavailable

**Scenario:** Persistence store (database, filesystem, etc.) unreachable
**Detection:** Persistence operations timeout or return connection errors
**Response:**
1. Fail-closed: Do not continue without persistence verification
2. Block evidence collection and consequence recording
3. Queue operations for retry when store recovers
4. Escalate to HG about persistence layer outage
5. Do not resume operations until store confirmed operational

---

## PART 4: Recovery Verification

### RV1: Evidence Integrity Check

**After any recovery:**
1. Recompute evidence checksums/hashes
2. Verify authorization references still valid
3. Verify timestamp sequences are monotonic
4. Verify no gaps or duplicates introduced
5. Mark recovery status in evidence metadata

**If verification fails:**
- Recovery incomplete; escalate for manual review
- Do not use recovered evidence in governance decisions

### RV2: Chain Continuity Check

**After any recovery:**
1. Recompute chain from authorization through final governance decision
2. Verify all elements present and correctly linked
3. Verify no new gaps introduced in recovery
4. Mark recovery status in chain metadata

**If verification fails:**
- Chain not fully recovered; mark as BROKEN
- Cannot support new governance decisions

---

## PART 5: Fail-Closed Enforcement

### FC1: Unresolved Recovery

**Rule:** If recovery procedure cannot fully restore verified state, must escalate to HG.

**Implementation:**
- No automatic retry loops (bounded retry only)
- No inference to substitute for missing verification
- No governance progression without complete evidence

### FC2: Partial Evidence Handling

**Rule:** Partial evidence cannot be used for authorization verification.

**Implementation:**
- PARTIAL status blocks governance decision
- Escalate gaps; do not assume resolution
- Mark all uses of partial evidence

### FC3: Consistency Escalation

**Rule:** Irreconcilable state inconsistency must be escalated to HG.

**Implementation:**
- Do not pick "most likely" state
- Do not assume which version is correct
- Present both versions to HG with evidence for each

---

## PART 6: Recovery Boundaries

### What Recovery CAN Do:
- Reconstruct lost evidence from related audit events
- Repair broken chains with gap documentation
- Recover state from last known-good checkpoint
- Verify integrity of recovered data

### What Recovery CANNOT Do:
- Generate new evidence (evidence synthesis only for audit)
- Infer correct state without evidence
- Modify authorization to match recovered state
- Create governance decisions about recovery (HG decides)

---

## PART 7: Open Issues (D3-Specific)

### OI-D3-01: Backup Strategy
**Issue:** How frequently must backups be taken?
- Impact: Recovery point objective (RPO) determination
- Options: Continuous | Periodic | On-demand | Per-decision
- Status: OPEN - requires systems architecture guidance

### OI-D3-02: Recovery Authority
**Issue:** Who determines if recovered evidence is acceptable?
- Impact: Whether recovery success is automatic or requires HG approval
- Options: Automated + escalate on failure | HG approves all recovery | Hybrid
- Status: OPEN - requires authority boundary decision

---

## PART 8: Consistency Audit

**State Locks Maintained:** All preserved ✓
**Design Boundary:** Design ≠ Implementation ✓
**Authority Boundary:** Recovery decisions ≠ Authorization decisions ✓

---

**D3 SPECIFICATION COMPLETE — READY FOR HG-D2 REVIEW**

D3 establishes failure modes and recovery procedures within fail-closed architecture.

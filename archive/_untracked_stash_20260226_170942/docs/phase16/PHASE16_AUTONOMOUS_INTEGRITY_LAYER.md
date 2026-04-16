PHASE16 Autonomous Integrity Layer Specification (Draft v0.1)
date: 2026-02-24
scope:
- Introduce an autonomous integrity subsystem responsible for anchors and irreversible commitments.
- Phase15 remains read-only reconciliation/visibility.

goals:
1) Provide "proof anchors" as immutable commitment points.
2) Bind anchors cryptographically to governance/audit artifacts.
3) Enable external attestation without mutating governance DB history.

non-goals:
- Do not retrofit Phase15 reconcile layer to create or enforce proof_anchor.
- Do not allow silent mutation of governance DB.

architecture:
A) integrity_db (new, separate)
   - tables:
     - proof_anchor
       - anchor_id (pk)
       - created_utc
       - source_event_id
       - source_chain_hash
       - final_chain_hash
       - signature_ed25519
       - public_key_id
       - note
     - attestation_log
       - attestation_id (pk)
       - created_utc
       - anchor_id
       - verifier
       - result
       - detail_json

B) interfaces
   - create_anchor (explicit command; never implicit)
   - verify_anchor (read-only verification)
   - export_attestation_pack (for external verification)

controls:
- All writes only occur inside integrity_db (never governance DB).
- Every write emits an audit event into reconciliation_log (visibility).
- Strict deterministic serialization for signed payload.

phase15 compatibility:
- phase15_audit_scan keeps reporting ANCHOR_PROOF as NG until Phase16 is deployed.
- After Phase16, ANCHOR_PROOF check changes to:
  "anchor exists and matches final_chain_hash and signature verifies".

milestones:
- M1: define schema + deterministic payload format
- M2: implement create_anchor (explicit)
- M3: implement verify/export tooling
- M4: connect Phase15 scan to Phase16 verifier (read-only)

notes:
- No enforcement until Phase16 passes external verification pack checks.

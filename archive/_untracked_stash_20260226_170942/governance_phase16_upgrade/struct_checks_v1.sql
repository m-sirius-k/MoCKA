-- NOTE: STRUCT checks v1
-- NOTE: These checks are designed to back INV-STRUCT-001..004.
-- NOTE: Some table/column names may differ in your DB. If a query errors, map names and re-run.

-- INV-STRUCT-001: GENESIS must be unique
-- Expected: exactly 1 genesis event.
-- Replace event_type column name if needed.
SELECT 'INV-STRUCT-001' AS invariant_id,
       CASE WHEN COUNT(*) = 1 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS observed_count
FROM governance_ledger_event
WHERE event_type = 'GENESIS';

-- INV-STRUCT-002: TIP must be reachable from GENESIS
-- This check is graph-specific; placeholder returns PASS if both exist.
-- Real reachability is implemented in Python verifier using chain traversal.
SELECT 'INV-STRUCT-002' AS invariant_id,
       'DEFERRED' AS status,
       'Reachability checked in struct_verify_v1.py' AS note;

-- INV-STRUCT-003: branch_registry.classification must NOT be NULL
-- If branch_registry does not exist in your governance DB, point this to correct DB/table.
SELECT 'INV-STRUCT-003' AS invariant_id,
       CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
       COUNT(*) AS null_classification_rows
FROM branch_registry
WHERE classification IS NULL;

-- INV-STRUCT-004: quarantine must not be TIP-selectable
-- If tip table differs, Python verifier checks TIP file and branch classification.
SELECT 'INV-STRUCT-004' AS invariant_id,
       'DEFERRED' AS status,
       'Quarantine/TIP selection checked in struct_verify_v1.py' AS note;
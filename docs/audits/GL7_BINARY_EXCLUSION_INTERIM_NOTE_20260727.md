# GL7 Binary Extension Exclusion - Interim Note (2026-07-27)

## Status

Provisional record. GL7 write path (mocka_write_event / mocka_integrity_write /
mocka_decision_write / mocka_add_todo) is currently blocked by
GL7_EXECUTION_BLOCKED (encoding_mismatch:docs/images/name-omitted.pdf), so this
implementation cannot be preceded by a normal PHL record. This file is the
interim substitute record required by kimura-hakase's explicit chat
instruction (2026-07-27), to be superseded by a formal mocka_write_event /
mocka_integrity_write / mocka_decision_write entry once GL7 is unblocked.

## Trigger

TODO_447 (completed[] to ARCHIVE flush mechanism) Phase 1 execution hit
GL7_EXECUTION_BLOCKED when calling mocka_write_event. mocka_check_utf8
confirmed the flagged file is a binary PDF (270943 bytes, UTF-8 decode error
at byte 10, cp932 decode also fails) - a false positive, not a real
mis-encoding.

Diagnostic step (per kimura-hakase's instruction): mocka_decision_write and
mocka_add_todo were also attempted with real Phase 0 content and both
returned the same GL7_EXECUTION_BLOCKED error. All three registration tools
(mocka_integrity_write / mocka_decision_write / mocka_add_todo) are blocked,
confirming this is not specific to mocka_write_event.

## Root cause (located via mocka_search / mocka_list_events)

File: C:/Users/sirok/MoCKA/structural/execution_governance.py
Function: ExecutionGovernanceEngine.check_abort_conditions (around line 171-179)

The loop decodes every changed file's bytes as UTF-8 to detect
encoding_mismatch, with an inline exclusion set for only
{".sqlite-shm", ".sqlite-wal", ".db"} (a hardcoded duplicate of the
module-level BINARY_EXTENSIONS constant defined at line 70-74, which was
never actually referenced by the check). No other binary extension is
excluded, so any binary file (PDF, image, office document, archive, etc.)
that fails UTF-8 decoding trips encoding_mismatch and blocks all
GL7-gated write tools repo-wide.

This is the same class of issue as the 2026-07-14 incident (root-level
UTF-16LE files, see GL7_ENCODING_REMEDIATION_EVIDENCE_20260714.md in this
directory), where the remediation was limited to re-encoding the specific
files rather than generalizing the exclusion by extension. That gap is why
the same failure mode recurred here with a different file type (binary PDF
instead of mis-encoded text).

## Planned fix

1. Expand the module-level BINARY_EXTENSIONS constant to include common
   binary extensions (.pdf/.png/.jpg/.jpeg/.gif/.docx/.xlsx/.pptx/.zip/.bin)
   in addition to the existing three (.sqlite-shm/.sqlite-wal/.db).
2. Replace the inline hardcoded set in check_abort_conditions with a
   reference to the module-level BINARY_EXTENSIONS constant (case-insensitive
   suffix match), so there is a single source of truth.
3. Explicitly NOT adding a null-byte-based binary heuristic as an additional
   skip condition, even though it was offered as an optional enhancement.
   Reason: UTF-16LE files (the exact failure mode from 2026-07-14) contain
   many null bytes for ASCII-range characters, so a null-byte skip would
   silently defeat the legitimate encoding_mismatch detection that GL7 is
   supposed to provide for mis-encoded text files. Extension-based exclusion
   only, to avoid loosening genuine detection.
4. Verify with mocka_check_utf8 that this specific PDF file no longer trips
   the check in isolation, then verify the actual GL7 gate is clear by
   retrying a previously-blocked write tool call.

## Start time

2026-07-27, immediately before editing structural/execution_governance.py.
No code has been changed yet at the time this note is written.

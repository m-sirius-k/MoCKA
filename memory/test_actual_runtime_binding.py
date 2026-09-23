"""
MoCKA 3.0 — Memory Layer
test_actual_runtime_binding.py

STEP 11 Phase E: Actual Runtime Binding Verification

CRITICAL DISTINCTION:
  - test_memory_binding_runtime.py: Synthetic test (dataclass + persistence only)
  - test_actual_runtime_binding.py: Real pipeline execution (end-to-end)

Purpose:
  Verify that when MemoryPipeline.process() is called with actual Decision generation,
  the binding gets recorded in memory_binding_ledger.jsonl with real decision_id
  from decision_ledger.jsonl.

Expected Path:
  1. Call MemoryPipeline.process() (actual)
  2. Decision gets generated (actual) with decision_id from decision_engine
  3. Decision gets recorded in memory_store.json (actual)
  4. Past memories are retrieved (actual) with memory_ids
  5. Binding should be recorded: memory_id -> decision_id (THIS IS WHAT WE TEST)
  6. Read memory_binding_ledger.jsonl to verify

Result:
  If binding_ledger is empty after process(), then "Runtime Binding" is NOT verified.
  Integration is missing.
"""

import sys
import tempfile
from pathlib import Path

_MEMORY_DIR = Path(__file__).resolve().parent
if str(_MEMORY_DIR) not in sys.path:
    sys.path.insert(0, str(_MEMORY_DIR))

from memory_pipeline import MemoryPipeline
from memory_binding_store import MemoryBindingStore
from memory_store import MemoryStore


def check(label: str, condition: bool) -> bool:
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def main():
    print("\n" + "=" * 70)
    print("STEP 11 PHASE E: ACTUAL RUNTIME BINDING VERIFICATION")
    print("Real MemoryPipeline Execution with Binding Ledger")
    print("=" * 70 + "\n")

    results = []

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        memory_store_path = tmpdir_path / "memory_store.json"
        binding_store_path = tmpdir_path / "memory_binding_ledger.jsonl"

        # --- STEP 1: Setup ---
        print("[STEP 1] Pipeline Setup")
        mem_store = MemoryStore(memory_store_path)
        bind_store = MemoryBindingStore(binding_store_path)
        pipeline = MemoryPipeline(mem_store)

        results.append(check(
            "MemoryPipeline initialized",
            pipeline is not None,
        ))

        # --- STEP 2: Execute Actual Pipeline ---
        print("\n[STEP 2] Execute MemoryPipeline.process()")

        test_text = "Please implement a comprehensive feature with proper documentation"
        test_context = {
            "phase": "phase2-3",
            "active_task": "TODO_impl_comprehensive",
        }

        try:
            decision_result, enriched_context = pipeline.process(test_text, test_context)
            results.append(check(
                "MemoryPipeline.process() executed successfully",
                decision_result is not None and enriched_context is not None,
            ))

            results.append(check(
                "DecisionResult has selected_action",
                bool(decision_result.selected_action),
            ))

            results.append(check(
                "EnrichedContext returned",
                enriched_context.intent_key is not None,
            ))
        except Exception as e:
            results.append(check(
                f"MemoryPipeline.process() failed: {e}",
                False,
            ))
            print(f"\nERROR: {e}")
            return 2

        # --- STEP 3: Check Memory Store ---
        print("\n[STEP 3] Verify Decision Recorded in Memory Store")
        mem_entries = mem_store.all()
        results.append(check(
            f"Memory store has {len(mem_entries)} entries",
            len(mem_entries) >= 1,
        ))

        if mem_entries:
            decision_memory_id = mem_entries[0].memory_id if mem_entries else None
            results.append(check(
                f"Decision recorded with memory_id: {decision_memory_id}",
                decision_memory_id is not None,
            ))

        # --- STEP 4: Check Past Memories Retrieved ---
        print("\n[STEP 4] Verify Past Memories Retrieved")
        results.append(check(
            f"EnrichedContext.past_decisions count: {len(enriched_context.past_decisions)}",
            isinstance(enriched_context.past_decisions, tuple),
        ))

        past_memory_ids = [m.entry.memory_id for m in enriched_context.past_decisions]
        results.append(check(
            f"Past memories retrieved: {len(past_memory_ids)} entries",
            len(past_memory_ids) >= 0,  # May be 0 on first run
        ))

        # --- STEP 5: CHECK FOR BINDING LEDGER ENTRIES ---
        print("\n[STEP 5] Check Memory Binding Ledger")
        print("CRITICAL: Does binding_ledger contain entries for this decision?")

        binding_entries = bind_store.all()
        results.append(check(
            f"Binding ledger entries: {len(binding_entries)}",
            isinstance(binding_entries, tuple),
        ))

        if len(binding_entries) > 0:
            # FOUND: Binding ledger has entries
            results.append(check(
                "POSITIVE: Binding ledger contains entries (Runtime binding verified)",
                True,
            ))

            for binding in binding_entries:
                print(f"  - BIND: {binding.binding_id}")
                print(f"    Memory: {binding.knowledge_record_id}")
                print(f"    Decision: {binding.decision_id}")
                print(f"    Status: {binding.binding_status}")
        else:
            # NOT FOUND: Binding ledger is empty
            results.append(check(
                "NEGATIVE: Binding ledger is EMPTY (Runtime binding NOT verified)",
                False,
            ))
            print("\nCRITICAL FINDING:")
            print("  MemoryPipeline.process() did NOT record bindings.")
            print("  The MemoryBindingStore integration is MISSING from MemoryPipeline.")
            print("  This is expected (not yet integrated), but means:")
            print("  - Phase A (model): IMPLEMENTED [OK]")
            print("  - Phase D (ledger): IMPLEMENTED [OK]")
            print("  - Phase E (runtime): NOT YET VERIFIED")
            print("\n  To verify runtime binding, MemoryPipeline must be modified to")
            print("  call MemoryBindingStore.append() when recording decisions.")
            print("  This requires authorization (currently NOT authorized).")

        # --- STEP 6: Final Assessment ---
        print("\n[STEP 6] Runtime Binding Assessment")

        if len(binding_entries) > 0:
            results.append(check(
                "Runtime binding VERIFIED (bindings recorded)",
                True,
            ))
        else:
            results.append(check(
                "Runtime binding NOT YET VERIFIED (no bindings recorded)",
                False,
            ))

    # --- FINAL VERDICT ---
    print("\n" + "=" * 70)
    total = len(results)
    passed = sum(results)

    print(f"\nRESULTS: {passed}/{total} checks passed\n")

    if passed == total:
        print("VERDICT: RUNTIME BINDING VERIFIED")
        print("End-to-end pipeline binding works correctly.")
        return 0
    else:
        print("VERDICT: RUNTIME BINDING NOT YET VERIFIED")
        print(f"\nBindings recorded: {len(binding_entries)}")
        print("\nReason:")
        print("  MemoryPipeline.process() does not integrate MemoryBindingStore.")
        print("  It retrieves memories but does not record binding traces.")
        print("  This is a missing integration point.")
        print("\nConclusion:")
        print("  Phase A/D implementation is complete (dataclass + persistence work)")
        print("  Phase E test data persistence works (synthetic test passed)")
        print("  But actual runtime binding is NOT YET wired")
        print("\nNext Step:")
        print("  Requires authorization to modify MemoryPipeline.process() to")
        print("  call MemoryBindingStore when retrieving and recording decisions.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

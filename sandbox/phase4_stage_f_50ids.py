#!/usr/bin/env python3
"""
PHASE 4 STAGE F: EXTENDED ID COUNT (50 IDs per process)
To better match original TEST 6 (50-100 IDs per thread)
Tests: 2, 5, 10 processes with 50 IDs each
"""

import multiprocessing as mp
import sqlite3
import datetime
from pathlib import Path
import time
import json

SANDBOX_DB_PATH = Path(r"C:\Users\sirok\MoCKA\sandbox\mocka_events_sandbox.db")
PHASE4_RESULTS_DIR = Path(r"C:\Users\sirok\MoCKA\sandbox")

def worker_simple(process_id, num_ids, results_queue):
    """Simplified worker for Stage F - minimal overhead"""
    process_start = time.time()
    metrics = {
        'process_id': process_id,
        'generated': [],
        'errors': 0,
        'start_time': process_start,
        'end_time': None,
        'duration_ms': 0
    }

    try:
        con = sqlite3.connect(str(SANDBOX_DB_PATH), timeout=30.0)
        today = datetime.date.today().strftime("%Y%m%d")

        for op_idx in range(num_ids):
            try:
                con.execute("BEGIN IMMEDIATE")
                con.execute(
                    "INSERT OR IGNORE INTO decision_id_counters (date, counter) VALUES (?, 0)",
                    (today,)
                )
                con.execute(
                    "UPDATE decision_id_counters SET counter = counter + 1 WHERE date = ?",
                    (today,)
                )
                row = con.execute(
                    "SELECT counter FROM decision_id_counters WHERE date = ?",
                    (today,)
                ).fetchone()

                next_num = row[0] if row else None

                if next_num is None or next_num > 999:
                    con.rollback()
                else:
                    con.commit()
                    id_val = f"DC_{today}_{next_num:03d}"
                    metrics['generated'].append(id_val)

            except Exception as e:
                try:
                    con.rollback()
                except:
                    pass
                metrics['errors'] += 1

        con.close()
    except Exception as e:
        metrics['errors'] += 1

    metrics['end_time'] = time.time()
    metrics['duration_ms'] = (metrics['end_time'] - process_start) * 1000.0

    results_queue.put(metrics)

def run_stage_f(num_processes, num_ids, stage_name):
    """Run Stage F test"""
    print(f"\n[{stage_name}: {num_processes} processes × {num_ids} IDs]")

    # Reset counter
    con = sqlite3.connect(str(SANDBOX_DB_PATH), timeout=10.0)
    today = datetime.date.today().strftime("%Y%m%d")
    con.execute("DELETE FROM decision_id_counters WHERE date = ?", (today,))
    con.commit()
    con.close()

    # Start processes
    results_queue = mp.Queue()
    processes = []
    stage_start = time.time()

    for p_id in range(num_processes):
        p = mp.Process(
            target=worker_simple,
            args=(p_id, num_ids, results_queue)
        )
        p.start()
        processes.append(p)

    # Wait with timeout
    timeout_sec = 120.0
    for p in processes:
        p.join(timeout=timeout_sec)

    stage_elapsed = time.time() - stage_start

    # Collect results
    all_metrics = []
    while not results_queue.empty():
        metrics = results_queue.get()
        all_metrics.append(metrics)

    # Report
    total_ids = sum(len(m['generated']) for m in all_metrics)
    total_errors = sum(m['errors'] for m in all_metrics)

    print(f"  Wall-clock time: {stage_elapsed:.2f}s")
    print(f"  IDs generated: {total_ids}/{num_processes * num_ids}")
    print(f"  Errors: {total_errors}")
    print(f"  Processes completed: {len(all_metrics)}/{num_processes}")

    if all_metrics:
        throughput = total_ids / stage_elapsed
        print(f"  Throughput: {throughput:.1f} IDs/sec")

    # Save
    output_file = PHASE4_RESULTS_DIR / f"phase4_{stage_name.lower().replace(' ', '_')}_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_metrics, f, indent=2, default=str)

    return {
        'stage': stage_name,
        'procs': num_processes,
        'ids': num_ids,
        'total_ops': num_processes * num_ids,
        'time_ms': stage_elapsed * 1000,
        'generated': total_ids,
        'errors': total_errors,
        'throughput': total_ids / stage_elapsed if stage_elapsed > 0 else 0
    }

def main():
    print("=" * 80)
    print("TARGET-1 PHASE 4 STAGE F: EXTENDED ID COUNT (50 IDs per process)")
    print("=" * 80)

    results = []

    # Stage F-B: 2 processes × 50 IDs
    results.append(run_stage_f(2, 50, "STAGE F-B"))

    # Stage F-C: 5 processes × 50 IDs
    results.append(run_stage_f(5, 50, "STAGE F-C"))

    # Stage F-D: 10 processes × 50 IDs
    results.append(run_stage_f(10, 50, "STAGE F-D"))

    # Summary
    print("\n" + "=" * 80)
    print("STAGE F SUMMARY (50 IDs per process)")
    print("=" * 80)
    for r in results:
        print(f"\n{r['stage']}: {r['procs']} × {r['ids']} = {r['total_ops']} ops")
        print(f"  Time: {r['time_ms']:.0f}ms ({r['time_ms']/1000:.1f}s)")
        print(f"  Throughput: {r['throughput']:.1f} IDs/sec")
        print(f"  Generated/Errors: {r['generated']}/{r['errors']}")

    # Save summary
    summary_file = PHASE4_RESULTS_DIR / "phase4_stage_f_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

if __name__ == '__main__':
    import sys
    sys.exit(main())

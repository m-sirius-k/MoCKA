#!/usr/bin/env python3
"""
PHASE 4 STAGE B-E: PROGRESSIVE LOAD TESTING
2, 5, 10, 20 processes with instrumented timing
"""

import multiprocessing as mp
import sqlite3
import datetime
from pathlib import Path
import time
import json

SANDBOX_DB_PATH = Path(r"C:\Users\sirok\MoCKA\sandbox\mocka_events_sandbox.db")
PHASE4_RESULTS_DIR = Path(r"C:\Users\sirok\MoCKA\sandbox")

def worker_generate_ids_instrumented(process_id, num_ids, results_queue):
    """Instrumented worker (same as Stage A)"""
    process_start = time.time()
    metrics = {
        'process_id': process_id,
        'process_start_time': process_start,
        'connection_open_time': None,
        'generated': [],
        'operations': [],
        'errors': [],
        'lock_waits': [],
        'commit_times': [],
        'total_lock_wait_ms': 0.0,
        'total_commit_time_ms': 0.0,
        'process_end_time': None,
        'total_duration_ms': 0.0
    }

    try:
        conn_open_start = time.time()
        con = sqlite3.connect(str(SANDBOX_DB_PATH), timeout=30.0)
        metrics['connection_open_time'] = time.time() - conn_open_start

        today = datetime.date.today().strftime("%Y%m%d")

        for op_idx in range(num_ids):
            op_record = {
                'operation_index': op_idx,
                'timestamp_start': time.time(),
                'lock_wait_ms': None,
                'commit_time_ms': None,
                'generated_id': None,
                'error': None,
                'status': None
            }

            try:
                begin_start = time.time()
                con.execute("BEGIN IMMEDIATE")
                lock_wait_ms = (time.time() - begin_start) * 1000.0
                op_record['lock_wait_ms'] = lock_wait_ms
                metrics['lock_waits'].append(lock_wait_ms)
                metrics['total_lock_wait_ms'] += lock_wait_ms

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
                    op_record['status'] = 'limit_exceeded'
                else:
                    commit_start = time.time()
                    con.commit()
                    commit_time_ms = (time.time() - commit_start) * 1000.0
                    op_record['commit_time_ms'] = commit_time_ms
                    metrics['commit_times'].append(commit_time_ms)
                    metrics['total_commit_time_ms'] += commit_time_ms

                    id_val = f"DC_{today}_{next_num:03d}"
                    op_record['generated_id'] = id_val
                    metrics['generated'].append(id_val)
                    op_record['status'] = 'success'

            except sqlite3.OperationalError as e:
                if 'timeout' in str(e).lower() or 'locked' in str(e).lower():
                    op_record['status'] = 'connection_timeout'
                else:
                    op_record['status'] = 'operational_error'
                op_record['error'] = str(e)
                metrics['errors'].append(str(e))
                try:
                    con.rollback()
                except:
                    pass
            except Exception as e:
                op_record['status'] = 'unexpected_error'
                op_record['error'] = str(e)
                metrics['errors'].append(str(e))
                try:
                    con.rollback()
                except:
                    pass

            op_record['timestamp_end'] = time.time()
            op_record['duration_ms'] = (op_record['timestamp_end'] - op_record['timestamp_start']) * 1000.0
            metrics['operations'].append(op_record)

        con.close()

    except Exception as e:
        metrics['errors'].append({'type': 'process_fatal', 'msg': str(e)})

    finally:
        metrics['process_end_time'] = time.time()
        metrics['total_duration_ms'] = (metrics['process_end_time'] - process_start) * 1000.0

    results_queue.put(metrics)

def run_stage(num_processes, num_ids, stage_name):
    """Run test for given process count"""
    print(f"\n[{stage_name}: {num_processes} processes × {num_ids} IDs]")
    print("-" * 80)

    # Reset counter
    con = sqlite3.connect(str(SANDBOX_DB_PATH), timeout=10.0)
    today = datetime.date.today().strftime("%Y%m%d")
    con.execute("DELETE FROM decision_id_counters WHERE date = ?", (today,))
    con.commit()
    con.close()

    # Start all processes
    results_queue = mp.Queue()
    processes = []
    stage_start = time.time()

    for p_id in range(num_processes):
        p = mp.Process(
            target=worker_generate_ids_instrumented,
            args=(p_id, num_ids, results_queue)
        )
        p.start()
        processes.append(p)

    # Wait for completion with timeout
    timeout_sec = 120.0
    for p in processes:
        p.join(timeout=timeout_sec)

    stage_elapsed = time.time() - stage_start

    # Collect results
    all_metrics = []
    total_generated = 0
    total_errors = 0

    while not results_queue.empty():
        metrics = results_queue.get()
        all_metrics.append(metrics)
        total_generated += len(metrics['generated'])
        total_errors += len(metrics['errors'])

    # Analysis
    print(f"Total time: {stage_elapsed:.2f}s")
    print(f"IDs generated: {total_generated}")
    print(f"Processes completed: {len(all_metrics)}/{num_processes}")

    if all_metrics:
        all_lock_waits = []
        all_commit_times = []

        for metrics in all_metrics:
            print(f"  Process {metrics['process_id']}: {len(metrics['generated'])} IDs, "
                  f"lock_wait_avg={sum(metrics['lock_waits'])/len(metrics['lock_waits']):.2f}ms, "
                  f"commit_avg={sum(metrics['commit_times'])/len(metrics['commit_times']):.2f}ms")
            all_lock_waits.extend(metrics['lock_waits'])
            all_commit_times.extend(metrics['commit_times'])

        if all_lock_waits:
            print(f"\nLock wait times (ms):")
            print(f"  Min: {min(all_lock_waits):.3f}, Max: {max(all_lock_waits):.3f}, "
                  f"Avg: {sum(all_lock_waits)/len(all_lock_waits):.3f}")

        if all_commit_times:
            print(f"\nCOMMIT times (ms):")
            print(f"  Min: {min(all_commit_times):.3f}, Max: {max(all_commit_times):.3f}, "
                  f"Avg: {sum(all_commit_times)/len(all_commit_times):.3f}")

    # Save results
    output_file = PHASE4_RESULTS_DIR / f"phase4_{stage_name.lower().replace(' ', '_')}_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_metrics, f, indent=2, default=str)
    print(f"\nResults saved to: {output_file}")

    return {
        'stage': stage_name,
        'num_processes': num_processes,
        'num_ids': num_ids,
        'total_time_ms': stage_elapsed * 1000.0,
        'ids_generated': total_generated,
        'processes_completed': len(all_metrics),
        'errors': total_errors,
        'metrics': all_metrics
    }

def main():
    print("=" * 80)
    print("TARGET-1 PHASE 4 STAGES B-E: PROGRESSIVE LOAD ANALYSIS")
    print("=" * 80)

    results = []

    # Stage B: 2 processes
    results.append(run_stage(2, 10, "STAGE B"))

    # Stage C: 5 processes
    results.append(run_stage(5, 10, "STAGE C"))

    # Stage D: 10 processes
    results.append(run_stage(10, 10, "STAGE D"))

    # Stage E: 20 processes
    results.append(run_stage(20, 10, "STAGE E"))

    # Summary
    print("\n" + "=" * 80)
    print("PROGRESSIVE LOAD SUMMARY")
    print("=" * 80)

    for r in results:
        print(f"\n{r['stage']}: {r['num_processes']} processes × {r['num_ids']} IDs")
        print(f"  Total time: {r['total_time_ms']:.1f}ms")
        print(f"  IDs generated: {r['ids_generated']}")
        print(f"  Processes completed: {r['processes_completed']}/{r['num_processes']}")
        print(f"  Errors: {r['errors']}")

    # Save summary
    summary_file = PHASE4_RESULTS_DIR / "phase4_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n✓ Summary saved to: {summary_file}")

if __name__ == '__main__':
    import sys
    sys.exit(main())

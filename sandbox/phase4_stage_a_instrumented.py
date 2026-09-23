#!/usr/bin/env python3
"""
PHASE 4 STAGE A: ROOT-CAUSE INSTRUMENTED TEST
Single-process measurement baseline (1 process x 10 IDs initially for quick feedback)
"""

import multiprocessing as mp
import sqlite3
import datetime
from pathlib import Path
import time
from collections import defaultdict
import json
import os

SANDBOX_DB_PATH = Path(r"C:\Users\sirok\MoCKA\sandbox\mocka_events_sandbox.db")
PHASE4_RESULTS_PATH = Path(r"C:\Users\sirok\MoCKA\sandbox\phase4_stage_a_results.json")

class LimitExceededException(Exception):
    pass

def worker_generate_ids_instrumented(process_id, num_ids, results_queue):
    """
    Instrumented worker process with detailed timing metrics
    """
    process_start = time.time()
    metrics = {
        'process_id': process_id,
        'process_start_time': process_start,
        'connection_open_time': None,
        'connection_close_time': None,
        'generated': [],
        'operations': [],
        'errors': [],
        'lock_waits': [],
        'total_lock_wait_ms': 0.0,
        'process_end_time': None,
        'total_duration_ms': 0.0
    }

    try:
        # Measure connection open
        conn_open_start = time.time()
        con = sqlite3.connect(str(SANDBOX_DB_PATH), timeout=30.0)
        metrics['connection_open_time'] = time.time() - conn_open_start

        today = datetime.date.today().strftime("%Y%m%d")

        for op_idx in range(num_ids):
            op_record = {
                'operation_index': op_idx,
                'timestamp_start': time.time(),
                'timestamp_begin_immediate': None,
                'timestamp_after_insert': None,
                'timestamp_after_update': None,
                'timestamp_after_select': None,
                'timestamp_end': None,
                'lock_wait_ms': None,
                'generated_id': None,
                'error': None,
                'status': None
            }

            try:
                # Measure BEGIN IMMEDIATE timing
                begin_start = time.time()
                con.execute("BEGIN IMMEDIATE")
                begin_end = time.time()
                lock_wait_ms = (begin_end - begin_start) * 1000.0
                op_record['lock_wait_ms'] = lock_wait_ms
                op_record['timestamp_begin_immediate'] = begin_end
                metrics['lock_waits'].append(lock_wait_ms)
                metrics['total_lock_wait_ms'] += lock_wait_ms

                # INSERT
                con.execute(
                    "INSERT OR IGNORE INTO decision_id_counters (date, counter) VALUES (?, 0)",
                    (today,)
                )
                op_record['timestamp_after_insert'] = time.time()

                # UPDATE
                con.execute(
                    "UPDATE decision_id_counters SET counter = counter + 1 WHERE date = ?",
                    (today,)
                )
                op_record['timestamp_after_update'] = time.time()

                # SELECT
                row = con.execute(
                    "SELECT counter FROM decision_id_counters WHERE date = ?",
                    (today,)
                ).fetchone()
                op_record['timestamp_after_select'] = time.time()

                next_num = row[0] if row else None

                # Fail-closed check
                if next_num is None or next_num > 999:
                    con.rollback()
                    op_record['status'] = 'limit_exceeded'
                    op_record['error'] = f'Counter exceeds limit: {next_num}'
                else:
                    con.commit()
                    id_val = f"DC_{today}_{next_num:03d}"
                    op_record['generated_id'] = id_val
                    metrics['generated'].append(id_val)
                    op_record['status'] = 'success'

                op_record['timestamp_end'] = time.time()

            except sqlite3.OperationalError as e:
                if 'timeout' in str(e).lower() or 'locked' in str(e).lower():
                    op_record['status'] = 'connection_timeout'
                    op_record['error'] = f'Connection/lock timeout: {e}'
                    metrics['errors'].append({'type': 'connection_timeout', 'msg': str(e), 'op_idx': op_idx})
                else:
                    op_record['status'] = 'operational_error'
                    op_record['error'] = str(e)
                    metrics['errors'].append({'type': 'operational_error', 'msg': str(e), 'op_idx': op_idx})
                try:
                    con.rollback()
                except:
                    pass
                op_record['timestamp_end'] = time.time()

            except Exception as e:
                op_record['status'] = 'unexpected_error'
                op_record['error'] = str(e)
                metrics['errors'].append({'type': 'unexpected_error', 'msg': str(e), 'op_idx': op_idx})
                try:
                    con.rollback()
                except:
                    pass
                op_record['timestamp_end'] = time.time()

            # Compute operation duration
            if op_record['timestamp_start'] and op_record['timestamp_end']:
                op_record['duration_ms'] = (op_record['timestamp_end'] - op_record['timestamp_start']) * 1000.0

            metrics['operations'].append(op_record)

        # Measure connection close
        conn_close_start = time.time()
        con.close()
        metrics['connection_close_time'] = time.time() - conn_close_start

    except Exception as e:
        metrics['errors'].append({'type': 'process_fatal', 'msg': str(e)})

    finally:
        metrics['process_end_time'] = time.time()
        metrics['total_duration_ms'] = (metrics['process_end_time'] - process_start) * 1000.0

    # Queue results
    results_queue.put(metrics)

def test_stage_a_single_process(num_ids=10):
    """Run Stage A: Single process baseline"""
    print(f"\n[PHASE 4 STAGE A: SINGLE-PROCESS INSTRUMENTED TEST]")
    print(f"Configuration: 1 process × {num_ids} IDs")
    print("-" * 80)

    # Reset sandbox counter
    con = sqlite3.connect(str(SANDBOX_DB_PATH), timeout=10.0)
    today = datetime.date.today().strftime("%Y%m%d")
    con.execute("DELETE FROM decision_id_counters WHERE date = ?", (today,))
    con.commit()
    con.close()
    print(f"Sandbox counter reset for {today}")

    # Start process
    results_queue = mp.Queue()
    start_time = time.time()

    p = mp.Process(
        target=worker_generate_ids_instrumented,
        args=(0, num_ids, results_queue)
    )
    p.start()
    p.join(timeout=60.0)  # 60 second timeout for Stage A

    total_elapsed = time.time() - start_time

    # Collect results
    metrics = None
    if not results_queue.empty():
        metrics = results_queue.get()

    # Analysis
    print("\n[RESULTS]")
    if metrics:
        print(f"Process ID: {metrics['process_id']}")
        print(f"Total duration: {metrics['total_duration_ms']:.1f}ms")
        print(f"IDs generated: {len(metrics['generated'])}")
        print(f"Operations recorded: {len(metrics['operations'])}")
        print(f"Errors: {len(metrics['errors'])}")

        if metrics['lock_waits']:
            lock_waits = sorted(metrics['lock_waits'])
            print(f"\nLock wait times (ms):")
            print(f"  Min: {min(lock_waits):.3f}")
            print(f"  Max: {max(lock_waits):.3f}")
            print(f"  Avg: {sum(lock_waits) / len(lock_waits):.3f}")
            print(f"  P50: {lock_waits[len(lock_waits)//2]:.3f}")
            print(f"  Total: {sum(lock_waits):.1f}ms")

        if metrics['operations']:
            op_durations = [op.get('duration_ms', 0) for op in metrics['operations'] if op.get('duration_ms')]
            if op_durations:
                print(f"\nOperation durations (ms):")
                print(f"  Min: {min(op_durations):.3f}")
                print(f"  Max: {max(op_durations):.3f}")
                print(f"  Avg: {sum(op_durations) / len(op_durations):.3f}")

        # Save to file
        with open(PHASE4_RESULTS_PATH, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
        print(f"\nDetailed metrics saved to: {PHASE4_RESULTS_PATH}")

        return metrics
    else:
        print(f"ERROR: Process timed out or no results captured")
        print(f"Process alive: {p.is_alive()}")
        if p.is_alive():
            p.terminate()
            p.join(timeout=5.0)
        return None

def main():
    print("=" * 80)
    print("TARGET-1 PHASE 4 STAGE A: ROOT-CAUSE INSTRUMENTATION")
    print("=" * 80)

    # Test with small number first (10 IDs)
    metrics = test_stage_a_single_process(num_ids=10)

    if metrics:
        print("\n[STAGE A COMPLETE]")
        print(f"✓ Single-process test completed successfully")
        print(f"✓ Baseline metrics collected")
        print(f"✓ Ready to progress to Stage B (2 processes)")
    else:
        print("\n[STAGE A FAILED]")
        print(f"✗ Single-process test failed or timed out")
        print(f"✗ Cannot proceed without baseline")
        return 1

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())

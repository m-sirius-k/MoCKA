#!/usr/bin/env python3
import json

with open('phase4_stage_d_results.json') as f:
    processes = json.load(f)

print(f"Stage D: {len(processes)} processes\n")

total_ids = 0
total_ops = 0
total_errors = 0
all_commits = []
all_locks = []

for proc in processes:
    ids = len(proc['generated'])
    errors = len(proc['errors'])
    ops = len(proc.get('operations', []))
    commits = proc.get('commit_times', [])
    locks = proc.get('lock_waits', [])

    total_ids += ids
    total_ops += ops
    total_errors += errors
    all_commits.extend(commits)
    all_locks.extend(locks)

    print(f"Proc {proc['process_id']}: {ids} IDs, {ops} ops, {len(commits)} commits")
    if commits:
        print(f"  Commits: min={min(commits):.1f}ms, max={max(commits):.1f}ms, avg={sum(commits)/len(commits):.1f}ms")
    if locks:
        print(f"  Locks: min={min(locks):.3f}ms, max={max(locks):.3f}ms, avg={sum(locks)/len(locks):.3f}ms")

print(f"\nTotal: {total_ids} IDs, {total_ops} ops, {total_errors} errors")
if all_commits:
    print(f"All commits: min={min(all_commits):.1f}ms, max={max(all_commits):.1f}ms, avg={sum(all_commits)/len(all_commits):.1f}ms")
if all_locks:
    print(f"All locks: min={min(all_locks):.3f}ms, max={max(all_locks):.3f}ms, avg={sum(all_locks)/len(all_locks):.3f}ms")

# Calculate wall-clock time
if processes:
    min_start = min(p['process_start_time'] for p in processes)
    max_end = max(p['process_end_time'] for p in processes)
    elapsed = max_end - min_start
    print(f"\nWall-clock time: {elapsed*1000:.0f}ms ({elapsed:.1f}s)")
    if elapsed > 0:
        print(f"Throughput: {total_ids/elapsed:.1f} IDs/sec")

#!/usr/bin/env python3
import json

for stage in ['a', 'b', 'c']:
    fname = f'phase4_stage_{stage}_results.json'
    try:
        with open(fname) as f:
            data = json.load(f)
    except:
        continue

    if isinstance(data, list):
        processes = data
    else:
        processes = [data]

    print(f'\nStage {stage.upper()}: {len(processes)} processes')

    total_ids = 0
    total_errors = 0
    total_ops = 0
    all_commits = []

    for proc in processes:
        ids = len(proc.get('generated', []))
        errors = len(proc.get('errors', []))
        commits = proc.get('commit_times', [])
        ops = len(proc.get('operations', []))

        total_ids += ids
        total_errors += errors
        total_ops += ops
        all_commits.extend(commits)

        print(f'  Proc {proc["process_id"]}: {ids} IDs, {ops} ops, {errors} errors')

    print(f'  Total: {total_ids} IDs, {total_ops} ops, {total_errors} errors')
    if all_commits:
        print(f'  Commit times: min={min(all_commits):.1f}ms, max={max(all_commits):.1f}ms, avg={sum(all_commits)/len(all_commits):.1f}ms')

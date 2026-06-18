"""
sync_watch.py
export_for_cloudflare を起動時に即実行し、その後 SYNC_INTERVAL 秒ごとに繰り返す常駐デーモン。
MoCKA-START.bat の PHASE 1 background job として起動する。

効果: 正本 -> data/ スナップショット -> git push までの遅延を最大 SYNC_INTERVAL 秒に抑える。
"""
import sys, time, subprocess, json
from datetime import datetime, timezone
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

MOCKA_ROOT    = Path(r'C:\Users\sirok\MoCKA')
EXPORT_SCRIPT = MOCKA_ROOT / 'PlanningCaliber' / 'workshop' / 'mocka-cloudflare' / 'export_for_cloudflare.py'
SYNC_INTERVAL = 600  # 10分
GIT_TARGETS   = [
    'data/MOCKA_OVERVIEW.json',
    'data/MOCKA_TODO.json',
    'data/lever_essence.json',
    'data/events_latest.json',
]


def run_export():
    result = subprocess.run(
        [sys.executable, str(EXPORT_SCRIPT)],
        cwd=str(MOCKA_ROOT),
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if result.stdout:
        print(result.stdout, end='')
    if result.stderr:
        print('[export stderr]', result.stderr, end='')


def git_push_if_changed():
    subprocess.run(
        ['git', 'add'] + GIT_TARGETS,
        cwd=str(MOCKA_ROOT), capture_output=True
    )
    diff = subprocess.run(
        ['git', 'diff', '--cached', '--quiet'],
        cwd=str(MOCKA_ROOT)
    )
    if diff.returncode == 0:
        print('[sync_watch] no changes, skip push')
        return
    now_str = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    subprocess.run(
        ['git', 'commit', '-m', f'auto sync {now_str}'],
        cwd=str(MOCKA_ROOT), capture_output=True
    )
    push = subprocess.run(
        ['git', 'push', 'origin', 'main'],
        cwd=str(MOCKA_ROOT), capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if push.returncode == 0:
        print(f'[sync_watch] pushed at {now_str}')
    else:
        print(f'[sync_watch] push failed: {push.stderr.strip()}')


def sync_once():
    ts = datetime.now().strftime('%H:%M:%S')
    print(f'[sync_watch] {ts} syncing...')
    try:
        run_export()
        git_push_if_changed()
    except Exception as e:
        print(f'[sync_watch] error: {e}')


if __name__ == '__main__':
    print(f'[sync_watch] started (interval={SYNC_INTERVAL}s)')
    while True:
        sync_once()
        time.sleep(SYNC_INTERVAL)

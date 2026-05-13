import sys

path = r"C:\Users\sirok\MoCKA\app.py"
src = open(path, encoding='utf-8').read()

# _seal_runningフラグ追加
if '_seal_running' not in src:
    src = src.replace(
        '_last_event_count = [0]',
        '_last_event_count = [0]\n_seal_running = [False]'
    )

# if True: → 多重起動防止条件に
src = src.replace(
    '            if True:\n                if count - _last_event_count[0] >= 50:',
    '            if count - _last_event_count[0] >= 50 and not _seal_running[0]:\n                if True:'
)

# timeout=30 → 60に
src = src.replace(
    '"AUTO_SEAL_50EVT"],\n                                   cwd=str(ROOT_DIR), timeout=30)',
    '"AUTO_SEAL_50EVT"],\n                                   cwd=str(ROOT_DIR), timeout=60)'
)

open(path, 'w', encoding='utf-8').write(src)
print("完了")

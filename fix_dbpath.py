f = open(r'C:\Users\sirok\MoCKA\interface\guidelines_engine.py', encoding='utf-8')
txt = f.read()
f.close()

old = r'MOCKA_ROOT / "mocka_events.db"'
new = r'MOCKA_ROOT / "data" / "events.db"'

if old in txt:
    txt = txt.replace(old, new)
    f = open(r'C:\Users\sirok\MoCKA\interface\guidelines_engine.py', 'w', encoding='utf-8')
    f.write(txt)
    f.close()
    print('OK: DB_PATH修正完了')
else:
    # 現在のDB_PATH行を確認
    for i, line in enumerate(txt.splitlines()):
        if 'DB_PATH' in line:
            print(f'line {i}: {line}')

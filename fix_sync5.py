from pathlib import Path

TARGET = Path('C:/Users/sirok/MoCKA/interface/mocka_firestore_sync.py')
content = TARGET.read_text(encoding='utf-8')

OLD = 'import json, io, os, sys'
NEW = 'import json, io, os, sys, time, urllib.request, urllib.error'

if 'urllib' not in content:
    content = content.replace(OLD, NEW, 1)
    TARGET.write_text(content, encoding='utf-8')
    print('OK: time + urllib added')
else:
    # 既存importを確認
    for i, line in enumerate(content.splitlines()[:15]):
        print(f'{i}: {line}')
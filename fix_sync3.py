from pathlib import Path

TARGET = Path('C:/Users/sirok/MoCKA/interface/mocka_firestore_sync.py')
content = TARGET.read_text(encoding='utf-8')

OLD = 'import json, io, os, sys'
NEW = 'import json, io, os, sys, time, re'

if 'time' not in content:
    content = content.replace(OLD, NEW, 1)
    TARGET.write_text(content, encoding='utf-8')
    print('OK: time, re added')
else:
    print('- already ok')
    print('imports:', content.splitlines()[0])
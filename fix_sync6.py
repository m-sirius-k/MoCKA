from pathlib import Path

TARGET = Path('C:/Users/sirok/MoCKA/interface/mocka_firestore_sync.py')
content = TARGET.read_text(encoding='utf-8')

OLD = 'import json, io, os, sys'
NEW = 'import json, io, os, sys, time, urllib.request, urllib.error'

content = content.replace(OLD, NEW, 1)
TARGET.write_text(content, encoding='utf-8')

# 確認
lines = TARGET.read_text(encoding='utf-8').splitlines()
print(lines[9])
print('OK')
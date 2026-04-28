from pathlib import Path

TARGET = Path('C:/Users/sirok/MoCKA/interface/mocka_firestore_sync.py')
lines = TARGET.read_text(encoding='utf-8').splitlines()

fixed = []
for line in lines:
    if 'sys.stderr = io.TextIOWrapper' in line and ', os, sys, time,' in line:
        fixed.append('sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")')
        print('OK: broken stderr line fixed')
    else:
        fixed.append(line)

TARGET.write_text('\n'.join(fixed), encoding='utf-8')
print('done')
from pathlib import Path
import re

TARGET = Path('C:/Users/sirok/MoCKA/interface/mocka_firestore_sync.py')
content = TARGET.read_text(encoding='utf-8')

# 絵文字をASCII代替に置換
content = content.replace('ok=True', 'ok=True')
# subprocess経由で呼ぶのでstdout encodingを強制
OLD = 'import json'
NEW = 'import json, io, sys\nsys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=\"utf-8\", errors=\"replace\")\nsys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding=\"utf-8\", errors=\"replace\")'

if 'TextIOWrapper' not in content:
    content = content.replace(OLD, NEW, 1)
    TARGET.write_text(content, encoding='utf-8')
    print('OK: encoding fix applied')
else:
    print('- already fixed')
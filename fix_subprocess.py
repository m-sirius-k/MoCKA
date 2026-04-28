from pathlib import Path

APP = Path('C:/Users/sirok/MoCKA/app.py')
content = APP.read_text(encoding='utf-8')

# subprocess.Popen呼び出しにencoding/env設定を追加
import re

# stdout/stderrなしのPopenにUTF-8環境変数を追加
OLD = 'subprocess.Popen([sys.executable, "tools/mocka_orchestra_v10.py", text, "collaborate"], cwd=ROOT_DIR)'
NEW = 'subprocess.Popen([sys.executable, "tools/mocka_orchestra_v10.py", text, "collaborate"], cwd=ROOT_DIR, env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})'

if OLD in content:
    content = content.replace(OLD, NEW)
    print("OK: orchestra collaborate fixed")

# 全Popen呼び出しにPYTHONIOENCODING追加（一括）
count = 0
lines = content.splitlines()
for i, line in enumerate(lines):
    if 'subprocess.Popen(' in line and 'PYTHONIOENCODING' not in line and 'cwd=ROOT_DIR)' in line:
        lines[i] = line.replace('cwd=ROOT_DIR)', 'cwd=ROOT_DIR, env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})')
        count += 1

content = '\n'.join(lines)
APP.write_text(content, encoding='utf-8')
print(f'OK: {count} Popen calls fixed with PYTHONIOENCODING=utf-8')
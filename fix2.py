import re
from pathlib import Path

APP = Path('C:/Users/sirok/MoCKA/app.py')
content = APP.read_text(encoding='utf-8')

MARKER = 'if __name__ == "__main__":'
block_pattern = r'(\n# .. cross_audit .*?# .+\n)'

match = re.search(block_pattern, content, re.DOTALL)
if not match:
    print('NG: block not found')
    # デバッグ: cross_auditの位置確認
    idx = content.find('cross_audit')
    print(f'cross_audit at index: {idx}')
    print(content[max(0,idx-50):idx+100])
    exit(1)

block = match.group(0)
content_clean = content.replace(block, chr(10))
marker_idx = content_clean.find(MARKER)
if marker_idx == -1:
    print('NG: __main__ not found')
    exit(1)

content_new = content_clean[:marker_idx] + block + chr(10) + content_clean[marker_idx:]
APP.write_text(content_new, encoding='utf-8')
print('OK: cross_audit moved before __main__')
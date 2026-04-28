from pathlib import Path

APP = Path("C:/Users/sirok/MoCKA/app.py")
content = APP.read_text(encoding="utf-8")

MARKER = "if __name__ == '__main__':"

# cross_auditブロックを抽出して削除
import re
block_pattern = r'\n# ── cross_audit.*?# ─+\n'
match = re.search(block_pattern, content, re.DOTALL)
if not match:
    print("NG: cross_audit block not found")
    exit(1)

block = match.group(0)
content_clean = content.replace(block, "\n")

# MARKERの直前に挿入
if MARKER not in content_clean:
    print("NG: __main__ marker not found")
    exit(1)

content_new = content_clean.replace(MARKER, block + "\n" + MARKER, 1)
APP.write_text(content_new, encoding="utf-8")
print("OK: cross_audit moved before __main__")
"""
fix_line37.py
guidelines_engine.py の壊れた37-38行目を修正
"""
from pathlib import Path

TARGET = Path(r"C:\Users\sirok\MoCKA\interface\guidelines_engine.py")

lines = TARGET.read_text(encoding="utf-8").splitlines()

fixed = []
skip_next = False
for i, line in enumerate(lines):
    if skip_next:
        skip_next = False
        continue
    # 37行目相当: r"^PS C:\\ で終わっている壊れた行
    if line.rstrip() == '    r"^PS C:\\\\':
        # 次行が '",' なら結合して正しい形に
        if i + 1 < len(lines) and lines[i+1].strip() in ('",', '",'):
            fixed.append('    r"^PS C:\\\\\\\\",')
            skip_next = True
        else:
            fixed.append('    r"^PS C:\\\\\\\\",')
    else:
        fixed.append(line)

result = "\n".join(fixed) + "\n"
TARGET.write_text(result, encoding="utf-8")

# 確認
verify = TARGET.read_text(encoding="utf-8").splitlines()
for i, l in enumerate(verify[34:42], 35):
    print(i, repr(l))
print("\n[OK] 修正完了")

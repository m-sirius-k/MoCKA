"""
patch_guidelines_noise.py
guidelines_engine.py にノイズパターンを追加するパッチ
実行: python patch_guidelines_noise.py
"""
from pathlib import Path

TARGET = Path(r"C:\Users\sirok\MoCKA\interface\guidelines_engine.py")

# 追加するノイズパターン（既存リストの先頭に挿入）
ADD_PATTERNS = [
    r'    r"^Mode\s+LastWriteTime",',
    r'    r"^FullName\s*$",',
    r'    r"^FullName\s*[-]+",',
    r'    r"^LineNumber",',
    r'    r"^Line\s+[-]+",',
    r'    r"^[-]+\s*$",',
    r'    r"^wt\s+-w\s+",',
    r'    r"^@app\.route",',
    r'    r"^async function",',
    r'    r"^const\s+\w+",',
    r'    r"_json\.dump\(",',
    r'    r"http://\w+\.py",',
    r'    r"^\s*OK:\s+\w+",',
    r'    r"^\s*NG:\s+",',
    r'    r"^done$",',
    r'    r"^DONE$",',
    r'    r"^FOUND:",',
    r'    r"^REPLACED:",',
    r'    r"^\s*\d+\s+\w+\s+\w+\s*$",',
]

txt = TARGET.read_text(encoding="utf-8")

# 挿入位置: NOISE_PATTERNS リストの最初の要素の前
ANCHOR = '    r"^PS C:\\\\'
if ANCHOR not in txt:
    # フォールバック
    ANCHOR = 'NOISE_PATTERNS = ['
    INSERT_AFTER = True
else:
    INSERT_AFTER = False

if INSERT_AFTER:
    insert_block = "\n".join(ADD_PATTERNS) + "\n"
    txt2 = txt.replace(ANCHOR, ANCHOR + "\n" + insert_block)
else:
    insert_block = "\n".join(ADD_PATTERNS) + "\n"
    txt2 = txt.replace(ANCHOR, insert_block + "    " + ANCHOR.strip() + "\n")

if txt2 == txt:
    print("[NG] 挿入位置が見つかりませんでした")
    print("先頭100文字:", txt[:200])
else:
    TARGET.write_text(txt2, encoding="utf-8")
    # 確認
    check = TARGET.read_text(encoding="utf-8")
    count = check.count("LineNumber")
    print(f"[OK] ノイズパターン追加完了 (LineNumber出現: {count}回)")
    print(f"     総ノイズパターン数確認中...")
    noise_count = check.count('    r"')
    print(f"     ノイズパターン推定: {noise_count}件")

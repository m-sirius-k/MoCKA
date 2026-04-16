"""
fix_encoding.py
Copilot収集JSONの文字化け（CP932化け）を修正する
"""
import json
from pathlib import Path

SRC  = Path(r"C:\Users\sirok\MoCKA\data\storage\infield\RAW\20260406_001445_ECOL_20260406_001445_COPI.json")
DEST = Path(r"C:\Users\sirok\MoCKA\data\storage\infield\RAW\COPI_fixed.json")

# 生バイトをcp932として読み直す
raw_bytes = SRC.read_bytes()

# まずUTF-8で読んでみる（正常なら終わり）
try:
    data = json.loads(raw_bytes.decode("utf-8"))
    text = data.get("text", "")
    # textフィールドがcp932化けしている場合
    try:
        fixed_text = text.encode("cp932", errors="replace").decode("utf-8", errors="replace")
    except Exception:
        fixed_text = text
    # latin-1経由で再デコード（Mojibake修正の定番）
    try:
        fixed_text2 = text.encode("latin-1").decode("cp932")
    except Exception:
        fixed_text2 = None

    print("=== UTF-8デコード成功 ===")
    print(f"text先頭（生）    : {text[:100]}")
    print(f"text先頭（latin1→cp932）: {fixed_text2[:100] if fixed_text2 else 'NG'}")

    if fixed_text2:
        data["text"] = fixed_text2
        data["encoding_fixed"] = True
        DEST.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n✓ 修正済み保存 → {DEST}")
    else:
        print("修正失敗 — 手動確認が必要")

except Exception as e:
    print(f"UTF-8デコード失敗: {e}")
    # CP932として読み直し
    try:
        data = json.loads(raw_bytes.decode("cp932"))
        DEST.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✓ CP932として読み直し成功 → {DEST}")
    except Exception as e2:
        print(f"CP932も失敗: {e2}")

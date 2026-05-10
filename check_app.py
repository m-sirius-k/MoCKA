from pathlib import Path

app_py = Path(r"C:\Users\sirok\MoCKA\app.py")
txt = app_py.read_text(encoding="utf-8")

# 末尾200行を確認
lines = txt.splitlines()
print(f"総行数: {len(lines)}")
print("--- 末尾20行 ---")
for i, l in enumerate(lines[-20:], len(lines)-19):
    print(f"{i:4d}: {l[:80]}")

# if __name__ の位置確認
for i, l in enumerate(lines):
    if "if __name__" in l:
        print(f"\nif __name__ 行: {i+1}")
        break

# guidelines既存チェック
print("\n既存guidelines:", "guidelines" in txt)
# essence_auto_updater確認
print("essence_auto_updater:", "essence_auto_updater" in txt or "auto_updater" in txt)

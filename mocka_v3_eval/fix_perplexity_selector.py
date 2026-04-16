from pathlib import Path

f = Path(r"C:\Users\sirok\MoCKA\tools\mocka-extension\background.js")
c = f.read_text(encoding="utf-8")

old = "perplexity: 'p',"
new = "perplexity: '.prose, [class*=\"answer\"], .break-words',"

if old in c:
    c = c.replace(old, new)
    f.write_text(c, encoding="utf-8")
    print(f"✓ 修正完了: {old} → {new}")
else:
    print("対象文字列が見つかりません")
    print("現在のperplexity行:")
    for line in c.splitlines():
        if "perplexity" in line and "SEL" not in line and "domain" not in line:
            print(f"  {line.strip()}")

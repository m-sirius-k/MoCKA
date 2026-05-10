f = open(r'C:\Users\sirok\MoCKA\interface\guidelines_engine.py', encoding='utf-8')
txt = f.read()
f.close()

start = txt.find('def is_noise(t):')
end = txt.find('\ndef ', start + 1)

new_is_noise = '''def is_noise(t):
    if not t or len(t.strip()) < 4: return True
    if any(p.search(t) for p in NOISE_RE): return True
    # 制御文字（Shift-JIS残骸）
    if sum(1 for c in t if ord(c) < 0x20 and c not in (chr(9), chr(10), chr(13))) >= 1:
        return True
    # 半角カタカナ (U+FF61-FF9F) が混入 = 文字化け確定
    hankaku_kata = sum(1 for c in t if 0xFF61 <= ord(c) <= 0xFF9F)
    if hankaku_kata >= 2: return True
    return False'''

txt = txt[:start] + new_is_noise + txt[end:]
f = open(r'C:\Users\sirok\MoCKA\interface\guidelines_engine.py', 'w', encoding='utf-8')
f.write(txt)
f.close()

# テスト
import importlib.util
spec = importlib.util.spec_from_file_location("ge", r'C:\Users\sirok\MoCKA\interface\guidelines_engine.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

tests = [
    ("[save] \u8708\uff71\u8b5b\u30fb ChatGPT", True),      # 蜈ｱ譛・ChatGPT
    ("[save] router.py\u95d5\uff73\u96cd\u5177\uff7d", True), # 闕ｳ雍具ｽ
    ("[collaboration] \u7e3a\uff61\u7e67\u30fb\u25b2\u7e3a", True), # 縺｡繧・▲縺
    ("MoCKAはどう思いますか？設計を改善しよう", False),
    ("recurrence_registry再発77件修正済み", False),
    ("なぜこのエラーが起きるのか？原因を調べて", False),
    ("MoCKA COMMAND CENTER v5.0稼働確認", False),
]

print("=== フィルタテスト ===")
all_ok = True
for text, expected in tests:
    result = mod.is_noise(text)
    ok = result == expected
    if not ok: all_ok = False
    print(f"  {'OK' if ok else 'NG'} is_noise({text[:35]!r}) = {result} (期待:{expected})")

print()
print("全テストOK ✓" if all_ok else "NGあり — 要確認")

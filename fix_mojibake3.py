f = open(r'C:\Users\sirok\MoCKA\interface\guidelines_engine.py', encoding='utf-8')
txt = f.read()
f.close()

start = txt.find('def is_noise(t):')
end = txt.find('\ndef ', start + 1)

new_is_noise = '''def is_noise(t):
    if not t or len(t.strip()) < 4: return True
    if any(p.search(t) for p in NOISE_RE): return True
    # 制御文字混入 = Shift-JIS文字化け残骸
    ctrl_count = sum(1 for c in t if ord(c) < 0x20 and c not in (chr(9), chr(10), chr(13)))
    if ctrl_count >= 1: return True
    # 非ASCII文字が多すぎる（日本語正常文字U+3000-U+9FFFは除外）
    weird = sum(1 for c in t if 0x80 <= ord(c) <= 0x9F)
    if weird >= 1: return True
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
    ("[save] Phase5\x80\x9f文字化け", True),
    ("MoCKAはどう思いますか？設計を改善しよう", False),
    ("recurrence_registry隠れた再発77件", False),
    ("なぜこのエラーが起きるのか？", False),
]
print("=== フィルタテスト ===")
all_ok = True
for text, expected in tests:
    result = mod.is_noise(text)
    ok = result == expected
    if not ok: all_ok = False
    print(f"  {'OK' if ok else 'NG'} is_noise({text[:30]!r}) = {result} (期待:{expected})")

print()
print("全テストOK" if all_ok else "NG あり — 要確認")

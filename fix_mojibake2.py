f = open(r'C:\Users\sirok\MoCKA\interface\guidelines_engine.py', encoding='utf-8')
txt = f.read()
f.close()

# 現在のis_noise関数を確認
start = txt.find('def is_noise(t):')
end = txt.find('\ndef ', start + 1)
print('現在のis_noise:')
print(txt[start:end])
print('---')

# Unicode範囲で文字化け検出する新関数（ASCII安全な書き方）
new_is_noise = '''def is_noise(t):
    if not t or len(t.strip()) < 4: return True
    if any(p.search(t) for p in NOISE_RE): return True
    # 文字化け検出: Shift-JIS残骸はU+7E40付近の文字が密集する
    # 繝(U+7E1D) 繧(U+7E27) 縺(U+7E3A) 髮(U+9AB6) 蜷(U+8737)
    suspicious = sum(1 for c in t if 0x7E00 <= ord(c) <= 0x7FFF or
                                     0x9A00 <= ord(c) <= 0x9AFF or
                                     0x8700 <= ord(c) <= 0x87FF)
    if suspicious >= 3: return True
    return False'''

# 置換
if 'def is_noise(t):' in txt:
    txt = txt[:start] + new_is_noise + txt[end:]
    f = open(r'C:\Users\sirok\MoCKA\interface\guidelines_engine.py', 'w', encoding='utf-8')
    f.write(txt)
    f.close()
    print('OK: is_noise関数を完全置換')
else:
    print('ERROR: is_noise関数が見つかりません')

# テスト
mojibake = '[share] MoCKA \u96b2\u5306\u8b1a\u4ed9\u30fb TODO \u83f4\u61b8\u30fb: 2026-04-04'
clean = 'MoCKAはどう思いますか？設計を改善しよう'

import re, importlib.util, sys
spec = importlib.util.spec_from_file_location("ge", r'C:\Users\sirok\MoCKA\interface\guidelines_engine.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print(f'文字化けテスト: is_noise("{mojibake[:30]}") = {mod.is_noise(mojibake)}')
print(f'正常テスト:     is_noise("{clean}") = {mod.is_noise(clean)}')

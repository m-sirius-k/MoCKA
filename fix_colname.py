f = open(r'C:\Users\sirok\MoCKA\interface\guidelines_engine.py', encoding='utf-8')
txt = f.read()
f.close()

# カラム名修正
fixes = [
    ('when_ts', 'when'),
]

for old, new in fixes:
    # SELECT文内のwhen_tsのみ修正（変数名のwhen_tsは残す）
    txt = txt.replace('"when_ts"', '"when"')
    txt = txt.replace("'when_ts'", "'when'")
    txt = txt.replace('when_ts,', 'when,')
    txt = txt.replace('when_ts DESC', 'when DESC')
    txt = txt.replace("ev.get(\"when_ts\"", "ev.get(\"when\"")
    txt = txt.replace("event.get(\"when_ts\"", "event.get(\"when\"")

f = open(r'C:\Users\sirok\MoCKA\interface\guidelines_engine.py', 'w', encoding='utf-8')
f.write(txt)
f.close()
print('OK: カラム名修正完了 (when_ts → when)')

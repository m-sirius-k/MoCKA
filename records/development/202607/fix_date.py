f = open('interface/mocka_notion_sync.py', encoding='utf-8')
c = f.read()
f.close()

# 日付パース関数を追加して、複数フォーマットに対応
old = 'def txt(v, n=2000):\n    return [{"text":{"content":str(v or "")[:n]}}]'

new = '''def txt(v, n=2000):
    return [{"text":{"content":str(v or "")[:n]}}]

def parse_date(v):
    """when_ts から ISO 8601 日付 (YYYY-MM-DD) を安全に抽出"""
    s = str(v or "").strip()
    if not s:
        return None
    # YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS
    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        return s[:10]
    # 20260429_112308 形式
    if len(s) >= 8 and s[:8].isdigit():
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
    return None'''

c = c.replace(old, new)

# 日付セット箇所を parse_date に変更
c = c.replace(
    '    dt = str(d.get("when_ts","") or "")[:10]\n    if len(dt)==10: props["Approved Date"]={"date":{"start":dt}}',
    '    dt = parse_date(d.get("when_ts",""))\n    if dt: props["Approved Date"]={"date":{"start":dt}}'
)
c = c.replace(
    '    dt = str(e.get("when_ts","") or "")[:10]\n    if len(dt)==10: props["Date"]={"date":{"start":dt}}',
    '    dt = parse_date(e.get("when_ts",""))\n    if dt: props["Date"]={"date":{"start":dt}}'
)
c = c.replace(
    '    dt = str(i.get("when_ts","") or "")[:10]\n    if len(dt)==10: props["Occurred Date"]={"date":{"start":dt}}',
    '    dt = parse_date(i.get("when_ts",""))\n    if dt: props["Occurred Date"]={"date":{"start":dt}}'
)

f = open('interface/mocka_notion_sync.py', 'w', encoding='utf-8')
f.write(c)
f.close()
print('done')

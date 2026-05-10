f = open(r'C:\Users\sirok\MoCKA\interface\guidelines_engine.py', encoding='utf-8')
txt = f.read()
f.close()

old = '    if path.exists(): return json.loads(path.read_text(encoding="utf-8"))\n    return {"meta":{"version":"1.1","philosophy":"失敗は資産になる",\n                    "created":datetime.now(timezone.utc).isoformat()},\n            "guidelines":[],"summary":{"total":0,"by_category":{},"last_updated":""}}'

new = '''    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if "summary" not in data:
            data["summary"] = {"total":0,"by_category":{},"last_updated":""}
        return data
    return {"meta":{"version":"1.1","philosophy":"失敗は資産になる",
                    "created":datetime.now(timezone.utc).isoformat()},
            "guidelines":[],"summary":{"total":0,"by_category":{},"last_updated":""}}'''

if old in txt:
    txt = txt.replace(old, new)
    print('OK: 完全一致修正')
else:
    # 部分修正
    txt = txt.replace(
        'def save_guidelines(path, data):\n    path.parent.mkdir(parents=True, exist_ok=True)\n    cats = {}',
        'def save_guidelines(path, data):\n    path.parent.mkdir(parents=True, exist_ok=True)\n    if "summary" not in data:\n        data["summary"] = {"total":0,"by_category":{},"last_updated":""}\n    cats = {}'
    )
    print('OK: 部分修正')

f = open(r'C:\Users\sirok\MoCKA\interface\guidelines_engine.py', 'w', encoding='utf-8')
f.write(txt)
f.close()
print('書き込み完了')

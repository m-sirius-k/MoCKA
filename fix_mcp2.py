src = open('C:/Users/sirok/MoCKA/mocka_mcp_server.py', encoding='utf-8').read()
old = '            row["title"]          = args.get("title", "")\n            row["short_summary"]'
new = '            row["why_purpose"]    = args.get("why_purpose", "")\n            row["how_trigger"]    = args.get("how_trigger", "")\n            row["title"]          = args.get("title", "")\n            row["short_summary"]'
if old in src:
    open('C:/Users/sirok/MoCKA/mocka_mcp_server.py', 'w', encoding='utf-8').write(src.replace(old, new))
    print('SUCCESS: why_purpose/how_trigger マッピング追加完了')
else:
    print('NOT FOUND')

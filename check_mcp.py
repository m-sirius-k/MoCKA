src = open('C:/Users/sirok/MoCKA/mocka_mcp_server.py', encoding='utf-8').read()
old = 'row["who_actor"]      = args.get("author",'
# 前後の文脈を確認
idx = src.find(old)
print(repr(src[idx:idx+300]))

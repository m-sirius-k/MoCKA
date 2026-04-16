src = open('C:/Users/sirok/MoCKA/mocka_mcp_server.py', encoding='utf-8').read()
old = '"name":"mocka_write_event","description":"イベント追記","inputSchema":{"type":"object","properties":{"title":{"type":"string"},"description":{"type":"string"},"tags":{"type":"string"},"author":{"type":"string","default":"Claude"}},"required":["title","description"]}'
new = '"name":"mocka_write_event","description":"イベント追記","inputSchema":{"type":"object","properties":{"title":{"type":"string"},"description":{"type":"string"},"tags":{"type":"string"},"author":{"type":"string","default":"Claude"},"why_purpose":{"type":"string"},"how_trigger":{"type":"string"}},"required":["title","description"]}'
if old in src:
    open('C:/Users/sirok/MoCKA/mocka_mcp_server.py', 'w', encoding='utf-8').write(src.replace(old, new))
    print('SUCCESS')
else:
    print('NOT FOUND')
    print(repr(src[src.find('mocka_write_event'):src.find('mocka_write_event')+200]))

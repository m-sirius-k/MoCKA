f = open(r'C:\Users\sirok\MoCKA\interface\guidelines_engine.py', encoding='utf-8')
txt = f.read()
f.close()

# SELECT文の when を [when] にエスケープ
txt = txt.replace(
    'SELECT event_id, when, who_actor, what_type,',
    'SELECT event_id, [when], who_actor, what_type,'
)
txt = txt.replace(
    'ORDER BY when DESC',
    'ORDER BY [when] DESC'
)
# ev.get("when") はそのままでOK（Python側）

f = open(r'C:\Users\sirok\MoCKA\interface\guidelines_engine.py', 'w', encoding='utf-8')
f.write(txt)
f.close()
print('OK: when予約語エスケープ完了')

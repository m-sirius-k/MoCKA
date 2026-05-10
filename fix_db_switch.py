f = open(r'C:\Users\sirok\MoCKA\interface\guidelines_engine.py', encoding='utf-8')
txt = f.read()
f.close()

# 1. DBパス変更
txt = txt.replace(
    'MOCKA_ROOT / "data" / "events.db"',
    'MOCKA_ROOT / "data" / "mocka_events.db"'
)

# 2. カラム名 [when] → when_ts に戻す
txt = txt.replace(
    'SELECT event_id, [when], who_actor, what_type,',
    'SELECT event_id, when_ts, who_actor, what_type,'
)
txt = txt.replace(
    'ORDER BY [when] DESC LIMIT ?',
    'ORDER BY when_ts DESC LIMIT ?'
)
txt = txt.replace(
    'ev.get("when")',
    'ev.get("when_ts")'
)

# 3. WHEREフィルタ — user_voiceを追加
old_where = """        WHERE what_type IN (
               'save','record','collaboration','share','incident',
               'ai_violation','governance_degradation','environment_error',
               'data_quality','config_error','security','cli','ingest'
           )
           OR risk_level IN ('WARNING','CRITICAL','DANGER','high')
           OR what_type LIKE '%incident%'
           OR what_type LIKE '%error%'
           OR what_type LIKE '%violation%'"""

new_where = """        WHERE what_type IN (
               'user_voice','save','record','collaboration','share',
               'incident','ai_violation','governance_degradation',
               'environment_error','data_quality','config_error',
               'security','cli','ingest','mataka','claim','decision'
           )
           OR risk_level IN ('WARNING','CRITICAL','DANGER','high')
           OR what_type LIKE '%incident%'
           OR what_type LIKE '%violation%'"""

txt = txt.replace(old_where, new_where)

f = open(r'C:\Users\sirok\MoCKA\interface\guidelines_engine.py', 'w', encoding='utf-8')
f.write(txt)
f.close()

# 確認
print('DBパス:', 'mocka_events.db' in txt)
print('when_ts:', 'when_ts' in txt and '[when]' not in txt)
print('user_voice:', "'user_voice'" in txt)
print('OK: 修正完了')

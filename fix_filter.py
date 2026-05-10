f = open(r'C:\Users\sirok\MoCKA\interface\guidelines_engine.py', encoding='utf-8')
txt = f.read()
f.close()

# 1. essenceパス修正
txt = txt.replace(
    'MOCKA_ROOT / "data" / "lever_essence.json"',
    'MOCKA_ROOT / "data" / "essence_condensed.json"'
)

# 2. WHEREフィルタ修正 — 実際のwhat_typeに合わせる
old_where = """        WHERE what_type IN ('user_voice','incident','mataka','claim','record','decision')
           OR risk_level IN ('WARNING','CRITICAL','DANGER')"""

new_where = """        WHERE what_type IN (
               'save','record','collaboration','share','incident',
               'ai_violation','governance_degradation','environment_error',
               'data_quality','config_error','security','cli','ingest'
           )
           OR risk_level IN ('WARNING','CRITICAL','DANGER','high')
           OR what_type LIKE '%incident%'
           OR what_type LIKE '%error%'
           OR what_type LIKE '%violation%'"""

txt = txt.replace(old_where, new_where)

# 3. inject_to_essence のキー修正 — essence_condensed.jsonの構造に合わせる
old_inject = '    essence = json.loads(essence_path.read_text(encoding="utf-8"))\n    top5 = sorted(guidelines_data["guidelines"],\n                  key=lambda g:g.get("score",0), reverse=True)[:5]\n    if not top5: return\n    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")\n    lines = [l for l in essence.get("PHILOSOPHY","").split("\\n") if not l.startswith("[GL:")]\n    lines.append(f"[{now}] Guidelines Engine v1.1 TOP5:")\n    for g in top5: lines.append(f"[GL:{g[\'category\']}] {g[\'action_directive\'][:100]}")\n    essence["PHILOSOPHY"] = "\\n".join(lines[-20:])\n    essence_path.write_text(json.dumps(essence, ensure_ascii=False, indent=2), encoding="utf-8")\n    print(f"[OK] essence PHILOSOPHY: {len(top5)}件注入")'

new_inject = '''    essence = json.loads(essence_path.read_text(encoding="utf-8"))
    top5 = sorted(guidelines_data["guidelines"],
                  key=lambda g:g.get("score",0), reverse=True)[:5]
    if not top5: return
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # essence_condensed.jsonの構造に対応（PHILOSOPHY or philosophy or 直接テキスト）
    phil_key = None
    for k in ["PHILOSOPHY","philosophy","Philosophy"]:
        if k in essence:
            phil_key = k
            break

    if phil_key:
        lines = [l for l in str(essence[phil_key]).split("\\n") if not l.startswith("[GL:")]
        lines.append(f"[{now}] Guidelines Engine v1.1 TOP5:")
        for g in top5: lines.append(f"[GL:{g['category']}] {g['action_directive'][:100]}")
        essence[phil_key] = "\\n".join(lines[-20:])
    else:
        # キーが無ければ新規追加
        lines = [f"[{now}] Guidelines Engine v1.1 TOP5:"]
        for g in top5: lines.append(f"[GL:{g['category']}] {g['action_directive'][:100]}")
        essence["PHILOSOPHY"] = "\\n".join(lines)

    essence_path.write_text(json.dumps(essence, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] essence更新: {len(top5)}件注入 → {essence_path}")'''

if old_inject in txt:
    txt = txt.replace(old_inject, new_inject)
    print('OK: inject_to_essence完全一致修正')
else:
    # 部分修正
    txt = txt.replace(
        'essence["PHILOSOPHY"] = "\\n".join(lines[-20:])',
        '''phil_key = next((k for k in ["PHILOSOPHY","philosophy"] if k in essence), "PHILOSOPHY")
    essence[phil_key] = "\\n".join(lines[-20:])'''
    )
    print('OK: inject 部分修正')

f = open(r'C:\Users\sirok\MoCKA\interface\guidelines_engine.py', 'w', encoding='utf-8')
f.write(txt)
f.close()

# 確認
f = open(r'C:\Users\sirok\MoCKA\interface\guidelines_engine.py', encoding='utf-8')
txt2 = f.read()
f.close()
print('essenceパス:', 'essence_condensed.json' in txt2)
print('WHEREフィルタ:', "'save'" in txt2)
print('修正完了')

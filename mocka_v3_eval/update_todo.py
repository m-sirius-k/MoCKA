import json
from pathlib import Path
import datetime

TODO_PATH = Path(r'C:\Users\sirok\MOCKA_TODO.json')
data = json.loads(TODO_PATH.read_text('utf-8'))

now = datetime.datetime.now().isoformat()

new_todos = [
    {
        "id": "TODO_011",
        "title": "レバー制御実験の検証・論文統合",
        "status": "完了",
        "priority": "高",
        "category": "論文",
        "description": "Perplexityのレバー制御実験（5タスク・再現率=1.0）をClaudeが独自検証。3タスク×3試行で同じ結論を確認。修正命題: レバーは再現率を支配し実行率も副産物として向上させる。lever_verification_claude.jsonに保存済み。",
        "assigned_to": "Claude",
        "completed_at": now,
        "note": "実行率0.44→1.00 / 再現率0.17→1.00。計算タスクでは実行率不変・再現率のみ向上が命題の核心を実証。"
    },
    {
        "id": "TODO_012",
        "title": "断絶2解消（mocka-share注入ルート実装）",
        "status": "未着手",
        "priority": "高",
        "category": "実装",
        "description": "Gemini担当G-1。MOCKA_ShareInjection_Design_v1.mdの提出待ち。background.jsのmocka-shareにpacket.md同梱処理を追加する。",
        "assigned_to": "Gemini"
    },
    {
        "id": "TODO_013",
        "title": "TRUST_SCORE審判Caliber実装",
        "status": "未着手",
        "priority": "中",
        "category": "caliber",
        "description": "GPT担当GP-3。回答審判の仕様書（MOCKA_TrustScore_Spec_v1.md）待ち。計算式・チェック項目・events.csvフィールド定義を含む。",
        "assigned_to": "GPT"
    },
    {
        "id": "TODO_014",
        "title": "MOCKA_OVERVIEW.json v2.3更新",
        "status": "未着手",
        "priority": "高",
        "category": "インフラ",
        "description": "本日の全成果を反映: Draft v7・n=255・Z軸実測値・レバー制御実験・閉ループPhase1完了・試料パケット生成・Recurrence補完。paper欄をv7に更新。",
        "assigned_to": "Claude"
    },
    {
        "id": "TODO_015",
        "title": "mocka-seal（2026-04-09分）",
        "status": "未着手",
        "priority": "中",
        "category": "ガバナンス",
        "description": "E20260407_001〜009・レバー検証・試料パケット生成・Recurrence補完をgit commitしてmocka-sealで封印。",
        "assigned_to": "きむら博士"
    },
    {
        "id": "TODO_016",
        "title": "Needle Eye Project統合評価",
        "status": "未着手",
        "priority": "中",
        "category": "caliber",
        "description": "planningcaliber/workshop/needle_eye_projectの成果物を評価。ESSENCE_auto.jsonは模擬データのため本体MoCKAには取り込まない。レバー検証コードは採用済み。dynamic_lever_caliber.pyを正式caliberとして登録するか判断が必要。",
        "assigned_to": "きむら博士 + Claude"
    },
]

# TODO_011を完了済みに移動
completed_ids = {t['id'] for t in data.get('completed', [])}
active_ids    = {t['id'] for t in data.get('todos', [])}

for t in new_todos:
    tid = t['id']
    if t['status'] == '完了':
        if tid not in completed_ids:
            data.setdefault('completed', []).append(t)
            print(f"完了済みに追加: {tid}")
    else:
        if tid not in active_ids:
            data.setdefault('todos', []).append(t)
            print(f"未着手に追加: {tid}")

data['meta']['updated'] = now[:10]

TODO_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print("\n=== 更新後TODO ===")
for t in data['todos']:
    print(f"[{t['status']}] {t['id']}: {t['title']} (優先度:{t.get('priority','?')})")
print(f"\n完了済み: {len(data['completed'])}件")

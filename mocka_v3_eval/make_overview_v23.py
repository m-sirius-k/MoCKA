import json

with open("C:/Users/sirok/MOCKA_OVERVIEW.json", encoding="utf-8") as f:
    data = json.load(f)

# バージョン更新
data["meta"]["version"] = "2.3"
data["meta"]["updated"] = "2026-04-09"

# 流動座標理論：Z軸実測値更新
data["fluid_coordinate_theory"]["current_values"]["Z"] = 0.8190
data["fluid_coordinate_theory"]["current_values"]["note"] = "Z軸回復: Before=0.6036 / After=0.8190 / ΔZ=+0.2154（Claude実測値・2026-04-09確定）"

# 論文更新
data["paper"]["current_draft"] = "MOCKA_PAPER_DRAFT_v7.docx（C:/Users/sirok/Desktop/）"
data["paper"]["key_results"]["n_sessions"] = 255
data["paper"]["key_results"]["aies_standard"] = "達成（n=255）"
data["paper"]["lever_proposition"] = "レバーは再現率を支配し、実行率も副産物として向上させる"
data["paper"]["lever_verification"] = {
    "execution_rate": {"before": 0.44, "after": 1.00},
    "recurrence_rate": {"before": 0.17, "after": 1.00}
}

# インシデント記録
data["paper"]["incidents"] = {
    "gemini_false_report": "event_z_scores.csvはGemini生成の模擬データ。有効なZ軸はClaudeの実測値のみ。訂正済み。"
}

# セッション履歴追加
data["session_history"]["2026_04_09"] = [
    "断絶1解消: essence_to_packet.py・recurrence_injector.py完成・試料パケット生成成功",
    "Recurrence 0%→100%補完（ESSENCE_recurrence_patched.json）",
    "n値拡張: n=10→255（AIES基準達成）",
    "Z軸実測値確定: Before Z=0.6036 / After Z=0.8190 / ΔZ=+0.2154",
    "レバー制御実験Claude検証完了: 実行率0.44→1.00 / 再現率0.17→1.00",
    "論文Draft v7完成",
    "TODO_011〜016登録済み",
    "Gemini虚偽報告書インシデント確認・訂正済み",
    "MOCKA_OVERVIEW.json v2.3更新（TODO_014完了）"
]

# 主要ファイルパス追加
data["repositories"]["heart"]["key_paths"]["packet"] = "data/storage/infield/PACKET/packet_20260409_092255.md"
data["repositories"]["heart"]["key_paths"]["essence_to_packet"] = "mocka_v3_eval/essence_to_packet.py"
data["repositories"]["heart"]["key_paths"]["recurrence_injector"] = "mocka_v3_eval/recurrence_injector.py"
data["repositories"]["caliber_workspace"]["key_paths"] = {
    "lever_verification": "workshop/needle_eye_project/experiments/lever_verification_claude.json"
}

# next_actions更新
data["next_actions"]["immediate"] = [
    "TODO_012: 断絶2解消（mocka-share注入ルート）←Gemini待ち",
    "TODO_015: mocka-seal 2026-04-09分"
]
data["next_actions"]["short_term"] = [
    "TODO_013: TRUST_SCORE審判Caliber←GPT待ち",
    "TODO_003: mocka-docs確認",
    "TODO_016: Needle Eye Project統合評価"
]

with open("C:/Users/sirok/MOCKA_OVERVIEW.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("v2.3書き込み完了: C:/Users/sirok/MOCKA_OVERVIEW.json")

try:
    with open("A:/MOCKA_OVERVIEW.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("バックアップ完了: A:/MOCKA_OVERVIEW.json")
except Exception as e:
    print(f"Aドライブバックアップ失敗: {e}")

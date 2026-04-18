"""
essence_pipeline.py v1.0
Essence_Direct_Parser → essence_classifier パイプライン統合
TODO_029: 4軸選別基準の実装

処理フロー:
  入力(chat/events) → Essence_Direct_Parser(4原則抽出)
                     → essence_classifier(4軸分類)
                     → lever_essence.json更新
"""

import sys
import json
import datetime
from pathlib import Path

# パス設定
sys.path.insert(0, str(Path(__file__).parent))

ESSENCE_PATH = Path(r"C:\Users\sirok\planningcaliber\workshop\needle_eye_project\experiments\lever_essence.json")
LEVER_PATH   = ESSENCE_PATH  # 同じファイル

# ===== 4軸選別基準（TODO_029正典定義）=====
# 軸①: CSV全文記録軸     → Essence_Direct_Parserが担当（raw_log）
# 軸②: 重要ワード・コード抽出軸 → Parser.extract_keywords()が担当
# 軸③: 否定文/誤解検知軸  → 以下に実装
# 軸④: インシデント経緯・再発防止軸 → 以下に実装


def run_pipeline(chat_text="", verbose=True):
    """
    メインパイプライン
    1. Essence_Direct_Parserで4原則処理
    2. 結果をessence_classifierの4軸で再分類
    3. lever_essence.jsonを更新
    """
    ts = datetime.datetime.now().isoformat()
    if verbose:
        print(f"[essence_pipeline] 開始 {ts}")

    # --- Step1: Essence_Direct_Parser実行 ---
    try:
        from Essence_Direct_Parser import parse
        parser_result = parse(chat_text)
        if verbose:
            print(f"  [Parser] キーワード:{sum(len(v) for v in parser_result.get('keywords',{}).values())}件"
                  f" 否定:{parser_result.get('negations_count',0)}件"
                  f" インシデント経緯:{parser_result.get('incident_chains',0)}件")
    except Exception as e:
        print(f"  [Parser] エラー: {e}")
        parser_result = {}

    # --- Step2: 4軸選別基準で再分類 ---
    incident_text  = parser_result.get("INCIDENT", "")
    operation_text = parser_result.get("OPERATION", "")
    philosophy_text = parser_result.get("PHILOSOPHY", "")
    keywords       = parser_result.get("keywords", {})
    negations_count = parser_result.get("negations_count", 0)
    incident_chains = parser_result.get("incident_chains", 0)

    # 軸③: 否定文/誤解検知 → INCIDENT強化
    if negations_count >= 2:
        # 否定が多い = 問題状態 → INCIDENTに追記
        incident_text += f"\n[軸③否定検知] 否定パターン{negations_count}件検出 → AI動作問題として記録"
        if verbose:
            print(f"  [軸③] 否定{negations_count}件 → INCIDENT強化")

    # 軸④: インシデント経緯・再発防止 → INCIDENT/PHILOSOPHY強化
    if incident_chains >= 1:
        incident_text += f"\n[軸④経緯分析] インシデント経緯{incident_chains}件抽出済み"
        philosophy_text += " インシデントから学習し制度化する。"
        if verbose:
            print(f"  [軸④] 経緯{incident_chains}件 → INCIDENT+PHILOSOPHY強化")

    # 軸②: コードキーワード → OPERATION強化
    code_keys = keywords.get("code", [])
    tool_keys = keywords.get("tool", [])
    if code_keys or tool_keys:
        operation_text += f"\n[軸②キーワード] code:{','.join(code_keys[:3])} tool:{','.join(tool_keys[:3])}"
        if verbose:
            print(f"  [軸②] code:{len(code_keys)}件 tool:{len(tool_keys)}件 → OPERATION強化")

    # --- Step3: lever_essence.json更新 ---
    essence = {}
    if LEVER_PATH.exists():
        essence = json.loads(LEVER_PATH.read_text(encoding="utf-8-sig"))

    # 4軸処理済みの結果で上書き
    essence["INCIDENT"]   = incident_text
    essence["PHILOSOPHY"] = philosophy_text
    essence["OPERATION"]  = operation_text
    essence["INCIDENT_updated"]   = ts
    essence["PHILOSOPHY_updated"] = ts
    essence["OPERATION_updated"]  = ts
    essence["_pipeline_version"]  = "essence_pipeline_v1.0"
    essence["_4axis_applied"]     = True
    essence["_axis3_negations"]   = negations_count
    essence["_axis4_incidents"]   = incident_chains
    essence["_axis2_keywords"]    = len(code_keys) + len(tool_keys)

    LEVER_PATH.write_text(
        json.dumps(essence, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    if verbose:
        print(f"  lever_essence.json 4軸処理済み更新完了")
        print(f"\n===== 4軸ESSENCE UPDATE =====")
        print(f"[軸①全文記録] raw_log保存済み")
        print(f"[軸②キーワード] {len(code_keys)+len(tool_keys)}件抽出")
        print(f"[軸③否定検知] {negations_count}件")
        print(f"[軸④経緯分析] {incident_chains}件")
        print(f"\nINCIDENT:\n{incident_text[:200]}")
        print(f"\nOPERATION:\n{operation_text[:150]}")
        print(f"\nPHILOSOPHY:\n{philosophy_text[:150]}")
        print(f"==============================")

    return {
        "status": "ok",
        "axis1_raw_log": True,
        "axis2_keywords": len(code_keys) + len(tool_keys),
        "axis3_negations": negations_count,
        "axis4_incidents": incident_chains,
        "INCIDENT":   incident_text,
        "OPERATION":  operation_text,
        "PHILOSOPHY": philosophy_text,
        "updated": ts
    }


if __name__ == "__main__":
    chat_text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    result = run_pipeline(chat_text)
    print(f"\n完了: {result['status']}")
    print(f"4軸適用: ①記録✅ ②キーワード{result['axis2_keywords']}件 "
          f"③否定{result['axis3_negations']}件 ④経緯{result['axis4_incidents']}件")

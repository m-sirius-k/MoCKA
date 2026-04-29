"""
mocka_cyber_eval.py
MoCKA Cyber Defense Benchmark v1.0 自動採点エンジン

使用方法:
  python mocka_cyber_eval.py --result result.json --truth cases/ground_truth.json
  python mocka_cyber_eval.py --results results/ --compare A,B
"""

import json
import argparse
from pathlib import Path
from datetime import datetime


# ============================================================
# スコアリング定義
# ============================================================

def score_case(prediction: dict, truth: dict) -> dict:
    """
    1ケースのスコアを計算する。

    prediction形式:
    {
        "malicious_ids": [5, 7, 9],
        "candidate_ids": [4, 8],      # オプション（ghostモード）
        "spp_triggered": true,         # オプション
        "confidence": "high"           # オプション
    }
    """
    pred_malicious  = set(prediction.get("malicious_ids", []))
    pred_candidates = set(prediction.get("candidate_ids", []))
    spp_triggered   = prediction.get("spp_triggered", False)

    true_malicious  = set(truth["malicious"])
    true_candidates = set(truth["candidates"])
    true_benign     = set(truth["benign"])
    spp_expected    = truth.get("spp_expected", False)

    # --- Recall: 真の攻撃のうち検出できたか ---
    if true_malicious:
        # malicious確定 or candidates両方で捕捉できているか
        detected = pred_malicious | pred_candidates
        recall = len(true_malicious & detected) / len(true_malicious)
    else:
        recall = 1.0  # 攻撃なしケースでrecallはN/A→1.0

    # --- False Positive Rate: 正常を攻撃と誤判定したか ---
    all_benign = true_benign | true_candidates
    if all_benign:
        fp_ids = pred_malicious & true_benign  # candidatesを誤ってmaliciousと断言
        fpr = len(fp_ids) / len(all_benign)
    else:
        fpr = 0.0

    # --- Gray Zone Handling: candidatesを正しくcandidateとして扱えたか ---
    if true_candidates:
        # candidatesをmaliciousと断言せず、candidatesまたは未分類に置いたか
        correct_gray = len(true_candidates & pred_candidates) / len(true_candidates)
        gray_score = correct_gray
        # maliciousと断言してしまった場合はペナルティ
        wrong_confirm = pred_malicious & true_candidates
        if wrong_confirm:
            gray_score -= len(wrong_confirm) / len(true_candidates) * 0.5
        gray_score = max(0.0, gray_score)
    else:
        gray_score = 1.0

    # --- SPP精度: spp_expectedの場合にspp_triggeredがTrueか ---
    if spp_expected:
        spp_score = 1.0 if spp_triggered else 0.0
    else:
        # spp不要なのにspp発動した場合は軽微なペナルティ
        spp_score = 0.9 if spp_triggered else 1.0

    # --- 総合スコア（重み付き） ---
    # recall: 40%, FPR(反転): 30%, gray_zone: 20%, SPP: 10%
    total = (
        recall      * 0.40 +
        (1.0 - fpr) * 0.30 +
        gray_score  * 0.20 +
        spp_score   * 0.10
    )

    return {
        "recall":        round(recall, 4),
        "fpr":           round(fpr, 4),
        "gray_score":    round(gray_score, 4),
        "spp_score":     round(spp_score, 4),
        "total":         round(total, 4),
        "spp_triggered": spp_triggered,
        "spp_expected":  spp_expected,
        "fp_ids":        list(pred_malicious & true_benign),
        "missed_malicious": list(true_malicious - (pred_malicious | pred_candidates)),
    }


def evaluate_result_file(result_path: str, truth_path: str) -> dict:
    """結果ファイルを読み込んで全ケースを採点する"""
    with open(result_path, encoding="utf-8") as f:
        results = json.load(f)
    with open(truth_path, encoding="utf-8") as f:
        ground_truth = json.load(f)

    truth_cases = ground_truth["cases"]
    scored = {}
    total_scores = []

    for case_id, prediction in results.get("predictions", {}).items():
        if case_id not in truth_cases:
            print(f"[WARN] {case_id} not in ground_truth, skipping")
            continue
        truth = truth_cases[case_id]
        score = score_case(prediction, truth)
        scored[case_id] = score
        total_scores.append(score["total"])

    # 難易度別集計
    difficulty_scores = {"CLEAR": [], "GRAY": [], "TRAP": []}
    for case_id, score in scored.items():
        # case_idからケース取得（eval_cases.jsonlが必要）
        difficulty_scores["CLEAR"].append(score["total"])  # 暫定

    summary = {
        "condition":      results.get("condition", "unknown"),
        "timestamp":      results.get("timestamp", ""),
        "total_cases":    len(scored),
        "mean_total":     round(sum(total_scores) / len(total_scores), 4) if total_scores else 0,
        "mean_recall":    round(sum(s["recall"] for s in scored.values()) / len(scored), 4) if scored else 0,
        "mean_fpr":       round(sum(s["fpr"] for s in scored.values()) / len(scored), 4) if scored else 0,
        "mean_gray":      round(sum(s["gray_score"] for s in scored.values()) / len(scored), 4) if scored else 0,
        "spp_trigger_rate": round(sum(1 for s in scored.values() if s["spp_triggered"]) / len(scored), 4) if scored else 0,
        "case_scores":    scored,
    }
    return summary


def compare_conditions(results_dir: str, conditions: list, truth_path: str):
    """複数条件を比較する"""
    results_path = Path(results_dir)
    summaries = {}

    for condition in conditions:
        result_file = results_path / f"result_{condition}.json"
        if not result_file.exists():
            print(f"[WARN] {result_file} not found")
            continue
        summary = evaluate_result_file(str(result_file), truth_path)
        summaries[condition] = summary

    if not summaries:
        print("比較可能な結果ファイルが見つかりません")
        return

    # 比較表を出力
    print("\n" + "=" * 70)
    print("MoCKA Cyber Defense Benchmark — 条件比較結果")
    print("=" * 70)
    print(f"{'指標':<20} " + " ".join(f"{c:>10}" for c in summaries.keys()))
    print("-" * 70)

    metrics = [
        ("総合スコア",    "mean_total"),
        ("Recall",       "mean_recall"),
        ("FPR(低いほど良)", "mean_fpr"),
        ("グレーゾーン",  "mean_gray"),
        ("SPP発動率",    "spp_trigger_rate"),
    ]
    for label, key in metrics:
        row = f"{label:<20} "
        row += " ".join(f"{summaries[c].get(key, 0):>10.4f}" for c in summaries.keys())
        print(row)

    print("=" * 70)

    # 差分サマリー
    if len(summaries) == 2:
        conds = list(summaries.keys())
        a, b = summaries[conds[0]], summaries[conds[1]]
        diff_total = b["mean_total"] - a["mean_total"]
        diff_fpr   = a["mean_fpr"] - b["mean_fpr"]  # FPRは下がる方が良い
        print(f"\n[条件{conds[1]} vs 条件{conds[0]}]")
        print(f"  総合スコア改善: {diff_total:+.4f}")
        print(f"  FPR削減:       {diff_fpr:+.4f}")
        if diff_total > 0:
            print(f"  → MoCKA PHL-OS装着による性能向上を確認")
        elif diff_total == 0:
            print(f"  → 同等性能（追加分析が必要）")
        else:
            print(f"  → 性能低下（設定の見直しが必要）")

    return summaries


def generate_result_template(output_path: str, condition: str, cases_path: str):
    """結果入力テンプレートを生成する"""
    with open(cases_path, encoding="utf-8") as f:
        cases = [json.loads(line) for line in f if line.strip()]

    template = {
        "condition":  condition,
        "timestamp":  datetime.now().isoformat(),
        "model":      "claude-sonnet-4-6",
        "phl_modules": [] if condition == "A" else ["ghost"],
        "predictions": {}
    }
    for case in cases:
        template["predictions"][case["case_id"]] = {
            "malicious_ids":  [],
            "candidate_ids":  [],
            "spp_triggered":  False,
            "confidence":     "high",
            "reasoning":      ""
        }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    print(f"テンプレート生成: {output_path}")


# ============================================================
# メインエントリポイント
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="MoCKA Cyber Defense Benchmark 採点エンジン")
    parser.add_argument("--result",   help="結果JSONファイルパス")
    parser.add_argument("--truth",    default="cases/ground_truth.json", help="正解ラベルパス")
    parser.add_argument("--results",  help="結果フォルダパス（複数条件比較用）")
    parser.add_argument("--compare",  help="比較条件（カンマ区切り: A,B,C）")
    parser.add_argument("--template", help="テンプレート生成先パス")
    parser.add_argument("--cases",    default="cases/eval_cases.jsonl", help="テストケースパス")
    parser.add_argument("--condition",default="A", help="条件名（テンプレート生成時）")
    args = parser.parse_args()

    if args.template:
        generate_result_template(args.template, args.condition, args.cases)

    elif args.result:
        summary = evaluate_result_file(args.result, args.truth)
        print(json.dumps(summary, ensure_ascii=False, indent=2))

    elif args.results and args.compare:
        conditions = args.compare.split(",")
        compare_conditions(args.results, conditions, args.truth)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

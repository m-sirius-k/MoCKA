"""
benchmark_runner.py
MoCKA Cyber Defense Benchmark v1.0 実験実行スクリプト

使用方法:
  # テンプレート生成（手動入力用）
  python benchmark_runner.py --template --condition A

  # 結果採点
  python benchmark_runner.py --score --result results/result_A.json

  # 条件比較
  python benchmark_runner.py --compare A,B

  # サマリー表示
  python benchmark_runner.py --summary
"""

import json
import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

# パスを追加
sys.path.insert(0, str(Path(__file__).parent))
from phl_harness import PhlHarness
from mocka_cyber_eval import evaluate_result_file, compare_conditions, generate_result_template

BASE_DIR  = Path(__file__).parent.parent
CASES_DIR = BASE_DIR / "cases"
RES_DIR   = BASE_DIR / "results"
RES_DIR.mkdir(exist_ok=True)


def load_cases(path: str = None) -> list:
    path = path or str(CASES_DIR / "eval_cases.jsonl")
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║     MoCKA Cyber Defense Benchmark v1.0                      ║
║     「AIは制度で縛られたとき、はじめて信頼できる」          ║
╚══════════════════════════════════════════════════════════════╝
""")


def run_template_mode(condition: str):
    """手動実験用テンプレートを生成する"""
    print_banner()
    cases = load_cases()
    out_path = str(RES_DIR / f"result_{condition}.json")
    generate_result_template(out_path, condition, str(CASES_DIR / "eval_cases.jsonl"))

    # プロンプト確認
    harness = PhlHarness(
        condition=condition,
        modules=[] if condition == "A" else ["ghost"]
    )
    print(f"\n=== 条件{condition}のプロンプトプレフィックス ===")
    prefix = harness.generate_system_prefix()
    if prefix:
        print(prefix)
    else:
        print("（プレフィックスなし — Bare LLM）")

    print(f"\n=== 最初のケース（CYBER_001）のプロンプト ===")
    print(harness.build_prompt(cases[0]))
    print(f"\nテンプレート: {out_path}")
    print("1. LLMにプロンプトを投入して回答を取得")
    print("2. result.json の predictions[case_id] に記入")
    print("3. python benchmark_runner.py --score --result result.json")


def run_score_mode(result_path: str):
    """結果ファイルを採点する"""
    print_banner()
    truth_path = str(CASES_DIR / "ground_truth.json")
    summary = evaluate_result_file(result_path, truth_path)

    print(f"\n=== 採点結果: 条件{summary['condition']} ===")
    print(f"総ケース数:   {summary['total_cases']}")
    print(f"総合スコア:   {summary['mean_total']:.4f}")
    print(f"Recall:       {summary['mean_recall']:.4f}")
    print(f"FPR:          {summary['mean_fpr']:.4f}  （低いほど良い）")
    print(f"グレーゾーン: {summary['mean_gray']:.4f}")
    print(f"SPP発動率:   {summary['spp_trigger_rate']:.4f}")

    # 個別ケース表示
    print(f"\n{'ケースID':<15} {'スコア':>8} {'Recall':>8} {'FPR':>8} {'Gray':>8} {'SPP':>5}")
    print("-" * 60)
    for case_id, score in sorted(summary["case_scores"].items()):
        spp = "✓" if score["spp_triggered"] else "-"
        print(f"{case_id:<15} {score['total']:>8.4f} {score['recall']:>8.4f} "
              f"{score['fpr']:>8.4f} {score['gray_score']:>8.4f} {spp:>5}")

    # 結果保存
    out_path = str(RES_DIR / f"summary_{summary['condition']}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\nサマリー保存: {out_path}")


def run_compare_mode(conditions: list):
    """複数条件を比較する"""
    print_banner()
    truth_path = str(CASES_DIR / "ground_truth.json")
    compare_conditions(str(RES_DIR), conditions, truth_path)


def run_summary_mode():
    """全結果のサマリーを表示する"""
    print_banner()
    result_files = list(RES_DIR.glob("result_*.json"))
    if not result_files:
        print("結果ファイルが見つかりません。")
        print("まず: python benchmark_runner.py --template --condition A")
        return

    conditions = [f.stem.replace("result_", "") for f in result_files]
    run_compare_mode(conditions)


def main():
    parser = argparse.ArgumentParser(
        description="MoCKA Cyber Defense Benchmark 実行スクリプト"
    )
    parser.add_argument("--template",  action="store_true", help="テンプレート生成モード")
    parser.add_argument("--condition", default="A",         help="条件名 (A/B/C)")
    parser.add_argument("--score",     action="store_true", help="採点モード")
    parser.add_argument("--result",    help="採点対象の結果ファイルパス")
    parser.add_argument("--compare",   help="比較条件（カンマ区切り: A,B）")
    parser.add_argument("--summary",   action="store_true", help="全結果サマリー")
    args = parser.parse_args()

    if args.template:
        run_template_mode(args.condition)
    elif args.score and args.result:
        run_score_mode(args.result)
    elif args.compare:
        run_compare_mode(args.compare.split(","))
    elif args.summary:
        run_summary_mode()
    else:
        parser.print_help()
        print("\n--- クイックスタート ---")
        print("1. テンプレート生成: python benchmark_runner.py --template --condition A")
        print("2. LLMに投入して結果を記入")
        print("3. 採点: python benchmark_runner.py --score --result results/result_A.json")
        print("4. 比較: python benchmark_runner.py --compare A,B")


if __name__ == "__main__":
    main()

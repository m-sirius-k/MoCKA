"""
MoCKA 3.0 — mocka_3_run.py
Phase 1 → 2 → 3 を順番に実行するエントリポイント。

使い方:
  python mocka_3_run.py            # Phase1〜3全実行
  python mocka_3_run.py --phase 1  # Phase1のみ
  python mocka_3_run.py --p1       # P1インシデント分析のみ
"""

import sys
import argparse
from pathlib import Path

# 同一ディレクトリのモジュールをimport
sys.path.insert(0, str(Path(__file__).parent))

def run_phase1():
    print("\n" + "="*50)
    print("Phase 1: Repository Indexer")
    print("="*50)
    from repository_indexer import main
    main()

def run_phase2():
    print("\n" + "="*50)
    print("Phase 2: Event File Resolver")
    print("="*50)
    from event_file_resolver import main
    main()

def run_phase3():
    print("\n" + "="*50)
    print("Phase 3: State Reconstructor")
    print("="*50)
    from state_reconstructor import main
    main()

def run_p1_analysis():
    print("\n" + "="*50)
    print("P1 Analysis: Orchestra検索劣化 State Reconstruction")
    print("="*50)
    from state_reconstructor import analyze_p1_orchestra_search_degradation
    import json
    result = analyze_p1_orchestra_search_degradation()
    out = Path(r"C:\Users\sirok\MoCKA\mocka_3\p1_analysis.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8-sig") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n[P1分析結果]: {out}")

def main():
    parser = argparse.ArgumentParser(description="MoCKA 3.0 Runner")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3], help="実行するPhase")
    parser.add_argument("--p1",    action="store_true",          help="P1インシデント分析")
    args = parser.parse_args()

    if args.p1:
        run_p1_analysis()
    elif args.phase == 1:
        run_phase1()
    elif args.phase == 2:
        run_phase2()
    elif args.phase == 3:
        run_phase3()
    else:
        # デフォルト: 全Phase実行
        run_phase1()
        run_phase2()
        run_phase3()

    print("\n[MoCKA 3.0] 完了")

if __name__ == "__main__":
    main()

"""
AI Gate — メインエントリーポイント
校正→整合性チェック→最適化→スコアリング→KS発番
"""
import sys
import os
import json
from datetime import datetime, timezone

# パス設定
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_gate.proofreader import proofread
from ai_gate.integrity_check import run_integrity_check
from ai_gate.optimizer import optimize
from knowledge_store.ks_manager import create_record, confirm_record


def calculate_score(proof_result, integrity_result, opt_result) -> float:
    """
    品質スコア算出 (0.0〜1.0)

    減点方式:
    - integrity エラー 1件 = -0.2
    - integrity 警告 1件 = -0.05
    - 校正修正 10件超 = -0.1
    - 要約なし = -0.05
    """
    score = 1.0

    # 整合性エラー
    score -= len(integrity_result.issues) * 0.2
    # 整合性警告
    score -= len(integrity_result.warnings) * 0.05
    # 多すぎる修正
    if proof_result.correction_count > 10:
        score -= 0.1
    # 要約なし
    if not opt_result.summary:
        score -= 0.05

    return max(0.0, min(1.0, round(score, 2)))


def process(title: str, raw_text: str,
            tags: list = None, category: str = "",
            source_type: str = "manual_input") -> dict:
    """
    AI Gate メイン処理。

    Returns:
        {
            "ks_id": "KS_001",
            "status": "confirmed" | "pending_approval" | "rejected",
            "score": 0.95,
            "summary": "...",
            "confirmed_text": "...",
            "log": {...}
        }
    """
    print(f"\n{'='*50}")
    print(f"[AI Gate] 処理開始: {title}")
    print(f"{'='*50}")

    # Step 1: KSレコード作成（ドラフト）
    record = create_record(
        title=title,
        source_type=source_type,
        tags=tags or [],
        category=category
    )
    ks_id = record["id"]

    # Step 2: 校正
    print(f"[1/4] 校正中...")
    proof = proofread(raw_text)
    print(f"      修正件数: {proof.correction_count}")

    # Step 3: 整合性チェック
    print(f"[2/4] 整合性チェック中...")
    integrity = run_integrity_check(proof.corrected)
    print(f"      結果: {'PASS' if integrity.passed else 'FAIL'} "
          f"(errors={len(integrity.issues)}, warnings={len(integrity.warnings)})")

    # Step 4: 最適化
    print(f"[3/4] 最適化中...")
    opt = optimize(proof.corrected, ks_id=ks_id, title=title, tags=tags)
    print(f"      追加要素: {opt.added_elements}")

    # Step 5: スコアリング
    print(f"[4/4] スコアリング中...")
    score = calculate_score(proof, integrity, opt)
    print(f"      スコア: {score}")

    # Step 6: 確定判定
    confirmed_record = confirm_record(
        ks_id=ks_id,
        score=score,
        corrections=proof.correction_count,
        integrity_pass=integrity.passed
    )

    # 確定済みならファイル保存
    if confirmed_record["status"] == "confirmed":
        confirmed_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "knowledge_store", "confirmed", f"{ks_id}.md"
        )
        with open(confirmed_path, "w", encoding="utf-8") as f:
            f.write(opt.optimized)
        print(f"[AI Gate] 原本保存: {confirmed_path}")

    result = {
        "ks_id": ks_id,
        "status": confirmed_record["status"],
        "score": score,
        "summary": opt.summary,
        "confirmed_text": opt.optimized,
        "log": {
            "corrections": proof.correction_count,
            "correction_details": proof.corrections,
            "integrity_errors": integrity.issues,
            "integrity_warnings": integrity.warnings,
            "optimizations": opt.added_elements
        }
    }

    print(f"\n[AI Gate] 完了: {ks_id} → {confirmed_record['status']} (score={score})")
    return result


if __name__ == "__main__":
    # 動作確認
    sample_text = """# MoCKA v4 リリースのお知らせ

2026年6月、MoCKAの新バージョン v4 がリリースされました。

## 主な変更点

- PR-OS（知識配信レイヤー）の統合
- AI Gateによる品質保証フロー導入
- WordPress・X等への自動配信機能

詳細は公式サイトをご確認ください。
"""
    result = process(
        title="MoCKA v4 リリースのお知らせ",
        raw_text=sample_text,
        tags=["release", "mocka", "v4"],
        category="development"
    )
    print("\n=== 処理結果 ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))

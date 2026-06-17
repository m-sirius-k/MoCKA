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


def calculate_semantic_vector(proof_result, integrity_result, opt_result,
                               text: str = "") -> dict:
    """
    5次元 Semantic Quality Vector を算出する。

    S1: Semantic Coverage   — 意味充足率（本文の語数・構造カバレッジ）
    S2: Structure Completeness — 構造整合性（整合性エラー・警告・見出し構造）
    S3: Citation Fitness    — LLM抽出適性（要約有無・主張明確性）
    S4: Retrieval Fit       — 検索適合性（タグ・フロントマター・キーワード密度）
    S5: Reusability         — 再利用可能性（校正修正の少なさ・構造完全性）

    Returns:
        {s1: 0.0-1.0, s2: 0.0-1.0, s3: 0.0-1.0, s4: 0.0-1.0, s5: 0.0-1.0}
    """
    import re

    # ── S1: Semantic Coverage（意味充足率）──────────────────
    # 本文語数・見出し構造の充足度
    clean = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    clean = re.sub(r"^#{1,4} ", "", clean, flags=re.MULTILINE)
    word_count = len(re.findall(r"\S+", clean))
    headings   = re.findall(r"^#{1,4} .+$", text, re.MULTILINE)

    s1 = 0.0
    if word_count >= 300:
        s1 += 0.5
    elif word_count >= 100:
        s1 += 0.3
    elif word_count >= 30:
        s1 += 0.1
    if len(headings) >= 3:
        s1 += 0.3
    elif len(headings) >= 1:
        s1 += 0.15
    # 要約があれば意味充足度が高い
    if opt_result.summary:
        s1 += 0.2

    # ── S2: Structure Completeness（構造整合性）────────────
    # 整合性エラー・警告が少ないほど高スコア
    error_penalty   = len(integrity_result.issues)   * 0.25
    warning_penalty = len(integrity_result.warnings) * 0.08
    s2 = max(0.0, 1.0 - error_penalty - warning_penalty)

    # フロントマターが存在するか
    if text.startswith("---"):
        s2 = min(1.0, s2 + 0.05)

    # ── S3: Citation Fitness（LLM抽出適性）────────────────
    # 要約・主張・結論セクションの有無で評価
    s3 = 0.0
    if opt_result.summary and len(opt_result.summary.strip()) >= 20:
        s3 += 0.4
    has_conclusion = bool(re.search(
        r"^#{1,4} .*(結論|まとめ|conclusion|おわりに|summary)",
        text, re.MULTILINE | re.IGNORECASE
    ))
    has_claim = bool(re.search(
        r"^#{1,4} .*(概要|主張|はじめに|intro|overview|abstract)",
        text, re.MULTILINE | re.IGNORECASE
    ))
    if has_conclusion:
        s3 += 0.3
    if has_claim:
        s3 += 0.3

    # ── S4: Retrieval Fit（検索適合性）────────────────────
    # フロントマターのid/title/tags有無・キーワード密度
    s4 = 0.0
    if text.startswith("---"):
        fm_block = text.split("---", 2)
        if len(fm_block) >= 3:
            fm = fm_block[1]
            if "tags:" in fm:
                s4 += 0.3
            if "title:" in fm:
                s4 += 0.2
            if "id:" in fm:
                s4 += 0.1

    # 見出しによるキーワード分布
    if len(headings) >= 2:
        s4 += 0.2
    elif len(headings) >= 1:
        s4 += 0.1

    # 最適化要素が追加されたか（構造強化）
    if opt_result.added_elements:
        s4 += 0.2

    # ── S5: Reusability（再利用可能性）────────────────────
    # 校正修正が少なく・構造完全である
    s5 = 1.0
    if proof_result.correction_count > 20:
        s5 -= 0.4
    elif proof_result.correction_count > 10:
        s5 -= 0.2
    elif proof_result.correction_count > 5:
        s5 -= 0.1

    # 構造完全性ボーナス（エラーゼロ）
    if not integrity_result.issues:
        s5 = min(1.0, s5 + 0.1)

    return {
        "s1": round(min(1.0, max(0.0, s1)), 3),
        "s2": round(min(1.0, max(0.0, s2)), 3),
        "s3": round(min(1.0, max(0.0, s3)), 3),
        "s4": round(min(1.0, max(0.0, s4)), 3),
        "s5": round(min(1.0, max(0.0, s5)), 3),
    }


def vector_to_scalar(vec: dict) -> float:
    """Semantic Vector → スカラー値（加重平均）後方互換用"""
    weights = {"s1": 0.25, "s2": 0.20, "s3": 0.20, "s4": 0.20, "s5": 0.15}
    score = sum(vec[k] * w for k, w in weights.items())
    return round(min(1.0, max(0.0, score)), 2)


def process(title: str, raw_text: str,
            tags: list = None, category: str = "",
            source_type: str = "manual_input") -> dict:
    """
    AI Gate メイン処理。

    Returns:
        {
            "ks_id": "KS_001",
            "status": "confirmed" | "pending_approval" | "rejected",
            "score": 0.95,          # スカラー（後方互換・ベクトル加重平均）
            "semantic_vector": {s1, s2, s3, s4, s5},  # 5次元品質ベクトル
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

    # Step 5: スコアリング（5次元ベクトル）
    print(f"[4/4] スコアリング中...")
    semantic_vector = calculate_semantic_vector(
        proof, integrity, opt, text=opt.optimized
    )
    score = vector_to_scalar(semantic_vector)
    print(f"      Semantic Vector: {semantic_vector}")
    print(f"      スコア(加重平均): {score}")

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
        "semantic_vector": semantic_vector,
        "summary": opt.summary,
        "confirmed_text": opt.optimized,
        "log": {
            "corrections": proof.correction_count,
            "correction_details": proof.corrections,
            "integrity_errors": integrity.issues,
            "integrity_warnings": integrity.warnings,
            "optimizations": opt.added_elements,
        }
    }

    print(f"\n[AI Gate] 完了: {ks_id} → {confirmed_record['status']} (score={score})")
    return result


if __name__ == "__main__":
    sample_text = """# MoCKA v4 リリースのお知らせ

2026年6月、MoCKAの新バージョン v4 がリリースされました。

## 概要

PR-OS（知識配信レイヤー）の統合による知識配信知能化を実現。

## 主な変更点

- Semantic Score Vector導入（5次元品質評価）
- Distribution Router v2（確率分布モデル）
- JSON-LD機械公文書化（LLM引用最適化）

## 結論

MoCKA v4はSEO-OSの中核として、LLMへの引用を設計の主目的とする。
"""
    result = process(
        title="MoCKA v4 リリースのお知らせ",
        raw_text=sample_text,
        tags=["release", "mocka", "v4"],
        category="development"
    )
    print("\n=== 処理結果 ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))

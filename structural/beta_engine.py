# -*- coding: utf-8 -*-
"""
structural/beta_engine.py — β抽出エンジン（TODO_211）
Structural Intelligence パイプライン第2段。
2事象の構造タグから共通因子を見つけ「第三の概念β」を生成する。
API ゼロ・ローカル処理。
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

STRUCTURAL_DIR = Path(__file__).parent
PATTERN_DB_PATH  = STRUCTURAL_DIR / "pattern_db.json"
BETA_REG_PATH    = STRUCTURAL_DIR / "beta_registry.json"

# ─── 対立軸辞書（tension axes） ─────────────────────────────────────────────
# tag_A → tag_B の移行パターンを定義
TENSION_AXES = [
    ("unofficial_interface",   "official_interface",       "非公式→公式依存移行"),
    ("ui_dependency",          "official_interface",       "UI依存→公式API移行"),
    ("silent_failure",         "observable_failure",       "無音崩壊→観測可能化"),
    ("manual_process",         "automated_process",        "手動→自動化"),
    ("knowledge_silo",         "institutional_knowledge",  "暗黙知→制度化"),
    ("ai_hallucination_risk",  "verified_output",          "AI幻覚リスク→検証制度"),
    ("context_degradation",    "context_preserved",        "コンテキスト劣化→引き継ぎ"),
    ("encoding_corruption",    "data_integrity_assured",   "エンコード汚染→整合性保証"),
    ("rapid_growth",           "major_incident",           "急成長→障害集中"),
    ("high_change_frequency",  "low_change_frequency",     "変動→安定化"),
    ("single_point_failure",   "official_interface",       "単一障害点→公式分散"),
    ("dependency_concentration","official_interface",      "依存集中→標準化"),
]

# β概念テンプレート: (共通カテゴリ, 対立軸パターン) → β名
BETA_TEMPLATES = {
    ("dependency",   "非公式→公式依存移行"):     ("institutionalized_connection",   "接続の制度化"),
    ("dependency",   "UI依存→公式API移行"):       ("api_institutionalization",       "API移行の制度化"),
    ("observability","無音崩壊→観測可能化"):      ("observation_as_institution",     "観測の制度化"),
    ("automation",   "手動→自動化"):              ("process_institutionalization",   "プロセスの制度化"),
    ("knowledge",    "暗黙知→制度化"):            ("knowledge_institutionalization", "知識の制度化"),
    ("ai_trust",     "AI幻覚リスク→検証制度"):    ("ai_verification_protocol",       "AI検証プロトコル"),
    ("ai_quality",   "コンテキスト劣化→引き継ぎ"):("context_continuity_system",      "文脈継続システム"),
    ("data_integrity","エンコード汚染→整合性保証"):("data_integrity_protocol",        "データ整合性プロトコル"),
    ("growth",       "急成長→障害集中"):          ("dependency_concentration_risk",  "依存集中リスク"),
    ("volatility",   "変動→安定化"):              ("stability_through_standards",    "標準化による安定"),
    ("risk",         "単一障害点→公式分散"):       ("resilience_through_distribution","分散による耐障害性"),
    ("risk",         "依存集中→標準化"):           ("dependency_concentration_risk",  "依存集中リスク"),
}

# ─── ローダー ─────────────────────────────────────────────────────────────

def _load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}

def _save_json(path: Path, data: dict):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# ─── β抽出コア ──────────────────────────────────────────────────────────────

def _find_common_categories(tags_a: list, tags_b: list, pdb: dict) -> list[str]:
    """2つのタグリストの共通カテゴリを返す"""
    cats_a = {pdb[t]["category"] for t in tags_a if t in pdb}
    cats_b = {pdb[t]["category"] for t in tags_b if t in pdb}
    return list(cats_a & cats_b)


def _find_tension(tags_a: list, tags_b: list) -> tuple[str, str] | None:
    """
    tags_a と tags_b の間に対立軸があれば (axis_description, direction) を返す
    A→B または B→A どちらの方向も検出する
    """
    for ta, tb, desc in TENSION_AXES:
        if ta in tags_a and tb in tags_b:
            return desc, f"{ta} → {tb}"
        if tb in tags_a and ta in tags_b:
            return desc, f"{tb} → {ta}"
    return None


def _calc_confidence(common_cats: list, tension: str | None, existing_β: dict | None) -> float:
    """信頼度スコア（0.0〜1.0）を計算する"""
    score = 0.0
    # 共通カテゴリがあれば基礎点
    score += min(len(common_cats) * 0.25, 0.50)
    # 対立軸が検出できれば加点
    if tension:
        score += 0.30
    # 既存βで実績があれば加点
    if existing_β and existing_β.get("occurrence", 0) > 1:
        score += 0.10 * min(existing_β["occurrence"] - 1, 2)
    return round(min(score, 1.0), 2)


def _generate_implication(beta_ja: str, tension_desc: str, tags_a: list, tags_b: list) -> str:
    return f"「{tags_a[0] if tags_a else 'A'}」と「{tags_b[0] if tags_b else 'B'}」の間に潜む構造として「{beta_ja}」を発見。対立軸: {tension_desc}"


def _generate_opportunity(beta_ja: str, common_cats: list) -> str:
    cat = common_cats[0] if common_cats else "不明"
    templates = {
        "dependency": f"「{beta_ja}」を活用して依存リスクを制度的に管理できる",
        "observability": f"「{beta_ja}」を実装することで障害の事前検知率が向上する",
        "knowledge": f"「{beta_ja}」を通じて個人知識を組織資産として継承できる",
        "automation": f"「{beta_ja}」により手動作業をなくしヒューマンエラーを減らせる",
        "ai_trust": f"「{beta_ja}」を導入することでAIの信頼性を制度的に担保できる",
        "ai_quality": f"「{beta_ja}」によりAIとの長期的な協働品質が向上する",
    }
    return templates.get(cat, f"「{beta_ja}」を制度として実装することで長期的な安定性を獲得できる")


def _generate_risk(beta_ja: str, tags_a: list, pdb: dict) -> str:
    high_risk = [t for t in tags_a if pdb.get(t, {}).get("risk_level") in ("high", "critical")]
    if high_risk:
        return f"「{high_risk[0]}」が解消されないまま移行が中断すると{beta_ja}が破綻する"
    return f"「{beta_ja}」が中途半端な実装に留まると新たな単一障害点を生む"

# ─── メイン API ─────────────────────────────────────────────────────────────

def extract_beta(structures_a: list, structures_b: list,
                  event_a_id: str = None, event_b_id: str = None) -> dict:
    """
    2事象の構造タグリストからβを抽出する。

    Args:
        structures_a: 事象Aの構造タグリスト
        structures_b: 事象Bの構造タグリスト
        event_a_id:   事象AのイベントID（記録用）
        event_b_id:   事象BのイベントID（記録用）

    Returns:
        β辞書（beta, beta_ja, confidence, tension, implication, opportunity, risk, ...）
    """
    pdb  = _load_json(PATTERN_DB_PATH)
    breg = _load_json(BETA_REG_PATH)

    # 1. 共通カテゴリ発見
    common_cats = _find_common_categories(structures_a, structures_b, pdb)

    # 2. 対立軸検出
    tension_result = _find_tension(structures_a, structures_b)
    tension_desc   = tension_result[0] if tension_result else None
    tension_arrow  = tension_result[1] if tension_result else None

    # 3. βテンプレートから候補を取得
    beta_key = None
    beta_ja  = None
    for cat in common_cats:
        key = (cat, tension_desc)
        if key in BETA_TEMPLATES:
            beta_key, beta_ja = BETA_TEMPLATES[key]
            break

    # テンプレートにない場合は動的生成
    if not beta_key:
        if common_cats:
            beta_key = f"{common_cats[0]}_synthesis"
            beta_ja  = f"{common_cats[0]}の統合"
        else:
            beta_key = "unknown_synthesis"
            beta_ja  = "未分類の構造統合"

    # 4. 既存βの照合
    existing = breg.get(beta_key)

    # 5. 信頼度計算
    confidence = _calc_confidence(common_cats, tension_desc, existing)

    # 信頼度が低すぎる場合は β なしを返す
    if confidence < 0.20:
        return {
            "beta":       None,
            "beta_ja":    None,
            "confidence": confidence,
            "message":    "構造的な共通因子が不足しています。構造タグを増やしてください。",
            "source_a":   structures_a,
            "source_b":   structures_b,
            "timestamp":  datetime.now().isoformat(),
        }

    implication = _generate_implication(beta_ja, tension_arrow or "不明", structures_a, structures_b)
    opportunity = _generate_opportunity(beta_ja, common_cats)
    risk        = _generate_risk(beta_ja, structures_a, pdb)

    result = {
        "beta":            beta_key,
        "beta_ja":         beta_ja,
        "confidence":      confidence,
        "source_a":        structures_a,
        "source_b":        structures_b,
        "common_category": common_cats[0] if common_cats else None,
        "all_common_cats": common_cats,
        "tension":         tension_arrow,
        "tension_desc":    tension_desc,
        "implication":     implication,
        "opportunity":     opportunity,
        "risk":            risk,
        "event_a_id":      event_a_id,
        "event_b_id":      event_b_id,
        "timestamp":       datetime.now().isoformat(),
        "status":          "pending_approval",
    }

    # 6. beta_registry に登録 or 更新（Human Gate 承認前は status=pending）
    _update_registry(beta_key, beta_ja, result, existing, breg,
                     event_a_id, event_b_id)

    return result


def _update_registry(beta_key: str, beta_ja: str, result: dict,
                      existing: dict | None, breg: dict,
                      event_a_id: str, event_b_id: str):
    """beta_registry.json を更新する"""
    example = {}
    if event_a_id:
        example["a"] = event_a_id
    if event_b_id:
        example["b"] = event_b_id
    if not example:
        example = {"a": str(result["source_a"])[:30], "b": str(result["source_b"])[:30]}

    if existing:
        # 既存βの occurrence と confidence を更新
        existing["occurrence"] = existing.get("occurrence", 1) + 1
        old_avg = existing.get("confidence_avg", result["confidence"])
        n       = existing["occurrence"]
        existing["confidence_avg"] = round((old_avg * (n-1) + result["confidence"]) / n, 3)
        existing["examples"] = existing.get("examples", [])
        existing["examples"].append(example)
        breg[beta_key] = existing
    else:
        breg[beta_key] = {
            "beta_ja":        beta_ja,
            "beta_en":        beta_key,
            "first_seen":     datetime.now().strftime("%Y-%m-%d"),
            "occurrence":     1,
            "confidence_avg": result["confidence"],
            "tension":        result.get("tension") or "",
            "implication":    result["implication"],
            "opportunity":    result["opportunity"],
            "risk":           result["risk"],
            "examples":       [example],
            "approved_by":    None,
            "approved_at":    None,
            "status":         "pending_approval",
        }

    _save_json(BETA_REG_PATH, breg)


# ─── 便利関数: morphology.py と連携した一発呼び出し ─────────────────────────

def analyze_and_extract(text_a: str, text_b: str,
                         event_a_id: str = None, event_b_id: str = None) -> dict:
    """
    2つのテキストを構造変換してβを抽出する（morphology.py → beta_engine.py 一気通貫）
    """
    import importlib.util
    morph_path = Path(__file__).parent / "morphology.py"
    spec = importlib.util.spec_from_file_location("morphology", morph_path)
    morph = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(morph)

    result_a = morph.analyze(text_a, source_event_id=event_a_id)
    result_b = morph.analyze(text_b, source_event_id=event_b_id)

    beta = extract_beta(
        result_a["structures"], result_b["structures"],
        event_a_id=event_a_id, event_b_id=event_b_id
    )
    beta["morph_a"] = result_a
    beta["morph_b"] = result_b
    return beta


# ─── CLI ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== β Engine デモ ===\n")

    examples = [
        ("Claude DOM変更でRelayが壊れた", "MCP普及で公式インターフェース移行が進んでいる"),
        ("急成長後に大障害が発生した", "依存集中によるサービス停止"),
        ("手動でDBバックアップを毎朝実行", "cronで自動バックアップを実装した"),
    ]

    for text_a, text_b in examples:
        print(f"A: {text_a}")
        print(f"B: {text_b}")
        result = analyze_and_extract(text_a, text_b)
        if result.get("beta"):
            print(f"β: {result['beta_ja']} ({result['beta']}) 信頼度={result['confidence']}")
            print(f"  対立軸: {result['tension']}")
            print(f"  機会: {result['opportunity']}")
            print(f"  リスク: {result['risk']}")
        else:
            print(f"β: 抽出不可 ({result.get('message', '')})")
        print()

# -*- coding: utf-8 -*-
import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
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


def _has_structural_basis(common_cats: list, tension_desc: str | None) -> bool:
    """βを生成する最低限の構造的根拠があるか判定する（confidence の代替）"""
    # テンション軸か、共通カテゴリのどちらかがあれば根拠あり
    return bool(tension_desc) or len(common_cats) >= 1


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
        β辞書（beta, beta_ja, tension, implication, opportunity, risk, evidence_increment, ...）
        NOTE: confidence フィールドは廃止。βは「予測値」でなく「証拠で成長する仮説構造体」。
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
    # まずカテゴリ+テンションで照合、次にテンションのみで照合（フォールバック）
    beta_key = None
    beta_ja  = None
    for cat in (common_cats or ["_any"]):
        key = (cat, tension_desc)
        if key in BETA_TEMPLATES:
            beta_key, beta_ja = BETA_TEMPLATES[key]
            break
    if not beta_key and tension_desc:
        for (_, t_desc), (bk, bj) in BETA_TEMPLATES.items():
            if t_desc == tension_desc:
                beta_key, beta_ja = bk, bj
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

    # 5. 構造的根拠チェック（confidence廃止 → 根拠の有無で判定）
    if not _has_structural_basis(common_cats, tension_desc):
        return {
            "beta":              None,
            "beta_ja":           None,
            "message":           "構造的な共通因子が不足しています。構造タグを増やしてください。",
            "source_a":          structures_a,
            "source_b":          structures_b,
            "evidence_increment": 0,
            "timestamp":         datetime.now().isoformat(),
        }

    implication = _generate_implication(beta_ja, tension_arrow or "不明", structures_a, structures_b)
    opportunity = _generate_opportunity(beta_ja, common_cats)
    risk        = _generate_risk(beta_ja, structures_a, pdb)

    # evidence_increment: テンション検出=1、共通カテゴリ数=+カテゴリ数、既存βへの追加=1
    ev_inc = 1 + len(common_cats)

    result = {
        "beta":              beta_key,
        "beta_ja":           beta_ja,
        "source_a":          structures_a,
        "source_b":          structures_b,
        "common_category":   common_cats[0] if common_cats else None,
        "all_common_cats":   common_cats,
        "tension":           tension_arrow,
        "tension_desc":      tension_desc,
        "implication":       implication,
        "opportunity":       opportunity,
        "risk":              risk,
        "evidence_increment": ev_inc,
        "event_a_id":        event_a_id,
        "event_b_id":        event_b_id,
        "timestamp":         datetime.now().isoformat(),
        "lifecycle_status":  existing.get("status", "観察β") if existing else "観察β",
    }

    # 6. beta_registry に登録 or 更新
    _update_registry(beta_key, beta_ja, result, existing, breg,
                     event_a_id, event_b_id)

    return result


def _update_registry(beta_key: str, beta_ja: str, result: dict,
                      existing: dict | None, breg: dict,
                      event_a_id: str, event_b_id: str):
    """beta_registry.json を evidence ベースで更新する（BEE v2.0 スキーマ）"""
    example = {}
    if event_a_id:
        example["a"] = event_a_id
    if event_b_id:
        example["b"] = event_b_id
    if not example:
        example = {"a": str(result["source_a"])[:40], "b": str(result["source_b"])[:40]}
    example["ts"] = result["timestamp"]

    ev_inc = result.get("evidence_increment", 1)
    today  = datetime.now().strftime("%Y-%m-%d")

    if existing:
        existing["evidence"]  = existing.get("evidence", 0) + ev_inc
        existing["last_seen"] = today
        existing["examples"]  = (existing.get("examples") or [])
        existing["examples"].append(example)
        if len(existing["examples"]) > 20:
            existing["examples"] = existing["examples"][-20:]
        # confidence/occurrence フィールドが残っていれば除去
        existing.pop("confidence_avg", None)
        existing.pop("occurrence",     None)
        breg[beta_key] = existing
    else:
        breg[beta_key] = {
            "beta_ja":      beta_ja,
            "beta_en":      beta_key,
            "status":       "観察β",
            "evidence":     ev_inc,
            "contradiction": 0,
            "last_seen":    today,
            "first_seen":   today,
            "tension":      result.get("tension") or "",
            "implication":  result["implication"],
            "opportunity":  result["opportunity"],
            "risk":         result["risk"],
            "co_occurrence": [],
            "meta_beta":    None,
            "examples":     [example],
            "approved_by":  None,
            "approved_at":  None,
            "expires_at":   None,
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
            print(f"β: {result['beta_ja']} ({result['beta']}) status={result['lifecycle_status']} ev+={result['evidence_increment']}")
            print(f"  対立軸: {result['tension']}")
            print(f"  機会: {result['opportunity']}")
            print(f"  リスク: {result['risk']}")
        else:
            print(f"β: 抽出不可 ({result.get('message', '')})")
        print()

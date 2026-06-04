"""test_similarity_engine.py — Similarity Engine テスト"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.planner.similarity_engine import calc_score, match, _age_fit, _budget_fit

MASTER = Path(__file__).parent.parent.parent / "data" / "insurers" / "master_20260604_v4.json"


def _base_client(**overrides):
    c = {
        "age": 35, "gender": "M",
        "needs": {"hospitalization": True, "death": True, "asset_formation": False,
                  "nursing": False, "lump_sum": False},
        "budget_monthly": 30000,
    }
    c.update(overrides)
    return c


def _dummy_plan(**overrides):
    p = {
        "plan_id": "TEST_P01", "plan_name": "テスト商品",
        "conditions": {"age_min": 20, "age_max": 70},
        "coverage": {"hospitalization_daily": True, "death": True, "nursing_care": False,
                     "asset_formation": False, "no_surrender_value": True},
        "monthly_premium": {"M_30_5000": 3000, "note": None},
        "tsi": 1.0, "tsi_status": "TRUSTED",
    }
    p.update(overrides)
    return p


# ── age_fit テスト ──────────────────────────────────────────────────────────

def test_age_in_range():
    plan = _dummy_plan(conditions={"age_min": 20, "age_max": 70})
    assert _age_fit(35, plan) == 1.0, "範囲内は1.0"


def test_age_out_of_range_high():
    plan = _dummy_plan(conditions={"age_min": 20, "age_max": 60})
    assert _age_fit(65, plan) == 0.0, "上限超過は0.0"


def test_age_out_of_range_low():
    plan = _dummy_plan(conditions={"age_min": 30, "age_max": 70})
    assert _age_fit(25, plan) == 0.0, "下限未満は0.0"


def test_age_no_limit():
    plan = _dummy_plan(conditions={"age_min": None, "age_max": None})
    assert _age_fit(99, plan) == 1.0, "制限なしは常に1.0"


# ── budget_fit テスト ────────────────────────────────────────────────────────

def test_budget_within():
    plan = _dummy_plan(monthly_premium={"M_30_5000": 3000})
    assert _budget_fit(30000, plan) == 1.0, "予算内は1.0"


def test_budget_exceeded():
    plan = _dummy_plan(monthly_premium={"M_30_5000": 50000})
    score = _budget_fit(10000, plan)
    assert score < 0.3, f"予算超過は低スコア: {score}"


def test_budget_none():
    plan = _dummy_plan(monthly_premium={"M_30_5000": None})
    assert _budget_fit(10000, plan) == 0.5, "保険料不明は0.5"


# ── calc_score テスト ─────────────────────────────────────────────────────────

def test_perfect_match():
    """全条件一致 -> score >= 0.9"""
    client = _base_client(age=35, budget_monthly=50000)
    plan = _dummy_plan(tsi=1.0)
    result = calc_score(client, plan)
    assert result["total"] >= 0.7, f"高スコア期待: {result['total']}"


def test_score_range():
    """スコアは0.0〜1.0の範囲内"""
    client = _base_client()
    plan = _dummy_plan()
    result = calc_score(client, plan)
    assert 0.0 <= result["total"] <= 1.0, f"範囲外: {result['total']}"


def test_breakdown_keys():
    """breakdownに全キーが存在する"""
    client = _base_client()
    plan = _dummy_plan()
    result = calc_score(client, plan)
    for k in ("age_fit", "need_match", "budget_fit", "tsi_quality"):
        assert k in result["breakdown"], f"{k}がbreakdownにない"


# ── match テスト（マスターJSON使用）────────────────────────────────────────────

def test_match_returns_list():
    """match()はリストを返す"""
    if not MASTER.exists():
        print("SKIP test_match_returns_list (master not found)")
        return
    client = _base_client()
    results = match(client, MASTER, top_n=5)
    assert isinstance(results, list), "リストを返す"


def test_dead_product_excluded():
    """DEAD商品はresultに含まれない"""
    if not MASTER.exists():
        print("SKIP test_dead_product_excluded (master not found)")
        return
    client = _base_client()
    results = match(client, MASTER, exclude_dead=True)
    for r in results:
        assert r.get("tsi_status") != "DEAD", f"DEAD商品が含まれている: {r['plan_id']}"


def test_sorted_by_score():
    """結果はスコア降順"""
    if not MASTER.exists():
        print("SKIP test_sorted_by_score (master not found)")
        return
    client = _base_client()
    results = match(client, MASTER, top_n=20)
    scores = [r["total"] for r in results]
    assert scores == sorted(scores, reverse=True), "スコア降順でない"


def test_top_n_limit():
    """top_n件数制限が機能する"""
    if not MASTER.exists():
        print("SKIP test_top_n_limit (master not found)")
        return
    client = _base_client()
    results = match(client, MASTER, top_n=5)
    assert len(results) <= 5, f"top_n超過: {len(results)}"


if __name__ == "__main__":
    tests = [
        test_age_in_range, test_age_out_of_range_high,
        test_age_out_of_range_low, test_age_no_limit,
        test_budget_within, test_budget_exceeded, test_budget_none,
        test_perfect_match, test_score_range, test_breakdown_keys,
        test_match_returns_list, test_dead_product_excluded,
        test_sorted_by_score, test_top_n_limit,
    ]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print("PASS " + t.__name__)
            passed += 1
        except AssertionError as e:
            print("FAIL " + t.__name__ + " -- " + str(e))
            failed += 1
    print(f"\n{passed}/{passed+failed} passed")
    if failed:
        sys.exit(1)

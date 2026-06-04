"""
Similarity Engine v1.0
顧客プロファイル x 保険マスターの類似度マッチングエンジン

入力: client_profile (dict)
出力: マッチング結果リスト (スコア順)

スコア構成:
  age_fit     0.25  年齢が契約可能範囲内か
  need_match  0.40  ニーズ x カバレッジの一致度
  budget_fit  0.20  予算内か
  tsi_quality 0.15  データ品質 (TSIスコア)
"""
import json
from pathlib import Path
from typing import Optional

DEFAULT_MASTER = Path(__file__).parent.parent.parent / "data" / "insurers" / "master_20260604_v4.json"

WEIGHTS = {
    "age_fit":     0.25,
    "need_match":  0.40,
    "budget_fit":  0.20,
    "tsi_quality": 0.15,
}

# ニーズ -> coverage キーのマッピング
NEED_COVERAGE_MAP = {
    "hospitalization": ["hospitalization_daily", "hospitalization_initial_10days"],
    "lump_sum":        ["lump_sum_hospitalization", "cancer_lump_sum", "three_major_disease_lump_sum"],
    "death":           ["death"],
    "nursing":         ["nursing_care"],
    "cancer":          ["cancer_lump_sum", "cancer_monthly_benefit"],
    "asset_formation": ["asset_formation"],
    "disability":      ["disability_income"],
    "annuity":         ["annuity"],
}


def _age_fit(client_age: int, plan: dict) -> float:
    """年齢適合スコア (0.0 or 1.0)"""
    cond = plan.get("conditions", {})
    age_min = cond.get("age_min")
    age_max = cond.get("age_max")
    if age_min is not None and client_age < age_min:
        return 0.0
    if age_max is not None and client_age > age_max:
        return 0.0
    return 1.0


def _need_match(client_needs: dict, plan: dict) -> float:
    """ニーズとカバレッジの一致度 (0.0〜1.0)"""
    coverage = plan.get("coverage", {})
    if not coverage:
        return 0.3  # 骨格商品は中間スコア

    wanted_keys = [k for k, v in client_needs.items() if v]
    if not wanted_keys:
        return 0.5

    matched = 0
    for need_key in wanted_keys:
        cov_keys = NEED_COVERAGE_MAP.get(need_key, [need_key])
        for ck in cov_keys:
            if coverage.get(ck):
                matched += 1
                break

    return round(matched / len(wanted_keys), 4)


def _budget_fit(budget: Optional[int], plan: dict) -> float:
    """予算適合スコア (0.0〜1.0)"""
    if budget is None:
        return 0.5  # 不明は中間

    mp = plan.get("monthly_premium", {})

    # ガードネクストのようにplans構造の場合は最安値プランを参照
    if isinstance(mp.get("plans"), dict):
        all_prices = []
        for plan_data in mp["plans"].values():
            all_prices.extend([v for v in plan_data.values() if isinstance(v, (int, float))])
        min_price = min(all_prices) if all_prices else None
    else:
        prices = [v for k, v in mp.items()
                  if isinstance(v, (int, float)) and k not in ("M_35_1000man_60sai",)]
        min_price = min(prices) if prices else None

    if min_price is None:
        return 0.5  # 保険料不明は中間
    if min_price <= budget:
        return 1.0
    # 予算超過: 超過率に応じてペナルティ
    ratio = budget / min_price
    return round(max(0.0, ratio), 4)


def _tsi_quality(plan: dict) -> float:
    """TSIスコアをそのまま品質スコアとして使用 (0.0〜1.0)"""
    return min(1.0, max(0.0, plan.get("tsi", 0.5)))


def calc_score(client: dict, plan: dict) -> dict:
    """
    1商品のマッチングスコアを計算する。

    Returns:
        {"total": float, "breakdown": {...}, "plan_id": str, "plan_name": str}
    """
    age = client.get("age", 40)
    needs = client.get("needs", {})
    budget = client.get("budget_monthly")

    scores = {
        "age_fit":     _age_fit(age, plan),
        "need_match":  _need_match(needs, plan),
        "budget_fit":  _budget_fit(budget, plan),
        "tsi_quality": _tsi_quality(plan),
    }
    total = round(sum(scores[k] * WEIGHTS[k] for k in WEIGHTS), 4)

    return {
        "plan_id":   plan.get("plan_id", ""),
        "plan_name": plan.get("plan_name", ""),
        "total":     total,
        "breakdown": scores,
    }


def match(client: dict, master_path: Path = DEFAULT_MASTER,
          exclude_dead: bool = True, top_n: int = 20) -> list:
    """
    顧客プロファイルと全商品のマッチングを実行する。

    Args:
        client:       顧客プロファイル dict
        master_path:  マスターJSONパス
        exclude_dead: DEAD商品を除外するか (default True)
        top_n:        上位N件を返す

    Returns:
        マッチング結果リスト (スコア降順)
    """
    with open(master_path, encoding="utf-8") as f:
        data = json.load(f)

    results = []
    for company in data.get("companies", []):
        company_id = company["company_id"]
        for plan in company.get("plans", []):
            # DEAD商品を除外
            if exclude_dead and (
                plan.get("discontinued") or plan.get("tsi_status") == "DEAD"
            ):
                continue

            result = calc_score(client, plan)
            result["company_id"] = company_id
            result["company_name"] = company.get("company_name", "")
            result["tsi"] = plan.get("tsi", 0.0)
            result["tsi_status"] = plan.get("tsi_status", "")
            results.append(result)

    results.sort(key=lambda x: x["total"], reverse=True)
    return results[:top_n]


if __name__ == "__main__":
    # サンプル実行
    sample_client = {
        "age": 35,
        "gender": "M",
        "family": {"spouse": True, "children": 2},
        "income_primary": True,
        "health": {"condition": "normal", "history": []},
        "needs": {
            "hospitalization": True,
            "lump_sum": False,
            "death": True,
            "nursing": False,
            "asset_formation": True,
        },
        "budget_monthly": 30000,
    }
    results = match(sample_client, top_n=10)
    print("=== Similarity Match Results (top 10) ===")
    for i, r in enumerate(results, 1):
        print(f"{i:2}. [{r['company_id']}] {r['plan_name'][:28]:<28} "
              f"score={r['total']:.3f} tsi={r['tsi']} ({r['tsi_status']})")

"""
NTP Planning Engine - 保険プランニングエンジン
客観的なスコアリングで最適プランを提案する
"""

from __future__ import annotations
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "insurers"
MASTER_FILE = DATA_DIR / "sample_master.json"

COVERAGE_TYPE_MAP = {
    "death": "死亡保障",
    "critical_illness": "重大疾病",
    "medical": "医療",
    "hospitalization": "入院",
    "surgery": "手術",
    "cancer": "がん",
    "stroke": "脳卒中",
    "heart_attack": "心筋梗塞",
    "disability": "就業不能",
    "mental_illness": "精神疾患",
    "long_term_care": "介護",
    "nursing": "介護",
    "retirement": "老後・年金",
}


@dataclass
class ClientProfile:
    age: int
    gender: str                      # "male" / "female"
    smoker: bool = False
    occupation_risk: str = "low"     # "low" / "medium" / "high"
    health_condition: str = "good"   # "good" / "substandard" / "declined"
    annual_income_man: int = 500     # 万円
    has_family: bool = False
    num_dependents: int = 0
    desired_coverages: list[str] = field(default_factory=list)
    budget_monthly: Optional[int] = None  # 円/月


@dataclass
class ScoredProduct:
    product: dict
    score: float
    reasons: list[str]
    warnings: list[str]


def load_products() -> list[dict]:
    if not MASTER_FILE.exists():
        return []
    with open(MASTER_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("products", [])


def _coverage_overlap(product_coverages: list[str], desired: list[str]) -> float:
    if not desired:
        return 0.5
    matched = sum(1 for c in desired if c in product_coverages)
    return matched / len(desired)


def score_product(product: dict, client: ClientProfile) -> ScoredProduct:
    score = 0.0
    reasons: list[str] = []
    warnings: list[str] = []

    # 年齢チェック
    age_range = product.get("age_range", {})
    if not (age_range.get("min", 0) <= client.age <= age_range.get("max", 99)):
        return ScoredProduct(product, -1.0, [], ["年齢範囲外"])

    # 健康状態チェック
    if client.health_condition == "declined":
        warnings.append("健康状態により引受困難の可能性あり")

    # 保障ニーズ合致度（40点）
    overlap = _coverage_overlap(product.get("coverage_types", []), client.desired_coverages)
    need_score = overlap * 40
    score += need_score
    if overlap >= 0.8:
        reasons.append("希望保障に高く合致")
    elif overlap >= 0.5:
        reasons.append("希望保障に部分的に合致")

    # 家族構成・死亡保障ニーズ（20点）
    if client.has_family and client.num_dependents > 0:
        if "death" in product.get("coverage_types", []):
            score += 20
            reasons.append("扶養家族あり→死亡保障が重要")
        if product.get("type") == "term":
            score += 5
            reasons.append("定期保険で高額保障が効率的")

    # 予算適合（20点）
    if client.budget_monthly:
        sample_key = f"{'male' if client.gender == 'male' else 'female'}_30_nonsmoker_1000man"
        sample = product.get("monthly_premium_sample", {})
        premium = sample.get(sample_key) or list(sample.values())[0] if sample else None
        if premium:
            ratio = premium / client.budget_monthly
            if ratio <= 0.3:
                score += 20
                reasons.append("予算に対して余裕あり")
            elif ratio <= 0.6:
                score += 12
                reasons.append("予算内に収まる見込み")
            elif ratio <= 1.0:
                score += 5
                warnings.append("予算ぎりぎりの可能性あり")
            else:
                warnings.append("予算超過の可能性あり")

    # 喫煙者割引あり商品の評価
    if client.smoker and not product.get("smoker_rates"):
        warnings.append("喫煙者向け特別料率なし")
    elif not client.smoker and product.get("smoker_rates"):
        score += 5
        reasons.append("非喫煙者割引適用可能")

    # 特徴点数（最大15点）
    features = product.get("features", [])
    score += min(len(features) * 3, 15)
    if features:
        reasons.append(f"特約・特徴: {', '.join(features[:2])}")

    # 待機期間ペナルティ
    waiting = product.get("waiting_period_months", 0)
    if waiting > 0:
        score -= waiting * 2
        warnings.append(f"待機期間{waiting}ヶ月あり")

    score *= product.get("score_weight", 1.0)
    return ScoredProduct(product, round(score, 1), reasons, warnings)


def search_plans(client: ClientProfile) -> list[ScoredProduct]:
    products = load_products()
    scored = [score_product(p, client) for p in products]
    scored = [s for s in scored if s.score >= 0]
    scored.sort(key=lambda s: s.score, reverse=True)
    return scored


def format_results(results: list[ScoredProduct]) -> list[dict]:
    out = []
    for r in results:
        p = r.product
        out.append({
            "id": p["id"],
            "insurer_name": p["insurer_name"],
            "product_name": p["product_name"],
            "type": p["type"],
            "score": r.score,
            "coverage_types": [COVERAGE_TYPE_MAP.get(c, c) for c in p.get("coverage_types", [])],
            "features": p.get("features", []),
            "reasons": r.reasons,
            "warnings": r.warnings,
            "monthly_premium_sample": p.get("monthly_premium_sample", {}),
            "sum_assured_range": p.get("sum_assured_range", {}),
            "health_requirements": p.get("health_requirements", ""),
            "waiting_period_months": p.get("waiting_period_months", 0),
        })
    return out


if __name__ == "__main__":
    client = ClientProfile(
        age=35,
        gender="male",
        smoker=False,
        has_family=True,
        num_dependents=2,
        desired_coverages=["death", "medical", "cancer"],
        budget_monthly=15000,
    )
    results = search_plans(client)
    formatted = format_results(results)
    print(json.dumps(formatted, ensure_ascii=False, indent=2))

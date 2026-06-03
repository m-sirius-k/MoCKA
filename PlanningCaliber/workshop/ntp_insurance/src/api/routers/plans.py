from fastapi import APIRouter
from src.api.models.schemas import ClientProfileRequest, PlanSearchResponse
from src.planner.engine import ClientProfile, search_plans, format_results

router = APIRouter(prefix="/api/plans", tags=["plans"])


@router.post("/search", response_model=PlanSearchResponse)
def search_insurance_plans(req: ClientProfileRequest):
    client = ClientProfile(
        age=req.age,
        gender=req.gender,
        smoker=req.smoker,
        occupation_risk=req.occupation_risk,
        health_condition=req.health_condition,
        annual_income_man=req.annual_income_man,
        has_family=req.has_family,
        num_dependents=req.num_dependents,
        desired_coverages=req.desired_coverages,
        budget_monthly=req.budget_monthly,
    )
    results = search_plans(client)
    formatted = format_results(results)

    return PlanSearchResponse(
        client_summary={
            "age": req.age,
            "gender": "男性" if req.gender == "male" else "女性",
            "smoker": req.smoker,
            "has_family": req.has_family,
            "num_dependents": req.num_dependents,
            "budget_monthly": req.budget_monthly,
        },
        results=formatted,
        total=len(formatted),
    )

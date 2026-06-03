from pydantic import BaseModel, Field
from typing import Optional


class ClientProfileRequest(BaseModel):
    age: int = Field(..., ge=0, le=99, description="年齢")
    gender: str = Field(..., pattern="^(male|female)$", description="性別: male / female")
    smoker: bool = Field(False, description="喫煙者フラグ")
    occupation_risk: str = Field("low", pattern="^(low|medium|high)$", description="職業リスク")
    health_condition: str = Field("good", pattern="^(good|substandard|declined)$")
    annual_income_man: int = Field(500, ge=0, description="年収（万円）")
    has_family: bool = Field(False, description="家族有無")
    num_dependents: int = Field(0, ge=0, description="扶養家族数")
    desired_coverages: list[str] = Field(default_factory=list, description="希望保障種類リスト")
    budget_monthly: Optional[int] = Field(None, ge=0, description="月額予算（円）")


class ProductSummary(BaseModel):
    id: str
    insurer_name: str
    product_name: str
    type: str
    score: float
    coverage_types: list[str]
    features: list[str]
    reasons: list[str]
    warnings: list[str]
    monthly_premium_sample: dict
    sum_assured_range: dict
    health_requirements: str
    waiting_period_months: int


class PlanSearchResponse(BaseModel):
    client_summary: dict
    results: list[ProductSummary]
    total: int


class InsurerInfo(BaseModel):
    id: str
    name: str
    short_name: str
    url: str
    enabled: bool


class HealthResponse(BaseModel):
    status: str
    version: str
    products_loaded: int

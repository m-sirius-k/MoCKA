"""
NTP API Server - Phase 2
FastAPI バックエンド: http://localhost:8400

起動: python -m uvicorn src.api.main:app --reload --port 8400
または start_api.bat をダブルクリック
"""

import sys
from pathlib import Path

# プロジェクトルートをPATHに追加（NTPフォルダから実行できるように）
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import plans, insurers
from src.api.models.schemas import HealthResponse
from src.planner.engine import load_products

app = FastAPI(
    title="NTP - 保険プランニングAPI",
    description="FP向け保険比較・プランニング支援 REST API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# file:// から開いたindex.htmlのCORSを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(plans.router)
app.include_router(insurers.router)


@app.get("/api/health", response_model=HealthResponse, tags=["system"])
def health_check():
    products = load_products()
    return HealthResponse(
        status="ok",
        version="2.0.0",
        products_loaded=len(products),
    )


@app.get("/", include_in_schema=False)
def root():
    return {"message": "NTP API is running. See /docs for API reference."}

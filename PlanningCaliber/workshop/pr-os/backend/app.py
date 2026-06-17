"""
app.py — PR-OS FastAPI
API固定3エンドポイント。これ以外追加禁止。
GET  /api/events
GET  /api/caliber
POST /api/action/{action}
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import events as ev
import executor as ex

app = FastAPI(title="PR-OS Command Center API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class ActionRequest(BaseModel):
    payload: dict = {}


# ── エンドポイント1: イベント一覧 ──
@app.get("/api/events")
def get_events(limit: int = 50):
    """最新イベントを返す。ファイルが壊れても空配列を返す（クラッシュしない）。"""
    try:
        items = ev.read_all(limit=limit)
        return {"events": items, "total": ev.count()}
    except Exception:
        return {"events": [], "total": 0}


# ── エンドポイント2: Caliber状態 ──
@app.get("/api/caliber")
def get_caliber():
    """Caliberスコアと要約を返す。"""
    try:
        total = ev.count()
        items = ev.read_all(limit=10)
        success = sum(1 for e in items if e.get("status") == "success")
        score = round(success / max(len(items), 1), 2)
        return {
            "score": score,
            "total_events": total,
            "recent_success_rate": score,
        }
    except Exception:
        return {"score": 0.0, "total_events": 0, "recent_success_rate": 0.0}


# ── エンドポイント3: アクション実行 ──
@app.post("/api/action/{action}")
def run_action(action: str, req: ActionRequest):
    """
    ホワイトリスト内のアクションを実行する。
    allowed: evaluate / submit / publish / sync
    """
    result = ex.run(action=action, payload=req.payload)
    if result.get("status") == "failed":
        # 失敗してもクラッシュさせない（200で返してUIに任せる）
        return result
    return result


# ── ヘルスチェック ──
@app.get("/health")
def health():
    return {"status": "ok", "service": "pr-os-command-center"}

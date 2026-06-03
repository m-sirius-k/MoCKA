import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from src.api.models.schemas import InsurerInfo

router = APIRouter(prefix="/api/insurers", tags=["insurers"])

CONFIG_FILE = Path(__file__).parent.parent.parent.parent / "config" / "insurers.json"


def _load_insurers() -> list[dict]:
    if not CONFIG_FILE.exists():
        return []
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f).get("insurers", [])


@router.get("", response_model=list[InsurerInfo])
def list_insurers():
    return _load_insurers()


@router.get("/{insurer_id}", response_model=InsurerInfo)
def get_insurer(insurer_id: str):
    insurers = _load_insurers()
    for ins in insurers:
        if ins["id"] == insurer_id:
            return ins
    raise HTTPException(status_code=404, detail=f"Insurer '{insurer_id}' not found")

from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

def read_bytes(path: str | Path) -> bytes:
    p = Path(path)
    return p.read_bytes()

def write_bytes(path: str | Path, data: bytes) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)

def canonical_dumps(obj: Dict[str, Any]) -> str:
    # Canonical JSON: sorted keys, no spaces
    return json.dumps(obj, separators=(",", ":"), sort_keys=True, ensure_ascii=False)

def canonical_bytes(obj: Dict[str, Any]) -> bytes:
    return canonical_dumps(obj).encode("utf-8")

def canonical_loads(b: bytes) -> Dict[str, Any]:
    return json.loads(b.decode("utf-8"))
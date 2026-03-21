import json
from pathlib import Path

base = Path(__file__).resolve().parents[1]
acc = base / "acceptance"

rows = []
for p in sorted(acc.glob("*_pass.json")):
    try:
        j = json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception:
        j = json.loads(p.read_text(encoding="utf-8"))
    rows.append({
        "file": p.name,
        "overall_status": j.get("overall_status"),
        "started_utc": j.get("started_utc"),
    })

matrix = {
    "generated_at_utc": "AUTO",
    "count": len(rows),
    "rows": rows,
}

(acc / "summary_matrix.json").write_text(json.dumps(matrix, indent=2), encoding="utf-8")
print("WROTE:", acc / "summary_matrix.json")

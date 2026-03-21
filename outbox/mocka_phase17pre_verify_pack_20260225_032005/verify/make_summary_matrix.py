import json
from pathlib import Path
from datetime import datetime, timezone

def utc_now_z():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def read_text(path: Path):
    return path.read_text(encoding="utf-8-sig")

def main():
    base = Path(__file__).resolve().parents[1]
    acc = base / "acceptance"

    rows = []
    for p in sorted(acc.glob("*_pass.json")):
        try:
            j = read_json(p)
        except Exception:
            j = json.loads(p.read_text(encoding="utf-8"))
        rows.append({
            "file": p.name,
            "overall_status": j.get("overall_status"),
            "started_utc": j.get("started_utc"),
        })

    pack_info_path = acc / "phase17pre_pack_sha256.txt"
    pack = None
    if pack_info_path.exists():
        lines = [ln.strip() for ln in read_text(pack_info_path).splitlines() if ln.strip()]
        d = {}
        for ln in lines:
            if "=" in ln:
                k, v = ln.split("=", 1)
                d[k.strip()] = v.strip()
        if d:
            pack = d

    matrix = {
        "generated_at_utc": utc_now_z(),
        "count": len(rows),
        "rows": rows,
        "external_pack": pack,
    }

    out = acc / "summary_matrix.json"
    out.write_text(json.dumps(matrix, indent=2), encoding="utf-8")
    print("WROTE:", out)

if __name__ == "__main__":
    main()

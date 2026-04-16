import json
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parents[1]
ACC = BASE_DIR / "acceptance"
PACK_INFO = ACC / "phase17pre_pack_sha256.txt"

def utc_now_z():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def read_text_any(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except Exception:
        return path.read_text(encoding="utf-8")

def read_json(path: Path):
    return json.loads(read_text_any(path))

def read_pack_info():
    if not PACK_INFO.exists():
        return None
    d = {}
    for ln in read_text_any(PACK_INFO).splitlines():
        t = ln.strip()
        if not t or "=" not in t:
            continue
        k, v = t.split("=", 1)
        d[k.strip()] = v.strip()
    if "zip_name" in d or "sha256" in d or "generated_utc" in d:
        return {
            "zip_name": d.get("zip_name"),
            "sha256": d.get("sha256"),
            "generated_utc": d.get("generated_utc"),
        }
    return None

def is_internal_pass_file(p: Path) -> bool:
    name = p.name
    if not name.endswith("_pass.json"):
        return False
    if name.startswith("TEMPLATE_"):
        return False
    if name.endswith("_outfield_pass.json"):
        return False
    return True

def is_outfield_pass_file(p: Path) -> bool:
    name = p.name
    if not name.endswith("_outfield_pass.json"):
        return False
    if name.startswith("TEMPLATE_"):
        return False
    return True

def main():
    ACC.mkdir(exist_ok=True)

    rows_internal = []
    rows_outfield = []

    # acceptance/ 直下のみを対象（quarantine 配下は glob されない）
    for p in sorted(ACC.glob("*.json")):
        if is_internal_pass_file(p):
            j = read_json(p)
            rows_internal.append({
                "file": p.name,
                "kind": "internal",
                "overall_status": j.get("overall_status"),
                "started_utc": j.get("started_utc"),
            })
        elif is_outfield_pass_file(p):
            j = read_json(p)
            env = j.get("environment") or {}
            pack = j.get("pack") or {}
            res = j.get("result") or {}
            rows_outfield.append({
                "file": p.name,
                "kind": "outfield",
                "pack_zip_name": pack.get("zip_name"),
                "pack_sha256": pack.get("sha256"),
                "os": env.get("os"),
                "python": env.get("python"),
                "machine": env.get("machine"),
                "submitted_utc": j.get("submitted_utc"),
                "overall_status": res.get("overall_status"),
                "started_utc": res.get("started_utc"),
                "run_id": j.get("run_id"),
            })

    matrix = {
        "generated_at_utc": utc_now_z(),
        "count_internal": len(rows_internal),
        "count_outfield": len(rows_outfield),
        "rows_internal": rows_internal,
        "rows_outfield": rows_outfield,
        "external_pack": read_pack_info(),
    }

    out = ACC / "summary_matrix.json"
    out.write_text(json.dumps(matrix, indent=2), encoding="utf-8")
    print("WROTE:", out)

if __name__ == "__main__":
    main()

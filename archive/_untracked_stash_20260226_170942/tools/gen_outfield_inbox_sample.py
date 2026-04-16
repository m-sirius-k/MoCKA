import json
from datetime import datetime, timezone

OUT = r"acceptance\inbox\sample_linux_py312_outfield_pass.json"

def utc_now_z():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

row = {
  "file": "sample_linux_py312_outfield_pass.json",
  "kind": "outfield",
  "pack_zip_name": "mocka_phase17pre_verify_pack_20260225_032005.zip",
  "pack_sha256": "A0221149435F18D7EEC1B63BB4E6059927DBF8F356FA8A1E17DF29CFAE115B78",
  "os": "Linux",
  "python": "3.12",
  "machine": "LINUX_HOST",
  "submitted_utc": utc_now_z(),
  "overall_status": "PASS",
  "started_utc": utc_now_z(),
  "run_id": "linux_py312_test_001"
}

note = [
  "NOTE: sample inbox payload for multi-env acceptance testing.",
  "NOTE: replace machine and run_id with actual values.",
  "NOTE: placeholder tokens are forbidden in submissions."
]

payload = {"note": note, "row_outfield": row}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2, ensure_ascii=True)

print("WROTE:", OUT)
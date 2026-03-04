import json
import re
from pathlib import Path

ROOT = Path(r"C:\Users\sirok\mocka-ecosystem")
REG  = ROOT / "MoCKA" / "tools" / "research_experiments.json"
CANON = ROOT / "_canon" / "docs" / "RESEARCH_MAP.md"
MIRROR = ROOT / "MoCKA" / "canon" / "RESEARCH_MAP.md"

def load_registry_ids():
    j = json.loads(REG.read_text(encoding="utf-8-sig"))
    ids = []
    for e in j.get("experiments", []):
        if isinstance(e, dict):
            eid = str(e.get("id","")).strip()
            if eid:
                ids.append(eid)
    return sorted(set(ids))

def load_map_ids(text: str):
    # "- experiment_id" の行だけ拾う
    out = set()
    for m in re.finditer(r"(?m)^\s*-\s+([A-Za-z0-9_\-]+)\s*$", text):
        out.add(m.group(1).strip())
    return out

def append_entries(path: Path, missing_ids):
    if not missing_ids:
        return

    entry_lines = []
    entry_lines.append("")
    entry_lines.append("")
    entry_lines.append("--------------------------------")
    entry_lines.append("AUTO-ADDED FROM REGISTRY")
    entry_lines.append("--------------------------------")
    entry_lines.append("")
    entry_lines.append("ENGLISH VERSION")
    entry_lines.append("")
    for eid in missing_ids:
        entry_lines.append(f"- {eid}")
        entry_lines.append(f"  - Purpose: registry synchronized entry")
        entry_lines.append(f"  - Script: MoCKA/experiments/exp_{eid}.ps1")
        entry_lines.append("")
    entry_lines.append("日本語版")
    entry_lines.append("")
    for eid in missing_ids:
        entry_lines.append(f"- {eid}")
        entry_lines.append(f"  - 目的: registry との同期で自動追記")
        entry_lines.append(f"  - Script: MoCKA/experiments/exp_{eid}.ps1")
        entry_lines.append("")

    text = path.read_text(encoding="utf-8-sig")
    path.write_text(text + "\n" + "\n".join(entry_lines), encoding="utf-8")

def main():
    reg_ids = load_registry_ids()

    canon_text = CANON.read_text(encoding="utf-8-sig")
    mirror_text = MIRROR.read_text(encoding="utf-8-sig")

    canon_ids = load_map_ids(canon_text)
    mirror_ids = load_map_ids(mirror_text)

    missing_canon = [x for x in reg_ids if x not in canon_ids]
    missing_mirror = [x for x in reg_ids if x not in mirror_ids]

    print("REG_IDS:", len(reg_ids))
    print("MISSING_CANON:", len(missing_canon))
    print("MISSING_MIRROR:", len(missing_mirror))

    append_entries(CANON, missing_canon)
    append_entries(MIRROR, missing_mirror)

    print("SYNC_OK")

if __name__ == "__main__":
    main()

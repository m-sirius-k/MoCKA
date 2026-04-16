import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DICT_PATH = os.path.join(ROOT, "docs", "PHASE15_PROOF_DICTIONARY.md")

BLOCK_CLOSE_BRANCH = r"""
---

### event_type: CLOSE_BRANCH

Target Table:
branch_registry

Deterministic Structure:
- id (INTEGER PRIMARY KEY AUTOINCREMENT)
- created_utc (TEXT NOT NULL)
- tip_event_id (TEXT NOT NULL)
- orphan_event_id (TEXT NULL)
- orphan_prev_id (TEXT NULL)
- classification (TEXT NOT NULL)

Idempotency Rule:
No-op (branch_registry has no close marker column).

Conflict Resolution:
Emit mismatch if governance emits CLOSE_BRANCH but no proof close-state exists.
Do not apply.

Reversibility:
Not applicable (no mutation).

Hash Stability:
No hash column. No mutation.
""".lstrip("\n")

BLOCK_ANCHOR_PROOF = r"""
---

### event_type: ANCHOR_PROOF

Target Table:
proof_anchor

Deterministic Structure:
- anchor_id (TEXT PRIMARY KEY)
- governance_event_id (TEXT NOT NULL)
- anchor_hash (TEXT NOT NULL)
- created_utc (TEXT NOT NULL)

Idempotency Rule:
INSERT OR IGNORE by anchor_id

Conflict Resolution:
If target table is missing -> mismatch (do not apply).
If existing row hash differs -> mismatch (do not apply).

Reversibility:
DELETE WHERE anchor_id = ? (only if created by current reconciliation attempt)

Hash Stability:
anchor_hash = SHA256(governance_event_id + anchor_id)
""".lstrip("\n")

def normalize(md: str) -> str:
    # same normalization as reconcile_diff
    md = re.sub(r"\\([#*\-])", r"\1", md)
    md = md.replace("\\_", "_")
    md = md.replace("竊・", " ")
    return md

def has_event_type(md: str, et: str) -> bool:
    n = normalize(md)
    return re.search(rf"(?im)^(?:\s*#+\s*)?event_type\s*[:=]\s*{re.escape(et)}\s*$", n) is not None

def main():
    if not os.path.exists(DICT_PATH):
        raise SystemExit(f"NG: dictionary not found: {DICT_PATH}")

    with open(DICT_PATH, "r", encoding="utf-8") as f:
        md = f.read()

    changed = False
    if not has_event_type(md, "CLOSE_BRANCH"):
        md = md.rstrip() + "\n\n" + BLOCK_CLOSE_BRANCH
        changed = True
    if not has_event_type(md, "ANCHOR_PROOF"):
        md = md.rstrip() + "\n\n" + BLOCK_ANCHOR_PROOF
        changed = True

    if changed:
        with open(DICT_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(md.rstrip() + "\n")
        print("OK: appended missing event_type blocks")
    else:
        print("OK: no changes (blocks already present)")

if __name__ == "__main__":
    main()
import json
import sys
import os
from pathlib import Path
from typing import Any, Dict, Tuple

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from verify.row_sign import sign_row_soft

def load_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8-sig"))

def write_json(p: Path, obj: Any) -> None:
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def sign_all_row_dicts(obj: Any, secret: str) -> Tuple[Any, int]:
    count = 0

    def walk(x: Any) -> Any:
        nonlocal count

        if isinstance(x, dict):
            # row_id を持つ dict を row と定義して署名付与
            if "row_id" in x:
                row_copy = dict(x)
                row_copy["row_sig"] = sign_row_soft(row_copy, secret)
                count += 1
                x = row_copy

            # 子要素を再帰
            return {k: walk(v) for k, v in x.items()}

        if isinstance(x, list):
            return [walk(v) for v in x]

        return x

    return walk(obj), count

def main() -> int:
    if len(sys.argv) < 3:
        print("usage: python tools/phase18_sign_pack.py <input_pack.json> <output_pack.json>")
        return 2

    secret = os.environ.get("MOCKA_ROW_SIG_SECRET")
    if not secret:
        print("ERROR: set MOCKA_ROW_SIG_SECRET env first")
        return 2

    inp = Path(sys.argv[1])
    out = Path(sys.argv[2])

    obj = load_json(inp)
    signed_obj, n = sign_all_row_dicts(obj, secret)

    if n <= 0:
        print("FAIL: no dict with row_id was found to sign")
        return 2

    write_json(out, signed_obj)
    print(f"SIGNED_ROWS: {n}")
    print(f"WROTE: {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

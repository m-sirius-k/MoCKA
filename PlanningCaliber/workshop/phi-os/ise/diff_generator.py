# diff_generator.py
from __future__ import annotations
import json
from pathlib import Path
from .schema import InstitutionState

def _load_snapshot(path: Path) -> dict | None:
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def generate_diff(old: dict, new: dict) -> list[dict]:
    """
    2つの State dict を比較し jsonpatch 形式の差分リストを返す。
    外部ライブラリ不使用。トップレベルキーのみ比較（v1仕様）。
    """
    ops = []
    all_keys = set(old) | set(new)
    for key in sorted(all_keys):
        if key not in old:
            ops.append({"op": "add",     "path": f"/{key}", "value": new[key]})
        elif key not in new:
            ops.append({"op": "remove",  "path": f"/{key}"})
        elif old[key] != new[key]:
            ops.append({"op": "replace", "path": f"/{key}", "value": new[key]})
    return ops

def get_diff_since(from_revision: int,
                   snapshots_dir: Path,
                   current_state: InstitutionState) -> dict:
    """
    from_revision から現在の State までの差分を返す。
    差分が100件超の場合は full_state を返す（Snapshot相当）。

    戻り値:
      {
        "type": "diff" | "full",
        "from_revision": int,
        "to_revision": int,
        "to_hash": str,
        "patch": list[dict]  # type=="diff" の場合
        "state": dict        # type=="full" の場合
      }
    """
    current_dict = current_state.to_dict()
    to_rev  = current_state.revision
    to_hash = current_state.state_hash

    # from_revision のスナップショットを探す
    snap_path = snapshots_dir / f"snapshot_R{from_revision}.json"
    old_dict  = _load_snapshot(snap_path)

    # スナップショットがない、または差分が大きすぎる場合は full 返却
    if old_dict is None:
        return {
            "type":          "full",
            "from_revision": from_revision,
            "to_revision":   to_rev,
            "to_hash":       to_hash,
            "state":         current_dict,
        }

    patch = generate_diff(old_dict, current_dict)

    # 差分100件超 → full 返却
    if len(patch) > 100:
        return {
            "type":          "full",
            "from_revision": from_revision,
            "to_revision":   to_rev,
            "to_hash":       to_hash,
            "state":         current_dict,
        }

    return {
        "type":          "diff",
        "from_revision": from_revision,
        "to_revision":   to_rev,
        "to_hash":       to_hash,
        "patch":         patch,
    }

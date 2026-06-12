# snapshot_manager.py
from __future__ import annotations
import json
import gzip
import re
from datetime import datetime, timezone
from pathlib import Path

from .schema import InstitutionState

SNAPSHOT_REVISION_THRESHOLD   = 100   # 100 Revision超
SNAPSHOT_TIME_THRESHOLD_HOURS = 24    # または24時間経過
SNAPSHOT_MAX_GENERATIONS      = 10    # 最新10世代保持

_SNAP_RE = re.compile(r"^snapshot_R(\d+)\.json(\.gz)?$")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def should_create_snapshot(current_rev: int,
                            last_snapshot_rev: int,
                            last_snapshot_time: datetime | None) -> bool:
    """どちらか早い方でスナップショットを生成する。last_snapshot_time=Noneは未生成扱い"""
    rev_exceeded = (current_rev - last_snapshot_rev) >= SNAPSHOT_REVISION_THRESHOLD
    if last_snapshot_time is None:
        time_exceeded = True
    else:
        time_exceeded = (_utcnow() - last_snapshot_time).total_seconds() >= SNAPSHOT_TIME_THRESHOLD_HOURS * 3600
    return rev_exceeded or time_exceeded


def _list_snapshots(snapshots_dir: Path) -> list[tuple[int, Path]]:
    """(revision, path) のリストをrevision降順で返す"""
    out = []
    if not snapshots_dir.exists():
        return out
    for p in snapshots_dir.iterdir():
        m = _SNAP_RE.match(p.name)
        if m:
            out.append((int(m.group(1)), p))
    out.sort(key=lambda t: t[0], reverse=True)
    return out


def get_last_snapshot_info(snapshots_dir: Path) -> tuple[int, datetime]:
    """
    最新スナップショットの (revision, mtime) を返す。
    存在しなければ (0, epoch) を返す。
    """
    snaps = _list_snapshots(snapshots_dir)
    if not snaps:
        return 0, datetime.fromtimestamp(0, tz=timezone.utc)
    rev, path = snaps[0]
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return rev, mtime


def create_snapshot(state: InstitutionState, snapshots_dir: Path) -> Path:
    """
    現在の State をスナップショットとして保存する。
    最新は非圧縮、SNAPSHOT_MAX_GENERATIONSを超えた古い世代はgzip圧縮、
    さらに古い世代は削除する。
    """
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    new_path = snapshots_dir / f"snapshot_R{state.revision}.json"
    with open(new_path, "w", encoding="utf-8") as f:
        json.dump(state.to_dict(), f, ensure_ascii=False, indent=2)

    _rotate_generations(snapshots_dir)
    return new_path


def _rotate_generations(snapshots_dir: Path):
    """
    最新 SNAPSHOT_MAX_GENERATIONS 件は非圧縮で保持し、
    それより古い世代はgzip圧縮、さらにそれを超える世代は削除する。
    （世代数の上限は SNAPSHOT_MAX_GENERATIONS * 2 とし、
      古い圧縮分はそれ以降に削除する）
    """
    snaps = _list_snapshots(snapshots_dir)

    # 最新 N 件は非圧縮のまま
    keep_uncompressed = snaps[:SNAPSHOT_MAX_GENERATIONS]
    older             = snaps[SNAPSHOT_MAX_GENERATIONS:]

    for rev, path in older:
        if path.suffix == ".gz":
            continue
        gz_path = path.with_suffix(path.suffix + ".gz")
        with open(path, "rb") as f_in, gzip.open(gz_path, "wb") as f_out:
            f_out.write(f_in.read())
        path.unlink()

    # 圧縮済みも含めて SNAPSHOT_MAX_GENERATIONS * 2 世代を超えたら削除
    all_snaps = _list_snapshots(snapshots_dir)
    for rev, path in all_snaps[SNAPSHOT_MAX_GENERATIONS * 2:]:
        path.unlink()


def save_snapshot(state_dict: dict, revision: int, snapshots_dir: Path):
    """
    dict形式のStateをスナップショットとして保存する（指示書互換API）。
    最新 SNAPSHOT_MAX_GENERATIONS 件は非圧縮、それより古い世代はgzip圧縮する。
    """
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    snap_path = snapshots_dir / f"snapshot_R{revision}.json"
    with open(snap_path, "w", encoding="utf-8") as f:
        json.dump(state_dict, f, ensure_ascii=False, indent=2)
    _rotate_generations(snapshots_dir)


def load_snapshot(revision: int, snapshots_dir: Path) -> dict | None:
    """指定Revisionのスナップショットを読み込む（gzip対応・指示書互換API）"""
    path    = snapshots_dir / f"snapshot_R{revision}.json"
    gz_path = snapshots_dir / f"snapshot_R{revision}.json.gz"

    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    if gz_path.exists():
        with gzip.open(gz_path, "rt", encoding="utf-8") as f:
            return json.load(f)
    return None


def maybe_create_snapshot(state: InstitutionState, snapshots_dir: Path) -> Path | None:
    """
    Snapshot閾値（100 Revision OR 24時間）を満たしていれば
    スナップショットを生成する。満たしていなければ None を返す。
    """
    last_rev, last_time = get_last_snapshot_info(snapshots_dir)
    if should_create_snapshot(state.revision, last_rev, last_time):
        return create_snapshot(state, snapshots_dir)
    return None

# update_state.py
"""
Institution State を更新するエントリポイント。
MoCKA-START.bat から定期実行される（5分間隔）。

  python -m PlanningCaliber.workshop.phi-os.ise.update_state
  （ハイフンディレクトリのためモジュール実行不可。直接実行する）
  python PlanningCaliber/workshop/phi-os/ise/update_state.py
"""
from __future__ import annotations
import sys
from pathlib import Path

_ISE_DIR  = Path(__file__).resolve().parent
_MOCKA_DIR = _ISE_DIR.parents[3]

if str(_ISE_DIR.parent) not in sys.path:
    sys.path.insert(0, str(_ISE_DIR.parent))

from ise.provider_chain import ProviderChain
from ise.state_provider import DefaultStateProvider
from ise.revision_manager import RevisionStore, update_institution_state
from ise.snapshot_manager import maybe_create_snapshot


def main():
    data_dir = _ISE_DIR / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    snapshots_dir = data_dir / "snapshots"
    snapshots_dir.mkdir(exist_ok=True)

    db_path   = _MOCKA_DIR / "data" / "mocka_events.db"
    todo_path = _MOCKA_DIR / "data" / "MOCKA_TODO.json"

    chain = ProviderChain([DefaultStateProvider(db_path, todo_path)])

    store = RevisionStore(data_dir / "revision_store.json")
    state = update_institution_state(chain, store, data_dir / "current_state.json")

    snap = maybe_create_snapshot(state, snapshots_dir)

    print(f"[ISE] revision={state.revision} hash={state.state_hash[:12]}... "
          f"snapshot={'created:'+snap.name if snap else 'skipped'}")


if __name__ == "__main__":
    main()

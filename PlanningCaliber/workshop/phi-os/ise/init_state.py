# init_state.py
"""
ISE 初回状態生成スクリプト。
実行後は /api/ise/state が 200 OK になる。

実行方法:
  cd C:\\Users\\sirok\\MoCKA
  python PlanningCaliber\\workshop\\phi-os\\ise\\init_state.py
"""
from __future__ import annotations
import sys
from pathlib import Path

_ISE_DIR   = Path(__file__).resolve().parent
_MOCKA_DIR = _ISE_DIR.parents[3]

if str(_ISE_DIR.parent) not in sys.path:
    sys.path.insert(0, str(_ISE_DIR.parent))

from ise.state_provider import DefaultStateProvider
from ise.provider_chain import ProviderChain
from ise.revision_manager import RevisionStore, update_institution_state

DB_PATH   = _MOCKA_DIR / "data" / "mocka_events.db"
TODO_PATH = _MOCKA_DIR / "data" / "MOCKA_TODO.json"
ISE_DATA  = _ISE_DIR / "data"
ISE_DATA.mkdir(parents=True, exist_ok=True)
(ISE_DATA / "snapshots").mkdir(exist_ok=True)


def main():
    provider = ProviderChain([DefaultStateProvider(DB_PATH, TODO_PATH)])
    store    = RevisionStore(ISE_DATA / "revision_store.json")
    state    = update_institution_state(provider, store, ISE_DATA / "current_state.json")
    print(f"[ISE] init_state completed")
    print(f"  revision   : {state.revision}")
    print(f"  state_hash : {state.state_hash[:16]}...")
    print(f"  todos      : {len(state.todos)}")
    print(f"  warnings   : {len(state.warnings)}")
    print(f"  output     : {ISE_DATA / 'current_state.json'}")


if __name__ == "__main__":
    main()

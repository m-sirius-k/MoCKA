# branch_manager.py
# Phase14: Branch & Orphan Management Core

from typing import List, Dict

class BranchManager:

    def detect_orphans(self, ledger_rows: List[Dict]) -> List[str]:
        '''
        Returns list of orphan event_ids.
        NOTE: detection logic to be implemented.
        '''
        return []

    def select_canonical_tip(self, candidates: List[str]) -> str:
        '''
        Deterministic tip selection rule.
        NOTE: longest-chain or highest-weight logic.
        '''
        if not candidates:
            raise ValueError("No candidate tips")
        return candidates[0]

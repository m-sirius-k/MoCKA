import os
import sys
sys.path.insert(0, r"C:\Users\sirok\MoCKA")
from schema.schema import LEDGER_PATH, GENESIS_PREV_HASH, new_event, save_ledger

os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)

if not os.path.exists(LEDGER_PATH):
    genesis = new_event("GENESIS", "INIT", GENESIS_PREV_HASH)
    save_ledger([genesis])
    print("LEDGER INITIALIZED")
else:
    print("LEDGER EXISTS")

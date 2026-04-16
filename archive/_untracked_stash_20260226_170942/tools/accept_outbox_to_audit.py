# FILE: C:\Users\sirok\MoCKA\tools\accept_outbox_to_audit.py
# NOTE: Phase13-B wrapper (delegation to v2 single entry)

import sys
from tools.accept_outbox_to_audit_v2 import main

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
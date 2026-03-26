import sys
sys.path.insert(0, r"C:\Users\sirok\MoCKA")
from schema.schema import verify_ledger

if verify_ledger():
    print("LEDGER OK")
else:
    print("LEDGER ERROR")

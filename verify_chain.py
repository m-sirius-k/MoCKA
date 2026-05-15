import sys
import os

# スクリプト自身の場所からMoCKAルートを自動解決（Windows/Linux共通）
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from schema.schema import verify_ledger
if verify_ledger():
    print("CHAIN OK")
else:
    print("CHAIN ERROR")
    sys.exit(1)

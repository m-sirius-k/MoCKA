# MoCKA 外部検証ガイド

## 1. Ledger検証
python verify_chain.py
→ LEDGER OK

## 2. Governance検証
python verify_all.py
→ ALL CHECKS PASSED

## 3. Caliber検証
python interface/router.py save "verify test" "external verification"
→ events.csvに記録確認

## 4. Router動作確認
python interface/router.py collaborate "verification query"
→ 4AI並列実行・events.csv記録

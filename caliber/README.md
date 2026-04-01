# MoCKA Caliber

MoCKAの外部プログラムを統括する組織。

## 構造
caliber/
  orchestra/   # 共有・協業（4AI並列実行）
  stress/      # ストレステスト
  intercept/   # ネットワーク傍受
  verify/      # 検証系

## 思想
CaliberはMoCKAのApp Storeである。
各caliberは独立したプログラムとして動作し、
router.pyを通じてMoCKAと接続する。

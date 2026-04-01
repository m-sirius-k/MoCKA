# Caliber: Orchestra

4AI並列実行による共有・協業システム。

## 機能
- share:      4AIに一斉送信（返答待たない）
- orchestra:  4AI回収→Claude統合分析

## 実行
python mocka_orchestra_v10.py "プロンプト" share
python mocka_orchestra_v10.py "プロンプト" orchestra

## router連携
router.pyのcollaborate()/share()から自動呼び出し

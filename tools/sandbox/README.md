# MoCKA Tools Sandbox

## 概要
作りかけ・実験中のモジュール置き場。
意図と現状を記録しておくことで、将来の実装時に経緯が分かるようにする。

## 収録ファイル

### ネットワーク傍受モジュール
- `mocka_intercept_v01.py` — 基本傍受テスト
- `mocka_intercept_v02.py` — 会話ID・通信構造の取得成功
- `intercept_log.json` — 傍受ログのサンプル

**現状：** ChatGPTの内部API通信を完全記録できることを実証済み
**保留理由：** MoCKAの記録蓄積が進んでから比較・異常検知に使う
**将来用途：** AIの通信パターン変化検知、セキュリティ監査層

### AI別セレクタ調査
- `mocka_perplexity_test.py` — Perplexity DOM調査
- `mocka_gemini_test.py` — Gemini DOM調査
- `mocka_copilot_test.py` — Copilot DOM調査

**現状：** 各AIの入力欄・回答欄のセレクタ確定済み
**用途：** orchestra_v03.pyに統合済み

### オーケストラ用質疑書
- `orchestra_playwright_query.txt` — Playwright機能評価質疑書
- `orchestra_results.txt` — 4AI回答収集結果

**現状：** 合議完了・Claude統合分析済み
**記録目的：** 初回オーケストラ合議の証跡として保存

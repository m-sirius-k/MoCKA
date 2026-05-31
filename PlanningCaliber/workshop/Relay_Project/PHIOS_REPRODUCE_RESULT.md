# PHIOS_REPRODUCE_RESULT.md

**PHI-OS (Relay v4.1.0) — Proof of Reproducibility**

- 実行日時: 2026-05-31 12:20:28
- 実行環境: Windows 11 / Python 3.13.13
- 対象: Chrome Extension MV3

## 試験結果

| シナリオID | 名称 | 結果 | 詳細 |
|-----------|------|------|------|
| P-S-01-a | ベースライン未設定→CPI=1.0 | PASS | baseline未設定→CPI=1.0 (got 1.0) |
| P-S-01-b | 正常状態→CPI≈1.0 | PASS | 正常状態→CPI≈1.0 (got 1.0) |
| P-S-01-c | 劣化状態→CPI上昇 | PASS | 劣化状態→CPI>1.5 (got 2.0) |
| P-S-01-d | ゼロ除算防止 (vasAI教訓適用) | PASS | ゼロ除算なし (got 1.0) |
| P-S-02-a | light モード T*=12500 | PASS | light: T*=12500 (got 12500) |
| P-S-02-b | heavy モード T*=5000 | PASS | heavy: T*=5000 (got 5000) |
| P-S-02-c | file モード T*=2500 | PASS | file: T*=2500 (got 2500) |
| P-S-02-d | progress計算 (50%) | PASS | progress=0.5 at 2500/5000 (got 0.5) |
| P-S-02-e | オーバーフロー→progress=1.0,margin=0 | PASS | overflow: progress=1.0,margin=0 (got {'T_star': 5000, 'margi |
| P-S-03-a | 低密度→NORMAL | PASS | 低密度→NORMAL (got NORMAL) |
| P-S-03-b | 高密度連続→HIGH_DENSITY | PASS | 高密度→HIGH_DENSITY (got HIGH_DENSITY) |
| P-S-03-c | 急変→TOPIC_SHIFT | PASS | 急落→TOPIC_SHIFT (got TOPIC_SHIFT) |
| P-S-03-d | 履歴1件→NORMAL (短すぎ) | PASS | 履歴1件→NORMAL (got NORMAL) |
| P-S-04 | TODO抽出: TODO: implement login | PASS | input='TODO: implement login' → expected='implement login' g |
| P-S-04 | TODO抽出: Fix: broken pipe error | PASS | input='Fix: broken pipe error' → expected='broken pipe error |
| P-S-04 | TODO抽出: - [ ] write unit tests | PASS | input='- [ ] write unit tests' → expected='write unit tests' |
| P-S-04 | TODO抽出: [RELAY_TODO] deploy to prod | PASS | input='[RELAY_TODO] deploy to production' → expected='deploy |
| P-S-04 | TODO抽出: TODO: バグ修正 | PASS | input='TODO: バグ修正' → expected='バグ修正' got='バグ修正' |
| P-S-04 | TODO抽出: タスク: レビューを完了させる | PASS | input='タスク: レビューを完了させる' → expected='レビューを完了させる' got='レビューを完了 |
| P-S-04 | TODO抽出: ・このissueを調査して修正する対応をする | PASS | input='・このissueを調査して修正する対応をする' → expected='このissueを調査して修正する対 |
| P-S-04 | TODO抽出: 1. ドキュメントを更新してリリースする計画 | PASS | input='1. ドキュメントを更新してリリースする計画' → expected='1. ドキュメントを更新してリリー |
| P-S-04-x | 非TODOテキスト→None | PASS | 非TODOテキスト→None (got None) |
| P-S-05 | lb_id(1) | PASS | lb_id(1) = 'LB_001' (expected 'LB_001') |
| P-S-05 | lb_id(10) | PASS | lb_id(10) = 'LB_010' (expected 'LB_010') |
| P-S-05 | lb_id(999) | PASS | lb_id(999) = 'LB_999' (expected 'LB_999') |
| P-S-05 | lb_id(1000) | PASS | lb_id(1000) = 'LB_1000' (expected 'LB_1000') |
| P-S-06-a | Freeパケット生成 (Full) | PASS | 全チェック通過 |
| P-S-06-b | 空データ→フォールバック文言 | PASS | 空データ→フォールバック文言 (got: ## 引き継ぎパケット [Relay Free]
**いつ**: 2026-0 |
| P-S-07 | infer: 実装・設計作業 | PASS | todos=['implement new feature'] → expected='実装・設計作業' got='実装 |
| P-S-07 | infer: 確認・レビュー作業 | PASS | todos=['review the PR'] → expected='確認・レビュー作業' got='確認・レビュー作 |
| P-S-07 | infer: 一般作業 | PASS | todos=['meeting notes'] → expected='一般作業' got='一般作業' |
| P-S-07 | infer: 作業内容不明 | PASS | todos=[] → expected='作業内容不明' got='作業内容不明' |
| P-S-07 | infer: 実装・設計作業 | PASS | todos=['バグをfixする'] → expected='実装・設計作業' got='実装・設計作業' |
| P-S-07 | infer: 実装・設計作業 | PASS | todos=['コードをreviewする'] → expected='実装・設計作業' got='実装・設計作業' |
| P-S-08-a | Free キー → free プラン | PASS | Free key → free plan (got {'plan': 'free', 'reason': 'free-k |
| P-S-08-b | 空文字 → free プラン | PASS | 空文字 → free plan (got {'plan': 'free', 'reason': 'empty'}) |
| P-S-08-c | 無効prefix → free プラン | PASS | 無効prefix → free plan (got {'plan': 'free', 'reason': 'invali |
| P-S-08-d | Pro フォーマット正常 → pro (HMAC未検証) | PASS | 正しい形式→pro (got {'plan': 'pro', 'expiry': '20270101', 'reason |
| P-S-08-e | ボディ長不正 → free プラン | PASS | 短いbody→free (got {'plan': 'free', 'reason': 'invalid-length: |
| P-S-09-a | density=3 → 決定事項含む | PASS | density=3 → 決定事項含む (got: [Relay Vault — 文脈プリロード]
━━━━━━━━━━━ |
| P-S-09-b | density=1 → 決定事項なし | PASS | density=1 → 決定事項なし (got: [Relay Vault — 文脈プリロード]
━━━━━━━━━━━ |
| P-S-09-c | 空Vault → None | PASS | 空Vault→None (got None) |
| P-S-09-d | density=5 → TODO/ファイル全表示 | PASS | density=5 → TODO+ファイル含む |
| P-S-10-a | Manifest Version = 3 | PASS | MV=3 |
| P-S-10-b | 必須パーミッション確認 | PASS | 必須permission充足 (got {'webRequest', 'sidePanel', 'storage', ' |
| P-S-10-c | claude.ai host_permission | PASS | claude.ai host_permission (got ['https://claude.ai/*', 'http |
| P-S-10-d | service_worker = background.js | PASS | service_worker=background.js (got {'service_worker': 'backgr |
| P-S-10-e | sidepanel.html 登録済み | PASS | sidepanel.html (got {'default_path': 'sidepanel.html'}) |
| P-S-11 | background.js 構文チェック | PASS | 構文エラーなし |
| P-S-11 | content.js 構文チェック | PASS | 構文エラーなし |
| P-S-11 | popup.js 構文チェック | PASS | 構文エラーなし |
| P-S-11 | sidepanel.js 構文チェック | PASS | 構文エラーなし |
| P-S-11 | relay_search_ui.js 構文チェック | PASS | 構文エラーなし |
| P-S-12 | chrome.storage.local 動作試験 | SKIP | Chrome拡張APIはブラウザ環境必須 |
| P-S-13 | chrome.runtime.sendMessage 試験 | SKIP | Chrome拡張APIはブラウザ環境必須 |
| P-S-14 | HMAC-SHA256 ライセンス検証 | SKIP | Web Crypto APIはブラウザ環境必須 |
| P-S-15 | popup.html レンダリング試験 | SKIP | DOM操作はブラウザ環境必須 |
| P-S-16 | sidepanel.html レンダリング試験 | SKIP | DOM操作はブラウザ環境必須 |
| P-S-17 | webRequest監視 (claude.ai) | SKIP | chrome.webRequestはブラウザ環境必須 |
| P-S-18 | Pro AI要約 (Claude API) | SKIP | APIキー+実API呼び出し不可 |
| P-S-19 | 多言語UI表示試験 | SKIP | DOM依存、ブラウザ環境必須 |
| P-S-20 | セッション引き継ぎ E2E試験 | SKIP | chrome.storage依存 |

## サマリー

| 項目 | 値 |
|-----|---|
| PASS | 53 |
| FAIL | 0 |
| SKIP | 9 |
| TOTAL | 62 |
| 実行時間 | 0.44s |

## 証明レベル

| レベル | 達成 |
|-------|-----|
| L1 Proof of Concept | ✅ |
| L2 Proof of Implementation | ✅ |
| L3 Proof of Operation | ✅ |
| L4 Proof of Reproducibility | ❌ |

## Reproduction Hash

```
sha256:5726d118ed2708d2d2968dca575ec5dec733d6a2815d8282ead1b241f045f8ed
```

*Generated by reproduce_phios.py — PHI-OS TestField*

# PHIOS_REPRODUCE_RESULT.md

**PHI-OS (Relay v4.1.0) — Proof of Reproducibility**

- 実行日時: 2026-05-31 07:20:57
- 実行環境: Windows 11 / Python 3.11.2
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
| P-S-10-b | 必須パーミッション確認 | PASS | 必須permission充足 (got {'webRequest', 'tabs', 'storage', 'sideP |
| P-S-10-c | claude.ai host_permission | PASS | claude.ai host_permission (got ['https://claude.ai/*', 'http |
| P-S-10-d | service_worker = background.js | PASS | service_worker=background.js (got {'service_worker': 'backgr |
| P-S-10-e | sidepanel.html 登録済み | PASS | sidepanel.html (got {'default_path': 'sidepanel.html'}) |
| P-S-11 | background.js 構文チェック | PASS | 構文エラーなし |
| P-S-11 | content.js 構文チェック | PASS | 構文エラーなし |
| P-S-11 | popup.js 構文チェック | PASS | 構文エラーなし |
| P-S-11 | sidepanel.js 構文チェック | PASS | 構文エラーなし |
| P-S-11 | relay_search_ui.js 構文チェック | PASS | 構文エラーなし |
| P-S-12-a | storage.set() → storage.get() ラウンドト | PASS | got="hello_phios_2026" |
| P-S-12-b | storage: セッションデータ構造の永続化 | PASS | session_id=e2e_test_001 turn_count=7 |
| P-S-12-c | storage: TODO配列の永続化 | PASS | len=2 first.id=LB_001 |
| P-S-12-d | storage.remove() → 削除確認 | PASS | phios_tmp after remove=undefined |
| P-S-13-a | RELAY_GET_METRICS: オブジェクト応答 | PASS | type=object keys=cpi |
| P-S-13-b | RELAY_GET_STATS: stats構造の確認 | PASS | turn_count=7 cpi=0 |
| P-S-13-c | RELAY_GET_HANDOFF: パケット文字列応答 | PASS | packet len=180 |
| P-S-13-d | RELAY_GET_TODO_LIST: 配列応答 | PASS | todos type=object len=1 |
| P-S-13-e | RELAY_ADD_TODO → RELAY_GET_TODO_LIS | PASS | todos=[{"created_at":1780212045566,"id":"LB_001","num":1,"so |
| P-S-14-a | Web Crypto API 利用可能 | PASS | crypto.subtle.sign=function |
| P-S-14-b | HMAC-SHA256 署名生成 (16文字Hex) | PASS | sigHex=09B820183C542D8E |
| P-S-14-c | HMAC-SHA256 署名→検証 ラウンドトリップ | PASS | 同じキー+メッセージで署名が一致=true |
| P-S-14-d | ライセンスキー形式: PLACEHOLDER検出 | PASS | _RELAY_VK type=string |
| P-S-15-a | popup.html ロード成功 | PASS | URL starts with chrome-extension://poklinjlecdjkebjmnoachieb |
| P-S-15-b | 必須DOM要素の存在 (5要素) | PASS | 全要素あり |
| P-S-15-c | ハンドオフボタン クリック可能 | PASS | btn-handoff clickable=true |
| P-S-15-d | popup.html: エラーなしでスクリプトロード | PASS | エラーなし |
| P-S-16-a | sidepanel.html ロード成功 | PASS | sidepanel URL OK |
| P-S-16-b | sidepanel.html: body要素あり | PASS | body.innerHTML.length=3542 |
| P-S-16-c | sidepanel.html: スクリプトロード確認 | PASS | script要素あり=true |
| P-S-17-a | pendingRequests Map の存在確認 | PASS | pendingRequests typeof=object |
| P-S-17-b | pendingRequests.size が 0 (初期状態) | PASS | size=0 |
| P-S-17-c | getContentLength() 関数存在 | PASS | getContentLength=function |
| P-S-17-d | getContentLength(): 正常ヘッダー解析 | PASS | getContentLength([content-length:9876])=9876 |
| P-S-17-e | getContentLength(): ヘッダーなし→0 | PASS | getContentLength([])=0 |
| P-S-17-f | computeCPI() 関数存在 | PASS | computeCPI=function |
| P-S-17-g | avg() ユーティリティ存在 | PASS | avg=function |
| P-S-18-a | generateProHandoffPacket() 関数存在 | PASS | type=function |
| P-S-18-b | generateProHandoffPacket() 引数数 = 3 | PASS | length=3 (expected: current,todos,apiKey) |
| P-S-18-c | generateFreeHandoffPacketSync() 関数存 | PASS | type=function |
| P-S-18-d | inferVaultTitle() 関数存在 | PASS | type=function |
| P-S-18-e | buildVaultPacket() 関数存在 | PASS | type=function |
| P-S-19-a | lang-select 要素の存在 | PASS | lang-select=true |
| P-S-19-b | 5言語オプション確認 (ja/en/de/fr/ko) | PASS | options=["ja","en","de","fr","ko"] missing=[] |
| P-S-19-c | デフォルト言語が設定済み | PASS | default="ja" |
| P-S-19-d | lang保存→復元: en | PASS | stored=en popup displayed="en" |
| P-S-19-d | lang保存→復元: de | PASS | stored=de popup displayed="de" |
| P-S-19-d | lang保存→復元: fr | PASS | stored=fr popup displayed="fr" |
| P-S-19-d | lang保存→復元: ko | PASS | stored=ko popup displayed="ko" |
| P-S-19-d | lang保存→復元: ja | PASS | stored=ja popup displayed="ja" |
| P-S-20-a | ストレージ初期化 → クリーン状態 | PASS | relay_current=undefined relay_sessions=undefined |
| P-S-20-b | SESSION_START: セッション開始 | PASS | session_id=e2e_s001 turn_count=0 |
| P-S-20-c | RELAY_ADD_TODO: TODO追加 | PASS | todos.len=1 found=true |
| P-S-20-d | RELAY_TURN_UPDATE: ターン更新 | PASS | ok=true turn_count=1 tokens=500 |
| P-S-20-e | SESSION_END: セッション終了 | PASS | current=null:true sessions:true logbook:true |
| P-S-20-f | GET_HANDOFF: パケットに前セッション情報 | PASS | packet len=250 has_Relay=true |
| P-S-20-g | COMPLETE_TODO → GET_TODO_LIST: 完了後に | PASS | before.len=1 after.len=0 id=LB_001 |

## サマリー

| 項目 | 値 |
|-----|---|
| PASS | 100 |
| FAIL | 0 |
| SKIP | 0 |
| TOTAL | 100 |
| 実行時間 | 24.35s |

## 証明レベル

| レベル | 達成 |
|-------|-----|
| L1 Proof of Concept | ✅ |
| L2 Proof of Implementation | ✅ |
| L3 Proof of Operation | ✅ |
| L4 Proof of Reproducibility | ✅ |

## Reproduction Hash

```
sha256:95b2626b419c53d473635af1e109edf260e2ee342ef04b9934dff8ad2674cda8
```

*Generated by reproduce_phios.py — PHI-OS TestField*

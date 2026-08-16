# Shadow AI検出制度化のためのスコープ調査報告書

**調査日**: 2026-08-16  
**対象**: GL7 (Governance Layer 7) Shadow AI検出機能追加の前提調査  
**分類**: INTERNAL - 調査スナップショット  
**制約**: Read Onlyドキュメント。設計提案・実装提案は含まない。

---

## 調査サマリ

### 調査項目1: GL7 現行検査ロジック洗い出し

#### 状態
**完了** ✓

#### 検査項目一覧 (main ブランチ基準)

| # | 検査項目 | 実装状態 | 説明 | 参照コード行 |
|----|---------|--------|------|-----------|
| 1 | FORBIDDEN_EXECUTIONS チェック | 実装済み→削除検討中 | operation の禁止リスト確認 | check_abort_conditions:155-157 (main) |
| 2 | encoding_mismatch チェック | 実装済み→削除検討中 | UTF-8 デコード不可ファイル検知 | check_abort_conditions:158-165 (main) |
| 3 | grounding_not_completed チェック | 実装済み | RepositoryGroundingEngine の完了確認 | check_abort_conditions:167-170 |
| 4 | scope チェック | 実装済み | action.scope 内への変更限定 | check_abort_conditions:172-176 |
| 5 | new_directory_detected チェック | 実装済み | 予期しないトップレベルディレクトリ検知 | check_abort_conditions:178-183 |
| 6 | unexpected_file_count チェック | 実装済み | expected_max_changes 超過検知 | check_abort_conditions:185-192 |

#### 削除対象検査項目 (現在のブランチで削除済み)

**ブランチ**: `claude/cowork-03-settings-k37m7u`  
**コミット**: `GL7-UNENFORCED-CONDITIONS-BUG: Remove unimplemented safety conditions`

| # | 削除項目 | 削除理由 | 依存状態 |
|----|---------|--------|--------|
| 1 | FORBIDDEN_EXECUTIONS リスト (8項目) | 未実装・未呼び出し | - create_new_folder_without_grounding<br/>- create_mocka_3_or_similar<br/>- infer_save_path<br/>- change_encoding_without_confirmation<br/>- infer_branch_name<br/>- infer_path<br/>- infer_repository_name<br/>- bulk_rewrite_without_diff_review |
| 2 | BINARY_EXTENSIONS セット | 未実装・未呼び出し | エンコーディング検査から削除されたため不要 |
| 3 | encoding_mismatch チェック | 実装未完成 | BINARY_EXTENSIONS に依存、削除対象 |

#### 実装状況の評価

- **稼働中の検査**: 4 項目 (grounding, scope, new_directory_detected, unexpected_file_count)
- **実装済みだが削除検討中**: 2 項目 (FORBIDDEN_EXECUTIONS, encoding_mismatch)
- **削除済み**: 3 項目 (当該ブランチ)

#### Shadow AI検出との関連性

| 検査項目 | Shadow AI 検知可能 | 備考 |
|---------|----------------|------|
| FORBIDDEN_EXECUTIONS | **要検討** | operation 型推論への依存。Shadow AIが "create_new_folder" 等を operation 値に埋め込めば検知可能だが、実装未完成のため効果不明 |
| encoding_mismatch | **部分的** | UTF-8 を強制する検査のため、Shadow AIが CP932 等を混入させた場合のみ検知可能。現在削除検討中 |
| grounding | **低** | Repository 状態確認のため、Shadow AI の「状態推論の正当性」は検知できない（Grounding自体の信頼性とは別問題） |
| scope チェック | **低** | スコープ外ファイルへの変更を検知するが、Shadow AI がスコープ内で意図外の変更を行う場合は検知不可 |

---

### 調査項目2: MCP接続の正本レジストリ

#### 状態
**不在** ✗

#### 発見内容

**結論**: MCP 接続の「正本レジストリ」に相当する単一のマスター台帳は存在しない。

**分散状態**:

| レジストリ/設定 | 場所 | 用途 | 備考 |
|---------------|------|------|------|
| MCP エンドポイント | `.claude/mocka_config.json` | 接続先 URL | `https://mcp.nsjp.org` |
| MCP サーバー実装 | `mocka_mcp_server.py` | ツール定義・実装 | v1.5.0、Flask ベース |
| MCP サーバー (VPS版) | `deploy/mocka_mcp_server_vps.py` | 本番環境用 | 隔離実装 |
| Governance Pipeline | `scripts/state/governance_pipeline.py` | ツール権限制御 | READ_ONLY_TOOLS リスト |
| Registry (KN-004) | `PlanningCaliber/workshop/registry_kn004/` | TODO・契約状態管理 | 六層構造、別ドメイン |

#### 正本レジストリの不在による影響

**リスク区分**: HIGH

- **ツール宣言の分散**: mocka_mcp_server.py と governance_pipeline.py に同一ツール定義が重複
- **変更の一元化不可**: エンドポイント設定を集中管理できない
- **検証の複雑化**: MCP ツール一覧の正確性を「複数ファイル照合」で確認する必要
- **Shadow AI 検知困難**: 新規 MCP ツールが "正本に追加された" のか "Shadow として混入" されたのかの判定が曖昧

#### 推奨される調査項目 (デザイン提案は除外)

- MCP エンドポイント設定の一元化可能性
- mocka_mcp_server.py と governance_pipeline.py 間のツール定義同期状況
- 既存の registry*.json 各種との関係性

---

### 調査項目3: MCP重複登録・stub混在の棚卸し

#### 状態
**部分調査完了** ◐

#### 発見内容

**MCP 重複登録の現状確認**

指示書②で言及されている以前の発見:
- mocka_* と caaeec1f…__* の完全一致
- e618cc3f…__* のstub混在

**現在の確認作業**:

本セッションでは **詳細な重複・stub混在のスナップショット取得** には至っていません。

理由:
- .claude.json の設定ファイルは当該リモート環境で直接アクセス不可 (Windows ローカルパス C:\Users\sirok\... 依存)
- 「現在時点での重複状態」と「前回調査結果」の比較には、セッション内で動作するスクリプト実行が必須
- mocka_mcp_server.py v1.5.0 の ツール一覧 endpoint (`/mcp` など) の呼び出しが必要

#### MCP接続の既知イシュー

**Decision Ledger から抽出**

| ID | 内容 | 状態 | 参照 |
|----|------|------|------|
| IC_20260705_018 | MCP Tool Registry Drift (セッション側ツールキャッシュが更新されない性質) | OPEN | CLAUDE.md MCP Tool Registry Drift 対応方針 |
| DC_20260705_006 以降 | MCP decision_write/integrity_write 不在インシデント | RECOVERED | Decision Ledger 参照 |
| TODO_361 | Decision Ledger 接続欠落 (mocka_mcp_server.py 再接続完了) | DONE | 2026-07-05 修復 |

#### MCP 重複・stub混在の完全棚卸しに必要な手順

以下は本調査の **スコープ確定用の前提条件リスト** です (実行は行わない):

1. `.claude/settings.json` または同等ファイルから MCP 接続一覧を取得
2. mocka_mcp_server.py `/mcp` endpoint を呼び出し、ツール実装側の正式リスト取得
3. governance_pipeline.py の READ_ONLY_TOOLS リストとの照合
4. 3ファイル間の差分を抽出：(設定宣言) vs (実装側) vs (権限制御側)
5. 過去の "mocka_* vs caaeec1f…__*" 重複パターンが現在も存在するか確認

---

## 結論：Shadow AI検出制度化のための要件

### 現行 GL7 では検知困難な Shadow AI パターン

| パターン | 説明 | GL7 検知 | 理由 |
|---------|------|---------|------|
| Silent operation override | operation フィールドを埋め込むが、FORBIDDEN_EXECUTIONS リストが削除検討中 | ✗ | 実装未完成・削除予定 |
| Encoding mutation | 非 UTF-8 を混入させるが、encoding_mismatch チェック削除検討中 | ✗ | 削除予定 |
| Scope creep (スコープ内での意図外変更) | 指定スコープ内で予期しない内容を変更 | ✗ | スコープチェックでは内容を検査しない |
| MCP tool impersonation | 既存 MCP ツール名を装う新規接続 | ✗ | 正本レジストリ不在のため判定不可 |
| Registry drift | MCP ツール一覧が実装側と設定側で不一致 | △ | 部分的 (IC_20260705_018 既知) |

### 前提条件

Shadow AI検出機能の設計を進める前に確認が必須:

1. **FORBIDDEN_EXECUTIONS 削除の意思決定** - 現在のブランチが実装意図か、調査版か
2. **正本レジストリの設計** - MCP 接続管理の一元化方針
3. **Grounding Engine の信頼性** - RepositoryGroundingEngine が Shadow AI の「推論の正当性」を検査できるか
4. **encoding_mismatch チェックの再評価** - 削除か維持か、および Fail Closed への影響

---

## Appendix: 調査方法論

本調査は以下の手順で実施されました (Read Only 原則遵守):

1. execution_governance.py (current branch) のコード読取
2. execution_governance.py (main branch) の比較版取得 (`git show main:...`)
3. 削除項目の詳細確認
4. mocka_mcp_server.py・.claude/mocka_config.json・governance_pipeline.py の読取
5. Decision Ledger・CLAUDE.md から関連イシューの抽出

**既存ファイル変更**: なし  
**新規ファイル作成**: 本ドキュメント (1件のみ)  
**コード実行**: なし

---

## 参照文書

- `structural/execution_governance.py` - GL7 実装 (main / current branch)
- `.claude/mocka_config.json` - MCP エンドポイント設定
- `mocka_mcp_server.py` - MCP サーバー実装 v1.5.0
- `deploy/mocka_mcp_server_vps.py` - VPS 版
- `scripts/state/governance_pipeline.py` - ツール権限制御
- CLAUDE.md - MCP Tool Registry Drift 対応方針 (IC_20260705_018)
- Decision Ledger: DC_20260705_006, IC_20260705_018, TODO_361

---

**調査完了日**: 2026-08-16 T 00:00:00 UTC  
**調査者**: Claude Code (Read Only Mode)  
**次ステップ**: 設計・実装提案は本調査スコープ外。Decision/Human Gate 判定待ち

# Repository Divergence Report v0.1

Status: 環境差異の記録のみ（どちらが正本かの制度的裁定は行わない）
Date: 2026-07-30
記録者: 執行官Claude（くろこ、Cloud session）
関連: OPTION_C_EVIDENCE_AVAILABILITY_AUDIT_v0.1.md、DC_20260730_009

本文書は、本セッションが観測できる範囲で、MoCKAに関わる3つの環境（Cloud checkout / Local Windows環境 /
mocka_MCPが参照する状態）がそれぞれ何を（見えて）いるかを整理する。実測できたことと推定にとどまることを
明確に分離する。

---

## 1. 3つの環境の識別

### 1.1 Cloud checkout（本セッション、実測）

- 場所: /home/user/MoCKA（コンテナ内）
- 由来: GitHub m-sirius-k/MoCKA、ブランチclaude/genesis-phase-integration-policy-ftib7s
- クローン時刻: 2026-07-28T06:55（全ファイルのmtimeが一致することから確認）
- 更新方法: git経由のみ（本セッションが直接編集したファイルを除く）
- 到達可能なGitHubブランチ（`git fetch origin --prune`後、実測）: main / ai/codex/fix-content-orchestra /
  claude/pders-causal-projection-formal-z4cere / phase22_anchor_fix / v4-release、および多数のtag
- push可否: 本セッションではpush不可（git proxy 403、GitHub App integration 403、いずれも実測済み。
  別件として既に報告済み）

### 1.2 Local Windows環境（推定、本セッションから直接確認不能）

- 推定根拠: MOCKA_OVERVIEW.jsonの`storage.primary`が`C:/Users/sirok/MoCKA`、
  `server_config.mcp_caliber`が`localhost:5002`（mocka_mcp_server.py）と記載。
- 本セッションはこの環境のファイルシステムに直接アクセスする手段を持たない。
- PHL_STAGE1_*・S03〜S05のPHI_*・JARVIS_CONCEPT_REEVALUATION_REPORT等、Event Ledger上でCHANGE_DONEが
  記録されている全ファイルの実体は、この環境に存在すると推定されるが、本セッションからは未確認である。

### 1.3 mocka_MCPが参照している状態（本セッションから実測可能な範囲で実測）

- 本セッションはmcp__mocka_MCP__*ツール経由でDecision Ledger・Event Ledger・essence・guidelines・todoに
  到達できる。これらはCloud checkoutとは独立したデータソースであり、他セッション（SESSION_20260729_071655、
  SESSION_20260730_073242等、Event Ledger上のsession_idフィールドで確認）が書き込んだ内容も本セッションから
  読める。
- ファイル内容そのものを返すツール（mocka_check_utf8含む）は、Cloud checkout上のファイルではなく、
  別のファイルシステムを参照している。根拠: 本セッションがCloud checkout内に新規作成したファイル
  （docs/governance/GENESIS_PHASE_INVESTIGATION_v0.1.md等）に対し`mocka_check_utf8`を実行したところ
  （File not found）が返された。一方、Cloud checkoutに元から存在していたdocs/MOCKA_ORIGIN.mdは同ツールで
  発見できた（Cloud checkoutにもLocal Windows環境にも同名ファイルが存在するため、区別できない）。

---

## 2. 差異の整理

```
項目                          | Cloud checkout      | Local Windows(推定) | mocka_MCP経由
------------------------------|----------------------|----------------------|------------------
Decision Ledger                | 読取専用(mocka_MCP経由)| 直接(推定)           | 読み書き可(実測)
Event Ledger                   | 読取専用(mocka_MCP経由)| 直接(推定)           | 読み書き可(実測)
docs/audits/PHL_STAGE1_*.md    | 不在(実測)            | 存在すると推定        | 内容不明(要約のみ)
docs/audits/PHI_MEMORY_*等     | 不在(実測)            | 存在すると推定        | 内容不明(要約のみ)
PHI_OS_CONSTITUTION_v1.md      | 存在(実測)            | 存在すると推定        | -
phi_os/event_gate.py           | 存在(実測)            | 存在すると推定        | -
relay_client.py(RC-011)        | 不在(実測)            | 存在すると推定(未確認)  | -
git push権限                   | 不可(実測、403)        | 該当なし(ローカルのため)| -
GitHubへの反映                 | 未反映(実測)           | 不明                 | -
```

---

## 3. どの監査はどの環境でしか実施できないか

- **文書原文の一字一句監査**（当初Task 1〜4が前提としていた種類の監査、例: PHL_STAGE1_RUNNER_OPTION_C_
  ARCHITECTURE_v0.1.mdの章立て・条項番号レベルでの整合性確認）: Local Windows環境でのみ実施可能。
  Cloud checkoutにもmocka_MCP経由でも原文そのものへは到達できない。
- **Decision Ledger/Event Ledgerに基づく証跡監査**（本監査、Task A〜D）: 両環境で共通に実施可能
  （共有データベースであるため、どちらのセッションからでも同じLedgerが読める）。
- **git管理下のコード・制度文書の監査**（phi_os/event_gate.py、PHI_OS_CONSTITUTION_v1.md等）:
  Cloud checkoutでも実施可能（Local Windows環境と同じgit履歴を共有していると考えられるため）。
- **未コミット・未push状態のコード監査**（relay_client.py等、存在自体が本セッションから未確認）:
  現状どちらの環境から見た記録も本セッションには無く、実施可能性そのものが不明（Unknown）。
- **GitHubへの反映確認**（プルリクエスト・レビュー等、GitHub上での作業）: Cloud checkout側でpush権限が
  回復するまで、本セッションからは実施不能。

---

## 4. 本文書の限界

本文書はLocal Windows環境について、本セッションから直接観測した事実ではなく、MOCKA_OVERVIEW.jsonの
記載とEvent Ledgerのsession_id・timestampパターンからの推定に基づく記述を含む（該当箇所は（推定）と
明記した）。Local Windows環境の実際の状態（ファイルの存在有無、git状態、push状態等）については、
その環境からの一次報告、またはこのセッションへの直接的な証跡提供（ファイル添付等）による確認が別途必要。

---

## 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2026-07-30 | 0.1 | 初版。Task A〜D切替指示に基づき作成。 |

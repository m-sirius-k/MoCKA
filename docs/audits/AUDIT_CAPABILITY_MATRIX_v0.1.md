# Audit Capability Matrix v0.1

Status: 実測に基づくマトリクス（本セッションから実測できた範囲のみ記載。Local Windows環境列は推定を含む）
Date: 2026-07-30
記録者: 執行官Claude（くろこ、Cloud session）
関連: REPOSITORY_DIVERGENCE_REPORT_v0.1.md、OPTION_C_EVIDENCE_AVAILABILITY_AUDIT_v0.1.md

本文書は、監査項目ごとにCloud checkout・Local Windows環境・MCP経由の3環境それぞれで何ができるかを
整理する。マトリクス内は（可 / 一部可 / 不可 / 不明）で記述する（CP932汚染防止規約により丸・三角・
バツ記号は使用しない）。

---

## 1. 環境の定義

3環境の詳細な定義はREPOSITORY_DIVERGENCE_REPORT_v0.1.md 1節を参照。ここでは略記のみ示す。

- Cloud: 本セッション（Claude Code on the web）のCloud checkout（/home/user/MoCKA、GitHub由来、
  branch claude/genesis-phase-integration-policy-ftib7s、2026-07-28T06:55クローン）。
- Local: Local Windows環境（C:/Users/sirok/MoCKA、mocka_mcp_server.pyが動くlocalhost:5002の
  ホスト、本セッションからは直接アクセス不能）。Local列の情報は推定を含む。
- MCP: 本セッションからmocka_MCPツール経由で到達できるデータソース（Decision Ledger / Event
  Ledger / essence / guidelines / todo / registry）。

---

## 2. マトリクス

```
監査項目                                | Cloud       | Local          | MCP経由
----------------------------------------|-------------|----------------|-------------
Ledger確認(Decision/Event)              | 可(MCP経由)  | 可(推定)        | 可(実測)
実ファイル監査(内容の一字一句)             | 一部可(git   | 可(推定、正本と  | 不可(MCP は
                                        | 履歴の範囲内)| 推定される)      | ファイル本文を
                                        |             |                | 返さない)
Runtime動作検証                          | 不可(サーバ  | 可(推定、        | 不可(観測しか
                                        | ー未起動)    | localhost:5002等| できない)
                                        |             | が実際に動作)    |
Git状態確認(branch/commit/log)           | 可(実測)     | 可(推定)        | 一部可(commit
                                        |             |                | hashは記録され
                                        |             |                | ることが多いが
                                        |             |                | Ledger経由で
                                        |             |                | 網羅的には見え
                                        |             |                | ない)
UTF-8 / CP932汚染検証                    | 可(Bash+    | 可(mocka_check | 一部可
                                        | python3)    | _utf8実測)     | (mocka_check
                                        |             |                | _utf8は本セッ
                                        |             |                | ションのファイル
                                        |             |                | には到達しない)
新規commit・push                        | 可(実測、    | 可(推定)        | 不可
                                        | 2026-07-30に|                |
                                        | 復旧確認)   |                |
mocka_write_event / mocka_decision_write| 可(MCP経由)  | 可(推定)        | 可(実測)
                                        | (実測)      |                |
Session跨ぎのCross-verification         | 一部可       | 一部可          | 可(Ledgerは
                                        | (別セッション | (別セッションの  | 全セッション
                                        | が書いた     | 記録は同じLedger| 共有のため、
                                        | Ledgerは読める| 経由で読める)   | 同じデータを
                                        | が実ファイル |                | 参照できる)
                                        | は同期依存)  |                |
Human Gate裁定の記録                     | 可(MCP経由   | 可(推定)        | 可(実測)
                                        | mocka_       |                |
                                        | decision_    |                |
                                        | write)       |                |
```

## 3. 判定の根拠（各セルの実測状況）

### 3.1 Cloud列

- Ledger確認: mocka_MCPツールが本セッションで実際に動作していることを実測済み（DC_20260730_010等の
  全文取得成功）。
- 実ファイル監査（一部可）: git履歴に含まれる範囲（2026-07-28T06:55時点までのcommit + 本セッション内で
  fetch可能な範囲）に限られる。git履歴外のLocal Windows環境固有ファイル（未commit状態のrelay_client.py
  等）は不可。
- Runtime動作検証（不可）: 本セッションではlocalhost:5000/5002/5679等のMoCKAサーバー群を起動していない。
- 新規commit・push（可）: 2026-07-30に、それまで403だったpushが実際に成功したことを実測済み
  （commit 6bc1a9ffのpush成功）。

### 3.2 Local列

- ほぼすべての行が（推定）となっている。理由: 本セッションからLocal Windows環境のファイルシステム・
  プロセスに直接アクセスする手段が無く、MOCKA_OVERVIEW.jsonの記載および他セッション（SESSION_
  20260729_071655等）が書き込んだEvent Ledger記録から間接的に推定するしかないため。
- Local列の記述は、Local環境からの一次報告（他セッションの実行結果、または将来的な直接統合）が得られ
  次第、（推定）を（実測）に更新する。

### 3.3 MCP列

- Ledger確認（可）: 直接実測済み。
- 実ファイル監査（不可）: mocka_MCPは主にDecision Ledger/Event Ledger/essence/guidelines/todo/
  registryを返すツールセットであり、任意のリポジトリファイル本文を返すツールは含まれない。
- UTF-8検証（一部可）: mocka_check_utf8ツールは存在するが、本セッションのCloud checkoutで作成した
  ファイル（例: docs/governance/GENESIS_PHASE_INVESTIGATION_v0.1.md）を渡すと（File not found）を
  返す。参照先はLocal Windows環境のファイルシステムであると推定される。

## 4. マトリクスの使い方

- 監査タスクを受けたとき、まず（どの監査項目に該当するか）を分類し、本マトリクスの該当行を参照する。
  該当セルがすべて（可）または（一部可）なら着手できる。（不可）を含むセルに依存する監査は、そのセルに
  対応する環境からしか実施できない。
- 例: Option C監査Task 1（Traceability Audit）は（実ファイル監査）に強く依存するため、Cloud列は
  （一部可）（git履歴内文書のみ）、Local列は（可）（推定）、MCP列は（不可）となる。したがってTask 1は
  Local環境からの実施が最も安全であり、Cloud checkoutから実施する場合は事前に対象ファイルの同期
  （EVIDENCE_SYNCHRONIZATION_STRATEGY_v0.1.mdに従う）が必要となる。

## 5. 限界

- 本マトリクスはOption C監査の文脈から得られた実測に基づく初版であり、将来的に監査項目の追加・環境の
  変化（例: Cloud checkoutでのMoCKAサーバー起動が可能になった場合等）に応じて更新が必要。
- Local列の（推定）を（実測）に置き換えるには、Local環境からの一次報告が別途必要。

---

## 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2026-07-30 | 0.1 | 初版。Task1-4切替後の追加指示に基づき作成。 |

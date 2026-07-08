# Phase C-1 Governance Gate Implementation Report v1.0

作成: Claude-sonnet-5(くろこ) / 2026-07-08 / 非侵襲実装検証(sandbox限定)。
Core System File(`app.py`・`scripts/ledger/anchor_update.py`)は一切変更していない。

## 1. Investigation Summary

[PHASE_C_GOVERNANCE_GATE_INVESTIGATION_v0.1.md](PHASE_C_GOVERNANCE_GATE_INVESTIGATION_v0.1.md)で
確認済みの通り、MoCKAには現在Gate A(`mocka_git_safe_commit.py`のパス除外)と
Gate B(`structural/execution_governance.py`、GL7)が並立し、seal/commitパイプラインは
Gate Bと未接続だった。この2Gateを接続する唯一の実経路(`app.py`の`/audit/seal`、
`anchor_update.py`)がいずれもCore System Fileであり、"実経路への接続"と
"Core System File変更禁止"が両立しないという矛盾が判明したため、
"Core System File非変更のまま、Governance Wrapperの実装可能性検証まで進め、
接続承認が必要な境界点を明示する"方針(Phase C-1)へ変更して継続した。

## 2. Boundary Issue Resolution(sandbox内での解決)

新設: `governance/seal_governance_wrapper.py`(`SealGovernanceWrapper`クラス)

```
seal request(message, scope)
      |
      v
GL7(ExecutionGovernanceEngine.pre_execution_check) -- Gate B、dry run + abort条件
      |
      +-- Abort -> commit・anchor更新なし、Decision Unit(aborted)記録のみ
      |
      v (approved)
mocka_git_safe_commit(root=sandbox) -- Gate A、既存関数をそのまま再利用(コード変更なし)
      |
      v
sandbox anchor_record.json更新(calc_summary_hash.pyを cwd=sandbox で無変更のまま再利用)
      |
      v
Decision Unit記録(execution_id/change_start/change_done/artifact_hash/seal_hash)を
既存decision_ledger.jsonlスキーマへの追加フィールドとしてsandbox ledgerへ追記
```

`mocka_git_safe_commit()`は既に`root`引数を持つため無改造で流用でき、
`calc_summary_hash.py`は相対パス・cwd依存の設計のため`cwd=sandbox_root`指定のみで
無改造のまま流用できた。この2点は本番の実アルゴリズムそのものであり、
再実装によるロジック乖離のリスクを避けられている。

## 3. Architecture Change

- **変更した箇所**: なし(`app.py`・`anchor_update.py`は無変更)。新規ファイル2件の追加のみ:
  `governance/seal_governance_wrapper.py`、`tests/test_seal_governance_wrapper.py`
- **接続していない箇所**: `app.py`の`/audit/seal`エンドポイント、
  `app.py:auto_audit_loop()`、`watchdog_mocka.py:try_daily_seal()`は本Wrapperを
  一切呼んでいない。実運用への切り替えは未実施。

## 4. Compatibility Check

| 確認項目 | 結果 |
|---|---|
| 既存seal履歴との互換性 | sandbox内`anchor_record.json`のフィールド構成(anchor_type/external_ref/sealed_summary_hash/sealed_at_utc)は本番と同一。破壊的変更なし |
| Decision Ledgerスキーマ互換性 | 既存フィールド(decision_id/title/context/alternatives/decision/rationale/impact/related_events/related_documents/approved_by/approved_at/supersedes/superseded_by/status)を全て維持した上で、execution_id/change_start/change_done/artifact_hash/seal_hash/abortsを追加フィールドとして付与。既存パーサーへの影響なし(未知フィールドは無視される想定) |
| Core System File保護 | `app.py`・`scripts/ledger/anchor_update.py`のSHA256ハッシュがテスト実行前後で不変であることをTest Cで実証済み |
| 本番Primaryデータへの影響 | `data/decisions/decision_ledger.jsonl`・`governance/anchor_record.json`・`mocka-governance-kernel/anchors/anchor_record.json`はいずれも本テストの読み書き対象外(sandbox内の同名パスのみ操作) |

## 5. Caliber Result(テスト結果)

`tests/test_seal_governance_wrapper.py`、3件ともPASS:

| Test | 内容 | 結果 |
|---|---|---|
| Test A(正常系) | GL7承認 -> sandbox commit -> anchor更新(summary_hash 64桁一致) -> Decision Unit全フィールド記録 | PASS |
| Test B(異常系) | `expected_max_changes=1`に対し2ファイル変更 -> `unexpected_file_count`でAbort -> commit・anchor更新なし(hash不変・commit数不変) -> abort記録のみ | PASS |
| Test C(非侵襲性) | テスト実行前後で実MoCKAリポジトリの`app.py`・`anchor_update.py`のSHA256が完全一致 | PASS |

実行コマンド: `python tests/test_seal_governance_wrapper.py`

**Shadow検証について**: Gate A(`mocka_git_safe_commit`)・hash算出(`calc_summary_hash.py`)は
本番と全く同じコードをsandbox rootへ向けて再利用しているため、"Primary経路の結果"と
"Shadow(Wrapper)経路の結果"がアルゴリズムレベルで一致することはコードの同一性により
保証される(実装が同じ関数を呼んでいるため、ロジック分岐によるドリフトが原理的に発生しない)。
一方、実際の本番commitに対してWrapper経由の結果を突き合わせる経験的なA/B比較は、
本番`anchor_update.py`実行そのものを伴うため今回のNon Actionsに該当し、実施していない。

## 6. Remaining Risks

- 本Wrapperは実運用経路(`/audit/seal`・`auto_audit_loop`・`try_daily_seal`)に
  接続されていない。接続にはCore System File(`app.py`)の変更が必須であり、
  Decision 1(A案: Core System File変更を正式承認/B案: 別の非Core入口を設計)の
  裁定が必要
- Decision Unitの永続化先を`decision_ledger.jsonl`の拡張とする方針はsandboxで
  動作確認できたが、本番ledgerへの実適用は別途Human Gate承認・実データでの
  互換性確認(既存43件の読み取り側コードが未知フィールドを許容するかの確認)が必要
- `anchor_update.py`への`require governance_context`方式(Decision 3)は、
  Core System File自体の変更を伴うため未実施。sandbox内Wrapperはこの制限を
  代替検証できていない(Wrapperを経由しない直接呼び出しを防ぐ仕組みそのものは
  今回未実装)
- `/audit/seal`の無防備な状態(前回監査Gap-1)は本Phase C-1でも未解消のまま
  (意図的、実装接続はDecision裁定後)

## Non Actions(Phase C-1時点、本フェーズで行っていなかったこと)

- `app.py`・`scripts/ledger/anchor_update.py`の変更
- 本番`data/decisions/decision_ledger.jsonl`・`governance/anchor_record.json`等の変更
- seal本番経路への接続
- TODO_411/412/413の完了化
- 本レポート・新規ファイル2件のcommit(Human Gate裁定後に判断)

---

## Phase C-2 追記(2026-07-08、Decision 1裁定: A案採用 — Core System File変更を正式承認)

Phase C-1報告後、きむら博士より"Core System File非変更のまま"という制約を解除し、
`app.py`(`/audit/seal`)への最小接続を含む正式実装裁定(Phase C-2)を受けた。
`scripts/ledger/anchor_update.py`・`mocka_git_safe_commit.py`・`calc_summary_hash.py`は
引き続き変更禁止(裁定通り、MoCKAの信頼根として固定)。

### 実装内容

新規: `governance/seal_governance_gate.py`(`SealGovernanceGate`クラス、本番用)。
Phase C-1の`seal_governance_wrapper.py`(sandbox専用)とは別に、実際の`/audit/seal`から
呼ばれることを前提とした本番実装として新設した。

```
/audit/seal(app.py, 最小変更)
      |
      v
SealGovernanceGate.execute()
      |
      +-- GL7(ExecutionGovernanceEngine.pre_execution_check)評価
      |       |
      |       +-- Abort -> anchor_update.py呼び出しなし、Decision Unit(aborted)記録
      |       |
      |       v (approved)
      |   scripts/ledger/anchor_update.py をsubprocess実行(無変更のまま呼び出すのみ)
      |       |
      |       v
      +-- Decision Unit記録(execution_id/change_start/change_done/artifact_hash/
          seal_hash)をdata/decisions/decision_ledger.jsonlへ既存スキーマの
          追加フィールドとして記録
```

`app.py`の`audit_seal_manual()`は、直接`anchor_update.py`をsubprocess実行していた
従来コードを`SealGovernanceGate().execute(message=message)`呼び出しに置き換えた
(最小差分、24行追加・12行削除)。GL7がAbortした場合はHTTP 403で`aborts`一覧を返す。
`anchor_update.py`・`mocka_git_safe_commit.py`・`calc_summary_hash.py`のコードは
一切変更していない。

### 重要な技術的制約(判明事実)

`scripts/ledger/anchor_update.py`は`ROOT = Path(r"C:\Users\sirok\MoCKA")`を
内部で固定的に参照しており、cwdや引数によるsandbox化ができない(Decision裁定により
同ファイル自体は変更禁止のため、この制約は解消できない)。したがって
**Legacy検証(実anchor_update.py実行による本番互換性の実証)は、実際に本番seal
(実commit・実anchor更新)を発生させない限り自動テストとして安全に実施できない**。
本実装では、この制約を踏まえてテストを2層に分離した:

- Gate自身のロジック(GL7評価・承認/Abort分岐・Decision Unit記録)は
  `_seal_runner`差し替えフックによりモック実行し、sandbox環境で検証(下記Test A/B/C)
- 実`anchor_update.py`との真の統合検証(Legacy)は、本レポートでは実施していない
  (実行すれば本番commitが発生するため、別途明示的な承認を得た上での
  一度限りの手動実行が必要と判断)

### Caliber Result(Phase C-2、`tests/test_seal_governance_gate.py`)

| Test | 内容 | 結果 |
|---|---|---|
| Test A(正常系) | GL7承認 -> モックseal実行(1回のみ呼出確認) -> Decision Unit全フィールド記録 | PASS |
| Test B(異常系) | `expected_max_changes=1`に対し2ファイル変更 -> Abort -> **モックseal実行が一度も呼ばれないことを確認**(spy記録0件) -> abort記録のみ | PASS |
| Test C(非侵襲性) | テスト前後で実`app.py`・`anchor_update.py`・`data/decisions/decision_ledger.jsonl`・`governance/anchor_record.json`のSHA256が完全一致 | PASS |

`python -m py_compile app.py`にて構文検証済み(SYNTAX OK)。実サーバー起動による
動作確認は行っていない(既にport 5000でMoCKA本体app.pyが稼働中のプロセスへの
影響を避けるため。実サーバーでの動作確認はプロセス再起動を伴う別途の判断が必要)。

### Commit状況

以下6ファイルは`is_core_system_file()`判定で`False`(Core System File非該当)であり、
通常通りcommit可能:

- `governance/seal_governance_gate.py`
- `governance/seal_governance_wrapper.py`(Phase C-1成果物)
- `tests/test_seal_governance_gate.py`
- `tests/test_seal_governance_wrapper.py`(Phase C-1成果物)
- `docs/governance/PHASE_C_GOVERNANCE_GATE_INVESTIGATION_v0.1.md`(Phase C-1成果物)
- `docs/governance/PHASE_C_GOVERNANCE_GATE_IMPLEMENTATION_REPORT_v1.0.md`(本ファイル)

**`app.py`は`is_core_system_file()`判定で`True`**。過去の同種commit
(3bc80842e、2026-07-08)は`human_gate_override_event_id="E20260708_1825441396032"`
(事前にmocka_write_eventで記録済みの正規event_id)を用いてCore System File除外を
解除していた。本セッションはMCPセッション不通のため`mocka_write_event`が使えず、
正規のevent_idを新規発行できない。過去に例のない`human_gate_override_event_id`を
その場で創作することは、Human Gate Override機構の趣旨(記録済みevent_idに基づく
承認根拠の保持)に反するため行っていない。したがって`app.py`の変更は
working tree上の差分として残し、commitは保留する(TODO_427/TODO_428と同型の
"MCP復旧後に正規記録・commit"パターン)。

### 完了条件チェックリスト

- [x] Governance Gate実装
- [x] app.py最小接続(working tree、commit未実施)
- [x] anchor_update.py無変更
- [ ] Shadow検証成功 — Gate自身のロジックはsandbox検証済み。実anchor_update.py
      との真の統合検証(Legacy)は上記の理由により未実施
- [x] Caliber検証成功(Test A/B/C 3件PASS)
- [x] Audit Report更新(本追記)
- [ ] Human Gate提出 — 本追記自体がその提出物。app.py commitの可否については
      追加のご判断を仰ぐ

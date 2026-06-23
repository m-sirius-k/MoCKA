# GL7 Execution Kernel 仕様書 v1.0

Status: CONFIRMED（実コードからの抽出。新規ロジックの追加なし）
Date: 2026-06-23
対象実体: `structural/execution_governance.py`（GL7本体）、
`structural/governance_pipeline.py`（GL1〜GL7をMCP toolへ接続する単一窓口）
関連: `phi_os/event_gate.py`, `phi_os/gate_validator.py`（PHI-OS Semantic Audit Layer。GL7とは別の統治層）

## 1. 責務

`structural/execution_governance.py:6-11` が定義する責務はこれだけである：

> 推論が正しくてもRepositoryを破壊しないための実行制御。
> Execute前に必ずDry Runを行い、想定外があれば自動で停止する。

GL7は「データの正しさ」を見ない。「この行為（tool呼び出し）を実行してよいか」だけを見る。

## 2. Execution Pipeline（固定順序）

`execution_governance.py:13-15` で定義される固定順序：

```
Task -> Grounding(GL1) -> Policy確認(GL1) -> Conflict検出
     -> Dry Run -> Approval(Human Gate) -> Execute -> Verify
```

`pre_execution_check()`（同ファイル154-166行）が行うのは「機械的検査のみ」であり、
approved=Trueでも別途Human Gateの承認が必要、とコメントに明記されている
（156-157行）。GL7単体は完全な実行許可権を持たない。

## 3. 呼び出し経路

`governance_pipeline.py:67` のコメント通り、GovernancePipelineが
「全Tool呼び出しの単一窓口」であり、`execute_tool()`の先頭で`before_tool()`を呼ぶ。

```
MCP tool呼び出し
    ↓
GovernancePipeline.before_tool(tool_name, args)
    ↓ (READ_ONLY_TOOLS以外は全てGL7 Dry Run対象 = Default Deny)
ExecutionGovernanceEngine.pre_execution_check(action)
    ↓
dry_run(action) → check_abort_conditions(dry_run, action)
    ↓
allowed = (not aborts) and checklist.ok
```

`after_tool()`はtool実行後に呼ばれ、`record_execution()`で実行結果を記録する
（実行可否の判定はしない）。

## 4. Default Deny ルール（governance_pipeline.py:31-52）

```python
READ_ONLY_TOOLS = {
    "mocka_get_overview", "mocka_get_essence", "mocka_get_todo",
    "mocka_list_events", "mocka_read_event", "mocka_search",
    "mocka_get_incidents", "mocka_get_guidelines",
    "mocka_get_command_center", "mocka_check_utf8",
}

WRITE_TOOLS = {
    "mocka_write_event", "mocka_add_todo", "mocka_update_todo", "mocka_seal",
}
```

`READ_ONLY_TOOLS`に含まれないtool（未知のtoolを含む）は既定で
GL7 Dry Run対象＝統制下に置かれる（`governance_pipeline.py:31-32`の
コメントに明記）。`WRITE_TOOLS`は後方互換のため維持されている集合で、
実際の判定は`tool_name not in READ_ONLY_TOOLS`で行われる
（`WRITE_TOOLS`自体は判定ロジック内で直接参照されていない）。

## 5. Dry Run の入力（action dict）

`before_tool()`が`pre_execution_check()`へ渡す`action`（`governance_pipeline.py:108-113`）：

```python
scope = grounding.project_structure
approval = self.execution.pre_execution_check({
    "scope": scope,
    "expected_new_dirs": scope,
    "expected_max_changes": 400,
})
```

`scope`は`RepositoryGroundingEngine`が返す`project_structure`（現在の
リポジトリ直下のディレクトリ構造）。固定値ではなく、Grounding結果に
依存する動的な値である。

## 6. ABORT_CONDITIONS（execution_governance.py:37-43）

| 条件 | 発生箇所 | 発生条件 |
|---|---|---|
| `grounding_not_completed` | `check_abort_conditions:124-125` | `grounding.repository_root`が取得できない |
| `deletion_outside_scope` | `check_abort_conditions:127-132` | `dry_run.changed_files`（git status差分）のいずれかが`action.scope`内のいずれの文字列とも前方一致しない。名称は「削除」だが実際は変更ファイル全般（追加・変更含む）がscope外であれば発火する |
| `new_directory_detected` | `check_abort_conditions:134-140` | `dry_run.additions`内のパスのトップレベルディレクトリが、既存のリポジトリ直下ディレクトリ一覧にも`expected_new_dirs`にも含まれない |
| `unexpected_file_count` | `check_abort_conditions:142-150` | `dry_run.change_count`が`action.expected_max_changes`を超える。例外: 全変更が削除のみ（`git rm --cached`等のインデックスのみ除去）かつ件数1000以下の場合はバイパス |
| `encoding_mismatch` | `ABORT_CONDITIONS`リストに定義あり | `check_abort_conditions()`内に対応する判定コードが見当たらない（未実装、または別箇所で判定）。本仕様書では「定義済みだが本ファイル内に発火ロジック未確認」として記録する |

abortsが1件以上あれば`allowed=False`、`reason="GL7 abort: {aborts}"`
（`governance_pipeline.py:117-118`）。

## 7. FORBIDDEN_EXECUTIONS（execution_governance.py:26-35）

```python
FORBIDDEN_EXECUTIONS = [
    "create_new_folder_without_grounding",
    "create_mocka_3_or_similar",
    "infer_save_path",
    "change_encoding_without_confirmation",
    "infer_branch_name",
    "infer_path",
    "infer_repository_name",
    "bulk_rewrite_without_diff_review",
]
```

このリストは定義のみで、`execution_governance.py`内に`FORBIDDEN_EXECUTIONS`を
参照する判定コードは本ファイル内に見当たらない。クラスdocstring
（67-76行）の「存在確認なしでのフォルダ生成・ファイル生成・保存場所決定は禁止、
必ずGrounding後に決定する」という方針の根拠リストとして存在し、
実効はGrounding経由の運用ルールとして担保されている可能性がある
（本仕様書では断定しない）。

## 8. 実体験ログ（本仕様書作成の根拠となった実発火）

2026-06-23、`tests/`直下への新規ディレクトリ作成を伴う`mocka_write_event`
呼び出しが以下の理由でブロックされた：

```
{"error": "GL7_EXECUTION_BLOCKED", "reason": "GL7 abort: ['deletion_outside_scope']"}
```

`git status --short`で確認した実差分には、既存の未関連dirty state
（`PlanningCaliber/`等の背景同期差分）と新規`tests/`が混在していたが、
`deletion_outside_scope`は新規ディレクトリがscope外パスであったことに
起因する（`new_directory_detected`ではなく`deletion_outside_scope`が
先に発火したのは、チェック順序が`deletion_outside_scope`判定
（127-132行）→`new_directory_detected`判定（134-140行）の順であるため）。
対応として該当ファイルを既存scope内の`phi_os/tests/`へ再配置し、
再実行でブロックは解消された。

## 9. GL7とPHI-OSの境界（再確認）

GL7は`before_tool()`（実行前）でtool呼び出し自体を許可/拒否する。
PHI-OS（`phi_os/gate_validator.py`の`validate()`）はtool本体実行中
（`mocka_write_event`処理内）で、実際に書き込まれるイベント
ペイロードの5W1H整合性を検証する。両者は独立した統治層であり、
GL7通過は「行為が許可された」ことのみを意味し、PHI-OS側の検証結果
（payloadの正当性）を保証しない。

## 10. 既知の欠落（2026-06-23 追跡調査で確定・REAL_GAP）

リポジトリ全体を`grep`で追跡した結果、以下3点はいずれも**定義のみで実行経路に未接続**であることが確定した。

### 10.1 FORBIDDEN_EXECUTIONS（execution_governance.py:26-35）

リポジトリ全体の`.py`ファイルを検索した結果、`FORBIDDEN_EXECUTIONS`を
参照しているのは定義箇所（execution_governance.py:26）自体のみ。
`check_abort_conditions()`を含むいずれの関数からも参照されておらず、
このリストは現状なんの行為も実際には禁止していない。クラスdocstring
（67-76行）が掲げる「フォルダ生成・ファイル生成・保存場所決定は
存在確認なしに禁止」という方針は、コードレベルでは実効していない。

### 10.2 encoding_mismatch（execution_governance.py:40）

`ABORT_CONDITIONS`リストに名前が存在するのみ。`check_abort_conditions()`
（119-152行）のいずれの分岐も`aborts.append("encoding_mismatch")`を
実行しない。この条件は定義上は存在するが、一度も発火しない。

### 10.3 Human Gate

`execution_governance.py`の15行目・157行目のコメントが「Dry Run承認後、
別途Human Gateの承認が必要」と言及するが、`structural/`配下のいずれの
ファイルからもHuman Gate相当の処理を呼び出すコードは存在しない。

一方、`app.py`には別の機構として「PREVENTION QUEUE + DECISION」
（`app.py:2151-2289`）が実在する。`data/prevention_queue.json`に
`recurrence_registry.csv`由来の再発パターン提案を`PENDING`状態で
キューイングし、`/decision/approve`・`/decision/reject`エンドポイント
経由で`kimura_hakase`(human)が承認/却下する仕組みである
（`severity`がHIGH/CRITICALの項目は`app.py:2042-2044`の
`continue  # Human Gate`によりAUTO_APPROVEをスキップされる）。
ただしこの機構は「再発パターンに対する予防策の承認」を扱うもので、
GL7の`pre_execution_check()`が返す`approved=True`の後続フローとは
コード上一切接続されていない（`structural/`から
`prevention_queue`/`decision_approve`/`decision_reject`への参照ゼロ）。
つまり「GL7 Dry Run通過後の人間承認」という想定動作は、現状
実装されていない。

### 10.4 結論

GL7は`ABORT_CONDITIONS`として5条件、`FORBIDDEN_EXECUTIONS`として
8項目を掲げているが、実際に発火するのは
`grounding_not_completed` / `deletion_outside_scope` /
`new_directory_detected` / `unexpected_file_count`の4条件のみであり、
`encoding_mismatch`と`FORBIDDEN_EXECUTIONS`全8項目、および
Dry Run通過後のHuman Gate承認は、現状コードレベルで機能していない。

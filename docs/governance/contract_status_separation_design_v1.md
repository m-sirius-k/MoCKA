# contract_status分離設計 v1（TODO_385設計案）

Status: DESIGN_PROPOSAL（本文書は設計案の提示のみ。コード変更・データ変更は未実施）
Date: 2026-06-28
作成: Claude-sonnet-4-6
関連: TODO_384(調査・正規化), TODO_385(本設計), .claude/CLAUDE.md「TODO管理スキーマ」節

## 0. 本文書のスコープ

これは設計案の提示であり、実行ではない。

- 実施しないこと: MOCKA_TODO.jsonへの書き込み変更 / mocka_mcp_server.pyのコード変更 /
  既存13件のstatus値の実移行
- 実施すること: スキーマ定義案 / 移行マッピング表 / コード変更案(差分形式) / リスク整理

実行は本文書の内容について別途Human Gate(きむら博士)承認後、別TODOとして着手する。

## 1. contract_statusフィールドのスキーマ定義案

### 1.1 フィールド名・型

- フィールド名: `contract_status`（提案。`status_contract`等への変更可）
- 型: 文字列、9値のenum
  `DECISION_RECORDED / DONE_LOCKED / ALTERNATE_IMPLEMENTED / SPEC_OBSOLETE / SUPERSEDED / CLOSED / 確定 / Phase3停止中(設計待ち) / 調査済み`

### 1.2 適用対象

`category`が`設計成果物`または`基準仕様`であるTODO（後述1.4で再確認した13件）に限定する。
通常TODOには付与しない。

通常TODOの判定基準: `category`が上記2値以外、かつIDが`TODO_`接頭辞を持つもの
（.claude/CLAUDE.md「TODO管理スキーマ」節の既存区分に準拠）。

### 1.3 未付与時のデフォルト値

3案を提示する（推奨: 案A）。

| 案 | 値 | 利点 | 欠点 |
|---|---|---|---|
| A(推奨) | フィールド省略(キー自体を持たない) | JSON容量増加なし。既存の通常TODO 多数を一括変更せずに済む(後方互換性が最も高い) | `"contract_status" in todo`でのキー存在チェックが必要(`is None`では判定不可) |
| B | `null` | 「フィールドはあるが値がない」ことが明示的 | 全通常TODOにキー追加が必要(既存ファイルへの一括変更が発生) |
| C | 空文字`""` | enum検証ロジックを「空文字は許可」の1分岐で済ませられる | 「値が空」と「対象外」の意味的区別が曖昧になりやすい |

案Aを推奨する理由: 通常TODO(現状十数件以上)に一括でキーを追加する必要がなく、
既存データへの変更を最小化できる。`mocka_add_todo`/`mocka_update_todo`側で
`contract_status`が渡された場合のみキーを書き込む実装と整合する。

### 1.4 既存`status`フィールドとの関係

両方のフィールドを持つTODO（=Architecture Contract系13件）について、
`status`は通常5値（未着手/進行中/完了/保留/廃止）のいずれかに読み替える。
読み替えの個別対応は2章の移行マッピング表に示す。

読み替えの一般原則（提案）:

| contract_status | 読み替え後status(5値) | 理由 |
|---|---|---|
| DECISION_RECORDED | 完了 | 決定記録自体は完了した作業 |
| DONE_LOCKED | 完了 | 完了し凍結された状態 |
| ALTERNATE_IMPLEMENTED | 完了 | 別実装で概念実現済み。タスクとしては完了 |
| SPEC_OBSOLETE | 廃止 | 仕様として失効。タスクの継続性なし |
| SUPERSEDED | 廃止 | 後継仕様に置換済み。本TODOは非アクティブ |
| CLOSED | 完了 | 議論・検討が終結 |
| 確定 | 完了 | 設計が確定し作業完了 |
| Phase3停止中(設計待ち) | 進行中 | 一時停止だが廃止ではなく再開予定（指示書内の例示に従う。保留との区別は2.1の注記参照） |
| 調査済み | 完了 | 調査フェーズ完了 |

この一般原則は提案であり、個別TODOの実態と矛盾する場合は2章の表で個別に上書きする。

## 2. 既存13件の移行マッピング表

### 2.1 対象13件の確定根拠（一次データ照合・推測なし）

MOCKA_TODO.json全件をstatusフィールドで全文検索し、Architecture Contract系9語彙
（DECISION_RECORDED/DONE_LOCKED/ALTERNATE_IMPLEMENTED/SPEC_OBSOLETE/SUPERSEDED/
CLOSED/確定/Phase3停止中(設計待ち)/調査済み）のいずれかを持つTODOを全件抽出した結果、
実際には**16件**が該当した（下記「除外3件」参照）。

TODO_384のnoteは「C(13件・現状維持+文書化)」と明記しているため、16件と13件の差分3件を
.claude/CLAUDE.md「TODO管理スキーマ」節の定義文と照合して特定した。同節は対象を
「[ARCHITECTURE_CONTRACT/LOCKED]・category="設計成果物"・TODO_接頭辞を持たない独自IDのもの」
と説明している。この基準を`category`フィールドで機械的に適用すると、
`category="設計成果物"`(7件)と`category="基準仕様"`(6件)の合計が**13件**となり、
TODO_384の件数と一致した。これにより以下の除外3件が確定する。

**除外3件（`category="Architecture_Contract_Critical"`・`status=DONE_LOCKED`・IDが`TODO_`接頭辞を持つ）:**

- `TODO_HAB_GPT_CONNECTION_SPEC_V1`
- `TODO_PHASE5_6_GOVERNANCE_AUTHORITY_V1`
- `TODO_ARCHITECTURE_MAP_MCP_V1`

この3件は「変更不可（LOCKED）」として別格扱いされている最上位契約であり、
TODO_接頭辞を持つことからもCLAUDE.mdの「Architecture Contract系」定義（TODO_接頭辞を
持たない独自ID）には該当しない。今回のcontract_status分離スコープには含めない。

**除外1件（参考・9語彙のうち`調査済み`を偶然使用しているが対象外）:**

- `GL7-VALIDATION-MISSING-BUG`（`category="不具合"`、バグ調査TODOであり設計成果物ではない）

この識別ロジック（category基準）は本文書の解釈であり、きむら博士による確認・確定を
本表の実行前に必須とする。万一この解釈が誤っている場合、13件の内訳が変わる可能性がある。

### 2.2 移行マッピング表（13件）

| TODO ID | 現status値 | 移行後status(5値・提案) | 移行後contract_status(9語彙) |
|---|---|---|---|
| EXEC-LAYER-STD-V1 | ALTERNATE_IMPLEMENTED | 完了 | ALTERNATE_IMPLEMENTED |
| HAB-CONTRACT-LAYER-V1 | SPEC_OBSOLETE | 廃止 | SPEC_OBSOLETE |
| CONTRACT-INTEGRATION-TEST-SPEC-V1 | CLOSED | 完了 | CLOSED |
| UNIFIED-EXEC-PHASE-PLAN-V1 | SPEC_OBSOLETE | 廃止 | SPEC_OBSOLETE |
| REALITY-ALIGNMENT-HAB-GL7-V1 | ALTERNATE_IMPLEMENTED | 完了 | ALTERNATE_IMPLEMENTED |
| GL7-MINIMAL-IMPL-SPEC | ALTERNATE_IMPLEMENTED | 完了 | ALTERNATE_IMPLEMENTED |
| GL7-MIGRATION-POLICY-V1 | CLOSED | 完了 | CLOSED |
| PHI-OS-GATE-BASELINE-V1 | SUPERSEDED | 廃止 | SUPERSEDED |
| MOCKA-TWO-LAYER-OS-BASELINE-V1 | 確定 | 完了 | 確定 |
| GL7-KERNEL-SPEC-DOC-V1 | CLOSED | 完了 | CLOSED |
| CONTROL-MAP-V1-DECISION | SUPERSEDED | 廃止 | SUPERSEDED |
| CONTROL-MAP-V2-DECISION | DECISION_RECORDED | 完了 | DECISION_RECORDED |
| PHI-OS-HUMAN-GATE-STATE-MODEL-V1 | Phase3停止中(設計待ち) | 進行中 | Phase3停止中(設計待ち) |

注記（PHI-OS-HUMAN-GATE-STATE-MODEL-V1）: 「進行中」は本指示書内の例示
（Phase3停止中(設計待ち)→進行中等）に従った。ただし当該TODOのnoteには
「[Phase3後半着手前に意図的停止]」と明記されており、語感としては「保留」も妥当である。
どちらを採用するかは実行時にきむら博士の判断を求める。

## 3. mocka_mcp_server.py変更案（差分形式・未適用）

現状（TODO_384により導入済み）: `TODO_STATUS_ENUM`が通常5値+Architecture Contract系
9語彙=14値を1つの集合として保持していると想定される（本文書では実コードを変更しないため、
正確な変数名・行番号は実装時にgrepで再確認すること）。

### 3.1 enum分割案

```python
# 変更前（想定・現状の14値混在enum）
TODO_STATUS_ENUM = {
    "未着手", "進行中", "完了", "保留", "廃止",
    "DECISION_RECORDED", "DONE_LOCKED", "ALTERNATE_IMPLEMENTED",
    "SPEC_OBSOLETE", "SUPERSEDED", "CLOSED", "確定",
    "Phase3停止中(設計待ち)", "調査済み",
}

# 変更後案（2つの独立したenumに分割）
TODO_STATUS_ENUM = {"未着手", "進行中", "完了", "保留", "廃止"}

CONTRACT_STATUS_ENUM = {
    "DECISION_RECORDED", "DONE_LOCKED", "ALTERNATE_IMPLEMENTED",
    "SPEC_OBSOLETE", "SUPERSEDED", "CLOSED", "確定",
    "Phase3停止中(設計待ち)", "調査済み",
}
```

### 3.2 mocka_add_todo / mocka_update_todo インターフェース変更案

```python
# 変更前（想定・statusのみ）
def mocka_add_todo(id, title, status, priority, category, ...):
    if status not in TODO_STATUS_ENUM:
        raise ValueError(f"invalid status: {status}")
    ...

# 変更後案（contract_statusを任意パラメータとして追加）
def mocka_add_todo(id, title, status, priority, category, ...,
                    contract_status: str | None = None):
    if status not in TODO_STATUS_ENUM:
        raise ValueError(f"invalid status: {status}")
    if contract_status is not None and contract_status not in CONTRACT_STATUS_ENUM:
        raise ValueError(f"invalid contract_status: {contract_status}")
    todo_record = {..., "status": status}
    if contract_status is not None:
        todo_record["contract_status"] = contract_status  # 1.3案A: 未指定時はキー自体を持たない
    ...

def mocka_update_todo(id, status=None, contract_status=None, ...):
    if status is not None and status not in TODO_STATUS_ENUM:
        raise ValueError(f"invalid status: {status}")
    if contract_status is not None and contract_status not in CONTRACT_STATUS_ENUM:
        raise ValueError(f"invalid contract_status: {contract_status}")
    ...
```

備考: 上記は概念差分であり、実際のパラメータ名・既存関数のシグネチャ・JSON書き込みロジックは
実装着手時に`mocka_mcp_server.py`の現物を読んで確認すること（本設計案は実コードを参照せずに
作成した骨格案であり、関数シグネチャの完全な再現性は保証しない）。

## 4. 移行実行時のリスク・注意点

### 4.1 記録義務

- 本移行（13件のstatus/contract_status書き換え、mocka_mcp_server.pyのenum分割）は
  通常のファイル変更と同等に扱い、CHANGE_START/CHANGE_DONEを必須とする
  （.claude/CLAUDE.md「運用ルール」節、TODO_384裁定に基づく）。
- 13件一括処理であっても、CHANGE_START一回・CHANGE_DONE一回で13件分をまとめて記録してよいか、
  TODOごとに個別記録すべきかは実行前にきむら博士の確認を得ること。

### 4.2 既存note/reference_eventとの整合性確認事項

- 13件のnoteには「[再分類]」「[後継TODOへ移行]」「[役割再定義・実装順序は不変]」等の表現で
  現状のstatus値（SPEC_OBSOLETE/SUPERSEDED等）を前提とした記述が含まれている。
  status値そのものを書き換えるわけではなくcontract_statusへ複製するだけであれば矛盾は
  生じないはずだが、移行後status(5値)を新たに付与する際、note本文の文脈（例:
  「[再分類]」という言葉が指す対象）と新status値の対応が読み手に分かりにくくなる
  可能性がある。移行時にnote末尾へ「[contract_status分離移行: status={旧値}→{新値},
  contract_status={旧値}を保持]」等の移行注記を追記することを推奨する。
- `reference_event`欄が他のArchitecture Contract系TODOのIDを指している連鎖がある
  （例: `HAB-CONTRACT-LAYER-V1.reference_event = "EXEC-LAYER-STD-V1"`、
  `CONTROL-MAP-V2-DECISION.reference_event = "CONTROL-MAP-V1-DECISION"`）。
  この参照網はIDベースであり、IDを変更しない前提の本設計では破壊されないが、
  移行作業時に誤ってID自体を変更しないよう注意すること。
- 2.1で識別した「除外3件」（TODO_HAB_GPT_CONNECTION_SPEC_V1等）は、`reference_event`や
  noteの記述上、13件のいずれとも直接の依存関係は確認できなかった（本文書作成時点の
  全文照合による）。ただし将易の確認はきむら博士の判断を優先する。

### 4.3 スコープ境界の再確認

- 本設計はstatus/contract_statusという2フィールドの分離のみを対象とする。
  `category`の再編（"設計成果物"と"基準仕様"を統合するか等）は本設計のスコープ外。
- 13件の中身（仕様の正しさ自体）の再検証は行わない。あくまでメタデータ（状態管理）の
  正規化のみが対象。

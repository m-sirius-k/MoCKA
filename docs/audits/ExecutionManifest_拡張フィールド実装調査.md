# Execution Manifest 拡張フィールド実装可否調査

作成日: 2026-07-08
作成者: Claude（くろこ）
位置づけ: 指示書「R01査読対応・拡大調査（v2最適化版）」TASK-3 成果物
調査範囲: 調査のみ。実コード変更は行っていない。
適用条件: 監査官R01裁定（TASK-2結果確認、2026-07-08）で追加指定されたExecution Manifest
確認項目（execution_id/decision_id/human_gate_event_id/approval_state/seal_target/
executor/timestamp/ledger link）を主軸に、指示書原文の6項目調査と統合して実施した。
一次データ: governance/seal_governance_gate.py, governance/seal_governance_wrapper.py,
governance/human_gate_continuity.py, phi_os/integrity.py, phi_os/human_gate.py,
data/decisions/decision_ledger.jsonl。

---

## 0. 調査結論サマリー

**「Execution Manifest」に相当する実体は、既に3系統ばらばらに存在している。**
統一されたスキーマはまだ存在しないが、いずれも `execution_id` を採番の起点とする
共通の設計思想を持つ点は一致している。

| # | 実装 | 用途 | 永続化先 |
|---|---|---|---|
| 1 | `governance/seal_governance_gate.py` `_record_decision_unit()` | 本番MANUAL_SEAL用Decision Unit | `data/decisions/decision_ledger.jsonl`（本番） |
| 2 | `governance/seal_governance_wrapper.py` `_record_decision_unit()` | sandbox検証用（Phase C-1、本番非接続） | sandbox配下の`decision_ledger.jsonl`（本番と分離） |
| 3 | `governance/human_gate_continuity.py` `PendingDecisionUnit` | MCP断線時のDeferred Human Gate（Phase C-4） | `data/decisions/pending_decision_units.jsonl`（Decision Ledgerとは意図的に分離） |

**これはTASK-2で確認した「並立するHuman Gate機構」と同型のパターンである。**
Execution Manifestを新設する場合、これら3系統のどれかへ機械的にフィールドを
追加するのではなく、まずこの3系統自体の統合要否を判断する必要がある
（本調査の範囲外、TASK-7で扱う）。

**最重要確認事項（監査官R01指定）: `human_gate_event_id`に相当する実フィールドは
現状どこにも存在しない。** `human_gate_continuity.py`の`human_gate_event_status`は
値が`"NOT_ISSUED"`のみを取りうるステータス列であり、実際のHuman Gate承認イベントの
IDを保持するフィールドではない。これはIC_20260708_004（PHI-OS Human Gate未接続
Execution Path）の裏付けとなる、独立した2件目の技術的証拠である。

---

## 1. 監査官R01指定8項目の確認結果

| 項目 | 存在 | 取得元 | 備考 |
|---|---|---|---|
| execution_id | ○ | 3系統いずれも`f"EXEC_{タイムスタンプ}_{uuid4().hex[:8]}"`形式で採番。実装は3箇所に重複（別モジュールがそれぞれ独自にこの文字列を生成しており、共有関数化されていない） | - |
| decision_id | ○（seal_governance_gate.py/wrapper.pyのみ） | `f"DC_{execution_id}"`としてdecision_ledger.jsonlへ記録。ただしDECISION_LEDGER_SCHEMA_v1.mdの採番規則（`DC_YYYYMMDD_NNN`）とは異なる形式であり、TASK-1/TASK-2で作成したDC_20260708_00N系列（本調査で新規追記したDC_20260708_006/007等）とはID体系が非互換（要確認事項として5章に記載） | human_gate_continuity.pyのPendingDecisionUnitにはdecision_idフィールド自体が存在しない（request_id/execution_idのみ） |
| **human_gate_event_id** | **×（存在しない）** | 該当なし | `human_gate_continuity.py`の`human_gate_event_status`（値は"NOT_ISSUED"のみ）が唯一の関連フィールドだが、実際のevent_idを保持しない。`phi_os/human_gate.py`は`HG{date}_...`形式のevent_idを生成する能力を持つが、seal_governance_gate.py/wrapper.pyのいずれからも呼ばれておらず、生成されたevent_idがExecution Manifest相当の記録に渡る経路が存在しない。IC_20260708_004の技術的根拠。 |
| approval_state | 部分的 | seal_governance_gate.py: `decision`フィールド（"approved"/"aborted"の2値、GL7の機械的判定のみを反映）。human_gate_continuity.py: `governance_state`（"WAITING_FOR_HUMAN_GATE"固定、他状態への遷移コードが存在しない） | いずれも「GL7のALLOW/DENY」または「Human Gate待ち」を表すのみで、`phi_os/human_gate.py`の実際のAPPROVED/REJECTED状態を反映するフィールドは存在しない |
| seal_target | ×（記録されない） | `execute()`/`request_seal()`の引数`scope`/`action_scope`はdry run判定にのみ使用され、`_record_decision_unit()`が書き込むentry辞書には含まれていない（governance/seal_governance_gate.py 125-146行を確認、scope/action_scopeへの言及なし） | Execution Manifest新設時は新規追加が必要な項目 |
| executor | ×（明示フィールドなし） | `approved_by: "system:seal_governance_gate"`（固定文字列）が最も近いが、これは「どのモジュールが承認したか」であり「誰が実行を要求したか」ではない。TASK-3原文が求める`actor_identity_hash`と対応する概念だが、現状は固定文字列のみで実行者を区別できない | 新規追加が必要 |
| timestamp | ○ | `change_start`/`change_done`/`recorded_at`/`approved_at`など複数フィールドで確認可能（ISO8601、timezone-aware） | - |
| ledger link | ○（seal_governance_gate.py/wrapper.pyのみ） | decision_ledger.jsonlへの追記自体がledger link。ただしhuman_gate_continuity.pyのPendingDecisionUnitはDecision Ledgerとは意図的に分離されたpending_decision_units.jsonlに記録されており、両者間のlink（相互参照フィールド）は存在しない | - |

---

## 2. 指示書原文6項目の確認結果

| 項目 | 取得可否 | 取得元候補 |
|---|---|---|
| human_gate_state_hash | ×（未実装。ただし土台は存在） | `phi_os/human_gate.py`の`get_state(request_id)`が状態文字列を返す。これをハッシュ化する処理は存在しない。実装コスト: 小（既存関数の戻り値をhashlib.sha256に通すのみ） |
| decision_policy_version | △（近い概念は存在するが別軸） | `interface/gate_policy.py`の`POLICY_VERSION`（現在"1.0"）はEvent Gateの許可チャネルポリシーのバージョンであり、Decision（裁定）のポリシーバージョンではない。DECISION_LEDGER_SCHEMA_v1.mdにも「バージョン」フィールドはdecision_id採番規則側になく、スキーマ自体のバージョン（v1.0.0）のみ。Decision Policy固有のバージョン管理機構は本調査では発見できなかった（推測: 未実装） |
| ledger_head_hash | ○（実装済み、転用可能） | `phi_os/integrity.py`のevent_signaturesテーブルが、events.dbの各行についてsha256ベースのhash chain（current_hash/previous_hash）を既に実装している（Phase5-2）。events.db側のchain headを取得する関数を追加すれば転用可能。ただしdecision_ledger.jsonl側には同等のhash chainが存在しない（append-onlyではあるが署名なし）。Execution Manifestがdecision_ledger.jsonlの状態を指すなら追加実装が必要 |
| actor_identity_hash | ×（未実装） | 上記1章「executor」と同一の欠落。`who_actor`列はevents.db側には存在する（5W1Hの一部）が、seal_governance_gate.py系のDecision Unit記録には転記されていない |
| execution_scope_hash | ×（未実装） | 上記1章「seal_target」と同一の欠落。scope自体が記録されていないため、そのハッシュも当然存在しない |
| parent_event_id | △（部分的） | events.db側は`related_event_id`列（hash chainのprevious_hash用途、integrity.py参照）を持つが、これは「直前のDBレコード」であって「このexecutionを引き起こしたAUTO_SEAL_PENDINGイベント等のevent_id」ではない。意味が異なる転用のため、新規フィールドとして区別して追加する必要がある |

---

## 3. 既存ログスキーマとの重複・矛盾

- decision_id採番規則の不一致（1章参照）: DECISION_LEDGER_SCHEMA_v1.mdの`DC_YYYYMMDD_NNN`形式と、seal_governance_gate.pyの`DC_EXEC_YYYYMMDDHHMMSS_{uuid8}`形式が混在している。本調査中に作成したDC_20260708_006/007（TASK-1/TASK-2の記録補完）は前者の形式に従っているが、SealGovernanceGateが自動生成するDecision Unitエントリは後者の形式であり、decision_ledger.jsonl内でdecision_idの形式が統一されていない状態が既に発生している（実データで確認済み、推測ではない）。
- `pending_decision_units.jsonl`（human_gate_continuity.py）は意図的にdecision_ledger.jsonlと分離されている（3章冒頭のdocstring根拠）。Execution Manifestを新設する場合、この分離方針を維持するか統合するかの設計判断が必要。
- Decision Unit拡張フィールド（execution_id/change_start/change_done/artifact_hash/seal_hash/aborts）は、DECISION_LEDGER_SCHEMA_v1.mdが定義する必須フィールド（decision_id/title/context/alternatives/decision/rationale/impact/approved_by/approved_at/status）に対する**後方互換な追加フィールド**として設計されている（seal_governance_gate.pyのコメントで明記）。この設計方針自体はExecution Manifestの6+8項目追加にも応用可能と考えられる（推測を含むが、既存の前例に沿った自然な拡張と言える）。

---

## 4. 追加実装規模の見積もり（概算）

| 項目群 | 規模 | 理由 |
|---|---|---|
| human_gate_event_id, approval_state(正規化), executor(actor_identity_hash) | 中 | 単純なフィールド追加ではなく、SealGovernanceGate.execute()から`phi_os/human_gate.py`を実際に呼び出す配線変更を伴う（TASK-2で提案した「GL7 ALLOW後にhuman_gate.pyのsubmit()を呼ぶ」設計と同一の変更が前提になる） |
| seal_target(execution_scope_hash) | 小 | 既存の`scope`/`action_scope`引数を`_record_decision_unit()`のentry辞書に追加するだけで足りる |
| human_gate_state_hash | 小 | `get_state()`の戻り値をhashlib.sha256に通すユーティリティ関数を1つ追加するのみ |
| ledger_head_hash | 中 | events.db用のchain-head取得は流用可能。decision_ledger.jsonl用は未実装のため新規のhash chain機構が必要 |
| parent_event_id | 小 | Decision Unit記録時に、呼び出し元（AUTO_SEAL_PENDING等）のevent_idを引数として受け取り記録するだけで足りる。ただし呼び出し元コード（app.py auto_audit_loop等）側の変更も必要 |
| decision_policy_version | 中〜大 | 対応するDecision Policyバージョン管理機構自体が現状存在しないため、Manifest側のフィールド追加以前にPolicy側の設計が必要（本調査では既存実装を発見できなかった） |
| decision_id採番規則の統一 | 中 | 3章の不一致を解消する場合、既存decision_ledger.jsonl内のレコードとの後方互換性を保ったまま新規レコードの採番規則を統一する設計が必要 |

---

## 5. 推測・未確認の明示

- decision_policy_versionに対応する既存機構の不在は、コードベース全体のgrep（"policy_version"等）に基づくが、命名が異なる形で実質的に存在する可能性は完全には排除できない（推測）。
- Decision Unit拡張フィールドの後方互換設計方針がExecution Manifestにそのまま適用できるという評価は、既存の設計パターンからの類推であり、実装時に別の制約が見つかる可能性がある。
- 3系統（seal_governance_gate.py/wrapper.py/human_gate_continuity.py）の統合要否はTASK-3の範囲外であり判断していない。

---

## 6. 次工程への申し送り

- `human_gate_event_id`の欠落は、TASK-2のIC_20260708_004と技術的に同一根拠を持つ。
  TASK-7横断マッピングでは、IC_20260708_004の解消（GL7 ALLOW後にHuman Gateへ接続する配線変更）
  と、Execution Manifestへの`human_gate_event_id`追加は同一の実装作業として扱えることを明記する。
- decision_id採番規則の不一致（3章）は、Execution Manifestとは独立した既存の技術的負債として、
  TASK-7またはHuman Gate判断で別途整理を検討すること。
- decision_policy_versionは、対応するPolicy側の設計（TASK-3の範囲外）が先行して必要。

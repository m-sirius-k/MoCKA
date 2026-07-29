# PHI-OS / MoCKA Integration Adapter — Implementation Plan v0.1

**Status:** PROPOSAL(計画文書のみ。コード作成・API実装・Runtime変更・MoCKA変更はまだ行わない)
**位置づけ:** `DC_20260729_013`(Candidate A、PHI-OS Adapter Pattern、Approved with Conditions)後続。Implementation Plan(Plan → Implementation → Verification → Sealの最初のステップ)。
**拘束条件(D-04の条件、逸脱時はHuman Gateへ差し戻し)**:
- D-02 Translation Boundary — Allowed: Interface transformation / Request-Response transformation / Context transfer / Evidence reference linking / Runtime connection management。Forbidden: Decision generation / Policy modification / Authority judgment / Human Gate replacement / Evidence modification
- D-03 Authority Ownership — PHI-OS(Runtime Coordination/Execution Control/Human Gate Routing)、MoCKA(Evidence Management/Decision Evidence/Audit Intelligence/Governance Analysis)、Human(Architecture Authority/Policy Change Approval/Irreversible Decision)。Adapterはこの3者いずれの権限も持たない

**未解決の残存項目(発見、本文書で確定させない)**: `DC_20260729_013`のD-01〜D-04にAdapterの具体的ファイルパス・モジュール名は含まれていない。§1でCandidate2案を提示するが、いずれの採否も本文書では決定しない(Architecture決定そのものではなく、Human Gate承認済みのCandidate Aパターン内の実装詳細の選択であるため、軽微な確認事項として次回応答で提示する)。

---

## 1. Adapter仕様

### Confirmed(D-02/D-03から継承、変更不可)

- Adapterの責務はTranslation Boundaryのみ。判断生成・ポリシー変更・権限判断・Human Gate代替・証跡改変のいずれも行わない
- Adapterは`phios/runtime/`4ファイル(Runtime Foundation、`DC_20260729_011`で凍結)を呼び出し元としてのみ使用し、変更しない
- Adapterは`phios/phl/relay_client.py`(RC-011、commit `9faa421`)を無変更のまま呼び出す

### Proposal(配置候補、未確定)

| 候補 | パス | 根拠 |
|---|---|---|
| 候補1 | `phios/bridge/mocka_integration_adapter.py`(新規パッケージ) | Runtime Foundation(`phios/runtime/`、凍結対象)・既存Adapter(`phios/adapter/`、AIプロバイダ用、別責務)のいずれとも独立させ、命名衝突(Decision Support Matrix §3 Candidate B Unknown項目で指摘した"Relay"名称衝突と同種のリスク)を避ける |
| 候補2 | `phios/phl/mocka_adapter.py`(RC-011と同一パッケージ内) | Adapterの唯一の下流依存先がRC-011であるため、物理的に隣接させることで依存関係を追いやすくする |

**注記:** `phios/adapter/`(既存、`adapter_interface.py`/`anthropic_adapter.py`/`openai_adapter.py`)はAIプロバイダ切替用であり、本Integration Adapterとは責務が異なる。同一ディレクトリへの配置は責務混同のリスクがあるため候補から除外した。

### Interface概形(Proposal、シグネチャ確定ではない)

Adapterが提供する操作はRC-011(`relay_client.py`)の既存公開関数(State/Decision/Decision Summary/Audit Status問い合わせ)をRuntime Foundation側の型(`phios/runtime/controller_core.py`の`State`/`TransitionRecord`等)との間で変換するラッパーに限定する。新規の判断ロジック・分岐条件は追加しない(D-02 Forbidden: Decision generation)。

---

## 2. API境界

### Confirmed

- 唯一の外部通信経路はRC-011経由の`http://localhost:5002/mcp`と`http://localhost:5000/api/gate/audit`(実測、変更なし)
- Adapterは新規の外部エンドポイントを持たない(D-02 Forbiddenの"Authority judgment"を新設APIとして公開しないことを含む)

### Proposal

- Adapterの公開関数は「Runtime Foundation型 ↔ RC-011型」の双方向変換に限定する(例: `to_runtime_state(relay_response) -> State`、`to_relay_query(controller_state) -> dict`)
- Adapterはevidence insufficient判定をRC-011から受け取った結果をそのまま伝播するのみとし、独自の閾値判定・再解釈を行わない(D-02 Forbidden: Decision generation / Authority judgment)

---

## 3. Test Plan

### Confirmed(回帰対象、既存)

- Runtime Foundation baseline 242テスト、RC-011 23テストへの回帰なしを維持する(`PHI_MOCKA_INTEGRATION_SCOPE_PROPOSAL_v0.1.md`§3の成功基準を継承)

### Proposal(新規テスト、未実装)

- Adapter単体テスト: 型変換の正当性(Runtime Foundation型⇄RC-011型)、evidence insufficient伝播の正当性(判定を生成せず、そのまま伝播することの確認)
- Runtime-Adapter結合テスト: `phios/runtime/tests/test_runtime_integration.py`と同様の形式で、AdapterがController/Event/State遷移に対し非干渉であることを確認(`memory_boundary.py`のnon-interference原則をAdapterにも適用)
- Adapter-RC-011結合テスト: RC-011の既存23テストのモックを再利用し、Adapter経由での呼び出しが既存の read-only tool allowlist・fail-closed設計を迂回しないことを確認
- 禁止事項テスト(Confirmed境界の実測維持): AdapterがDecision Ledger書き込み・Human Gate関数・MoCKA本体ファイルのいずれも呼び出さないことを、importグラフ検査(既存`phios/runtime/*.py`のno-MoCKA-import確認手法を踏襲)で保証する

---

## 4. Migration手順

### Confirmed(既存資産、無変更)

- Runtime Foundation・RC-011は本Migrationの対象外(いずれも凍結・既存のまま)

### Proposal

1. §1候補パスの確定(Human Gate相当ではないが、次回応答時に博士へ簡易確認)
2. CHANGE_START記録 → Adapterファイル新規作成(Writeツールのみ)→ `mocka_check_utf8`検証
3. Adapter単体テスト作成・実行(§3)
4. Runtime-Adapter結合テスト・Adapter-RC-011結合テスト作成・実行(既存242+23テストの回帰確認を含む)
5. 全テストpass確認後、CHANGE_DONE記録
6. `mocka_git_safe_commit()`経由でcommit(push=False)
7. Decision Ledgerへ実装完了を追記(`related_events`にCHANGE_DONE event_idを追加する形での更新、または新規Decision行としての記録は博士判断)

**MoCKA/Memory/Relay/Orchestraへの展開は対象外**(`DC_20260729_012`の統合順序に従い、MoCKA接続の検証完了後に別途Human Gateを経て着手)。

---

## 5. Rollback条件

### Confirmed(既存の原則を継承)

- Adapterの追加はRuntime Foundation・RC-011のいずれのファイルも変更しないため、Adapterファイル自体の削除のみでRollback可能(既存資産への副作用なし)

### Proposal

以下のいずれかに該当した場合、実装を中断しRollbackする:

- **RB-1**: Adapter単体テストまたは結合テストが既存242+23テストのいずれかを回帰させた場合
- **RB-2**: Adapterの実装がD-02 Forbidden(Decision generation / Policy modification / Authority judgment / Human Gate replacement / Evidence modification)のいずれかに該当する挙動を持つことが判明した場合(§3禁止事項テストで検出)
- **RB-3**: AdapterがMoCKA側モジュールを直接importする、またはRC-011以外の経路でMoCKAへ接続する実装になった場合
- **RB-4**: Gap-001(REJECTED状態不足)を暗黙に解消する形で実装された場合(Pending維持の原則違反)

Rollback手順: 新規作成したAdapterファイル・テストファイルを削除し、Runtime Foundation・RC-011は無変更のため復旧作業は不要。CHANGE_START/CHANGE_DONEの記録は残し、Rollback理由をIncidentとして`mocka_write_event`(Runtime Divergence相当)で記録する。

---

## Knowledge Lineage

**Document:** PHI_MOCKA_INTEGRATION_ADAPTER_IMPLEMENTATION_PLAN_v0.1.md
**Status:** PROPOSAL
**Created:** 2026-07-29
**Origin:** `DC_20260729_013`(D-04: Approved with Conditions)の次工程指定を受けて作成。
**Parent Documents:** `DC_20260729_013`(Decision Ledger)、`docs/audits/PHI_MOCKA_INTEGRATION_HUMAN_GATE_DECISION_RECORD_v0.1.md`(commit `972719aa2`)、`docs/audits/PHI_MOCKA_INTEGRATION_DECISION_SUPPORT_MATRIX_v0.1.md`(commit `8d5ca81a6`)
**Derived From:** `DC_20260729_013`のD-02(Translation Boundary)・D-03(Authority Ownership)を実装詳細レベルへ展開
**Supersedes:** なし
**Reason For Creation:** DC_20260729_013で承認された境界内で、実装(次工程)に着手可能な具体仕様・Test Plan・Migration手順・Rollback条件を、コードを書く前に固定するため。

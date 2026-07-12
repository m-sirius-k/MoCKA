# PHI-OS Event Gate との整合性検証（Gate HOLD拡張 影響範囲調査）

作成日: 2026-07-08
作成者: Claude（くろこ）
位置づけ: 指示書「R01査読対応・拡大調査（v2最適化版）」TASK-2 成果物
調査範囲: 調査のみ。Gate/Policy実コードへの変更は行っていない。
適用条件: 監査官R01裁定（未検出バイパス事後処理、2026-07-08）で指定されたTASK-2実施条件
（発生→記録→判断→実行→証跡の連続性確認／Ledger接続性確認／router・save系4点確認）を適用する。
一次データ: phi_os/event_gate.py, phi_os/human_gate.py, interface/gate_policy.py,
structural/execution_governance.py（GL7）, governance/seal_governance_gate.py,
governance/mocka_git_safe_commit.py, app.py（/decision/approve, /decision/reject, /audit/seal）。

---

## 0. 調査結論サマリー

**「PHI-OS Event Gate」という単一のGateは存在しない。役割の異なる複数のGate/承認機構が
並立しており、それぞれ「単一の書込経路（Single Write Path）」は個別に守られているものの、
機構間の接続（あるGateのALLOW/HOLD判定が他の機構から見て意味を持つか）は制度として
保証されていない。** 具体的には次の4系統を確認した。

| # | 機構 | 責務 | 状態モデル | 実行への接続 |
|---|---|---|---|---|
| 1 | `phi_os/event_gate.py`（Event Gate） | イベント（記録）のSingle Write Path | なし（受理/拒否のみ） | 実行判断は行わない（記録専用） |
| 2 | `phi_os/human_gate.py`（Human Gate状態機械） | 汎用承認エンジン | PENDING/APPROVED/REJECTED/EXPIRED/CANCELED（event-sourced） | **承認イベントの記録のみ。approve()自体は何も実行しない**（呼び出し元が別途実行する設計、現状はReview Gateユースケースのみ接続） |
| 3 | `app.py` `/decision/approve` `/decision/reject` | Prevention Queue（recurrence対応案）専用の承認 | pending/approved/rejected（JSONファイル、`PREVENTION_QUEUE_PATH`） | 承認後、ping_generator.py実行のみ（Core System File変更やseal実行とは無関係） |
| 4 | `structural/execution_governance.py`（GL7） + `governance/seal_governance_gate.py`（SealGovernanceGate） + `mocka_git_safe_commit.py`の`human_gate_override_event_id` | 実行可否の機械的検査＋git commit実行制御 | ALLOW/DENY（HOLD概念なし） | **GL7のALLOWのみでSealGovernanceGate.execute()が直ちにanchor_update.pyを実行する。GL7自身のdocstringは「approved=TrueでもHuman Gateの承認が別途必要」と明記しているが、呼び出し元(app.py `/audit/seal`)はこの追加承認を要求していない（2章で詳述、最重要発見）。** |

機構1（Event Gate）はTASK-1・過去監査で繰り返し検証されておりSingle Write Pathは技術的に
確認できた。**問題は機構2〜4の間、および機構4内部にある。**

---

## 1. Single Write Path の実装箇所（Event記録層、機構1）

`phi_os/event_gate.py`の`process_event()`（115-135行）が唯一の保存経路であることをコード
コメントで確認した：

> 「Flask route(/api/gate/event)とMCP server(mocka_write_event)のいずれの呼び出し元からも、
> トランスポート(HTTP/インプロセス)を問わずこの関数を経由しなければならない。これ以外に
> events保存を行う経路は制度上存在しない。」（event_gate.py:120-122）

`app.py`の`append_event()`（242行〜）も、TODO_347以降はLocal Buffer経由で非同期に
`process_buffered_event()`（event_gate.pyの一部）へ収束する設計であることをコメントで
確認した（「Gate直叩きの同期書き込みは廃止。Local Bufferへpushし...非同期でGate経由で
SQLiteへ永続化する」）。`interface/gate_policy.py`の`compute_gate_audit()`は、この経路を
逸脱した直接書込み（`_source`列がlive/buffered/許可Directのいずれでもない行）を
「violation」として定量的に検出する仕組みを持つ。

**確認結果: Event（記録）レベルのSingle Write Pathは制度・実装ともに存在し、監査可能である。
これは指示書がいう「HOLD理想経路」図の"Ledger Write"部分の受け皿としては十分に機能する。**

---

## 2. HOLDの理想経路と現状のギャップ（最重要）

### 2.1 指示書が示す理想経路

```
Event
  |
PHI-OS Gate
  |
Decision
  |
  +-- ALLOW --> 実行
  |
  +-- DENY  --> 停止
  |
  +-- HOLD  --> Ledger Write --> Human Queue
```

### 2.2 現状で最も近い実装: GL7 + SealGovernanceGate

`structural/execution_governance.py`（GL7）の`pre_execution_check()`は、まさに
ALLOW/DENYを返す実装を持つ（211-222行）。dry run（git status差分の機械的検査:
新規ディレクトリ検出・encoding不整合・スコープ外変更・変更件数超過）の結果に基づき、
`_emit_gl7_event("ALLOW"/"DENY", ...)`をphi_os/event_bus経由でイベント化する。

しかし**GL7にHOLD状態は存在しない**。ALLOW/DENYの二値のみである。かつ、
`pre_execution_check()`のdocstring自身が次のように明記している（execution_governance.py:206行）:

> 「approved=TrueでもHuman Gateの承認が別途必要(本関数は機械的検査のみ)」

これはGL7設計者自身が「機械的ALLOW ≠ 人間承認」を認識していたことを示す一次証拠である。

### 2.3 確認された最重要ギャップ: `/audit/seal`（MANUAL_SEAL）

`app.py`の`/audit/seal`エンドポイント（2150-2176行）は、`SealGovernanceGate().execute()`
（governance/seal_governance_gate.py）を呼び出す。`SealGovernanceGate.execute()`
（70-100行）の実装は:

```
GL7.pre_execution_check(action)
  |
  +-- approved=False --> Decision Unit記録(aborted) --> 403応答、実行なし
  |
  +-- approved=True  --> ただちにanchor_update.pyをsubprocess実行(_run_seal_script)
                          --> Decision Unit記録(approved) --> 200応答
```

**GL7自身が「Human Gateの承認が別途必要」と明記しているにもかかわらず、
`/audit/seal`にもSealGovernanceGate.execute()にも、その追加承認（phi_os/human_gate.pyの
PENDING/APPROVE経由、あるいはhuman_gate_override_event_id相当の確認）を要求する
コードは存在しない。** `app.py`自体にも認証ミドルウェア（`@app.before_request`等）が
一切存在しないことを確認した（grep結果、該当なし）。

これは名称こそ「MANUAL_SEAL」だが、実態は「機械的ドライラン検査を通過すれば
POSTリクエスト1回でCore System Fileを含む変更をcommit・push相当まで進められる
経路」である（`SealGovernanceGate._record_decision_unit()`がDecision Ledgerへ
`approved_by: "system:seal_governance_gate"`という**システム主体**の承認記録を
書き込む点にも注意。人間の承認者名ではない）。

**指示書がいう「二重Gate化」パターン（Gate A→HOLD→Gate B→ALLOW→実行）そのものではないが、
本質的に同型の危険パターンである: 「Gate Aの契約上ALLOWは不十分（Human Gate必須）と
明記されているのに、呼び出し元がGate AのALLOWのみで実行してしまう」。これはHOLD新設を
設計する際、必ず解消しておくべき既存の欠陥として扱うべきである。**

### 2.4 「HOLD」に相当する既存概念の所在

`phi_os/human_gate.py`のPENDING状態（STATES定義、23行）は、指示書がいうHOLDと
概念的に最も近い。ただし現状の接続先は「Review Gate」（Reason Unit → Knowledge Assets
昇格審査、TODO_396）のみであり、GL7・SealGovernanceGate・AUTO_SEAL系のいずれからも
呼び出されていない（コードベース全体でgrep確認: `phi_os.human_gate`のimportは
`phi_os/tests/test_human_gate.py`とhuman_gate.py自身以外に存在しない）。

**AUTO_SEAL系が2026-07-08是正で導入した「AUTO_SEAL_PENDING」イベントは、
`phi_os/human_gate.py`のPENDING状態機械とは無関係の、events.dbへの単純なイベント
記録（get_buffer().push()）に過ぎない。** 名前が同じ「PENDING」であるため混同されやすいが、
以下の点で別物である。

| | phi_os/human_gate.pyのPENDING | AUTO_SEAL_PENDING(app.py/watchdog) |
|---|---|---|
| 実体 | human_gate_eventsテーブルの状態(event-sourced) | events.dbへの1回限りのイベントレコード |
| 遷移可能な次状態 | APPROVED/REJECTED/EXPIRED/CANCELED(TRANSITIONS辞書で制御) | なし(状態機械ではない、記録して終わり) |
| 承認API | `/api/human_gate/approve`等、専用HTTP API | 存在しない(人間がSlack/chat等の別経路で指示し、`human_gate_override_event_id`を人力で特定してmocka_git_safe_commitへ渡す運用) |

---

## 3. 二重Gate化リスク箇所一覧（具体的コード箇所）

| # | 箇所 | リスクの型 | 詳細 |
|---|---|---|---|
| 1 | `app.py:/audit/seal` → `SealGovernanceGate.execute()` | **GL7契約違反型**（最重要、2.3節） | GL7の「ALLOWのみでは不十分」という自己申告契約を呼び出し元が守っていない。HOLD新設時、この経路にもHOLD分岐を挿入しない限り、新設したHOLDを迂回する既存の穴として残り続ける。 |
| 2 | `governance/mocka_git_safe_commit.py`の`human_gate_override_event_id`パラメータ | **検証なきoverride型** | 渡された`event_id`文字列が実在するか、実際にHuman Gate相当の承認を表しているか、mocka_git_safe_commit()は一切検証しない（コード上、単にcommitメッセージへ埋め込むのみ）。理論上、`_auto_approve_prevention()`が生成した`approved_by="AUTO_GATE"`のイベントIDや、無関係の任意イベントIDを渡しても機械的には通ってしまう。HOLD新設時、HOLD解除の正当性をこのoverrideパラメータ経由で偽装できないよう、参照先イベントの検証（例: decision_ledger.jsonlまたはphi_os/human_gate.pyのAPPROVED状態と突合）を設計に含める必要がある。 |
| 3 | `app.py:/decision/approve` `/decision/reject` | **並立状態機械型** | Prevention Queue専用の独自承認機構であり、phi_os/human_gate.pyともDecision Ledgerとも接続していない。承認記録は`append_event()`（what_type: DECISION_APPROVED）のみで、`decision_ledger.jsonl`への記録を経由しない。TODO_361（Decision Ledger記録義務）の対象範囲外として運用されている可能性があり、Gate三値化の対象にPrevention Queueを含めるかどうかは別途整理が必要。 |
| 4 | `_auto_approve_prevention()`（app.py 2023-2049行） | **自己承認型**（TASK-1権限比較表でも既出、TODO_428パック2の対象） | NORMAL/CAUTION severityを`approved_by="AUTO_GATE"`として無条件自己承認する。HOLD新設の際、「機械的にHOLD解除して良いケース」の線引きをこの既存の自己承認パターンと混同しないよう注意が必要（[[feedback_flag_autonomy_risk_in_governance_design]]の観点）。 |

---

## 4. HOLD状態を新設した場合の既存ALLOW/DENY判定ロジックへの影響箇所

- **GL7 (`structural/execution_governance.py`)**: `ApprovalResult.approved`は現在bool型（True/False二値）。HOLDを追加する場合、`bool`から三値（Enum等）への型変更が必要であり、`pre_execution_check()`の戻り値を参照している唯一の既知呼び出し元は`SealGovernanceGate.execute()`（`if not approval.approved:`という単純なbool判定、79行）。三値化する場合はこの分岐を`ALLOW/DENY/HOLD`の3分岐に書き換える必要がある。
- **SealGovernanceGate (`governance/seal_governance_gate.py`)**: `GateResult.approved`も同様にbool型（43行）。HOLD時の戻り値・`_record_decision_unit()`のdecision欄（現状"approved"/"aborted"の2値、130行）も見直しが必要。
- **`phi_os/human_gate.py`**: 既にPENDING状態を持つため、型変更は不要。**ただし2.4節の通り、GL7/SealGovernanceGateとの接続が現状存在しない。HOLD新設は「GL7にHOLDを追加する」のではなく「GL7のDENY以外の場合にphi_os/human_gate.pyのsubmit()を呼び、PENDING状態を経由させてから実行する」という既存資産の再利用で実現できる可能性が高い（2.4節の設計提案、TASK-7で詳細化）。**
- **`mocka_git_safe_commit.py`**: 現状のexcluded/human_gate_override_event_idの二値的な扱い（除外 or override）にHOLDという中間状態は存在しない。3章#2で述べた検証なきoverride問題と合わせて設計が必要。
- **`interface/gate_policy.py`の`compute_gate_audit()`**: HOLD状態のイベントが`_source`列にどう記録されるか（新しい`_source`値を追加するか、既存の`live`のまま`what_type`で判別するか）によって、Gate Audit集計ロジック（`GATE_SOURCE_VALUES`等）への影響が生じる可能性がある。実装時に確認が必要（本調査では未確定、推測）。

---

## 5. 監査官R01実施条件への対応

### 5.1 条件1: 発生→記録→判断→実行→証跡の連続性確認

現状のAUTO_SEAL_PENDING/AUTO_SEAL_PENDING_DAILY経路（2026-07-08是正後）で連続性を検証した。

```
発生: event_count>=50 または 日次0時条件成立(app.py auto_audit_loop)
  |
記録: get_buffer().push({...AUTO_SEAL_PENDING...})  -> events.db(Gate経由、Local Buffer)
  |
判断: [ここで途切れる] -- 人間が明示的にseal実行を指示する専用API/UIが存在しない。
  |                        きむら博士が別途human_gate_override_event_idを人力で
  |                        特定し、anchor_update.pyまたはmocka_git_safe_commitを
  |                        手動起動する運用に依存している(2.4節表)。
実行: (人間の手動操作、経路は運用依存で制度化されていない)
  |
証跡: mocka_git_safe_commit()のpost_commit_files/post_commit_violationで事後検証(1707fcc38是正済み)
```

**連続性の評価: 「発生→記録」までは制度化されている。「記録→判断→実行」の間は
制度化されておらず、人間の運用手続きに依存している。これはTODO_429
（human_gate_cli.py、制度判断待ちでWAIT）が扱おうとしている領域と重なる。**
「実行→証跡」はTODO_426是正により機械的に保証されている。

### 5.2 条件2: 「正しい変更」≠「正しい制度経路で成立した変更」の観点

TASK-1で確認したb66af6c63/0f7f9b89cは、まさにこの原則の実例である
（内容はDC_20260706_003/004・Event Ledger記録により正当性が確認できたが、
commit成立の経路自体はHuman Gateの明示的紐付けを経ていなかった）。本章2.3節の
`/audit/seal`ギャップは、将来同種の事例を生みうる**現在も開いたままの経路**である
点で、TASK-1の2件（根本原因は是正済み）より優先度が高い可能性がある
（評価はTASK-7またはHuman Gate判断に委ねる）。

### 5.3 条件3: router/save系操作の4点確認

`SealGovernanceGate._record_decision_unit()`は変更前イベント（change_start記録）と
変更後イベント（change_done、Decision Ledger追記）の両方を記録する設計にはなっている
（120-149行）。ただし読み戻し検証（write後にdecision_ledger.jsonlを実際に読んで
反映を確認する処理）はコード上存在しない（`with open(...).write()`のみで、
書込み直後の読み戻しはない）。TODO_361の「実行証跡の定義」原則
（書込みツールの戻り値だけでなく読み戻し確認が必要）が、この経路には
まだ適用されていない可能性がある（推測、実際の運用フローでの読み戻し有無は未確認）。

---

## 6. 推測・未確認の明示

- interface/gate_policy.pyのGATE_SOURCE_VALUESへのHOLD追加要否は未検証（推測に留める）。
- `/decision/approve` `/decision/reject`がDecision Ledgerと接続していない点について、
  意図的な設計（Prevention Queueは軽量案件のみを扱うため）か、単なる未接続かは
  一次データから断定できなかった（推測: TODO_361のスコープ外として意図的に残された
  可能性が高いが、確定情報は見つかっていない）。
- `/audit/seal`のGL7契約違反ギャップ（2.3節）が実際に悪用/誤用された過去事例が
  あるかどうかは、本調査の範囲（TASK-2）では調査していない（TASK-1と同様の
  git log監査が必要であれば別途実施が必要）。

---

## 7. 次工程への申し送り

- 2.3節の`/audit/seal`ギャップは、TASK-1の2件と異なり**現在も開いたままの経路**である。
  修正はTASK-2の範囲外（調査のみ）だが、TASK-7横断マッピングで優先度評価の対象とすること。
- HOLD新設の実装方針としては、GL7に新しい状態を追加するより、
  「GL7のALLOW後にphi_os/human_gate.pyのsubmit()を呼びPENDING経由させる」という
  既存資産の再利用案（4章）を、TASK-7またはPhase 1設計時の選択肢として明記すること。
- `mocka_git_safe_commit.py`の`human_gate_override_event_id`の検証なき信頼（3章#2）は、
  Gate三値化・Execution Manifest（TASK-3のactor_identity_hash等）双方に関わる
  横断的な課題として扱うこと。

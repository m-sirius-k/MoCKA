# AUTO_SEAL Boundary Design v1.0

- Document ID: GOV-DESIGN-ASBD-001
- Status: Proposed (implementation pending human approval)
- Date: 2026-07-13
- Author: Claude-opus-4-8 (くろこ)
- Commissioned / approval owner: きむら博士
- Decision: DC_20260713_003
- Scope: TODO_411 / TODO_412 / TODO_413 (AUTO_SEAL Boundary Audit)
- Classification: Upstream boundary design (design only, no code change)
- Inputs: docs/governance/TODO_411_412_413_AUTO_SEAL_BOUNDARY_AUDIT_v1.0.md (audit / gap finding),
  docs/governance/GL7_STATE_INTEGRITY_NOTE_v1.0.md

本書は「直す」ための実装指示ではない。AUTO_SEALが将来 誰(who)によって、
どのDecision(decision_id)に基づき、どのArtifact(artifact_hash)を固定したかを
証明できる境界を設計として確定するものである。実装は本書承認後の別工程とする。

---

## 1. Current State

### 1.1 Seal生成の実処理 (frozen)

- scripts/ledger/anchor_update.py: git add -A -> staged禁止パターン検査 ->
  mocka_git_safe_commit(commit) -> calc_summary_hash -> anchor_record.json(2箇所)更新 ->
  再commit -> verify_all.py。commit messageのみを引数に取り、seal本体を実行する。
- governance/calc_summary_hash.py / governance/mocka_git_safe_commit.py: seal/hash/commitの実処理。
- runtime/mocka_seal.py: 別系統の hash-chain ledger (runtime/ledger.json)。anchor_recordとは別物。
- 上記は Decision裁定により Core System File として変更禁止(frozen)。

### 1.2 AUTO_SEAL 3経路の現状 (2026-07-13)

| 経路 | 実装箇所 | Trigger側 | 承認の実体 |
|---|---|---|---|
| AUTO_SEAL_50EVT | app.py auto_audit_loop | PENDING記録のみ、自動実行なし(是正済 TODO_370/371) | 人間指示待ち |
| AUTO_SEAL_DAILY | app.py auto_audit_loop + watchdog_mocka.py | PENDING記録のみ、自動実行なし(是正済 TODO_427) | 人間指示待ち |
| MANUAL_SEAL | app.py /audit/seal (POST) -> SealGovernanceGate | GL7評価後、承認時 anchor_update.py 実行(Phase C-2) | system:seal_governance_gate (自動) |

補足: 監査 v1.0(2026-07-08)時点で「未閉鎖」とされた MANUAL_SEAL Gap-1 は、その後
SealGovernanceGate(governance/seal_governance_gate.py)経由へ構造的に接続された。
ただし後述のとおり、この Gate の承認主体は GL7 の自動判定であり、人間ではない。

### 1.3 Human承認情報の現在の保持状況

SealGovernanceGate._record_decision_unit が decision_ledger.jsonl へ以下を追記する:
decision_id(DC_EXEC_...自動採番), execution_id, change_start, change_done,
artifact_hash(commit), seal_hash(summary), approved_by="system:seal_governance_gate",
approved_at, aborts。

- 保持あり: decision_id(自動生成), artifact_hash, seal_hash, execution時刻。
- 保持なし: 人間の requester、人間の approved_by、人間の approval_timestamp、
  seal_request_id、事前承認済み Decision への束縛。
- 直接実行(anchor_update.py CLI)経路では、上記のいずれも記録されない(git commit証跡のみ)。

---

## 2. Risk Boundary

| ID | Risk | 由来 | Operational Impact |
|---|---|---|---|
| RB-1 | Direct Execution Bypass: `python anchor_update.py "msg"` は gate/auth/human/decisionを一切経由せず seal可能 | 是正が caller単位(監査v1.0 Gap-2) | Not observed(証跡なし)。構造的な未閉鎖境界 |
| RB-2 | Auto-approval masquerading as governance: SealGovernanceGate は GL7 dry-run cleanで自動approveし approved_by=system と記録。人間不在の承認が Decision Ledgerに"承認済"として残る | Phase C-2実装 | 制度整合性リスク。自律裁定化 |
| RB-3 | No human identity: requester / 人間approver / seal_request_id が無く、"誰が要求し誰が承認したか"を証明不能 | 監査v1.0 Gap-4 + 設計未確定 | 証明可能性の欠落 |
| RB-4 | Weak Decision binding: Gate は DC_EXEC_... を自己採番するのみで、事前承認された人間Decisionへ束縛しない。Seal と "根拠Decision" が接続されない | 設計未確定 | どのDecisionに基づくSealか不明 |
| RB-5 | PENDING-Completion 非対称: Trigger側はPENDING(require_human_gate=True)化されたが、Completion側(/audit/seal, 直接実行)はPENDINGイベントを参照・検証せずに完了できる | 是正の非対称性 | Human Gateの論理的未閉鎖 |

いずれも「発生中の障害」ではなく「未閉鎖境界(Boundary Risk)」である。

---

## 3. AUTO_SEAL 責務定義 (Phase 2-1)

### 3.1 Seal対象 (What is sealed)

- 対象: あるcommit時点のリポジトリ状態を要約する sealed_summary_hash と、
  それを指す external_ref(commit URL)を anchor_record.json へ固定すること。
- 非対象: runtime/ledger.json(mocka_seal.py の hash-chain)は本設計の対象外(別系統)。

### 3.2 Seal前条件 (Preconditions)

1. staged禁止パターン(secrets/.env/Cache等)を含まない (anchor_update.py 既存検査)。
2. 根拠となる承認(normal: 事前承認Decision / emergency: 人間の緊急承認)が存在する。
3. seal_request_id が採番され、requester が記録されている。

### 3.3 Seal後保証 (Postconditions)

1. anchor_record.json(2箇所)が同一 sealed_summary_hash / external_ref / sealed_at_utc を持つ。
2. seal監査レコードに who / decision_id / artifact_hash / seal_hash / approval_timestamp が揃う。
3. 対応する Audit Event が events.db に残る。
4. verify_all.py が pass する。

---

## 4. Human Gate Model (Phase 2-2)

### 4.1 候補比較

| 案 | 内容 | 長所 | 短所 |
|---|---|---|---|
| A: Seal単位承認 | Seal 1回ごとに人間が明示承認 | 最高保証。全Sealにhuman証跡 | 高摩擦。日次/50EVTで都度承認負荷 |
| B: Decision単位承認 | 人間が Decision(decision_id)を承認し、そのDecisionに束縛されたSealが実行可 | MoCKAのDecision Ledger中心思想に整合。who/decision_id/artifactが揃う | Decisionのscope設計が必要 |
| C: Policy単位承認 | 人間が恒常Policyを承認し、条件合致Sealは自動実行 | 摩擦最小 | 恒常自動承認ループを再導入。Human Gate迂回と同型(RB-2の制度化) |

### 4.2 推奨: B を主経路、A を緊急/Core scope必須、C は不採用

- 主経路 = B(Decision単位承認)。理由: 本タスクの成功基準「誰が/どのDecisionに基づき/
  どのArtifactを固定したか」を、decision_id(どのDecision)+ 人間approved_by(誰)+
  artifact_hash(どのArtifact)で直接満たす。MoCKAの三要素 Record(記録なき作業は存在しない)と
  Decision Ledger記録義務に最も適合する。
- 緊急/Core System File scope = A(Seal単位の明示human承認)必須。事前Decisionが無い状況でも
  人間の承認証跡を必ず残す。
- C(Policy単位)は不採用。恒常的な自動承認は RB-2(自律裁定化)を制度として固定化し、
  MoCKAが明示的に禁じる Human Gate迂回と同型になるため。GL7は「承認者」ではなく
  「事前フィルタ(abort判定)」に留めるべきであり、GL7 pass を人間承認の代替にしない。

### 4.3 GL7 の位置付け(重要)

現行 SealGovernanceGate は GL7 pass を approved と等価に扱い approved_by=system と記録する。
本設計では GL7 を「実行前フィルタ(abortsがあれば止める)」に限定し、approve判定は
人間(B: Decision承認者 / A: Seal承認者)に置く。GL7 pass だけでは seal を承認済にしない。

---

## 5. Auth Model (Phase 2-3)

seal監査レコード(既存 decision_ledger.jsonl の Decision Unit拡張、後方互換の追加フィールド)で
最低限保持する証跡:

| フィールド | 意味 | normal(B) | emergency(A) |
|---|---|---|---|
| seal_request_id | Seal要求の一意ID(execution_idとは別に要求単位を識別) | 必須 | 必須 |
| requester | 要求主体(human識別子 or system:auto_audit_loop) | 必須 | 必須 |
| decision_id | 根拠となる事前承認Decision(人間承認済) | 必須(実Decision) | emergency Decisionを事後採番 |
| approved_by | 人間の承認者(例: きむら博士) | 必須(human) | 必須(human) |
| approval_timestamp | 人間が承認した時刻 | 必須 | 必須 |
| artifact_hash | 固定対象のcommit hash | 必須 | 必須 |
| seal_hash | sealed_summary_hash | seal後必須 | seal後必須 |
| pending_ref | 対応する AUTO_SEAL_PENDING event_id (RB-5 閉鎖) | AUTO由来なら必須 | 任意 |

- approved_by は system 値を許容しない(RB-2是正)。system が要求主体(requester)になることは
  あっても、承認者(approved_by)は常に人間。
- decision_id は Gate自己採番(DC_EXEC_...)ではなく、事前に人間が承認した Decision を指す
  (RB-4是正)。

---

## 6. Direct Execution Boundary / Emergency Procedure (Phase 2-4)

anchor_update.py の削除は禁止(本タスク制約 + TODO_364共有ヘルパー呼出元)。実処理は温存し、
「いつ呼んでよいか」の境界のみを上位で定義する。

### 6.1 Normal path

Decision(人間承認) -> seal_request_id採番 + requester記録 -> (GL7 abortフィルタ) ->
Seal実行(anchor_update.py) -> Auth Model全項目を監査レコードへ記録 -> Audit Event。

### 6.2 Emergency path

Emergency Request -> Reason(必須) -> Human Approval(A: Seal単位) -> Seal実行 ->
Audit Event(緊急seal + reason + approved_by + 事後decision_id)。事前Decisionが無い緊急時でも、
人間承認と理由の証跡を必ず残す。

### 6.3 直接実行(CLI)の扱い

- anchor_update.py の生CLI実行は「emergency path でのみ許容」を運用境界とする。
- 生CLI実行した場合は、直後に Auth Model 準拠の監査レコード + Audit Event を残すことを必須とする
  (external harness の手動CHANGE_DONE補完と同型の運用義務。GOV-PROC-EHCR-001参照)。
- anchor_update.py 自体は無変更のため、この境界は「コードによる強制」ではなく
  「呼び出し層(gate)＋運用規約」で担保する。caller単位の見落とし(RB-1/監査v1.0 Gap-2)を
  将来 構造的に閉じるかは Migration Plan の判断事項とする。

---

## 7. Proposed Architecture (要約)

- 単一の論理境界「Seal Authorization Boundary」を定義する。全Seal(AUTO由来/MANUAL/直接)は
  この境界を通ったことを Auth Model のレコードで証明できること。
- Trigger(PENDING) と Completion(Seal実行) を pending_ref で接続し、RB-5(非対称)を閉じる。
- GL7 = 事前フィルタ、Human = 承認者、Decision Ledger = 承認と証跡の正本、
  anchor_update.py = 実行器(frozen)。役割を分離する。

（本章は設計方針の宣言であり、どの層に実装するか(gate拡張 / anchor_update.py一元化 /
別ラッパ)は Migration Plan で人間が選択する。）

---

## 8. Migration Plan

各ステップは きむら博士の明示承認を前提とし、本書承認までは着手しない。

1. M0(本書): 境界・Human Gate Model(B)・Auth Model・Emergency Procedure の設計確定。
2. M1: Auth Model フィールド(seal_request_id/requester/人間approved_by/pending_ref)を
   decision_ledger.jsonl の追加フィールドとして定義(後方互換、既存フィールド不変更)。実装は別承認。
3. M2: MANUAL_SEAL(/audit/seal)の approved_by を system から human承認必須へ変更する設計反映。
   GL7 を承認者から事前フィルタへ格下げ。
4. M3: AUTO_SEAL_PENDING と Completion の pending_ref 接続(RB-5閉鎖)。
5. M4(判断保留): 直接実行境界(RB-1)を caller単位のままとするか、呼出元非依存の一元ゲートへ
   構造化するか(監査v1.0 修正候補2)の制度判断。
6. 各Mは Non Goals(第9章)を侵さない範囲でのみ計画する。

実装フェーズへ進む条件(第9章の制約解除条件):
- 本書(GOV-DESIGN-ASBD-001)を きむら博士が承認する。
- Human Gate Model B 採用、GL7の事前フィルタ格下げ、approved_by=human必須を裁定する。
- 変更対象(app.py/anchor_update.py/gate のどこを触るか)ごとに Core System File Human Gate の
  個別承認を得る。

---

## 9. Non Goals

本書および本タスクでは以下を行わない。

- app.py / API / port / events.db仕様 の変更。
- scripts/ledger/anchor_update.py の変更・削除・再実装。
- global filesystem hook の追加。
- 既存 AUTO_SEAL処理(auto_audit_loop / watchdog / SealGovernanceGate)の直接改修。
- 既に是正済みの Trigger側(AUTO_SEAL_50EVT / DAILY の PENDING化)の再変更。
- 本設計に基づく実装そのもの(実装は本書承認後の別工程)。

---

## 10. History

- 2026-07-13: 初版(v1.0)。監査 v1.0(TODO_411_412_413_AUTO_SEAL_BOUNDARY_AUDIT_v1.0.md,
  2026-07-08/10)を Current State入力として、上流の Boundary/Human Gate/Auth/Emergency/Migration
  設計を確定(DC_20260713_003)。監査v1.0 で未閉鎖とされた Gap-1(MANUAL_SEAL)は SealGovernanceGate
  接続で構造対応済だが、承認主体が GL7自動(approved_by=system)である点を RB-2として本書で明示。

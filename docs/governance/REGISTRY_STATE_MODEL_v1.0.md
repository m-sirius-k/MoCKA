# REGISTRY_STATE_MODEL_v1.0

KN-006: Registry State Model(状態遷移)

## 1. Scope

本文書はRegistry Recordのライフサイクル状態のみを定義する。
Human Gateにおける承認プロセスの状態(PENDING、APPROVED等)は
別の状態空間であり、本書では定義・変更しない。

対象:
- Registry Record(KN-004 lifecycle.status)が取り得る状態の意味
- 状態間の許可される遷移方向
- 禁止される遷移
- status_changed_at の更新規則

対象外:
- Human Gate承認プロセスの状態(phi_os/human_gate.pyの管轄)
- 遷移の検証ロジック・整合性チェック(KN-007の範囲)
- 遷移の実行処理・コード実装(KN-007以降の範囲)
- Category/Series間のTopology(Atlas Seriesの範囲)

## 2. State Principles(状態設計原則)

- Registry Record Stateは「資産としての存在状態」を表すものであり、
  「誰かがそれを承認したかどうか」(Human Gate State)とは独立した
  軸である。両者は同時に参照されることはあっても、混同してはならない。
- 状態は単調に進行することを原則とし、逆行(例: Archived→Draft)は
  原則禁止とする。逆行が必要な場合は新規Recordの作成として扱う。
- すべての状態遷移はstatus_changed_atの更新を伴う。

## 3. State Definitions

| Status | 意味 |
|---|---|
| Draft | 作成中。Registry未確定の草稿状態 |
| Review | Registry Recordが正式登録前の審査・確認工程にある状態 |
| Approved | Registryにおいて正式な有効Recordとして登録された状態 |
| Deprecated | 後継Recordの登場等により非推奨化されたが、参照は可能 |
| Archived | 有効な参照対象から除外された最終状態 |

## 4. Transition Rules

```
Draft → Review → Approved → Deprecated → Archived
          ↓
        Draft(差し戻し)
```

許可される遷移:
- Draft → Review
- Review → Approved
- Review → Draft(審査不承認による差し戻し)
- Approved → Deprecated
- Deprecated → Archived

禁止される遷移:
- Approved以降の状態からDraftへの復帰
- Archivedから他状態への遷移(最終状態)
- Draft → Approved の直接遷移(Reviewを経ない承認は認めない)

## 5. Boundary(境界)

### 5.1 Human Gate Boundary

Registry Record StateとHuman Gate State(PENDING/APPROVED/REJECTED/
EXPIRED/CANCELED)は別の状態空間である。RecordのReview工程はHuman
Approval Gateによる審査を含み得るが、審査そのものの状態管理はHuman
Gate側(phi_os/human_gate.py)の責務であり、Recordの状態遷移条件と
Human Gateの状態遷移ルールは独立して管理する。

### 5.2 Validation Boundary

本文書は遷移として許可される値・方向のみを定義する。ある遷移要求が
実際にルールを満たしているかを検証する仕組み(Validator)はKN-007
の範囲であり、本書では扱わない。

### 5.3 Execution Boundary

本文書は遷移の定義(仕様)のみを扱う。遷移を実際に実行する処理・
コードの実装はKN-007以降の実装フェーズの範囲であり、本書では扱わない。

## 6. Extension Policy

- 新規状態の追加は、既存5状態で表現できない資産のライフサイクルが
  実際に発生した場合にのみ検討する(新規状態追加は最後の手段とする、
  CATEGORY_REGISTRY_V1の新Category追加原則を継承)。
- 遷移ルールの変更は本文書の改訂として扱い、KN-004(lifecycle.status
  enum)への影響を都度確認する。
- 本状態モデルはRegistry Recordに限定される。他システム(Human Gate、
  Workflow、Execution Runtime等)は必要に応じて独自のState Modelを
  持つことができるが、本状態モデルを変更しない。

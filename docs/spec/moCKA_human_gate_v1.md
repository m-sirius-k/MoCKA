# MoCKA Human Gate Spec v1

## 1. 位置づけ

Human Gateは、IR/Spec Layer（観測・制約）とExecution Layer（app.py、唯一の実行終端）の間に位置する、唯一の承認経路である。

```
IR Layer
  ↓
Spec Layer
  ↓
[ Human Gate ]  ← 本Spec
  ↓
Execution Layer (app.py)
```

Human Gateを経由しない経路でIR/Spec内容がExecution Layerへ到達することは禁止する。

---

## 2. 承認フロー（最低3段階）

```
1. observation review     — IRの観測内容を人間が確認する
2. risk validation         — 提案（transition）のリスクを人間が評価する
3. execution approval      — 実行可否を人間が明示的に承認する
```

各段階は独立しており、前段階の承認なしに次段階へ進むことはできない。

---

## 3. 自動承認禁止

- いずれの段階も、アルゴリズム・自動処理による承認確定を禁止する。
- 「承認待ち」の状態をデフォルトで「承認済み」とみなす設計は禁止する。
- 承認は real human（博士／くろこ）による明示的な行為（承認操作）を必須とする。

---

## 4. rollback条件

以下のいずれかに該当する場合、承認済みの実行をrollbackする：

- execution approval後、app.py適用前に新たな矛盾するIR観測が発見された場合
- 適用結果が事後検証（post-execution verification）でIR/Specとの不整合を示した場合
- 承認者自身が明示的にrollbackを要求した場合

rollbackは状態を承認前の状態に戻すことを意味し、IRの書き換えやobserver結果の改変を伴わない。

---

## 5. 非対象

- IR/Execution境界の構造自体（[[moCKA_phaseC_execution_boundary_v1]]の対象）
- app.py内部の責務（[[moCKA_app_boundary_v1]]の対象）

---

## 6. 関連文書

- [[moCKA_phaseC_execution_boundary_v1]]
- [[moCKA_app_boundary_v1]]
- v1.0 / v1.0.1 / v1.0.2-rc

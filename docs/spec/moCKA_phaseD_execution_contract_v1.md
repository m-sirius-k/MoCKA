# MoCKA Phase D — Execution Boundary Contract v1

## 1. 目的

本Specは、Execution Layer（app.py）とIR/Spec Layerとの境界契約を定義する設計文書である。
**実装変更は含まない。**

---

## 2. Execution層の境界定義

- Execution Layerはapp.pyのみで構成される（[[moCKA_phaseD_execution_core_v1]]の単一性原則）。
- Execution Layerの入力は、Human Gate承認済みの内容に限定される（[[moCKA_human_gate_v1]]）。
- Execution Layerの出力は結果のみであり、IR/Specへの書き戻しを行わない。

---

## 3. IR/Specとの分離保証

```
[IR Layer]      state / transition / observation
      ↓ (read-only)
[Spec Layer]     constraints / semantics / Phase C・D rules
      ↓ (Human Gate ONLY)
[Execution Layer] app.py (deterministic terminal)
```

- IR LayerからExecution Layerへの直接接続は存在しない。必ずSpec LayerとHuman Gateを経由する。
- Spec LayerはExecutionに対して制約を与えるのみであり、自らは実行しない（v1.0.1の`Spec = 制約であり計算ではない`原則を継承）。

---

## 4. state書き込み禁止の再確認

- Execution Layer（app.py）は、IRが定義するstate（`recurrence.state.csv` / `recurrence.state.db`等、Truth Type Map由来の分類）に対し、Human Gate承認を経た正規の実行操作以外での書込を行わない。
- これは既存実装確認結果（[[moCKA_app_boundary_v1]]）を再確認するものであり、新たな制約を追加するものではない。

---

## 5. observer呼び出しの制限（read-only保証）

- app.py内のobserver呼び出しは、[[moCKA_human_gate_v1]]・[[moCKA_app_boundary_v1]]で確認済みの条件（SELECT/READ/LOCAL_COMPUTE/TRANSFORM_OUTPUTのみ、INSERT/UPDATE/DELETE/WRITE/MUTATE禁止）をPhase Dにおいても維持する。

---

## 6. Execution Layerの性質（確定）

```
Execution Layer properties:
- deterministic（v1.0.2-rcのobserver determinismと整合する実行の決定性）
- terminal（再帰なし、観測・遷移層への戻り経路を持たない）
- side-effect controlled（副作用はHuman Gate承認済みの範囲に限定）
- human-authorized only（Human Gateを経由しない実行は存在しない）
```

---

## 7. 関連文書

- [[moCKA_phaseD_execution_core_v1]]
- [[moCKA_phaseD_execution_flow_v1]]
- [[moCKA_phaseC_execution_boundary_v1]]
- [[moCKA_human_gate_v1]]
- [[moCKA_app_boundary_v1]]

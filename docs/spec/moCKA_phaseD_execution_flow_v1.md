# MoCKA Phase D — Execution Flow Model v1

## 1. 目的

本Specは、app.py内部の処理フローを形式化する設計文書である。
**実装変更は含まない。**

---

## 2. 基本フロー

```
[Input]
  ↓
IR Observation (read-only)
  ↓
Human Gate validation
  ↓
Execution (app.py)
  ↓
Output (result only)
```

- IR Observation: observer関数（[[moCKA_human_gate_v1]]・[[moCKA_app_boundary_v1]]で定義済み）による読取専用の観測。
- Human Gate validation: [[moCKA_human_gate_v1]]の3段階（observation review / risk validation / execution approval）を経由しなければ次段階に進めない。
- Execution: Human Gate承認済みの内容のみをapp.pyが実行する。
- Output: 実行結果のみを返す。結果がIRやstateへ再入力されることはない。

---

## 3. 非同期・ループ禁止の明示

- 上記フローは単方向（unidirectional）であり、Outputから前段階への分岐・再入力経路を持たない。
- 非同期処理を導入する場合も、Human Gate validationをスキップする経路を作ってはならない。
- observer出力を入力として再度同じフローに投入するループ構造は禁止する（v1.0.2-rcの`observer determinism`原則と整合）。

---

## 4. Human Gate通過後のみ実行

- 「Execution」ステップは、Human Gate validationの完了（3段階すべての承認）を前提条件とする。
- 承認が完了していない状態でのExecutionステップへの遷移は、本Specの違反とする。

---

## 5. 関連文書

- [[moCKA_phaseD_execution_core_v1]]
- [[moCKA_phaseD_execution_contract_v1]]
- [[moCKA_human_gate_v1]]

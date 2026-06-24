# MoCKA Phase D — Execution Core Spec v1

## 1. 目的

本Specは、IR/Spec層で確定した制約のもとでapp.pyが「実行終端」としてどのように振る舞うかを定義する設計文書である。
**本Specはapp.pyの実コードへの変更を含まない。**

---

## 2. app.pyの責務（完全定義）

- app.pyはMoCKAにおける唯一のexecution endpointである。
- app.pyはIR/Specを参照できるが、その内容を変更してはならない（非干渉ルール）。
- app.pyの処理は「入力→処理→出力」の固定構造を持ち、それ以外の経路を持たない。

```
[Input] → [処理（Human Gate承認済みのもののみ）] → [Output（結果のみ）]
```

---

## 3. execution endpointとしての単一性

- Execution Layerに該当する処理は、すべてapp.pyを経由する。
- app.py以外の場所（CLIスクリプト・MCPサーバ等）から、Human Gateを経由しない実行経路を新設してはならない。

---

## 4. IR/Specへの非干渉ルール

- app.pyはIRを書き換えない。
- app.pyはSpec（v1.0/v1.0.1/v1.0.2-rc/Phase C文書群）の内容を変更しない。
- app.py内のobserver呼び出し（[[moCKA_app_boundary_v1]]で定義済みのread-only呼び出し）は、本Specにおいても同条件を維持する。

---

## 5. 関連文書

- [[moCKA_phaseD_execution_flow_v1]]
- [[moCKA_phaseD_execution_contract_v1]]
- [[moCKA_phaseC_execution_boundary_v1]]
- [[moCKA_human_gate_v1]]
- [[moCKA_app_boundary_v1]]

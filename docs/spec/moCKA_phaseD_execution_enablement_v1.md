# MoCKA Phase D — Execution Enablement Spec v1（実装準備仕様・設計のみ）

## 0. 位置づけ

本Specは「Execution Design Extension（Execution実装準備仕様）」である。
**新規Pythonファイルの作成、app.pyへの変更は一切含まない。**
Code Binding Phase（実コード生成・app.py変更）へ進むには、博士による明示的なHuman Gate承認を別途必要とする（[[moCKA_human_gate_v1]]）。

---

## 1. 前提（変更不可前提）

- IR = read-only observation layer
- Spec = constraint / semantics layer
- Execution = app.py単一点（唯一の実行終端）
- Human Gate = 唯一の実行許可点
- 自動実行禁止（default constraint）

---

## 2. Execution Entry Contract（app.py契約・設計）

### 2.1 単一入口関数（設計）

```
main(input)
```

- 唯一の外部入口として設計される（未実装）。
- 内部処理順序（設計）: IR Observation → Spec Validation → Human Gate Check → Execution → Output Finalization

### 2.2 禁止事項

- IRへの書き込み禁止
- Spec変更禁止
- Human Gateを通らない実行禁止
- 複数入口禁止
- 並列Execution禁止

---

## 3. IR Observation Contract（設計）

### 3.1 入力の扱い

- immutable snapshot
- read-only projection
- state / transition / observation のみ生成可能

### 3.2 IR出力形式（必須構造・設計）

- state
- transition
- observation
- timestamp
- source_id

### 3.3 禁止

- state mutation
- history overwrite
- speculative generation

---

## 4. Spec Validation Layer（設計）

### 4.1 機能（Execution前の静的検証）

- 制約違反チェック
- 入力整合性チェック
- IR構造整合チェック

### 4.2 出力

- valid / invalid
- reason code
- severity level

---

## 5. Human Gate Spec（最重要・[[moCKA_human_gate_v1]]の拡張設計）

### 5.1 定義

Human Gateは「唯一の実行許可点」。

### 5.2 入力

- IR snapshot
- Spec validation result
- Execution request metadata

### 5.3 判断出力（必須3択）

- APPROVE
- REJECT
- MODIFY_REQUEST

### 5.4 APPROVE条件（最小要件）

- IRがvalid state
- Spec違反なし
- Execution scope明示
- risk_level定義済み

### 5.5 禁止

- 自動承認
- 確率的承認
- 暗黙承認

---

## 6. Execution Layer Spec（設計）

### 6.1 実行定義（許可される範囲）

- deterministic function execution
- IR参照のみ
- Spec参照のみ

### 6.2 禁止

- 外部状態変更（IR除く）
- 非決定ロジック依存
- Human Gateスキップ

### 6.3 実行単位（設計上の要件）

Execution Unitは必ず：
- input-bound
- stateless
- reproducible

---

## 7. Output Layer Spec（設計）

### 7.1 出力構造

- execution_result
- IR snapshot reference
- Human Gate decision log
- execution trace

### 7.2 禁止

- hidden state output
- speculative results
- partial execution leakage

---

## 8. Failure Handling Spec（設計）

失敗時フロー（設計）:
- stop execution
- return IR snapshot
- log failure reason
- route to Human Gate again

---

## 9. Security Boundary Model（設計）

三層防御:
- IR = read-only firewall
- Spec = semantic firewall
- Human Gate = execution firewall

---

## 10. Minimal Implementation Order（参考・未着手）

以下は実装順序の**設計上の参考案**であり、いずれも現時点では着手していない。
着手にはHuman Gate承認が必要（Code Binding Phase）。

1. Human Gate module
2. IR Observation function
3. Spec Validation function
4. Execution engine
5. app.py orchestration (main)
6. Output formatter

---

## 11. 最終状態定義（目標、未達成）

本仕様がすべて実装された場合、MoCKAは
「deterministic, gated, non-autonomous execution system」
になる。**この状態は現時点では未達成であり、本Specは目標の記述に留まる。**

---

## 12. 関連文書

- [[moCKA_phaseC_execution_boundary_v1]]
- [[moCKA_human_gate_v1]]
- [[moCKA_app_boundary_v1]]
- [[moCKA_phaseD_execution_core_v1]]
- [[moCKA_phaseD_execution_flow_v1]]
- [[moCKA_phaseD_execution_contract_v1]]

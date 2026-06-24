# MoCKA Phase C — Execution Boundary Spec v1

## 1. 目的

本Specは、IR（観測結果）をHuman Gateを経由してExecutionへ安全に接続するための境界を定義する。
本Specは設計文書であり、実装（app.py）への変更を含まない。

---

## 2. 構造図（最終形）

```
IR Layer
  ↓ (read-only projection)
Spec Layer
  ↓ (Human Gate only)
Execution Layer (app.py)
```

---

## 3. 変換禁止ルール

- IR → Execution の自動変換は禁止する。
- observerの出力（output）は、いかなる経路でもIRやstateへの再入力に使用してはならない。
- transitionは「提案（proposal）」であり、「実行命令（execution command）」ではない。`prevention_queue.json`への書込はtransitionの記録であって、実行のトリガーではない。
- app.pyは唯一の実行終端（single execution terminus）である。Execution Layerの外側に実行経路を作らない。

---

## 4. 非対象（本Specが定義しないもの）

- app.py内の具体的な実装変更（[[moCKA_app_boundary_v1]]の対象）
- Human Gateの承認フロー詳細（[[moCKA_human_gate_v1]]の対象）

---

## 5. 適合条件

以下を満たさない変更案は、本Specに違反する：

1. IRが書き換えられる経路を持つ
2. observer結果がstateに反映される経路を持つ
3. transitionが人間の承認なしに実行される経路を持つ
4. observer出力を再入力するループ構造を持つ
5. app.py以外の場所からIRが直接更新される経路を持つ

---

## 6. 関連文書

- v1.0 / v1.0.1 / v1.0.2-rc（IR/Spec本体、不変）
- [[moCKA_human_gate_v1]]
- [[moCKA_app_boundary_v1]]

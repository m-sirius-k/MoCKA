# MoCKA app.py Boundary Spec v1（設計のみ）

## 1. 位置づけ

本Specはapp.pyの責務を「実行終端（execution terminus）」に限定する設計文書である。
**本Specはapp.py自体への実装変更を含まない。** 実装変更はHuman Gate承認後、別途実施される。

---

## 2. app.pyの責務定義

- app.pyはExecution Layerの唯一の終端である。
- app.pyはIR/Specにアクセスして参照することはできるが、IR/Specの内容を変更してはならない。
- app.pyによる実行は、Human Gateの承認（[[moCKA_human_gate_v1]]の3段階）を経た後にのみ行われる。

---

## 3. state書き込みに関する制約

- IR非破壊性（IR層が観測によって変更されないこと）を維持するため、observerの呼び出し経路においてstate書き込みを禁止する。
- 既存実装で確認済みの`decision_log_detail()`・`_calc_todo_risk_score()`はobserverとして該当し、現状すでにread-onlyである（SELECT文のみ、INSERT/UPDATE/DELETE/ファイル書込なし、確認済み）。
- 既存実装で確認済みの`prevention_generate()`（recurrence_registry.csv読取→prevention_queue.json書込）は、transitionの記録であり、これは「提案の記録」であって「実行」ではない（[[moCKA_phaseC_execution_boundary_v1]]の定義に従う）。

---

## 4. observer呼び出しの制約

- app.py内からobserver関数を呼び出す場合、その呼び出しはread-onlyでなければならない。
- observerの出力を、app.py内のいかなる書込処理（state更新・queue更新・ファイル書込）の入力として直接使用してはならない。

---

## 5. 絶対禁止事項（再掲）

- IRの書き換え
- observer結果のstate反映
- transitionの自動実行
- ループ構造の導入（observer出力の再入力）
- app.pyからのIR直接更新

---

## 6. 成功条件

- app.pyの役割が「実行終端」のみに限定されている
- IRが完全read-only状態を維持している
- Executionの経路がapp.py一つに限定されている
- 自動実行経路（Human Gateを経由しない実行経路）が存在しない

---

## 7. 関連文書

- [[moCKA_phaseC_execution_boundary_v1]]
- [[moCKA_human_gate_v1]]
- v1.0 / v1.0.1 / v1.0.2-rc

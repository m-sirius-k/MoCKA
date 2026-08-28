# RCP-01 Gap Boundary Relationship Consistency Check

検査日時: 2026-08-28
目的: 4つのGapが既存10 Boundaryのどこに関連するか明確化
制約: 新規概念導入なし、実装提案なし、採用判定なし

---

## Gap - Boundary 関連性マッピング

### Gap A: Human Gate Runtime Implementation

**定義**: ドキュメント上は「コアシステムファイルへの書き込みは人間ゲート承認必須」だが、実行直前に人間が STOP/拒否できるRuntime停止点が見つからない。

#### 関連する既存 Boundary

| Boundary | 関係性 | Evidence | 理由 |
|----------|------|---------|------|
| **Approval → Execution** | DIRECTLY_RELATED | mocka_mcp_server.py:480-510 では before_tool() が GL7 dry_run のみを実行し、human approval gate がない | Approval から Execution までの間に、人間が STOP する仕組みがない |
| **Policy → Execution** | PARTIALLY_RELATED | governance_pipeline.py:106-128 で policy は機械的に検査されるが、人間による policy override がない | policy に従って execution decide が変わるが、人間がそれを override できない |
| **Knowledge → Action** | INDIRECTLY_RELATED | Human Gate は knowledge を持つことと action 実行の間に人間を挿入する仕組み | read-write 分離に加えて人間による最終判定を要求 |
| **Execution → Evidence** | PARTIALLY_RELATED | Decision Ledger に approval が記録されるが、execution block point ではない（記録のみ） | accountability の記録はあるが、approval enforcement がない |

#### 関連性分析

**直接関連**: Approval → Execution
- 現状: GL7 dry_run + GL6 checklist が OK なら execution
- 要求: human が最終判定して OK/DENY を decide
- Gap: human の判定ポイントがない

**間接関連**: Policy → Execution
- 現状: policy に基づいて machine が decision
- 要求: human が policy に基づいた decision を override 可能
- Gap: human override ポイントがない

#### UNKNOWN

1. Human Gate の実装位置（どの Boundary に挿入されるべきか）
   - Approval → Execution の直後か
   - Policy → Execution の決定後か
   - 実行前全体のレビューか

2. Human Gate の決定権限の scope
   - 全ての write tool か
   - core files のみか
   - 判定条件は何か

3. Human Gate の実装スケジュール
   - Phase 18 以降の要求か
   - 実装準備中か
   - 廃止予定か

---

### Gap B: Context Re-grounding

**定義**: GL7 dry_run で承認した時点の repository state と、実際に execution する時点の state に時間差があり、別プロセスが状態を変更した場合、再検証されない。

#### 関連する既存 Boundary

| Boundary | 関係性 | Evidence | 理由 |
|----------|------|---------|------|
| **Context → Execution** | DIRECTLY_RELATED | mocka_mcp_server.py:480-510 では before_tool() は一度だけ GL7 dry_run を実行し、execution 時に再度実行されない | Boundary 自体が「time gap vulnerability」として documented |
| **Policy → Execution** | PARTIALLY_RELATED | policy はグラウンディングに基づくが、execution 時の grounding state が異なる可能性がある | grounding の freshness が execution decision に影響 |
| **Scope → Action** | PARTIALLY_RELATED | scope は dry_run 時点での project_structure に基づくが、execution 時に scope が無効になっている可能性がある | scope の有効性が time-dependent |
| **Governance → Side Effect** | INDIRECTLY_RELATED | single entry point は HTTP/fallback pathway を提供するが、approval から execution までの時間差は考慮されていない | governance pipeline 全体が point-in-time approval に基づく |

#### 関連性分析

**直接関連**: Context → Execution
- Gap そのもの: 時間差が存在する
- Evidence: mocka_mcp_server.py での implementation flow に再検証がない
- Timeline:
  ```
  T0: GL7 dry_run ✓ (git status OK)
  T0+n: (別プロセスが git commit)
  T0+2n: mocka_write_event 実行 ← repository state は異なる
  ```

**間接関連**: Policy → Execution
- grounding が policy の基礎だが、grounding 再チェックがない

#### UNKNOWN

1. Context change の実装検出可能性
   - git hash を保存して comparison するか
   - repository integrity を execution 時に再確認するか
   - 許容される state change の範囲は何か

2. Context re-grounding の cost
   - execution 直前に grounding を再実行する overhead
   - network latency 増加

3. Tolerance level
   - どの level の context change が問題か
   - metadata change（branch info）vs file change
   - その他の process による change を許容するか

---

### Gap C: Authority Scope

**定義**: who_actor は validation で身元確認されるが、その者が何を実行できるか（capability/permission matrix）が implicit に定義されており、全ての write tool に対して同じ who_actor が使用可能。

#### 関連する既存 Boundary

| Boundary | 関係性 | Evidence | 理由 |
|----------|------|---------|------|
| **Authority → Action** | DIRECTLY_RELATED | gate_validator.py:8-47 で who_actor は checked されるが、what_action との binding がない | 「誰が何を実行できるか」が定義されていない |
| **Scope → Action** | PARTIALLY_RELATED | scope は resource-level で制御されるが、actor-level での capability がない | resource boundary と actor capability が独立している |
| **Policy → Execution** | PARTIALLY_RELATED | policy は tool-level で適用されるが、actor ごとの policy override がない | policy は uniform であり、actor-dependent variation がない |
| **Knowledge → Action** | INDIRECTLY_RELATED | read-write separation は全 actor に共通だが、actor ごとの write permission がない | knowledge access と action permission が decoupled |

#### 関連性分析

**直接関連**: Authority → Action
- 現状: who_actor の身元確認のみ
- 要求: who_actor ごとに実行可能な action を定義
- Gap: capability matrix が実装されていない

**間接関連**: Scope → Action
- scope は「どこ」を制御（resource）
- authority scope は「誰が何」を制御（actor-action）
- 両者は orthogonal

#### UNKNOWN

1. Authority scope の定義方法
   - Role-Based Access Control (RBAC) か
   - Capability-Based Security か
   - その他の model か

2. Who_actor の granularity
   - AI model version ごとか（Claude-sonnet-4-6）
   - AI type ごとか（Claude vs GPT）
   - Instance ごとか（session-based）

3. Action classification
   - tool name ごと（mocka_write_event, mocka_add_todo等）か
   - resource type ごと（events table, decision ledger）か
   - operation ごと（read, write, delete）か

4. Cross-cutting concerns
   - time-based policy（business hours のみとか）
   - rate limiting
   - audit requirements by action type

---

### Gap D: Direct Write Physical Prevention

**定義**:現在、direct write は技術的に可能（SQL access があれば）であり、unsigned_event violation として事後に検知される。物理的防止ではなく detection-based。

#### 関連する既存 Boundary

| Boundary | 関係性 | Evidence | 理由 |
|----------|------|---------|------|
| **Governance → Side Effect** | DIRECTLY_RELATED | phi_os/event_gate.py:46-100 では process_event() が唯一の entry point だが、direct SQL write は prevent されていない。bypass は検知される（phi_os/integrity.py:244-270） | single entry point は policy-based（人間が守る）であり、physical prevention ではない |
| **Execution → Evidence** | PARTIALLY_RELATED | signature chain で bypass を検知するが、prevention ではない | accountability の記録は完全だが、bypass block は実装されていない |
| **Knowledge → Action** | INDIRECTLY_RELATED | read-write separation は物理的に enforcement されるが、write path そのものの protection は policy-based | write の制御は governance に依存 |

#### 関連性分析

**直接関連**: Governance → Side Effect
- 現状: single entry point (detection-based)
  ```
  process_event() → validate() → _write() → integrity.sign_event()
  ↓
  unsigned_event として事後に detect
  ```
- 要求: SQL access を physically prevent
  ```
  direct INSERT to events は OS-level で禁止
  database ACL で権限を制限
  ```
- Gap: bypass を prevent する layer がない

**間接関連**: Execution → Evidence
- bypass も signed として記録されるが、prevention ではない

#### UNKNOWN

1. Physical prevention の実装方法
   - SQLite database file permissions
   - SQL-level ACL (if supported)
   - container/process isolation
   - 他の方法

2. Prevention 的効果測定
   - どの level の attacker を prevent するのか
   - insider threat に対するのか
   - external attack に対するのか

3. Cost-benefit analysis
   - prevention の overhead
   - logging/monitoring の overhead
   - operation complexity の増加

4. Threat model の定義
   - process-level isolation で十分か
   - privilege escalation を assume するか
   - data center access を assume するか

---

## Gap - Boundary 関連性マトリックス

| Gap | 直接関連 | 間接関連 | 未関連 | UNKNOWN の主要項目 |
|-----|---------|--------|--------|-----------------|
| A. Human Gate | Approval → Execution | Policy → Execution, Knowledge → Action, Execution → Evidence | Authority → Action, Scope → Action, Context → Execution, Governance → Side Effect | Human Gate の位置、決定権限の scope、実装schedule |
| B. Context Re-grounding | Context → Execution | Policy → Execution, Scope → Action | Authority → Action, Execution → Evidence | detection 可能性、re-grounding cost、tolerance level |
| C. Authority Scope | Authority → Action | Scope → Action, Policy → Execution, Knowledge → Action | Approval → Execution, Human Gate → Execution | scope 定義方法、actor granularity、action classification |
| D. Direct Write Prevention | Governance → Side Effect | Execution → Evidence | Knowledge → Action, Reasoning → Execution, Approval → Execution, Context → Execution | prevention 実装方法、threat model、cost-benefit |

---

## 外部議論との関係確認

### A. Human Gate と外部 「approval fatigue」「actionのirreversibility」

関連性: **DIRECTLY_RELATED**

- 外部: approval fatigue を低減するため、critical action のみを human gate にかける
- MoCKA: ドキュメント上は人間ゲート承認必須だが、実装がない
- 共通点: human による最終判定の必要性

相違点:
- 外部: reversibility を前提に approval 後の override を想定
- MoCKA: governance で approval の段階を明確にしている

### B. Context Re-grounding と外部 「execution直前のauthority確認」

関連性: **PARTIALLY_RELATED**

- 外部: execution 直前に authority/context を re-confirm
- MoCKA: policy は execution 決定前に決まり、execution 時の context change は未検証
- 共通点: execution 直前の再検証の必要性

相違点:
- 外部: reversibility と correction を想定
- MoCKA: prevention に重点

### C. Authority Scope と外部 「Standing」「誰が決定するのか」

関連性: **INDIRECTLY_RELATED**

- 外部: who has standing to make this decision
- MoCKA: who_actor は recorded だが、who has permission to do action は implicit
- 共通点: decision maker の明確化の必要性

相違点:
- 外部: multi-stakeholder context での standing
- MoCKA: single AI system context での permission

### D. Direct Write Prevention と外部議論

関連性: **NOT_RELATED**

- 外部コメント: direct write prevention の要求なし
- MoCKA: detection-based design が existing decision
- この gap は「外部から要求されたのではなく」、「RCP-01 監査で発見された実装特性」

---

## 確認結果

### 確認できた関連性

1. **Human Gate implementation** → Approval → Execution Boundary に直結
   - 実装が必要なら Approval → Execution 間に human decision point が必要

2. **Context re-grounding** → Context → Execution Boundary が directly addresses
   - 実装が必要なら execution 直前の re-grounding が必要

3. **Authority scope** → Authority → Action Boundary が insufficient
   - 実装が必要なら actor-action matrix が必要

4. **Direct write prevention** → Governance → Side Effect の detection-based design limitation
   - 実装が必要なら database-level protection が必要

### 未確認な関連性

1. A, B, C, D が相互に how they interact するか
   - 例: Authority scope がなければ human gate の判定基準が定義できない可能性
   - 例: Context re-grounding がなければ authority check のための context が stale である可能性

2. 外部議論での「逆方向」の影響
   - reversibility や compensability が MoCKA architecture に require される変更があるか
   - この検査では確認していない

---

## Human Gate へ返却される判断事項

以下は監査官は判定しない。Human Gate で決定すべき。

1. **Human Gate runtime implementation の必要性**
   - ドキュメント上の要求との一致性
   - 実装が本当に必要か、または廃止すべきか
   - 関連する Boundary: Approval → Execution

2. **Context re-grounding の feasibility**
   - cost/benefit analysis
   - tolerance level の定義
   - 関連する Boundary: Context → Execution

3. **Authority scope の定義**
   - RBAC vs Capability vs other model
   - actor/action の granularity
   - 関連する Boundary: Authority → Action

4. **Direct write physical prevention の必要性**
   - threat model の確認
   - prevention vs detection のトレードオフ
   - 関連する Boundary: Governance → Side Effect

---

## 制約事項の再確認

✓ 新規 Boundary の創出: なし
✓ Boundary の統合: なし
✓ Reversibility/Compensability の採用判定: なし
✓ 実装提案: なし
✓ 設計変更: なし
✓ Human Gate の採用判定: なし
✓ Baseline: 凍結のまま

---

## 結論

4つの Gap は既存 10 Boundary の不完全性または非実装として特定された。

- **A. Human Gate**: Approval → Execution Boundary の実装ギャップ
- **B. Context Re-grounding**: Context → Execution Boundary の実装ギャップ
- **C. Authority Scope**: Authority → Action Boundary の不完全性
- **D. Direct Write Prevention**: Governance → Side Effect の detection-based design limitation

各 Gap について判定が必要な場合、Human Gate で以下を確認すること:

1. Gap が本当に「埋める必要のある Gap」か
2. Gap を埋める cost/benefit
3. Gap を埋めた場合の architecture への影響
4. 外部議論との関連性と MoCKA の philosophy の整合性

No Evidence, No Pass.
Unknown must be preserved.
Baseline remains frozen.
No adoption by implication.

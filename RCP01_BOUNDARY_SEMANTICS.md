# RCP-01 Boundary Semantics Analysis
# 各 Boundary の分離目的・条件・実装経路の明確化

文書作成日: 2026-08-28
分析対象: RCP-01 で確認された 10 個の Boundary
目的: 各 Boundary が「何と何を分離するのか」を明らかにする
方針: 新規概念導入なし。MoCKA の既存実装から出発。

---

## 1. Knowledge → Action 境界

### 左側（越える前）
- AI エージェント が実行可能な情報（overview, todo, essence等）を 取得
- 過去の判断・承認の history を読み取り可能
- Repository state, governance policy を 知識として所持

### 右側（越えた後）
- 実際の side effect 実行
- DB への永続化
- Repository への commit
- System state の変更

### 分離の目的
**知識と実行を物理的に分離する**
- 情報を持つこと ≠ 実行できること
- read と write の根本的分離

### 越える条件
1. AI が tool を呼び出す（例: mocka_write_event）
2. tool call が execute_tool() に到達
3. GL7 dry_run check が PASS
4. Governance Pipeline が allowed=True を返す

### 条件を判定するのは
**Governance Pipeline (execute_tool() 内の before_tool())**

### Runtime での強制
**YES - PASS**

実装経路:
```
1. mocka_mcp_server.py:1457 @app.route("/agent/<tool_name>")
2. mocka_mcp_server.py:1467 execute_tool(tool_name, args) 呼び出し
3. mocka_mcp_server.py:480-507 execute_tool()
   - _governance が None なら Fail Closed
   - _governance.before_tool() で GL7 dry_run
   - dry_run でabort があれば GL7_EXECUTION_BLOCKED を返す
4. これを通さずに tool body は実行されない
```

### 外部議論との関連性
**INDIRECTLY_RELATED**

外部での「irreversibility」「consequence」との関連:
- Knowledge を持つだけで実行できない → consequence の物理防止に寄与
- しかし、逆転不可能性そのものではない（read-write separation であり reversibility determination ではない）

### 相違点
- MoCKA: read と write の完全分離
- 外部議論: 実行結果の reversibility（実行後の問題）

---

## 2. Reasoning → Execution 境界

### 左側（越える前）
- AI の推論結果（何をすべきか判断した state）
- Pre-answer checklist の生成
- 思考プロセスの完了

### 右側（越えた後）
- 実際の system call
- side effect の発動
- execution の開始

### 分離の目的
**推論完了 ≠ 実行許可**
- 正しく考えたこと が実行可能を意味しない
- 追加の実行前 gate を設置

### 越える条件
1. GL6 Pre-Answer Checklist を enforce_pre_answer_checklist() で取得
2. checklist.ok が True
3. checklist に missing がない

### 条件を判定するのは
**ReasoningGovernanceEngine (GL6)**

### Runtime での強制
**YES - PASS**

実装経路:
```
1. structural/governance_pipeline.py:106
   checklist = self.reasoning.enforce_pre_answer_checklist()
2. structural/governance_pipeline.py:122
   allowed = (not aborts) and checklist.ok
3. checklist.ok が False なら
   reason = f"GL6 pre-answer checklist failed: missing={checklist.missing}"
4. allowed=False で GL7_EXECUTION_BLOCKED を返す
```

### 外部議論との関連性
**PARTIALLY_RELATED**

外部での「authority confirmation」との関連:
- MoCKA の GL6: thinking mode の確認（reasoning process の completeness）
- 外部の authority: 実行権限者の確認（who has permission to do this）

重なっていない部分: GL6 は「who has the authority」を検査していない

### 相違点
- MoCKA: 推論プロセスの妥当性
- 外部議論: 実行権限者の authorization

---

## 3. Authority → Action 境界

### 左側（越える前）
- who_actor（実行者の身元）
- who_role（実行者の役割）
- who_session（実行セッション）

### 右側（越えた後）
- 具体的な action の実行
- resource へのアクセス
- state の変更

### 分離の目的
**身元確認と権限バインディング**
- 誰が実行するのか を記録
- その者が何を実行できるか を制御

### 越える条件
1. who_actor が validation で必須（空でない）
2. who_actor が legacy values（"Claude"等）でない
3. who_session が SESSION_YYYYMMDD_HHMMSS 形式

### 条件を判定するのは
**PHI-OS Gate Validator (gate_validator.py:REJECT-01, REJECT-02)**

### Runtime での強制
**PARTIAL - 身元確認のみ**

実装経路:
```
1. phi_os/event_gate.py:115-135 process_event()
2. phi_os/gate_validator.py:8-47 validate()
3. REJECT-01: who_actor が legacy value でないか確認
4. REJECT-02: who_session が形式を満たすか確認
5. これらが満たされないと status='rejected' で return
```

**不足している部分: Scope of authority**
- 誰が何を実行できるか（capability/permission matrix）が実装されていない
- who_actor ごとの action permission がない
- 全ての write tools に同じ who_actor が使用可能

### 外部議論との関連性
**DIRECTLY_RELATED**

外部での「authority」との定義:
- MoCKA: who_actor の身元確認
- 外部: who_actor の権限 scope（capability/permission）

### 相違点
- MoCKA: 「誰であるか」を確認（authentication level）
- 外部: 「誰が何を実行できるか」を定義（authorization level）

---

## 4. Scope → Action 境界

### 左側（越える前）
- 変更予定のファイル・ディレクトリのリスト
- expected_new_dirs（許可される新規ディレクトリ）
- expected_max_changes（許可される変更数上限）

### 右側（越えた後）
- 実際の git 操作
- repository への commit
- 許可外のディレクトリへのアクセス

### 分離の目的
**変更範囲の制限**
- 全 repository への write を許可しない
- 特定のディレクトリのみに限定

### 越える条件
1. GL7 dry_run で変更ファイルを抽出
2. 変更ファイルが scope に属しているか確認
3. scope に属さないファイルがあれば deletion_outside_scope abort

### 条件を判定するのは
**ExecutionGovernanceEngine (execution_governance.py:145-179)**

### Runtime での強制
**YES - PASS**

実装経路:
```
1. structural/execution_governance.py:154-159
   scope = action.get("scope", [])
   for path in dry_run.changed_files:
       if not any(path.startswith(s) for s in scope):
           aborts.append("deletion_outside_scope")
2. structural/governance_pipeline.py:114-119
   scope = grounding.project_structure
   approval = self.execution.pre_execution_check({
       "scope": scope,
       ...
   })
3. aborts があれば execution は BLOCKED
```

### 外部議論との関連性
**DIRECTLY_RELATED**

外部での「consequence admissibility」との関連:
- 変更範囲を制限する → consequence を bounded area に限定
- scope を超えた action は禁止 → unintended consequence を prevent

### 相違点
- 共通: resource の変更範囲を制限する
- MoCKA はさらに「repository structure grounding」を行う（git state を見る）

---

## 5. Approval → Execution 境界

### 左側（越える前）
- 実行前の approval status
- dry_run check の result
- decision ledger への記録

### 右側（越えた後）
- 実際の execution
- side effect の発生
- state change の確定

### 分離の目的
**approval された action のみ実行許可**
- 承認されていない action は実行しない
- 承認と実行の 2 段階分離

### 越える条件
1. GL7 dry_run が OK（no aborts）
2. GL6 checklist が OK
3. PHI-OS Gate validation が OK（who_actor, what_type, why_purpose等）

### 条件を判定するのは
**複数層:**
- GL7: ExecutionGovernanceEngine
- GL6: ReasoningGovernanceEngine
- PHI-OS: gate_validator.py

### Runtime での強制
**PARTIAL - 機械的検査のみ**

実装経路:
```
1. structural/governance_pipeline.py:91-136 before_tool()
   - GL7 dry_run check
   - GL6 checklist check
   - 両方 OK なら allowed=True
2. mocka_mcp_server.py:492-498
   - before_tool() の decision.allowed を確認
   - allowed=False なら GL7_EXECUTION_BLOCKED を返す
3. phi_os/event_gate.py:115-135 process_event()
   - validate() で who_actor, what_type等を再度検査
   - validation fail なら status='rejected'
```

**機械的検査のため、以下が不足:**
- 人間による approval UI がない
- execution 直前に人間が STOP できない
- decision が記録されるが、execution block point ではない

### 外部議論との関連性
**PARTIALLY_RELATED**

外部での「approval」との定義:
- MoCKA: 機械的な dry_run/validation
- 外部: Human-in-the-loop approval（人間が判断する）

### 相違点
- MoCKA: policy based automatic approval（policy が OK なら実行可）
- 外部: human-based discretionary approval（人間が each case で判定）

---

## 6. Context → Execution 境界

### 左側（越える前）
- GL7 dry_run を実行した時点での repository state
- その時点での context（branch, files, permissions）

### 右側（越えた後）
- 実際の execution が開始された時点
- その時点での repository state（異なる可能性がある）

### 分離の目的
**approval context と execution context の一致確保**
- approval した時の状態 = execution する時の状態
- context change を検知・防止

### 越える条件
1. GL7 dry_run でその時点の git status を確認
2. ✗ GL7 と execution の間に context 再検証がない
3. ✗ 別プロセスが git commit した場合、検知されない

### 条件を判定するのは
**（現在のところ実装されていない）**

### Runtime での強制
**NO - 不実装**

証拠:
```
時刻 T0: GL7 dry_run チェック
   git status --porcelain で state 確認 ← OK
時刻 T1: (別プロセスが git commit)
時刻 T2: mocka_write_event 実行
   repository state は T0 から変わっているが再検証されない
```

mocka_mcp_server.py:480-510 では:
- before_tool() は実行前に dry_run をする
- 実行中に context が変わる可能性は処理されない
- after_tool() も context 再検証を行わない

### 外部議論との関連性
**DIRECTLY_RELATED**

外部での「execution context」との関連:
- 外部: approval から execution までの time gap での context change
- MoCKA: これを検知する仕組みがない

### 相違点
- 共通: context change に気づくこと
- MoCKA はさらに「before_tool の一度きりのチェック」に依存
- 外部は「approval と execution の context snapshot 比較」を想定

---

## 7. Policy → Execution 境界

### 左側（越える前）
- governance policy の version
- policy が何を許可・禁止するか

### 右側（越えた後）
- policy に従った execution
- policy に違反した execution（ブロック）

### 分離の目的
**policy に基づいた execution の制御**
- policy が変われば execution decision も変わる
- policy ない状態では execution しない

### 越える条件
1. GL1 Grounding で current policy を取得
2. policy が load できない場合は execution 不可
3. policy に基づいて decision を判定

### 条件を判定するのは
**RepositoryGroundingEngine (GL1)**

### Runtime での強制
**YES - PASS**

実装経路:
```
1. structural/governance_pipeline.py:96
   grounding = self._refresh_grounding()
2. structural/grounding_engine.py
   - current policy version を確認
   - repository から governance policy を読む
3. execution_governance.py
   - policy に基づいて abort conditions を判定
4. policy が change なら re-evaluate
```

### 外部議論との関連性
**INDIRECTLY_RELATED**

外部での「policy」との概念:
- MoCKA: runtime policy（git state に基づく policy）
- 外部: static policy（organization level の定められた rule）

### 相違点
- MoCKA: policy は code repo に versioned
- 外部: policy は centralized governance system で管理

---

## 8. Human Gate → Execution 境界

### 左側（越える前）
- AI が実行判断を完了
- decision が記録された
- 人間への通知

### 右側（越えた後）
- 人間の approval を待たずに実行
- または人間が拒否を強制できない

### 分離の目的
**人間による最終確認と拒否権**
- 機械的チェックが OK でも、人間が STOP できる
- execution の最後の防衛線

### 越える条件
**（ドキュメント上では要求されているが実装されていない）**

CLAUDE.md: "Phase18以降: コアシステムファイルへの書き込みは人間ゲート承認必須"

### 条件を判定するのは
**存在しない（見つからない）**

### Runtime での強制
**NO - NOT IMPLEMENTED**

証拠:
```
1. CLAUDE.md では要求
2. human_gate.py は複数箇所に存在（phi_os/, runtime/jarvis/等）
3. しかし、mocka_mcp_server.py の execute_tool() workflow に統合されていない
4. COMMAND CENTER に Human Gate approval UI がない
5. Decision Ledger は「決定を記録」するが、「execution を block」しない
```

現在の実装:
- AI が decision を記録
- mocka_decision_write() で Decision Ledger に追記
- その後、mocka_write_event() が実行される
- 人間による STOP point がない

### 外部議論との関連性
**DIRECTLY_RELATED**

外部での「Human-in-the-loop」との概念:
- MoCKA (要求): 人間による最終判断
- 外部: human approval gate

### 相違点
- 共通: 人間による最終チェック
- MoCKA: ドキュメント上の要求だが実装なし
- 外部: 明示的な approval workflow の要求

---

## 9. Governance → Side Effect 単一経路

### 左側（越える前）
- execution 指令
- 誰が何をしたいのか（who/what/why）

### 右側（越えた後）
- side effect の実行
- system state の変更
- DB への永続化

### 分離の目的
**governance を通さない side effect を禁止**
- 全ての write operation は governance経由
- bypass 経路がない

### 越える条件
1. mocka_write_event() を呼び出す
2. PHI-OS Event Gate (HTTP) へ POST
3. または、直接 process_event() を呼び出す（fallback）

### 条件を判定するのは
**PHI-OS Event Gate (single entry point)**

### Runtime での強制
**YES - PARTIALLY**

実装経路:
```
1. mocka_mcp_server.py:700-738 mocka_write_event()
   r = requests.post(GATE_URL, json=gate_payload, timeout=5)
2. app.py:80 に phi_os.event_gate を register
3. phi_os/event_gate.py:115-135 process_event()
   - validate(payload) で検査
   - _write() で DB に INSERT
   - integrity.sign_event() で署名
4. fallback: mocka_mcp_server.py:725-738
   - HTTP fail時はインプロセスで process_event() を直接呼び出し
   - 同じ validation を通す
```

**ただし、bypass は物理的には可能**:
```
- 直接 SQL で events table に INSERT することは技術的に可能
- unsigned_event violation として検知される（事後）
- hash chain で検出される（事後）
```

### 外部議論との関連性
**INDIRECTLY_RELATED**

外部での「single source of truth」「audit trail」との関連:
- MoCKA: single entry point + signature chain
- 外部: immutable audit log

### 相違点
- MoCKA: detection-based（bypass を検知）
- 外部: prevention-based（bypass を物理防止）

---

## 10. Execution → Evidence 結び付け

### 左側（越える前）
- execution が行われたという事実

### 右側（越えた後）
- その execution が記録された
- who が何をしたか、いつ、なぜを記録
- authority/decision/reason と紐付けられた

### 分離の目的
**executionの accountability**
- 実行後に「何が起きたか」を追跡可能に
- AI が何をしたか、誰が authorize したかを記録

### 越える条件
1. mocka_write_event() が実行される
2. PHI-OS Gate で event_id が生成される
3. event_id = E{YYYYMMDD}_{micros}{hex}
4. integrity.sign_event() で signature が付与
5. hash chain で previous_hash が記録

### 条件を判定するのは
**PHI-OS Event Gate (process_event)**

### Runtime での強制
**YES - PASS**

実装経路:
```
1. phi_os/event_gate.py:34-43 _next_event_id()
   - time-ordered unique id を生成
2. phi_os/event_gate.py:46-100 _write()
   - payload を events table に INSERT
3. phi_os/integrity.py:91-95
   - integrity.sign_event(conn, row) で署名
   - current_hash (trace_id) と previous_hash (related_event_id) を記録
4. hash chain により順序と改ざんを検知可能
```

### 外部議論との関連性
**DIRECTLY_RELATED**

外部での「evidence」「audit trail」との概念:
- 共通: execution と authority/decision を結び付ける記録

### 相違点
- 共通: accountability の記録
- MoCKA: signature + hash chain による改ざん検知
- 外部: timestamped audit log

---

## 境界マトリックス統合表

| # | Boundary | 分離対象 | Runtime 強制 | 実装状況 | Gap |
|----|----------|--------|-------------|--------|-----|
| 1 | Knowledge → Action | read vs write | YES | complete | なし |
| 2 | Reasoning → Execution | thinking vs doing | YES | complete | なし |
| 3 | Authority → Action | who vs what | PARTIAL | authentication only | authorization scope なし |
| 4 | Scope → Action | resource boundary | YES | complete | なし |
| 5 | Approval → Execution | policy vs execution | PARTIAL | automatic only | human approval UI なし |
| 6 | Context → Execution | state consistency | NO | not implemented | time gap 検知なし |
| 7 | Policy → Execution | rule-based decision | YES | complete | なし |
| 8 | Human Gate → Execution | machine vs human | NO | documented only | 実装なし |
| 9 | Governance → Side Effect | single path | YES | detection-based | physical prevention なし |
| 10 | Execution → Evidence | action vs record | YES | complete | なし |

---

## 外部議論との関連性マッピング

### 外部で提示された概念

1. **Irreversibility / Consequence**
   - 関連: Knowledge → Action, Scope → Action
   - 相違: MoCKA は"実行不可にする"、外部は"結果を戻す"

2. **Authority / Authorization**
   - 関連: Authority → Action
   - 相違: MoCKA は身元確認、外部は権限定義

3. **Context / Approval**
   - 関連: Approval → Execution, Context → Execution
   - 相違: MoCKA は機械的チェック、外部は人間判定

4. **Standing / Who decides**
   - 関連: Human Gate → Execution
   - 相違: MoCKA は未実装、外部は要求

5. **Reversibility**
   - 関連: Execution → Evidence
   - 相違: MoCKA は"記録して追跡可能に"、外部は"実行を戻す"

---

## 確認された UNKNOWN

1. **Human Gate の実装意図**
   - documented が実装されない理由
   - 今後の実装予定

2. **Context re-grounding の必要性**
   - time gap が実際に問題になるか
   - tolerance level

3. **Authority scope の定義**
   - who_actor ごとの permission matrix の必要性
   - 現在の all-write-allowed design の意図

4. **Bypass detection sufficiency**
   - signature chain による detection で十分か
   - physical prevention の必要性

---

## 次の確認対象

以下は Human Gate で判定される事項として return される:

1. Human Gate の実装が本当に必要か
2. Context re-grounding の実装が必要か
3. Authority scope を明示化する必要か
4. Direct write を物理防止する必要か

**これらの判定は実装Authorization ではなく、設計ゴーの再確認として**

---

No Evidence, No Pass.
Unknown must be preserved.
Baseline remains frozen.
No adoption by implication.

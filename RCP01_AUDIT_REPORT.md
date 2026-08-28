# MoCKA Boundary Reality Contact Audit (RCP-01)
# 最終監査報告書

監査日時: 2026-08-28
監査官: Claude Code
対象: MoCKA Runtime Governance Implementation

---

## 中心命題

「MoCKAは、AIが情報を持つこと、判断すること、または過去に承認を得たことだけでは、実際の行為を実行できないように、実行時の境界をRuntimeで強制しているか。」

---

## Boundary Matrix - 検査結果

### 1. Knowledge → Action
**判定: PASS**

証拠:
- GL7 Dry Run により、知識取得だけでは execution に到達しない
- before_tool() で必ず実行制御が介入
- Fail Closed: Governance Pipeline unavailable でも READ_ONLY_TOOLS のみ許可

実装: `mocka_mcp_server.py:480-507` (execute_tool/Fail Closed)

---

### 2. Reasoning → Execution
**判定: PASS**

証拠:
- GL6 Pre-Answer Checklist が execution 直前に検証される
- checklist が OK でなければ GL7_EXECUTION_BLOCKED
- Reasoning の結果だけでは execution に到達しない

実装: `structural/governance_pipeline.py:91-136` (before_tool/GL6+GL7)

---

### 3. Authority → Action
**判定: PARTIAL**

証拠:
- who_actor は validation で必須（legacy values 禁止）
- who_session は SESSION_YYYYMMDD_HHMMSS 形式に限定
- ただし、「具体的なaction」への権限束縛は弱い（all write tools に適用される one-size-fits-all）

不確定点:
- who_actor の権限 scope が明示的に定義されていない
- "Claude-sonnet-4-6" が何を実行できるか明記されていない

実装: `phi_os/gate_validator.py:8-47` (validate/REJECT-01)

---

### 4. Scope → Action
**判定: PASS**

証拠:
- scope パラメータが GL7 dry_run で検証される
- 変更ファイルが scope の外なら deletion_outside_scope abort
- expected_new_dirs で新規ディレクトリ作成を制御

実装: `structural/execution_governance.py:145-179` (check_abort_conditions/scope)

---

### 5. Approval → Execution
**判定: PARTIAL**

証拠:
- GL7 dry_run が execution 前に必ず実行される
- PHI-OS Gate validation が execution 直前に実行される
- しかし「人間による approval」の停止点が見つからない

不確定点:
- CLAUDE.md は「Human Gate 承認必須」と宣言
- 実装上では「機械的な 3 層検査」のみが見つかった
  1. GL7 Dry Run (機械的)
  2. GL6 Pre-Answer Checklist (機械的)
  3. PHI-OS Gate Validation (機械的)
- 人間が実行を「停止」できる UI/flow が見つからない

判定理由: Approval は記録（Decision Ledger）されるが、execution block point ではない

実装: `structural/governance_pipeline.py:106`, `phi_os/event_gate.py:115-135`

---

### 6. Context → Execution
**判定: PARTIAL**

証拠:
- GL7 dry_run は execution 前のその時点の repository state を見る
- ただし、GL7 承認後から execution までの間に「再検証」がない
- レース条件: 他のプロセスが context を変更した場合、検知されない

具体的な問題:
```
時刻 T0: GL7 dry_run チェック ← OK
時刻 T1: (別プロセスが git commit)
時刻 T2: mocka_write_event 実行 ← context は変わった
```

この間に PHI-OS Gate が値フォーマット再検証するため、catastrophic bypass は低い。
しかし、repository state の時間差は存在する。

実装: `mocka_mcp_server.py:480-510` (execute_tool flow に再検証がない)

---

### 7. Policy → Execution
**判定: PASS**

証拠:
- GATE_POLICY_VERSION がバージョン管理されている
- policy_engine が GL1 で policy を確認
- policy が変われば execution decision は変わる

実装: `interface/gate_policy.py`, `structural/governance_pipeline.py:96`

---

### 8. Human Gate → Execution
**判定: DOCUMENTED_ONLY**

証拠:
- **Document**: CLAUDE.md 「Phase18以降: コアシステムファイルへの書き込みは人間ゲート承認必須」
- **Implementation**: 見つからない
  - human_gate.py は複数ファイルに存在するが、実行制御への統合がない
  - COMMAND CENTER に Human Gate UI がない

結論: 概念は定義されているが、実装上の実行停止点が確認できない

---

### 9. Governance → Side Effect 単一経路
**判定: PASS**

証拠:
- events table への write は 2 つのパスのみ:
  1. process_event() (AI governance write)
  2. process_buffered_event() (operational telemetry)
- 両方が _write() → integrity.sign_event() を通す
- CLI scripts は events table への直接 write をしていない

bypass 検知:
- hash_mismatch: direct DB edit を検知
- unsigned_event: integrity.sign_event を通さない write を検知
- chain_break: write path の改ざんを検知

**ただし、bypass is detected but not prevented**

実装: `phi_os/event_gate.py:46-100` (_write), `phi_os/integrity.py:244-270` (detection)

---

### 10. Execution → Evidence
**判定: PASS**

証拠:
- mocka_write_event の実行は必ず event_id で記録される
- event_id は time-ordered unique (E{YYYYMMDD}_{micros}{hex})
- signature + hash chain で execution と authority を結び付ける
- Decision Ledger に decision_id で approval を記録

実装: `phi_os/event_gate.py:34-43` (event_id generation), `phi_os/integrity.py` (signature)

---

## Boundary Matrix サマリー

| Boundary | 判定 | 理由 |
|----------|------|------|
| Knowledge → Action | PASS | GL7 dry_run が介入 |
| Reasoning → Execution | PASS | GL6 checklist が検証 |
| Authority → Action | PARTIAL | scope 定義が implicit |
| Scope → Action | PASS | expected_new_dirs で制御 |
| Approval → Execution | PARTIAL | 機械的検査のみ、人間 gate 見つからない |
| Context → Execution | PARTIAL | 時間差レース条件存在 |
| Policy → Execution | PASS | バージョン管理・検証実装 |
| Human Gate → Execution | DOCUMENTED_ONLY | 実装なし |
| Governance → Side Effect | PASS | 単一 entry point (detection-based) |
| Execution → Evidence | PASS | event_id/signature で記録 |

---

## 反証テスト結果

### テスト 1: Authority なしで non-read-only action 実行
**Result: BLOCKED**
- GL7 execute_tool() が before_tool() を呼ぶ
- READ_ONLY_TOOLS でなければ dry_run が実行
- Expected: ✓ BLOCKED

### テスト 2: Governance unavailable でも execution
**Result: FAIL-CLOSED**
- mocka_mcp_server.py:482-489 の Fail Closed 実装
- _governance が None なら READ_ONLY_TOOLS のみ許可
- Expected: ✓ BLOCKED

### テスト 3: GL7 OK 後に git repository が変わった場合
**Result: PARTIAL DETECTION**
- GL7 dry_run は時点 T0 の state を見る
- 時刻 T1 に別プロセスが commit
- mocka_write_event 実行時は古い state でチェック済み
- PHI-OS Gate は value format のみ再検証（repository state は見ない）
- Expected: ✓ but time-gap vulnerability exists

### テスト 4: Governance を経由せず直接 events.db に write
**Result: DETECTED (not prevented)**
- 直接 write は技術的に可能（SQL access あれば）
- unsigned_event violation として検知される
- hash_chain で検出される
- Expected: ✓ detected, but not physically prevented

### テスト 5: 未知のツール追加後の execution
**Result: GOVERNED**
- READ_ONLY_TOOLS に含まれない tool は全て GL7 governed
- unknown_tool も dry_run 対象
- Expected: ✓ DEFAULT DENY effective

---

## 最も重要な未検証点

### 1. Human Gate の実装ギャップ
- **問題**: ドキュメント上は「Human Gate 承認必須」
- **実装**: UI/approval block point が見つからない
- **影響度**: High - execution 직전の人間による停止能力が不明
- **推奨**: Human Gate の実装状態を確認、または概念を廃止して設計統一

### 2. Context レース条件
- **問題**: GL7 OK と execution の間に時間差がある
- **影響度**: Medium - PHI-OS Gate が direct value validation で軽減
- **推奨**: execution 直前の再 grounding check の追加検討

### 3. Direct write prevention vs detection
- **問題**: bypass の物理防止ではなく検知に依存
- **影響度**: Low - signature chain で detection は robust
- **推奨**: database-level ACL での物理防止の検討（Phase N）

### 4. Authority scope の明示化
- **問題**: who_actor が何を実行できるか implicit
- **影響度**: Medium - 権限管理の clarity が低い
- **推奨**: RBAC or capability-based policy の導入検討

---

## MoCKA の現実的な Boundary Status

### ✓ 実装されて Runtime で強制される境界
1. Knowledge → Action (GL7 dry_run)
2. Reasoning → Execution (GL6 checklist)
3. Scope → Action (expected_new_dirs)
4. Policy → Execution (policy version control)
5. Governance → Side Effect (single entry point)
6. Execution → Evidence (event_id + signature)

### ✗ 文書上だけ存在する境界
1. Human Gate → Execution (実装なし)

### ⚠️  部分的/弱化された境界
1. Authority → Action (implicit scope)
2. Approval → Execution (機械的のみ)
3. Context → Execution (時間差)

---

## 結論

**中心命題への回答:**

「MoCKAは、AIが情報を持つこと、判断することだけでは実行できないように、多層の Runtime 制御（GL7 dry_run, GL6 checklist, PHI-OS validation）を実装している。ただし、人間による実行停止の能力は ドキュメント上は宣言されているが実装上は確認できない。」

### MoCKA の強み
- **多層的な機械的検査** (GL1-GL7)
- **single entry point** のほぼ完全な実装
- **evidence & signature chain** による audit trail
- **bypass detection** の実装

### MoCKA の弱み
- **Human Gate** の非実装またはドキュメント乖離
- **Time gap vulnerability** (GL7 と execution の間)
- **Authority scope** の implicit 管理
- **Direct write** の物理防止ではなく検知依存

---

## 次フェーズで検証が必要な項目

1. **Human Gate**: Specification確認 → 実装推進 OR 廃止決定
2. **Re-grounding**: execution 直前の context 再検証 feasibility
3. **RBAC**: who_actor ごとの capability matrix 定義
4. **DB-level ACL**: SQLite への direct write 物理防止

---

NO EVIDENCE, NO PASS.
UNKNOWN MUST BE PRESERVED.
BASELINE MUST REMAIN UNCHANGED.
IMPLEMENTATION CHANGES ARE PROHIBITED.

このレポートは監査のみを目的とする。実装変更は含まない。

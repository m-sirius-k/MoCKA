# MOCKA BUTTERFLY EFFECT CONTROL POLICY v1.0 Draft-01

## 1. Policy Identity

**Name:**
MOCKA BUTTERFLY EFFECT CONTROL POLICY v1.0

**Status:**
Draft-01

**Effective Date:**
2026-10-01（Draft開始日）

**Authority:**
Human Gate Review Panel

**Mode:**
Design Document (実装前Design Phase)

**Scope:**
- MoCKA Governance Layer
- MoCKA Runtime Execution
- MoCKA Event Store
- MoCKA Memory System
- AI Authority Boundary

---

## 2. Butterfly Effect Definition

### 2.1 MoCKAにおけるバタフライエフェクト

複雑系でのバタフライエフェクトとは、「初期状態の小さな差異が、時間経過後に大きな結果差を生む現象」を指す。

MoCKAにおいて特に危険なのは、単なる技術的バグではなく、以下のような **連鎖増幅パターン** である：

```
Small State Difference
        ↓
Evidence Difference
        ↓
Context Difference
        ↓
Decision Difference
        ↓
Authority Difference
        ↓
Runtime Difference
        ↓
Institutional Memory Difference
```

### 2.2 具体例

**例1: Decision欠落による権限混同**
```
Decision_ID missing from Event
    ↓
AI が past decision を参照できない
    ↓
同じ判断を再実行
    ↓
Authority boundary が実質消失
    ↓
governance失効
```

**例2: Event Store記録欠落による状態喪失**
```
Event write失敗（未記録）
    ↓
Memory が事実を知らない
    ↓
AI が存在しない状態を前提に判断
    ↓
実装が乖離
    ↓
Replay不能
```

**例3: Memory Drift による誤判断**
```
旧 Phase状態がCacheに残る
    ↓
AI が「まだ未完了」と誤認
    ↓
不要な修正提案
    ↓
実装破壊
```

---

## 3. Detection Layer Architecture

バタフライエフェクト防止は、4層の検知・制御を通じて実装される。

### Layer A: Decision Layer

**対象:**
- Decision_ID の存在
- Authorization Scope の定義
- Runtime Scope の明示

**検知条件:**
```
Decision exists
AND
Runtime request has no reference
```

**例:**
```
Error State:
  - Decision_ID = DC_20260912_001
  - Runtime Request: {decision_id: null}
  
Result:
  BLOCK + INCIDENT_RECORD
```

**Action:**
1. Block execution
2. Record incident (IC-{date}-{seq})
3. Request Human Gate Review
4. Do NOT proceed silently

### Layer B: Event Store Layer

**対象:**
- Event Write成功の確認
- Event ID 採番
- Read Back検証

**完了条件 (5段階):**
```
EXECUTED
    ↓
EVENT_CREATED
    ↓
EVENT_ID_ASSIGNED
    ↓
READ_BACK VERIFIED
    ↓
MONITORED
```

**禁止状態:**
```
EXECUTED
without
EVENT_VERIFIED
```

**Rule:**
- Write ACK ≠ Persistence（WRITE ACKだけでは成功と見なさない）
- Read Back 必須（実際にデータベースから読み戻して検証する）
- Idempotency確認（同じevent_idが2回作成されていないか）

### Layer C: Runtime Traceability Layer

**対象:**
各Execution State の分離記録

**必須状態遷移:**
```
CONFIGURED
    ↓
CONNECTED
    ↓
EXECUTED
    ↓
VERIFIED
    ↓
MONITORED
```

**各状態の意味:**
- CONFIGURED: 設定は完了だが、接続は確認していない
- CONNECTED: プロセス/ポート が応答確認済み
- EXECUTED: 実行指令が送られた
- VERIFIED: 実行結果が読み戻される
- MONITORED: 継続監視中

**禁止:**
- CONFIGURED を CONNECTED と混同する（Process existsはAPI responseを保証しない）

### Layer D: Memory Consistency Layer

**対象:**
Memory の3層分離

**分類:**
```
Tier 1: Current State
  - 現在の状態
  - 即時更新
  - AI参照時は PRIORITY

Tier 2: Historical Record
  - 過去のイベント
  - 参照のみ
  - AI判断の背景根拠

Tier 3: Decision Memory
  - 「なぜそう判断したか」の理由
  - 権限境界の記録
  - Human Gate承認の証拠
```

**混在禁止:**
```
Error: Current State と Historical が混在
         → AI が旧状態で判断
```

---

## 4. Risk 001-007 と Prevention Rules

### Risk 001: Human Gate判断記録の初期差異

**対象:**
Decision_ID / Authorization_Scope / Forbidden_Action

**Prevention:**
- Decision Schema 必須項目化
  - decision_id (unique)
  - decision_object
  - authorization_scope
  - runtime_scope
  - allowed_action
  - forbidden_action
  - evidence_requirement
  - expiration

- System constraint化

### Risk 002: Event Store記録欠落

**対象:**
Event の完全永続化

**Prevention:**
- Write保証: EXECUTED → EVENT_VERIFIED
- Recurrence monitoring: ≥2件の同種miss → escalate
- Read Back mandatory

### Risk 003: AI Runtime判断の自己増幅

**対象:**
Authority boundary混同

**Prevention:**
- Role separation固定
  - HAB = Intelligence Provider
  - JARVIS = Conductor
  - Human Gate = Authority Holder
- AI出力に必須フィールド付与
  - Recommendation
  - Evidence
  - Uncertainty
  - Human Decision Required

### Risk 004: Git変更による潜在的波及

**対象:**
Single File Change → Runtime Impact

**Prevention:**
- Change unit: Code Change + Impact Analysis + Runtime Verification + Rollback Point
- 必須: 変更前状態保存 → 変更 → 実Runtime確認 → Read Back

### Risk 005: Working Context / Memory Drift

**対象:**
旧情報参照による誤判断

**Prevention:**
- Memory 3層分離（Current / Historical / Decision）
- AI参照時: Current State優先

### Risk 006: MCP / Relay / Port接続状態

**対象:**
CONFIGURED ≠ CONNECTED 混同

**Prevention:**
- 毎回検証: Process Exists → Port Listening → API Response → Event Created → Read Back
- 5段階確認必須

### Risk 007: 商用展開時の制度的増幅

**対象:**
Mini-MoCKA ユーザー向け説明

**Prevention:**
- 必須表現固定化
  - "MoCKA does not replace human authority"
  - "MoCKA records, verifies, and governs AI-assisted decisions"

---

## 5. Butterfly Prevention Rule Set

### Rule BE-001: 記録と実装の分離管理

**Statement:**
記録された状態（Log/Event）は、実装された状態（Source Code）とは別管理する。

**禁止:**
```
Log exists
    =
Current System Capability
```

**許可:**
```
Log exists
AND
Source Verification
AND
Runtime Verification
```

**Example (IC-BA04-001):**
```
Observed:
  Event Log: "GL7 abort: BA04_DECISION_ID_MISSING"

Found:
  Source Code: NO IMPLEMENTATION

Action:
  Do NOT assume BA04 is active
  Classify: UNKNOWN
  Require verification
```

### Rule BE-002: Historical Evidence と Current State の分離

**Statement:**
過去イベントは未来判断の唯一根拠にしない。

**必須:**
```
Historical Evidence
    +
Current Runtime State
    +
Decision Authority
```

**Example:**
```
Error Pattern:
  "Phase is still Phase4 (historical log)"
  → AI decides: "Phase4 maintenance needed"
  → Reality: Current Phase is Phase5
  → Impact: Wrong governance applied

Prevention:
  Always check: Current MOCKA_OVERVIEW.json
             + Historical event
             + Decision Ledger latest
```

### Rule BE-003: 未確定状態の停止条件

**Statement:**
UNKNOWN / NOT FOUND / CONFLICT 状態は「停止対象」として扱う。

**処理:**
- No Expansion（範囲拡張禁止）
- No Authorization Increase（権限昇格禁止）
- Require Verification（検証待ちへ）

**Example (IC-BA04-001):**
```
Classification: UNKNOWN
Status: STOP pending verification
  ↓
DO NOT use BA04 as governance rule
  ↓
DO NOT expand abort conditions based on BA04
  ↓
DO NOT assume BA04 implementation exists
```

### Rule BE-004: Small Change Audit Inversion

**Statement:**
小さい変更ほど大きく監査する。

**通常システム:**
```
Large Change → Strict Audit
Small Change → Simple Audit
```

**MoCKA:**
```
Initial Condition Change → Maximum Audit
Small Code Change → Full Impact Analysis
1-Line Change → Rollback Plan Required
```

### Rule BE-005: Proof of Execution

**Statement:**
実行結果は「ツール戻り値」ではなく「状態変化読み戻し」で確認する。

**禁止:**
```
Tool returns {"status": "ok"}
    =
Task complete
```

**必須:**
```
Tool returns {"status": "ok"}
    ↓
Read back actual data
    ↓
Verify state changed
    ↓
Then: Task complete
```

---

## 6. Incident Case: IC-BA04-001

### 6.1 Case Identity

**Case ID:**
IC-BA04-001

**Title:**
GL7 Abort Code DECISION_ID_MISSING: Source vs Record Divergence

**Discovery Date:**
2026-10-01

**Classification:**
UNKNOWN (Investigation Ongoing)

### 6.2 Observed State

**Event Log Evidence:**
```
Event Record:
  event_id: E20260930_76553730773d7
  when_ts: 2026-09-30T07:36:05.537333+00:00
  what_type: governance_block
  where_component: ba04_execution_gate
  title: "[GOVERNANCE_BLOCK] mocka_write_event"
  short_summary: "Tool: mocka_write_event
                  Reason: GL7 abort: ['BA04_DECISION_ID_MISSING']
                  req_id: N/A
                  decision_id: N/A"
  
Frequency: Multiple (10+ occurrences 2026-09-30 to 2026-10-01)
```

### 6.3 Investigation Result

**Source Code Search:**
```
Target: BA04_DECISION_ID_MISSING implementation

Scanned:
  - structural/execution_governance.py    → NOT FOUND
  - structural/governance_pipeline.py     → NOT FOUND
  - phi_os/gate_validator.py              → NOT FOUND
  - interface/gate_policy.py              → NOT FOUND
  - mocka_mcp_server.py (write_event)     → NOT FOUND

Result: NO IMPLEMENTATION DETECTED
```

**Abort Code Generator Search:**
```
Expected locations:
  - ABORT_CONDITIONS in execution_governance.py
  - validate() checks in gate_validator.py
  - reason_code generation

Found:
  - execution_governance.ABORT_CONDITIONS:
    ["new_directory_detected", "unexpected_file_count", 
     "deletion_outside_scope", "grounding_not_completed"]
    → BA04_DECISION_ID_MISSING NOT PRESENT

Result: GENERATION SOURCE UNKNOWN
```

### 6.4 Contradiction State

**State Chart:**
```
┌─────────────────────────────┐
│  Event Record Exists        │
│  (Multiple instances)       │
│  GL7 abort: BA04_..MISSING  │
└────────────────┬────────────┘
                 │
                 ↓
     ┌───────────────────────┐
     │ Source Code Search    │
     │ BA04_DECISION_ID_MISSING
     │ NOT FOUND             │
     └───────────────────────┘
                 │
                 ↓
     Divergence Detected
     Evidence ≠ Implementation
```

### 6.5 Classification Candidates

**Candidate B: Runtime Divergence**
- Hypothesis: Code version mismatch
- Current source ≠ Running process
- Evidence: NOT verified (local env only)

**Candidate D: Record Layer Issue**
- Hypothesis: Event store captures legacy code traces
- Historical events not cleaned
- Evidence: NOT verified (local env only)

**Final Classification:**
UNKNOWN (Verification required from production environment)

### 6.6 Recommended Action

**Immediate:**
1. DO NOT rely on BA04 as governance rule
2. DO NOT assume BA04 blocks are valid
3. DO NOT expand scope based on BA04

**Next Step:**
- Verify in production runtime
- Confirm abort code generator
- Trace event record origin
- Determine if legacy or active

**Escalation:**
If verified as B (Runtime Divergence):
  → Rollback process or update source
If verified as D (Record Layer):
  → Clean historical records or document legacy events

---

## 7. Human Gate Re-Authorization Conditions

バタフライエフェクト制御ポリシーの対象となる変更が発生した場合、新たなDecision Recordが必須。

### 7.1 Re-Authorization Trigger Events

以下の場合は Human Gate 再審査対象：

```
Decision Schema変更
  ↓ (e.g., new required field in decision_ledger.jsonl)

Authorization Scope変更
  ↓ (e.g., expand/restrict which AItools can call mocka_write_event)

Event Schema変更
  ↓ (e.g., add/remove column in events table)

Memory Structure変更
  ↓ (e.g., split Historical into Tier2a/Tier2b)

Gate Logic変更
  ↓ (e.g., new ABORT_CONDITIONS in execution_governance.py)

Process Binding変更
  ↓ (e.g., move GATE_URL to new port)
```

### 7.2 Re-Authorization Checklist

```
New Decision Record Required:
  [ ] decision_id (DC_YYYYMMDD_...)
  [ ] Change object (what is changing)
  [ ] Authorization scope (who can use it)
  [ ] Impact analysis (which systems affected)

Rollback Point Required:
  [ ] Before state preserved
  [ ] Revert procedure documented
  [ ] Test rollback (if applicable)

Evidence Required:
  [ ] Why this change
  [ ] Alternatives considered
  [ ] Risk assessment
  [ ] Mitigation strategy
```

---

## 8. Principle vs Practice

### 8.1 MoCKA Three Core Elements

```
Structure (構造)
  ↓ システムで縛る。信頼しない

Record (記録)
  ↓ 記録なき作業はMoCKAとして存在しない

Verification (検証)
  ↓ UTF-8・整合性・動作を必ず確認する
```

Butterfly Effect Control は、この3要素を強化する具体的な制度。

### 8.2 UNKNOWN は ABSENT ではない

```
NOT FOUND (IC-BA04-001)
    ≠
Does not exist

RECORDED
    ≠
VERIFIED

CONFIGURED
    ≠
CONNECTED
```

このポリシーは、これらの区別をシステムで実装し、未確定状態では進まないルールを確立する。

---

## 9. Policy Version History

**v1.0 Draft-01 (2026-10-01)**
- KUROKO WEB Butterfly Effect Investigation 基づく
- IC-BA04-001 (UNKNOWN case) 組込
- 4層Detection Layer定義
- 7層Risk対応ルール定義
- 5つの Butterfly Prevention Rule定義
- Human Gate再承認条件定義

---

## 10. Next Steps

### Phase 1: Design Validation (Current)
- Policy Draft presentation to Human Gate
- IC-BA04-001 verification plan approval
- Scope boundary confirmation

### Phase 2: Implementation (Post-Approval)
- STEP 1B: Risk 001-007 実装監査
- Layer A-D Detection implementation
- Monitoring dashboard setup

### Phase 3: Operational (Post-Implementation)
- Live monitoring
- Incident response procedure
- Policy refinement based on incidents

---

**Document Status:**
Draft-01 (2026-10-01 03:XX:XX UTC)

**Authority:**
Human Gate Review Panel (きむら博士)

**Approval Status:**
Pending Review

---

EOF

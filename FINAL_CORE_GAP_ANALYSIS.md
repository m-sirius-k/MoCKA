# 【最終技術ギャップ分析】

## CORE GAP MATRIX

| Gap # | 項目 | 現物証拠 | 実装状態 | HAB Impact | JARVIS Impact | 分類 |
|-------|------|---------|---------|----------|--------------|------|
| **1** | Decision ID Atomicity | mocka_mcp_server.py:436-448 | VERIFIED RISK: max(used)+1パターン、non-atomic | **POTENTIAL BLOCKER** | N/A | Technical |
| **2** | Full Request→Decision→Execution Trace | decision_ledger.jsonl: request_id field なし、related_events field あり | BROKEN: request_id→event◎、event→decision◎、decision→execution✗ | **PARTIAL TRACE** | **BROKEN TRACE** | Technical |
| **3** | Consequence→Knowledge | app.py:auto_update_essence_from_mataka() | PARTIAL: MATAKA専用、一般化されていない | N/A | **POST-MVP** | Design |
| **4** | Knowledge Gate Round-Trip | mocka_mcp_server.py:663-667 + app.py | VERIFIED: 5000依存、fallback無し、ファイル永続化◎ | N/A | **PORT 5000 REQUIRED** | Architectural |
| **5** | REM (alternatives schema) | decision_ledger alternatives: {option, rejected_reason} | NOT APPLICABLE: REM未定義、alternatives未検証 | N/A | **POST-MVP** | Requirement Gap |

## 判定ロジック

### 1. Decision ID Atomicity

**現状:** Flask single process、threaded model、max+1 生成方式  
**リスク:** 同時write時にID重複可能  
**HAB MVP:** ID重複=Ledger integrity喪失（重大）  
**判定:** **POTENTIAL BLOCKER** ← しかし実装は可能（fix時間30分）

### 2. Full Request→Decision→Execution Trace

**現状:**
- request_id→event: 11イベント に request_id存在 ✓
- event→decision: 153決定に related_events存在 ✓
- decision→execution: execution_id field **なし** ✗
- execution→essence: 直結無し（MATAKA経由のみ）

**分析:** Multi-AI共有状態の再構成に不可欠だが、schema追加で可能  
**HAB MVP:** Request→Decision まで追跡可能なら partial trace でOK  
**JARVIS MVP:** Full trace (execution→essence) 必須 → **BLOCKING**

### 3. Consequence→Knowledge Pipeline

**現状:** app.py only MATAKA→essence update実装  
**分析:** 一般的execution_result→knowledge pipeline**無し**  
**JARVIS:** 必須だが設計レベル → **POST-MVP**

### 4. Knowledge Gate Round-Trip

**現状:** port 5000 必須、fallback 無し  
**分析:** 5000が起動前提 → Architectural constraint（NOT blocker）  
**JARVIS:** 必須 runtime dependency

### 5. REM

**分析:**
- REM自体がMVP要件として定義されていない  
- alternatives schema は "rejected_reason" only  
- "adopted as evidence" 表現不可（設計ギャップ）  
- **が、MVP開始に必須ではない**

---

## 最終判定

### HAB MVP

**Technical Status: READY FOR IMPLEMENTATION**

Condition: Decision ID atomicity を並列安全方式に修正（30分）  
Root cause: max+1→time-ordered+random に変更のみ

**実装可能:** YES  
**実装前条件:** 1件 (Decision ID fix)  
**Blockers:** 0 (条件解消後)

### JARVIS MVP

**Technical Status: BLOCKED**

Blocking issues:
1. **Decision→Execution trace missing** (execution_id field)  
2. **Consequence→Knowledge general pipeline** (MATAKA only)  
3. **Port 5000 architectural dependency** (mitigatable but constraint)

Unblocking path:
- Add execution_id to decision_ledger schema
- Implement general execution_result→essence ingest pipeline
- (Optional) Add file fallback to mocka_get_essence

Estimated work: **3-5 days**

---

## ONE NEXT ACTION

**RECOMMENDATION: B. Add execution_id to Decision Ledger schema + implement execution_result→essence bridge**

Why: 
- HAB can start immediately (after ID atomicity fix)
- JARVIS blocker is SPECIFICALLY missing trace connection
- One focused technical fix unblocks JARVIS

Cost: 
- Schema: 1 hour (add field)
- Bridge: 2-3 days (implementation + test)
- Total: SHORT CRITICAL PATH

Not recommended:
- A (HAB only) — wastes JARVIS setup time
- C/D/E — governance decisions, not technical fixes

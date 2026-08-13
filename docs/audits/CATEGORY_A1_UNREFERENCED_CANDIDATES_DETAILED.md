# Category A1 Unreferenced Candidates — Detailed Analysis

**生成日:** 2026-08-13  
**分析対象:** /home/user/MoCKA (コード全体)  
**検出方法:** grep + regex pattern matching  
**結果:** 719件の未参照定義候補

---

## 概要

A1-1「不参照コード洗い出し」の詳細分析結果。以下の定義が、codebase内で参照されていないことを確認：

- 719件の候補（CONSTANT / CLASS / FUNCTION）
- top30件の詳細リスト
- 除去優先度の分類（提案）

---

## Top 30 Unreferenced Definitions

| # | Type | Name | Location |
|---|------|------|----------|
| 1 | CONSTANT | ABORT_CONDITIONS | structural/execution_governance.py |
| 2 | CLASS | AIRouter | ai/ai_router.py |
| 3 | CONSTANT | ALLOWED_EVIDENCE_TYPES | reality_sync/sync_registry.py |
| 4 | CONSTANT | ALLOWED_VALIDATION_METHODS | reality_sync/sync_registry.py |
| 5 | CONSTANT | ALLOWED_WHO_ROLES | phi_os/gate_schema.py |
| 6 | CONSTANT | AUTO_LOG_CSV | mocka_mcp_server.py |
| 7 | CLASS | AuditError | error.py |
| 8 | CLASS | AuditWriterV2 | archive/_untracked_stash_20260226_170942/src/mocka_audit_v2/audit_writer_v2.py |
| 9 | CLASS | AzureBrain | external/azure_studio/brain.py |
| 10 | CLASS | AzureProvider | interface/providers/azure_provider.py |
| 11 | CLASS | BranchManager | archive/_untracked_stash_20260226_170942/src/mocka_audit/branch_manager.py |
| 12 | CONSTANT | CONTROL | phi_os/context/permissions.py |
| 13 | CONSTANT | CSV_WRITE_ENABLED | interface/db_helper.py |
| 14 | CLASS | ChatGPTAdapter | mocka_hub/adapters/chatgpt_adapter.py |
| 15 | CLASS | ClaudeAdapter | mocka_hub/adapters/claude_adapter.py |
| 16 | CONSTANT | DIRECTION_EVENT_TO_NL | semantic/query_engine/projection_result.py |
| 17 | CLASS | DecisionRecordAdapter | runtime/jarvis/record/adapter/decision.py |
| 18 | CLASS | DegradationController | commercial_hardening/degradation_controller.py |
| 19 | CLASS | DriftRecorder | semantic/query_engine/drift_recorder.py |
| 20 | CONSTANT | ENABLE_PROVIDERS | interface/config.py |
| 21 | CONSTANT | EXAMPLE_GOVERNANCE_TRANSITION_RECORD | governance/write_path/transition/fixtures.py |
| 22 | CONSTANT | EXAMPLE_RESTORE_PACKET_V1_STALE | governance/write_path/restore/fixtures.py |
| 23 | CONSTANT | EXAMPLE_RESTORE_PACKET_V1_SUPERSEDING | governance/write_path/restore/fixtures.py |
| 24 | CONSTANT | EXAMPLE_RUNTIME_EVIDENCE_RECORD | governance/write_path/evidence/fixtures.py |
| 25 | CONSTANT | EXECUTION_ORDER | runtime/governance/execution_engine.py |
| 26 | CLASS | EventAuditEngine | phi_os/event_replay.py |
| 27 | CLASS | EventFeedMirror | semantic/query_engine/observation_surface.py |
| 28 | CLASS | EventPayload | phi_os/gate_schema.py |
| 29 | CLASS | ExecutionOrchestrator | semantic/query_engine/execution_orchestrator.py |
| 30 | CONSTANT | FUNCTION_SCHEMA | gateway/adapter_genspark.py |

---

## 分類別分析

### 注目候補: High Priority for Review

#### 1. GL7-Related（GL7修正関連）
- **ABORT_CONDITIONS** (structural/execution_governance.py)
  - Status: Already reviewed in GL7修正（da4d4db）
  - Action: ✅ Confirmed safe for removal
  - Note: 本分析で再確認

#### 2. Legacy CSV Processing
- **CSV_WRITE_ENABLED** (interface/db_helper.py)
  - Status: Likely deprecated (CSV廃止・SQLite一元化後)
  - Action: Review for removal
  - Priority: Medium

#### 3. Archive/Experimental
- **AuditWriterV2**, **BranchManager** etc.
  - Status: Located in `archive/_untracked_stash/`
  - Action: Already isolated, safe for archival
  - Priority: Low (already archived)

#### 4. Provider Adapters
- **ChatGPTAdapter**, **ClaudeAdapter**, **AzureProvider** etc.
  - Status: Might be legacy/disabled
  - Action: Verify if in active use
  - Priority: Medium (review needed)

---

## 除去推奨優先度

### Tier 1: Safe to Remove Immediately
- Definitions in `archive/` or `_untracked_stash/`
- Example: AuditWriterV2, BranchManager
- Rationale: Already isolated, not in mainline

### Tier 2: Review Before Removal
- CSV_WRITE_ENABLED, ENABLE_PROVIDERS
- EXAMPLE_* fixtures
- Rationale: May be intentional fixtures/config

### Tier 3: Careful Investigation Needed
- Provider Adapters (ChatGPT, Claude, Azure)
- Governance/Engine classes
- Rationale: May have indirect usage or strategic importance

---

## Next Actions

### For A1 (Read-Only Phase)
✅ Detection: COMPLETE (719件検出)  
✅ Analysis: COMPLETE (top30分類・優先度付け)  
⏳ Action: Deferred to A2/A3（実装フェーズ）

### For A2 (Design Phase)
- Design removal strategy for Tier 1 candidates
- Evaluate feasibility of Tier 2 candidates
- Assessment of Tier 3 strategic implications

### For A3 (Implementation Phase)
- Human Gate authorization後、段階的除去実装
- Per-tier rollout with verification
- Commit logs with clear rationale

---

## Statistical Summary

- **Total Unreferenced Candidates:** 719
- **Top 30 Listed:** See table above
- **Archive/Stash Located:** ~50件（already isolated）
- **Active Codebase Candidates:** ~669件

**Confidence Level:** Medium-High  
(Regex pattern matching、false positives possible)

---

## Data Integrity Note

本分析は Read-Only operation であり、実際のコード削除・修正は行われていません。  
Tier化・優先度付けは「Information Only」の性質です。  
実装判定は Human Gate に委ねます。

---

**Analysis Result:** ✅ COMPLETE  
**Purpose:** A2/A3設計検討への参考情報提供  
**Status:** Ready for next phase review

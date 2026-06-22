# Phase5 Boundary Declaration (Step3時点)

Status: ACTIVE
Date: 2026-06-22

本文書はPhase5 Step3完了時点で、MoCKA Time OSが何に接続されていて
何に接続されていないかを宣言する。Phase5 Step4(GPT/MCP Adapter)の
設計会議はこの境界を前提として行う。

## Connected（接続済み・内部完結）

- Replay (`relay/replay_engine.py`, `relay/replay_engine_v2.py`)
- Audit (`relay/replay_audit.py`)
- API (`phi_os/api/time_api.py` - Time API v0)
- Query (`phi_os/api/time_api.py` - Time Query v0)
- Capability (`phi_os/api/time_api.py` - Time Capability Layer)
- Semantic (`phi_os/semantic/query_resolver.py` - Semantic Query Layer v1)

これら全てはRelayKernelを唯一の入口とする内部完結した契約であり、
外部の意思決定主体(LLM/外部エージェント)からの呼び出しは想定されていない。

## Not Connected（未接続・Phase5 Step3時点では存在しない）

- GPT Adapter
- MCP Adapter
- External Agent
- External Tool

## Rule（絶対規則・Phase5 Step3時点で適用中）

1. No direct GPT access — GPTがTime OSの内部コンポーネントを直接呼び出すことは禁止。
2. No MCP execution — MCP経由でのTime OS操作(state変更・mode変更等)は禁止。
3. No external authority delegation — 外部主体への意思決定権限の委譲は禁止。

## 次フェーズへの引き渡し条件

Phase5 Step4(GPT/MCP Adapter Governance Design)の設計会議は、
本文書のConnected/Not Connected区分とRuleを前提として開始する。
Adapter設計は「既存のTime OS Contract(`docs/contracts/time_os_contract_v1.md`)
を呼び出すだけ」の境界線を越えてはならない。

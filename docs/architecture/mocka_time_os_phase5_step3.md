# MoCKA Time OS - Architecture Snapshot (Phase5 Step3)

Status: STABLE (基準線)
Date: 2026-06-22

## Layers

1. Event Layer (`relay/repositories.py` EventRepository, `relay/repositories_sqlite.py` LocalEventRepository)
2. Queue Layer (`relay/repositories.py` QueueRepository, `relay/repositories_sqlite.py` LocalQueueRepository)
3. Snapshot Layer (`relay/repositories.py` SnapshotRepository, `relay/repositories_sqlite.py` LocalSnapshotRepository)
4. Replay Layer (`relay/replay_engine.py` v1, `relay/replay_engine_v2.py` v2)
5. Replay Audit Layer (`relay/replay_audit.py` ReplayAuditLog, `relay/replay_router.py` ReplayRouter)
6. Time API Layer (`phi_os/api/time_api.py` - /time/state, /time/events, /time/replay, /time/audit)
7. Time Query Layer (`phi_os/api/time_api.py` - POST /time/query, 固定コマンド5種)
8. Capability Layer (`phi_os/api/time_api.py` - GET /time/capabilities)
9. Semantic Query Layer (`phi_os/semantic/query_resolver.py`, `phi_os/api/time_api.py` - POST /time/semantic_query)

## 依存関係図

```
Semantic
    ↓
Capability
    ↓
Time Query
    ↓
Time API
    ↓
Relay Kernel
    ↓
Replay Router
    ↓
Replay Engine
    ↓
Snapshot
    ↓
Queue
    ↓
Event
```

## 設計原則(全層共通)

- 上位層は下位層の契約のみを呼び出す。下位層の内部実装(SQLiteスキーマ等)へは直接アクセスしない。
- RelayKernelが唯一の入口(single entry point)。ReplayEngine/ReplayRouter/Repository系への直接アクセスはAPI層から禁止。
- Semantic Query Layerは「意味を理解する」層ではなく「意味をCapability Layerの既存契約へ変換するだけ」の層(固定キーワードマッピング、LLM/推論不使用)。
- 各層の追加は既存の下位層への構造変更を伴わない(非破壊・最小侵入の原則をPhase5全体で維持)。

## 関連文書

- 契約定義: `docs/contracts/time_os_contract_v1.md`
- 能力registry: `docs/contracts/capability_registry_v1.md`
- Replay検証: `docs/verification/replay_equivalence_report.md`
- 境界宣言: `docs/governance/phase5_boundary_declaration.md`
- 封印記録: `docs/releases/PHASE5_STEP3_SEAL.md`

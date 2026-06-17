# PHI-OS SEO Command Index v3

PlanningCaliber の SEO コマンドナビゲーション OS。セマンティック検索・推薦・学習・監査・Runtime統合を提供。

## Architecture

```
seo-os/
  command_index/   Phase 1 — Registry, Metadata, Category, Alias, Tag, Version, DB
  semantic/        Phase 2 — SynonymDictionary, SemanticIndex, IntentResolver, MeaningSearch, SimilarityRanking
  context_bridge/  Phase 3 — MoCKA Context Runtime v2 連携
  recommendation/  Phase 4 — Related, Next, Dependency, Workflow
  learning/        Phase 5 — 使用頻度・成功率・ランキング
  cross_repo/      Phase 6 — 複数リポジトリ横断検索
  dep_graph/       Phase 7 — 依存グラフ (JSON/SVG/HTML)
  dashboard/       Phase 8 — HTML Command Center (Flask server)
  api/             Phase 9 — REST API /api/v3/*
  runtime/         Phase 10 — UnifiedRuntime (統合オーケストレーター)
  mcp_server.py    Phase 11 — MCP Server /mcp/*
  audit/           Phase 12 — AuditLogger
  tests/           Phase 13 — 61テスト全Pass
  data/            DBファイル・スナップショット・レジストリJSON
```

## Quick Start

```bash
# REST API サーバー起動 (port 8761)
cd workshop/seo-os
python api/app.py

# Dashboard + REST API サーバー (port 8761)
python dashboard/server.py

# MCP Server (port 8762)
python mcp_server.py

# テスト実行
python -m pytest tests/test_all.py -v
```

## REST API /api/v3/

| Method | Endpoint | 説明 |
|--------|----------|------|
| GET | `/commands` | コマンド一覧 |
| GET | `/commands/<id>` | コマンド詳細+推薦 |
| GET | `/search?q=` | セマンティック検索 |
| POST | `/execute` | コマンド実行 |
| GET | `/history` | 実行履歴 |
| GET | `/recommend/<id>` | コマンド推薦 |
| GET | `/context` | Context Runtime状態 |
| GET | `/graph?format=json\|svg\|html` | 依存グラフ |
| GET | `/ranking` | 使用頻度ランキング |
| GET | `/audit` | 監査ログ |
| GET | `/workflows` | ワークフロー一覧 |
| GET | `/categories` | カテゴリ一覧 |

## MCP Tools /mcp/

| Endpoint | Tool名 |
|----------|--------|
| POST `/mcp/command.search` | クエリ検索 |
| POST `/mcp/command.execute` | コマンド実行+Gate |
| GET `/mcp/command.context` | Context状態 |
| POST `/mcp/command.graph` | 依存グラフ |
| POST `/mcp/command.recommend` | 推薦 |
| GET `/mcp/health` | ヘルス確認 |
| POST `/mcp/boot` | Runtime Boot |
| POST `/mcp/resume` | スナップショット復元 |
| POST `/mcp/snapshot` | 状態保存 |

## Memory Runtime Protocol

Boot時に Context Runtime v2 から以下の順序でコンテキストをロード:

1. **Memory** — MoCKA events DB (5W1H, incidents, decisions)
2. **Architecture** — ARCHITECTURE_REGISTRY.json (allowed/forbidden modules)
3. **Project** — MOCKA_OVERVIEW.json (phase, seal, todo)
4. **Execution** — ExecutionGate (boundary/module/permission checks)

## Builtin Commands (24)

| Category | Commands |
|----------|----------|
| seo (8) | seo.analyze, seo.metadata, seo.ogp, seo.schema, seo.keyword, seo.readability, seo.sitemap, seo.robots |
| publish (3) | publish.job.create, publish.job.approve, publish.job.run |
| distribution (4) | dist.wordpress, dist.sftp, dist.x, dist.instagram |
| caliber (3) | caliber.health, caliber.recommend, caliber.lifecycle |
| governance (3) | gov.snapshot, gov.audit, gov.boundary |
| context (3) | ctx.memory, ctx.working, ctx.resume |

## Workflows

- **seo_publish** (8 steps): analyze → metadata → ogp → schema → keyword → readability → sitemap → publish
- **seo_social** (7 steps): analyze → ogp → dist.x → dist.instagram → …
- **governance_cycle** (3 steps): gov.snapshot → gov.audit → gov.boundary
- **context_resume** (3 steps): ctx.memory → ctx.working → ctx.resume
- **health_check** (3 steps): caliber.health → caliber.recommend → caliber.lifecycle

## Architecture Boundary

このシステムは PlanningCaliber プロジェクトに属します。
MoCKA の forbidden_modules (SEO, Distribution, Publishing 等) は実装禁止。
`ARCHITECTURE_REGISTRY.json` (MoCKA root) で境界を定義。

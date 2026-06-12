# MoCKA 3.0 実装ロードマップ CHANGELOG

## Phase 1: 設計書 → 実装仕様書

- `docs/mocka3/implementation_spec.md` を作成
- `docs/mocka3/schemas/` 以下に `event.schema.json` / `commission.schema.json` /
  `ack.schema.json` / `state.schema.json` / `handshake.schema.json` を作成

## Phase 2: インターフェース固定

- `adapter/adapter_interface.py` — `AIAdapter` ABC
  (`handshake` / `receive_commission` / `execute` / `ack`)
- `knowledge_repository/repository_interface.py` — `KnowledgeRepository` ABC
  (`store` / `search` / `evolve`)
- `docs/mocka3/openapi.yaml` — API仕様定義

## Phase 3: コア実装

- `verification/verify_api.py` — Decision Ledgerのチェーン整合性を検証する
  薄いラッパー (`verify()`)
- `adapter/openai_adapter.py` — `AIAdapter` のOpenAI向けスケルトン実装 (`OpenAIAdapter`)
- `adapter/anthropic_adapter.py` — `AIAdapter` のAnthropic向けスケルトン実装
  (`AnthropicAdapter`)
- `phi_os_core.py` — `PHIOSCore`。ISE State Machine / Decision Ledger /
  Fluid Coordinate を束ねるセッションコア (`start` / `degrade` / `recover`)
- `app.py` に `/api/verification/verify` エンドポイントを追加
  (レスポンス形式: `{"ok": bool, "data": ..., "error": str|None}`)
- `verification/`, `adapter/`, `knowledge_repository/` を `__init__.py` 追加により
  正式なPythonパッケージ化
- `conftest.py` (phi-os直下) を追加し、`ise` / `verification` / `adapter` /
  `phi_os_core` を app.py と同じ絶対importパターンでテスト時に解決できるようにした

## Phase 4: 統合試験

- `ise/tests/test_integration_lifecycle.py` —
  正常系E2E: Event発生 → Decision Ledger更新 → Institution State更新
  → ISE knock相当(認証) → Adapter実行 → ACK → Verification → Seal相当
- `ise/tests/test_integration_incident.py` —
  異常系E2E: タイムアウト → Incident記録 → State DEGRADED遷移
  → Fluid Coordinate ΔZ低下 → Human Gate介入 → State ACTIVE復帰 → ΔZ回復記録
- `ise/tests/test_integration_components.py` —
  PHIOSCore / OpenAIAdapter / AnthropicAdapter / verify_api / FluidConnector の
  単体・組み合わせ試験
- pytest結果: **86 passed** (Phase 3完了時点では61件、Phase4で +25件)

## Phase 5: リファクタリング・モジュール境界レビュー

- **モジュール境界**: Institution Domain (`ise/`配下: state_machine,
  decision_ledger, revision_manager等) と AI Runtime Domain
  (`adapter/`, `phi_os_core.py`) の分離を確認。`phi_os_core.py`は両ドメインを
  繋ぐオーケストレーション層として位置づけ、ドメインロジックを持たない。
- **命名規則**: クラス=PascalCase (`PHIOSCore`, `OpenAIAdapter`,
  `AnthropicAdapter`, `AIAdapter`)、関数/メソッド=snake_case、
  状態名/Enum値=lower_snake_case (`ISEState`)。既存 `ise/` 配下と一貫。
- **APIレスポンス形式統一**: 新規エンドポイント `/api/verification/verify` は
  `{"ok": bool, "data": ..., "error": str|None}` 形式を採用。
  既存 `/api/ise/*` エンドポイントは独自形式 (`{"status": ...}` 等) のまま
  残置 — 既存テスト・フロントエンドへの破壊的変更を避けるため、
  統一は将来のリファクタリング項目として記録する。
- **テストカバレッジ**: `ise/tests/` 配下 86件すべてpass。
  Phase A〜E (61件) + Phase 4統合試験 (25件)。

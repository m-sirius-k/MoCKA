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

## Phase 2追加: PHI-OS core/registry分離・EventPipeline・Adapter v0・Ledger単一化・ExecutionGate

「Phase 2 実装チェックリスト『絶対に事故らない実装順』」(ref E20260612_103/104,
GPT条件「Boot Sequenceに最低保証モードを追加」) に基づく5ステップ実装。

- **命名上の変更点（重要）**: 指示書では新パッケージ名として `phi_os` が
  指定されていたが、phi-os直下には既に `phi_os.py`（`PHIOS`/`PHIOSError`を
  定義する既存単一ファイルモジュール、`test/test_phios_layer1〜4.py`が
  `from phi_os import PHIOS, PHIOSError`で依存）が存在する。
  同名の `phi_os/` パッケージディレクトリを作成すると、sys.pathの解決順序により
  既存の `phi_os.py` がシャドーイングされ、既存テスト4件がimportエラーで
  collectionエラーになることが判明したため、新パッケージ名を
  **`phios`（アンダースコアなし）** に変更した。内部参照
  (`from phi_os.xxx import` 等) もすべて `phios.xxx` に統一済み。

- **STEP1: core/registry分離**
  - `phios/registry/taxonomy.py` — Event Taxonomy v1.1への読み取り専用ラッパー
    (`get_taxonomy`, `is_valid_event`, `get_category`, `is_revision_update`等)。
    書き込みメソッドなし。
  - `phios/registry/rules.py` — `FORBIDDEN_OPERATIONS`,
    `ALLOWED_DECISION_CATEGORIES`, `BOOT_SEQUENCE` の静的定数定義。
  - `phios/boot.py` — `safe_boot(full: bool)`。
    `full=True`はフルゲート起動、`full=False`は最低保証モード
    (taxonomy + registryのみ保証) として動作。

- **STEP2: EventPipeline**
  - `phios/core/event_pipeline.py` — `EventPipeline`(シングルトン`pipeline`)。
    `emit()` が validate → enrich → persist → audit の単一経路を構成。
  - `ise/state_builder.py` の `emit_event()` は `pipeline.emit()` を
    呼び出すだけの薄い窓口に変更。

- **STEP3: Adapter v0**
  - `phios/adapter/mock_adapter.py` — `MockAdapter`（`AIAdapter`実装、
    safe_bootの最低保証として常時登録）。
  - `phios/adapter/openai_adapter.py` — `OpenAIAdapter` v0
    （実APIは呼ばない。`execute()`内で将来呼び出す拡張ポイントのみ）。
  - `phios/core/adapter_manager.py` — Adapterのプロセス内レジストリ
    (`register`/`get`/`list_adapters`/`reset`)。

- **STEP4: EventLedger単一ソース化**
  - `phios/ledger_gate.py` — `rebuild_state_from_ledger()`（Decision Ledgerから
    revisionを再計算）, `verify_ledger_is_source_of_truth()`
    （`decision_ledger.verify_chain()`の薄いラッパー）。
  - `decision_ledger`/`snapshot_manager`/`state_provider`（既存の読み取り専用
    レガシーDBアクセス）以外にDB直接書き込みが存在しないことをテストで確認。

- **STEP5: ExecutionGate**
  - `phios/core/execution_gate.py` — `gate_check()`（`verify_all.py`を
    MoCKAルートで`subprocess`実行し`ALL CHECKS PASSED`を確認）、
    `require_gate`デコレータ（ゲート失敗時に`RuntimeError`）。

- 新規テスト: `test_phi_os_separation.py`(6), `test_event_pipeline.py`(7),
  `test_adapter_v0.py`(7), `test_ledger_single_source.py`(4),
  `test_execution_gate.py`(4) — 計28件追加。
- pytest結果: **131 passed** (Phase 5完了時点103件 + 28件)。
- `safe_boot(full=True)` / `safe_boot(full=False)` ともに
  `[PHI-OS] Boot complete.` を出力して正常終了することを確認。
- `verify_all.py` 9ステップ ALL CHECKS PASSED を確認。
- registry層（`phios.registry.taxonomy`）には書き込みメソッドが存在せず、
  書き込み試行は不可能であることを確認。

## Phase 3 (v1.1): Meaning-driven Runtime — Meaning Registry / EventInterpreter / DecisionSynthesis / SemanticRouter / Executor / Orchestrator

「MoCKA 3.0 Phase 3 修正版指示書 v1.1」(ref E20260612_114/115, GPT指摘:
「意味をコードから分離しないとPhase 4で詰まる」) に基づく実装。
設計原則: `code = meaning executor`（実行するだけ）/ `meaning = registry / rules`（意味を定義する）。

- **STEP0**: `phios/registry/meaning.py`（intent/impact/urgencyのマッピング定義）、
  `phios/registry/decision_rules.py`（`DecisionRule`frozen dataclass + `DECISION_RULES`
  + `match_rule()`）。`ise/taxonomy_validator.py`に`get_severity()`を追加し、
  `phios/registry/taxonomy.py`から再公開。
- **STEP1**: `phios/core/event_interpreter.py` — `InterpretedEvent`が
  `meaning.py`の`get_intent`/`get_impact`/`get_urgency`を参照してmeaningを決定。
  `_classify_*`系の直書き分類ロジックは持たない。
- **STEP2**: `phios/core/decision_synthesis.py` — `DecisionSynthesizer.synthesize()`が
  `decision_rules.match_rule()`を参照してActionを決定。`if impact ==`/`if intent ==`の
  直書き分岐は持たない。
- **STEP3/3b**: `phios/core/semantic_router.py`（routing専念。destination決定のみ、
  Adapter実行・ack・gate_checkを呼ばない）と `phios/core/executor.py`
  （routing結果に基づく実際の実行・mock_fallback・エラーハンドリングを集約）に分離。
  human_gateルートには`gate_reason`/`gate_origin_event`を付与。
- **STEP4**: `phios/core/orchestrator.py` — Interpreter → Synthesizer → Router →
  Executorを束ねる`Orchestrator.process(event_type, raw)`。
- **STEP5**: `test_phase3_integration.py` — meaning-driven flow一式のE2E確認、
  critical eventのhuman_gateログ確認、meaning/decisionがコード直書きでないことの
  静的検証、Router/Executor分離の静的検証、taxonomy v1.1全イベント
  (37+)がInterpretedEvent生成可能であることの確認。

- 新規テスト: `test_meaning_registry.py`(10), `test_event_interpreter.py`(7),
  `test_decision_synthesis.py`(7), `test_semantic_router_v1.py`(7),
  `test_executor.py`(5), `test_orchestrator.py`(5),
  `test_phase3_integration.py`(6) — 計47件追加。
- pytest結果: **178 passed** (Phase 2完了時点131件 + 47件)。
- `verify_all.py` 9ステップ ALL CHECKS PASSED を確認。

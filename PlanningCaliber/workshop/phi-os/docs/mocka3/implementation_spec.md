# MoCKA 3.0 実装仕様書
# Phase 1: 設計書 → 実装仕様書
# 執筆: Claude / 2026-06-12
# 参照: MoCKA3_IMPLEMENTATION_ROADMAP.md / E20260612_074

本書は、企画書の全概念を実装へ写像し、「何がどのコードに対応するか」を確定するためのものである。
実在パスは2026-06-12時点で確認済み。未実装の概念は「設計済み」として記載する。

---

## 1-1 概念 → モジュール対応表（完全版）

| 企画書概念 | Pythonモジュール | パス | 状態 |
|-----------|----------------|------|------|
| Institution Contract | institution_contract.py | PlanningCaliber/workshop/phi-os/ise/ | ✅ 実装済み |
| Institution State | state_builder.py | PlanningCaliber/workshop/phi-os/ise/ | ✅ 実装済み |
| ISE | ise/ | PlanningCaliber/workshop/phi-os/ | ✅ Phase A〜E完了 |
| Decision Ledger | decision_ledger.py | PlanningCaliber/workshop/phi-os/ise/ | ✅ 実装済み |
| State Machine | state_machine.py | PlanningCaliber/workshop/phi-os/ise/ | ✅ 実装済み |
| Fluid Coordinate | fluid_connector.py | PlanningCaliber/workshop/phi-os/ise/ | ✅ 実装済み |
| Relay | relay/ | C:/Users/sirok/m-sirius-k/sirius-lab/ | ⚠️ 収益化未着手 |
| Memory | memory/ | C:/Users/sirok/m-sirius-k/sirius-lab/ | ⚠️ Free実装のみ |
| Verification | verification/ | PlanningCaliber/workshop/phi-os/ | ❌ 未実装 |
| Adapter | adapter/ | PlanningCaliber/workshop/phi-os/ | ❌ 未実装 |
| Knowledge Repository | knowledge_repository/ | PlanningCaliber/workshop/phi-os/ | ❌ 未実装 |
| Learning Engine | learning_engine/ | PlanningCaliber/workshop/phi-os/ | ❌ 未実装 |

---

## 1-2 API一覧（完全版）

既存エンドポイントに加え、未実装のAPIも「設計済み」として記載する。

| エンドポイント | メソッド | 担当モジュール | 状態 |
|--------------|---------|--------------|------|
| /api/ise/knock | POST | ise/sync_protocol.py | ✅ |
| /api/ise/ack | POST | ise/sync_protocol.py | ✅ |
| /api/ise/state | GET | ise/ | ✅ |
| /api/ise/status | GET | ise/ | ✅ |
| /api/ise/panel | GET | ise/ | ✅ |
| /api/ise/ledger | GET | decision_ledger.py | ✅ |
| /api/ise/state_machine | GET | state_machine.py | ✅ |
| /api/ise/ai_sessions | GET | ise/ai_session_state.py | ✅ |
| /api/handshake | POST | interface/handshake.py | ✅ |
| /api/adapter/{ai_id}/commission | POST | adapter/ | ❌ 設計済み |
| /api/adapter/{ai_id}/ack | POST | adapter/ | ❌ 設計済み |
| /api/verification/verify | POST | verification/ | ❌ 設計済み |
| /api/knowledge/search | POST | knowledge_repository/ | ❌ 設計済み |

---

## 1-3 JSON Schema定義

以下のスキーマを `docs/mocka3/schemas/` に定義する（本Phaseで新規作成）。

- `event.schema.json` — events.dbのイベント構造
- `commission.schema.json` — AIへの委任状
- `ack.schema.json` — AI応答構造
- `state.schema.json` — current_state.json構造
- `handshake.schema.json` — Handshake Protocol

各スキーマの詳細は同ディレクトリ内の各ファイルを参照。

---

## 1-4 Revision更新条件

current_state.jsonのrevisionが+1されるトリガーを以下に明文化する。

| トリガー | 更新量 | 理由 |
|---------|--------|------|
| knock受信 | +0（ドラフト） | 認証のみ、状態変化なし |
| ack受信（成功） | +1 | 実行完了 |
| state_transition | +1 | ISE状態変化 |
| incident検知 | +0（記録のみ） | 状態変化なし |
| seal実行 | +0（封印のみ） | revisionは不変 |

---

*implementation_spec.md / MoCKA 3.0 実装ロードマップ Phase 1 / Claude作成 / 2026-06-12*
*参照: MoCKA3_IMPLEMENTATION_ROADMAP.md / E20260612_074*

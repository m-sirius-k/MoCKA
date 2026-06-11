# PHI-OS Core Specification v1.0 — 追記事項

発行日: 2026-06-11
対象: Claude Code実装担当向け
種別: 差分追記（本文修正なし）
本体参照: X:\down\PHI-OS_Core_Spec_v1.0.docx

---

## 【修正①】9章 残作業 — 前提関係追加

TODO_195（実機テスト）は以下の順序で実施すること：

```
前提1: 新規登録「PHI-OS ingest() → mocka_write_event接続実装」完了
前提2: 新規登録「PHI-OS ⇄ vasAI 双方向ループ実装」完了
↓
TODO_195: PHI-OS v1.0 実機テスト（chrome://extensions）実施可能
```

実装順序を違反した場合はmocka_write_eventにVIOLATIONとして記録すること。

## 【修正②】5.2 vasAIループ — 終了条件追加

```
ループ終了条件:
  - vasAIからのfeedback.status == 'STABLE' の場合、再投入しない
  - 再投入回数が MAX_LOOP_COUNT（デフォルト: 3）を超えた場合、
    mocka_write_eventにLOOP_LIMIT_REACHEDとして記録し停止
  - mockaから HALT命令を受信した場合、即時停止

再投入後のview_type: 'fusion'固定
（再構成結果をvasAIに返す際は常にfusion viewを使用）
```

## 【改善③】4章 — node_id命名規則

```
命名規則: phi-os-{layer}-{product}-{instance}

例:
  phi-os-mocka-core-001       # mocka本体
  phi-os-vasai-core-001       # vasAI
  phi-os-mini-orchestra-001   # Orchestra
  phi-os-mini-relay-001       # Relay
  phi-os-mini-memory-001      # Memory

node_idはPHI-OS初期化時に設定し、変更不可。
mocka_write_eventのwhoフィールドに必ず使用する。
```

## 【改善④】1.2 — インスタンス数の明確化

```
インスタンス配置ルール:
  - mocka本体: 1インスタンス（phi-os-mocka-core-001）
  - vasAI: 1インスタンス（phi-os-vasai-core-001）
  - mini MoCKA製品: 製品ごとに1インスタンス
    （Orchestra / Relay / Memory それぞれ独立）
  - mini全体の統合観測: orchestratorインスタンスが担当
    （phi-os-mini-orchestrator-001）

インスタンス間の状態共有: FORBIDDEN（FORBIDDEN③に準拠）
インスタンス間の視点データ共有: mini orchestratorが集約して実施
```

## 【改善⑤】エラー記録仕様

```
エラー発生時の記録義務:

def _handle_error(self, error_type: str, context: dict):
    mocka_write_event(
        who=self.node_id,
        what='PHI_OS_ERROR',
        error_type=error_type,   # LOOP_LIMIT / DIRECTION_VIOLATION /
                                 # SYNC_FAIL / INGEST_FAIL
        context=context,
        severity='ERROR'
    )

assertによるvasAI方向違反の場合:
  error_type = 'DIRECTION_VIOLATION'
  処理は中断。呼び出し元に例外を返す。
```

## 【軽微⑥】8章 — バージョン管理方針

```
バージョン番号ルール:
  - パッチ (x.x.N): 軽微な追記・誤記修正
  - マイナー (x.N.0): API追加・原則追加
  - メジャー (N.0.0): FORBIDDEN変更・アーキテクチャ変更

本追記事項の適用後: v1.1.0
```

## 【軽微⑦】5.1 — 神の伝令 通信形式

```
通信方式: ポーリング型（PHI-OS側から定期取得）
取得間隔: 5分（essence_auto_updaterと同期）
形式: JSON
エンドポイント: localhost:5000/api/living-context
認証: HMAC（既存MoCKA認証に準拠）
受信後: ingest('mocka', payload) で即時処理
```

---

以上7点。
Claude Codeへの引き渡し時は本追記事項を
PHI-OS_Core_Spec_v1.0.docxと併せて渡すこと。
記録義務: 本追記事項の適用もmocka_write_eventに記録する。

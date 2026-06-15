# MoCKA Decision Ledger Schema v1

**Document ID**: DECISION_LEDGER_SCHEMA_v1
**Version**: 1.0.0
**Status**: Active
**Created**: 2026-06-15
**Depends On**: VERSION_POLICY_v1.md (v1.0.0), EVENT_FOUNDATION_v1.md (v1.0.1)

---

## 1. Purpose

Decision Ledgerは、MoCKAにおける全ての設計判断・変更承認・方針決定を制度として記録する監査台帳。

イベント基盤（Foundation/Lifecycle/Protocol）が「何が・どう変化したか」を管理するのに対し、Decision Ledgerは「なぜそう決定されたか」を記録し、設計継承性・監査性・再現性を保証する。

---

## 2. 位置付け（アーキテクチャ上の役割）

```
                VERSION_POLICY
                      │
                      ▼
    ┌────────────────────────────────┐
    │      DECISION_LEDGER_SCHEMA    │  ← 全仕様を横断する監査台帳
    └────────────────────────────────┘
          │              │              │
          ▼              ▼              ▼
EVENT_FOUNDATION  EVENT_DATA_LIFECYCLE  EVENT_TRANSITION_PROTOCOL
```

Decision Ledgerは各仕様に従属するのではなく、全仕様を横断して参照される共通基盤。

---

## 3. Decision レコードスキーマ

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| decision_id | string | ✅ | `DC_YYYYMMDD_NNN` 形式（例: DC_20260615_001） |
| title | string | ✅ | 決定事項の一行要約 |
| context | string | ✅ | 背景・前提・問題設定 |
| alternatives | array | ✅ | 検討した代替案（最低1件・却下理由も記載） |
| decision | string | ✅ | 採用した判断の明文 |
| rationale | string | ✅ | 採用理由（alternatives との比較を含む） |
| impact | string | ✅ | 影響範囲（対象ドキュメント・実装・運用） |
| related_events | array | - | 関連MoCKAイベントID（例: E20260615_048） |
| related_documents | array | - | 関連仕様書（例: EVENT_FOUNDATION_v1.md） |
| approved_by | string | ✅ | 承認者（きむら博士 / Claude / くろこ 等） |
| approved_at | string | ✅ | 承認日時（ISO8601） |
| supersedes | string | - | 本決定が置き換える旧Decision ID |
| superseded_by | string | - | 本決定を置き換えた新Decision ID |
| status | string | ✅ | Active / Superseded / Withdrawn |

---

## 4. decision_id 採番ルール

- 形式: `DC_YYYYMMDD_NNN`（NNNは当日連番・001始まり）
- 採番タイミング: approved_at 確定時
- 重複禁止・欠番可

---

## 5. alternatives フォーマット

```json
"alternatives": [
  {
    "option": "SQLiteに直接記録",
    "rejected_reason": "スキーマ変更時の移行コストが高い"
  },
  {
    "option": "JSONLファイルに記録",
    "rejected_reason": "検索性が低く監査に不向き"
  }
]
```

alternatives が1件もない場合は `"alternatives": [{"option": "N/A", "rejected_reason": "単一選択肢"}]` とする。

---

## 6. status 定義

| status | 意味 |
|--------|------|
| Active | 現行の意思決定として有効 |
| Superseded | より新しいDecisionに置き換えられた |
| Withdrawn | 撤回された（理由をrationale欄に記録） |

---

## 7. ストレージ

- v1実装: `C:\Users\sirok\MoCKA\data\decisions\decision_ledger.jsonl`（append-only）
- 形式: 1行1レコードのJSONL
- 不変条件: 既存レコードの上書き・削除禁止
- Superseded/Withdrawn の場合は新レコードを追記し、旧レコードの `superseded_by` を更新する

> ⚠️ Storage Mapping（実装依存）
> v1: JSONL / Future: SQLite / Parquet / Object Storage

---

## 8. MoCKAイベントとの連携

Decision を記録する際は必ず `mocka_write_event` も同時に実行する。

```
Decision作成 → decision_ledger.jsonl に APPEND
             → mocka_write_event（what_type: DECISION_MADE）
             → related_events に Event ID を記録
```

---

## 9. 監査クエリ（v1で答えられるべき問い）

- この設計判断はいつ・誰が承認したか？
- どの代替案が検討され、なぜ却下されたか？
- このDecisionは後継Decisionに置き換えられたか？
- 特定イベントに紐付く意思決定は何か？
- 特定仕様書に影響を与えたDecisionの一覧は？

---

## 10. 使用例

```json
{
  "decision_id": "DC_20260615_001",
  "title": "Decision Ledgerを全仕様横断の監査台帳として設計する",
  "context": "イベント基盤四層構造（Policy/Foundation/Lifecycle/Protocol）が完成し、設計判断の記録層が必要になった。",
  "alternatives": [
    {
      "option": "各仕様書内の変更履歴で代替",
      "rejected_reason": "横断検索・関連イベント参照が困難"
    },
    {
      "option": "EventのDECISION_MADEタイプのみで管理",
      "rejected_reason": "rationale・alternatives・supersedes関係の表現力が不足"
    }
  ],
  "decision": "Decision Ledgerを独立スキーマとして定義し、全仕様を横断する共通基盤とする",
  "rationale": "監査性・設計継承性・再現性を最大化するため、専用スキーマが必要。イベントとDecisionを1対多で関連付けることで将来の監査クエリに対応できる。",
  "impact": "docs/mocka3/全仕様・data/decisions/decision_ledger.jsonl新設・mocka_write_eventのwhat_typeにDECISION_MADE追加",
  "related_events": ["E20260615_052"],
  "related_documents": ["VERSION_POLICY_v1.md", "EVENT_FOUNDATION_v1.md", "EVENT_DATA_LIFECYCLE_v1.md", "EVENT_TRANSITION_PROTOCOL_v1.md"],
  "approved_by": "きむら博士",
  "approved_at": "2026-06-15T00:00:00Z",
  "supersedes": null,
  "superseded_by": null,
  "status": "Active"
}
```

---

## 11. 依存関係

```
VERSION_POLICY_v1.md → バージョン管理・Status管理ルールを適用
EVENT_FOUNDATION_v1.md → Invariants（append-only等）を継承
```

---

## 12. 変更履歴

| Version | Status | Date |
|---------|--------|------|
| 1.0.0 | Active | 2026-06-15 |

| バージョン | 日付 | 変更内容 |
|-----------|------|----------|
| 1.0.0 | 2026-06-15 | 初版作成 |

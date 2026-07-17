# semantic_vocabulary/concept (minimal implementation)

Provenance: DC_20260715_006 (C-1 採択) / DC_20260715_008 (6採択条件確定) /
design spec docs/internal/SEMANTIC_VOCABULARY_CONCEPT_RECORD_SCHEMA_DESIGN_v0.1.md

本ディレクトリは、採択済み最小 Concept Record Schema (C-1) の実体化 (materialization)
である。Human Gate (きむら博士) 承認による最小実装のみを含む。

含むもの:
- concept_record.schema.json : Concept Record の機械可読スキーマ (型定義のみ)。

含まないもの (意図的):
- concept 実データ / インスタンス (自動補完データ生成は禁止)。
- storage engine / DB / 永続化 (C-2 保留)。
- Validator (Option A 後続)。schema 内の一部不変条件 (exactly-one-active 等) は
  将来の Validator が強制する。
- relation graph (C-3 保留)。relation フィールドは非包含 (採択条件6)。
- API / MCP / migration / KN-004 接続。

境界:
- 本実装は設計どおりの encode のみ。設計変更・新規概念追加・未承認 schema 拡張は
  行っていない (additionalProperties:false)。
- 公開は未許可。本ファイル群は未 commit (untracked) で保持する。公開は別途
  Human Gate の Publication Boundary 判断を要する。
- Decision Ledger / design spec は本実装により変更していない。

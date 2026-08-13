# Category A Feasible Scope Audit v1.0

**作成日:** 2026-08-13  
**Event ID:** E20260813_60854181059cc  
**状態:** Phase 4 HOLD維持・独立進行可能領域抽出完了

## 概要

Phase 4 HOLDを維持しながら、HOLDを破らずに進行可能な領域（Category A）を抽出・体系化した監査報告書。

**目標：**
- HOLDを壊さない
- 商用化速度を落とさない
- Human Gate境界を守る
- MoCKAの価値提供を前進できる

## Phase 4 HOLD制約

### 禁止領域
- **Write Path変更**: Ledger, Event Store, Decision Ledgerへの直接書き込み
- **Evidence Path変更**: 検証・監査経路への介入
- **スキーマ変更**: 既存データ構造・型定義の修正
- **実装開始**: 改善候補の実装（設計検討のみ許可）

## Category A: 可能領域

### 1. 既存実装クリーンアップ

**GL7-UNENFORCED-CONDITIONS-BUG修正（完了）**
- 削除対象: FORBIDDEN_EXECUTIONS (8項), encoding_mismatch check, BINARY_EXTENSIONS定義
- 残存: 4つのアクティブなABORT_CONDITIONS
- Commit: da4d4db
- 参照: DC_20260705_009

**進行状況:** ✓ 完了

---

### 2. 改善候補の設計検討

| TODO ID | テーマ | 現状 | Category Aタスク |
|---------|--------|------|-----------------|
| `TODO_W1` | Relay provenance model統一 | 改善候補登録・HG Review待ち | 各ingestion pathの who_actor処理を分析・比較 |
| `TODO_W2` | Decision Ledger reverse traceability | 改善候補登録・HG Review待ち | 物理的 vs resolver/index設計検討 |
| `TODO_W4` | Search inheritance/continuity | 改善候補登録・HG Review待ち | 全文検索の意味的連続性・再現性設計検討 |

**制約:** 実装禁止・Decision Ledger entry禁止・スキーマ変更禁止

**進行状況:** ◎ 開始準備

---

### 3. Integrity違反の検出と記録

**許可操作:**
- events.dbの構造整合性確認（読み取り専用）
- Decision Ledger内の矛盾検出
- UTF-8エンコーディング確認
- mocka_write_event()での違反記録

**制約:** 修正実装禁止（Human Gate判定待ち）

**進行状況:** ◎ 開始準備

---

### 4. Phase 3C検証の補助

**TODO_451「検証履歴のcommit/seal/push + Genesis v1.1をRepair Branch保持」の完成支援**

- Durable Historyのcommit/seal/push確認
- Genesis Record v1.1 / Constitution v1.1の Repair Branch検証
- 禁止: genesis record seal / Ratification artifact freeze

**進行状況:** ◎ 開始準備

---

## 実行境界マトリックス

| 操作 | Phase 4 HOLD下 | 理由 | Category A許可 |
|------|--------------|------|----------------|
| Ledger/Event Store読み取り | 許可 | 検証・分析 | YES |
| Ledger/Event Store書き込み | 禁止 | Write Path変更 | NO |
| Decision Ledger読み取り | 許可 | 整合性検証 | YES |
| Decision Ledger新規entry | 禁止 | 設計決定未確定 | NO |
| スキーマ変更 | 禁止 | 既存データへの影響 | NO |
| 既存実装の除去（未使用コード） | 許可 | 純粋クリーンアップ | YES |
| 改善候補の実装開始 | 禁止 | HG判定前 | NO |
| 改善候補の設計検討 | 許可 | 情報収集・準備 | YES |
| Integrity違反の検出 | 許可 | 防御的モニタリング | YES |
| Integrity違反の自動修正 | 禁止 | HG判定待ち | NO |

---

## Category A実行計画

### Tier 1: 即進行可能（GL7-like）
- GL7未実装条件の除去（完了）
- 不参照の型定義・定数の洗い出し（進行中）

### Tier 2: 調査・分析（設計検討）
- TODO_W1分析: Relay paths比較・文書化
- TODO_W2設計検討: Reverse traceability アーキテクチャ評価
- TODO_W4設計検討: Search継続性・再現性設計

### Tier 3: 補助的検証
- TODO_451 Runtime verification補助
- 既存Integrity監査（読み取り専用）

---

## 制度的意味

Category Aの実行は、Phase 4 HOLDを維持しながら「MoCKAの価値提供」を前進させる戦略的操作です：

- **HOLDを壊さない**: Write Path/Evidence Path変更なし
- **商用化速度を落とさない**: 改善候補の設計を並行準備 → Just-in-time実装
- **Human Gate境界を守る**: 実装禁止・Decision Ledger entry禁止により博士の判定権を侵害しない
- **価値提供を前進**: クリーンアップ・分析・Integrity監視により制度の堅牢性向上

**沈黙禁止のコロラリ**: Integrity違反の検出・記録により、潜在的問題の可視化と事後的追跡可能性を確保。

---

## 参考情報

- **Event ID**: E20260813_60854181059cc
- **Commit**: da4d4db (GL7修正)
- **Branch**: claude/category-a-feasible-scope-0xnulq
- **参照**: Phase 4 HOLD（e-mail/memo）、DC_20260705_009、DC_20260812系

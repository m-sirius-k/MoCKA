# MoCKA Module Maturity Model v1

**Document ID**: MODULE_MATURITY_MODEL_v1
**Version**: 1.0.0
**Status**: Active
**Created**: 2026-06-15
**Depends On**: VERSION_POLICY_v1.md (v1.0.0), DECISION_LEDGER_SCHEMA_v1.md (v1.0.0), EVENT_FOUNDATION_v1.md (v1.0.1)

---

## 1. Purpose

MoCKA全モジュールの品質・運用・昇格基準を共通尺度で定義し、制度的一貫性・監査性・長期運用耐性を保証する横断規約。

イベント仕様（Foundation/Lifecycle/Protocol）とは独立し、全モジュール（製品・Caliber・OS層）に適用される。

---

## 2. Maturity Levels（成熟度定義）

| Level | 名称 | 状態 |
|-------|------|------|
| M0 | Concept | アイデア・設計構想段階 |
| M1 | Prototype | 動作確認・PoC段階 |
| M2 | Experimental | 開発中・不安定 |
| M3 | Stable | 安定運用・内部利用可 |
| M4 | Production | 商用利用・外部公開可 |
| M5 | Institutional | 制度基盤・長期保証・変更禁止原則 |

> M5はPHI-OS・Decision Ledger・EVENT_FOUNDATIONなど「制度そのもの」を構成するモジュールに付与する特別区分。
> M5モジュールへの変更はきむら博士の明示的承認とDecision Ledger登録を必須とする。

---

## 3. 評価軸（Dimensions）

成熟度は以下7軸の複合評価で決定する。

| 軸 | 説明 |
|----|------|
| Architecture | 設計の整合性・依存関係の明確さ |
| Tests | テストカバレッジ・自動化率 |
| Documentation | README・仕様書・使用例の充実度 |
| Auditability | mocka_write_event連携・イベント記録率 |
| Observability | ログ・ヘルスチェック・TIC連携状況 |
| Versioning | VERSION_POLICY適用・変更履歴の完全性 |
| Decision Traceability | Decision Ledger登録・設計判断の追跡可能性 |

---

## 4. Level別 必須条件

| 条件 | M1 | M2 | M3 | M4 | M5 |
|------|----|----|----|----|----|
| README整備 | - | ✅ | ✅ | ✅ | ✅ |
| mocka_write_event連携 | - | - | ✅ | ✅ | ✅ |
| VERSION_POLICY適用 | - | - | ✅ | ✅ | ✅ |
| Decision Ledger登録 | - | - | ✅ | ✅ | ✅ |
| テスト自動化（基本） | - | - | ✅ | ✅ | ✅ |
| TIC監視対象登録 | - | - | - | ✅ | ✅ |
| ヘルスチェック実装 | - | - | - | ✅ | ✅ |
| 外部公開ドキュメント整備 | - | - | - | ✅ | ✅ |
| きむら博士承認（変更時） | - | - | - | - | ✅ |
| Impact Assessment必須 | - | - | - | - | ✅ |

---

## 5. 昇格条件

### M0 → M1
- 設計概要ドキュメント存在
- 実装開始の意思決定（Decision Ledger登録）

### M1 → M2
- 基本動作確認済み
- README初版作成

### M2 → M3
- mocka_write_event連携完了
- VERSION_POLICY適用済み
- Decision Ledger登録済み
- 基本テスト自動化済み
- 重大バグなし（直近30日）

### M3 → M4
- TIC監視対象登録済み
- ヘルスチェック実装済み
- 外部公開ドキュメント整備済み
- Stripe等収益化基盤（製品の場合）

### M4 → M5
- きむら博士による明示的承認
- Decision Ledger登録（DC_YYYYMMDD_NNN）
- 全評価軸でM4条件を6ヶ月以上維持
- 後継モジュールまたは代替手段が存在（単一障害点でないこと）

---

## 6. 降格条件

| 状況 | 降格 |
|------|------|
| 重大障害（データ損失・セキュリティ侵害） | M4 → M3 |
| テスト自動化の崩壊 | M3 → M2 |
| イベント記録の断絶（7日以上） | M3 → M2 |
| 長期メンテナンス停止（90日以上） | 任意 → M2 |

降格時は必ず `mocka_write_event`（MODULE_MATURITY_CHANGED）を記録する。

---

## 7. MoCKAイベント連携

成熟度変更時は以下を必ず実行する：

```
成熟度変更 → mocka_write_event
  title: <モジュール名> M{N} → M{N+1}（または降格）
  what_type: MODULE_MATURITY_CHANGED
  why_purpose: 昇格/降格理由
→ Decision Ledger登録（DC_YYYYMMDD_NNN）
→ related_events に Event ID を記録
```

---

## 8. 現行モジュール成熟度一覧（v1.0.0時点）

| モジュール | Level | 根拠 |
|-----------|-------|------|
| Orchestra | M4 | 本番稼働・Stripe収益化・CWS公開 |
| Relay | M3 | 実装完了・収益化未着手 |
| Memory | M3 | Free実装完了 |
| PHI-OS | M3 | v1.0実装完了・実機テスト待ち |
| vasAI | M4 | v1.4.9 VERIFIED封印・GitHub公開 |
| EVENT_FOUNDATION | M5 | 制度基盤・不変条件定義 |
| DECISION_LEDGER_SCHEMA | M5 | 横断監査台帳・制度そのもの |
| TIC | M3 | Layer0〜1稼働・Layer2〜4未着手 |
| BEE | M3 | v2.0稼働・4 beta確認済み |
| COMMAND CENTER | M4 | 全サーバー統合・本番稼働 |

---

## 9. 依存関係

```
VERSION_POLICY_v1.md          → バージョン管理・Status管理ルールを適用
DECISION_LEDGER_SCHEMA_v1.md  → 昇格/降格の意思決定を記録
EVENT_FOUNDATION_v1.md        → append-only等のInvariantsを継承
```

---

## 10. 変更履歴

| Version | Status | Date |
|---------|--------|------|
| 1.0.0 | Active | 2026-06-15 |

| バージョン | 日付 | 変更内容 |
|-----------|------|----------|
| 1.0.0 | 2026-06-15 | 初版作成 |

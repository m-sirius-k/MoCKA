# GM2_REGISTRY_BASELINE_002

Registry Series ベースラインスナップショット v2

Artifact Type: Governance Document
Evidence Location: docs/governance/GM2_REGISTRY_BASELINE_002.md
固定日時: 2026-07-01
固定 commit: 10246ce43

---

## 概要

KN-001・KN-002・TERM-001 の 3 件がすべて Human Approval Gate（きむら博士）の承認を受けた時点のスナップショットである。
KN-003（Registry Record Specification）着手の起点として固定する。

---

## 承認済み成果物一覧

| ID | タイトル | commit | 承認状態 |
|---|---|---|---|
| KN-001 | REGISTRY_CHARTER_v1.0.md | 94d2155ab | 承認済み |
| KN-002 | CATEGORY_REGISTRY_v2.0.md | 80007bb7d | 承認済み |
| TERM-001 | TERM-001_REGISTRY_TERMINOLOGY.md (v1.1) | 10246ce43 | 承認済み |

---

## 確定した設計原則（この時点で固定）

1. Registry Neutrality Principle（存在中立原則）
   - Registry は対象の正当性・品質・価値を判断しない。存在を登録し、参照可能にすることのみを責務とする。

2. Index Model 採用
   - Record は Artifact の内容を複製・内包しない。Artifact への参照情報（Reference）を保持する。
   - Entity Model 不採用（Registry Neutrality Principle と整合しないため）。

3. Category / Series 構造
   - 6 カテゴリ固定（DP/GV/IA/OA/KN/KA）
   - Category 1:N Series
   - Maturity は Category/Series の属性（個別 Record の属性ではない）

4. 用語確定（12 用語）
   - Registry / Record / Entry（暫定：Record 同義語、KN-003 で再確認可）/ Artifact / Reference / Category / Series / Identifier / Status / Maturity / Source / Index

---

## KN-003 着手の前提条件（すべて満足済み）

- KN-001 承認済み: Registry の目的・責務・位置付けが確定
- KN-002 承認済み: Category/Series 体系が Registry 登録エントリとして整理済み
- TERM-001 承認済み: 用語集・設計原則・採用モデルが確定

---

## 未確定事項（KN-003 以降で扱う）

- Record の詳細フィールド定義（KN-003 の範囲）
- JSON Schema（KN-004 の範囲）
- Validator・整合性条件（KN-005 の範囲）
- Status の詳細な状態遷移（KN-006 の範囲）
- 実装計画（KN-007 の範囲）
- Source の正本確定（独立 TODO の範囲）
- Entry の暫定定義の確定（KN-003 で再確認）

---

## MCP記録について

本ベースライン固定時点で MoCKA MCP 接続が切断されていたため、mocka_write_event による event 記録は接続復旧後に補完する。
補完対象イベント: TERM-001 承認・GM2_REGISTRY_BASELINE_002 固定。

---

## 改訂履歴

- v1.0（2026-07-01）: KN-001/KN-002/TERM-001 全承認確認後に固定。くろこ作成。

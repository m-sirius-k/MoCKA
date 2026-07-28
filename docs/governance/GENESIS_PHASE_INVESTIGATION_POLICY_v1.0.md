# Genesis Phase調査 統合方針 v1.0

Decision ID: DC_20260728_006
承認: きむら博士
記録日: 2026-07-28
記録者: 執行官Claude（くろこ）
文書種別: Governance Policy（正本）

---

## 1. Decision

MOCKA_ORIGIN.md は新規Timeline文書へ分離しない。
Genesis Phase調査の一次資料として扱う。

---

## 2. 文書責務

### MOCKA_ORIGIN.md

- 役割: 創始者意図の保存
- 記録対象: 創始者の問題意識 / 開発動機 / 哲学 / 宣言 / Vision
- 分類: Founder Narrative

### Genesis Phase調査（Genesis Phase Investigation）

- 役割: 開発過程の歴史的再構成
- 記録対象: 実装履歴 / 試行錯誤 / 採用判断 / 未採用案 / 方向転換 / 時系列
- 分類: Historical Reconstruction

---

## 3. Classification Rule

Origin文書・Genesis資料ともに、文書単位ではなくStatement単位で評価する。

| Classification | 意味 |
|---|---|
| Confirmed | 証拠により確認済み |
| Source | 根拠資料 |
| Founder Narrative | 創始者本人の意図・認識 |
| Hypothesis | 解釈・仮説 |
| Unknown | 未確認 |
| Rejected | 否定済み |

---

## 4. 禁止事項

以下を避ける。

- Origin文書から現在の構造を逆算して一本道の歴史を生成しないこと。
  - 例: （OriginにPHI-OS思想が存在した）ではなく、（Originの記述とPHI-OS設計には概念的対応が確認できる）と記述する。
- 後知恵による因果接続をConfirmed扱いしないこと。
  - 例: Origin -> MoCKA -> EBGA -> PHI-OS という流れは、（現在から見た体系的整理）であり、（当時存在した開発経路）とは分離する。
- Unknownを埋めないこと。
  - 不明な期間・判断・転換点は、Unknownとして保持する。

---

## 5. 最終的な構造

```
MoCKA History
+-- MOCKA_ORIGIN.md
|       `-- Founder Narrative
|
`-- Genesis Phase Investigation
        +-- Evidence
        +-- Timeline
        +-- Decisions
        +-- Unknown
        `-- Interpretation Boundary
```

Genesis Phase Investigationのスケルトンは docs/governance/GENESIS_PHASE_INVESTIGATION_v0.1.md に初期化済み（本方針制定時点では実データはUnknown起点）。

---

## 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2026-07-28 | 1.0 | 初版。DC_20260728_006として決定・記録。 |

# PlanningCaliber 憲法 v1.0（完全版）

**制定日**: 2026-06-17  
**制定者**: きむら博士  
**執行官**: くろこ（Claude Code）  
**イベントID**: E20260617_017  
**前法**: PLANNING_CALIBER_LAW_v1.md  
**効力**: 即日発効・全モジュール適用・恒久効力

---

## 第1章（目的）

PlanningCaliberはMoCKAにおける唯一の  
**「実験統制・評価・昇格制度」** である。

PlanningCaliberが存在する理由はただ一つ：  
> **「残るものを選別する」**

生成ではなく選別。  
作ることではなく、残ることを許可すること。

---

## 第2章（構造原則）

本システムは以下の**4層構造**を持つ。

```
┌─────────────────────────────────────────┐
│  workshop    │ 生成・実験  │ 唯一の実装空間       │
│  Caliber     │ 評価・監査  │ 統制機構（非生成）    │
│  candidates  │ 採用候補    │ 評価通過・統合検討中  │
│  specs       │ 採用確定    │ 本体準拠・変更再審必要│
└─────────────────────────────────────────┘
```

各層は**一方向にのみ**進む。  
candidates → workshop への逆行は「再実験命令」としてのみ発動する。

---

## 第3章（絶対原則）

以下は**いかなる理由があっても禁止**される：

| 禁止番号 | 禁止事項 | 違反した場合 |
|---|---|---|
| 禁止1 | workshopを経由しない本体生成 | 即時削除対象 |
| 禁止2 | Caliber未評価の仕様採用 | 採用無効・再評価義務 |
| 禁止3 | candidates/specsを経由しない統合 | 本体汚染として記録 |
| 禁止4 | AI Gate単体での外部実行設計 | workshop送り返し |
| 禁止5 | logsなし・DESIGNなしの実験着手 | Caliber受理拒否 |

---

## 第4章（唯一の昇格経路）

すべての成果物は**以下の経路のみ**を通る：

```
workshop（実験）
    ↓  CaliberScore算出
Caliber（評価）
    ↓  0.65以上の場合のみ通過
candidates（選別・採用検討）
    ↓  0.85以上 + 博士承認
specs（確定仕様）
    ↓  安定運用確認後
MoCKA本体（統合）
```

**スキップは存在しない。**  
緊急でも例外でも、この経路を通る。

---

## 第5章（評価義務）

すべての成果物はCaliberによる**数値評価**を受ける。

評価は `caliber/caliber_score.py` で実行する。  
スコアなき成果物は「存在しないもの」として扱う。

評価軸・スコア計算・判定ルールは  
`caliber/SCORING_SPEC_v1.md` に定義する。

---

## 第6章（フィードバック義務）

評価結果・外部展開結果・失敗記録はすべて  
**PlanningCaliberへ帰還する義務**を持つ。

帰還形式：
- 成功 → `mocka_write_event(tags="caliber_pass")` で記録
- 失敗 → `mocka_write_event(tags="caliber_fail")` で記録
- 外部展開結果 → PR-OS `feedback_publish()` → PlanningCaliber

帰還なき実験は「完了していない」とみなす。

---

## 各システムの憲法的役割（固定・変更不可）

### MoCKA（意味中枢）
意味の源泉。PlanningCaliberはMoCKAの制度腕である。

### AI Gate
- 位置：workshop内部エンジン
- 役割：意味変換・構造生成・品質スコアリング
- 制約：Caliber評価前の外部接続禁止

### SEO-EG（SEO-CENTER）
- 位置：PlanningCaliber配下（PR-OS内）
- 役割：認識構造生成・検索最適化
- 制約：workshop実験を経た成果物のみ処理可

### PR-OS
- 位置：PlanningCaliber配下
- 役割：配信・投稿・外部展開
- 制約：specs昇格済みコンテンツのみ配信

### Caliber
- 位置：PlanningCaliber内部監査部門
- 役割：評価・採用判定・改善指示・強制再設計命令
- 制約：生成行為禁止。評価のみ。

---

## 設計思想（根本一文・改訂不可）

> **「本体は作るものではなく、評価されて残ったものだけが本体になる」**

---

## 全体最終構造

```
MoCKA（意味中枢）
   │
PlanningCaliber（制度・統制）
   │
   ├── workshop/           実験空間
   │     └── <project>/
   │           ├── core/
   │           ├── experiment/
   │           ├── logs/
   │           ├── output/
   │           ├── config/
   │           ├── tests/
   │           └── DESIGN.md
   │
   ├── caliber/            評価エンジン
   │     ├── caliber_score.py
   │     └── SCORING_SPEC_v1.md
   │
   ├── candidates/         採用候補（Caliber通過済み）
   ├── specs/              確定仕様（本体準拠）
   │
   ├── AI Gate             生成エンジン（workshop内）
   ├── SEO-EG              認識設計（PR-OS内）
   └── PR-OS               配信実行
          ↓
   現実フィードバック → PlanningCaliberへ帰還
```

---

## くろこ憲法遵守宣誓（執行官行動規範）

くろこは以下を誓約する：

1. すべての設計提案の冒頭で「この憲法に適合するか」を問う
2. workshop外への実装提案を行わない
3. CaliberScore なしの specs 昇格を提案しない
4. 実験結果は必ず `mocka_write_event` で帰還記録する
5. 緊急・例外を理由とした禁止事項の迂回を行わない

---

## 改正手続き

この憲法の改正には以下が必要：

1. きむら博士による明示的な改正指示
2. MoCKAイベントへの記録（`tags=constitution_amendment`）
3. バージョン番号更新（v1.0 → v1.1 等）

---

*PlanningCaliber 憲法 v1.0 / 制定 2026-06-17 / イベントID: E20260617_017*

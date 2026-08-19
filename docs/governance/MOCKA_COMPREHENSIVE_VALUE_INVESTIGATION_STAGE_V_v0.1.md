# MoCKA Comprehensive Value Investigation - Stage V
# 前回調査の回復と価値モデル構築

**Status**: Investigation Phase Recovery
**Date**: 2026-08-19
**Prior Stage**: Stage IV (Phase 2 Closure / Governance Finalization)
**Target**: IFRS-style Comprehensive Value Model

---

## PHASE 1: 過去探索結果の回収 

### 1.1 確認済みリポジトリマップ（MOCKA_OVERVIEW.json v4.1より抽出）

#### Heart System（心臓部）
| リポジトリ | Path | Role | Status |
|---|---|---|---|
| MoCKA | C:/Users/sirok/MoCKA | 制度核・心臓部 | active_main |
| mocka-civilization | - | 設計思想・青写真層 | phase9-29 |
| mocka-transparency | - | 改ざん検知・署名検証 | - |
| mocka-external-brain | - | AIオーケストラ神経系・合議バス | share->ask->reply->decide |

#### Institution & Governance（制度・統治層）
| リポジトリ | Role | Status |
|---|---|---|
| mocka-core-private | 実装実験・検証環境 | 凍結中 |
| mocka-knowledge-gate | 制度的記憶層 | - |
| mocka-outfield | 外野・公開ネットワーク層 | - |
| mocka-public | 公開ドキュメント・証明層 | - |
| mocka-docs | ドキュメント群 | - |

#### Products（製品展開）
| 製品 | Status | Type |
|---|---|---|
| Orchestra | 本番稼働中 | Revenue Stream |
| Relay | 実装完了・収益化保留 | Product |
| PHI-OS | v1.0実機テスト完了 | Runtime Layer |
| vasAI | v1.4.9 VERIFIED封印済み | Governance System |
| PR-OS | コード全完成・WordPress credentials設定待ち | Product |
| Memory | Free実装完了 | Feature |

#### Technical Assets（技術資産）
| Asset | Type | Status |
|---|---|---|
| Event Ledger | Persistence | SQLite統一化完了（11929件） |
| Decision Ledger | Governance | 承認待ち（TODO_361） |
| MCP Server | API | localhost:5002稼働 |
| COMMAND CENTER | Dashboard | v6.1稼働 |
| Caliber Pipeline | Processing | localhost:5679稼働 |

---

## PHASE 2: Repository間関係整理

### 2.1 時系列的な拡散・収束パターン

**フェーズ1（初期設計）**: mocka-civilization / mocka-external-brain / mocka-transparency 
→ 理論基盤の構築

**フェーズ2（統治層整備）**: mocka-knowledge-gate / mocka-core-private / mocka-public
→ 制度化・公開化

**フェーズ3（製品化）**: Orchestra / Relay / PHI-OS / vasAI / PR-OS
→ 商用展開

**フェーズ4（統合）**: MoCKA心臓部への吸収/統合予定
→ 単一Event Store化（2026-06-16完了）

### 2.2 機能吸収マッピング

後発の製品・システムが、先行リポジトリの機能を統合・再実装した痕跡：

- **mocka-external-brain** (Decision Layer/合議Bus) 
  → Orchestra / Relay の判定ロジックへ
  
- **mocka-transparency** (改ざん検知)  
  → PHI-OS Event Gate / 単一書き込み経路確立へ
  
- **mocka-knowledge-gate** (制度的記憶)
  → MoCKA Event Ledger / Decision Ledger へ統合進行中

---

## PHASE 3: 各資産の出生・変化・吸収先確認

### 3.1 Event Store の進化系統

1. **出生**: events.csv (2026-04-05まで使用)
2. **変化**: SQLite events.db へ移行（2026-06-16完了）
3. **吸収先**: PHI-OS Event Gate（単一書き込み経路）/ 各製品の判定ロジック

### 3.2 Decision / Governance の進化

1. **出生**: mocka-external-brain (AI合議プロトコル share/ask/reply/decide)
2. **変化**: Decision Ledger Schema v1 設計開始（TODO_305系）
3. **未完**: Decision Ledger ↔ Event Store の接続（TODO_361待ち）

### 3.3 Institutional Memory の進化

1. **出生**: mocka-knowledge-gate
2. **変化**: MoCKA_TODO.json / MOCKA_OVERVIEW.json 中心に移行
3. **現状**: 複数記録系統並存（Decision Ledger / Event Store / TODO.json）

---

## PHASE 4: 価値カテゴリ分類（IFRS的視点）

### 4.1 技術資産（Technical Assets）

**定義**: 実行時に価値を生成するコード・API・システムコンポーネント

- **Event Store** (events.db)
  - 出生元: events.csv
  - 累積価値: 20,679 events (2026-08-19現在)
  - 吸収価値: PHI-OSへの単一経路統一
  
- **Decision Engine** (external-brain/orchestra/relay)
  - 出生元: mocka-external-brain (AI合議)
  - 累積価値: 245 decisions / 10段階意思決定ロジック
  - 吸収価値: 複数製品の自動判定ロジック
  
- **MCP Server** (localhost:5002)
  - 出生元: mocka_mcp_server.py
  - 累積価値: 27+ tools / ngrok経由クラウドアクセス
  - 吸収価値: 外部AIとのtool-use integration

### 4.2 知識資産（Knowledge Assets）

**定義**: 設計思想・原則・理論基盤

- **Civilization Loop** (8段階ループ理論)
  - 出生元: mocka-civilization (phase9-29)
  - 累積価値: Observation→Record→Incident→Recurrence→Prevention→Decision→Action→Audit
  - 吸収価値: MoCKA制度の根本原則 + AIES 2026論文

- **Governance Constitution** 
  - 出生元: CONSTITUTION.md / INSTITUTION_ARCHITECTURE.md
  - 累積価値: 310+件のガバナンス文書体系
  - 吸収価値: 各製品の信頼性保証

- **Connector Framework** (AI能力登録・ルーティング)
  - 出生元: Distribution Router v2
  - 累積価値: Semantic Score Vector / Multi-AI orchestration
  - 吸収価値: ChatGPT/Gemini/Claude/Perplexity統治制度

### 4.3 記憶資産（Memory Assets）

**定義**: 過去のイベント・判断・経緯の記録

- **Event Ledger** (events.db + decision_ledger.jsonl)
  - 出生元: events.csv (開始時期未記録)
  - 累積価値: 20,679 events + 245 decisions
  - 吸収価値: 全製品・全人間ゲート判定の履歴追跡

- **TODO System** (MOCKA_TODO_ACTIVE.json)
  - 出生元: 2026-05-11前後より本格化
  - 累積価値: 48未着手 + 427完了 + 14保留 + 14廃止 = 503件
  - 吸収価値: 進行状況追跡・優先度管理

- **MOCKA_OVERVIEW.json**
  - 出生元: 2026-03-28（session_history記載）
  - 累積価値: v4.1 (meta欄seal更新・本文v4.0相当)
  - 吸収価値: マスターファイル＝全context一行での提示

### 4.4 制度資産（Institutional Assets）

**定義**: 判定・承認・検証のプロセス・ルール

- **Human Gate System**
  - 出生元: Phase C Governance Gate実装 (2026-06-01)
  - 累積価値: 複数段階の判定ゲート / Authority Boundary確立
  - 吸収価値: AI/人間の責任分離・信頼の証

- **Audit Structure** (TIC Layer0-4 + BEE v2.0)
  - 出生元: Phase 4移行(2026-06-01)
  - 累積価値: health_check + tech_watcher + sandbox(TODO_205) + impact_analyzer(TODO_206) + UI(TODO_207)
  - 吸収価値: 外部技術変化への4層防衛

- **Integrity Classification** (IC_20260705_018 後続)
  - 出生元: 2026-07-05 MCP Tool Registry Drift対応
  - 累積価値: MCP schema hash検知 / Runtime Divergence分類
  - 吸収価値: AI内部状態の監視・信頼性保証

### 4.5 継承資産（Succession Assets）

**定義**: 後発システムへの吸収・移植・継承されたもの

- **Governance Constitution** → Orchestra/Relay/PHI-OSへ
- **Decision Protocol** → vasAI/PR-OS へ
- **Event Store** → 全製品の判定根拠DB
- **TIC Layer** → SEO-OS/PR-OS外部監視

---

## PHASE 5: IFRS的包括価値モデルへの変換（設計中）

### 5.1 資産区分表（Financial Accounting Style）

| カテゴリ | 出生元 | 現在価値指標 | 吸収先 | 評価状態 |
|---|---|---|---|---|
| Technical | Events.csv→DB | 20,679件 | 全製品 | Measured |
| Technical | MCP Server | 27+ tools | External AI | Active |
| Knowledge | mocka-civilization | 8段階理論 | AIES論文+制度 | Published |
| Knowledge | Governor Docs | 310+ docs | 全制度 | Catalogued |
| Memory | Event Ledger | 20,679 events | Audit trail | Sealed |
| Memory | TODO System | 503 items | Priority queue | Current |
| Memory | OVERVIEW | v4.1 | Master context | Living |
| Institutional | Human Gate | Phase C+ | Approval layer | Enforced |
| Institutional | TIC Layer | Layer0-4 | External guard | Partial(TODO_207待ち) |
| Succession | Constitution | Multiple | Products | Absorbed |

### 5.2 累積価値命題（Comprehensive Value Proposition）

**MoCKA は単なるAI制度ではなく、以下の5層構造による累積価値を形成している：**

1. **Layer 1 - Technical Substrate**
   - 20,679 events の監査証跡 / 27+ MCP tools の能力registry
   - 価値: 完全な実行履歴追跡 → Trustworthiness Proof

2. **Layer 2 - Knowledge Foundation**
   - 8段階civilization loop理論 / 310+件governance文書体系
   - 価値: 設計の正当性・再現性 → Reproducibility Guarantee

3. **Layer 3 - Memory Infrastructure**
   - 20,679 events + 245 decisions + 503 TODOs の統合記憶
   - 価値: 集団学習・改善ループ → Continuous Improvement

4. **Layer 4 - Institutional Controls**
   - Human Gate / TIC Layer / Integrity Classification
   - 価値: 自律実行の信頼性限界設定 → Safety Boundary

5. **Layer 5 - Product Succession**
   - Orchestra/Relay/PHI-OS/vasAI/PR-OS への制度吸収
   - 価値: 単一企業を超えた知識継承 → Institutional Immortality

### 5.3 IFRS型評価フレームワーク（仮案）

MoCKAの包括価値を、国際財務報告基準のように「一貫した基準」で定量化する試案：

```
MoCKA Comprehensive Value Statement = 

  ∑[Technical Assets] (Event Store Scale + Tool Count)
  + ∑[Knowledge Assets] (Theory Completeness + Documentation Coverage)
  + ∑[Memory Assets] (Event Density + Decision Traceability)
  + ∑[Institutional Assets] (Gate Coverage + Audit Effectiveness)
  + ∑[Succession Assets] (Product Absorption Rate + Knowledge Transfer Success)
  
  = Trustworthiness Index × Reproducibility Index × Autonomy Safety Index
```

---

## 次フェーズ（PHASE 6以降）

1. **PHASE 6**: 各資産のメトリクス定義（数値化基準の確定）
2. **PHASE 7**: 過去12ヶ月の時系列追跡（価値増減の可視化）
3. **PHASE 8**: 複数AIシステムとの比較分析
4. **PHASE 9**: 論文・公開ドキュメント化
5. **PHASE 10**: 制度への逆還元（Artifact昇格）


# MoCKA Comprehensive Value Ledger v0.1
# 価値認識基準・資産台帳

**Status**: Framework Definition Phase
**Date**: 2026-08-19
**Purpose**: IFRSスタイルの資産認識・分類・評価の基盤構築

---

## 資産認識の基本構造

### MoCKA型資産認識プロセス

従来型(Repository→File→Code→Function)ではなく：

```
Origin（発生源）
  ↓
Problem（課題認識）
  ↓
Creation（創造）
  ↓
Evolution（進化）
  ↓
Integration（統合）
  ↓
Inheritance（継承）
  ↓
Current Role（現在役割）
```

---

## 5価値分類の定義

### A. 技術価値（Technical Value）

**対象**: 実行・自動化・相互運用を可能にする資産

- Event Store (events.db)
- MCP Server & Tools
- Runtime Engines
- API Endpoints
- Automation Infrastructure

**評価観点**:
- 実行可能性: 動作するか / 止まっていないか
- 再利用性: 他システムで使用可能か
- 拡張性: 機能追加・修正が容易か
- 継続性: メンテナンス負荷は持続可能か

**メトリクス候補**:
- 稼働時間率
- Tool実行回数 / 月
- API呼び出し成功率
- 拡張ポイント数

---

### B. 知識価値（Knowledge Value）

**対象**: 思想・原則・理論・設計基盤

- Constitution (8条憲章)
- Civilization Loop Theory
- Governance Principles
- Evidence Supremacy Doctrine
- Authority Model
- Decision Philosophy

**評価観点**:
- 独自性: MoCKA固有の考え方か
- 一貫性: 全体で矛盾していないか
- 他領域適用可能性: 他分野でも使えるか
- 引用度: どれだけ参照されているか

**メトリクス候補**:
- Constitution引用文書数
- Governance文書総数 (310+件)
- 論文発表数 / ピアレビュー
- 学位論文・研究引用

---

### C. 記憶価値（Memory Value）

**MoCKA独自領域。過去の意思決定・実行経緯を保持する資産**

- Event Ledger (20,679 events)
- Decision Ledger (245 decisions)
- TODO History (503 items)
- MOCKA_OVERVIEW.json (v4.1 / マスターコンテキスト)
- Incident Records
- Seal History

**評価観点**:
- 再現性: 過去の状態を復元できるか
- 判断経緯保持: なぜその決定をしたか分かるか
- 時系列復元能力: いつどの段階だったか追跡可能か
- 監査可能性: 第三者が検証できるか

**メトリクス候補**:
- Event密度 (events/month)
- Decision追跡率 (決定の根拠記録率)
- TODO→Decision完了率
- Seal更新間隔 (信頼性証明)

---

### D. 制度価値（Institutional Value）

**対象**: 判定・承認・検証・統制のプロセス・ルール

- Human Gate System (判定・承認レイヤ)
- HAB (Human Authority Boundary)
- TIC Layer (4層防衛)
- Decision Immutability (書き込み後不変性)
- Integrity Classification
- Governance Gate
- Module Certification

**評価観点**:
- 責任境界: 誰が判定するか明確か
- 監査可能性: 判定過程が検証可能か
- 統制能力: 問題発生時に対応できるか
- スケーラビリティ: 規模拡大時に耐えるか

**メトリクス候補**:
- Gate通過率 / 却下率
- Authority Boundary侵犯事例ゼロ達成期間
- 監査指摘対応率
- インシデント検知時間

---

### E. 継承価値（Succession Value）

**IFRS比較の中心。「現在どこにあるか」ではなく「何へ変換され残ったか」**

**パターン1: リポジトリ層での継承**
- mocka-civilization (理論) → MoCKA core constitution化
- mocka-external-brain (合議) → Orchestra/Relay decision engine化
- mocka-transparency (改ざん検知) → PHI-OS event gate化
- mocka-knowledge-gate (記憶) → Event Ledger/Decision Ledger化

**パターン2: 機能層での継承**
- Relay (Free版AI要約) → Memory (Free実装完了)へ
- vasAI (統治実証) → MoCKA constitutional base へ
- PHI-OS (Runtime Layer) → 全製品の信頼性基盤へ

**パターン3: 試作→修復→本装備化**
- 初期試作機能
  ↓修復（バグ取り・最適化）
  ↓別システムへ吸収
  ↓現在の制度要素として機能

**評価観点**:
- 吸収度: どれだけ他システムに統合されたか
- 知識転移成功度: 理論が実装に反映されたか
- 継承の完全性: 元のシステムは廃止可能か
- 後発産物への寄与度: 製品品質向上への貢献

**メトリクス候補**:
- 吸収されたRepository数
- 継承された主要概念の実装カバー率
- 派生製品数 / リポジトリ
- 製品機能のMoCKA Constitutional引用率

---

## Value Ledger フォーマット

### 行単位（各資産ごと）

| 項目 | 内容 | 記入例 |
|---|---|---|
| **Asset ID** | 資産識別子 | EVT-001 / DEC-002 / REP-003等 |
| **Asset Name** | 資産名称 | Event Ledger / Decision Engine等 |
| **Value Class** | 5分類 | Technical / Knowledge / Memory / Institutional / Succession |
| **Origin** | 発生源 | events.csv / mocka-external-brain / RFC/提案 |
| **Origin Date** | 発生時期 | 2026-04-05 / 2026-05-11等 |
| **Problem** | 課題認識 | 何が必要だったか | CSV形式のログ化では不十分→DB化必要 |
| **Creation** | 創造プロセス | 誰が・いつ・どう作ったか | Python + SQLite / claude実装 / 2026-06-16 |
| **Repository** | 所在・移動履歴 | data/events.db(現) / 元: events.csv |
| **Transformation** | 変化・進化 | v1→v2→...の変更 | CSV→SQLite / 11,929件→20,679件 |
| **Integration** | 統合・吸収先 | 複数システムでの再利用 | PHI-OS Event Gate / 各製品の判定ロジック |
| **Inheritance** | 後発への継承 | 何が継承されたか | Decision Logic → Orchestra/Relay |
| **Current Role** | 現在の役割 | 今何を担当しているか | 全製品の監査証跡・根拠DB |
| **Evidence** | 根拠 | どこで確認できるか | commit hash / 文書 / events.db record |
| **Status** | 現在状態 | Active / Frozen / Evolving等 |
| **Maintainer** | 保守主体 | 誰が責任を持つか |
| **Last Review** | 最終確認日 | 2026-08-19 |
| **Notes** | 備考 | - |

---

## 記入例（3件）

### 例1: Event Ledger（技術価値）

| 項目 | 内容 |
|---|---|
| Asset ID | EVT-001 |
| Asset Name | Event Ledger |
| Value Class | Technical + Memory |
| Origin | events.csv (2026-04 | 前後開始) |
| Problem | イベント履歴をログファイルで管理→検索・集計困難 |
| Creation | Python SQLite / claude実装 / 2026-06-16 |
| Repository | data/events.db (現) ← events.csv (廃止) |
| Transformation | CSV形式→SQLite / 11,929件→20,679件 (8月現在) |
| Integration | PHI-OS Event Gate (単一書き込み経路確立) |
| Inheritance | 全製品の判定ロジック / 監査根拠DB |
| Current Role | MoCKAの執行履歴保持・監査証跡・再現性保証 |
| Evidence | commit 571351a95 / PHI-OS event_gate.py / CHANGE_DONE記録 |
| Status | Active / Growing |
| Maintainer | MoCKA core team |
| Last Review | 2026-08-19 |

---

### 例2: Decision Engine（技術価値 + 制度価値）

| 項目 | 内容 |
|---|---|
| Asset ID | DEC-002 |
| Asset Name | Decision Engine |
| Value Class | Technical + Institutional |
| Origin | mocka-external-brain (AI合議プロトコル) |
| Problem | 単一AIの判定→複数AI合議による信頼性向上必要 |
| Creation | Python / share/ask/reply/decide プロトコル設計 / 2026-05 |
| Repository | mocka-external-brain (原本) / MoCKA core統合進行中 |
| Transformation | 合議バス→Decision Policy化 / 分散→集約 |
| Integration | Orchestra decision logic / Relay判定ロジック / vasAI governance core |
| Inheritance | 複数製品の自動判定基盤 / Human Gate承認前段 |
| Current Role | 全システムの意思決定エンジン・責任分離 |
| Evidence | mocka-external-brain/share_ask_reply_decide.py / Decision Ledger (245 decisions) |
| Status | Evolving (Decision Ledger接続待ち TODO_361) |
| Maintainer | MoCKA governance team |
| Last Review | 2026-08-19 |

---

### 例3: Constitution（知識価値 + 制度価値）

| 項目 | 内容 |
|---|---|
| Asset ID | KNW-003 |
| Asset Name | MoCKA Constitution |
| Value Class | Knowledge + Institutional |
| Origin | MOCKA_CHARTER_v2.md / 8条憲章 |
| Problem | AIの自律実行→信頼性・責任性の枠組み必要 |
| Creation | くろこ理論化 / 2026-03 前後 / 文書化2026-06 |
| Repository | docs/governance/MOCKA_CHARTER_v2.md + CONSTITUTION.md |
| Transformation | 初版→v2.0(承認済み) / 310+件ガバナンス文書体系へ展開 |
| Integration | 全製品・全制度の基盤原則 / AIES 2026論文 |
| Inheritance | Philosophy→Implementation / Theory→Operation |
| Current Role | MoCKAの根本原則・判定基準・信頼性保証根拠 |
| Evidence | MOCKA_CHARTER_v2.md (承認済み) / 310+ガバナンス文書の引用 / AIES Submission282 |
| Status | Established / Active |
| Maintainer | きむら博士 / MoCKA governance team |
| Last Review | 2026-08-19 |

---

## Ledger作成の次フェーズ

### PHASE 6-B: 11リポジトリの完全マッピング

**対象リポジトリ**:

| # | Repository | Value Class | 現在状態 | 優先度 |
|---|---|---|---|---|
| 1 | MoCKA (core) | ALL | active_main | Critical |
| 2 | mocka-civilization | Knowledge | phase9-29 | High |
| 3 | mocka-external-brain | Technical + Institutional | Active Development | High |
| 4 | mocka-transparency | Technical + Institutional | Active Development | High |
| 5 | mocka-knowledge-gate | Memory | Active Development | High |
| 6 | mocka-core-private | Technical | Frozen | Medium |
| 7 | mocka-public | Knowledge | - | Medium |
| 8 | mocka-outfield | Succession | - | Low |
| 9 | mocka-docs | Knowledge | - | Medium |
| 10 | planningcaliber | Technical | workshop稼働 | High |
| 11 | vasAI | Institutional | v1.4.9 VERIFIED | Medium |

### PHASE 6-C: 価値時系列トレース

2026-03-28 (OVERVIEW.json v1作成) から 2026-08-19 (現在) までの

**各価値クラスの成長曲線** をプロット

### PHASE 6-D: メトリクス定量化

各Value Classごとに

**実測可能な指標** を確定

---

## 次のアクション（博士へ）

1. **Value Ledgerの行数**
   - 全資産数: 3セクタ（リポジトリ/製品/技術資産）×複数階層
   - 見積: 50～100行規模

2. **5価値分類の妥当性確認**
   - A(技術) - B(知識) - C(記憶) - D(制度) - E(継承)
   - 他の分類が必要か？

3. **優先度指示**
   - 11リポジトリ全体のLedger作成 vs. コア資産のみ先行
   - 時間軸: 2週間で完成可能か？

4. **最終形式の指示**
   - Markdown vs. JSON vs. SQLite DB vs. 複合形式


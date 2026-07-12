# Position of MoCKA within International AI Governance — 技術仕様書 v1.0

**文書種別:** 技術仕様書（主張文書ではない）。正本設計: `POSITION_CHAPTER_INTEGRATION_DESIGN_v0.1.md`。

**状態管理凡例（本仕様書全体で使用）:**
- **検証済み** — 本セッションまたは先行監査で直接証拠を確認済み
- **設計済み** — 設計文書・原則文書として存在するが、運用実証の証拠は未確認
- **部分検証** — 一部の側面のみ証拠確認済み、残部は未確認
- **未検証** — 証拠確認を実施していない、または実施したが結論に至らなかった
- **無効** — 証拠確認の結果、主張されていた内容が実装として存在しないことが確定した
- **判断待ち** — 事実関係は確認済みだが、解釈・是非の判断が人間（きむら博士）に委ねられている

**参照関係（重複説明を避けるための参照先）:** 個別評価の詳細は`MoCKA_vs_NIST_AIRMF_TACIP_GAP_ANALYSIS_v1.0.md`、証拠一覧は`MOCKA_EVIDENCE_MATRIX_v1.0.md`、検証債務の事実確認は`VERIFICATION_DEBT_PHASE1_CLOSURE_REPORT_v1.0.md`、MoCKAの制度思想全般は`MOCKA_INTERNATIONAL_AI_GOVERNANCE_POSITION_PAPER_v1.0.md`（Reference、変更禁止）を参照。本仕様書はこれらの内容を再説明せず、位置づけの確定にのみ焦点を当てる。

---

## 1. Purpose

**本章の目的:** 監査結果（Audit Report群、8文書）に基づき、MoCKA 1.0の国際AIガバナンス上の位置づけを、主張ではなく証拠経路として確定する。

**適用範囲:** *NIST AI RMF Profile on Trustworthy AI in Critical Infrastructure, Community of Interest Discussion Draft, Jul 7, 2026*（ステータス: "NOT OFFICIAL GUIDANCE, FOR DISCUSSION ONLY"）との比較評価結果に限定する。ISO/IEC標準・EU AI Act等の他の国際的枠組みとの比較は実施しておらず、本仕様書の適用範囲外とする。

**対象評価基準:** `MoCKA_vs_NIST_AIRMF_TACIP_GAP_ANALYSIS_v1.0.md`の12分類（Governance/Accountability/Risk Management/Human Oversight/Transparency/Explainability/Traceability/Verification-Validation/Documentation/Monitoring/Incident Management/Knowledge Management）、NIST全53Task、4段階評価（NONE/PARTIAL/ACHIEVED/ADVANCED）。

---

## 2. System Position

### 2.1 位置づけの一次分類

MoCKAはAI支援作業を対象とした制度的ガバナンスシステムであり、Critical Infrastructure運用者ではない。物理OT/ICS資産（バルブ・PLC・SCADA・医療機器等）を保有・操作しない。この一次分類は**検証済み**（`MoCKA_vs_NIST_AIRMF_TACIP_GAP_ANALYSIS_v1.0.md` §1のドメイン不一致に基づくNONE判定、12分類中1分類がこれに該当）。

### 2.2 既存Frameworkとの差分

NIST TACIPは「AIが物理インフラを操作する」文脈を前提とする。MoCKAは「AIが組織自身の統治プロセス（意思決定・変更管理・記録）に参加する」文脈で発展した。この差分は**検証済み**であり、比較が直接成立するのは両文脈が重なる評価軸（Accountability・Explainability決定レベル・Traceability・Incident Management）に限定される。

### 2.3 評価分布（状態としての提示）

| 状態 | 分類数 | 該当分類 |
|---|---|---|
| 検証済み（ACHIEVED以上） | 4 | Accountability／Explainability（決定レベル）／Traceability／Incident Management |
| 部分検証（PARTIAL） | 7 | Governance／Risk Management／Human Oversight／Transparency／Verification-Validation／Documentation／Monitoring／Knowledge Management |
| 対象外（NONE） | 1 | Explainability（モデルレベル） |

出典: `MoCKA_vs_NIST_AIRMF_TACIP_GAP_ANALYSIS_v1.0.md` §3全項目、§4、§5。全評価とも4項目（NIST要求・MoCKA対応・証拠・差分）を伴う個別記録があり、本仕様書ではこの分布を再集計するのみで個別評価の再説明は行わない。

---

## 3. Evidence Boundary

### 3.1 評価済み証拠（本仕様書が依拠する一次証拠のカテゴリ）

| カテゴリ | 証拠源 | 状態 |
|---|---|---|
| Decision Ledger個別レコード | `mocka_decision_get`による直接取得（DC_20260711_002/001、DC_20260710_005/004、DC_20260708_007/006/001、DC_20260707_002/003、DC_20260705_008/009/002 等） | 検証済み（本セッション直接取得） |
| Decision Ledger全体件数 | `mocka_decision_list`応答内`"count": 56` | 検証済み |
| Integrity Classification Ledger | `mocka_integrity_list`、全31件 | 検証済み（本セッション全件読了） |
| Event Ledger規模 | `mocka_get_overview().current_view.recent_events.count`（15,412件時点） | 検証済み |
| router.py実装状態 | `ast.parse`によるPython構文解析、文字列検索 | 検証済み（無効の確定に使用） |
| AUDIT_STANDARD系文書（3監査サイクル実績） | `AUDIT_STANDARD_PHASE1_FACT_COLLECTION_v0.1.md`等、検証エージェントによる内容読了 | 検証済み |
| TRDP原則 | `cross_audit.py`内定義、`caliber/stress/`配下のexam問題群 | 部分検証（原則定義は検証済み、恒常運用の実測は未検証） |
| Shadow Movement原則 | `docs/architecture/SHADOW_MOVEMENT_PRINCIPLE.md` | 部分検証（原則文書は検証済み、75%数値の運用実証は未検証） |

### 3.2 未評価領域

| 領域 | 状態 | 理由 |
|---|---|---|
| mocka-transparencyリポジトリ内容 | 未検証 | 存在確認のみ、内容未読（`MOCKA_EVIDENCE_MATRIX_v1.0.md`と同型の限界） |
| リスク閾値事前定義framework | 未検証 | Integrity Ledgerは事後分類が中心、事前閾値設計文書の有無を確認できていない |
| mocka-knowledge-gateリポジトリの一部（PROJECT_501/MRS-001） | 判断待ち | E-001、push経緯の事実確認がきむら博士の判断待ち |
| ADVANCED評価（Incident Management）の証拠境界 | 未検証 | 本仕様書§5.2で条件付き表現に留める理由 |

### 3.3 証拠IDとの対応（Position判断に直接使用したもの）

| 証拠ID | 用途 | 状態 |
|---|---|---|
| IC_20260708_004 | Human Gate執行ギャップの根拠（§2.3 Governance/Human Oversight PARTIAL判定） | 検証済み・Open（未解決） |
| IC_20260707_005 | Transparency/Monitoring評価における表示層信頼性の留保根拠 | 検証済み・Open（未解決） |
| E-001（`VERIFICATION_DEBT_PHASE1_CLOSURE_REPORT_v1.0.md`） | Knowledge Management評価の否定的証拠 | 判断待ち |
| E-004（同上） | Verification/Validation評価の否定的証拠（calc_drift_v3不在） | 無効確定 |
| E-003（同上） | Traceability評価における留保（supersede双方向反映欠落） | 検証済み（欠陥として確定） |

---

## 4. Verification Architecture

MoCKAの検証・記録機構は単一の仕組みではなく、役割分担された複数レイヤーで構成される。以下は各レイヤーの**役割**と**現在の状態**の一覧であり、各レイヤーの内部構造の詳細説明は`MOCKA_BEYOND_NIST_ANALYSIS_v1.0.md`を参照（本仕様書では再説明しない）。

| レイヤー | 役割 | 状態 | 根拠 |
|---|---|---|---|
| **Transparency Layer**（mocka-transparency） | 改ざん検知・署名検証 | 未検証 | 存在確認のみ、内容未読 |
| **Knowledge Gate** | 知識の継承・検索窓口 | 部分検証 | 名称が2つの無関係な実体（`search_knowledge_gate()`関数／独立repo）を指す衝突を検証済み。独立repo自体は409コミットの資産を持つが2026年4-6月に約4ヶ月休眠、CI無効化を検証済み |
| **Institutional Memory**（essenceパイプライン・MOCKA_OVERVIEW.json） | セッション間の知識継承（記憶を持たないAIセッションへの再ブリーフィング） | 検証済み | `MOCKA_OVERVIEW.json`の`meta.staleness_note`が自己の陳腐化を自己申告する機構を持つことを含め検証済み |
| **Shadow Verification**（Shadow Movement） | 主系統の独立検証経路・縮退運用（約75%機能維持の設計原則） | 設計済み | `SHADOW_MOVEMENT_PRINCIPLE.md`により原則は検証済み。75%という具体数値の運用実証（ドリル記録・テスト結果）は未検証のまま |
| **TRDP**（Trust but Record, Detect, Penalize） | 複数AI間の役割分担・多重監査プロトコル、単独AIの独断防止 | 設計済み | `cross_audit.py`定義・`caliber/stress/`のストレステスト問題群（例: 「TRDPの役割分担に不満がある場合...」等のSocratic型設問）により原則の存在は検証済み。恒常的な多重監査としての継続執行実績は未検証 |
| **Decision Ledger**（参考: Accountability/Traceability評価の主要根拠） | 意思決定の記録・再構成 | 検証済み | §3.1参照。supersede双方向反映のみ既知の欠陥（E-003） |
| **Integrity Classification Ledger**（参考: Incident Management評価の主要根拠） | 制度的インシデントの検知・分類・解決追跡 | 検証済み | §3.1参照 |

**構造上の観察（証拠に基づく事実、主張ではない）:** 7レイヤー中、「検証済み」はInstitutional Memory・Decision Ledger・Integrity Classification Ledgerの3件のみである。Transparency Layerは未検証、Knowledge Gate・Shadow Verification・TRDPは部分検証または設計済み（原則は存在するが運用実証が不足）に留まる。これは検証アーキテクチャ全体が均質に成熟しているわけではないことを示す。

---

## 5. Unique Contribution

証拠で確認できる貢献のみを記載する。

### 5.1 証拠確認済みの貢献

- **Traceability（検証済み）**: Decision Ledgerの相互参照（`related_events`/`related_documents`）を実際に辿り、単なるログ保存を超えた意思決定再構成が可能であることを実地確認した（`VERIFICATION_DEBT_PHASE1_CLOSURE_REPORT_v1.0.md` §1のDC_20260708_003追跡例）。
- **Accountability（検証済み）**: 全確認対象Decision Ledgerレコードに`approved_by`フィールドが例外なく存在することを確認した。
- **Explainability・決定レベル（検証済み）**: Decision Ledgerの`alternatives`/`rationale`フィールドが、却下案とその却下理由を意思決定時点で記録する構造を持つことを確認した。これはNIST Practice 8.1.2が問題視する事後統計的説明（SHAP/LIME型）とは異なる、一次的な理由記録である。

### 5.2 ADVANCED判定候補（条件付き表現）

**Incident Management** について、`MoCKA_vs_NIST_AIRMF_TACIP_GAP_ANALYSIS_v1.0.md` §3.11はADVANCEDと判定したが、本仕様書ではR01審査の指摘（§3.3「証拠境界確認」が未実施であること）を踏まえ、以下の条件付き表現とする。

> Integrity Classification Ledgerの運用実績（31件、検知手法・解決経緯まで記録された継続的制度）は**検証済み**である。この実績がNIST Discussion Draft Practice 8.1の対応するImplementation群（大部分が`(TBD)`のまま）と比較して先行していることも**検証済み**である。しかし、この比較優位が「NIST側が単に未記述であるために生じているのか」「MoCKA側の制度が成熟しているために生じているのか」を分離する証拠境界確認は**未検証**である。したがって本仕様書では「ADVANCED」ではなく **「ADVANCED (within evaluated scope: NIST側実装記述が現時点でTBDである範囲内での比較優位)」** と表現し、絶対的な国際基準超越の主張とはしない。

**Knowledge Management** について、思想・設計（essenceパイプラインによる知識継承）とKnowledge Gateという具体的実装を分離して評価する。

> 継承制度としての思想は**設計済み・一部運用実績あり**（Institutional Memoryの検証済み部分）であり、ADVANCED候補となりうる水準にある。一方、「Knowledge Gate」という名称を冠する具体的実装は、名称衝突・長期休眠・E-001（判断待ち）という3つの未解決事項により**部分検証**に留まる。したがって「思想: ADVANCED候補」「実証: PARTIAL」の二層分離を維持し、統合した単一評価は行わない。

---

## 6. Limitations and Future Validation

### 6.1 未検証事項（優先順位順）

1. **E-001（判断待ち）**: PROJECT_501/MRS-001のcommit `ecab6c0`が「commit/push禁止」の明示記述に反して公開リモートへpush済みである事実は検証済みだが、経緯・許諾の有無はきむら博士の判断待ち。
2. **§5.2 ADVANCED証拠境界（未検証）**: NIST側TBDによる相対的優位か、MoCKA側の絶対的成熟かの分離。
3. **Transparency Layer内容（未検証）**: mocka-transparencyリポジトリの内容未読。
4. **TRDP・Shadow Verificationの運用実証（部分検証）**: 原則文書は存在するが、恒常運用としての実測データが不足。
5. **リスク閾値事前定義framework有無（未検証）**。

### 6.2 今後必要な検証

- E-001の事実確認をきむら博士に依頼し、`VERIFICATION_DEBT_PHASE1_CLOSURE_REPORT_v1.0.md`のE-001ステータスを確定させること
- ADVANCED証拠境界確認を独立した検証タスクとして実施し、§5.2の表現を本文確定後に再評価すること
- mocka-transparencyリポジトリの内容検証を、Knowledge Gate検証と同様の方式で実施すること
- Shadow Movement・TRDPの運用実証（ドリル記録・多重監査ログ等）の有無を確認すること
- 上記が完了した時点で、本仕様書のv1.1改訂を検討する（既存v1.0は改変せず、新バージョンとして作成する）

---

## 参照関係一覧

| 参照先 | 関係 |
|---|---|
| `POSITION_CHAPTER_INTEGRATION_DESIGN_v0.1.md` | 正本設計（本仕様書はこれに基づき作成） |
| `MOCKA_INTERNATIONAL_AI_GOVERNANCE_POSITION_PAPER_v1.0.md` | Reference（変更禁止、思想的基盤として参照のみ） |
| `MoCKA_vs_NIST_AIRMF_TACIP_GAP_ANALYSIS_v1.0.md` | 評価データの一次ソース（本仕様書は再集計・再構成のみ行う） |
| `VERIFICATION_DEBT_PHASE1_CLOSURE_REPORT_v1.0.md` | E-001〜E-004の事実確認結果の一次ソース |
| `MOCKA_EVIDENCE_MATRIX_v1.0.md` | 証拠カテゴリ分類の一次ソース |
| `MOCKA_BEYOND_NIST_ANALYSIS_v1.0.md` | Verification Architecture各レイヤーの詳細説明（本仕様書では再説明しない） |

## 制約の遵守について

既存文書（`MOCKA_INTERNATIONAL_AI_GOVERNANCE_POSITION_PAPER_v1.0.md`含む全既存成果物）は一切変更していない。Git commit/pushは行っていない。全記述に状態タグ（検証済み/設計済み/部分検証/未検証/無効/判断待ち）を付与し、「できる」という能力主張ではなく状態管理として記述した。既存文書との重複説明を避け、参照関係を明示した。

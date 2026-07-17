# Observation Constitutional Map v0.1

Status: OBSERVATION / EVIDENCE MAP / NON-CANONICAL
Date: 2026-07-14
作成: くろこ(Claude Code)
基礎資料: R-04 Observation Constitutional Cross-System Validation

## 0. 本文書の位置づけ(最重要)

- 本文書は、MoCKA内に分散存在するObservation関連構成物の責務・境界・関係性を
  「地図」として可視化する証拠整理資料である。
- 本文書は制度整理・証拠整理のみを目的とする。統合設計・実装変更・権限変更・
  制度決定は一切行わない。
- Recommendation / Decision / Architecture Mutation を含まない。R-04で発見された
  未整理(曖昧点)は、解消せず、そのまま保存する(Ambiguity Preserved)。
- 実行モード: READ ONLY。本文書の作成以外に、Code Modification / Schema Change /
  Decision Ledger Write / Event Write / Commit / Merge は行っていない。
- 「単一制度か/複数Layerとして維持するか/Ex-Auditをどの境界に配置するか」の判断は、
  本地図を入力とするHuman Gate判断領域であり、本文書では判断しない。

補足(証拠境界): R-04で参照指定された基礎資料 R-03 Observation Architecture
Evidence Book / Observation Constitutional Position Paper は、MoCKAの一次データ
(events / knowledge_gate)の検索では未検出であった。本地図のEvidenceは、
event ledgerのレコードおよびリポジトリ内の一次ファイル(file:line)に基づく。
この未収載自体はSection 3 Issue 7として保存する。

---

## Section 1. Observation Inventory

### 1.1 一覧(Observation Component | Source | Role | Evidence)

| Observation Component | Source | Role | Evidence |
|---|---|---|---|
| A6 O0 (Observation Layer) | docs/experimental/meta/a6_observation_layer_o0_v1.md | A6本体(L0-L3)非破壊の観測レイヤ。観測のみ、介入なし | 同ファイル:8-13, 13行「観測のみ、修正・介入は一切行わない」 |
| Phase8-4 Observation Surface | docs/contracts/phase8_4_observation_surface_v1.md | 分断された意味空間を観測可能にするだけの層。表示のみ | 同ファイル:0章「理解できないまま見えるUI」, 20-22行 |
| Phase10-4 Operational Observation Layer | docs/contracts/phase10_4_operational_observation_layer_v1.md | 観測系の挙動をログ化。差分発生の事実記録 | 同ファイル:4章「Observation = 差分発生の事実記録」 |
| META_OBSERVATION_LOG | docs/governance/META_OBSERVATION_LOG_v0.1.md | 4監査で共通観測されたパターンの事実記録 | 同ファイル:5行「発見されるが制度的に解消される仕組みがない」 |
| AUDIT OBSERVATION_LAYER | docs/governance/MOCKA_AUDIT_INSTRUCTION_v1.0_OBSERVATION_LAYER_v0.1.md | 監査指示書3.1-3.4の構造的事実をfile:line根拠付き報告 | 同ファイル:3行「くろこの役割は観測・事実収集のみ」 |

補足(R-04スコープ外で発見された観測名称ファイル、参考記載のみ):

| Observation-named file | Source | Role | Evidence |
|---|---|---|---|
| MCP Scope Separation Observation | docs/governance/MOCKA_MCP_SCOPE_SEPARATION_OBSERVATION_v0.1.md | MCP transport 4層のobservation-mode監査 | 同ファイル:3行「推測・設計・改善提案は含めない」 |
| R02 Observation Candidates | docs/governance/TODO_437_R02_OBSERVATION_CANDIDATES_v0.1.md | 未検証Evidence Candidateの抽出整理 | 同ファイル:14行「Human Gate承認後まで行わない」 |

### 1.2 構成物詳細(Name/Source/Purpose/Responsibility/Input/Output/Authority/Boundary/Evidence/Status)

#### Governance Loop

- Name: Governance Loop (mocka_Movement / 主統治ループ)
- Source: docs/architecture/COGNITIVE_GOVERNANCE_LAYER_v1.md (event E20260615_111 / E20260615_112)
- Purpose: 観測系(Step1-3)から判断生成系(Step4)への移行を定義する自己更新ループ
- Responsibility: G1 Intent Synthesis / G2 Intent Prioritization / G3 Conflict Resolution /
  G4 Direction Projection
- Input: source_intent_set, drift_context, constraint_result
- Output: decision_graph / synthesized_intents / conflict_resolution_map / future_projection_vector
- Authority: アーキテクチャ層定義(設計)。制度(Institution)としての独立宣言は未確認
- Boundary: constraint_resultによりARCHITECTURE P4(Layer3はLayer1経由のみ実行反映)へ接続。
  実装(mocka_mcp_server.py等)とは別レコード
- Evidence: E20260615_111/112, README.md(mocka_Movement = primary governance loop)
- Status: Evidence Found(アーキテクチャ層として)。制度独立宣言は Ambiguous
- Observationとの関係: Governance Loopの自己更新ループ(Intent生成 -> Constraint評価 ->
  Execution -> Drift観測 -> Decision再生成)の中に「Drift観測」が構成要素として内在する。
  観測がGovernance Loop内部に既に含まれている点が、Observationを独立化した場合の境界論点となる

#### PHL

- Name: PHL (ping_hook_lever / 複数AI整流層)
- Source: PHL論文(Zenodo DOI), lever_essence.json, PHL-OS(EPHL_ schema),
  Phase H1 PHL Responsibility Definition (event E20260621_9708876874349)
- Purpose: 複数AI整流層の意味レイヤ責務を、実装前に確定する
- Responsibility (H1責務定義, 実装ゼロ):
  - H1-1 Actor: actor_id(必須、登録 != 信頼付与、外部AI自己生成不可) / actor_type / actor_name。
    Binding Rule: author = 観測値(既存・継続), actor_id = 制度上の識別子(新規)。両者は一致しない場合がある
  - H1-2 Trace(Responsibility Trace Layer): actor_id / author / trace_link。
    責任評価を行わない、関係の記録のみ
  - H1-3 Propagation(Actor Propagation Layer): 既存フロー
    (Event -> WorkingContext -> Snapshot -> MemoryContext)への意味付け層。新規伝播経路は追加しない
  - H1-4 Trust(Trust Boundary): 信頼 = 行為評価ではなく、システムに対する観測可能性の制御。
    TraceとTrustは独立する
- Input: actor情報, 既存データフロー
- Output: 責務定義(意味レイヤ)。実装成果物は未発行
- Authority: 意味レイヤ設計のみ確定。H2(PHL制度設計)・H3(PHL実装)は将来工程として未着手
- Boundary: H1は実装ゼロを明示宣言。Trust Gateway/Ed25519署名等の実装は未採用・設計保留
- Evidence: E20260621_9708876874349 (DECISION_RECORD: Phase H1 完了)
- Status: Evidence Found(責務定義層まで)。H2 制度設計は未着手 = Ambiguous
- Observationとの接点: H1-1 Binding Rule の「author = 観測値」は、Observation(観測値)が
  PHL Actor定義の一構成に接続していることを示す。ただしObservation制度とPHL制度の
  境界の明示的宣言は一次資料に未確認

#### A6 O0 (Observation Layer)

- Name: A6 Observation Layer (O0)
- Source: docs/experimental/meta/a6_observation_layer_o0_v1.md
- Purpose: A6本体(L0-L3)を一切変更せず、seal後構造の時間安定性検証・WARN挙動観測・
  逸脱/再現性/自然消滅の判定のみを行う
- Responsibility: 観測のみ。修正・介入は一切行わない(非干渉原則)
- Input: A6-v2 seal states, WARN 2件(a6_v2_consistency_test_v1.md記載)
- Output: WARN_LOG / STABILITY_LOG / DEVIATION_ALERT
- Authority: NON-CANONICAL。正式governanceではない。docs/governance/配下を上書き・置換しない
- Boundary: A6構造修正・verified再定義・レイヤ再番号付け・Trigger Wiring(A7)接触を行わない
- Evidence: 同ファイル:3行(NON-CANONICAL), 8-13行(非破壊/非干渉)
- Status: EXPERIMENTAL / META / NON-CANONICAL

#### Phase8-4 Observation Surface

- Name: Observation Surface Contract v1
- Source: docs/contracts/phase8_4_observation_surface_v1.md
- Purpose: 分断された意味空間(trace_id空間とcluster_id空間)を観測可能にするだけの層
- Responsibility: 表示 / 分離可視化 / 状態そのまま出す。解釈 / 比較 / 統合 / 正規化はしない
- Input: trace_view / cluster_view / collision_view / ruling_view の既存reader/store/record
- Output: 4チャネルのread-only snapshot(派生データ・集計・要約・スコア化の生成禁止)
- Authority: DRAFT。統合・差分・正規化は恒久的に禁止
- Boundary: 4チャネルは互いに参照しない。Phase8-2の非統合保証を壊さない
- Evidence: 同ファイル:0章(役割定義), 24-35行(View Channels完全分離)
- Status: DRAFT

#### Phase10-4 Operational Observation Layer

- Name: Operational Observation Layer(宣言のみ)
- Source: docs/contracts/phase10_4_operational_observation_layer_v1.md
- Purpose: 観測系(Signal/Reasoning/Drift Monitor/tech_watcher/Essence pipeline/Advisor)の
  動作挙動をログ化する。意味ではなく差分の蓄積
- Responsibility: Observation = 差分発生の事実記録。評価・解釈・状態変化の記述はしない
- Input: 観測系各要素の挙動
- Output: 最小ログ(event_id / target / drift_type / before...), 3種Drift限定
  (Structure Drift / Semantic Drift / Operational Drift)
- Authority: 宣言のみ。実装・拡張・設計深化を含まない
- Boundary: Phase10-3(FROZEN, WP_PHASE10_3_BASELINE)を基点とし不変・干渉なし。再定義禁止
- Evidence: 同ファイル:4章(観測の定義固定), 6章(評価禁止)
- Status: 宣言のみ(DRAFT)

#### META_OBSERVATION_LOG

- Name: Meta Observation Log v0.1
- Source: docs/governance/META_OBSERVATION_LOG_v0.1.md
- Purpose: 4件の独立監査(Vocabulary Audit / Cross Reference Audit / CI Failure /
  Governance Catalog KN-004重複)で共通観測されたパターンを事実としてのみ記録
- Responsibility: 事実の横断並記のみ。改善案・解決策・設計案は一切含めない
- Input: 上記4監査の該当箇所(file:line)
- Output: 共通パターン記録「発見されるが制度的に解消される仕組みがない」
- Authority: Phase B-6提出物に含めない。将来のPhase A v2設計時の入力として保持
- Boundary: 「共通パターンである」という記述が唯一の統合的判断。それを超える原因分析をしない
- Evidence: 同ファイル:3-5行, 33行
- Status: v0.1(記録)

#### AUDIT OBSERVATION_LAYER

- Name: MoCKA Audit Instruction v1.0 - Observation Layer v0.1
- Source: docs/governance/MOCKA_AUDIT_INSTRUCTION_v1.0_OBSERVATION_LAYER_v0.1.md
- Purpose: 監査指示書v1.0の重点監査項目3.1-3.4について、構造的事実をfile:line根拠付きで報告
- Responsibility: 観測・事実収集のみ。判断・評価・改善提案は一切行わない
- Input: 3.1制度ループ構造 / 3.2スキーマ不一致 / 3.3未定義責務領域 / 3.4障害再発条件
- Output: file:line根拠付きの構造的事実
- Authority: 指示書4.x(構造評価/分類/制度欠陥/強化提案)はくろこ担当範囲外。
  R01・博士のPhase 2以降の領域
- Boundary: 実行レイヤー(Governance Catalog Phase B-6)とは別の観測レイヤー
- Evidence: 同ファイル:1-5行
- Status: v0.1(観測レイヤーのみ)

### 1.3 構造的事実(Observationの二義性、事実記載のみ)

一次資料の観察上、MoCKA内で「Observation」は少なくとも2つの異なる意味で使われている。
本項は事実の記載であり、統合・優劣の判断は行わない。

- (a) 名前を持つ観測レイヤ/サーフェス: A6 O0 / Phase8-4 Observation Surface /
  Phase10-4 Operational Observation Layer。いずれも別Phase・別文書で独立に定義されている
- (b) 監査に適用される観測モード/役割: AUDIT OBSERVATION_LAYER / META_OBSERVATION_LOG /
  (スコープ外)MCP Scope Separation Observation / R02 Observation Candidates。
  いずれも「観測・事実収集のみ、判断しない」という役割として運用されている

---

## Section 2. Responsibility Boundary Map

各層の責務を分離して並記する。境界の維持状態は一次資料に基づく事実であり、
統合・再配置の提案は行わない。

| Layer | 役割(すること) | しないこと | Evidence根拠 |
|---|---|---|---|
| Observation | 差分・逸脱・状態の事実記録。表示/分離可視化 | 評価・解釈・判断・介入・統合・正規化 | phase10_4:4-6章, phase8_4:0章, a6 O0:13行 |
| Evidence / Provenance | 証拠の帰属・来歴・検証状態の管理 | 判断・承認・採用の決定 | KNOWLEDGE_PROVENANCE_VERIFICATION_ROADMAP_v0.6, R02 Observation Candidates(検証状態=未検証) |
| Integrity Classification | 状態分類(Failure/Risk/Unknown)と裁定(Open/Resolved/Superseded) | 実行・承認権限の付与 | Integrity Classification Ledger, DC_20260713_003(境界記述) |
| Decision | 承認証跡の発行(append-only, Active/Superseded/Withdrawn) | 観測・事実の一次生成 | Decision Ledger, DC_20260713_003(Decision=承認証跡) |
| Human Gate | 最終意思決定・裁定 | 一次観測・事実収集の代行 | DC_20260713_003(Human=最終意思決定), AUDIT OBSERVATION_LAYER:3行 |

責務分離の観察(事実):
- Observationは「評価禁止」を各構成物で明示している(phase10_4 6章, a6 O0非干渉原則,
  AUDIT OBSERVATION_LAYER「判断・評価・改善提案は一切行っていない」)
- Decision / Human Gate は「判断・承認」を担い、Observationとは責務が分離している
- ただしObservation と Integrity Classification の境界、Observation と Evidence/Provenance
  の境界は、概念的に近接する箇所があり、境界の明示的宣言が一次資料に未確認である
  (詳細はSection 3 Issue 5, 6)

---

## Section 3. Conflict / Ambiguity Register

R-04 Phase 4 の8項目を継承する。各項目は解消せず、曖昧なまま保存する。

### Issue 1: Observation と Governance Loop の関係(包含か分離か)

- Evidence: Governance Loop定義(COGNITIVE_GOVERNANCE_LAYER_v1.md, E20260615_111/112)の
  自己更新ループ内に「Drift観測」が構成要素として内在する
- Current Understanding: 観測はGovernance Loopの一フェーズとして既に内在している
- Unresolved Point: Observationを独立制度化した場合、Governance Loop内の観測フェーズと
  責務が重なる可能性がある。包含か分離かは未宣言
- Human Gate Required: Yes

### Issue 2: Observation の正本定義

- Evidence: 複数のObservation構成物が別Phase・別文書で独立定義(A6 O0 / Phase8-4 /
  Phase10-4 / META / AUDIT)。加えて観測モードとしての用法も存在(Section 1.3)
- Current Understanding: 統一されたObservation正本定義は一次資料に存在しない
- Unresolved Point: 分散が設計意図(複数維持)か副産物かは未確定。正本定義は未宣言
- Human Gate Required: Yes

### Issue 3: PRISM の存在・定義

- Evidence: events / knowledge_gate の一次データに literal "PRISM" が未検出(0件)
- Current Understanding: 本工程の一次範囲ではPRISMの制度定義は確認できない(Evidence Not Found)
- Unresolved Point: PRISMが制度対象か否か、別リポジトリ/会話層に定義が存在するか
- Human Gate Required: Yes

### Issue 4: PHL制度設計(H2)の未着手

- Evidence: Phase H1(E20260621_9708876874349)で責務定義のみ確定、H2/H3は将来工程宣言
- Current Understanding: PHLは責務定義層まで確定、制度設計(H2)は未着手
- Unresolved Point: ObservationとPHLの境界はH2(PHL制度設計)に依存し、現時点で確定できない
- Human Gate Required: Yes

### Issue 5: Observation と Integrity の境界(DEVIATION_ALERT vs Risk/Failure分類)

- Evidence: a6 O0のDEVIATION_ALERT/WARN(非評価・事実記録)と Integrity Classification
  (Failure/Risk/Unknownの分類・裁定)。一次資料上は分離
- Current Understanding: 役割は分離(観測=非評価 / Integrity=分類)しているが概念が近接
- Unresolved Point: 逸脱検知とRisk/Failure分類の境界の明示的宣言が未確認
- Human Gate Required: Yes

### Issue 6: Observation と Evidence / Provenance の境界

- Evidence: Observation(事実記録)と Evidence/Provenance(証拠帰属・来歴)は共に「記録」
- Current Understanding: 両者とも記録層であり概念的に近接する
- Unresolved Point: 両者の境界の明示的宣言が一次資料に未確認
- Human Gate Required: Yes

### Issue 7: R-04基礎資料のMoCKA一次データ未収載

- Evidence: R-03 Observation Architecture Evidence Book / Observation Constitutional
  Position Paper が events / knowledge_gate 検索で未検出
- Current Understanding: 基礎資料は会話/ファイル層に存在する可能性があるが、
  MoCKA一次データ上には収載されていない
- Unresolved Point: 基礎資料の正本所在(どこが正本か)が未確定
- Human Gate Required: Yes

### Issue 8: XUZ+TS と Observation の境界

- Evidence: XUZ+TS / ZYXTS の literal が一次データに未検出(PHL論文のZYXTSタグに関連の
  可能性はあるが確証なし)
- Current Understanding: XUZ+TSとObservationの境界を判断する一次根拠がない
- Unresolved Point: XUZ+TSの定義とObservationとの境界宣言が未確認
- Human Gate Required: Yes

---

## Section 4. Relationship Diagram

概念図のみ。統合案ではなく、関係確認図である。矢印/枠は「現在観測される関係」を
示すものであり、あるべき構造の提案ではない。

```
                 Human Gate
                     |
                     | (最終意思決定・裁定)
                     |
              Decision System
                     | (承認証跡 append-only)
                     |
+-----------------------------------------------+
|                MoCKA System                    |
|                                               |
|   Governance Loop                              |
|   (G1-G4 / 内部に Drift観測 を内在)   <-- Issue 1  |
|        |                                       |
|        |                                       |
|   Observation Components                       |
|   (a) Layers/Surfaces:                         |
|       A6 O0 / Phase8-4 / Phase10-4             |
|   (b) Observation-mode:                        |
|       AUDIT / META_OBSERVATION_LOG             |
|        |                                       |
|        | <-- Issue 5 (Integrity境界)            |
|        | <-- Issue 6 (Evidence/Provenance境界)  |
|        |                                       |
|   Evidence / Provenance                        |
|   Integrity Classification                     |
|                                               |
|   PHL (H1責務定義: Actor/Trace/Propagation/Trust)|
|       author=観測値 で Observation と接点        |
|       H2制度設計は未着手  <-- Issue 4            |
|                                               |
|   PRISM : 一次データ未検出  <-- Issue 3           |
|   XUZ+TS: 一次データ未検出  <-- Issue 8           |
+-----------------------------------------------+

              External View

               Ex-Audit
       (配置境界は未確定 / Human Gate判断領域)
```

図の注記:
- Governance Loop から Observation Components への線は、Governance Loop内に観測が
  内在している事実(Issue 1)を示す。包含/分離の確定ではない
- Ex-Audit の配置境界は本地図では確定しない(禁止事項)。Human Gate判断領域である
- PRISM / XUZ+TS は一次データ未検出のため、枠内に名称のみ保持し関係線は引かない

---

## 完了条件チェック

- Evidence Source Listed: 各構成物にSource(file path)とEvidence(file:line / event_id)を付与
- Responsibility Separation Documented: Section 2で5層の責務を分離記載
- Ambiguity Preserved: Section 3で8項目を解消せず保存
- No Recommendation: 推薦・優劣評価なし
- No Decision: 裁定・採用決定なし
- No Mutation Confirmed: 本文書作成以外のCode/Schema/Ledger/Event/Commit/Merge変更なし

## 改訂履歴

- v0.1 (2026-07-14): R-04を基礎資料として新規作成。くろこ起草。READ ONLY / Mutation NONE。

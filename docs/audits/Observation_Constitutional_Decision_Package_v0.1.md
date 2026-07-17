# Observation Constitutional Decision Package v0.1

Status: DECISION SUPPORT / NON-CANONICAL / HUMAN GATE INPUT
Date: 2026-07-14
作成: くろこ(Claude Code)
基礎資料: Observation Constitutional Map v0.1, R-04 Observation Constitutional Cross-System Validation

---

## Section 1. Purpose and Boundary

### 1.1 本資料の目的

Observation Constitutional Map v0.1 を基礎資料として、MoCKAのObservation制度に関する
判断を Human Gate が下せる状態まで証拠を整理する。本資料は以下までを行う:

- 判断対象の明確化
- Evidence整理
- 選択肢構造化
- 影響範囲整理
- 未解決事項提示

そして Human Gate へ引き渡せる状態で停止する。

### 1.2 Decision Package の役割

本資料は「判断のための入力」であり、判断そのものではない。選択肢を構造化して並べるが、
どの選択肢を採るべきかは示さない。

### 1.3 Authority / Boundary(最重要)

- 本作業者(くろこ)は判断者ではない。以下を行わない:
  制度採択 / Architecture決定 / Observation正本決定 / Ex-Audit配置決定 / Phase C開始判断
- Recommendation を行わない。優劣評価を行わない。
- Mutation Boundary: Document生成のみ。Code変更 / Schema変更 / Decision Ledger Write /
  Event Ledger Write / Commit / Merge / Existing Artifact Modification はいずれも行っていない。
- 本工程の完了は「Observation制度が決定した」ことを意味しない。
  意味するものは「Human Gateが制度判断できる証拠状態になった」ことである。

工程位置:
```
R-04
 -> Observation Constitutional Map v0.1
 -> Observation Constitutional Decision Package v0.1  (本資料。ここで停止)
 -> Human Gate  (次工程は人間判断後)
```

---

## Section 2. Current Evidence State

### 2.1 Observation

存在確認済み構成物(一次ファイル根拠あり):

| Component | Source | Evidence | Current Role |
|---|---|---|---|
| A6 O0 | docs/experimental/meta/a6_observation_layer_o0_v1.md | 同:8-13行 | A6非破壊の観測レイヤ。観測のみ、介入なし(NON-CANONICAL) |
| Phase8-4 Observation Surface | docs/contracts/phase8_4_observation_surface_v1.md | 同:0章,24-35行 | 分断意味空間の表示のみ。解釈/比較/統合しない(DRAFT) |
| Phase10-4 Operational Observation Layer | docs/contracts/phase10_4_operational_observation_layer_v1.md | 同:4章,6章 | 差分発生の事実記録。評価禁止(宣言のみ) |
| META_OBSERVATION_LOG | docs/governance/META_OBSERVATION_LOG_v0.1.md | 同:5行 | 監査横断の共通パターン事実記録 |
| AUDIT OBSERVATION_LAYER | docs/governance/MOCKA_AUDIT_INSTRUCTION_v1.0_OBSERVATION_LAYER_v0.1.md | 同:3行 | 監査項目の構造的事実をfile:line根拠付き報告 |

Reference Candidate(R-04対象範囲外、正本扱いしない。将来Inventory拡張時の候補):

| Component | Source | 分類 |
|---|---|---|
| MCP Scope Separation Observation | docs/governance/MOCKA_MCP_SCOPE_SEPARATION_OBSERVATION_v0.1.md | Reference Candidate |
| R02 Observation Candidates | docs/governance/TODO_437_R02_OBSERVATION_CANDIDATES_v0.1.md | Reference Candidate |

構造的事実(Observationの二義性、判断の前提):
- (a) 名前を持つ観測レイヤ/サーフェス: A6 O0 / Phase8-4 / Phase10-4
- (b) 監査に適用される観測モード/役割: AUDIT OBSERVATION_LAYER / META_OBSERVATION_LOG
- この二義が同一語「Observation」で共存している。HG-01の判断に先行する前提として提示する。

### 2.2 Governance Loop

- Architecture定義: docs/architecture/COGNITIVE_GOVERNANCE_LAYER_v1.md
  (event E20260615_111 / E20260615_112)。G1 Intent Synthesis / G2 Prioritization /
  G3 Conflict Resolution / G4 Direction Projection の自己更新ループ
- Observationとの接点: 自己更新ループ(Intent生成 -> Constraint評価 -> Execution ->
  Drift観測 -> Decision再生成)の中に「Drift観測」が構成要素として内在する
- 未確定境界: Observationを外部Observation Layerとして独立させるか、Governance Loop内の
  観測フェーズのままとするかは未宣言(HG-02)。制度(Institution)としての独立宣言も未確認

### 2.3 PHL

- H1責務定義(event E20260621_9708876874349、実装ゼロ):
  H1-1 Actor(actor_id: 登録 != 信頼付与) / H1-2 Trace(関係記録のみ、責任評価しない) /
  H1-3 Propagation(既存フローへの意味付け、新規経路追加なし) /
  H1-4 Trust(信頼=観測可能性の制御、TraceとTrust独立)
- Observationとの接点: H1-1 Binding Rule「author = 観測値(既存・継続)」により、
  Observation(観測値)がPHL Actor定義の一構成に接続している
- 未着手領域: H2(PHL制度設計)・H3(PHL実装)は将来工程として未着手。
  ObservationとPHLの境界確定はH2に依存する

参考(一次データ未検出、判断の前提として明示):
- PRISM: events / knowledge_gate に literal 0件(Evidence Not Found)
- XUZ+TS / ZYXTS: 一次データに定義未検出

---

## Section 3. Human Gate Decision Items

以下5項目を判断対象として整理する。各項目に対して選択肢・Evidence・影響範囲を示すが、
優劣評価・推薦は行わない。判断は Human Gate 領域である。

### HG-01: Observation 正本定義

- 論点: Observationを制度としてどう定義するか
- 前提: Observationの二義性(2.1)。(a)Layer/Surface名称 か (b)観測モード/役割 か、
  あるいは両方を含む定義かの整理が本項に先行する
- 選択肢(優劣評価禁止):
  - Single Institution: Observationを単一の制度として定義する
  - Multiple Institutions: 複数のObservation構成物を別制度として維持する
  - Layered Structure: Observationを層構造として定義する
- Evidence(R-04 Cross-System Evidence Alignment。採用可能性ではなく「証拠の揃い具合」):
  - Single: 単一正本定義は一次資料に存在しない -> Alignment LOW
  - Multiple: 複数構成物が別Phase/別文書で独立定義 + 観測モード用法が併存 -> Alignment MEDIUM
  - Layered: 層構造の材料が複数(A6=時間層/空間層分離、Governance Loop=観測系Step1-3から
    判断生成系Step4、Phase10-4=Phase10-3 baseline上の非干渉層) -> Alignment MEDIUM
  - 注: Alignment は evidence の揃い具合のみを示し、優劣・採用可能性を示さない
- 影響範囲: HG-02〜HG-05 および Section 4(Ex-Audit/Phase C)はすべて本定義に依存する
- Human Gate Required: Yes

### HG-02: Observation <-> Governance Loop

- 論点: 包含 / 分離 / 相互関係
- 選択肢:
  - 包含: ObservationをGovernance Loopの一フェーズとして扱う(現状の内在を追認)
  - 分離: Observationを独立した層/制度として切り出す
  - 相互関係: 両者を別立てにしつつ接続関係を定義する
- Evidence(R-04結果): Governance Loop定義(COGNITIVE_GOVERNANCE_LAYER_v1.md,
  E20260615_111/112)内に「Drift観測」が構成要素として内在。README.mdでmocka_Movementが
  primary governance loopとして記述される
- 影響範囲: HG-01と相互依存。分離を選ぶ場合、Governance Loop内の観測フェーズとの
  責務重複の調整が必要になる(Open Issue 1)
- Human Gate Required: Yes

### HG-03: Observation <-> Integrity Boundary

- 論点: Observation / Integrity Classification / Decision の責務境界
- Evidence:
  - Observation = 非評価・事実記録(phase10_4 6章、a6 O0 非干渉原則)
  - Integrity Classification = 状態分類・裁定(Failure/Risk/Unknown, Open/Resolved/Superseded)
  - Decision = 承認証跡(append-only)
  - 現在の境界(Map Section 2): 事実取得 -> 分類・評価 -> 人間判断 の流れが維持されている
  - 近接点: ObservationのDEVIATION_ALERT と Integrityの Risk/Failure分類(Open Issue 5)
- 制度上の懸念(事実記述、判断はHuman Gate): 境界を誤ると
  「観測者 -> 評価者 -> 裁定者」への滑りが生じうる
- 影響範囲: HG-05(Ex-Auditのobservation_only維持条件)に直結する
- Human Gate Required: Yes

### HG-04: Observation <-> Evidence / Provenance Boundary

- 論点: 事実観測 / 証拠帰属 / 来歴管理
- Evidence:
  - Observation = 事実観測(差分発生の事実記録)
  - Evidence / Provenance = 証拠帰属・来歴管理
    (KNOWLEDGE_PROVENANCE_VERIFICATION_ROADMAP_v0.6)
  - 両者とも「記録層」であり概念的に近接する(Open Issue 6)
  - 中間例: R02 Observation Candidates(検証状態=未検証の証拠候補)
- 影響範囲: Observation出力がどの時点でProvenance管理下に入るかの境界が未定義
- Human Gate Required: Yes

### HG-05: Ex-Audit 配置境界

- 論点: Observation Layerとの関係 / 外部監査層としての位置 / observation_only維持条件
- Evidence State(重要、明示): 「Ex-Audit」「observation_only」「Ex-Audit v0.1」は、
  MoCKA一次資料(docs/governance, docs/contracts, docs/architecture)および
  events / knowledge_gate 検索で定義が未検出である。現時点では会話層の参照であり、
  正本定義が一次データ上に存在しない
- したがって本項は、HG-01〜HG-04の判断に加えて「Ex-Audit正本定義の確定」を先行条件とする。
  Evidence基盤が未確立であるため、選択肢の構造化は前提成立後に可能となる
- 論点提示(前提未成立の状態で):
  - Ex-Audit を Observation Layer の内側に置くか、外部に置くか
  - 外部監査層として observation_only(観測のみ、評価・裁定しない)を維持する条件は何か
- 影響範囲: HG-03(Observation/Integrity境界)の帰結に依存する
- Human Gate Required: Yes(先行条件: Ex-Audit正本定義の確定)

---

## Section 4. Future Phase Condition

Phase C / EA-03 について整理する。

- Evidence State: 「Phase C」「EA-03」は events / knowledge_gate / docs いずれの一次データ
  でも定義が未検出である
- 現時点では未承認である
- v0.1境界(READ ONLY / Mutation NONE / observation-only 相当の非介入)を維持する
- Phase C / EA-03 の開始可否は Human Gate 判断後に決定される事項である
- 本資料は実装計画化・ロードマップ確定を行わない(禁止事項)

---

## Section 5. Open Issues

R-04 Phase 4 の Issue 1〜8 を継承する。いずれも解消せず、曖昧なまま提示する
(詳細は Observation Constitutional Map v0.1 Section 3 を参照)。

| Issue | 要旨 | Human Gate Required |
|---|---|---|
| 1 | Observation <-> Governance Loop の関係(包含か分離か)。観測がLoop内に内在 | Yes |
| 2 | Observation の正本定義。複数構成物が分散、統一定義未宣言 | Yes |
| 3 | PRISM の存在・定義。一次データ未検出(Not Found) | Yes |
| 4 | PHL制度設計(H2)の未着手。Observation境界がH2に依存 | Yes |
| 5 | Observation <-> Integrity 境界(DEVIATION_ALERT vs Risk/Failure分類) | Yes |
| 6 | Observation <-> Evidence/Provenance 境界。両者とも記録層で近接 | Yes |
| 7 | R-04基礎資料(R-03 Evidence Book / Position Paper)のMoCKA一次データ未収載 | Yes |
| 8 | XUZ+TS <-> Observation 境界。XUZ+TS一次未検出 | Yes |

補足 Open Issue(R-04 Phase4の8項目とは別枠。本パッケージで新たに保存):

| Issue | 要旨 | Human Gate Required |
|---|---|---|
| S-1 | 「ファイル生成はMutationか」= Document Artifact Creation vs Artifact Creation Event。本工程はArtifact CreationとしてEvent記録なしで許可されたが、通常運用ではArtifact Creation Eventが要る可能性。Observation制度自身の運用設計課題として保存(未記録) | Yes |
| S-2 | Ex-Audit / observation_only / EA-03 / Phase C の正本定義が一次データ未検出。HG-05・Section 4の前提が未成立 | Yes |

---

## Section 6. Final Handover Status

```
Observation Constitutional Decision Package v0.1

Status:              COMPLETE
Purpose:             Human Gate Decision Support
Authority:           NONE
Recommendation:      NONE
Decision:            NONE
Mutation:            NONE
Ready for Human Gate: YES
```

終端条件チェック:
- Evidence Organized: Section 2 で Observation / Governance Loop / PHL の証拠状態を整理
- Decision Items Defined: Section 3 で HG-01〜HG-05 を判断対象として定義
- Options Structured: 各HG項目に選択肢・Evidence・影響範囲を構造化(優劣評価なし)
- No Recommendation: 推薦なし
- No Decision: 裁定なし
- No Mutation: 本文書生成以外に Code/Schema/Ledger/Event/Commit/Merge/既存Artifact変更なし
- Human Gate Ready: Yes

注意: 本工程の完了は Observation制度の決定を意味しない。
Human Gate が制度判断できる証拠状態に到達したことを意味する。

## 改訂履歴

- v0.1 (2026-07-14): Observation Constitutional Map v0.1 を基礎資料として新規作成。
  くろこ起草。READ ONLY / Mutation NONE / Recommendation NONE。

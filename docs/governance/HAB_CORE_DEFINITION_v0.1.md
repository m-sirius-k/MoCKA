# HAB Core Definition v0.1
## Human Authority Boundary — 最小定義(Canonical State / Actor / Transition Ledger / JARVIS 権限境界)

**文書番号:** HAB-CORE-DEF-001
**作成日:** 2026-08-04
**状態:** **DRAFT(未裁定)**
**Decision Ledger 登録:** なし
**実装:** **なし**(コード・スキーマ・データのいずれも変更していない)

---

## 0. 本文書の位置づけ

### 0.1 何であり、何でないか

| | |
|---|---|
| **本文書である** | 制度境界の**定義**。Human Gate Finalization への提示材料 |
| **本文書でない** | 発効した規約 / 実装指示 / マイグレーション計画 / Decision |

きむら博士の方針(原文)に従う:
> 既存システムの全面改修は禁止。まず制度境界を固定し、その後 JARVIS 能力を拡張する。

**本文書は既存の HG-1〜HG-5 を直接統合変更しない。**
canonical state を**新たに定義し**、既存状態との mapping を作るのみである。

### 0.2 禁止事項の遵守状況

| 禁止事項(博士指示) | 遵守状況 |
|---|---|
| 一括修正スクリプト作成禁止 | 遵守(スクリプトを一切作成していない) |
| 既存データの書換禁止 | 遵守(`human_gate_events` / `prevention_queue.json` 等に一切書き込んでいない) |
| 過去イベント補完禁止 | 遵守(backfill・補完を設計にも含めていない) |
| 原因推測禁止 | 遵守(§1 の Finding は観測事実のみ。U-30 等の原因を推測していない) |

### 0.3 表記規約

| ラベル | 意味 |
|---|---|
| **【観測】** | 一次データで確認した事実 |
| **【博士提示】** | きむら博士が本指示で提示した内容。本文書はこれを基準として採用する |
| **【起案】** | 本文書が新たに提案する内容。**未裁定** |
| **【未確定】** | 一次資料に記載がなく、本文書では確定させない事項 |

### 0.4 対象とする "HAB" の特定(重要)

`JARVIS_HGJ03_EVIDENCE_COMPLETE_v0.1.md` §1.1 のとおり "HAB" は4つの対象を指す。
**本文書が対象とするのは HAB-A(Human Authority Boundary)である。**

| # | 呼称 | 本文書との関係 |
|---|---|---|
| **HAB-A** | **Human Authority Boundary**(`docs/governance/mocka_hab_v1_contract.md`、DRAFT) | **本文書の対象** |
| HAB-B | HAB spine(`semantic/query_engine/`) | 対象外 |
| HAB-C | PHI-HAB(構想、`ジャビス.md`) | 対象外(HG-J03 裁定待ち) |
| HAB-D | PHI-HAB(制度、`DC_20260729_008`。3系統) | 対象外(HG-J03 裁定待ち) |

**本文書は HG-J03 を先取りしない。** HAB-C / HAB-D の帰属は依然 Human Gate 裁定事項である。

### 0.5 既存 HAB-A 契約との軸の分離(重要)

`mocka_hab_v1_contract.md` §2 は「全システム状態」として
`STABLE / DRAFT / REVIEW / STASIS / ACTIVE` を定義している【観測】。

**これは本文書が定義する canonical state とは軸が異なる。**

| 軸 | 対象 | 語彙 | 出典 |
|---|---|---|---|
| **層状態(Layer State)** | FROZEN 層 / Extension 層 等、**層そのもの**の状態 | `STABLE / DRAFT / REVIEW / STASIS / ACTIVE` | `mocka_hab_v1_contract.md` §2(既存 DRAFT) |
| **要求状態(Request State)** | **個々の承認要求(request_id)** の状態 | 本文書 §2 の canonical state | 本文書(新規) |

**【起案】本文書は層状態を変更しない。両者を同一視してはならない。**
`mocka_hab_v1_contract.md` §5 の遷移規則(DRAFT→ACTIVE 等)は層状態の規則であり、本文書は触れない。

---

## 1. HG-J04 Evidence Record — Finding の固定

きむら博士の指示に従い、HG-J04 観測で確認された事項を Finding として固定する。
**すべて観測事実であり、原因の推測を含まない。**

### F-1: State Authority 分裂【観測】

同一の承認概念に対し、**5系統が独立した状態記録先と状態語彙を持つ。**

| 系統 | 状態記録先 | 状態語彙 |
|---|---|---|
| HG-1 `phi_os/human_gate.py` | `mocka_events.db` / `human_gate_events` | `PENDING / APPROVED / REJECTED / EXPIRED / CANCELED` |
| HG-2 `app.py /decision/*` | `data/prevention_queue.json` | `NEW / approved / rejected` |
| HG-3 `mocka_git_safe_commit.py` | git 作業ツリー(未コミット保持) | 状態語彙なし |
| HG-4 `semantic/query_engine/human_gate.py` | インメモリ(非永続) | `accept / reject / defer / split` |
| HG-5 `governance/human_gate_continuity.py` | `data/decisions/pending_decision_units.jsonl` | `WAITING_FOR_HUMAN_GATE` |

**実測された不一致:** 同一の 1,773 項目について
HG-1 は `PENDING`(1,774件)、HG-2 は `rejected`(1,799件)を保持している。
`prevention_queue.json` の `id` と `human_gate_events.request_id` は 1,773 / 1,941 が一致する。

### F-2: Transition Ledger 欠落【観測】

状態遷移が発生しても、その遷移が台帳に記録されない経路が存在する。

| 観測項目 | 実測 |
|---|---|
| `human_gate_events` の `action` 分布 | `submit` 1,774 / `approve` 5。**`reject` / `expire` / `cancel` は 0件** |
| `prevention_queue.json` の `rejected` | **1,799件** |
| 対応する `DECISION_REJECTED` イベント | **1件** |
| 2026-06-28 の一括却下(`NEW` 1,799 → `rejected` 1,799)に対応する台帳記録 | **`human_gate_events` 0件 / Event Ledger 0件** |

**すなわち 1,798件の状態遷移について、遷移そのものの記録が存在しない。**
(原因・実施主体は **U-30** として Unknown 保持。**推測しない。**)

### F-3: Actor 識別不足【観測】

| 観測項目 | 実測 |
|---|---|
| `human_gate_events` のカラム | `event_id, timestamp, type, action, request_id, payload, previous_state, next_state` |
| **`actor` に相当するカラム** | **存在しない** |
| HG-2 の `who_actor` | `"kimura_hakase"` を**コード内にハードコード**。呼出者の検証処理は本ルート上に発見できず |
| 定義文書の要求 | `mocka_human_gate_decision_definition_v1.md` §7: 「APPROVE/HOLD/REJECT/DEFER の確定は Human Gate Finalization(博士本人)のみが行う」 |

**結果:** 記録から **Core 実行と Finalization 実行を区別できない**。

### F-4: Unknown 保持(U-30〜U-37)

| # | Unknown | 状態 |
|---|---|---|
| U-30 | 2026-06-28 一括却下の実施主体・手段 | **保持**(追跡しない) |
| U-31 | HG-5 `WAITING_FOR_HUMAN_GATE` が `HOLD` / `DEFER` のいずれに対応するか | **保持** |
| U-32 | `TECH_ALERT_*` 1,768件の生成主体の直接証拠 | **保持** |
| U-33 | HG-3 の「承認」の記録先 | **保持** |
| U-34 | HG-4 `HumanGateRulingStore` の実行時生成箇所 | **保持** |
| U-35 | `pending_decision_units.jsonl` 2件の内容 / TODO_429 の現況 | **保持** |
| U-36 | `prevention_queue` の 168件が HG-1 側へ反映される経路の有無 | **保持** |
| U-37 | `/decision/approve` `/decision/reject` の呼出元と使用頻度 | **保持** |

---

## 2. Canonical State Definition【博士提示 + 起案】

### 2.1 基準語彙

きむら博士が提示した8状態を canonical state として採用する【博士提示】。

| # | State | 定義【起案】 | 到達条件【起案】 |
|---|---|---|---|
| 1 | `IDLE` | 対象について評価も要求も開始されていない | 初期状態。記録を伴わない(§2.3) |
| 2 | `EVALUATING` | Human Gate Core が判断材料を生成中 | Core が評価を開始した |
| 3 | `PENDING_HUMAN_GATE` | 判断材料が揃い、**きむら博士の裁定を待っている** | Core の評価完了(定義文書 §5 の `EVALUATED` に対応) |
| 4 | `APPROVED` | 裁定により承認が確定した | **Finalization のみ**が到達させうる |
| 5 | `REJECTED` | 裁定により不許可が確定した | **Finalization のみ** |
| 6 | `DEFERRED` | 他層依存等により裁定が延期された | **Finalization のみ** |
| 7 | `EXPIRED` | 裁定されないまま有効期限に達した | 期限条件(**未確定**、§2.4) |
| 8 | `CANCELLED` | 要求が取り下げられた | 要求元による取消 |

### 2.2 遷移規則【起案】

```
IDLE
  │ (要求発生)
  ▼
EVALUATING ──────────────┐
  │ (Core 評価完了)       │ (取消)
  ▼                      │
PENDING_HUMAN_GATE ──────┤
  │                      │
  │ ★ Finalization のみ  │ (期限到達)
  ├──► APPROVED          ├──► EXPIRED
  ├──► REJECTED          │
  ├──► DEFERRED ─────────┘ (再評価で EVALUATING へ戻りうる)
  │
  └──► CANCELLED
```

**★ 印の遷移(`PENDING_HUMAN_GATE` → `APPROVED` / `REJECTED` / `DEFERRED`)は、
Human Gate Finalization(きむら博士本人)のみが実行できる**【起案、定義文書 §7 の継承】。

`EVALUATING` から `APPROVED` / `REJECTED` / `DEFERRED` への**直接遷移は定義しない**。
必ず `PENDING_HUMAN_GATE` を経由する【起案】。

### 2.3 `IDLE` の記録上の扱い【起案】

`IDLE` は「まだ何も起きていない」状態であり、**記録を生成しない**。
`IDLE → EVALUATING` の遷移が最初の記録となる。

理由: `IDLE` を記録対象にすると、対象になりうる全事象について記録が発生し、
Event Ledger の意味が変わるため。

### 2.4 **`HOLD` の不在について(重要な観測)**【観測 + 未確定】

`mocka_human_gate_decision_definition_v1.md` §2.2 が定める Finalization の出力は
**`APPROVE / HOLD / REJECT / DEFER`** の4値である【観測】。

博士提示の canonical state には **`HOLD` に対応する状態が含まれていない**
(`DEFERRED` は `DEFER` に対応する)。

| 定義文書の出力値 | canonical state の対応 |
|---|---|
| APPROVE | `APPROVED` |
| **HOLD** | **対応なし** |
| REJECT | `REJECTED` |
| DEFER | `DEFERRED` |

**本文書は `HOLD` を勝手に追加しない。** 以下のいずれであるかは **【未確定】**:
- (a) `HOLD` を canonical state に追加すべき
- (b) `HOLD` は `PENDING_HUMAN_GATE` へ差し戻す操作であり状態ではない
- (c) `HOLD` は `DEFERRED` に統合される

**Human Gate 提示事項 HG-H01**(§10)。

同様に `EXPIRED` の期限条件も **【未確定】**(HG-H02)。

---

## 3. Existing State Mapping【起案】

**本 mapping は既存システムの状態値を変更しない。** 読み替え表である。

### 3.1 HG-1 `phi_os/human_gate.py`

| 既存 | canonical | 備考 |
|---|---|---|
| `PENDING` | `PENDING_HUMAN_GATE` | 1:1 |
| `APPROVED` | `APPROVED` | 1:1 |
| `REJECTED` | `REJECTED` | 1:1 |
| `EXPIRED` | `EXPIRED` | 1:1 |
| `CANCELED` | `CANCELLED` | **綴りが異なる**(1 L / 2 L)。値の変更は行わず読み替えのみ |
| (なし) | `IDLE` / `EVALUATING` / `DEFERRED` | **既存側に対応なし** |

### 3.2 HG-2 `app.py /decision/*`(`prevention_queue.json`)

| 既存 | canonical | 備考 |
|---|---|---|
| `NEW` | **【未確定】** | `IDLE` / `EVALUATING` / `PENDING_HUMAN_GATE` のいずれとも読めるため確定しない(HG-H03) |
| `approved` | `APPROVED` | 大小文字差のみ |
| `rejected` | `REJECTED` | 同上 |
| (なし) | `EVALUATING` / `DEFERRED` / `EXPIRED` / `CANCELLED` | 既存側に対応なし |

**注記【観測】:** `TODO_387案B` の記載により、`prevention_queue` の status 値は
生成元によって表記が割れている(app.py:2276 コメント)。本 mapping はこの分岐を解決しない。

### 3.3 HG-4 `semantic/query_engine/human_gate.py`

| 既存 | canonical | 備考 |
|---|---|---|
| `accept` | `APPROVED`(相当) | **対象が異なる**(下記) |
| `reject` | `REJECTED`(相当) | 同上 |
| `defer` | `DEFERRED`(相当) | 同上 |
| **`split`** | **対応なし【未確定】** | canonical に対応語彙がない(HG-H04) |
| (`merge`) | — | **恒久的に除外**(契約5章)。canonical にも追加しない |

**重要な観測:** HG-4 の裁定対象は **collision(意味衝突)** であり、承認要求ではない。
遷移(TRANSITIONS)の概念を持たず、`RulingRecord` を append するのみである。
**したがって HG-4 を canonical state 体系に含めるべきかどうか自体が【未確定】**(HG-H04)。

### 3.4 HG-5 `governance/human_gate_continuity.py`

| 既存 | canonical | 備考 |
|---|---|---|
| `WAITING_FOR_HUMAN_GATE` | **【未確定】** | `PENDING_HUMAN_GATE` / `DEFERRED` / (`HOLD`) のいずれとも読める。**U-31 として Unknown 保持中**。本文書では確定しない(HG-H05) |

**構造的制約【観測】:** HG-5 は「`WAITING_FOR_HUMAN_GATE` へ遷移した時点で処理を止める構造であり、
governance_state をそこから先に進める関数自体を実装しない」と自ら明記している。
canonical 側の `PENDING_HUMAN_GATE` は前進しうる状態であり、**この構造的制約と同一ではない**。

### 3.5 HG-3 `mocka_git_safe_commit.py`

| 既存 | canonical | 備考 |
|---|---|---|
| (状態語彙なし。Core System File を未コミット保持) | **【未確定】** | 記録先が U-33 として Unknown。mapping を作る材料がない(HG-H06) |

### 3.6 Mapping の網羅状況【観測】

| canonical state | 対応する既存実装 |
|---|---|
| `IDLE` | **なし** |
| `EVALUATING` | **なし**(定義文書 §5 の Core 状態も未実装) |
| `PENDING_HUMAN_GATE` | HG-1 `PENDING` のみ |
| `APPROVED` | HG-1 / HG-2 / (HG-4 `accept`) |
| `REJECTED` | HG-1 / HG-2 / (HG-4 `reject`) |
| `DEFERRED` | (HG-4 `defer`)のみ |
| `EXPIRED` | HG-1 のみ(実データ 0件) |
| `CANCELLED` | HG-1 `CANCELED` のみ(実データ 0件) |

---

## 4. Actor Model Definition【博士提示 + 起案】

### 4.1 必須フィールド【博士提示】

博士が提示した7項目を必須とする。

| フィールド | 型【起案】 | 定義【起案】 |
|---|---|---|
| `actor_id` | string | 行為主体の一意識別子。人間・スクリプト・AI を問わず必須 |
| `actor_type` | enum | §4.2 |
| `decision_scope` | string | 当該行為が及ぶ範囲(対象 request_id / 層 / ファイル群等) |
| `evidence_reference` | string[] | 根拠となる Event ID / Decision ID / 文書パスの配列 |
| `previous_state` | canonical state \| null | 遷移前。新規生成時は null |
| `next_state` | canonical state | 遷移後 |
| `timestamp` | ISO8601(UTC) | 記録時刻 |

### 4.2 `actor_type` の値【起案】

| 値 | 定義 | `PENDING_HUMAN_GATE` → `APPROVED/REJECTED/DEFERRED` の実行可否 |
|---|---|---|
| `human_authority` | きむら博士本人(Human Gate Finalization) | **可** |
| `human_other` | 博士以外の人間 | **不可**【起案】 |
| `ai_agent` | AI(JARVIS を含む) | **不可** |
| `script` | 自動処理・バッチ・デーモン | **不可** |
| `system` | ランタイム内部処理(期限切れ判定等) | **`EXPIRED` のみ可**【起案】 |
| `unknown` | 主体を特定できない記録 | **不可**。§4.4 |

**根拠:** `mocka_human_gate_decision_definition_v1.md` §7、
`mocka_hab_human_gate_relation_v1.md` §4「自動裁定ループ禁止」。

### 4.3 目的の充足【博士提示】

> 「誰が、何を根拠に、どの状態を変更したか」を後から検証可能にする。

| 問い | 対応フィールド |
|---|---|
| 誰が | `actor_id` + `actor_type` |
| 何を根拠に | `evidence_reference` |
| どの状態を | `decision_scope` + `previous_state` → `next_state` |
| いつ | `timestamp` |

### 4.4 既存記録への遡及【起案 — 禁止事項の遵守】

**既存の `human_gate_events` 1,779件に `actor` を遡及付与しない。**
理由: 博士指示の「過去イベント補完禁止」に該当する。
既存記録は `actor_type` を判定する情報を持たないため、
**推定による補完は Evidence-Bound 原則に反する。**

既存記録を canonical モデルで参照する場合の扱いは
`actor_type = unknown` **として読む**のみとし、**データは書き換えない**【起案】。

---

## 5. Decision Transition Ledger Schema【博士提示 + 起案】

### 5.1 設計制約【博士提示】

> 既存 `human_gate_events` を破壊しない。新規または拡張形式で定義する。

**【起案】新規台帳として定義する(既存テーブルの変更を伴わない)。**
理由: `human_gate_events` へのカラム追加は既存1,779件に NULL 列を生じさせ、
それを埋める作業が「過去イベント補完」に該当するため。

### 5.2 Decision Transition Record — 最低要件【博士提示】

| フィールド | 型【起案】 | 定義【起案】 |
|---|---|---|
| `decision_id` | string | 本遷移の一意 ID |
| `event_id` | string | 対応する Event Ledger の event_id。**Canonical Ledger 経路で発行されたもの** |
| `actor` | object | §4.1 の Actor Model(`actor_id` / `actor_type` / `decision_scope` / `evidence_reference`) |
| `action` | enum | `submit / evaluate / approve / reject / defer / expire / cancel`【起案】 |
| `before` | canonical state \| null | 遷移前 |
| `after` | canonical state | 遷移後 |
| `evidence_hash` | string | §5.4 |

### 5.3 append-only 制約【起案】

- **上書き・削除を行わない。** 訂正は新しいレコードの追加で表現する。
- 根拠: `PHI_OS_CONSTITUTION_v1.md` 原則1(Event Ledger は append-only)、
  `DC_20260801_002` HG-1(COLLISION 自動修復禁止)。

### 5.4 `evidence_hash` について【起案 + 観測】

**【観測】** `evidence_hash` という名称の実装はリポジトリ内に存在しない
(`.py` 全体 grep、`archive/`・`venv/` 除外。0件)。

**【観測】既存の最も近い先例:** `event_signatures` テーブル
(`event_id, seq, timestamp, previous_hash, current_hash, signature_version, algorithm`、19,037件)。
`phi_os/event_gate.py` の `integrity.sign_event()` が生成する。

**【起案】** `evidence_hash` は `evidence_reference` が指す証跡集合の同一性を担保する値とする。
**何をどのアルゴリズムでハッシュするかは本文書では確定しない【未確定】**(HG-H07)。
理由: 既存 `event_signatures` の連鎖と整合させるか、独立させるかは設計判断であり、
本文書のスコープ(制度境界の定義)を超える。

### 5.5 記録先【未確定】

候補は複数ありうるが、**本文書では確定しない**(HG-H08)。
既存の記録先(`human_gate_events` / `decision_ledger.jsonl` / `pending_decision_units.jsonl`)は
いずれも用途が既に定義されており、そこへ混在させるか新設するかは裁定事項である。

**確定していること【起案】:** 記録は `phi_os/event_gate.py: process_event()` を経由する
Canonical Ledger 経路と整合させること。
根拠: `DC_20260725_003` 条件3「Canonical Ledger 経路(`get_buffer().push()`)には一切変更を加えない」。

---

## 6. JARVIS Authority Boundary【博士提示 + 起案】

### 6.1 許可【博士提示】

| # | 許可行為 | 条件【起案】 |
|---|---|---|
| A-1 | **Evidence 収集** | 収集のみ。改変・要約による意味変更をしない |
| A-2 | **状態説明** | canonical state を用いて現状を説明する。状態を変更しない |
| A-3 | **異常検知** | 不一致・欠落の**検出と報告**。是正しない |
| A-4 | **提案生成** | 候補の提示のみ。`decision` フィールドを含めない |

### 6.2 禁止【博士提示】

| # | 禁止行為 | 根拠 |
|---|---|---|
| P-1 | **Human Decision の代替** | `mocka_human_gate_decision_definition_v1.md` §7 |
| P-2 | **approve / reject の実行** | 同上。`actor_type` が `human_authority` 以外は §4.2 により不可 |
| P-3 | **authority escalation** | `PHI_OS_CONSTITUTION_v1.md` §3.2 Authority 一意性原則 / §5.5「記録なき Authority 委譲」禁止 |
| P-4 | **ledger 改変** | 原則1(append-only)/ `DC_20260801_002` HG-1 |

### 6.3 派生する禁止【起案】

| # | 禁止行為 | 理由 |
|---|---|---|
| P-5 | 自身を `actor_type = human_authority` として記録すること | P-1/P-2 の実効性担保 |
| P-6 | `evidence_reference` を伴わない状態説明・提案 | Evidence-Bound(`DC_20260730_009`) |
| P-7 | 検出した異常の自動是正・一括修正 | P-4 / 博士指示「一括修正スクリプト作成禁止」 |
| P-8 | 既存記録の欠落を推測で補完すること | 博士指示「過去イベント補完禁止」「原因推測禁止」 |
| P-9 | 本 Authority Boundary 自体の変更を自ら実行すること | 自己適用原則(`JARVIS_CONSTITUTION_DRAFT.md` §3.3) |

### 6.4 `JARVIS_CONSTITUTION_DRAFT.md` との対応【観測】

本章は Constitution Draft §3 の権限境界と矛盾しない。

| 本文書 | Constitution Draft |
|---|---|
| A-1 Evidence 収集 | A-2 既存 Evidence の提示 |
| A-2 状態説明 | A-1 解釈候補の生成(候補明示) |
| A-3 異常検知 | A-6 未検証文脈の検出と隔離報告 |
| A-4 提案生成 | A-1 / A-4(`decision` フィールドを含めない) |
| P-1 / P-2 | P-2 / P-3 / P-14 |
| P-3 | P-10 Authority の変更・委譲禁止 |
| P-4 | P-5 / P-6 / P-7 |

---

## 7. 自動裁定化リスクの自己点検【起案】

`mocka_hab_human_gate_relation_v1.md` §4 が禁止する3構造に該当しないことを確認する。

| 禁止構造 | 本定義での扱い |
|---|---|
| **直接遷移**(Human Gate を経由しない遷移) | §2.2 で `EVALUATING` → `APPROVED/REJECTED/DEFERRED` の直接遷移を**定義していない**。必ず `PENDING_HUMAN_GATE` を経由する |
| **自動裁定ループ**(Core → 自動 APPROVE) | §4.2 で `human_authority` 以外の `actor_type` による `APPROVED/REJECTED/DEFERRED` 到達を**不可**とした。閾値・条件による自動承認条項を**一切設けていない** |
| **HAB の意思化**(状態記述層が判断主体になる) | 本文書は状態語彙と記録形式のみを定義し、判断ロジックを定義していない |

| 追加点検 | 結果 |
|---|---|
| JARVIS が承認を確定できる条項 | **なし**(P-2 / §4.2) |
| 沈黙・無応答が承認とみなされる条項 | **なし**(`EXPIRED` は承認ではない) |
| `system` actor が承認しうる経路 | **`EXPIRED` のみ**。`APPROVED` へは到達不可 |
| 既存データを書き換える設計 | **なし**(§4.4 / §5.1) |

**本点検は起草者による自己申告であり、検証の代替にならない。** 検証は HG-H09。

---

## 8. 本文書が決めないこと

| # | 事項 | 理由 |
|---|---|---|
| N-1 | 既存 HG-1〜HG-5 の統合・改修 | 博士方針「既存システムの全面改修は禁止」 |
| N-2 | 既存データの移行・補完 | 禁止事項 |
| N-3 | 2ストア乖離(F-1 / F-2)の是正 | 是正は別 Decision。本文書は Finding の固定まで |
| N-4 | U-30〜U-37 の解消 | Unknown 保持指示 |
| N-5 | HAB-C / HAB-D の帰属 | HG-J03 裁定待ち。**先取りしない** |
| N-6 | 実装(スキーマ作成・コード) | 本文書は定義のみ |
| N-7 | `HOLD` の扱い / `EXPIRED` 期限条件 / `NEW` の対応 / `split` の扱い / `WAITING_FOR_HUMAN_GATE` の対応 / HG-3 の mapping / `evidence_hash` 仕様 / 記録先 | いずれも §10 の裁定事項 |

---

## 9. 完了条件チェック

| # | 完了条件(博士指示) | 該当章 | 状態 |
|---|---|---|---|
| 1 | **Canonical State Definition** | §2 | ✔ 記載。ただし `HOLD` 不在(§2.4)と `EXPIRED` 期限条件が【未確定】 |
| 2 | **Existing State Mapping** | §3 | ✔ 記載。HG-2 `NEW` / HG-4 `split` / HG-5 `WAITING_FOR_HUMAN_GATE` / HG-3 全体は【未確定】として明示 |
| 3 | **Actor Model Definition** | §4 | ✔ 記載。7必須フィールド + `actor_type` 6値 + 遡及禁止 |
| 4 | **Transition Ledger Schema** | §5 | ✔ 記載。`evidence_hash` 仕様と記録先は【未確定】 |
| 5 | **JARVIS Authority Boundary Document** | §6 | ✔ 記載。許可4 / 禁止4(博士提示)+ 派生禁止5 |
| 追加 | HG-J04 Evidence Record 保存 | §1 | ✔ F-1 / F-2 / F-3 を固定、U-30〜U-37 を Unknown 保持 |

**【未確定】を残したまま「完了」としている。**
これは条件未達ではなく、**確定させると裁定を先取りするため意図的に空欄としたもの**である。
該当箇所はすべて §10 に提示した。

---

## 10. Human Gate 提示事項

**本章は `decision` フィールドを含まない。**

| ID | 判断事項 | 関連 |
|---|---|---|
| **HG-H01** | `HOLD` を canonical state に追加するか / 操作とみなすか / `DEFERRED` に統合するか | §2.4 |
| **HG-H02** | `EXPIRED` の期限条件 | §2.1 |
| **HG-H03** | HG-2 の `NEW` が canonical のどれに対応するか | §3.2 |
| **HG-H04** | HG-4(collision 裁定)を canonical state 体系に含めるか。`split` の扱い | §3.3 |
| **HG-H05** | HG-5 `WAITING_FOR_HUMAN_GATE` の canonical 対応(U-31) | §3.4 |
| **HG-H06** | HG-3 の記録先(U-33)と mapping の要否 | §3.5 |
| **HG-H07** | `evidence_hash` の対象範囲とアルゴリズム。既存 `event_signatures` 連鎖との関係 | §5.4 |
| **HG-H08** | Decision Transition Ledger の記録先(新設 / 既存台帳への追加) | §5.5 |
| **HG-H09** | §7 自己点検表の検証 | §7 |
| **HG-H10** | 本文書の Status を DRAFT から変更するか / Decision Ledger 登録の単位 | 全体 |

**依存関係【観測】:** HG-H01 は §2 の canonical state 自体を変える可能性があり、
確定すると §3 の mapping と §5 の `action` enum に波及する。

---

## Knowledge Lineage

**Document:** HAB_CORE_DEFINITION_v0.1.md
**Status:** DRAFT(未裁定、Decision Ledger 未登録、実装なし)
**Created:** 2026-08-04
**Origin:** きむら博士指示「JARVIS化を安全に進めるため、Human Authority Boundary(HAB)の最小実装を先行する。Phase 1: HAB Core Definition 作成」
**Parent Documents:**
- `docs/governance/mocka_hab_v1_contract.md`(HAB-A、DRAFT)
- `docs/governance/mocka_hab_human_gate_relation_v1.md`
- `docs/governance/mocka_human_gate_decision_definition_v1.md`
- `docs/governance/JARVIS_HGJ04_EVIDENCE_M1_M2_M3_v0.1.md`(F-1〜F-3 の一次証拠)
- `docs/governance/JARVIS_CONSTITUTION_DRAFT.md`(§3 権限境界)
- `docs/governance/JARVIS_HGJ03_EVIDENCE_COMPLETE_v0.1.md`(§0.4 HAB の語の特定)
**Referenced Decisions:** `DC_20260725_003`(Canonical Ledger 経路)/ `DC_20260730_009`(Evidence Supremacy)/
`DC_20260801_002`(HG-1 自動修復禁止)/ `PHI_OS_CONSTITUTION_v1.md`(原則1・§3.2・§5.5)
**Affected Components:** なし(コード・スキーマ・データのいずれも変更していない)
**Revision History:**
- R1(2026-08-04): 新規作成。Canonical State / Existing Mapping / Actor Model /
  Transition Ledger Schema / JARVIS Authority Boundary / HG-J04 Finding を記載。
  【観測】【博士提示】【起案】【未確定】を分離表記。実装・Decision Ledger 登録・データ変更なし。

# DP-1 State Boundary — Decision Ledger 登録準備資料 v0.1

**文書番号:** (未採番)
**作成日:** 2026-08-07
**工程:** DP-1 Decision Ledger 登録準備
**状態:** **登録実行済み — `DC_20260807_001` (2026-08-07T02:52:36Z)。登録後検証 全8項目 PASS。検証証跡 `E20260807_3096181546b72`**
**CHANGE_START:** E20260807_91442502442eb

**対象 Decision:** `docs/governance/DP1_STATE_BOUNDARY_DECISION_RECORD_DRAFT_v1.0.md` (Status: **DP-1: APPROVED**、commit 209081c)

---

## 0. 本資料の位置付け

### 0.1 何であり、何でないか

| | |
|---|---|
| **本資料である** | 承認済み DP-1 Decision を Decision Ledger へ登録するための、実行可能な準備一式 (前提条件の確認結果 / 正確な写像 / 登録手順 / 登録後の検証手順) |
| **本資料でない** | 登録の実行 / Seal 生成 / 実装指示 / Migration 計画 |

### 0.2 実施状況

| # | 事項 | 状況 |
|---|---|---|
| 1 | `mocka_decision_write` の実行 | **実行済み** (2026-08-07。`DC_20260807_001`。登録後検証 全8項目 PASS) |
| 2 | Seal 生成 | **未実施** |
| 3 | 実装変更 | **未実施** |
| 4 | 既存 Decision の supersede | **未実施** (登録レコードの `supersedes` / `superseded_by` とも null であることを検証項目4で確認済み) |
| 5 | Migration 開始 | **未実施** |
| 6 | 追加設計判断 | **未実施** |
| 7 | Integrity Classification 起票 | **未実施** |
| 8 | A-1 の解決 | **未実施** (未解決状態を維持) |

**先例:** `HG-C10_DECISION_RECORD_v1.0.md` は `Status: APPROVED` かつ `Decision Ledger: 未登録 (登録は Human Authority の指示待ち)` の状態で存在する。承認と Ledger 登録は分離可能である。

---

## 1. 登録前提条件の確認結果

### 1.1 ツール可用性

| # | 確認項目 | 結果 |
|---|---|---|
| 1 | `mocka_decision_write` のセッション内可用性 | **確認済み** (2026-08-07、本セッション) |
| 2 | `mocka_decision_get` のセッション内可用性 | **確認済み** (登録後検証に使用) |
| 3 | MCP Tool Registry Drift の有無 | **Drift なし** (両ツールとも本セッションのツール一覧に存在) |
| 4 | `data/tic/mcp_schema_hash.json` によるセッション基準ハッシュ | **取得不能**。同ファイルは `.gitignore` の `data/tic/*` により Web 環境の clone に存在しない。IC_20260705_018 の hash ベース検知手順は本環境では実行できない |

### 1.2 スキーマ適合

`mocka_decision_write` の inputSchema に対する適合確認。

| フィールド | 必須 | 本登録での扱い |
|---|---|---|
| `title` | **必須** | 第2章に確定値 |
| `context` | **必須** | 第2章に確定値 |
| `alternatives` | **必須** (却下案が無い場合も `option: "N/A"` を1件入れる) | **3件を設定** (Rejected Alternatives) |
| `decision` | **必須** | 第2章に確定値 |
| `rationale` | **必須** | 第2章に確定値 |
| `impact` | **必須** | 第2章に確定値 |
| `approved_by` | **必須** | きむら博士 (Human Authority) |
| `decision_id` | 任意 | **省略** (自動採番 `DC_YYYYMMDD_NNN` に委ねる) |
| `related_documents` | 任意 | 3件を設定 |
| `related_events` | 任意 | 4件を設定 |
| `status` | 任意 (既定 `Active`) | `Active` |
| `supersedes` | 任意 | **フィールドごと省略する。** 本 Decision はいかなる既存 Decision も supersede しない (1.4 参照) |

### 1.3 Decision Ledger の現況

| # | 項目 | 観測値 (本セッション) |
|---|---|---|
| 1 | `mocka_decision_list` の返す件数 (decision_id 毎に最新行) | 203 |
| 2 | `current_view.recent_decisions.count` (jsonl 行数) | 210 |
| 3 | 差 | 7行 (同一 decision_id への追記行) |
| 4 | 観測時点の最新 decision_id | `DC_20260806_002` |
| 5 | `status` 分布 | Active 202 / Superseded 1 |

**採番の見込み:** `decision_id` を省略した場合、登録日の日付で `DC_YYYYMMDD_NNN` が自動採番される。**本資料は採番値を予測しない。** 実際の値は登録応答および第4章の読み戻しで確認する。

### 1.4 `supersedes` を設定しないことの確認

本 Decision は既存 Decision を supersede しない。対象 Decision の記載 (逐語):

> 本 Decision は `DC_20260712_008` を supersede しない。同 Decision の status は Active のまま維持され、その定める Memory Model (2層) は引き続き有効である。

> **本 Decision はこれらのいずれも supersede しない。**

したがって `supersedes` フィールドは**設定しない (省略する)**。

**留意:** 本セッションの監査で、Decision Ledger の supersede 関係について以下が観測されている。本登録は supersede を行わないため直接の影響を受けないが、記録しておく。

| # | 観測事実 |
|---|---|
| 1 | `superseded_by` は全203件で `null`。逆リンクが一度も書き込まれていない |
| 2 | `supersedes` を持つ13件のうち11件で、supersede 対象は `status: Active` のまま残存する |
| 3 | `DC_20260712_008` は `supersedes` の値が自分自身である (自己参照) |
| 4 | Decision Ledger 内で `supersedes` は、append-only 制約下での**訂正の記録手段**として使用されている (`DC_20260724_002` 逐語: "DC_20260724_001の判断を訂正する(append-only原則によりsupersedeとして新規記録)") |

### 1.5 既知リスク — Decision Ledger の文字化け事象 (TODO_423)

**登録前に必ず認識すべき既知の未解決事象がある。**

| 項目 | 内容 |
|---|---|
| TODO_423 | Decision Ledger 文字化け原因追跡 — decision write pipeline の文字列変化点特定 |
| status | **保留** (原因未確定) |
| 現象 | `decision_ledger.jsonl` に保存された内容が、意図した漢字と異なるコードポイントで記録される |
| 確定済みの事実 | (a) 表示環境の問題ではなく**保存データ自体が破損**している (b) `_append_decision()` 自体には文字変換処理がない (c) json.dumps 層・ファイル I/O 層は原因から除外済み (Phase A-1 / A-2) (d) **非決定的な事象**である |
| 観測されたコードポイント差異 | 際 U+969B -> U+969F (+4) / 陳 U+9673 -> U+9670 (-3) / 腐 U+8150 -> U+8155 (+5)。いずれも下位ニブルのみの変化 |
| 未確定 | 発生レイヤー (文字列生成時 / write 時 / 中間処理 / Unicode正規化 / encoding指定ミス等)。UTF-8 バイト列レベルでの差異は未確認 |
| 保留理由 (note より) | Phase A-3 (write 直前・保存直後のハッシュ取得による差分検知の仕組み設計) は品質向上系であり緊急性なしと判断。原因未確定・監視待ちの状態で保留 |

**本登録への含意:** 本 Decision のペイロードは日本語の長文を多数含む。**登録が成功応答を返したことをもって内容が正しく保存されたとみなしてはならない。** 第4章の登録後検証において、**文字列レベルの完全一致照合**を必須手順とする。

---

## 2. `mocka_decision_write` への写像 (確定値)

以下は登録時に渡す値である。**本資料はこれを実行しない。**

### 2.1 `title`

```
DP-1 State Boundary Decision: JARVIS Institutional Runtime における
State Layer / Event Store / Human Authority Boundary の境界定義
(Runtime State Reconstruction Model の確立)
```

### 2.2 `context`

```
JARVIS の層原則は phi_os/hab/JARVIS_OPERATING_RULES_v0.1.md により
"JARVIS is an intelligence layer. Human Gate is an authority layer."
として既に確定している。JARVIS が Allowed 事項の一つである
Explain system state を担うためには、何が State であるかが確定している
必要がある。上位方針 (HAB_CORE_DEFINITION_v0.1.md 0.1、きむら博士) は
"既存システムの全面改修は禁止。まず制度境界を固定し、その後 JARVIS
能力を拡張する" である。

DP-1 着手前の時点で、State に関する記述が位格の異なる複数の文書に
分散していた。DC_20260712_008 (Active) は Event を Observation Layer に
分類し単独では load-bearing 記録として扱わないと定める一方、
minimal_safe_architecture_v1.md (PROPOSED、Decision Ledger 参照0件) は
同じ event_store を STATE LAYER の source of truth と記述していた。
Human Gate についても、JARVIS_OPERATING_RULES_v0.1.md が authority layer
と規定する一方、DC_20260705_008 (Active) が State Management Layer と
定義していた。

加えて、State 関連の実体7件のうち、層への割当に単一かつ確定的な根拠を
持つものは Decision Ledger の1件のみであった。runtime/state.json には
互換性のない2つの書込元が同一パスに存在し (runtime/action_selector.py と
scripts/state/state_engine.py)、最終更新は 2026-04-05 で停止している。
current_view の永続先 data/MOCKA_OVERVIEW_CURRENT.json は生成されていない。
Context Snapshot は層への割当の根拠文書を確認できない。

また VOCABULARY_AUDIT_EVALUATION_v0.1.md:171 は、憲法原則5 と Ledger
4候補の並立について "文書上明示的に解消されていない緊張がある" と
既に記録している。

DP-2 (Snapshot 定義) および DP-3 (Delta 定義) は DP-1 に依存するため、
DP-1 未確定のまま後続を進められない。
```

### 2.3 `decision`

```
DP-1-A: State は Event history の fold 型として定義する。Runtime に
おける State は Event history を畳み込んだ結果として導出され、独立に
保持される第一級の実体ではない。

DP-1-B: Event Store (data/mocka_events.db) は State Layer の Primary
Source である。

DP-1-C: Human Gate は Authority Layer に属し、State Management は
Execution Layer に属する。両者は別層とし、同一層として扱わない。

DC_20260712_008 との関係: DC_20260712_008 は既存 Memory Governance
Model として維持する (status は Active のまま)。本 Decision は
DC_20260712_008 を supersede しない。本 Decision は Runtime State
Reconstruction Model として別軸を定めるものであり、同一対象 (Event)
について、Memory Governance Model 軸における Observation Layer 分類と、
Runtime State Reconstruction Model 軸における Primary Source 指定は
併存する。DC_20260712_008 が定める Durable Layer 対象4件、Observation
から Durable への昇格4条件、昇格には別途 Human Gate Decision を要する
規定、status:ok の定義、制度記憶採用条件の3点セットは、いずれも本
Decision によって変更されない。

DC_20260705_008 / DC_20260705_009 との関係: 両者を維持する。本 Decision
の DP-1-C は、DC_20260705_008 が定める3つの責務分離を Authority と
Execution の層境界として明示するものであり、phi_os/human_gate.py の
モジュール分割を意味しない。

未解決事項として保持: Decision Statement における Execution Layer と
Architecture Boundary における Action Layer の対応関係 (A-1)。本
Decision の採択は A-1 の解決を前提としない。
```

### 2.4 `rationale`

```
1. 憲法原則5 (Event history is the single source of truth) および
憲法原則1 (Event ledger is append only) と、Runtime State を fold 型と
する定義は整合する。State を導出結果として扱うため、状態変更が
append-only の記録を経由しない経路が発生しない。

2. Event Store は既に単一書込経路 (phi_os/event_gate.process_event()、
TODO_322) を持つ。State Layer の Primary Source として、代替候補の中で
唯一、書込経路が制度的に確定している。

3. DC_20260712_008 との2軸分離は、MoCKA において先例のある形式である。
TODO_385 は status (タスク進行度) と contract_status (契約ライフサイクル
状態) を異なる軸として別 enum に分離しており、同一対象について複数の
軸上の位置を併存させる構成は既に制度内に存在する。

4. DP-1-C の二層分離は、DC_20260705_008 が既に確定している3つの責務分離
((1) 自動検知系は PENDING 投入のみで可否判断に関与しない (2) Human Gate
は受付窓口としてのみ機能し判断・自動応答を行わない (3) approve()/reject()
は人間操作のみ) を、層構造上に表現するものである。同一層化した場合、この
分離が層構造に表現されない。同型の先例として DC_20260731_005 が INC に
ついて進行軸 (機械) と承認軸 (人間のみ) の2軸モデルを採用している。
```

### 2.5 `impact`

```
本 Decision は Architecture Definition であり、実装変更を直接許可しない。
以下はいずれも本 Decision の採択によって許可されない: コードの変更 /
スキーマの変更 / データの変更・移行 / モジュールの分割・統合 /
runtime/state.json の書込元競合の解消 / current_view の永続化の開始 /
fold の実装 / _STATE_COLUMNS の運用開始。

Migration Plan は別 Decision の対象とする。本 Decision は Migration の
開始を許可しない。

実装着手前に確認を要する既知の事実 (別 Decision の入力として記録):
(1) fold の実装は存在しない。phi_os/event_replay.py の replay() は
what_type によるグループ化であり状態を縮約する畳み込みではない
(2) _STATE_COLUMNS のうち change_type / impact_scope / impact_result は
標本200件で使用実績ゼロ。before_state は194件 (97.0%) が null
(3) 標本は claude_mcp が181件 (90.5%) を占め、DB全体 19,360件 (25型) に
対する代表性はない
(4) runtime/state.json に互換性のない2つの書込元が存在する
(5) current_view の永続先 data/MOCKA_OVERVIEW_CURRENT.json は
生成されていない
(6) Decision Ledger の現在有効な決定集合を機械的に導出する経路は現状
存在しない (superseded_by が全203件 null、supersede 対象13件中11件が
Active のまま)
(7) registry_store (KN-004) の実体はリポジトリ外

裁定範囲外として保持される事項: A-1 (Execution Layer と Action Layer の
対応関係、未解決事項として保持) / A-2 (層名 Memory Layer と既存
MEMORY_LAYER.md の関係) / A-3 (層名 State Layer と既存2用法の関係) /
A-4 (INSTITUTION_RUNTIME_v1.md の authority_manager.py との関係) /
A-5 (current_view / runtime/state.json / Context Snapshot の位置) /
A-6 (分類B 5件の処遇) / A-7 (HAB_CORE_DEFINITION_v0.1.md の Canonical
State との関係)。

DP-2 (Snapshot 定義) および DP-3 (Delta 定義) は本 Decision の確定を
前提として着手可能になる。
```

### 2.6 `alternatives` (3件)

**第1件**

```
option:
  State を可変 DB として保持する方式

rejected_reason:
  憲法原則1 (Event ledger is append only) の下では、可変ストアを State の
  保持先とする方式は、状態の変更が append-only の記録を経由しない経路を
  生じさせる。採用された fold 型は状態を導出結果として扱うためこの経路が
  発生しない。可変ストア方式の実例である runtime/state.json は、同一パスに
  互換性のない2つの書込元が存在し、最終更新が 2026-04-05 で停止している。
  また working_memory.json 破損インシデント (State Cache Corruption) に
  対する事後対応として 2026-06-22 から 06-23 に5件の PROPOSED 文書が
  作成されている。
```

**第2件**

```
option:
  Event Store を Observation Layer に限定する方式
  (Runtime State Reconstruction Model の軸における候補)

rejected_reason:
  本方式では State Layer の Primary Source を別に定める必要が生じるが、
  State を保持する実体7件のうち層への割当に単一かつ確定的な根拠を持つ
  ものは Decision Ledger の1件のみであり、Event Store に代わる Primary
  Source の候補が確定していない。採用された方式は、既に単一書込経路
  (phi_os/event_gate.process_event()) を持つ Event Store を Primary
  Source とする。
  適用範囲の明示: 本項の不採用は Runtime State Reconstruction Model の
  軸における候補に対するものである。DC_20260712_008 が Memory Governance
  Model の軸において Event を Observation Layer に分類することは本
  Decision によって維持されており、本項はこれを対象としない。
```

**第3件**

```
option:
  Human Gate と State Management を同一層化する方式

rejected_reason:
  DC_20260705_008 (Active) は Human Gate について3つの責務分離を既に
  定めている。同一層化した場合、この分離が層構造上に表現されない。
  採用された二層分離は、既に確定している責務分離を層境界として明示する
  ものである。同型の先例として DC_20260731_005 (Active) が INC について
  進行軸 (機械が進める) と承認軸 (人間のみが進める) の2軸モデルを
  採用している。
```

### 2.7 `approved_by`

```
きむら博士 (Human Authority)
```

### 2.8 `related_documents`

```
[
  "docs/governance/DP1_STATE_BOUNDARY_DECISION_RECORD_DRAFT_v1.0.md",
  "docs/governance/DP1_STATE_BOUNDARY_DECISION_DRAFT_v0.1.md",
  "docs/governance/DP1_STATE_BOUNDARY_ADJUDICATION_PREP_v0.1.md"
]
```

### 2.9 `related_events`

```
[
  "E20260807_8023474020011",
  "E20260807_9775174934c0b",
  "E20260807_593034273be7c",
  "E20260807_91442502442eb"
]
```

### 2.10 `status`

```
Active
```

### 2.11 設定しないフィールド

| フィールド | 理由 |
|---|---|
| `decision_id` | 省略し、自動採番 (`DC_YYYYMMDD_NNN`) に委ねる |
| `supersedes` | **フィールドごと省略する。** 本 Decision はいかなる既存 Decision も supersede しない (1.4) |

---

## 3. 登録手順

**以下は Human Authority の実行指示があった場合の手順である。本資料の作成時点では実行していない。**

| # | 手順 |
|---|---|
| 1 | `mocka_decision_write` の可用性を再確認する (MCP Tool Registry Drift 対策。不在の場合は CLAUDE.md の Drift 対応方針に従い、再試行は1回のみとし、以降は Incident 化してセッション内の再確認を行わない) |
| 2 | 第2章の確定値を `mocka_decision_write` へ渡す。`decision_id` と `supersedes` は渡さない |
| 3 | 応答から採番された `decision_id` を取得する |
| 4 | **第4章の登録後検証を実施する** |
| 5 | 検証結果を `mocka_write_event` で記録する |
| 6 | 採番された `decision_id` を `DP1_STATE_BOUNDARY_DECISION_RECORD_DRAFT_v1.0.md` 第7.1章に反映し、`Decision Ledger` の記載を `未登録` から更新する |

---

## 4. 登録後の検証手順

CLAUDE.md の実行証跡の定義 (書込操作の成立条件) に基づく。

> 書込系ツールが `{"status":"ok"}` を返したことだけをもって、その変更が成立したとみなしてはならない。

さらに TODO_423 (1.5) により、**存在確認だけでは不十分である。**

### 4.1 必須検証項目

| # | 検証 | 手段 | 合格条件 |
|---|---|---|---|
| 1 | レコードの存在 | `mocka_decision_get(decision_id)` | レコードが返る |
| 2 | `decision_id` の一致 | 同上 | 登録応答の値と一致 |
| 3 | `status` | 同上 | `Active` |
| 4 | `supersedes` | 同上 | `null` または不在 (**値が入っていたら異常**) |
| 5 | `approved_by` | 同上 | 第2.7章の値と一致 |
| 6 | `alternatives` の件数 | 同上 | **3件** |
| 7 | **本文の文字列完全一致 (TODO_423 対策)** | `mocka_decision_get` の戻り値と第2章の確定値を**文字単位で照合** | `title` / `context` / `decision` / `rationale` / `impact` / `alternatives` の各文字列が完全一致 |
| 8 | `related_documents` / `related_events` | 同上 | 各3件 / 4件が一致 |

### 4.2 検証項目7の実施方法

TODO_423 の現象はコードポイントの下位ニブルのみが変化する非決定的なものであり、目視では検出できない。**プログラムによる文字列比較を行う。**

```
1. 第2章の確定値を Python 文字列として保持する
2. mocka_decision_get の戻り値の該当フィールドを取得する
3. 両者を == で比較する
4. 不一致の場合、差分位置と両者のコードポイントを記録する
   (例: 位置 N, 意図 U+969B, 保存 U+969F)
5. 不一致が1文字でもあれば検証を FAIL とする
```

### 4.3 検証失敗時の扱い

| 状況 | 対応 |
|---|---|
| 検証項目1から6のいずれかが不合格 | 登録が成立していない。`mocka_write_event` で記録し、Human Authority へ報告する。**再登録は Human Authority の指示を待つ** (append-only のため、誤登録の削除はできない) |
| **検証項目7が不合格 (文字化け検出)** | TODO_423 の再現である。`mocka_write_event` で記録し、**TODO_423 の Phase A-3 (write 直前・保存直後のハッシュ取得による差分検知) の入力証拠として保存する。** 訂正は append-only 原則に従い supersede による新規記録で行うが、その実施可否は Human Authority の判断による |
| 検証が実施できない (ツール不在等) | CLAUDE.md の MCP Tool Registry Drift 対応方針に従う。**別経路での書込による代替は行わない** |

---

## 5. 登録に含めないもの

| # | 対象 | 理由 |
|---|---|---|
| 1 | Seal 生成 (`mocka_seal`) | 本工程の対象外。`DC_20260713_003` の AUTO_SEAL Model B に従い、Seal は承認済み Decision 発行後の別工程 |
| 2 | Integrity Classification 起票 | 本工程の対象外 |
| 3 | 既存 Decision の supersede | 本 Decision は supersede しない (1.4) |
| 4 | 実装変更 | 対象 Decision 第6章により禁止 |
| 5 | Migration の開始 | 別 Decision 対象 |
| 6 | A-1 の解決 | 承認時の指示により未解決事項として保持 |
| 7 | A-2 から A-7 の解決 | 裁定範囲外 |

---

## 6. 実行承認欄

```
登録実行の指示:  きむら博士 (Human Authority)

指示日時:        2026-08-07

採番された decision_id: DC_20260807_001
   登録応答:     status=ok / event_id=E20260807_15808415664e1
   Ledger 記録:  approved_at=2026-08-07T02:52:36Z (UTC、サーバ自動付与)
                 status=Active / supersedes=null / superseded_by=null

登録後検証の結果 (第4章):
   項目1 レコード存在        : PASS
   項目2 decision_id 一致    : PASS  (DC_20260807_001)
   項目3 status = Active     : PASS
   項目4 supersedes 不在     : PASS  (supersedes / superseded_by とも null)
   項目5 approved_by 一致    : PASS  (len 23/23, sha 1e4194bb5fcdef65)
   項目6 alternatives 3件    : PASS
   項目7 本文文字列完全一致  : PASS  <- TODO_423 対策 (必須)
   項目8 related_* 件数一致  : PASS  (documents 3件 / events 4件)

   総合判定: PASS -- 登録成功として扱う

検証実施者:      くろこ (Claude Code, Claude-opus-5)
検証日時:        2026-08-07T02:55:09Z (UTC)
検証証跡:        E20260807_3096181546b72
```

### 6.1 検証項目7 の詳細 (送信長/保存長、SHA-256 先頭16。いずれも一致)

| フィールド | 長さ | SHA-256 (先頭16) |
|---|---|---|
| `title` | 163 / 163 | `2ef5f8047658f34f` |
| `context` | 1203 / 1203 | `e8f131808644e920` |
| `decision` | 1120 / 1120 | `8bc96d3a7684e159` |
| `rationale` | 769 / 769 | `2c8381689e6df55e` |
| `impact` | 1295 / 1295 | `c269287ae6feaf35` |
| `alt1.option` | 22 / 22 | `bb84a5336b0dd246` |
| `alt1.rejected_reason` | 343 / 343 | `e5c55fa0bf4f9275` |
| `alt2.option` | 85 / 85 | `c5421f15f17c2fd6` |
| `alt2.rejected_reason` | 443 / 443 | `9ce668bdd7077ab7` |
| `alt3.option` | 39 / 39 | `4e2e12a3ed3374f3` |
| `alt3.rejected_reason` | 216 / 216 | `7accbd8f4b01319e` |

**TODO_423 の再現:** 検出されなかった。全11文字列でコードポイントレベルの差異ゼロ。本結果は TODO_423 Phase A-3 (write 直前・保存直後のハッシュ取得による差分検知) の観測データ1件として利用可能である。

### 6.2 ペイロード生成方法 (転記ドリフト対策)

第2章のコードブロックから機械的に抽出し JSON 化した上で送信した。`title` のみ、本資料内の折返し3行を半角スペースで連結して1行へ正規化している (Decision Ledger の既存 title が単一行であるため)。他フィールドは本資料の記載どおり。

---

## 7. 本資料の限界

1. 本資料は Claude Code Web 環境から作成された。リポジトリの clone は shallow (直近24時間) である。
2. `data/decisions/decision_ledger.jsonl` は本環境に不在であり、Decision Ledger の観測は MCP 応答を経由した間接観測である。**第4章の検証項目7 (文字列完全一致) も MCP 応答に対する照合であり、jsonl 実体に対する照合ではない。** TODO_423 の現象が MCP 応答層より下で発生する場合、本検証では検出できない可能性がある。
3. `data/tic/mcp_schema_hash.json` が本環境に存在しないため、MCP schema drift のセッション基準ハッシュを取得できていない (1.1)。
4. 第1.3章の Decision Ledger 現況は本セッション観測時点の値であり、登録実行時点の値とは異なりうる。
5. 本資料は `mocka_decision_write` を実行していない。

---

## 8. 参照

### 8.1 対象 Decision

`docs/governance/DP1_STATE_BOUNDARY_DECISION_RECORD_DRAFT_v1.0.md` (Status: DP-1: APPROVED)

### 8.2 維持される Active Decision

`DC_20260712_008` / `DC_20260705_008` / `DC_20260705_009` / `DC_20260731_003` / `DC_20260731_005` / `DC_20260713_003` / `DC_20260712_005` / `DC_20260724_008` / `DC_20260730_009`

### 8.3 既知リスク

`TODO_423` (Decision Ledger 文字化け原因追跡、status: 保留、原因未確定、非決定的事象) — Phase A-1 は `DC_20260707_012`、Phase A-2 は `DC_20260707_014` で完了。Phase A-3 は未着手

### 8.4 制度規約

CLAUDE.md の実行証跡の定義 (書込操作の成立条件) / CLAUDE.md の MCP Tool Registry Drift 対応方針 (IC_20260705_018) / CLAUDE.md の Decision Ledger への記録義務 (TODO_361)

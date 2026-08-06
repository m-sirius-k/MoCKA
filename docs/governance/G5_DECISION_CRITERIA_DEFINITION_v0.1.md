# G-5 Decision Criteria Definition v0.1

## Human Gate 正典候補を評価するための判断基準

**文書番号:** EBGA-G5-CRIT-001
**作成日:** 2026-08-06

> **R2 注記 (2026-08-06、追記のみ。本文は不変更):**
> 本版の発行後、**HG-C03 がきむら博士により裁定された** (評価粒度 = 系統単位 / 検証粒度 = 経路単位 /
> 評価結果と検証結果は独立記録)。裁定を反映した版は
> **`G5_DECISION_CRITERIA_DEFINITION_v0.2.md`** である。
> 本 v0.1 は **裁定前の状態を保存する版**として残す。Criterion 2 の判定単位について引用する場合は v0.2 を参照すること。
> HG-C01 / C02 / C04 / C05 / C06 / C07 は v0.2 でも未裁定のままである。
**工程:** Phase B-2 (Gate 2 Execution Authority Boundary Decision の準備工程)
**状態:** 判断基準の定義のみ。**適用なし / 裁定なし / Decision Ledger 登録なし / 実装なし**

---

## 0. 本工程の位置付け

### 0.1 上位からの接続 (Confirmed)

`DC_20260805_001` (Gate 1 Rule Boundary Decision, External Reference: `DEC-EBGA-20260805-G1`,
approved_by NSJP kimura / 2026-08-05T10:01:43Z, status Active) は次の2点を確定している。

| 項目 | 内容 |
|---|---|
| 未解消 Unknown | 23件保持 (解消0)。うち **G-5 = Human Gate 接続先が5系統並存** |
| 次工程 | Gate 2 Execution Authority Boundary Decision。優先順位: **G-5 Human Gate 接続先** / Q-5 Actor Identity Normalization / Q-6 Multi Boundary Interceptor Model |
| 状態拘束 | Design Freeze ACTIVE / Implementation STOP (LOCKED 維持) |

本文書は、その G-5 について **正典候補を評価するための判断基準** を定義するものである。

### 0.2 本工程が答える問い

- 答える問い: **Human Gate と呼ぶために最低限満たす制度条件は何か**
- 答えない問い: Human Gate を何にするか (正典候補の決定)

### 0.3 本工程で実施しないこと (きむら博士指示による制約)

以下はいずれも本文書の範囲外であり、本文書は一切これを行っていない。

1. 正典候補の決定
2. Human Gate 仕様変更
3. コード変更
4. Decision Ledger 登録
5. Q-5 (Actor Identity Normalization) の確定
6. Q-6 (Multi Boundary Interceptor Model) の確定

加えて、本文書は **評価結果を生成しない**。HG-1 から HG-5 への Criterion 適用は次工程 (0.5 参照) である。

### 0.4 基準の出所

Criterion 1 から Criterion 5、およびその評価目的・確認項目は **きむら博士 (Human Authority) が提示したもの** である。
本文書はそれを評価可能な形へ固定する作業であり、**基準の新規追加・削除・優先順位付けは行っていない**。
本文書がラベル `[起案]` を付した箇所のみが、くろこが判定を実行可能にするために補った未裁定の定義である。

### 0.5 本定義後に実施する範囲 (次工程、本文書では未実施)

1. HG-1 から HG-5 の各候補へ Criterion 1 から 5 を適用
2. 比較表 (5候補 x 5基準) の作成
3. 不足証拠の確認
4. G-5 Decision Criteria Report の作成

---

## 1. 表記ラベル

本文書は次の4ラベルで記述の性質を分離する。引用時にこの区別を潰さないこと。

| ラベル | 意味 |
|---|---|
| `[Confirmed]` | 一次データ (コード実測 / DB実測 / Decision Ledger / 既存文書) で確認済みの事実 |
| `[継承]` | 既に Active または RATIFIED である確定事項からの引き写し。本工程で再決定しない |
| `[起案]` | 本文書での新規定義。**未裁定**。Human Gate 裁定を要する |
| `[Unknown]` | 未確定として保持する。推測で埋めない |

---

## 2. 評価対象の識別子固定

### 2.1 HG-1 から HG-5 の定義 `[Confirmed]`

本評価における HG-1 から HG-5 は、`docs/governance/JARVIS_HGJ04_EVIDENCE_M1_M2_M3_v0.1.md`
(文書番号 JARVIS-HGJ04-EV-001) 第1章の定義を用いる。値は同文書からの引き写しである。

| # | 実体 | 状態記録先 | 状態語彙 |
|---|---|---|---|
| HG-1 | `phi_os/human_gate.py` | `mocka_events.db` の `human_gate_events` テーブル | PENDING / APPROVED / REJECTED / EXPIRED / CANCELED |
| HG-2 | `app.py` `/decision/approve` `/decision/reject` | `data/prevention_queue.json` | NEW / approved / rejected |
| HG-3 | `governance/mocka_git_safe_commit.py` の Core System File 除外 | git 作業ツリー (未コミット状態として保持) | 状態語彙なし (コミット有無) |
| HG-4 | `semantic/query_engine/human_gate.py` | インメモリ (`HumanGateRulingStore._records: list`)。永続化なし | accept / reject / defer / split |
| HG-5 | `governance/human_gate_continuity.py` | `data/decisions/pending_decision_units.jsonl` | WAITING_FOR_HUMAN_GATE のみ |

### 2.2 識別子 `HG-n` の多義性 `[Confirmed]`

同じ `HG-n` 表記が、現在少なくとも3つの別体系で使われている。**混同すると評価対象が入れ替わる。**

| 体系 | 出典 | 指すもの |
|---|---|---|
| 本評価の HG-1..HG-5 | JARVIS-HGJ04-EV-001 第1章 | Human Gate 実装の5系統 |
| HG-1 / HG-3 / HG-4 | `DC_20260801_002` | Decision Identity の制度判断項目 (HG-1 = COLLISION 自動修復禁止 等) |
| HG-J01..HG-J09 | `docs/governance/JARVIS_CONSTITUTION_DRAFT.md` 第9章 | JARVIS Constitution の Human Gate 提示事項 |

本文書内で修飾なしに `HG-1` と書いた場合は、常に 2.1 の定義 (`phi_os/human_gate.py`) を指す。

### 2.3 TTY Guard の所在 `[Confirmed]`

きむら博士の指示文中の「HG-1 TTY Guard」について、実測により所在を確定した。

| 項目 | 実測 |
|---|---|
| Guard の実体 | `governance/human_gate_cli.py:36-40` の `_require_tty()` (`sys.stdin.isatty()` が偽なら `sys.exit(1)`) |
| 適用範囲 | `approve` / `reject` サブコマンドのみ (`cmd_approve` / `cmd_reject` の先頭で呼ぶ) |
| HG-1 との関係 | 同ファイル 33行が `from phi_os.human_gate import submit, approve, reject, get_state, list_pending` を実行する。すなわち **HG-1 のバックエンドに対する CLI 入口であり、HG-1 とは別実体の front-end である** |
| 帰結 | Guard は `phi_os/human_gate.py` 自体ではなく **CLI 経路上に存在する**。同バックエンドを Python から直接 import する経路には TTY 判定が存在しない |

この事実は、Criterion 2 の判定を **系統単位ではなく経路単位で行う必要がある** ことの根拠になる (4.2.4 参照)。
なお本項は所在の確定のみであり、**HG-1 の適合判定ではない**。

---

## 3. 継承する既存確定事項 `[継承]`

以下は既に確定済みであり、本工程で再定義・再決定しない。Criterion はこれらと整合する形で定義する。

| # | 事項 | 出典 |
|---|---|---|
| I-1 | Event ledger is append only。いかなる主体も既存 Event を変更・削除できない | 憲法原則1 (`MOCKA_OVERVIEW.json` constitution) |
| I-2 | Custodian Operation Boundary = **Append 管理のみ** (G-10 Selection A) | `DC_20260805_001` |
| I-3 | Rule Owner = Human Authority / Rule Custodian = HAB (C2-01) | `DC_20260805_001` |
| I-4 | Rule 制定 = Human Authority / Detection = Invariant Evaluator / Execution = Runtime Enforcement Gateway の分離 (C2-02) | `DC_20260805_001` |
| I-5 | Enforcement Point は Integrity Ledger 管理 (C2-03) | `DC_20260805_001` |
| I-6 | Validation Layer は独立 Authority Layer (G-9 Selection B) | `DC_20260805_001` |
| I-7 | Enforcement は Human 承認済み Allow も実行可能 (G-11 Selection B)。ただし INV-2.8 = 承認済み許可を執行できるが許可権限を生成できない | `DC_20260805_001` |
| I-8 | 裁定 (採用/却下/保留) が確定した時点で Decision Ledger へ記録する義務 | TODO_361 / `.claude/CLAUDE.md` |
| I-9 | Human Gate は Core (評価のみ) と Finalization (きむら博士専権) の2層に分離される | `PHI_OS_CONSTITUTION_v1.md` 系 / JARVIS Constitution Draft 第2章 |

### 3.1 自動裁定化リスクに対する本文書の自己拘束 `[起案]`

本文書が定義する判断基準は **評価のみを生成し、承認を確定しない**。

- Criterion の PASS は「Human Gate として認定される」ことを意味しない。**正典採用は Human Authority の裁定事項である**
- 本基準に閾値を設けて自動的に正典を決定する条項を、本文書は持たない
- 本基準の適用結果を根拠に、くろこが Human Gate 仕様・コード・Ledger を変更することはない

---

## 4. 判断基準の定義

### 4.0 共通判定語彙 `[起案]`

各 Criterion の判定は次の4値で表す。

| 判定 | 定義 |
|---|---|
| PASS | 確認項目のすべてについて、一次証拠により要求を満たすことが確認できた |
| CONDITIONAL | 確認項目の一部を満たすが、限定条件 (特定の経路のみ / 特定の操作のみ 等) が付く。限定条件を明記する |
| FAIL | 一次証拠により、要求を満たさないことが確認できた |
| UNKNOWN | 判定に必要な証拠が現存しない。**FAIL とは区別する** |

**UNKNOWN と FAIL を区別する理由:** 証拠の不在は不適合の証明ではない。
両者を混同すると、記録が存在しないだけの候補を「不適合」と誤って確定させる。
UNKNOWN は解消されるまで Unknown として保持し、推測で FAIL または PASS に寄せない。

---

### 4.1 Criterion 1: Human Authority 証明可能性

#### 4.1.1 評価目的 (博士提示)

単に操作履歴が残ることではなく、**Authority 主体を再現可能にすること**。

#### 4.1.2 確認項目と要求 (博士提示)

| 項目 | 要求 |
|---|---|
| Actor Identity | 誰が操作したか識別可能 |
| Authority Basis | どの権限・資格で実行したか説明可能 |
| Action Trace | 何を実行したか再現可能 |
| Evidence Link | 証拠への接続が可能 |

#### 4.1.3 判定条件 (博士提示)

**操作者と承認権限者の同一性または関係性を説明できること。**

#### 4.1.4 証拠要件 `[起案]`

各候補について、次の4点を一次証拠 (スキーマ実測 / コード行 / 実データ) で示すこと。

1. **Actor が保持されるフィールド**: 記録スキーマ上のどの列・キーに actor が保持されるか。列が存在しない場合は「列なし」を実測で示す
2. **Actor 値の出所**: その値が (a) 実行者の検証結果か (b) 呼出側が渡した任意値か (c) コード内固定値か。コード行を示す
3. **Action Trace の再現単位**: 何が実行されたかを事後に特定できる記録が、要求単位 (request_id 等) で残るか
4. **Evidence Link**: 承認記録から対象 (Decision / commit / state 変更) へ到達する参照が記録側に存在するか

#### 4.1.5 参考となる既存実測 `[Confirmed]`

以下は既に判明している実測値であり、次工程の評価が **再確認すべき起点** である (判定そのものではない)。

- `human_gate_events` テーブルの列は `event_id / timestamp / type / action / request_id / payload / previous_state / next_state` の8列。**`actor` 列は存在しない** (`DC_20260805_001` の G-6 と一致)
- 同テーブルの action 分布は `submit` 1,774件 / `approve` 5件。`reject` / `expire` / `cancel` は 0件
- `app.py` の `/decision/approve` は Event に `who_actor="kimura_hakase"` を **コード内固定値として** 記録する (JARVIS-HGJ04-EV-001 第2章)

#### 4.1.6 判定不能条件 `[起案]`

actor の出所が (a) 検証結果か (b) 任意値か (c) 固定値かをコード上で特定できない場合は、UNKNOWN とする。

#### 4.1.7 本 Criterion が決定しないこと

- Actor Identity の正規化方式 (= Q-5)。本 Criterion は「識別可能か」を評価するのみで、**どう正規化すべきかは扱わない**
- 既存記録への actor 遡及付与の可否 (HAB Core Definition v0.1 で「過去イベント補完に該当するため行わない」と既に整理済み)

---

### 4.2 Criterion 2: AI 自動承認排除性

#### 4.2.1 評価目的 (博士提示)

**AI が Human Gate を代替しない構造であること。**

#### 4.2.2 確認項目と要求 (博士提示)

| 項目 | 要求 |
|---|---|
| AI Approval | 禁止または不可 |
| Human Presence | 明示的存在 |
| Execution Guard | 承認前実行不可 |
| Override Control | AI による迂回不可 |

#### 4.2.3 重要確認 (博士提示)

「人間が端末を操作した」ことと「Human Authority による正式承認」は **分離して評価する**。
TTY Guard は前者の補助要素であり、後者には追加証明が必要である。

#### 4.2.4 証拠要件 `[起案]`

**判定は経路単位で行う。系統単位で行わない。** 根拠は 2.3 の実測 (同一バックエンドに対し、Guard を経由する CLI 経路と経由しない直接 import 経路が併存する)。

各候補について次を列挙すること。

1. **承認関数への到達経路の全列挙**: 承認を確定させる関数・エンドポイントを特定し、そこへ到達可能な呼出経路をすべて挙げる (CLI / HTTP route / Python import / MCP tool)
2. **経路ごとの Guard 有無**: 各経路に人間性の担保 (TTY 判定 / 認証 / セッション検証) が存在するか、コード行で示す
3. **Guard を持たない経路の有無**: 1経路でも Guard なしで承認確定に到達できる場合、その事実を明示する
4. **Override 経路**: 承認を迂回して同じ結果 (state 変更・commit 等) を得られる経路が存在するか

#### 4.2.5 二段階の分離評価 `[起案]`

4.2.3 の博士指示を判定に落とすため、Criterion 2 は次の2要素を **別々に** 記録する。合成した単一値にしない。

| 要素 | 問い | 証拠の例 |
|---|---|---|
| C2-a 人間操作性 | 非対話実行 (自動スクリプト・パイプ・AI からの直接呼出) が機械的に拒否されるか | `human_gate_cli.py:36-40` の TTY 判定 |
| C2-b Authority 正式性 | その操作が Human Authority による正式承認であることを、記録側で証明できるか | actor 記録 / 権限根拠 / Finalization 層の分離 |

C2-a が成立し C2-b が UNKNOWN の場合、Criterion 2 全体の判定は **PASS ではない**。この場合の表記は
`C2-a: PASS / C2-b: UNKNOWN` とし、単一値へ丸めない。

#### 4.2.6 判定不能条件 `[起案]`

到達経路の全列挙が完了していない段階では、Criterion 2 を PASS と判定しない (未列挙経路が Guard を持たない可能性を排除できないため)。この場合は UNKNOWN とし、未調査範囲を明記する。

#### 4.2.7 本 Criterion が決定しないこと

- Guard を追加すべきか、どこに置くべきか (= 実装設計。Implementation STOP 対象)
- 複数境界での interception モデル (= Q-6)

---

### 4.3 Criterion 3: Decision Ledger 接続性

#### 4.3.1 評価目的 (博士提示)

**Human Gate 判断が Institutional Memory へ継続できること。**

#### 4.3.2 要求経路 (博士提示)

```
Human Gate
  -> Decision Record
  -> Decision Ledger
  -> Institutional State
```

#### 4.3.3 確認項目 (博士提示)

1. Decision ID 存在
2. Actor 記録
3. Timestamp 記録
4. Evidence 参照
5. State 変化との関連

#### 4.3.4 証拠要件 `[起案]`

1. **経路の段ごとの実在確認**: 4段のそれぞれについて、接続が (a) コード上に実装されているか (b) 運用規約として存在するのみか (c) 存在しないか を区別して示す
2. **Decision Ledger の同定**: 参照先が `data/decisions/decision_ledger.jsonl` であることを実測で示す。他ストア (`data/ise/` / `workshop/phi-os/data/ise/`) を指す場合はその旨を明記する
3. **確認項目5点の所在**: 各項目がどのフィールドに保持されるかを、実レコード1件以上で示す
4. **接続の断絶点**: 経路が途中で切れる場合、どの段で切れるかを特定する

#### 4.3.5 判定不能条件 `[起案]`

Decision Record が生成されるか否かがコードから判定できず、かつ実レコードも存在しない場合は UNKNOWN とする
(実績 0件は「接続なし」の証明ではないため、FAIL に寄せない)。

#### 4.3.6 本 Criterion が決定しないこと

- Decision Ledger の分散3ストアを統合するか否か (別 Unknown)
- Institutional State の定義そのもの

---

### 4.4 Criterion 4: Append-only 整合性

#### 4.4.1 評価目的 (博士提示)

**過去の意思決定履歴を改変不能な形で保持できること。**

#### 4.4.2 既存原則 `[継承]`

Custodian Operation Boundary = **Append 管理のみ** (`DC_20260805_001` G-10 Selection A)。
状態変更は既存 Record の書換ではなく **Transition Record の追記** で表現する。
上位に憲法原則1 (Event Ledger は append-only) がある (I-1)。

#### 4.4.3 確認項目 (博士提示)

1. Update による履歴変更が不可であること
2. Delete による証跡消去が不可であること
3. 新規 Decision として追記可能であること

#### 4.4.4 証拠要件 `[起案]`

1. **書込操作の型**: 状態更新が (a) 追記 (append) か (b) 既存レコードの書換 (update) か (c) ファイル全体の書き戻しか を、コード行で示す
2. **削除経路の有無**: 削除・上書きのメソッドまたは経路が存在するか。存在しない場合は「構造的に存在しない」ことを示す
3. **不可変性の担保方式**: 担保が (a) 構造上メソッドが無い (b) 規約のみ (c) 担保なし のいずれかを区別する

#### 4.4.5 参考となる既存実測 `[Confirmed]`

- HG-4 (`semantic/query_engine/human_gate.py`) は上書き・削除メソッドが **構造的に存在しない** (append-only)。ただし永続化されない (プロセス内メモリ)
- HG-2 (`app.py` `/decision/approve`) は `data/prevention_queue.json` の該当 item の `status` を書き換えてファイル全体を保存し直す (`_save_pqueue`) 構造である
- `DC_20260805_001` は未解消 Unknown として G-15 (`prevention_queue` の既存レコード書換え3箇所) を保持している

#### 4.4.6 判定不能条件 `[起案]`

書込経路が複数あり、そのうち一部しか確認できていない場合は CONDITIONAL とし、未確認経路を明記する。

#### 4.4.7 本 Criterion が決定しないこと

- 既存の書換箇所を是正するか否か、その方法 (Implementation STOP 対象)
- Transition Record の格納先 (= `DC_20260805_001` の G-14 として Unknown 保持中)

---

### 4.5 Criterion 5: 不可逆操作境界

#### 4.5.1 評価目的 (博士提示)

**承認情報が不可逆処理の前に利用可能であること。**

#### 4.5.2 対象 (博士提示)

1. Database Write
2. Git Commit
3. Runtime Action
4. State Transition

#### 4.5.3 確認項目 (博士提示)

Decision Evidence が、**実行後の記録ではなく実行前の Gate 条件として参照可能であること**。

#### 4.5.4 証拠要件 `[起案]`

各候補・各対象 (4種) について次を示す。

1. **参照の時点**: 承認 evidence を参照するコードが、不可逆操作の **前** にあるか **後** にあるか。行番号で示す
2. **参照の効果**: 参照結果が実行可否を分岐させるか (Gate 条件)、単に記録されるだけか (事後記録)
3. **evidence 不在時の挙動**: evidence が無い場合に処理が停止するか、続行するか
4. **対象4種のうち適用外のもの**: 候補がその対象を扱わない場合は「対象外」と記す。**FAIL としない**

#### 4.5.5 参考となる既存実測 `[Confirmed]`

- `governance/mocka_git_safe_commit.py` は引数 `human_gate_override_event_id` を持ち (162行)、
  `if core_files and not human_gate_override_event_id:` (211行) で **commit 実行前に分岐する**。
  これは承認証跡を実行前 Gate 条件として参照する実測例である
- `DC_20260805_001` の実測によれば、**承認証跡を参照する Enforcement Point は EP-3 の1件のみ**であり、
  EP-1 / EP-2 / EP-4 / EP-5 が承認を参照しない理由は設計意図か未実装か不明 (G-18 として Unknown 保持)

#### 4.5.6 判定不能条件 `[起案]`

参照が存在するがそれが Gate 条件か事後記録かを分岐構造から判定できない場合は UNKNOWN とする。

#### 4.5.7 本 Criterion が決定しないこと

- Enforcement Point を追加・移動すべきか (Implementation STOP 対象)
- EP-1/2/4/5 の承認非参照が設計意図か未実装かの確定 (= G-18、Unknown 保持中)

---

## 5. 次工程の出力仕様 `[起案]`

次工程 (0.5 の1から4) は、次の形式で結果を出す。本文書はこの形式を定義するのみで、**中身を一切埋めていない**。

### 5.1 比較表の形式

5候補 (HG-1..HG-5) x 5基準 (Criterion 1..5) の 25セル。各セルは次を持つ。

| 要素 | 内容 |
|---|---|
| 判定 | PASS / CONDITIONAL / FAIL / UNKNOWN (Criterion 2 のみ C2-a と C2-b を分離して2値) |
| 一次証拠 | ファイルパスと行番号、または DB 実測値。**文書の要約を証拠としない** |
| 限定条件 | CONDITIONAL の場合、限定される範囲 |
| 不足証拠 | UNKNOWN の場合、何が無いために判定できないか |

### 5.2 総合判定を置かないこと `[起案]`

比較表に **候補ごとの総合スコア・順位・推奨を置かない**。理由は次の2点。

1. 基準間の重み付けは Human Authority の裁定事項であり、くろこが決定できない
2. 総合値を置くと、それ自体が正典候補の事実上の決定として機能し、3.1 の自己拘束に反する

---

## 6. Human Gate 提示事項 (未確定事項)

本文書の `[起案]` 項目のうち、次工程に入る前に裁定が要るものを列挙する。
**推奨・優劣評価・採用すべき案の提示は行わず、観測と選択肢の列挙のみ** とする。

> **R1 訂正 (2026-08-06):** 初版はこの形式の根拠を `mocka_human_gate_decision_definition_v1.md` 第6章のみに帰属させていた。
> 一次資料を確認した結果、同第6章が定めるのは (a) Human Gate Core の出力に `decision` フィールドを含めないこと、
> (b) `recommended_note` は推奨ではなく観測であること、の2点までである。
> **選択肢を列挙する形式は `JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md` 冒頭の先例に従うもの**であり、
> 出典を分離して記載する。

| # | 未確定事項 | 選択肢 |
|---|---|---|
| HG-C01 | 判定語彙 (4.0 の PASS / CONDITIONAL / FAIL / UNKNOWN の4値) を採用するか | A: 4値を採用 / B: PASS-FAIL の2値 / C: 別語彙を博士が指定 |
| HG-C02 | UNKNOWN を FAIL と区別して保持するか | A: 区別する (4.0 の定義) / B: 区別せず不適合として扱う |
| HG-C03 | Criterion 2 を経路単位で判定するか系統単位で判定するか (根拠実測は 2.3) | A: 経路単位 / B: 系統単位 / C: 両方を併記 |
| HG-C04 | Criterion 2 の C2-a / C2-b 分離記録 (4.2.5) を採用するか | A: 分離して記録 / B: 単一値に合成 |
| HG-C05 | 5基準すべての充足を Human Gate 認定の必要条件とするか、一部で足りるか | A: 全5基準必須 / B: 必須基準と参考基準を分ける (どれを必須とするかは博士指定) / C: 本工程では決めない |
| HG-C06 | 比較表に総合判定を置かない方針 (5.2) を採用するか | A: 置かない / B: 置く (重み付けは博士が指定) |
| HG-C07 | Criterion 5 で「候補が対象を扱わない」場合を対象外と記す扱い (4.5.4-4) を採用するか | A: 対象外と記す / B: FAIL とする |

---

## 7. 本文書の限界

1. 本文書は基準の定義であり、**どの候補も評価していない**。第2章および第4章の `[Confirmed]` 実測は、
   識別子の固定と証拠要件の具体化のために引いたものであり、**適合判定ではない**
2. 第2章 2.1 の5系統一覧は JARVIS-HGJ04-EV-001 (2026-08-04 調査) の引き写しである。
   同調査以降のコード変更の有無は本文書では再確認していない
3. Human Gate の実体が 2.1 の5系統で網羅されているか自体が G-5 の Unknown の一部である。
   5系統外の第6の実体が存在しないことを、本文書は証明していない
4. `[起案]` 項目は未裁定であり、第6章の裁定前に確定事項として引用してはならない

---

## Knowledge Lineage

| 参照 | 内容 |
|---|---|
| `DC_20260805_001` | Gate 1 Rule Boundary Decision。G-5 の定義、Gate 2 の優先順位、I-1..I-7 の継承元 |
| `DC_20260801_002` | Decision Identity 制度判断。識別子体系の多義性 (2.2) |
| `docs/governance/JARVIS_HGJ04_EVIDENCE_M1_M2_M3_v0.1.md` | HG-1..HG-5 の定義 (2.1) および実測値 |
| `docs/governance/HAB_CORE_DEFINITION_v0.1.md` | canonical state と actor_type の整理 |
| `docs/governance/mocka_human_gate_decision_definition_v1.md` | 第6章 = Core 出力に `decision` を含めない / `recommended_note` は推奨ではなく観測。第2章 = Core と Finalization の2層分離 |
| `docs/governance/JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md` | 選択肢列挙形式の先例 (R1) |
| `docs/governance/HUMAN_GATE_CLI_ALIGNMENT_REPORT.md` | human_gate_cli.py の位置付け |
| `governance/human_gate_cli.py:33,36-40` | TTY Guard の所在 (2.3) |
| `governance/mocka_git_safe_commit.py:162,211` | 実行前 Gate 条件参照の実測例 (4.5.5) |
| `data/mocka_events.db` `human_gate_events` | 列構成8列 / action 分布 (4.1.5) |

**記録:** CHANGE_START `E20260806_988252226ebdb`

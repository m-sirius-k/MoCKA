# G-5 Decision Criteria Definition v0.3

## Human Gate 正典候補を評価するための判断基準 (HG-C01 / C02 / C03 / C04 / C05 / C06 / C07 裁定反映版)

**文書番号:** EBGA-G5-CRIT-001 (v0.3)
**作成日:** 2026-08-06

> **R4 注記 (2026-08-06、追記のみ。本文は不変更):**
> 本版の発行後、**HG-C11 / HG-C12 がきむら博士により裁定された**。
> 反映版は **`G5_DECISION_CRITERIA_DEFINITION_v0.4.md`** である。
> 本 v0.3 は **HG-C01 から C07 までを反映した状態を保存する版**として残す。
> v0.4 で確定した主な事項: 旧 C2-a / C2-b はラベルとして復活させない /
> 人間操作性と Authority 正式性は Criterion 2 共通要求として独立記録 /
> N/A は適用対象外であり4値とは別状態 / Finalization 判定は PASS のみ充足・
> CONDITIONAL と UNKNOWN は未確定・FAIL は不充足・N/A は適用外。
> 本版 5.5.2 が `[起案]` としていた CONDITIONAL の扱いは v0.4 で確定した。
**前版:** `G5_DECISION_CRITERIA_DEFINITION_v0.2.md` (HG-C03 のみ反映)。**v0.2 / v0.1 は各時点の状態として保存する**
**工程:** Phase B-2
**状態:** **HG-C01 / C02 / C03 / C04 / C05 / C06 / C07 は裁定済 (Ruled)。HG-C08 / C09 / C10 は保留。
本版で新たに派生した HG-C11 / C12 は未裁定。**
比較評価なし / 正典決定なし / 実装なし / **Decision Ledger 未登録 (一括登録まで意図的保留)**

---

## 0. 本文書の位置付け

### 0.1 上位からの接続 (Confirmed)

`DC_20260805_001` (Gate 1, External Reference `DEC-EBGA-20260805-G1`, approved_by NSJP kimura /
2026-08-05T10:01:43Z / Active) の未解消 Unknown **G-5 (Human Gate 接続先が5系統並存)** に属する。
Gate 2 の優先順位は G-5 / Q-5 / Q-6。Design Freeze ACTIVE / Implementation STOP は維持中。

### 0.2 本工程が答える問い

- 答える問い: **Human Gate と呼ぶために最低限満たす制度条件は何か**
- 答えない問い: Human Gate を何にするか (正典候補の決定)

### 0.3 v0.2 からの変更点

| # | 変更 | 反映元 | 箇所 |
|---|---|---|---|
| 1 | 判定語彙4値を確定 | HG-C01 | 第3章 |
| 2 | UNKNOWN と FAIL の分離を確定 | HG-C02 | 3.2 |
| 3 | Criterion 2 の記録を **C2-a (評価軸) / C2-b (検証軸)** として分離確定。**ラベルの指す対象が前版から変更された** | HG-C04 | 4.2.4 / 4.2.11 |
| 4 | 認定必要条件 (5 Criterion 全充足。UNKNOWN は FAIL 扱いしない) を追加 | HG-C05 | 5.5 |
| 5 | 総合判定欄の不設置を確定 | HG-C06 | 5.4 |
| 6 | Criterion 5 に **N/A (対象外)** を確定。FAIL / UNKNOWN と区別 | HG-C07 | 3.3 / 4.5.4 |
| 7 | 本裁定群から派生した未確定事項 **HG-C11 / HG-C12** を追加 | - | 6.3 |

**Criterion 1 から 5 の評価目的・確認項目は博士提示のまま、v0.1 から一貫して変更していない。**

### 0.4 本文書で実施していないこと

1. 正典候補の決定
2. Human Gate 仕様変更 / コード変更 / 実装 / commit
3. **Decision Ledger 登録** (0.7 の一括登録方針による意図的保留)
4. HG-1 から HG-5 への Criterion 適用 (比較評価)
5. Q-5 / Q-6 の確定
6. HG-C08 / C09 / C10 / C11 / C12 の裁定

### 0.5 表記ラベル

| ラベル | 意味 |
|---|---|
| `[Confirmed]` | 一次データで確認済みの事実 |
| `[継承]` | 既に Active または RATIFIED である確定事項からの引き写し |
| `[Ruled]` | **本工程で Human Authority が裁定した事項**。確定済み |
| `[起案]` | 本文書での新規定義。**未裁定** |
| `[Unknown]` | 未確定として保持する。推測で埋めない |

### 0.6 裁定記録

#### 0.6.1 RULE-HGC03 (2026-08-06) `[Ruled]`

**対象:** Criterion 2 の判定単位

**裁定文 (きむら博士の記述より。CP932 汚染防止規約に従い引用符のみ ASCII へ正規化。語句は不変):**

> 実務における最も堅牢な手法は、"B（系統）で網羅的な評価枠組みをつくり、A（経路）でサンプリング検証する" アプローチです。
>
> B（系統）で評価: システム全体におけるHuman Gateの位置づけ、承認権限の定義、バイパスを許容するセキュリティレベルの基準を評価・設計する。
>
> A（経路）で検証: 定義された高リスクな経路（本番アクセス、特権ID付与、本番DB変更など）において、実際にHuman Gateを回避・無視できない構造になっているかを技術的に評価する。
>
> 評価粒度は系統単位とする。検証粒度は経路単位とする。評価結果と検証結果は混同せず、それぞれ独立した記録として管理する。

| # | 確定内容 |
|---|---|
| R-1 | 評価粒度 = 系統単位 (HG-1 から HG-5) |
| R-2 | 検証粒度 = 経路単位 (承認関数への到達経路) |
| R-3 | 評価結果と検証結果は混同しない。それぞれ独立した記録として管理する |
| R-4 | 評価は網羅的に行う。検証はサンプリングで行う |

**性質:** 選択肢 A 単独でも B 単独でもなく、選択肢 C (同一判定への両方併記) でもない **軸分離型の裁定**。
**C は採用も却下もされていない** (本裁定により論点自体が置き換わったため)。

#### 0.6.2 RULE-HGC01/02/04/05/06/07 (2026-08-06) `[Ruled]`

**裁定文 (きむら博士の記述より。語句は不変):**

| # | 裁定 |
|---|---|
| **HG-C01** | 4値 (PASS / CONDITIONAL / FAIL / UNKNOWN) を採用 |
| **HG-C02** | UNKNOWN と FAIL は分離する |
| **HG-C04** | Criterion 2 は **C2-a (評価軸)** と **C2-b (検証軸)** に分離記録する |
| **HG-C05** | 5 Criterion 全充足を必要条件とする。**ただし UNKNOWN は FAIL 扱いしない** |
| **HG-C06** | 比較表に総合判定欄は設置しない |
| **HG-C07** | Criterion 5 は **対象外 (N/A) を許容する。FAIL / UNKNOWN とは区別する** |

**保留:** HG-C08 / HG-C09 / HG-C10 は別裁定として保留。

### 0.7 Decision Ledger 登録状態 `[Ruled]`

**G-5 の裁定はいずれも 2026-08-06 時点で Decision Ledger に未登録である。**

| 項目 | 状態 |
|---|---|
| 現時点の登録 | 行わない (Phase B-2 開始時の禁止事項を維持) |
| 登録の時期 | **HG-C01 から HG-C10 の制度裁定が完了した時点** |
| 登録の単位 | **G-5 裁定群として一括登録** |
| 実施主体 | Human Authority の指示による。くろこの判断では実施しない |
| それまでの裁定の所在 | 本文書と Event 記録 |

現在の未登録状態は **記録漏れではなく意図的な保留**である。
TODO_361 および I-8 の記録義務との差分は、一括登録の時点で解消される。

**本版時点の未裁定件数:** HG-C08 / C09 / C10 の3件 (加えて本版で派生した HG-C11 / C12)。
**したがって一括登録の条件は依然として成立していない。**

---

## 1. 評価対象の識別子固定

### 1.1 HG-1 から HG-5 の定義 `[Confirmed]`

`docs/governance/JARVIS_HGJ04_EVIDENCE_M1_M2_M3_v0.1.md` (JARVIS-HGJ04-EV-001) 第1章からの引き写し。

| # | 実体 | 状態記録先 | 状態語彙 |
|---|---|---|---|
| HG-1 | `phi_os/human_gate.py` | `mocka_events.db` の `human_gate_events` テーブル | PENDING / APPROVED / REJECTED / EXPIRED / CANCELED |
| HG-2 | `app.py` `/decision/approve` `/decision/reject` | `data/prevention_queue.json` | NEW / approved / rejected |
| HG-3 | `governance/mocka_git_safe_commit.py` の Core System File 除外 | git 作業ツリー (未コミット状態として保持) | 状態語彙なし (コミット有無) |
| HG-4 | `semantic/query_engine/human_gate.py` | インメモリ (`HumanGateRulingStore._records: list`)。永続化なし | accept / reject / defer / split |
| HG-5 | `governance/human_gate_continuity.py` | `data/decisions/pending_decision_units.jsonl` | WAITING_FOR_HUMAN_GATE のみ |

**RULE-HGC03 R-1 により、評価軸 (C2-a) の1単位はこの表の1行である。**

### 1.2 識別子の多義性 `[Confirmed]`

| 体系 | 出典 | 指すもの |
|---|---|---|
| 本評価の HG-1..HG-5 | JARVIS-HGJ04-EV-001 第1章 | Human Gate 実装の5系統 |
| HG-1 / HG-3 / HG-4 | `DC_20260801_002` | Decision Identity の制度判断項目 |
| HG-J01..HG-J09 | `JARVIS_CONSTITUTION_DRAFT.md` 第9章 | JARVIS Constitution の Human Gate 提示事項 |
| HG-H01..HG-H10 | `HAB_CORE_DEFINITION_v0.1.md` | HAB Core Definition の裁定事項 |
| HG-C01..HG-C12 | 本文書 第6章 | G-5 判断基準の裁定事項 |

本文書内で修飾なしに `HG-1` と書いた場合は、常に 1.1 の定義を指す。

### 1.3 TTY Guard の所在 `[Confirmed]`

| 項目 | 実測 |
|---|---|
| Guard の実体 | `governance/human_gate_cli.py:36-40` の `_require_tty()` (`sys.stdin.isatty()` が偽なら `sys.exit(1)`) |
| 適用範囲 | `approve` / `reject` サブコマンドのみ |
| HG-1 との関係 | 同ファイル33行が `from phi_os.human_gate import submit, approve, reject, get_state, list_pending` を実行する。CLI は **HG-1 バックエンドの front-end** である |
| 帰結 | Guard は `phi_os/human_gate.py` 自体ではなく **CLI 経路上に存在する**。直接 import する経路には TTY 判定が存在しない |
| 検索範囲 | `C:\Users\sirok\MoCKA` 配下の Python コード。`.venv` / `archive` / `node_modules` 除外、2026-08-06 時点。**範囲外に別の担保機構が存在しないことは証明していない** |

---

## 2. 継承する既存確定事項 `[継承]`

| # | 事項 | 出典 |
|---|---|---|
| I-1 | Event ledger is append only | 憲法原則1 |
| I-2 | Custodian Operation Boundary = Append 管理のみ (G-10 Selection A) | `DC_20260805_001` |
| I-3 | Rule Owner = Human Authority / Rule Custodian = HAB (C2-01) | `DC_20260805_001` |
| I-4 | Rule 制定 / Detection / Execution の分離 (C2-02) | `DC_20260805_001` |
| I-5 | Enforcement Point は Integrity Ledger 管理 (C2-03) | `DC_20260805_001` |
| I-6 | Validation Layer は独立 Authority Layer (G-9 Selection B) | `DC_20260805_001` |
| I-7 | INV-2.8 = 承認済み許可を執行できるが許可権限を生成できない (G-11 Selection B) | `DC_20260805_001` |
| I-8 | 裁定が確定した時点で Decision Ledger へ記録する義務 (0.7 の一括登録方針により時期を後倒し) | TODO_361 / `.claude/CLAUDE.md` |
| I-9 | Human Gate は Core (評価のみ) と Finalization (きむら博士専権) の2層に分離される | `mocka_human_gate_decision_definition_v1.md` 第2章 |

### 2.1 自動裁定化リスクに対する自己拘束 `[起案]`

本基準は **評価および検証のみを生成し、承認を確定しない**。

- 5 Criterion 全充足 (HG-C05) を満たすことも、**正典として採用されることを意味しない**。
  正典採用は Human Authority の裁定事項である
- 本基準に閾値を設けて自動的に正典を決定する条項を、本文書は持たない
- 本基準の適用結果を根拠に、くろこが Human Gate 仕様・コード・Ledger を変更することはない

---

## 3. 判定語彙 `[Ruled]`

### 3.1 4値 (HG-C01)

| 判定 | 定義 |
|---|---|
| **PASS** | 確認項目のすべてについて、一次証拠により要求を満たすことが確認できた |
| **CONDITIONAL** | 確認項目の一部を満たすが、限定条件が付く。限定条件を明記する |
| **FAIL** | 一次証拠により、要求を満たさないことが確認できた |
| **UNKNOWN** | 判定に必要な証拠が現存しない |

本語彙は **C2-a (評価軸) と C2-b (検証軸) の双方に適用する**。

### 3.2 UNKNOWN と FAIL の分離 (HG-C02)

**UNKNOWN と FAIL は分離する。**

| 規則 | 内容 |
|---|---|
| V-1 | 証拠の不在は不適合の証明ではない。**UNKNOWN を FAIL へ読み替えない** |
| V-2 | UNKNOWN は解消されるまで UNKNOWN として保持する。推測で PASS / FAIL に寄せない |
| V-3 | UNKNOWN の記載には **何が無いために判定できないか** を必ず併記する |
| V-4 | HG-C05 の必要条件判定においても UNKNOWN は FAIL 扱いしない (5.5 参照) |

### 3.3 N/A (HG-C07)

**Criterion 5 は対象外 (N/A) を許容する。N/A は FAIL とも UNKNOWN とも区別する。**

| 判定 | 意味の区別 |
|---|---|
| **N/A** | 候補が構造上その対象を扱わないため、評価対象そのものが存在しない |
| FAIL | 対象を扱うが、要求を満たさないことが確認できた |
| UNKNOWN | 対象を扱うか否か、または要求を満たすか否かの証拠が現存しない |

| 規則 | 内容 |
|---|---|
| V-5 | N/A の記載には **その候補がその対象を扱わないことの一次証拠** を併記する。証拠がない場合は N/A ではなく UNKNOWN とする |
| V-6 | N/A の適用範囲は **Criterion 5 の対象4種**である。他 Criterion への適用可否は裁定されていない (6.3 HG-C12 と併せて未確定) |

---

## 4. 判断基準の定義

### 4.1 Criterion 1: Human Authority 証明可能性

**判定単位:** 系統単位

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

操作者と承認権限者の同一性または関係性を説明できること。

#### 4.1.4 証拠要件 `[起案]`

1. **Actor が保持されるフィールド**: 記録スキーマ上のどの列・キーに actor が保持されるか
2. **Actor 値の出所**: (a) 実行者の検証結果 / (b) 呼出側が渡した任意値 / (c) コード内固定値。コード行を示す
3. **Action Trace の再現単位**: 何が実行されたかを事後に特定できる記録が要求単位で残るか
4. **Evidence Link**: 承認記録から対象へ到達する参照が記録側に存在するか

#### 4.1.5 参考となる既存実測 `[Confirmed]`

- `human_gate_events` の列は8列 (`event_id / timestamp / type / action / request_id / payload / previous_state / next_state`)。**`actor` 列は存在しない** (`DC_20260805_001` G-6 と一致)
- action 分布は `submit` 1,774件 / `approve` 5件。`reject` / `expire` / `cancel` は 0件
- `app.py` の `/decision/approve` は Event に `who_actor="kimura_hakase"` を **コード内固定値として** 記録する

#### 4.1.6 判定不能条件 `[Ruled 準拠]`

actor の出所が (a) / (b) / (c) のいずれかをコード上で特定できない場合は **UNKNOWN** とする (V-1 / V-2 適用)。

#### 4.1.7 本 Criterion が決定しないこと

- Actor Identity の正規化方式 (= Q-5)
- 既存記録への actor 遡及付与の可否

---

### 4.2 Criterion 2: AI 自動承認排除性 (RULE-HGC03 / HG-C04 適用)

#### 4.2.1 評価目的 (博士提示)

**AI が Human Gate を代替しない構造であること。**

#### 4.2.2 確認項目と要求 (博士提示)

| 項目 | 要求 |
|---|---|
| AI Approval | 禁止または不可 |
| Human Presence | 明示的存在 |
| Execution Guard | 承認前実行不可 |
| Override Control | AI による迂回不可 |

#### 4.2.3 重要確認 (博士提示、v0.1 から一貫して保持)

「人間が端末を操作した」ことと「Human Authority による正式承認」は分離して評価する。
TTY Guard は前者の補助要素であり、後者には追加証明が必要である。

**注意:** この要求は取り下げられていない。どちらの軸で担保するかは未確定である (6.3 HG-C11)。

#### 4.2.4 二軸構造 `[Ruled]` (RULE-HGC03 + HG-C04)

| 軸 | ラベル | 粒度 | 網羅性 | 評価対象 |
|---|---|---|---|---|
| **評価軸 (Evaluation)** | **C2-a** | 系統単位 (HG-1 から HG-5) | 網羅的 (5系統すべて) | Human Gate の位置づけ / 承認権限の定義 / バイパスを許容するセキュリティレベルの基準 |
| **検証軸 (Verification)** | **C2-b** | 経路単位 (承認関数への到達経路) | サンプリング (高リスク経路) | 対象経路で Human Gate を回避・無視できない構造かの技術的検証 |

**HG-C04 により、Criterion 2 は C2-a と C2-b を分離記録する。**

#### 4.2.5 C2-a (評価軸) の証拠要件 `[起案]`

系統ごとに次を示す。

1. **Human Gate の位置づけ**: 当該系統が承認機構として何を対象とするか (承認要求 / collision 裁定 / commit 抑止 等)
2. **承認権限の定義**: 誰が承認主体として定義されているか。定義の所在 (文書 / コード / 未定義) を区別する
3. **バイパス許容水準の基準**: 当該系統がバイパスをどこまで許容する設計かの定義が存在するか
4. **AI 承認の可否に関する定義**: AI が承認主体になりうるかについての定義の有無

#### 4.2.6 C2-b (検証軸) の証拠要件 `[起案]`

対象経路ごとに次を示す。

1. **経路の同定**: 承認確定に到達する経路 (CLI / HTTP route / Python import / MCP tool) をファイルと行で特定する
2. **Guard の有無**: 当該経路に人間性の担保 (TTY 判定 / 認証 / セッション検証) が存在するか。コード行で示す
3. **回避可能性**: 当該経路で Human Gate を回避・無視して同じ結果に到達できるか
4. **サンプリング根拠**: なぜその経路を検証対象に選んだか (HG-C08 の裁定に依存する)

#### 4.2.7 記録分離規則 `[Ruled]` (RULE-HGC03 R-3 + HG-C04)

| # | 規則 |
|---|---|
| S-1 | C2-a と C2-b は **別の記録として管理する**。同一のセル・同一の値へ合成しない |
| S-2 | C2-a の判定値をもって C2-b の結論としない。逆も同様 |
| S-3 | 一方の結果を他方の根拠として引用する場合は、**出所の軸を明示する** |
| S-4 | 両者が食い違う場合の統合規則は **未定義** (HG-C09)。統合値を作らずに両方を保持する |

#### 4.2.8 判定不能条件 `[Ruled 準拠]`

| 軸 | 判定不能条件 |
|---|---|
| C2-a | 承認権限の定義またはバイパス許容水準の定義が文書・コードのいずれにも存在しない場合、当該項目を **UNKNOWN** とする。**定義の不在を FAIL と読み替えない** (V-1) |
| C2-b | 対象経路の同定が完了していない場合、当該経路について判定しない。**未検証の経路を安全と推定しない** |

#### 4.2.9 本 Criterion が決定しないこと

- Guard を追加すべきか、どこに置くべきか (Implementation STOP 対象)
- 複数境界での interception モデル (= Q-6)
- 検証対象とする高リスク経路の選定基準 (= HG-C08、未裁定)

#### 4.2.10 RULE-HGC03 による副次的帰結 `[Confirmed]`

`G5_HGC03_OPTION_COMPARISON_v0.1.md` 3.2 は、選択肢 B の制約として
「系統内に複数経路がある場合、どの経路の性質を系統の判定値とするかの規則が別途必要になる」を挙げていた。

C2-a が定義・設計を対象とし、経路の実装差は C2-b が扱うため、
C2-a において経路の集約規則を要する度合いは低下する。
ただし **C2-a が定義レベルのみを見るのか、実装状態も含むのかは裁定文からは一意に定まらない** (HG-C10)。

#### 4.2.11 ラベル C2-a / C2-b の意味変更 `[Confirmed]` (重要)

**HG-C04 の裁定により、C2-a / C2-b の指す対象が前版から変更された。**

| 版 | C2-a | C2-b |
|---|---|---|
| v0.1 / v0.2 (4.2.5) | 人間操作性 (非対話実行が機械的に拒否されるか) | Authority 正式性 (Human Authority による正式承認と記録側で証明できるか) |
| **v0.3 (本版、裁定後)** | **評価軸 (系統単位)** | **検証軸 (経路単位)** |

**引用時にこの区別を潰さないこと。** v0.1 / v0.2 の C2-a / C2-b を参照している記述は、
本版の C2-a / C2-b とは別の対象を指す。

前版の区別 (人間操作性 / Authority 正式性) は 4.2.3 の博士提示要求として **依然有効**であり、
**取り下げられていない**。これを C2-a / C2-b のどちらで担保するかは未確定である (6.3 HG-C11)。

---

### 4.3 Criterion 3: Decision Ledger 接続性

**判定単位:** 系統単位

#### 4.3.1 評価目的 (博士提示)

Human Gate 判断が Institutional Memory へ継続できること。

#### 4.3.2 要求経路 (博士提示)

```
Human Gate
  -> Decision Record
  -> Decision Ledger
  -> Institutional State
```

#### 4.3.3 確認項目 (博士提示)

1. Decision ID 存在 / 2. Actor 記録 / 3. Timestamp 記録 / 4. Evidence 参照 / 5. State 変化との関連

#### 4.3.4 証拠要件 `[起案]`

1. **経路の段ごとの実在確認**: (a) コード上に実装 / (b) 運用規約のみ / (c) 存在しない を区別する
2. **Decision Ledger の同定**: 参照先が `data/decisions/decision_ledger.jsonl` であることを実測で示す
3. **確認項目5点の所在**: 各項目がどのフィールドに保持されるかを実レコード1件以上で示す
4. **接続の断絶点**: 経路が途中で切れる場合、どの段で切れるかを特定する

#### 4.3.5 判定不能条件 `[Ruled 準拠]`

Decision Record が生成されるか否かがコードから判定できず、かつ実レコードも存在しない場合は **UNKNOWN** とする
(実績0件は接続なしの証明ではない。V-1 適用)。

#### 4.3.6 本 Criterion が決定しないこと

- Decision Ledger の分散3ストアを統合するか否か
- Institutional State の定義そのもの

---

### 4.4 Criterion 4: Append-only 整合性

**判定単位:** 系統単位

#### 4.4.1 評価目的 (博士提示)

過去の意思決定履歴を改変不能な形で保持できること。

#### 4.4.2 既存原則 `[継承]`

Custodian Operation Boundary = Append 管理のみ (`DC_20260805_001` G-10 Selection A)。
状態変更は既存 Record の書換ではなく Transition Record の追記で表現する。上位に憲法原則1 (I-1)。

#### 4.4.3 確認項目 (博士提示)

1. Update による履歴変更が不可であること
2. Delete による証跡消去が不可であること
3. 新規 Decision として追記可能であること

#### 4.4.4 証拠要件 `[起案]`

1. **書込操作の型**: (a) 追記 / (b) 既存レコードの書換 / (c) ファイル全体の書き戻し をコード行で示す
2. **削除経路の有無**: 削除・上書きのメソッドまたは経路が存在するか
3. **不可変性の担保方式**: (a) 構造上メソッドが無い / (b) 規約のみ / (c) 担保なし を区別する

#### 4.4.5 参考となる既存実測 `[Confirmed]`

- HG-4 は上書き・削除メソッドが構造的に存在しない (append-only)。ただし永続化されない
- HG-2 は `data/prevention_queue.json` の該当 item の `status` を書き換えてファイル全体を保存し直す
- `DC_20260805_001` は G-15 (`prevention_queue` の既存レコード書換え3箇所) を Unknown として保持

#### 4.4.6 判定不能条件 `[Ruled 準拠]`

書込経路が複数あり **一部しか確認できていない** 場合は **CONDITIONAL** とし、未確認経路を明記する。
**経路の存否そのものが確認できない** 場合は **UNKNOWN** とする (V-1 / V-3 適用)。

> **v0.2 からの明確化:** v0.1 / v0.2 では本項が CONDITIONAL のみを規定しており、
> 同種の「一部未確認」状態に対する割当が Criterion 2 (UNKNOWN) と非対称であった (PREP CH-1)。
> HG-C01 / HG-C02 の裁定を受け、**確認済み範囲があるか否か**で CONDITIONAL と UNKNOWN を分ける形に整理した。
> これは裁定の適用であり、新たな基準の追加ではない。

#### 4.4.7 本 Criterion が決定しないこと

- 既存の書換箇所を是正するか否か、その方法 (Implementation STOP 対象)
- Transition Record の格納先 (= G-14、Unknown 保持中)

---

### 4.5 Criterion 5: 不可逆操作境界 (HG-C07 適用)

**判定単位:** 系統単位

#### 4.5.1 評価目的 (博士提示)

承認情報が不可逆処理の前に利用可能であること。

#### 4.5.2 対象 (博士提示)

1. Database Write / 2. Git Commit / 3. Runtime Action / 4. State Transition

#### 4.5.3 確認項目 (博士提示)

Decision Evidence が、実行後の記録ではなく実行前の Gate 条件として参照可能であること。

#### 4.5.4 証拠要件 `[起案 + Ruled]`

各候補・各対象 (4種) について次を示す。

1. **参照の時点**: 承認 evidence を参照するコードが不可逆操作の前にあるか後にあるか。行番号で示す
2. **参照の効果**: 参照結果が実行可否を分岐させるか (Gate 条件)、単に記録されるだけか (事後記録)
3. **evidence 不在時の挙動**: evidence が無い場合に処理が停止するか、続行するか
4. **対象外の扱い** `[Ruled]`: 候補がその対象を **構造上扱わない** 場合は **N/A** とする。
   **FAIL とはしない。UNKNOWN とも区別する** (HG-C07 / V-5)。
   N/A とするには、扱わないことの一次証拠を併記する。証拠がない場合は UNKNOWN とする

#### 4.5.5 参考となる既存実測 `[Confirmed]`

- `governance/mocka_git_safe_commit.py` は引数 `human_gate_override_event_id` を持ち (162行)、
  `if core_files and not human_gate_override_event_id:` (211行) で **commit 実行前に分岐する**
- `DC_20260805_001` の実測では、承認証跡を参照する Enforcement Point は **EP-3 の1件のみ**。
  EP-1 / EP-2 / EP-4 / EP-5 が承認を参照しない理由は設計意図か未実装か不明 (G-18)

#### 4.5.6 判定不能条件 `[Ruled 準拠]`

参照が存在するがそれが Gate 条件か事後記録かを分岐構造から判定できない場合は **UNKNOWN** とする。

#### 4.5.7 本 Criterion が決定しないこと

- Enforcement Point を追加・移動すべきか (Implementation STOP 対象)
- EP-1/2/4/5 の承認非参照が設計意図か未実装かの確定 (= G-18)

#### 4.5.8 検証軸 (C2-b) との関係 `[Unknown]`

Criterion 5 の証拠要件はコード行単位の特定を求めており C2-b と粒度が近接するが、
**Criterion 5 を C2-b へ組み入れるか否かは裁定されていない**。
本文書では Criterion 5 を系統単位の Criterion として扱い、組入れは行わない。

---

## 5. 次工程の出力仕様

### 5.1 評価記録 (Evaluation Record) `[Ruled 準拠]`

- **単位:** 系統 (HG-1 から HG-5)
- **網羅性:** 5系統すべて
- **形式:** 5候補 x 5基準 = 25セル。Criterion 2 のセルには **C2-a のみ**を記載する

| 要素 | 内容 |
|---|---|
| 判定 | PASS / CONDITIONAL / FAIL / UNKNOWN (Criterion 5 のみ N/A を含む) |
| 一次証拠 | ファイルパスと行番号、または DB 実測値。文書の要約を証拠としない |
| 限定条件 | CONDITIONAL の場合、限定される範囲 |
| 不足証拠 | UNKNOWN の場合、何が無いために判定できないか (V-3) |
| 対象外根拠 | N/A の場合、扱わないことの一次証拠 (V-5) |

### 5.2 検証記録 (Verification Record) `[Ruled 準拠]`

- **単位:** 経路
- **網羅性:** サンプリング (対象選定基準は HG-C08 の裁定に依存)
- **形式:** 経路ごとの独立レコード。**評価記録の25セルに埋め込まない** (S-1)

| 要素 | 内容 |
|---|---|
| 対象経路 | ファイルと行での同定 |
| 所属系統 | 参照のみ。**評価記録の判定値を上書きしない** (S-2) |
| Guard の有無 | コード行 |
| 回避可能性 | 検証結果 |
| 判定 | PASS / CONDITIONAL / FAIL / UNKNOWN |
| サンプリング根拠 | なぜ対象に選んだか |

### 5.3 分離の維持 `[Ruled]`

S-1 から S-4 により、5.1 と 5.2 は別文書または別章として管理し、
**両者を合成した単一の判定値を作らない**。

### 5.4 総合判定欄の不設置 `[Ruled]` (HG-C06)

**比較表に総合判定欄は設置しない。** 候補ごとの総合スコア・順位・推奨のいずれも置かない。

### 5.5 認定必要条件 `[Ruled]` (HG-C05)

**5 Criterion 全充足を Human Gate 認定の必要条件とする。ただし UNKNOWN は FAIL 扱いしない。**

#### 5.5.1 適用の形式 `[起案]`

HG-C05 (全充足を必要条件とする) と HG-C06 (総合判定欄を設置しない) の双方を満たすため、
本必要条件は **比較表の欄としてではなく、Human Gate Finalization が適用する判断規則として記述する**。
すなわち評価記録の各セルは個別判定のみを保持し、全充足の成否は表に書き込まない。

**この形式は本文書による解釈である。** 両裁定を同時に満たす形として起案したものであり、
形式そのものの裁定は受けていない。

#### 5.5.2 必要条件の状態 `[起案]`

裁定 (全充足必要 / UNKNOWN は FAIL 扱いしない) から、候補の状態は次の3種に分かれる。

| 状態 | 条件 |
|---|---|
| **充足** | 5 Criterion すべてが PASS |
| **不充足** | 1つ以上の Criterion が FAIL |
| **未確定** | FAIL は無いが、1つ以上の Criterion が UNKNOWN または CONDITIONAL |

**未確定は不充足ではない** (V-4)。UNKNOWN が解消されるまで、その候補の必要条件充足は確定しない。

**未裁定の残件:**
- CONDITIONAL を充足とみなすか未確定とみなすかは裁定されていない。本文書では **未確定**側に置いている `[起案]`
- **N/A を含む候補の扱い**は裁定されていない (6.3 HG-C12)

#### 5.5.3 必要条件と正典採用の関係 `[継承]`

必要条件を満たすことは **正典として採用されることを意味しない** (2.1)。
正典採用は Human Authority の裁定事項である。

---

## 6. 裁定状態一覧

### 6.0 R1 訂正 (v0.1 から継承)

未確定事項の記述形式について。`mocka_human_gate_decision_definition_v1.md` 第6章が定めるのは
(a) Human Gate Core の出力に `decision` フィールドを含めないこと、(b) `recommended_note` は推奨ではなく観測であること、の2点。
**選択肢を列挙する形式は `JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md` の先例に従う。**
推奨・優劣評価・採用すべき案の提示は行わない。

### 6.1 裁定済 `[Ruled]`

| # | 事項 | 裁定内容 | 裁定日 |
|---|---|---|---|
| HG-C01 | 判定語彙 | 4値 (PASS / CONDITIONAL / FAIL / UNKNOWN) を採用 | 2026-08-06 |
| HG-C02 | UNKNOWN と FAIL | 分離する | 2026-08-06 |
| HG-C03 | Criterion 2 の判定単位 | 評価粒度 = 系統単位 / 検証粒度 = 経路単位 / 独立記録 (R-1..R-4) | 2026-08-06 |
| HG-C04 | Criterion 2 の記録形式 | C2-a (評価軸) と C2-b (検証軸) に分離記録 | 2026-08-06 |
| HG-C05 | 認定必要条件 | 5 Criterion 全充足を必要条件とする。UNKNOWN は FAIL 扱いしない | 2026-08-06 |
| HG-C06 | 総合判定欄 | 設置しない | 2026-08-06 |
| HG-C07 | Criterion 5 の対象外 | N/A を許容。FAIL / UNKNOWN と区別する | 2026-08-06 |

### 6.2 保留中 (別裁定)

| # | 未確定事項 | 選択肢 |
|---|---|---|
| HG-C08 | 検証軸 (C2-b) のサンプリング対象 (高リスク経路) の選定基準 | A: Criterion 5 の対象4種を軸に選定 / B: 承認確定に到達する経路をすべて対象とする / C: 博士が個別に指定 |
| HG-C09 | C2-a と C2-b が食い違った場合の扱い (S-4 により統合値は作らないが、その先が未定義) | A: 両方を保持したまま Human Gate へ提示 / B: 不一致を Incident として記録 / C: 博士が指定 |
| HG-C10 | C2-a が見る対象範囲 | A: 定義・設計レベルのみ / B: 実装状態も含む / C: 博士が指定 |

### 6.3 本裁定群から派生した新規未確定事項

**以下は裁定の適用に必要な未定義部分であり、くろこが新たな評価軸を追加したものではない。**

| # | 未確定事項 | 発生源 | 選択肢 |
|---|---|---|---|
| HG-C11 | 4.2.3 の博士提示要求 (人間操作性 と Authority 正式性 の分離評価) を、C2-a / C2-b のどちらで担保するか。HG-C04 により C2-a / C2-b のラベルが評価軸 / 検証軸へ再割当されたため、旧区別の担保位置が未定義になった | HG-C04 | A: 人間操作性を C2-b、Authority 正式性を C2-a で担保する / B: 両方を C2-a の確認項目として保持 / C: 独立した第3の記録とする / D: 博士が指定 |
| HG-C12 | 認定必要条件 (HG-C05) の判定において N/A を含む候補をどう扱うか | HG-C05 + HG-C07 | A: N/A は充足とみなす / B: N/A の Criterion を対象から除外し残りで判定 / C: N/A があるかぎり未確定とする / D: 博士が指定 |

**加えて 5.5.2 の CONDITIONAL の扱い**が未裁定である (本文書では未確定側に置いた `[起案]`)。

---

## 7. 次工程への引き渡し

### 7.1 引き渡す成果物

| # | 成果物 | 状態 |
|---|---|---|
| 1 | 本文書 (G-5 判断基準 v0.3) | HG-C01..C07 反映済み |
| 2 | `G5_DECISION_CRITERIA_DEFINITION_v0.2.md` | HG-C03 のみ反映の版として保存 |
| 3 | `G5_DECISION_CRITERIA_DEFINITION_v0.1.md` | 裁定前の版として保存 |
| 4 | `G5_DECISION_CRITERIA_DECISION_PREP_v0.1.md` | 裁定準備資料 |
| 5 | `G5_HGC03_OPTION_COMPARISON_v0.1.md` | HG-C03 の裁定根拠資料 |

### 7.2 次工程の開始条件 `[Unknown]`

| 裁定 | 次工程への影響 | 状態 |
|---|---|---|
| HG-C01 / C02 | 判定値の表記 | **確定** |
| HG-C03 | 証拠収集の粒度 | **確定** |
| HG-C04 | Criterion 2 の記録形式 | **確定** |
| HG-C05 / C06 | 認定必要条件と出力形式 | **確定** (適用形式 5.5.1 と CONDITIONAL の扱いは `[起案]`) |
| HG-C07 | Criterion 5 の N/A | **確定** |
| HG-C08 | C2-b の対象経路の選定 | **未裁定。C2-b (検証軸) に着手できない** |
| HG-C10 | C2-a が見る対象範囲 | **未裁定。C2-a の証拠要件 (4.2.5) の解釈が定まらない** |
| HG-C09 | C2-a と C2-b の不一致時の手続き | 未裁定。両軸の結果が出た後に必要 |
| HG-C11 | 人間操作性 / Authority 正式性 の担保位置 | 未裁定 |
| HG-C12 | 必要条件判定における N/A の扱い | 未裁定。Criterion 5 に N/A が生じた候補で必要 |

**着手可能性の事実 (推奨ではない):**
Criterion 1 / 3 / 4 / 5 の評価軸証拠収集は、上記未裁定項目に依存しない。
Criterion 2 は C2-a が HG-C10、C2-b が HG-C08 に依存する。

**現時点で比較評価工程には着手していない。着手可否は Human Authority の指示による。**

### 7.3 記録義務の状態

0.7 のとおり、G-5 の裁定は Decision Ledger に **未登録**である (意図的保留)。
**HG-C08 / C09 / C10 が未裁定であるため、一括登録の条件は成立していない。**
HG-C11 / C12 を一括登録の対象に含めるかは未確定である。

---

## 8. 本文書の限界

1. 本文書は基準の定義であり、**どの候補も評価・検証していない**
2. 第1章 1.1 の5系統一覧は JARVIS-HGJ04-EV-001 (2026-08-04 調査) の引き写しである。同調査以降のコード変更の有無は再確認していない
3. 5系統外の第6の実体が存在しないことを、本文書は証明していない (G-5 の Unknown 本体)
4. `[起案]` 項目は未裁定である。特に **5.5.1 の適用形式と 5.5.2 の CONDITIONAL の扱い**は本文書の解釈である
5. 4.2.11 のとおり **C2-a / C2-b は前版と指す対象が異なる**。版をまたいで引用する際は必ず版を明示すること
6. 1.3 の Guard 所在は検索範囲を限定した実測である

---

## Knowledge Lineage

| 参照 | 内容 |
|---|---|
| `G5_DECISION_CRITERIA_DEFINITION_v0.2.md` | 前版 (HG-C03 のみ反映) |
| `G5_DECISION_CRITERIA_DEFINITION_v0.1.md` | 初版 (裁定前) |
| `G5_DECISION_CRITERIA_DECISION_PREP_v0.1.md` | HG-C01..C07 の裁定準備資料。CH-1 (CONDITIONAL / UNKNOWN の非対称) は 4.4.6 で解消 |
| `G5_HGC03_OPTION_COMPARISON_v0.1.md` | HG-C03 の選択肢比較資料 |
| `DC_20260805_001` | Gate 1。G-5 の定義、I-1..I-7、G-6 / G-14 / G-15 / G-18 |
| `DC_20260801_002` | Decision Identity。識別子体系の多義性 (1.2) |
| `docs/governance/JARVIS_HGJ04_EVIDENCE_M1_M2_M3_v0.1.md` | HG-1..HG-5 の定義および実測 |
| `docs/governance/mocka_human_gate_decision_definition_v1.md` | 第2章 / 第6章 / 第7章 |
| `docs/governance/JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md` | 選択肢列挙形式の先例 (R1) |
| `governance/human_gate_cli.py:33,36-40` | TTY Guard の所在 (1.3) |
| `governance/mocka_git_safe_commit.py:162,211` | 実行前 Gate 条件参照の実測例 (4.5.5) |
| `data/mocka_events.db` `human_gate_events` | 列構成8列 / action 分布 (4.1.5) |

**記録:** CHANGE_START `E20260806_281953138dd94`

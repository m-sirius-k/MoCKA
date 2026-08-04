# JARVIS Constitution — DRAFT v0.1

**文書番号:** JARVIS-CONST-DRAFT-001
**作成日:** 2026-08-04
**状態:** **DRAFT(未裁定)**
**Decision Ledger 登録:** **なし**
**実装:** **なし**(本文書はコード・Runtime・HAB のいずれも実装しない)

---

## 第0章 本文書の制度的位置づけ(先に確定させる)

### 0.1 本文書は何であり、何でないか

| | |
|---|---|
| **本文書である** | JARVIS を制度上どう定義するかの **起草案**。Human Gate Finalization への提示材料 |
| **本文書でない** | 発効した憲法 / 承認された要件定義 / 実装指示 / Decision |

`PHI_OS_CONSTITUTION_v1.md` 第2章 原則2(Active/RATIFIED)により
**制度の新設・変更・廃止は PHI-OS の専権事項**であり、
`mocka_human_gate_decision_definition_v1.md` §2.2 により
**APPROVE/HOLD/REJECT/DEFER の確定はきむら博士本人のみが行う**。

したがって本文書は、起草(くろこ)の時点では制度的効力を一切持たない。
本文書が効力を持つのは、Human Gate Finalization による裁定と Decision Ledger 登録の後である。

### 0.2 表記規約

| ラベル | 意味 |
|---|---|
| **【継承】** | 既存の Active な Decision・RATIFIED 文書から引き写した条項。本 Draft は内容を変更していない。出典を必ず併記する |
| **【起案】** | 本 Draft が新たに提案する条項。**未裁定。Human Gate の判断対象** |
| **【未裁定】** | 一次資料間に不一致があり、本 Draft では確定させない事項 |
| **【Unknown】** | 一次資料が存在せず、確定の材料自体がない事項 |

**【起案】は提案であって事実ではない。** 本文書を引用する際、【継承】と【起案】を混同してはならない。

### 0.3 起草の根拠資料(すべて一次資料を直接読解)

| 資料 | 状態 |
|---|---|
| `C:\Users\sirok\Desktop\aimd\ジャビス.md`(2026-08-04 09:33) | 構想メモ。**Decision Ledger 未登録** |
| `PHI_OS_CONSTITUTION_v1.md`(PHI-OS-CONST-001) | **RATIFIED v1** |
| `docs/governance/mocka_human_gate_decision_definition_v1.md` | DRAFT |
| `docs/governance/mocka_hab_v1_contract.md` / `mocka_hab_human_gate_relation_v1.md` | DRAFT |
| `docs/audits/PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md` | DESIGN |
| `docs/audits/PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1.md` | 調査文書 |
| Decision Ledger(206行を走査) | `DC_20260728_002` `DC_20260728_003` `DC_20260729_001` `DC_20260729_008` `DC_20260729_009` `DC_20260729_013` `DC_20260730_009` `DC_20260801_002` ほか |
| MoCKA Runtime 実測 | `JARVIS_ARCHITECTURE_CURRENT.md` / `JARVIS_RUNTIME_FLOW.md`(2026-08-04) |

---

## 第1章 JARVIS の定義

### 1.1 定義【継承 — ただし出典は未登録文書】

`ジャビス.md` §8 は JARVIS を次のように定める(原文):

> JARVIS は万能AIではない。
> 役割: 「人間の意図をInstitutional AI環境へ接続するインターフェース」

**注意:** この定義の出典 `ジャビス.md` は Decision Ledger 未登録であり、
`DC_20260729_001`(Active)は JARVIS 構想の扱いを
**Deferred(将来のPHI-OS全体再設計時に再評価)** と裁定している。
本 Draft は §1.1 を「唯一存在する定義文」として採用するが、
**これを承認済み定義として扱うか否かは Human Gate の判断事項**(HG-J01)である。

### 1.2 JARVIS が「でない」もの【起案】

`PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md` §1 が Sequence Controller に対して用いた
否定形の定義様式を踏襲し、JARVIS についても同様に定める。

- JARVIS は **AIモデルではない**(推論主体そのものではない)
- JARVIS は **Decision Maker ではない**(最終判断を下さない)
- JARVIS は **Sequence Controller ではない**(Module間の状態遷移制御は PHI-OS の責務)
- JARVIS は **Governance ではない**(許可・証拠検証は MoCKA の責務)
- JARVIS は **Memory ではない**(過去の保持は Memory/MoCKA の責務)
- JARVIS は **万能AIではない**(§1.1 原文)

### 1.3 JARVIS の責務範囲【起案】

`ジャビス.md` §8 の構造図に基づく。

```
Human
  |
  v
JARVIS          … 意図理解・対話。人間の意図を制度環境が扱える形へ変換する
  |
  v
PHI-HAB         … 認知環境(§7 の用語問題を参照)
  |
  v
Institutional Runtime  … MoCKA / Orchestra / P-DERS
```

JARVIS の責務は **入口の変換のみ**であり、変換より下流のいかなる責務も持たない。

### 1.4 JARVIS が答える問い【起案】

`PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md` §5.1(Active な設計文書)は各層の問いを定めている。
本 Draft はこれに JARVIS 行を **追加提案** する。

| コンポーネント | 問い | 出典 |
|---|---|---|
| **JARVIS** | **「人間は何を意図しているか」** | **【起案】** |
| Sequence Controller | 「次に何をするか」 | 【継承】 |
| MoCKA | 「それを許可できるか」「証拠はあるか」 | 【継承】 |
| Memory | 「過去に何があったか」 | 【継承】 |
| Orchestra | 「どのモデル・能力を使うか」 | 【継承】 |
| Relay | 「外部状態を同期する」 | 【継承】 |

**JARVIS は「次に何をするか」を答えてはならない。** それは Sequence Controller の問いである。

---

## 第2章 上位規範からの継承(変更不可)

本章は既存の Active/RATIFIED 規範をそのまま引き写したものである。
**本 Draft はこれらを一切変更しない。** JARVIS がこれらに反することは制度違反である。

### 2.1 PHI-OS 制度憲法 7原則【継承 — `PHI_OS_CONSTITUTION_v1.md` 第2章、RATIFIED】

| 原則 | JARVIS への適用(本 Draft の読み替え) |
|---|---|
| 原則1: Event は唯一の事実である | JARVIS の対話内容・意図解釈は、Event として記録されない限り制度上存在しない |
| 原則2: PHI-OS のみが制度を定義できる | **JARVIS は制度を定義できない。** JARVIS Constitution 自身の制定も Gate Authority の承認を要する |
| 原則3: Gate のみが制度変更を承認できる | JARVIS を経由した制度変更は Gate を通過しなければ Shadow 状態であり効力を持たない |
| 原則4: DB は保存媒体であり真実ではない | JARVIS は DB 内容を制度的事実として引用してはならない |
| 原則5: Derived View は派生情報である | JARVIS の出力・要約・提案はすべて Derived View であり、制度上の権威を持たない |
| 原則6: Meaning が制度上の意味を決定する | JARVIS 自身が Meaning 未定義であれば、いかなる Institution・Gate にも制度接続できない |
| 原則7: Institution が責任主体となる | JARVIS は単一の主 Institution に帰属しなければならない(帰属先は **【未裁定】**、HG-J02) |

原則1の系として `PHI_OS_CONSTITUTION_v1.md` 1.2 は
**「沈黙の禁止 — 記録なき作業はMoCKAとして存在しない」** を掲げる。JARVIS にも同様に適用される。

### 2.2 Human Gate 2層分離【継承 — `mocka_human_gate_decision_definition_v1.md`】

```
Human Gate Core         … 評価機構(自動)。判断材料の生成のみ
Human Gate Finalization … きむら博士本人。APPROVE/HOLD/REJECT/DEFER の確定
```

同文書 §7(最重要)原文:
> APPROVE/HOLD/REJECT/DEFER の確定は Human Gate Finalization(博士本人)のみが行う。
> Core がこれを単独で確定することは禁止。

同文書 §6: Human Gate Core の出力構造に **`decision` フィールドを含めてはならない**。

**JARVIS への適用【起案】:** JARVIS は Human Gate Core より下位の層であり、
Core が持たない権限を JARVIS が持つことはあり得ない。
したがって **JARVIS の出力にも `decision` フィールドを含めてはならない。**

### 2.3 禁止構造【継承 — `mocka_hab_human_gate_relation_v1.md` §4】

同文書が明示的に禁止する3構造:

- **直接遷移**: Human Gate を経由しない ACTIVE 遷移
- **自動裁定ループ**: Human Gate Core → 自動 APPROVE 確定
- **HAB の意思化**: 状態記述層が「判断主体」になる構造

同文書 §7:
> 「評価は機械化できるが、遷移は人間にしか起こせない」

### 2.4 Evidence Supremacy と未検証文脈の隔離【継承 — `DC_20260730_009`、Active】

継続前提の文章が提示された場合、**必ず以下の順序で確認する**:

```
(1) 現在の会話履歴
(2) リポジトリ内の実ファイル(一次証拠)
(3) Decision Ledger
(4) Event Ledger
(5) その他の履歴
```

一致する証拠が存在しない場合は「**未検証文脈(Unverified Context)**」として隔離し、作業を進めない。
**推測・補完・記憶による接続は禁止する。**

**JARVIS への適用:** JARVIS は「意図理解」を責務とするため、
本原則に最も強く拘束される層である(§5.2 参照)。

### 2.5 境界と Adapter の権限【継承】

| 出典 | 内容 |
|---|---|
| `DC_20260728_003`(Active) | PHI-OS Core と MoCKA Governance Runtime は別レイヤー。**PHI-OS Core から MoCKA 本体への直接 import 禁止**。接続は PHL/Relay Interface 経由のみ |
| `DC_20260729_013` D-02(Active) | Adapter = Translation Boundary。**禁止**: 意思決定生成 / ポリシー変更 / 権限判断 / Human Gate 代替 / 証跡改変 |
| `DC_20260729_013` D-03(Active) | Authority Ownership: PHI-OS = Runtime Coordination / Execution Control / Human Gate Routing、MoCKA = Evidence Management / Decision Evidence / Audit Intelligence / Governance Analysis、**Human = Architecture Authority / Policy Change Approval / Irreversible Decision** |
| RC-011 `phios/phl/relay_client.py`(実装確認済み) | PHI-OS → MoCKA は `localhost:5002/mcp` と `localhost:5000/api/gate/audit` のみ、read-only allowlist 強制 |

### 2.6 Decision Identity【継承 — `DC_20260801_002`、Active】

- **HG-1**: COLLISION 発生時の自動修復を禁止する
- **P-1**: 同一 Decision ID の複数行は原則異常
- **HG-3**: 検査失敗時は処理を停止する

### 2.7 Encoding【継承 — `CONSTITUTION.md`(MoCKA Encoding Policy v1.01 FINAL)】

UTF-8 を唯一の正規形とする。文字化け断片検知時は直ちに HALT する。

---

## 第3章 JARVIS の権限境界

### 3.1 JARVIS が実行できること【起案】

`PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md` §5 が Sequence Controller に許した範囲を
上限とし、JARVIS はそれ以下に留まる。

| # | 許可行為 | 条件 |
|---|---|---|
| A-1 | 人間の発話・意図の**解釈候補**の生成 | 候補であることを明示する。確定として提示しない |
| A-2 | 解釈候補に対応する**既存 Evidence の提示** | §2.4 の5段階確認を経た一次証拠のみ |
| A-3 | 下流層(Sequence Controller / MoCKA)への**要求の受け渡し** | 変換のみ。内容の付加・省略をしない |
| A-4 | Human Gate への**提示材料の整形** | `decision` フィールドを含めない(§2.2) |
| A-5 | 自身の入出力の **Event 記録** | §6 の記録義務に従う |
| A-6 | 未検証文脈の**検出と隔離報告** | §2.4 |

### 3.2 JARVIS が実行できないこと【起案】

| # | 禁止行為 | 根拠 |
|---|---|---|
| P-1 | 制度の新設・変更・廃止 | 原則2(RATIFIED) |
| P-2 | APPROVE/HOLD/REJECT/DEFER の確定 | `mocka_human_gate_decision_definition_v1.md` §7 |
| P-3 | 出力に `decision` フィールドを含めること | 同 §6 |
| P-4 | Evidence なしの実行・提案 | `PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md` §5 / `DC_20260730_009` |
| P-5 | Gate を迂回した Event 生成 | 原則3 / `PHI_OS_CONSTITUTION_v1.md` §5.1 |
| P-6 | DB への直接書き込み | 原則4 / §5.1 |
| P-7 | Derived View の直接編集 | 原則5 / §5.4 |
| P-8 | 「次に何をするか」の決定 | §1.4(Sequence Controller の責務) |
| P-9 | 「それを許可できるか」の判断 | §1.4(MoCKA の責務) |
| P-10 | Authority の変更・委譲 | 原則2 / Authority一意性原則 |
| P-11 | 推測・記憶による文脈接続 | `DC_20260730_009` |
| P-12 | 自身の権限範囲の自己拡張 | §3.3 |
| P-13 | MoCKA 本体への直接 import | `DC_20260728_003` |
| P-14 | 人間の裁定の代行・先取り | `mocka_hab_human_gate_relation_v1.md` §4「自動裁定ループ」禁止 |

### 3.3 自己適用原則【継承+起案】

`PHI_OS_CONSTITUTION_v1.md` 原則2 は
「PHI-OS 自身の変更も Gate Authority の承認を要する(自己適用原則)」と定める。

**【起案】** JARVIS についても同様とし、加えて次を課す:
**JARVIS は自身の Constitution・権限範囲・禁止事項を変更する提案を、自ら実行してはならない。**
変更提案の作成は許可するが、その採否は Human Gate Finalization に限る。

### 3.4 自動裁定化リスクの自己点検【起案】

本 Draft が「自動承認ループ」を作っていないことを、以下により確認する。

| 点検項目 | 本 Draft での扱い |
|---|---|
| JARVIS が承認を確定できる条項があるか | **なし**(P-2) |
| JARVIS の出力が承認とみなされる経路があるか | **なし**(P-3、出力に decision を持たない) |
| JARVIS が Human Gate をスキップできる条件があるか | **なし**(条件付きスキップ条項を一切設けていない) |
| 「軽微な変更は自動承認」等の閾値条項があるか | **なし**(意図的に設けていない) |
| JARVIS が自身の権限を拡張できるか | **なし**(P-12、§3.3) |
| 沈黙・無応答が承認とみなされる条項があるか | **なし** |

**この点検表自体も Human Gate の検証対象である。** 起草者による自己点検は、検証の代替にならない。

---

## 第4章 接続経路

### 4.1 JARVIS が使用してよい経路【起案】

既存の実測済み経路(`JARVIS_RUNTIME_FLOW.md`)の範囲内に限定する。**新規 Runtime を作らない。**

| 用途 | 経路 | 状態 |
|---|---|---|
| 記録(write) | `phi_os/event_gate.py: process_event()` 経由のみ(MCP `mocka_write_event` → `POST localhost:5000/api/gate/event`) | 実測済み |
| 参照(read) | MCP read 系 tool / `/api/gate/audit` | 実測済み |
| 裁定の提示 | Human Gate(経路は **【未裁定】**、§7.2) | — |

`phi_os/event_gate.py: process_event()` の docstring は
**「これ以外に events 保存を行う経路は制度上存在しない」** と宣言している。JARVIS もこれに従う。

### 4.2 read-only 原則【起案】

`DC_20260728_003` と RC-011 が確立した「境界越えは read-only allowlist」の様式を JARVIS にも適用する。

**JARVIS が write できるのは、自身の入出力を記録する Event のみとする。**
Decision Ledger・TODO・Registry・Integrity 台帳への書き込みは JARVIS の権限外とする。

### 4.3 新規 Runtime 禁止【起案】

本 Draft は JARVIS のための新規プロセス・新規ポート・新規 DB を一切定義しない。
JARVIS の実装形態(既存プロセス内か、別プロセスか)は **【未裁定】**(HG-J05)。

---

## 第5章 Context に関する規律

`ジャビス.md` §5 は Context Governance を PHI-HAB の責務としているが、
JARVIS は Context の**利用者**であるため、利用側の規律を定める。

### 5.1 Context の権威【起案】

- JARVIS が保持する会話文脈は **Derived View** であり、制度上の事実ではない(原則5)
- 制度上の事実の確認は常に Event Ledger を参照して行う(原則1)
- 会話文脈と Event Ledger が矛盾する場合、**Event Ledger が優先する**

### 5.2 未検証文脈の取り扱い【継承 — `DC_20260730_009`】

JARVIS は「意図理解」を担うため、人間の発話に含まれる**継続前提**(過去にそう決めた、という前提)を
最初に受け取る層になる。したがって §2.4 の5段階確認を **JARVIS の一次責務**とする【起案】。

一致する証拠が得られない場合、JARVIS は次を行う:
1. 当該前提を「未検証文脈」として明示的にラベル付けする
2. 作業を進めない
3. 隔離したことを人間に報告する

**推測で補完して会話を継続してはならない。**

### 5.3 Context Compiler の位置づけ【未裁定】

`ジャビス.md` §5 の Context Compiler は
`Human Thought → AI Analysis → Principle Extraction → Context Update Candidate → Human Gate → Official Context`
というフローを持ち、**Human Gate を内包している**。

これが `mocka_human_gate_decision_definition_v1.md` の Core/Finalization 2層分離のどちらに接続するかは、
いずれの一次資料にも記載がない。**本 Draft では確定させない**(HG-J04)。

---

## 第6章 記録義務

### 6.1 記録の原則【継承 — 原則1 / `PHI_OS_CONSTITUTION_v1.md` 1.2「沈黙の禁止」】

記録なき JARVIS の動作は、制度として存在しない。

### 6.2 記録すべき事象【起案】

| # | 事象 | 理由 |
|---|---|---|
| R-1 | 人間の意図に対する解釈候補の生成 | 後から解釈の妥当性を検証可能にするため |
| R-2 | 未検証文脈の検出と隔離 | §5.2。隔離判断自体が監査対象 |
| R-3 | 下流層への要求の受け渡し | 変換に付加・省略がなかったことの検証 |
| R-4 | Human Gate への提示材料の生成 | 裁定材料の出所の追跡 |
| R-5 | JARVIS 自身の制約に抵触した要求の拒否 | P-1〜P-14 の実効性の証拠 |

### 6.3 記録形式【未裁定】

既存 `events` テーブルは 5W1H スキーマ(34カラム)を持ち、
`who_actor` / `what_type` / `where_component` 等が既に定義されている。
JARVIS 用の `what_type` 値を新設するか既存値を使うかは **【未裁定】**(HG-J06)。

`PHI_OS_CONSTITUTION_v1.md` §6.5 は違反記録の形式を
`INCIDENT: {違反種別} — {対象Artifact} — {対処状態}` と定めており、これは変更しない【継承】。

---

## 第7章 用語の未解決問題(本 Draft では確定させない)

### 7.1 "PHI-HAB" の四義性【未裁定 — 最重要】

**"HAB" は少なくとも4つの異なる対象を指している。** うち Active な Decision を持つのは1つのみである。

| # | 呼称 | 出典 | 定義 | 制度状態 |
|---|---|---|---|---|
| HAB-A | Human Authority Boundary | `docs/governance/mocka_hab_v1_contract.md` | MoCKA 内部の統治層。状態 STABLE/DRAFT/REVIEW/STASIS/ACTIVE | **DRAFT** |
| HAB-B | HAB spine | `docs/contracts/phase8_hab_runtime_integration_v1.md` + `semantic/query_engine/execution_orchestrator.py` | Phase7 A〜E 構造の実行系 | DRAFT / コードは未配線 |
| HAB-C | PHI-HAB(構想) | `Desktop\aimd\ジャビス.md` §4 | 人間とAIの活動環境。Context Core / Compiler / Doctor / AI Adapter | **未登録** |
| **HAB-D** | **PHI-HAB(制度)** | **`DC_20260729_008`** | **PHI-REG-02(a) = Chrome拡張JSハブスタック(Connection/協調層)。`PlanningCaliber/workshop/phi-os/extension/`, `core/`, `adapters/`** | **Active(採用済み)** |

**HAB-C と HAB-D は同じ語 "PHI-HAB" を使いながら、指す対象が異なる。**
- HAB-D(Active): Chrome拡張の**接続・協調層**
- HAB-C(未登録): **Context 管理環境**

`ジャビス.md` の階層図(`JARVIS → PHI-HAB → Institutional Runtime`)を制度上どう読むかは、
HAB-C と HAB-D のどちらを指すかで**まったく別の設計になる**。

**本 Draft はこれを確定させない。** Human Gate 提示事項 HG-J03。

`PHI_OS_CONSTITUTION_v1.md` 末尾の「追加記録: PHI-OS名称の二義性について」(2026-07-25、HG-3 承認済み)は、
同種の名称衝突を**憲法本体への追記**という形で処理した先例である【継承 — 先例として記録】。

### 7.2 Human Gate の実装分散【未裁定】

`phi_os/human_gate.py` は
> 基本原則: PHI-OSがHuman Gateの唯一の状態管理責務を持つ。…(本モジュールが単一の真実)

と宣言するが、実測では以下が並存する(`JARVIS_CAPABILITY_INVENTORY.md` §2.4):

1. `phi_os/human_gate.py`(**`human_gate_bp` が `app.py` に未登録 = HTTP 到達不能**)
2. `app.py` `/decision/approve` `/decision/reject`(稼働中)
3. `governance/mocka_git_safe_commit.py` の Core System File 除外
4. `semantic/query_engine/human_gate.py`(未配線)
5. `governance/human_gate_continuity.py`

**JARVIS がどの Human Gate に接続するかを、本 Draft では確定させない**(HG-J04)。

### 7.3 P-DERS【未裁定 — Phase 0 の記載を訂正】

`JARVIS_GAP_ANALYSIS.md` G-11 は P-DERS を **Missing** と判定したが、
その調査範囲は `*.md` / `*.py` に対する grep であり、**Decision Ledger(`.jsonl`)を含んでいなかった**。

Decision Ledger を走査した結果、以下が実在する(Confirmed):

| Decision | 内容 |
|---|---|
| `DC_20260730_001`(p-DERS 版) | p-DERS 形式理論トラック(Track A)— Causal Projection 選定〜Compositional Safety Theorem 部分証明 |
| `DC_20260730_002`(p-DERS 版) | Sound Local Approximation の証明と「第3の軸」への位置づけ確定 |
| `DC_20260730_003`(p-DERS 版) | MoCKA Governance Function G の実態調査 — Track A 理論との関係 |
| `DC_20260730_009` | `pDERS_causal_projection_v0.1.md` / `pDERS_overlap_consistency_v0.1.md` / R_i/Ω_i/Ψ_i 三分割構造 / Local Invariant Gate / Zenodo アーカイブ / Rust プロトタイプ の**6件を「未検証文脈」として隔離**し、継続対象としないと裁定 |

**訂正後の判定:** P-DERS は「Missing」ではなく、
**形式理論トラックとして Decision が存在し、かつ一部の前提資料は明示的に隔離済み**である。

**注記(Decision Identity):** `DC_20260730_001` `_002` `_003` は
PHI-OS Milestone 系と p-DERS 系で**同一 ID が重複している**。
これは `DC_20260801_002` の **P-1「同一 Decision ID の複数行は原則異常」** に該当する観測事実である。
本 Draft は修復を行わない(`DC_20260801_002` HG-1「自動修復禁止」)。**観測の記録のみとする。**

### 7.4 Authority Flow【継承 — `DC_20260729_009` により Pending】

PHI-Con / PHI-Core 間の Authority 階層は `DC_20260729_009`(Active)により
**Option D(条件付き Pending Resolution)= 未解決のまま保持**と裁定済み。

**JARVIS の Authority 上の位置づけも、この Pending が解けるまで確定できない**【未裁定】(HG-J02)。

---

## 第8章 本 Draft が決めない事項

以下は意図的に未着手とする。憶測で埋めない。

| # | 事項 | 理由 |
|---|---|---|
| N-1 | JARVIS の実装形態(プロセス構成・言語・配置) | 実装は本 Draft の対象外。禁止事項に明記されている |
| N-2 | HAB の実装 | 禁止事項に明記されている |
| N-3 | 自律Agent権限 / 音声UI / 常駐プロセス / 外部デバイス制御 / 完全自動実行 | `PHI_SEQUENCE_CONTROLLER_DESIGN_SCOPE_v0.1.md` §7 が Phase J5 対象として現スコープ外と明記 |
| N-4 | ジャービス化ロードマップ J3〜J5 の内容 | 未着手。着手指示は別途要する |
| N-5 | Context Core の集約方法 | `JARVIS_GAP_ANALYSIS.md` G-02 は差分の観測のみで、対処方法を含まない |
| N-6 | JARVIS の受入基準・完了条件 | 一次資料が存在しない【Unknown】 |
| N-7 | JARVIS と既存 `gateway/adapter_gpt.py` の関係 | 帰属を定める文書が存在しない【Unknown】 |

---

## 第9章 Human Gate 提示事項

本 Draft が Human Gate Finalization に提示する判断項目。
`mocka_human_gate_decision_definition_v1.md` §6 に従い、**本章に `decision` 値は含めない。**

| ID | 判断事項 | 論点 | 依存 |
|---|---|---|---|
| **HG-J01** | `ジャビス.md` を JARVIS の定義出典として採用するか | `DC_20260729_001` が Deferred と裁定済み。採用は同 Decision の再評価を伴う可能性がある | `DC_20260729_001` |
| **HG-J02** | JARVIS の帰属 Institution と Authority 上の位置 | 原則7 は単一 Institution 帰属を要求。ただし Authority Flow は `DC_20260729_009` により Pending | `DC_20260729_009` |
| **HG-J03** | "PHI-HAB" が HAB-C / HAB-D のどちらを指すか | §7.1。HAB-D は Active、HAB-C は未登録。同語異義の解消先例は `PHI_OS_CONSTITUTION_v1.md` 末尾追記 | `DC_20260729_008` |
| **HG-J04** | JARVIS が接続する Human Gate の実体 | §7.2。5系統が並存。`phi_os/human_gate.py` は HTTP 到達不能 | — |
| **HG-J05** | JARVIS の実装形態(新規 Runtime を作らない前提の可否) | §4.3。本 Draft は新規 Runtime を定義していない | — |
| **HG-J06** | JARVIS の Event 記録形式(`what_type` 新設の要否) | §6.3 | — |
| **HG-J07** | 第3章 権限境界(A-1〜A-6 / P-1〜P-14)の採否 | 本 Draft の中核。【起案】であり未裁定 | §2 の各 Active Decision |
| **HG-J08** | §3.4 自己点検表の妥当性検証 | 起草者の自己点検は検証の代替にならない | `mocka_hab_human_gate_relation_v1.md` §4 |
| **HG-J09** | 本 Draft を Decision Ledger に登録するか、登録するならどの単位で分割するか | `DC_20260729_007`(文言追加は事前承認対象)の運用ルールに関わる | `DC_20260729_007` |

---

## 第10章 発効条件

【起案】本 Draft は、以下がすべて満たされたときにのみ効力を持つ。

1. 第9章の HG-J01〜HG-J09 について Human Gate Finalization による裁定が行われること
2. 裁定結果が Decision Ledger に記録されること
3. `PHI_OS_CONSTITUTION_v1.md` 原則2「PHI-OS 自身の変更も Gate Authority の承認を要する」に従い、
   Gate Authority の承認を経ること
4. 本文書の Status が DRAFT から変更されること

**上記が満たされるまで、本文書は「参照可能な設計文書」に過ぎない。**
これは `mocka_hab_v1_contract.md` §9・`mocka_human_gate_decision_definition_v1.md` §9 が
自らに課したのと同じ位置づけである【継承 — 先例】。

---

## Knowledge Lineage

**Document:** JARVIS_CONSTITUTION_DRAFT.md
**Status:** DRAFT(未裁定、Decision Ledger 未登録、実装なし)
**Created:** 2026-08-04
**Origin:** JARVIS Phase 1 — 制度定義(実装ではない)
**Parent Documents:**
- `PHI_OS_CONSTITUTION_v1.md`(PHI-OS-CONST-001、RATIFIED v1)
- `docs/governance/mocka_human_gate_decision_definition_v1.md`
- `docs/governance/mocka_hab_v1_contract.md` / `mocka_hab_human_gate_relation_v1.md`
- `docs/audits/PHI_SEQUENCE_CONTROLLER_ARCHITECTURE_v1.0.md`
- `docs/audits/PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1.md`
- `docs/audits/JARVIS_{ARCHITECTURE_CURRENT,CAPABILITY_INVENTORY,BOUNDARY_ANALYSIS,GAP_ANALYSIS,RUNTIME_FLOW}.md`
- `C:\Users\sirok\Desktop\aimd\ジャビス.md`(Decision Ledger 未登録)
**Referenced Decisions:** `DC_20260728_002` / `DC_20260728_003` / `DC_20260729_001` / `DC_20260729_007` /
`DC_20260729_008` / `DC_20260729_009` / `DC_20260729_013` / `DC_20260730_009` / `DC_20260801_002` /
`DC_20260730_001`(p-DERS 版) / `DC_20260730_002`(p-DERS 版) / `DC_20260730_003`(p-DERS 版)
**Supersedes:** なし
**Affected Components:** なし(コード変更・Runtime 作成・HAB 実装のいずれも行っていない)
**Revision History:**
- R1(2026-08-04): 新規作成。【継承】【起案】【未裁定】【Unknown】を分離して記載。
  第7.3 で `JARVIS_GAP_ANALYSIS.md` G-11(P-DERS = Missing)を調査範囲不足として訂正。
  実装・Decision Ledger 登録は無し。

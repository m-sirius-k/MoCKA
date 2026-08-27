# Evidence Entitlement Boundary N3 Reassessment v1.0

```
EVIDENCE ENTITLEMENT BOUNDARY
N3 REASSESSMENT

Current Status:
N3

Evidence Entitlement Responsibility:
NECESSARY

Existing Evidence Level Coverage:
NONE

Reverification Coverage:
NONE

Human Gate Coverage:
NONE

Canonical Design Coverage:
NONE

Independent Boundary Necessity:
CONFIRMED

Implementation Authorization:
NOT AUTHORIZED
```

- Document ID: AUDIT-EEB-003
- Class: Necessity Reassessment (read-only investigation)
- Date: 2026-08-27
- Author: Claude-opus-5 (くろこ)
- Directive: R01 `Evidence Entitlement Boundary N2からN3判定への残存UNKNOWN解消調査`
- Base commit: 23874be (branch `claude/mocka-evidence-proposition-boundary-1m781u`)
- Predecessors: AUDIT-EEB-001 (0b46bd9, Forensics) / AUDIT-EEB-002 (23874be, Necessity N2)
- Classification: Documentation only. コード変更なし / Schema変更なし / threshold変更なし /
  Ledger変更なし / DB変更なし / TODO変更なし / テスト変更なし / Human Gate変更なし /
  Canonicalization変更なし / 新Boundary実装なし。

---

## 0. 判定変更の要点

AUDIT-EEB-002 は N2 と判定した。その理由は"既存機構に責務がない"ことが
不確かだったからではなく、**3件のUNKNOWNが"読めない / 未解決"の状態にあり、
既存機構が責務を担っている可能性を否定できなかった**からである。

本調査でその3件すべてが解消された。解消の方向は以下の通りである。

| # | AUDIT-EEB-002 での状態 | 本調査での結果 |
|---|---|---|
| K1 `Evidence Level階層` の内容 | **読めない** (Decision Identity Collision) | **読めた**。内容は provenance分類 + 優先順位規則であり、Entitlement を含まない |
| K2 `再検証の手続き` の所在 | **未整理 / 未解決** | **解決済み**。HG-C10 で正式に候補提示され、Human Authority が**選択しなかった** (Y-4) |
| K3 Canonical Source 競合 | **どちらが Canonical か不明** | **確定**。`MOCKA_CHARTER_v2.md` = CANONICAL、README Core Articles = DERIVED |

**"否定できなかった"から"読んだ結果、担っていない"へ変わった。**
これが N2 から N3 への変更理由であり、新しい設計判断ではない。

---

## 1. Purpose

AUDIT-EEB-002 の N2 判定を阻害していた3件のUNKNOWNのみを対象に解消し、
`Evidenceが何を確立する資格を持つか` という責務が既存MoCKAのどこかで
既に担われているかを最終判定する。

新しい設計を作らない。Evidence Entitlement Boundary を実装しない。
N3 という結論を先に置かない。

## 2. Scope

### 2.1 対象 (3件のみ。調査対象を広げない)

1. `DC_20260730_001` -> Evidence Level Hierarchy
2. `G5_HGC10` -> Reverification Procedure
3. Core Articles 0-10 VS `MOCKA_CHARTER_v2.md` -> Canonical Authority

### 2.2 対象外

上記3件に関係しない新規調査。実装。設計提案。

### 2.3 結論誘導の禁止 (指示書 2.2)

`Evidence Level階層にはEntitlementが存在しない` も
`Evidence Level階層がEntitlementを既に解決している` も仮定していない。
第4章で一次Evidenceの原文を取得し、第5章で項目別に判定した。

## 3. Investigation Method

### 3.1 K1 の突破口

`data/decisions/decision_ledger.jsonl` は .gitignore により本cloneに存在せず、
`mocka_decision_get` は同一IDの最新行のみを返す。AUDIT-EEB-002 はここで停止した。

本調査は別経路を用いた。`mocka_mcp_server.py:1004-1024` は
`mocka_decision_write` の実行時に **companion event** を events.db へ書き込み、
その `short_summary` に `context` / `decision` / `rationale` / `impact` の
全文を格納する。したがって **Decision Ledger 184行目の内容は events.db 側に
独立して保存されている**。`mocka_search` の全文検索によりこれを回収した。

これは回避策ではない。既存の正規記録経路が二重化されていたことの利用であり、
読み取り専用である。

### 3.2 証拠分類

`OBSERVED` / `INFERRED` / `UNKNOWN` と、
`CODE` / `TEST` / `DATA` / `DOCUMENT` / `EXECUTION` / `ARCHITECTURAL INFERENCE` を付与する。
`DECLARED` と `ENFORCED` を分離する (第6章)。

### 3.3 表記

CLAUDE.md の CP932汚染防止規約に従い非ASCII装飾記号を使用しない。
一次資料からの逐語引用 (blockquote `>`) のみ原文の角括弧を保持する。
引用の改変は本報告書が依拠する Evidence の同一性を損なうためである。

---

## 4. DC_20260730_001 Forensics

### 4.1 Decision Identity Collision の時系列 (DATA / OBSERVED)

| 行 | 主題 | 記録時刻 (UTC) | 取得経路 |
|---|---|---|---|
| 184 | Evidence Level階層・役割固定・セッション同期プロトコルの採用 | 2026-07-29T22:43:40Z | companion event `E20260730_020387442514a` |
| 193 | p-DERS形式理論トラック (Track A) | 2026-07-30T04:26:58Z | `mocka_decision_get` (最新行) |

184行目が先、193行目が約5時間43分後。
`mocka_decision_get("DC_20260730_001")` が返すのは 193 のみである。
**したがって 193 の内容だけを Canonical Evidence として扱ってはならない**
(指示書 STEP 1-A の指示に一致)。

Collision 自体は 2026-07-31 に `DECISION_IDENTITY_INCIDENT_TRIAGE.md` で検出済み。
本調査は Collision の解消を行わない (Read-only)。

### 4.2 184行目の原文 (DATA / OBSERVED)

companion event `E20260730_020387442514a`
(when_ts 2026-07-29T22:43:40.387479+00:00, who_actor きむら博士,
free_note `decision_ledger,DC_20260730_001,Active`) の `short_summary` より。

context (抜粋):
> 本セッションで2件のcross-session contamination事故が発生した(1: Genesis Phase関連の
> 指示混入、2: 本セッションで作成していない「PHI-OS Integration Migration」status
> (mocka_integration_adapter.py・commit dd198bd5451b・baddd113d等)がきむら博士の発言
> として提示された事例。いずれもgit log/find等での検証により、該当commit・fileが
> このリポジトリに存在しないことを確認し、事実として扱うことを拒否した)。

decision (全文):
> 今後の標準運用として以下を採用する。(1) Evidence Level階層: Level 1(確定、この
> チャットで提示された内容・実際のリポジトリ確認結果・git log/grep/test結果)、
> Level 2(準確定、ローカル実測結果のユーザー報告)、Level 3(参考、過去チャットの記憶・
> 推測・設計案)。Level 3はLevel 1・2と矛盾したら必ず破棄する。(2) 役割固定: Claude Code
> は実装・テスト・git操作・リポジトリ監査のみを担当し、アーキテクチャ・判断整理・監査・
> 長期的一貫性確認はきむら博士が担当する。(3) セッション同期: 各セッション開始時に、
> きむら博士がCurrent Verified State(Repository/Commit/Verified Documents/Current Task/
> Blockers/Evidence)を提示し、Claude Codeはその内容のみを基準に判断する。
> (4) Evidence First順序: Evidence -> Analysis -> Decision -> Implementation ->
> Verificationの順序を崩さない。

impact (抜粋):
> 今後のClaude Codeとのやり取りは本プロトコルに従う。特に、存在が確認できていない
> commit/fileを事実として扱わない、過去の記憶よりも現在提示されたEvidenceを優先する、
> という運用を徹底する。

### 4.3 継承先 (DATA / OBSERVED)

`DC_20260730_002` (line 185, companion event `E20260730_15508419841d5`) が
184行目を明示的に継承している。

> DC_20260730_001のCurrent Verified Stateテンプレートに、Verification Timestamp
> (確認時点の明示)とVerification Scope(確認範囲の明示)の2項目を追加する。
> (中略) DC_20260730_001の(1)Evidence Level階層・(2)役割固定・(4)Evidence First順序は
> 変更なし。

したがって 184行目は Collision により**上書きされたのではなく、
後続 Decision に継承されて生きている**。Withdrawn でも Superseded でもない。

---

## 5. Evidence Level Hierarchy

### 5.1 STEP 1-B 責務判定 (指示書指定の11項目)

原文 (4.2) に対して一項目ずつ判定する。名称による判断は行わない。

| # | 問い | 判定 | 根拠 (原文の該当部分) |
|---|---|---|---|
| 1 | Evidenceの品質を分類するか | **YES** | Level 1/2/3 の3段階分類が存在する |
| 2 | Evidenceの信頼性を分類するか | **YES** | 確定 / 準確定 / 参考 |
| 3 | Evidenceの provenance を分類するか | **YES** | 分類基準が**出所そのもの**である。L1=このチャット/リポジトリ確認/git log/grep/test、L2=ローカル実測のユーザー報告、L3=過去チャットの記憶/推測/設計案 |
| 4 | Evidenceの sufficiency を分類するか | **NO** | 量・充足度に関する記述が原文に存在しない |
| 5 | Evidenceが特定Propositionを支持できる範囲を定義するか | **NO** | Level と命題の対応規則が原文に存在しない。Level N が何を言えるかの記述が皆無 |
| 6 | EvidenceからPropositionへの変換条件を定義するか | **NO** | 変換条件の記述なし。(4) Evidence First順序は**順序**を定めるが**条件**を定めない |
| 7 | EvidenceとPropositionの関係を検証するか | **NO** | 検証手順の記述なし |
| 8 | Counter-evidenceを考慮するか | **PARTIAL** | `Level 3はLevel 1・2と矛盾したら必ず破棄する`。ただし対象は**Evidence間の矛盾**であり、Evidence対Propositionではない。かつ L1対L2、L1対L1 の矛盾規則は存在しない |
| 9 | Contextを考慮するか | **NO** | context の記述なし |
| 10 | Timeを考慮するか | **PARTIAL** | `過去チャットの記憶` を L3 とすることで時間的近接性が間接的に反映されるが、Evidence の有効期限・失効の概念はない |
| 11 | Human Gate以前の判定として機能するか | **YES (ただし人間の運用規則として)** | `今後のClaude Codeとのやり取りは本プロトコルに従う`。適用対象はAIの会話上の振る舞いである |

### 5.2 最重要項目の判定

> Evidenceが「何を確立する資格を持つか」を制約しているか

**判定: NO (OBSERVED)**

Evidence Level階層は **Evidence 側にのみ項が存在する構造** である。
Level は Evidence の出所を3段階に格付けし、矛盾時にどれを破棄するかを定める。
**Proposition 側の項が存在しない。** Level N の Evidence が
どの範囲の命題を確立してよいかという対応規則は、原文のどこにも存在しない。

具体的に言えば、`ast.parse が成功した` という観測は
Level 1 (実際のリポジトリ確認結果・test結果) に分類される。
Level 1 は最上位である。しかし Level 1 であることは、
その観測が `FIXED (修正済み)` という命題を確立してよいことを意味しない。
Evidence Level階層はこの飛躍について何も述べていない。

### 5.3 責務の所属先 (OBSERVED)

Evidence Level階層が実際に担っている責務は、AUDIT-EEB-002 第8章で
既に代替不能と判定済みの2機構に一致する。

| Evidence Level階層の要素 | 該当する既存責務 | AUDIT-EEB-002 での判定 |
|---|---|---|
| Level 1/2/3 の格付け基準が**出所**である | **Provenance** (STEP 4-A) | 代替不可 **NO** |
| `Level 3はLevel 1・2と矛盾したら必ず破棄する` | **Arbitration** (STEP 4-C) | 代替不可 **NO** |

**Evidence Level階層は新しい責務を導入していない。**
Provenance分類 + 源泉優先順位という、既に `NO` と判定済みの2責務の
別表現である。したがって AUDIT-EEB-002 の STEP 4 判定は、
Evidence Level階層の内容が判明した後も変わらない。

補足 (OBSERVED): この構造は `DC_20260730_009` (Evidence Supremacy) の
5段階確認順序と同型である。両者はいずれも
"どの出所を信じるか"を定め、"その出所が何を言えるか"を定めない。

### 5.4 Evidence First順序について

原文 (4) は以下を定める。

> Evidence First順序: Evidence -> Analysis -> Decision -> Implementation ->
> Verificationの順序を崩さない。

これは本調査にとって**両義的**であるため、正確に記録する。

- **N3を弱める側**: これは Evidence から Analysis への段が制度上存在することの
  Canonical な明示である。段の存在自体は既に認められている。
- **N3を強める側**: 定めているのは**順序**のみであり、
  Analysis が Evidence から正当に導かれたかを検査する条件は存在しない。
  順序を守っていても、Evidence が支持しない Analysis を置くことは可能である。

**判定: 順序の規定であって、導出の妥当性の規定ではない (OBSERVED)。**

### 5.5 STEP 1-C: DECLARED と ENFORCED の分離

| 側面 | 状態 | 根拠 |
|---|---|---|
| DECLARED | **YES** | `DC_20260730_001` (Active、`DC_20260730_002` により継承確認済み) |
| ENFORCED (runtime) | **NO** | 第10章 PROBE。全 `.py` に対する `Evidence Level` の grep 結果 **0件** |

runtime 経路
```
Evidence -> Level evaluation -> Proposition formation
```
は存在しない。`Level evaluation` に相当するコードがリポジトリに1行も無い。

**Evidence Level階層はAIの会話運用プロトコルであり、実行時機構ではない (OBSERVED)。**

### 5.6 Existing Evidence Level Coverage 判定

```
Existing Evidence Level Coverage: NONE
```

`PARTIAL` としない理由: Coverage が問うのは
`Evidence Entitlement 責務のカバー率` である。5.2 の通り Entitlement 項が
構造的に存在しないため、部分的にも担っていない。
Provenance と Arbitration は担っているが、それらは別責務である (5.3)。

---

## 6. G5_HGC10 Reverification Trace

### 6.1 起点 (DOCUMENT / OBSERVED)

`G5_HGC10_DECISION_PREP_v0.1.md:157`:
> 候補 B (証拠間の不整合) は Evidence Supremacy と最も直接に接続するが、
> 同時に 再検証の手続きを要求する。手続きの所在は本資料では未整理

AUDIT-EEB-002 はここを K2 として UNKNOWN 保存した。

### 6.2 後続文書の探索結果 (STEP 2-A)

`mocka_search("再検証手続き")` および repository 検索により、以下の系列を特定した。

| 順 | 文書 | Event | 日時 (UTC) | 内容 |
|---|---|---|---|---|
| 1 | `G5_HGC10_DECISION_PREP_v0.1.md` | `E20260806_961696349f18e` | 2026-08-06T00:42:41Z | 未整理として提起 |
| 2 | `G5_HGC10_DECISION_INPUT_v0.1.md` | `E20260806_5828029439482` | 2026-08-06T00:53:02Z | **判断対象3 として正式に選択肢化** |
| 3 | `HG-C10_DECISION_RECORD_v1.0.md` | (repository内) | - | **Human Authority が裁定** |

### 6.3 判断対象3 の選択肢 (DATA / OBSERVED)

`E20260806_5828029439482` の記録より:

> 判断対象3 (Evidence 接続方式): 3-1 不一致記録そのものを新規 Evidence /
> 3-2 既存 Evidence への参照付与に留める /
> **3-3 再検証トリガーとし再検証結果を Evidence とする** / 3-4 博士指定

**再検証手続きは、選択肢 3-3 として Human Authority に正式に提示された。**

### 6.4 裁定結果 (DOCUMENT / OBSERVED)

`docs/governance/HG-C10_DECISION_RECORD_v1.0.md:51-58`:

> | 判断対象 | 候補 | 選択 |
> | 1 不一致の意味論 | A 制度と実装の乖離 / B 証拠間の不整合 / C 定義・設計・実装間の差異 / **D 複合階層分類** | **D** |
> | 3 Evidence 接続方式 | 3-1 新規 Evidence 化 / **3-2 既存 Evidence への参照付与** / 3-3 再検証トリガー / 3-4 指定 | **3-2** |

同 4.1:
> | **Y-4** | **不一致自体を Evidence 化しない。既存 Evidence への参照付与に留める** | 判断対象3 = 3-2 |

同 5.3 (判断理由):
> 不一致自体を大量の Evidence 化せず、既存 Evidence との関係性として保持する。
> 候補検知と最終意味確定を分離する。

### 6.5 判定

**再検証手続きは、Human Authority により正式に検討され、選択されなかった (OBSERVED)。**

これは実装漏れでも未着手でもない。**裁定された結果である。**
`HG-C10_DECISION_RECORD_v1.0.md:60` は
`不採用となった候補は却下ではなく、本裁定において選択されなかったものとして記録する`
と明記している。

さらに、判断対象1 において `候補 B (証拠間の不整合)` も選択されず `D` が選ばれた。
再検証手続きを要求する分岐 (候補B) 自体が採られていない。

したがって、AUDIT-EEB-002 の要因B
(`MoCKA自身は本件を手続きの不在として登録している`) は解消された。
その手続きは提示され、選択されなかった。**未整理ではなく、不採用である。**

### 6.6 STEP 2-B: 再検証と Entitlement の分離

指示書の警告に従い、両者を混同していないことを明示する。

| 概念 | 問い | MoCKA での状態 |
|---|---|---|
| Reverification | Evidence がまだ有効か | 機構なし (6.5)。加えて `is_fresh()` は経過時間を判定に用いない (AUDIT-EEB-002 §11) |
| Entitlement | Evidence がこの Proposition を確立する資格を持つか | 機構なし (第9章) |

仮に 3-3 が選択されていたとしても、それは Reverification 機構であり、
Entitlement を保証したとは限らなかった。
**本調査が確認したのは、そもそもどちらも存在しないという事実である。**

なお `Y-6` (`Unknown は保持するが、再評価条件または期限を付す`) は
再評価の一形態だが、対象は **Unknown 分類の停滞防止**であり、
Evidence が Proposition を支持するかの再評価ではない。混同しない。

```
Reverification Coverage: NONE
```

---

## 7. Canonical Source Arbitration

### 7.1 競合の内容 (DOCUMENT / OBSERVED)

| 文書 | 条項集合 |
|---|---|
| `docs/governance/MOCKA_CHARTER_v2.md` (702 bytes) | 第1条 - 第8条 (8条) |
| `README.md:174-186` (英語) | Article 0 - Article 10 (11条) |
| `README.md:801-810` (日本語) | 第0/2/4/6/8/10条 (6条抜粋) |

3者はいずれも異なり、README の英語版と日本語版すら一致しない。
README の両版はともに `MOCKA_CHARTER_v2.md` を
`Full Charter` / `全文` としてリンクしている。

### 7.2 制度上の採用記録 (DOCUMENT / OBSERVED)

日付ではなく採用記録で判定する (指示書 STEP 3-A)。

| 出典 | 記述 |
|---|---|
| `GOVERNANCE_CLASSIFICATION_v0.1.md:46` | `MOCKA_CHARTER_v2.md \| 憲法層 \| 文書名自体がCharterと自称、8条憲章として制定済み` |
| `GOVERNANCE_INVENTORY_v0.1.md:165` | `MOCKA_CHARTER_v2.md \| MOCKA CHARTER v2.0 \| Charter \| 制定済み(8条憲章) \| 全体基盤` |
| `GOVERNANCE_RELATIONSHIP_MAP_v0.1.md:36` | `Charter(8条憲章)として全体基盤に位置づけ` |
| `MOCKA_GOVERNANCE_CATALOG_DRAFT_v0.1.md:19,67` | 憲法層5件の1つ。`MOCKA_CHARTER_v2を最上位とし` |

**4つの独立した governance 分類文書が、一致して
`MOCKA_CHARTER_v2.md` (8条) を憲法層・制定済み・最上位と記録している。**

対して、**README を governance 文書・憲法層として分類した記録は
1件も存在しない** (上記4文書のいずれにも記載なし)。

git 履歴による判定は不可能である (OBSERVED): 両ファイルとも
`aed114f 2026-08-10 auto sync` の単一 commit でのみ現れる。
リポジトリ履歴が同期時に集約されており、作成時期を git から復元できない。

### 7.3 STEP 3-A 分類

| 文書 | 分類 |
|---|---|
| `MOCKA_CHARTER_v2.md` | **CANONICAL** |
| README Core Articles 0-10 | **DERIVED** (かつ Charter と内容が乖離している) |

`PARALLEL_CANONICAL` としない理由: README 自身が Charter を
`Full Charter` として参照しており、上位を主張していない。
かつ憲法層への分類記録が存在しない。

`SUPERSEDED` としない理由: README の 11条集合を採用・失効させた
制度記録が発見されなかった。両者の系譜関係は **UNKNOWN** である
(README が Charter v1 を記述している可能性は INFERRED に留まり、断定しない)。

### 7.4 STEP 3-B: Entitlement 判定に影響する差異のみ抜粋

全文転載は行わない (指示書 STEP 3-B)。

| Article (README) | Charter v2 対応 | Status | Entitlement 判定への影響 |
|---|---|---|---|
| 0 `Verifiability - all claims must be externally verifiable` | **対応条項なし** | **README のみ** | **最重要**。`claims (主張)` の外部検証可能性を求める条項は Canonical 側に存在しない |
| 8 `Evidence supremacy - system logs override AI reports` | 第1条 `物理証拠優先原則` / 第8条 `実証主義` | 条番号が異なるが実質同一 | 源泉優先の規定。Entitlement 非該当 |
| (該当なし) | 第4条 `検証可能性: すべての挙動は再現可能であること` | Charter のみ | 対象が `挙動 (behavior)` であり `主張 (claim)` ではない |
| 3 `Pre-implementation checklist - system verifies, not AI` | 第6条 `制御優先: AIではなくシステムが最終決定を行う` | 実質同一 | 決定主体の規定 |

### 7.5 判定の帰結 - AUDIT-EEB-002 §13.5 の確定

AUDIT-EEB-002 は `EVIDENCE SUPREMACY IMPACT: PARTIAL` とし、
その理由を `README Article 0 を Canonical と見なす場合には直接侵食に当たるが、
どちらが Canonical かが UNKNOWN` と記載した。

本調査により確定した (OBSERVED):

**Article 0 (`all claims must be externally verifiable`) は Canonical ではない。**
Canonical な Charter 第4条が求めるのは `挙動の再現可能性` であり、
`主張の外部検証可能性` ではない。

これは **N3 を弱める方向の発見である**。本調査が結論誘導していないことの
一例として明示的に記録する。AUDIT-EEB-002 が
`Evidence Supremacy への直接侵食` の可能性として挙げていた根拠は、
Canonical でないことが判明したため成立しない。

```
Canonical Design Coverage: NONE
```

Canonical な条項集合 (Charter 8条) のいずれも、
Evidence が何を確立する資格を持つかについて規定していない。
すなわち Canonical Design は当該責務を**担っていない**。

---

## 8. Existing Substitute Mechanisms

AUDIT-EEB-002 第8章の判定を、本調査で判明した内容に照らして再評価する。

| 機構 | AUDIT-EEB-002 | 本調査後 | 変更理由 |
|---|---|---|---|
| A. Provenance | NO | **NO (強化)** | Evidence Level階層が provenance分類そのものであることが判明 (5.3)。最も洗練された provenance 規定でも Entitlement 項を持たない |
| B. Authenticity | NO | **NO (変更なし)** | - |
| C. Arbitration | NO | **NO (強化)** | Evidence Level階層の L3破棄規則も arbitration であることが判明 (5.3) |
| D. Sufficiency | NO | **NO (変更なし)** | Evidence Level階層は sufficiency を扱わない (5.1 #4) |
| E. Human Gate | NO | **NO (強化)** | HG-C10 で Human Authority が再検証機構を明示的に選択しなかった (6.4)。Human Gate は上流の検証機構を要求しない選択を行っている |
| F. Reverification (新規評価) | (未評価) | **NONE** | 6.5。正式検討され不採用 |
| G. Canonical Design (新規評価) | (UNKNOWN) | **NONE** | 7.5。Charter 8条に該当条項なし |

### 8.1 憲法層5件の網羅確認 (N3条件9のため)

`MOCKA_GOVERNANCE_CATALOG_DRAFT_v0.1.md:19` が列挙する憲法層5件を個別に確認した。

| 文書 | 責務 | Entitlement 該当 |
|---|---|---|
| `MOCKA_CHARTER_v2.md` | 8条憲章 | **なし** (7.4) |
| `VOCABULARY_CONSTITUTION_v0.1.md` | 8用語の辞典。`Decision Evidence` は独立見出しを立てていないと自認 | **なし** |
| `STATUS_VOCABULARY_v1.0_CONSTITUTION.md` | status 語彙 | **なし** |
| `SATELLITE_REPOSITORY_ARCHITECTURE_v1.0_CONSTITUTION.md` | 衛星リポジトリの運用状態分類 | **なし** |
| `REGISTRY_CHARTER_v1.0.md` | `Registry とは何が存在するかを一元的に管理する台帳` | **なし** (存在の台帳であり、含意の台帳ではない) |

### 8.2 全 governance 文書に対する Entitlement 型記述の探索

`docs/` および root `*.md` 全体に対し、
`確立する資格` / `支持できる範囲` / `支持する資格` / `何を確立` /
`導出の妥当性` / `推論の妥当性` / `evidence.*entitl` を検索した結果、
本監査シリーズ自身の文書を除き **0件** (OBSERVED)。

---

## 9. Evidence -> Proposition Analysis

3件のUNKNOWN解消後の、責務所在の最終整理。

```
Evidence
   |
   |-- 出所は何か           -> Evidence Level階層 (L1/L2/L3)      [DECLARED, NOT ENFORCED]
   |                           DC_20260730_009 5段階順序           [DECLARED, 運用規則]
   |
   |-- 本物か               -> SHA-256 / Ed25519 / append-only     [ENFORCED]
   |
   |-- 存在するか           -> DC_20260730_009 未検証文脈隔離      [DECLARED, 運用規則]
   |
   |-- 十分か               -> validation_engine / prediction gate [部分的に ENFORCED]
   |
   |-- 出所が競合したら     -> L3破棄 / PRIORITY_ORDER / Article 8 [部分的に ENFORCED]
   |
   |-- まだ有効か           -> 機構なし (HG-C10 Y-4 で不採用)      [NONE]
   |
   |-- ### この Evidence は P を確立してよいか ###
   |       担当機構: なし
   |       Canonical 規定: なし
   |       runtime 経路: なし
   |       憲法層5件: 該当なし
   |       governance 文書全体: 該当記述 0件
   v
Proposition
```

**Evidence 側の問いは6種類すべてに担当機構が割り当てられている。
Proposition との関係を問う段にのみ、担当が存在しない。**

これは機構の不足ではなく、**問いの種類が1つ欠けている**構造である。
Evidence Level階層という、MoCKA で最も精緻な Evidence 分類制度ですら
Proposition 側の項を持たないことが (5.2)、この欠落が
偶発的なものではなく体系的なものであることを示している。

---

## 10. Runtime Evidence

読み取り専用実行。永続化関数は使用していない。

### 10.1 STEP 6 連鎖検証

Evidence は authentic (実在する検証文字列 `AST_PARSE_OK`)、
provenance あり、admissible (許容性検査が存在しないため自動的に通過)、
sufficient (8 scope 全充足)。ただし対象モジュールと論理的関係を持たない。

```
Proposition (validation) : VALID
Truth       (decision)   : PASS
State       (commit)     : committed = True
Institutionalization     : no Human Gate stage exists in this pipeline
   -> committed mirrors 'decision != FAIL' (CommitRecord docstring)
```

**Evidence -> Proposition -> Truth -> State の全段を通過し、
committed = True まで到達する。** 停止点は存在しない。

### 10.2 Evidence Level階層の runtime 参加

```
grep 'Evidence Level' over all .py : 0 matches
```

**DECLARED であって ENFORCED ではない (5.5 の確定)。**

### 10.3 不変性確認

```
registry hashes UNCHANGED   (beta_registry.json / pattern_db.json)
git status --porcelain      (空)
```

実行前後で md5 一致、working tree 変更なし。DB 書き込みなし。

---

## 11. Remaining UNKNOWN

本判定を阻害しない残存事項を、性質を明示して記録する。

| # | 項目 | 性質 | N3への影響 |
|---|---|---|---|
| R-1 | HG-C10 Y-4 の適用範囲は EBGA G-5 の `不一致の Evidence 接続方式` である。汎用の再検証手続きを普遍的に否定したものではない | **探索して不在を確認済み** (`再検証` / revalidation / reassessment 検索で他系列なし) | 影響なし。ただし普遍的否定の証明ではないことを明記する |
| R-2 | 条件9の網羅性。憲法層5件は個別確認したが、全 policy 文書の逐一列挙はしていない | **探索して不在を確認済み** (8.2 の全文検索 0件) | 影響なし |
| R-3 | README Core Articles 11条集合と Charter v2 8条集合の系譜関係 (v1 との関係) | **UNKNOWN** | 影響なし。7.3 で DERIVED と確定しており、系譜が判明しても Canonical 判定は変わらない |
| R-4 | `DC_20260730_001` の Decision Identity Collision 自体は未解消 | **既知・Open** | 影響なし。184行目の内容は companion event から回収済み |
| R-5 | production GL7 が本branch HEAD と異なるコードで稼働している理由 | **UNKNOWN** | 影響なし (第17章) |

**R-1 と R-2 は AUDIT-EEB-002 の K1/K2/K3 とは性質が異なる。**
K1/K2/K3 は `読めない` / `未解決` であった。R-1/R-2 は
`探索し、不在を確認した` である。前者は判定を阻害し、後者は阻害しない。

---

## 12. N3 Necessary Conditions

指示書 STEP 5 の9条件を一つずつ判定する。
**一つでも未確認なら N3 ではなく UNKNOWN を維持する。**

| # | 条件 | 判定 | 根拠 |
|---|---|---|---|
| 1 | Evidence -> Proposition の Entitlement 責務が MoCKA の制度目的に必要 | **CONFIRMED** | AUDIT-EEB-002 §13.4 のうち、Canonical に残る根拠: Charter 第1条 (すべての評価はログ・実行結果・記録に基づく)、Charter 第4条、Charter 第6条、HAB `No assumption-based completion`、`DC_20260730_001` (4) Evidence First順序、`mocka_hab_human_gate_relation_v1.md` §7。**なお README Article 0 は Canonical でないため根拠から除外した (7.5)** |
| 2 | 既存 Evidence Level 等がその責務を完全には担わない | **CONFIRMED** | 第5章。Proposition 側の項が構造的に存在しない (5.2)。runtime 参照0件 (5.5) |
| 3 | Human Gate では代替できない | **CONFIRMED** | AUDIT-EEB-002 §8E + 本調査 6.4 (Human Authority が再検証機構を選択しなかった) |
| 4 | Provenance では代替できない | **CONFIRMED** | AUDIT-EEB-002 §8A + 5.3 (Evidence Level階層は provenance分類であり Entitlement 項を持たない) |
| 5 | Authenticity では代替できない | **CONFIRMED** | AUDIT-EEB-002 §8B |
| 6 | Sufficiency では代替できない | **CONFIRMED** | AUDIT-EEB-002 §8D + 5.1 #4 |
| 7 | Arbitration では代替できない | **CONFIRMED** | AUDIT-EEB-002 §8C + 5.3 (L3破棄規則も arbitration) |
| 8 | Reverification でも代替できない | **CONFIRMED** | 第6章。正式に提示され (3-3)、選択されなかった (Y-4)。機構は存在しない |
| 9 | 他の既存 Canonical 制度にも同等の責務が存在しない | **CONFIRMED** | 8.1 (憲法層5件を個別確認) + 8.2 (governance 文書全体の全文検索 0件) + 7.4 (Charter 8条に該当条項なし) |

**9条件すべて CONFIRMED。**

### 12.1 STEP 4 Case 判定

指示書 STEP 4 の4ケースに照らす。

| Case | 内容 | 該当 |
|---|---|---|
| A | Evidence Level階層が Entitlement を既に制度的に定義・強制している | **非該当** (5.2, 5.5) |
| B | Evidence Level階層は品質・信頼性等だけを扱い Entitlement を扱わない。かつ G5_HGC10 以降にも代替機構が存在しない | **該当** (第5章, 第6章) |
| C | 既存機構が複数存在し、組み合わせれば Entitlement を完全に実現している | **非該当** (第8章。7機構すべて NO/NONE) |
| D | 既存機構は部分的に責務を担うが完全には拘束しない | **非該当**。部分的にも担っていない。Entitlement 項が存在しない |

**Case B に該当。** 指示書は Case B について
`N3の必要条件が大幅に強化される。ただし、それだけでN3確定とはしない` と定める。
本調査は Case B の確認に加え、STEP 5 の9条件すべてを個別に CONFIRMED とした。

---

## 13. Final Necessity Assessment

### 13.1 判定

```
N3
```

> N3: MoCKA の制度目的を成立させるために、独立 Boundary が論理的に不可欠。

### 13.2 N2 から N3 へ変更した理由

**新しい証拠が見つかったからではなく、読めなかった証拠を読んだ結果である。**

AUDIT-EEB-002 が N2 に留めた理由は2つだけであった (同 §13.7)。

| 要因 | AUDIT-EEB-002 | 本調査 |
|---|---|---|
| A: `Evidence Level階層` が既に責務を担っている可能性を否定できない | Decision Identity Collision により**読めなかった** | companion event から**原文を回収**。Proposition 側の項が構造的に存在しないことを確認 (5.2)。runtime 参照0件 (5.5) |
| B: MoCKA は本件を `手続きの不在` として登録しており、Boundary を要さない可能性がある | `未整理` `未確定事項` の状態 | HG-C10 で**正式に選択肢化され (3-3)、Human Authority が選択しなかった (Y-4)**。未整理ではなく不採用 |

両要因が消えた。他に N3 を阻害する要因は発見されなかった。

### 13.3 N3 が"独立 Boundary"を指す理由

責務が必要 (条件1) であり、かつ既存の7機構
(Provenance / Authenticity / Arbitration / Sufficiency / Human Gate /
Reverification / Canonical Design) のいずれにも属さない (条件3-9)。
さらに憲法層5件および governance 文書全体にも該当記述がない (条件9)。

**どの既存機構の拡張としても位置づけられないことが確認された結果、
独立した責務単位として残る。** これは設計判断ではなく、
帰属先の網羅的探索が尽きたことによる帰結である。

### 13.4 本判定が主張していないこと

- 実装すべきである、とは述べていない (`IMPLEMENTATION AUTHORIZATION: NOT AUTHORIZED`)。
- 実装形態・配置・名称について何も述べていない。
- `Evidence Entitlement Boundary` という名称を MoCKA の概念として提案していない。
  本報告書における当該語は、指示書からの引用と本監査シリーズの識別子としてのみ用いている。
- MoCKA が危険である、とは述べていない。指示書 第15章の論証順序に従い、
  `保証されない部分の特定` -> `制度目的への影響` -> `帰属先の探索` -> `判定` の順で論じた。

### 13.5 結論誘導を行っていないことの証跡

本調査で N3 を弱める方向の発見が2件あり、いずれも記録している。

1. **7.5**: README Article 0 (`all claims must be externally verifiable`) が
   Canonical でないことが判明し、AUDIT-EEB-002 が挙げていた根拠の1つが失われた。
   条件1の根拠から明示的に除外した。
2. **5.4**: `Evidence First順序` は Evidence -> Analysis の段が制度上
   存在することの Canonical な明示であり、N3 を弱める側面を持つ。両義性を記録した。

これらを隠さず反映した上で、9条件は依然としてすべて CONFIRMED である。

---

## 14. Implementation Impact

**本章は実装提案ではない。実装は承認されていない。**
仮に将来 Human Gate が実装を裁定した場合に影響が及ぶ範囲を事実として列挙する。

| 影響先 | 事実 |
|---|---|
| `DC_20260730_001` | Active かつ `DC_20260730_002` に継承済み。Evidence Level階層は provenance/arbitration 責務として現行のまま維持されうる。Entitlement を追加する場合、当該 Decision の改変ではなく別責務の追加となる |
| `HG-C10_DECISION_RECORD_v1.0.md` | Y-4 は EBGA G-5 の裁定であり Decision Immutable 原則 (`DC_20260805_001` G-10) の対象。本判定は Y-4 を変更しない |
| `MOCKA_CHARTER_v2.md` | 8条。Entitlement 条項は存在しない。Charter 改定は憲法層の変更に当たる |
| README Core Articles | Charter と乖離している (7.1)。DERIVED として整理するか同期するかは別件 |
| `core_kernel/governance` | Entitlement を導入する場合の最有力の受け皿だが、production から import 0件 (DORMANT) |
| `structural/bee.py` | 稼働中。Approval -> Evidence 還流 (AUDIT-EEB-002 §6.5) が Entitlement と整合しない |
| Decision Identity Collision | `DC_20260730_001` は未解消 (R-4)。本判定はこれを変更しない |

## 15. Recommendation

指示書 2.1 により実装は禁止されている。実装勧告は行わない。

判定は N3 に到達し、指示書 STEP 5 の9条件はすべて CONFIRMED となった。
したがって **追加調査は本判定のためには不要である**。

以下は本判定と独立に存在する既知の未解消事項であり、
実施可否はきむら博士の裁定による。本判定はこれらの解消を前提としない。

| # | 事項 | 性質 |
|---|---|---|
| S-1 | `DC_20260730_001` の Decision Identity Collision (184/193) | 既知・Open。`DECISION_IDENTITY_INCIDENT_TRIAGE.md` で管理中 |
| S-2 | README Core Articles と `MOCKA_CHARTER_v2.md` の乖離 | 7.1。Canonical は確定済みのため、README 側の整合は文書保守事項 |
| S-3 | production GL7 と branch HEAD の不一致 | 第17章。3回の記録試行すべてで観測 |

## 16. Evidence Index

| ID | 種別 | 所在 | 用途 |
|---|---|---|---|
| N-01 | DATA (MCP) | event `E20260730_020387442514a` (2026-07-29T22:43:40Z) | **DC_20260730_001 184行目の原文**。K1 解消の一次証拠 |
| N-02 | DATA (MCP) | event `E20260730_15508419841d5` | `DC_20260730_002` による 184行目の継承確認 |
| N-03 | DATA (MCP) | `mocka_decision_get("DC_20260730_001")` = 193行目 (p-DERS) | 最新行のみが返ることの確認 |
| N-04 | DOCUMENT | `docs/governance/decision_identity/DECISION_IDENTITY_INCIDENT_TRIAGE.md:59` | 184行目の主題と行番号 |
| N-05 | DATA (MCP) | event `E20260806_961696349f18e` | G5_HGC10 PREP。再検証手続きの提起 |
| N-06 | DATA (MCP) | event `E20260806_5828029439482` | G5_HGC10 INPUT。**判断対象3 の選択肢 3-1..3-4** |
| N-07 | DOCUMENT | `docs/governance/HG-C10_DECISION_RECORD_v1.0.md:51-58, 4.1 Y-4, 5.3` | **裁定結果 3-2 採用 / 3-3 不採用**。K2 解消の一次証拠 |
| N-08 | DOCUMENT | `docs/governance/MOCKA_CHARTER_v2.md` (8条) | Canonical 条項集合 |
| N-09 | DOCUMENT | `README.md:174-186` (11条) / `:801-810` (6条) | DERIVED。相互不一致 |
| N-10 | DOCUMENT | `GOVERNANCE_CLASSIFICATION_v0.1.md:46` | Charter = 憲法層・制定済み |
| N-11 | DOCUMENT | `GOVERNANCE_INVENTORY_v0.1.md:165` | Charter = 制定済み(8条憲章)・全体基盤 |
| N-12 | DOCUMENT | `GOVERNANCE_RELATIONSHIP_MAP_v0.1.md:36` | Charter = 全体基盤 |
| N-13 | DOCUMENT | `MOCKA_GOVERNANCE_CATALOG_DRAFT_v0.1.md:19,67` | 憲法層5件・Charter 最上位 |
| N-14 | DOCUMENT | `VOCABULARY_CONSTITUTION_v0.1.md:121` | `Decision Evidence` を独立見出しとしていないことの自認 |
| N-15 | DOCUMENT | `REGISTRY_CHARTER_v1.0.md` 第1章 | Registry = 存在の台帳 |
| N-16 | CODE (grep) | 全 `.py` に対する `Evidence Level` 検索 = 0件 | DECLARED / NOT ENFORCED の確定 |
| N-17 | CODE (grep) | `docs/` + root `*.md` の entitlement 型記述検索 = 0件 | 条件9 |
| N-18 | EXECUTION | 第10章 PROBE | Evidence -> committed=True の全段通過 |
| N-19 | EXECUTION | registry md5 一致 / `git status` 空 | 非改変の証明 |
| N-20 | CODE | `mocka_mcp_server.py:1004-1024` | companion event が decision 全文を events.db へ複写する経路 (K1 突破口) |
| N-21 | OBSERVATION | 第17章 GL7_EXECUTION_BLOCKED | 記録試行の結果 |

## 17. Audit Trail

```
EVENT WRITE ATTEMPTED : mocka_write_event (CHANGE_START)
RESULT                : BLOCKED
REASON (observed)     : {"error": "GL7_EXECUTION_BLOCKED",
                         "reason": "GL7 abort: ['encoding_mismatch:data/n8n/database.sqlite',
                                                'encoding_mismatch:di_terminology_inventory_20260820.txt',
                                                'encoding_mismatch:s05_decision_extract.txt']",
                         "thinking_mode": "audit"}
WORKAROUND            : NOT ATTEMPTED
```

本監査シリーズを通じ、記録試行は計5回すべて同一理由で BLOCKED である
(AUDIT-EEB-001 で2回、AUDIT-EEB-002 で2回、本調査で1回)。
`encoding_mismatch` は base commit `da4d4db` で `ABORT_CONDITIONS` から
削除済みの条件であり、production runtime が本 branch HEAD と異なるコードで
稼働していることは Confirmed、原因は UNKNOWN (R-5)。

回避策は作成していない。**本報告書の git commit が本調査の唯一の永続的 Evidence である。**

### 17.1 非改変の確認

| 対象 | 確認方法 | 結果 |
|---|---|---|
| working tree | `git status --porcelain` | 空 (本報告書追加前) |
| `structural/beta_registry.json` | md5 実行前後比較 | 一致 |
| `structural/pattern_db.json` | md5 実行前後比較 | 一致 |
| events.db | 書き込みツール未使用 (GL7 により全試行 BLOCKED) | 変更なし |
| decision_ledger.jsonl | `mocka_decision_write` 未使用 | 変更なし |
| コード / Schema / threshold / TODO / テスト | 変更操作を実施していない | 変更なし |

## 18. History

- 2026-08-27: 初版 (v1.0)。R01 directive による残存UNKNOWN解消調査。
  base commit 23874be。K1/K2/K3 すべて解消。判定 N2 -> **N3**。
  実装変更なし。`IMPLEMENTATION AUTHORIZATION: NOT AUTHORIZED`。

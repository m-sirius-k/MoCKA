# AUTO_SEAL Specification Series Architecture v1.0

- Document ID: AUTO-SEAL-ARCH-001
- Series: AUTO_SEAL Documentation Framework
- Class: Foundation (Series-defining document)
- Status: Review Candidate (S0 structural draft; pending S0.5 review + Human Gate; not yet Approved)
- Version: 1.0
- Date: 2026-07-13
- Author: Claude-opus-4-8 (くろこ)
- Commissioned / approval owner: きむら博士
- Directive: KUROKO-DOC-S0-001 (Sprint S0, Phase S0-1)
- Classification: Documentation only. No source code, no Core System File change.
- Related: AUTO-SEAL-IDX-001 (Index), AUTO-SEAL-GLO-001 (Glossary),
  docs/governance/AUTO_SEAL_BOUNDARY_DESIGN_v1.0.md (GOV-DESIGN-ASBD-001)

本書は AUTO_SEAL Documentation Framework の最上位規格である。個々の Standard の中身では
なく、Series 全体の骨格(分類原則・責務境界・命名規則・文書番号体系・将来拡張ルール)を
確定する。本書が定める枠に、Foundation / Process / Governance の各 Standard が収まる。

---

## 1. 目的とスコープ

### 1.1 目的

AUTO_SEAL に関する設計・規格・運用文書は、これまで docs/governance/ 配下に個別文書
(AUTO_SEAL_BOUNDARY_DESIGN, AUTO_SEAL_M1_IMPLEMENTATION_PROPOSAL 等)として蓄積されてきた。
本 Series は、それらを貫く共通規格(証跡・追跡・メタデータ・識別子・状態)を単一の体系
として確定し、後続の各 Standard が参照する土台を提供する。

### 1.2 スコープ

- 対象: AUTO_SEAL(Seal Authorization Boundary、anchor_record 固定、承認証跡)に関わる
  文書の規格。
- 非対象: AUTO_SEAL 実装コード(anchor_update.py / seal_governance_gate.py 等)、
  events.db 仕様、app.py、port 契約。これらは本 Series の記述対象であっても変更対象ではない。

### 1.3 本書が確定しないこと(Non Goals)

- 各 Foundation Standard の詳細規格(Sprint S1 以降)。
- 実装・Migration の着手(Core System File Human Gate 承認が別途必要)。
- 既存 GOV-* 文書番号体系の改番・移設。

---

## 2. 分類原則: Foundation / Process / Governance

Series 内の全 Standard は、次の 3 分類のいずれか 1 つに属する。分類は責務の性質で決まり、
文書の重要度ではない。

| 分類 | 定義 | 問いに答える | 例 |
|---|---|---|---|
| Foundation | 全文書が従う共通の土台。他 Standard から参照される語彙・構造・不変条件を定義する | 「何を、どの形式で表現するか」 | Evidence, Traceability, Metadata, Identifier, Status |
| Process | 作業の進め方を定義する。Foundation を前提に、手順・ゲート・成果物要件を規定する | 「どう進め、どこで人間が承認するか」 | Proposal, (将来) Verification, Audit, Release |
| Governance | 制度としての拘束・適合判定・逸脱時の扱いを定義する | 「何をもって適合とし、逸脱をどう扱うか」 | (将来) Conformance, Human Gate Policy |

分類原則(不変):

1. Foundation は Process / Governance に依存してはならない(下位が上位を参照する一方向)。
2. Process は Foundation を参照してよいが、他 Process に循環依存してはならない。
3. Governance は Foundation / Process を参照して適合基準を定義する。
4. 1 文書は 1 分類のみに属する。またがる場合は文書を分割する。

依存方向は Foundation <- Process <- Governance の一方向とする(矢印は「参照される側 <- する側」)。
具体的な依存関係は AUTO-SEAL-IDX-001 の Dependency Matrix で管理する。

---

## 3. Standard 間の責務境界

各 Standard の責務は重複させない。境界が曖昧になった場合は本書の改訂で裁定する。

| Standard | 責務(この文書が唯一の正本となる範囲) | 責務外(他 Standard の領分) |
|---|---|---|
| Evidence (STD-001) | 証跡の定義、証跡たりうる条件、証跡の最小構成 | 証跡をどこに記録するか(Metadata/実装) |
| Traceability (STD-002) | 文書間・成果物間の参照関係、たどれることの保証 | 参照される識別子の書式(Identifier) |
| Metadata (STD-003) | 文書ヘッダの共通フィールドと必須/任意区分 | フィールド値の状態語彙(Status) |
| Identifier (STD-004) | ID の書式・採番・一意性・不変性 | ID が指す対象の状態(Status) |
| Status (STD-005) | 状態語彙とその遷移、fail closed 既定 | 状態を持つ対象の識別(Identifier) |
| Proposal (STD-006) | 提案文書の構造・必須節・承認ゲート要件 | 提案が参照する証跡の定義(Evidence) |

責務境界の原則:

- 「定義する場所は 1 つ」: ある概念(例: Identifier の書式)を定義する Standard は 1 つに限る。
  他 Standard は再定義せず参照する。
- 重複記述の禁止: 同じ規則を 2 文書に書かない。片方を正本、他方を参照とする。

---

## 4. 命名規則

### 4.1 Series 名

本 Series の正式名称は「AUTO_SEAL Documentation Framework」、短縮 Series 接頭辞は
`AUTO-SEAL` とする。

### 4.2 文書タイトル

- 形式: `AUTO_SEAL <Subject> <DocType> v<Version>`
- 例: `AUTO_SEAL Evidence Foundation Standard v0.1`
- CP932 汚染防止規約(MoCKA CLAUDE.md)に従い、タイトル・本文ともに非 ASCII 装飾記号
  (矢印・丸付き数字・罫線・全角括弧以外の各種括弧)を使用しない。全角括弧 () は可。

### 4.3 ファイル名

- 形式: `<Document ID>_<TITLE_UPPER_SNAKE>_v<Version>.md`
- 例: `AUTO-SEAL-STD-001_EVIDENCE_FOUNDATION_STANDARD_v0.1.md`
- 拡張子は .md。1 文書 1 ファイル。

### 4.4 用語

- 用語は AUTO-SEAL-GLO-001 (Glossary) を唯一の正本とする。本 Series 内で用語を再定義しない。

---

## 5. 文書番号体系

### 5.1 書式

```
AUTO-SEAL-<TYPE>-<NNN>
```

- `AUTO-SEAL`: Series 接頭辞(固定)。
- `<TYPE>`: 文書種別コード(下表)。
- `<NNN>`: Series 内で TYPE 単位に連番(001 から、ゼロ埋め 3 桁)。

### 5.2 TYPE コード

| TYPE | 意味 | 分類 |
|---|---|---|
| ARCH | Series Architecture(本書のような Series 定義文書) | Foundation |
| IDX | Series Index(目録・依存関係) | Foundation |
| STD | Standard(規格。Foundation / Process いずれも STD を用い、分類は Index で管理) | Foundation / Process |
| GLO | Glossary(用語集) | Foundation |
| RVW | Review Guideline(制度レビューの観点・役割・完了条件) | Process |
| PROC | Process 手順書(Standard ではない運用手順) | Process |
| GOV | Governance 規程 | Governance |

STD は Foundation と Process の両方で使う。ある STD がどの分類かは AUTO-SEAL-IDX-001 の
Master Catalog が正本として持つ(番号からは分類を導出しない。将来の再分類に耐えるため)。

### 5.3 採番規則(不変性)

- 一度採番した Document ID は再利用しない。文書が廃止(SUPERSEDED / OBSOLETE)されても
  番号は欠番として残す。
- 版更新(v0.1 -> v1.0)では Document ID を変えない。Version のみを上げる。
- 後継文書で概念を置換する場合は新番号を採番し、旧文書 Status を SUPERSEDED とし
  相互参照する(Traceability Standard 準拠)。

### 5.4 既存 GOV-* 体系との関係

docs/governance/ には既存の `GOV-<TYPE>-<SLUG>-NNN` 体系(例: GOV-DESIGN-ASBD-001)が存在する。
本 Series は既存体系を改番せず、以下の関係で共存する。

- GOV-* は governance 文書全体の汎用採番。AUTO-SEAL-* は AUTO_SEAL に限定した Series 内採番。
- 1 文書が両方の ID を持つことはしない。新規 AUTO_SEAL 規格文書は AUTO-SEAL-* を用いる。
- 既存の AUTO_SEAL 個別文書(AUTO_SEAL_BOUNDARY_DESIGN 等)は現行のまま残し、
  AUTO-SEAL-IDX-001 から Reference として関連付ける(移設・改番はしない)。

---

## 6. 将来拡張ルール

Series の拡張は次の順序と条件で行う。

1. 新規 Standard の追加は、既存 Standard の責務を侵さないこと(第 3 章)を確認してから行う。
2. 新規 TYPE コードの追加は本書(ARCH-001)の改訂を要する。TYPE を勝手に増やさない。
3. 分類(Foundation/Process/Governance)の変更は Dependency Matrix の一方向性
   (第 2 章)を壊さないことを確認する。
4. Sprint 単位で拡張する。S0 = 骨格確定、S1 以降 = Foundation 詳細、以降 Process/Governance。
5. すべての拡張は CHANGE_START / CHANGE_DONE 記録を伴う(MoCKA 記録義務)。
   制度的裁定を含む場合は Decision Ledger へも記録する。

---

## 7. 適合(Conformance)の位置付け

本書は Conformance の判定基準そのものは定義しない(将来の Governance Standard の領分)。
本書は「適合を判定できるだけの構造(分類・責務・番号・依存)」を提供するに留める。
Conformance 分類の枠組みは AUTO-SEAL-IDX-001 に置き、判定規程は将来の Governance Standard
で確定する。

---

## 8. History

- 2026-07-13: 初版(v1.0)。KUROKO-DOC-S0-001 Sprint S0 Phase S0-1 として、AUTO_SEAL
  Documentation Framework の分類原則・責務境界・命名規則・文書番号体系・将来拡張ルールを
  確定。実装・Core System File 変更は伴わない(設計骨格のみ)。
- 2026-07-13: きむら博士裁定により本 Series の S0 成果物を Review Candidate として扱う。
  Approved 移行と Decision Ledger 記録は S0.5 レビュー(ChatGPT / Gemini)+ Human Gate 後に一括。
  本書 Status を Review Candidate へ更新(構造・番号体系・本文は不変更)。
- 2026-07-13: S0.5 のため新 TYPE コード RVW(Review Guideline)を第 5.2 節へ追加(新規 TYPE は
  本書改訂を要するという第 6 章の自己ルールに従う)。AUTO-SEAL-RVW-001 を採番。

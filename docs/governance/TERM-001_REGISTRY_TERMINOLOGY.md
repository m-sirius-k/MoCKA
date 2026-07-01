# TERM-001_REGISTRY_TERMINOLOGY

TERM-001: Registry Terminology & Principles
Pre-KN Artifact（KN-003着手前の前提成果物）

Artifact Type: Governance Document
Completion Evidence: .md 必須
Evidence Location: docs/governance/TERM-001_REGISTRY_TERMINOLOGY.md
Verification Status: Pending（きむら博士承認待ち）

依存関係: GM2_REGISTRY_BASELINE_001 -> TERM-001 -> KN-003

---

## 1. Purpose（目的）

本文書は KN-003（Registry Record Specification）以降の Registry Series 設計において
共通して参照する用語の定義と設計原則を確立することを目的とする。

KN-001（REGISTRY_CHARTER_v1.0）および KN-002（CATEGORY_REGISTRY_v2.0）は
「Registryとは何か」「何を登録するか」を定めた。これらの設計を前提として、
KN-003 以降がレコードの構造・スキーマ・検証ルール・ライフサイクルを設計する際に
用語の解釈が揺れることを防ぐため、本文書で用語と設計原則を先行して確定する。

本文書はカテゴリでもシリーズでもない。Registry Series 内で KN-003 着手前に必要な
「前提成果物（Pre-KN Artifact）」として位置づけられる。
KN-001・KN-002 への遡及編集は行わない。KN-003 以降の番号予告も変更しない。

---

## 2. Core Principles（設計原則）

### 2-1. Registry Neutrality Principle（存在中立原則）

> Registry は対象の正当性・品質・価値を判断しない。
> 存在を登録し、参照可能にすることのみを責務とする。

これは KN-001 セクション1の「Registry は存在の正当性を判断しない。
存在を登録・参照可能にすることのみを責務とする。」という一文を、
KN-003 以降の設計が参照すべき独立した設計原則として明文化したものである。

この原則はすべての Registry 設計判断の基準となる。
記録の評価・承認・品質判定は Registry の外部（Human Approval Gate 等）が担う。

### 2-2. Entity Model vs Index Model — 採用モデルの確定

Registry Record の性質について、設計上の重要な問いがある。

**Entity Model（実体モデル）**
Record 自体が意味のある実体であり、対象の属性・内容・状態を Record 内に保持する。
Record が対象を代表し、Record の変更が対象の変更を意味する。

**Index Model（索引モデル）**
Record は「対象がどこにあるか」を示す索引である。
対象（Artifact）は Record の外部に存在し、Record は Artifact への参照情報を保持する。
Record の責務は「存在を問い合わせ可能にすること」に限定される。

**採用モデル: Index Model**

MoCKA Registry は Index Model を採用する。

採用の根拠は以下の 3 点である。

1. KN-001 の定義「存在する」ことを、問い合わせ可能な状態で保持する」は、
   Registry の責務を「発見可能性の保証」に限定している。これは Index Model と一致する。

2. KN-001 の Registry Neutrality Principle「存在の正当性を判断しない」は、
   Record が対象の内容や品質を抱え込まないことを意味する。
   Entity Model では Record が対象の権威的な表現となり、この原則と矛盾しやすい。

3. KN-002 の設計（カテゴリ・シリーズの存在事実を登録）は、
   Artifact 自体（CATEGORY_REGISTRY_V1・KN_SERIES_LEDGER）を外部に保持し、
   Registry はその参照を管理するという Index Model の実践例となっている。

この決定は KN-003（Record Specification）・KN-004（Schema）・KN-005（Validation）の
設計に直接影響する。Record は Artifact の内容を複製・内包するのではなく、
Artifact への参照情報（Reference）を保持する構造として設計されるべきである。

Entity Model 不採用の理由: Entity Model は Record が対象そのものを代表する設計となるため、Registry Neutrality Principle および Index Model 設計と整合しないため採用しない。

---

## 3. Terminology（用語集）

以下に 12 の基本用語を定義する。
各定義は Index Model（セクション 2-2）および Registry Neutrality Principle（セクション 2-1）
と整合している。

### Registry（レジストリ）

存在を登録・参照するための台帳。
「何が存在するか」を問い合わせ可能な状態で保持する仕組みである。
Registry の責務は存在の登録と参照の提供のみであり、対象の評価・承認は行わない。

KN-001 に定義された概念であり、本用語集においても KN-001 の定義を上書きしない。

### Record（レコード）

Registry 内の 1 件の登録単位。
1 つの Artifact（または登録対象）に対して 1 つの Record が存在する。
Record は Artifact を参照する索引であり、Artifact の内容を内包しない（Index Model）。

### Entry（エントリ）

Record の別称として使用する同義語である。

Record と Entry は同一概念を指す。
KN-002 では「Registry 登録エントリ」という表現を使用しており、
本文書では Entry を Record の同義語として暫定採用する。
別概念（例: Record のサブ要素としての Entry）への拡張は行わない。
この暫定定義は KN-003 で再確認・上書きしてよい。

### Artifact（アーティファクト）

実際の成果物。文書・JSON・コード・イベント記録など、実体として存在するものを指す。
Record が参照する対象であり、Registry の外部に存在する。
Registry は Artifact の存在を登録するが、Artifact の内容は Registry 内に複製しない。

KN-001 セクション 2 の登録対象種別（DOCUMENT/EVENT/DECISION 等）はいずれも
具体的な Artifact の分類である。

### Reference（リファレンス）

Artifact への参照情報。
Record が Artifact を指し示すために保持する情報であり、
ファイルパス・URL・識別子・場所情報などが該当する。
Index Model において Record の中核をなす要素である。

### Category（カテゴリ）

責務を表す安定した分類。
KN-002 で確立した 6 カテゴリ（DP/GV/IA/OA/KN/KA）はその実例である。
カテゴリは「責務（Why）」で定義され、シリーズより上位の安定した骨格として機能する。
カテゴリ自身も Registry の管理対象である（KN-001 セクション 2）。

### Series（シリーズ）

Category を実現する継続的な成果物群。
1 つの Category は 0 個以上の Series を持ち、1 つの Series は必ず 1 つの Category に属する。
Series 間に親子関係はない（KN-002 セクション 4-1 の構造原則）。
Series はカテゴリの責務を実現する単位として機能し、成長・追加が可能な部分である。

### Identifier（識別子）

Record を一意に識別する識別子。
Registry 内で Record を特定するための文字列または番号体系である。
KN-003 で識別子の命名規則・形式を定義する（本文書の範囲外）。

### Status（ステータス）

Lifecycle で管理される Record の状態。
Record の生存状態（例: Draft / Review / Approved / Deprecated / Archived 等）を表す。
詳細な状態遷移は KN-006（Registry Lifecycle）で定義する（本文書の範囲外）。

### Maturity（成熟度）

Category または Series の成熟度を表す状態値。
KN-002 で使用した Active / Reserved / Historical がその実例である。
Maturity は対象の運用状況・活性化度を示す概念であり、
個別 Record の Status とは区別される別軸の状態値である。

### Source（ソース）

正本・参照元の概念。
あるデータ・情報の権威的な一次ソースを指す。
KN-002 セクション 6 注記「Governance Document と Operational Record のどちらを正本とするか」
の文脈で登場した概念であり、Source の確定は将来の設計課題として残されている。

Registry の文脈では、ある Artifact に対して複数の表現形式（JSON / Markdown 等）が
存在する場合に「どれが正本か」を示すために Source の概念が必要になる。

Registry は Source を参照できるが、Source を決定する責務は持たない（Registry Neutrality Principle 準拠）。

### Index（インデックス）

「どこにあるか」を示す索引。
本文書のセクション 2-2 で採用した Index Model の中核概念である。
Registry 全体が Index として機能し、各 Record が個別の索引エントリとなる。

Index と Registry の関係: Registry は Artifact 群に対する Index である。

---

## 4. Concept Map（概念マップ）

以下に Registry を構成する概念の関係をテキスト形式で示す。

### 4-1. 主要関係

```
Registry
  |
  +-- [1:N] Record (= Entry)
               |
               +-- [1:1] Identifier    （Record を一意に識別）
               |
               +-- [1:1] Status        （Lifecycle で管理される状態）
               |
               +-- [Reference] -------> Artifact
                                           |
                                           +-- [0:1] Source    （正本の指定）

Category / Series
  |
  +-- [0:1] Maturity                   （Category/Series 固有の成熟度）
```

注: Maturity は Category/Series の属性であり、個別 Record の属性ではない（セクション 3 Maturity 定義に準拠）。

### 4-2. Category - Series の関係

```
Category
  |
  +-- [1:N] Series
                |
                +-- [1:N] Artifact    （Series を構成する成果物群）
```

Category と Series の関係は KN-002 セクション 4-1 で確立済みである。
本概念マップはその関係を再掲したものであり、KN-002 の定義を上書きしない。

### 4-3. Index Model の構造

```
[Registry = Index]
  |
  +-- Record_A --> Reference --> Artifact_A（docs/governance/KN-001.md 等）
  +-- Record_B --> Reference --> Artifact_B（data/MOCKA_TODO_ACTIVE.json 等）
  +-- Record_C --> Reference --> Artifact_C（...）

Artifact はすべて Registry の外部に存在する。
Record は Artifact の内容を複製しない。
```

### 4-4. Registry Neutrality Principle の位置づけ

```
[Human Approval Gate]  <- 正当性・品質・価値の判断はここで行う
        |
        v（承認結果）
[Artifact]             <- 実際の成果物
        |
        v（存在登録）
[Record in Registry]   <- 存在を参照可能にするのみ
```

Registry は Artifact の評価結果を記録することができるが、
評価そのものは行わない。Registry Neutrality Principle はこの境界を明示する。

---

## 5. Scope Freeze（本文書の範囲外）

以下は本文書の範囲外である。KN-003 以降で扱う。

- JSON Schema の定義（KN-004 の範囲）
- Record の詳細フィールド定義（KN-003 の範囲）
- Validator・整合性条件（KN-005 の範囲）
- Status の詳細な状態遷移定義（KN-006 の範囲）
- 実装・コード変更（KN-007 の範囲）
- Source の正本確定（将来の独立した方針決定 TODO の範囲）

---

## 6. 参照文書

- REGISTRY_CHARTER_v1.0.md（KN-001）: Registry の目的・責務・Registry Neutrality Principle の源泉
- CATEGORY_REGISTRY_v2.0.md（KN-002）: Category/Series の Registry 登録、Index Model の実践例
- MOCKA_TODO_ACTIVE.json 内 GM2_REGISTRY_BASELINE_001: 本文書の起点となるベースライン

---

## 改訂履歴

- v1.0（2026-07-01）: TERM-001 として新規作成。Registry用語集・存在中立原則・Entity vs Index確定・概念マップ。くろこ起草、きむら博士承認待ち。
- v1.1（2026-07-01）: 4点修正（Entry暫定性明示・Concept Map整合・Source責務境界・Entity不採用理由追記）＋将来検討事項追加。

## 将来検討事項

- 「Index Model」という名称は将来「データベースのインデックス」と混同される可能性がある。外部公開段階では「Reference Index Model」等への改名を検討する余地がある。実際の改名は行わない（記録のみ）。

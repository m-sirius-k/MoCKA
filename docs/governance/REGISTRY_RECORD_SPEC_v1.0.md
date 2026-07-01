# REGISTRY_RECORD_SPEC_v1.0

KN-003: Registry Record Specification

Artifact Type: Governance Document
Completion Evidence: .md 必須
Evidence Location: docs/governance/REGISTRY_RECORD_SPEC_v1.0.md
Verification Status: Pending（きむら博士承認待ち）

依存関係: KN-001 -> KN-002 -> TERM-001 -> GM2_REGISTRY_BASELINE_002 -> KN-003

---

## Phase 0: 冒頭確定事項

本セクションは設計に入る前に確定すべき4点を明文化する。
以下の確定事項はすべてGM2_REGISTRY_BASELINE_002が申し送った論点に対する回答である。

---

### 0-1. Recordの責務と責務境界

#### Recordの責務

Recordは「Artifactが存在すること」をRegistryの中で参照可能にすることを責務とする。
具体的には以下を行う。

- Artifactを一意に識別する情報を保持する
- ArtifactへのReferenceを保持し、発見可能にする
- Artifactの分類情報（Category/Series等）を保持する
- Recordの生存状態（Status）を保持する

#### Recordが保持しないもの

- Artifactの内容・本文・データ（Index Model原則）
- Artifactの品質・正当性に関する評価結果
- 他のRecordとの関係情報（将来Atlas Seriesの責務）
- Artifactが正本かどうかの判定（Source確定は将来の独立 TODO の範囲）

#### ArtifactとRecordの境界

Artifactは Registry の外部に存在する実体（文書・JSON・イベント記録等）である。
RecordはArtifactを指し示す索引エントリであり、Artifactの内容をRecord内に複製しない。

境界の判定基準：
- 「Artifactがなければ意味を持たない情報」はArtifactの属性であり、Recordには含めない。
- 「Artifactの場所・種別・状態を把握するために必要な情報」はRecordの属性として保持する。

#### Registry Neutrality Principleとの整合

TERM-001セクション2-1が定めるRegistry Neutrality Principleは「存在を登録し、参照可能にすることのみを責務とする」と定める。

RecordはArtifactの評価・承認・品質判定の結果を保持しない。
RecordはArtifactが「存在する」という事実と「どこにあるか」という参照情報のみを保持する。
これによりRecordの設計はRegistry Neutrality Principleと完全に整合する。

---

### 0-2. Artifact:Recordの多重度

#### 確定原則: One Artifact -> One Record（1:1）

1つのArtifactに対して1つのRecordを対応させることを基本原則として採用する。

#### 採用理由

1. Index Modelとの整合: TERM-001が採用したIndex Modelでは、RecordはArtifactへの索引エントリである。索引において同一対象に複数エントリが存在すると、「どのRecordが権威的か」という問いが生まれ、Registry Neutrality Principleと矛盾する。

2. Validationの単純性: 1:1であればRecord IDとArtifactの対応関係の検証が単純になる（KN-005 Validationの設計負荷が下がる）。

3. 拡張方向の非対称性: 1:1から1:Nへの拡張は将来可能である。しかし1:N前提で設計した後に1:1に戻すことは困難である。現時点では1:1を採用し、必要性が生じた際に拡張する。

#### 将来検討事項（今回は設計しない）

1:Nへの拡張（1つのArtifactに複数のRecord）が必要になるユースケースとして以下が想定される。

- 同一Artifactを異なるCategory/Seriesの視点で分類する場合
- 多言語版・バージョン違いを同一Artifactとして扱う場合

これらのユースケースは現時点では発生していない。1:N拡張が必要になった場合は、
独立した設計TODO（Architecture Contract相当）として起票し、KN-004/KN-005への影響を評価した上で判断する。

---

### 0-3. Record Identity（同一性の定義）

RecordはIdentifierのみによって同一性を定義する。

「同じRecord」とは「同じIdentifierを持つRecord」である。
Source・Reference等の他のフィールドが異なっていても、Identifierが同じであれば同一のRecordとみなす。

この方針を採用する理由は以下の通りである。

- Identifierは Registry 内でRecordを一意に識別するために設計される（TERM-001 Identifier定義）。同一性の判定にIdentifier以外のフィールドを加えると、「どのフィールドが同一性に関わるか」という解釈の余地が生まれ、Validationが複雑になる。
- Index ModelではRecordは索引エントリである。索引の同一性はキー（Identifier）によって定まる。

フィールドの詳細・Identifierの命名規則はKN-004（Schema）で定義する。

---

### 0-4. Record = Index、Proxyではないという設計原則

「RecordはArtifactの代理（Proxy）ではなく、Artifactを発見可能にする索引（Index）である。」

この一文をKN-003の設計原則として明記する。

TERM-001セクション2-2はIndex Modelを採用し、「Record は Artifact の内容を複製・内包するのではなく、Artifact への参照情報（Reference）を保持する構造として設計されるべきである」と定めた。

本原則はその確定をRecord単位に橋渡しするものである。

Proxy（代理）との違い:
- Proxyモデルでは、RecordはArtifactの代わりに問い合わせに応答する。RecordがArtifactの内容・属性を内包する。
- Index Modelでは、RecordはArtifactの「場所」を返すのみである。内容の取得はArtifactを直接参照することで行う。

MoCKA RegistryはIndex Modelを採用するため、Recordの設計はProxy的な振る舞いを排除する。

---

## Phase 1: Recordが持つ情報の種類

Recordが保持する情報を5つのカテゴリに整理する。
本セクションでは各カテゴリの目的・情報の性質・KN-004以降との関係を記述する。
個々のフィールド名・型・必須項目はKN-004（Schema）で定義する。

---

### 1-1. Identity

#### 目的

Registry内でこのRecordを一意に識別するための情報を保持する。
IdentityがなければRecordを特定できず、検索・参照・更新のいずれも成立しない。

#### 含まれる情報の性質

- Registryの中でRecordを一意に識別する識別子（Identifier）に関する情報
- Identifierの命名体系・形式に関する情報（体系自体の記録）

Identityは変更されることを想定しない。変更が必要な場合は新規Recordの作成と旧Recordの廃止を原則とする。

#### KN-004以降との関係

KN-004（Schema）でIdentifierのフィールド名・型・形式制約を定義する。
KN-005（Validation）でIdentifierの一意性検証ルールを定義する。

---

### 1-2. Reference

#### 目的

Artifactの場所・参照先を示す情報を保持する。
Index Modelにおいて、ReferenceはRecordの中核をなす情報カテゴリである。

「RecordはArtifactを発見可能にする索引である」という設計原則（Phase 0-4）を具体化するのがReferenceである。

#### 含まれる情報の性質

- Artifactの格納場所を示す情報（ファイルパス・URL等）
- Artifactを識別するための参照キー（Artifact固有の識別子等）
- SourceがArtifactとして外部に存在する場合、その参照情報

ReferenceはArtifactが移動した場合に更新が必要になる情報カテゴリである。
Reference自体がArtifactの内容を複製することはない。

#### KN-004以降との関係

KN-004（Schema）でReferenceフィールドの型・形式（パス形式・URL形式等）を定義する。
KN-005（Validation）でReferenceが示す先のArtifactが到達可能かどうかの検証ルールを定義する（到達可能性検証の範囲はKN-005で決定する）。

---

### 1-3. Classification

#### 目的

このRecordがどの種類のArtifactを指しているかを示す情報を保持する。
Classificationにより、Registry全体から特定の種別・カテゴリ・シリーズに属するRecordを絞り込む検索が可能になる。

#### 含まれる情報の性質

Classification内の情報は以下の2階層に分かれる。

- Artifact Type: Artifactの種別を示す情報（KN-001セクション2の登録対象種別: DOCUMENT/EVENT/DECISION/POLICY/SPEC等）。KN-004でこの語をフィールド名として使用することを前提とする。
- Category/Series: ArtifactがどのCategory（DP/GV/KN等）・Seriesに属するかを示す情報（KN-002で確立した体系に対応）。Artifact Typeとは別階層の分類情報である。
- Series内での番号・順序に関する情報（該当する場合）

ClassificationはRegistry Neutrality Principleに準拠し、Artifactの品質・重要度は含まない。
「何の種類か」を示すのみであり、「良いか悪いか」は含まない。

Maturity（成熟度）はCategory/Seriesの属性であり、個別RecordのClassification情報ではない（TERM-001 Maturity定義準拠）。

#### KN-004以降との関係

KN-004（Schema）でArtifact Type・Category・Series等のフィールド定義と許容値を定義する。
KN-005（Validation）でClassification値がKN-002で確立した体系と整合するかの検証ルールを定義する。

---

### 1-4. Lifecycle

#### 目的

Recordの生存状態を管理する情報を保持する。
Lifecycleにより「このRecordが現在有効か、廃止されたか、アーカイブされたか」を把握できる。

#### 含まれる情報の性質

- Recordの状態（Status）に関する情報
  - KN-001セクション5で予告されたDraft / Review / Approved / Deprecated / Archivedが基本形
  - 詳細な状態遷移はKN-006（Registry Lifecycle）で定義する
- 状態が変化した時点に関する情報（いつ状態が変わったか）

RecordのLifecycleはRecord自身の管理状態であり、Artifactのライフサイクルを表すものではない。
LifecycleはRecord自身の生存状態を管理するものであり、Artifactの承認状態とは区別される。
「RecordがRegistry内で有効か」という問いにLifecycleが答える。
「ArtifactがMoCKAとして承認されたか」という問いはHuman Approval Gateが答え、Registryの外部で管理される。

#### KN-004以降との関係

KN-004（Schema）でStatusフィールドの型・許容値（列挙型）を定義する。
KN-005（Validation）でStatus値の整合性（存在しない状態値が使われていないか等）を検証する。
KN-006（Registry Lifecycle）でStatusの詳細な状態遷移（遷移可能な方向・条件）を定義する。

---

### 1-5. Metadata

#### 目的

Record自体の管理に必要な補助的情報を保持する。
Metadataは検索・絞り込みの主軸ではなく、監査・追跡・運用管理のために使用する。

#### 含まれる情報の性質

- Recordが作成された日時に関する情報
- Recordが最後に更新された日時に関する情報
- Recordを作成した主体に関する情報（くろこ等のAI識別子、または人間起草者）
- Recordに付与されるラベル・タグ等の補助的な分類情報（将来検討）

Metadataは自動的に生成・更新されることが望ましい情報カテゴリである。
MetadataはArtifactの内容に関する情報を含まない。
MetadataはRecordの管理情報であり、Record Identityには含まれない。

#### KN-004以降との関係

KN-004（Schema）でMetadataフィールドの型・形式（日時形式・主体の表記規則等）を定義する。
KN-005（Validation）でMetadataの形式整合性（日時形式が正しいか等）を検証する。

---

### 設計思想：Authorityという情報カテゴリは存在しない

Registry には Authority（権限・権威）という情報カテゴリは存在しない。

これは Scope Freeze による先送りではなく、設計思想として意図的に排除している。
Record が Authority 情報を持つと、「どの Record が権威的か」という問いが生まれ、
Registry Neutrality Principle と矛盾するためである。

Recordの権威性・正当性の判断は Human Approval Gate が担い、Registry の外部で行われる。

---

## Phase 2: Scope Freeze

以下は本文書の範囲外である。

| 範囲外の事項 | 担当 |
|---|---|
| JSON Schemaの定義（フィールド名・型・形式制約） | KN-004の範囲 |
| 必須項目・省略可能項目の決定 | KN-004の範囲 |
| Validator・整合性検証ルール | KN-005の範囲 |
| Statusの詳細な状態遷移（遷移条件・許可方向） | KN-006の範囲 |
| 実装（ファイル生成・データ操作・コード変更） | KN-007の範囲 |
| Identifierの命名規則・形式の詳細 | KN-004の範囲 |
| Source正本の確定 | 独立 TODO の範囲 |

---

## 参照文書

- REGISTRY_CHARTER_v1.0.md（KN-001）: Registry の目的・責務・Registry Neutrality Principleの源泉
- CATEGORY_REGISTRY_v2.0.md（KN-002）: Category/Series体系・Index Modelの実践例
- TERM-001_REGISTRY_TERMINOLOGY.md（TERM-001）: 用語集・Index Model採用・設計原則の確定
- GM2_REGISTRY_BASELINE_002.md: KN-003着手の前提条件確認・申し送り論点

---

## KN-004 への申し送り

KN-004 では、Record が持つ情報だけでなく「Record が絶対に持ってはいけない情報」を冒頭で禁止事項として一覧化すること。

禁止事項の候補（本文書では対応しない）：
- Artifact 本文・内容データ
- 品質評価・承認判断の結果
- 他の Record との関係情報
- 正本（Source）の判定結果

---

## 改訂履歴

- v1.0（2026-07-01）: KN-003として新規作成。Record Specification（Phase 0: 4確定事項 + Phase 1: 5情報カテゴリ）。くろこ起草、きむら博士承認待ち。
- v1.1（2026-07-01）: 4点修正（Artifact Type固定・Lifecycle一文追加・Metadata一文追加・Authority排除明記）+ KN-004申し送り追加。

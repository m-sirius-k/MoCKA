# CATEGORY_REGISTRY_v2.0

KN-002: Category Registry

Artifact Type: Governance Document
Completion Evidence: .md 必須
Evidence Location: docs/governance/CATEGORY_REGISTRY_v2.0.md
Verification Status: Pending（きむら博士承認待ち）

---

## 1. 本文書の目的

本文書は REGISTRY_CHARTER_v1.0（KN-001）セクション2が定める登録対象種別のうち、
CATEGORY（MoCKA 内の分類体系）をRegistryとして整理するものである。

整理対象は以下の2つの既存制度記録である：

- CATEGORY_REGISTRY_V1（6カテゴリ: DP/GV/IA/OA/KN/KA）
- KN_SERIES_LEDGER（KN カテゴリ内の Registry Series/Atlas Series）

本文書は存在する分類体系を登録・参照可能にすることを責務とする。
フィールド定義・スキーマ・Validator・実装は本文書の範囲外である。

---

## 2. カテゴリ一覧（CATEGORY_REGISTRY_V1 Registry 登録エントリ）

CATEGORY_REGISTRY_V1 で確定した 6 カテゴリを、Registry 登録エントリとして以下に示す。

| カテゴリ略号 | 正式名称 | 説明 | カテゴリ成熟度 | 現在のシリーズ数 |
|---|---|---|---|---|
| DP | Decision | 意思決定制度に関するカテゴリ | Active | 1（Decision Policy Series） |
| GV | Governance | ガバナンス監査に関するカテゴリ | Active | 1（Governance Audit Series） |
| IA | Impact | 影響評価・監査に関するカテゴリ | Active | 1（Impact Audit Series） |
| OA | Operational Assurance | 運用保証に関するカテゴリ | Reserved | 0 |
| KN | Knowledge Navigation | 知識ナビゲーションに関するカテゴリ | Active | 1（Registry Series、進行中） |
| KA | Knowledge Activation | 知識活性化に関するカテゴリ | Reserved | 0 |

備考:
- Active = カテゴリに属するシリーズが少なくとも1つ以上稼働中または完了済みである。
- Reserved = カテゴリ名のみ制度化し、稼働シリーズが存在しない状態。
- Historical = 廃止済みカテゴリ。Registry には残し履歴として保持する。
- 詳細な状態遷移は KN-006 Lifecycle で定義する。

本テーブルが 6 カテゴリの正式な Registry 登録エントリである。
CATEGORY_REGISTRY_V1（MOCKA_TODO_ACTIVE.json 内）はこの登録の一次ソースであり、
本文書はそれを Governance Document として整理したものである。

---

## 3. シリーズ一覧（KN_SERIES_LEDGER および既存シリーズの Registry 登録エントリ）

### 3-1. KN カテゴリのシリーズ（KN_SERIES_LEDGER 準拠）

| シリーズ名 | カテゴリ | 略号 | 現在の番号 | 状態 |
|---|---|---|---|---|
| Registry Series | KN（Knowledge Navigation） | KN | KN-001 承認済み、KN-002 進行中 | Planning（稼働中） |
| Atlas Series | KN（Knowledge Navigation） | （未定） | （未着手） | 将来予告のみ |

- Registry Series = 「何が存在するか」を知る（What）機能を担う。
- Atlas Series = 「どう繋がっているか」を知る（How）機能を担う。両シリーズの責務分離は KN-001 セクション 4 で明文化済み。

### 3-2. その他のカテゴリのシリーズ

| シリーズ名 | カテゴリ | 略号 | Artifacts | 状態 |
|---|---|---|---|---|
| Decision Policy Series | DP（Decision） | DP | TODO_399, 400, 401, 402, 404, 405 | 完了（全件 completed） |
| Governance Audit Series | GV（Governance） | GV | TODO_406, 407, 408, 409 | 完了（全件 completed） |
| Impact Audit Series | IA（Impact） | IA | IA-001 | 完了 |

備考: DP/GV/IA の各シリーズは CATEGORY_REGISTRY_V1 第2段階（既存シリーズ名称不変・分類のみ付与）の方針に従い、シリーズ名称は変更していない。上記テーブルは分類の対応表として機能する。Artifacts 列は個別成果物の識別子を示す。識別子の命名規則が将来変わっても表構造は変わらない。

---

## 4. カテゴリとシリーズの階層関係

### 4-1. 構造原則

MoCKA のカテゴリとシリーズは以下の 1:N 階層構造を持つ。

> 1 つのカテゴリは 0 個以上のシリーズを持つ。
> 1 つのシリーズは必ず 1 つのカテゴリに属する。
> シリーズ間に親子関係はない（すべて同一カテゴリ内のフラット構造）。

- カテゴリは「責務（Why）」で定義される安定した骨格である。
- シリーズは「成果物（What）」で定義される成長可能な部分である。
- シリーズはカテゴリの責務を実現する単位である。
- カテゴリは安定、シリーズは増えてよい——これが CATEGORY_REGISTRY_V1 の設計原則である。

### 4-2. 階層ツリー（2026-07-01 時点）

```
MoCKA カテゴリ体系
|
+-- DP (Decision)
|    +-- Decision Policy Series [完了]
|
+-- GV (Governance)
|    +-- Governance Audit Series [完了]
|
+-- IA (Impact)
|    +-- Impact Audit Series [完了]
|
+-- OA (Operational Assurance)
|    （シリーズなし・予約）
|
+-- KN (Knowledge Navigation)
|    +-- Registry Series [稼働中]
|    |    +-- KN-001: Registry Charter [承認済み]
|    |    +-- KN-002: Category Registry [進行中]
|    |    +-- KN-003 〜 KN-007: [前段階承認後に着手]
|    |
|    +-- Atlas Series [将来予告のみ]
|
+-- KA (Knowledge Activation)
     （シリーズなし・予約）
```

---

## 5. カテゴリの追加・廃止ルール（大枠）

詳細な状態遷移（Draft / Review / Approved / Deprecated / Archived 等）は KN-006 Lifecycle で定義する。
本セクションでは追加・廃止の大枠のみを示す。

### 5-1. カテゴリ追加の条件（大枠）

カテゴリを追加できる条件の大枠は以下の通りである。

1. 既存シリーズの追加で解決できないこと（新カテゴリは最後の手段である）。
2. 既存の 6 カテゴリ（DP/GV/IA/OA/KN/KA）のいずれにも収まらない新たな責務領域が明確に存在すること。
3. 追加の必要性が具体的な成果物（シリーズ・文書）の発生見込みに基づくこと（概念だけによる先行追加は行わない）。
4. Human Approval Gate（きむら博士が現時点での承認者）による明示的な承認を得ること。
5. カテゴリ追加は CATEGORY_REGISTRY のこのファイルを改訂するガバナンス文書変更として扱い、CHANGE_START/CHANGE_DONE を記録すること。

### 5-2. カテゴリ廃止の条件（大枠）

カテゴリを廃止できる条件の大枠は以下の通りである。

1. 廃止対象カテゴリに属するシリーズが全件 completed または archived 状態であること。
2. 廃止後に同カテゴリの責務を引き受けるカテゴリが存在するか、または当該責務の消滅が明示されること。
3. Human Approval Gate による明示的な承認を得ること。
4. 廃止はカテゴリを削除するのではなく、状態を「廃止」として Registry に残し、履歴として保持する。

### 5-3. 現状の運用方針

CATEGORY_REGISTRY_V1 の設計思想（「カテゴリは安定、シリーズは増えてよい」）に基づき、
現時点では 6 カテゴリを固定とし、新カテゴリの追加は慎重に判断する。
カテゴリ追加よりもシリーズ追加で吸収できないか先に検討すること。

---

## 6. 参照文書

- REGISTRY_CHARTER_v1.0.md（KN-001）: Registry Series 憲章、Registry の目的・責務・位置付けを定義
- MOCKA_TODO_ACTIVE.json 内 CATEGORY_REGISTRY_V1: 6 カテゴリ確定の一次ソース
- MOCKA_TODO_ACTIVE.json 内 KN_SERIES_LEDGER: KN カテゴリのシリーズ台帳
- MOCKA_TODO_ACTIVE.json 内 GM2_BASELINE_STEP1: Step1 完了時点のスナップショット

注: Governance Document（本文書）と Operational Record（MOCKA_TODO_ACTIVE.json）のどちらを正本とするかは、将来の KN-006（Lifecycle）または独立した方針決定 TODO で扱う未確定事項である。

---

## 改訂履歴

- v2.0（2026-07-01）: KN-002 として新規作成。CATEGORY_REGISTRY_V1 および KN_SERIES_LEDGER を Governance Document として整理。くろこ起草、きむら博士承認待ち。

備考: v1.0 は存在しない。CATEGORY_REGISTRY_V1 は MOCKA_TODO_ACTIVE.json 内の記録であり、本文書（v2.0）は GM2 Registry Series の中でそれを正式な Governance Document として整理したものである。

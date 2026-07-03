# Activity Frequency Metadata v0.1

位置づけ: 博士裁定(2026-07-03、STATUS_VOCABULARY_v1.0_CONSTITUTION.md第2部)に基づき新規作成。「更新頻度」を、Status Vocabulary(状態・成熟度を表す7段階語彙)とは独立した補助メタデータ軸として定義する。Status Vocabularyへの新規段階追加は行わない代替として新設する。

目的: README等の自己申告によるStatus表記(状態・成熟度)と、実際の更新頻度(観測事実)は性質の異なる別々の情報である。この2つを単一の語彙(Status Vocabulary)に混在させず、別軸のメタデータとして独立に記録する。

実装・コード変更は一切含まない。既存ファイルの上書きは行わない。v0.1とし、v1.0は名乗らない。

---

## 第1部: Status VocabularyとActivity Frequencyの関係

| 軸 | 定義 | 情報源 | 定義ファイル |
|---|---|---|---|
| Status Vocabulary(状態・成熟度) | Research/Active Development/Active/Stable/Frozen/Deprecated/Archivedの7段階。README等の自己申告に基づく | README Status節等(自己申告) | REPOSITORY_STATUS_VOCABULARY_v0.1.md |
| Activity Frequency(更新頻度) | 最終pushからの経過日数等、観測可能な活動頻度の指標。本ファイルで定義 | GitHub pushed_at等(観測事実) | 本ファイル |

両軸は独立して記録し、一方の値が他方の値を自動的に決定することはない。Status VocabularyがActive Developmentであっても、Activity Frequencyが低い(更新間隔が長い)場合はその両方をそのまま並記する。矛盾の評価・解釈は本ファイルの対象外とする。

---

## 第2部: 適用例(Task-Hで記録済みの観測事実の再整理)

REPOSITORY_STATUS_VOCABULARY_v0.1.md第2部の記載(本文および備考欄の数値)を、Activity Frequency軸の初期適用例として再掲する。数値の再取得は行っていない。

| リポジトリ | Status Vocabulary(自己申告) | 最終push(Repository Health Report v1.0時点、2026-07-03起算) |
|---|---|---|
| MoCKA(コア) | Active Development | 0日前 |
| mocka-runtime | Active Development | 17日前(mocka-public行の備考欄に記載の数値) |
| mocka-outfield | Active Development | 17日前(同上) |
| mocka-civilization | Active Development | 96日前(2026-03-29) |
| mocka-external-brain | Active Development | 96日前(2026-03-29) |
| mocka-transparency | Active Development | 96日前(2026-03-29) |
| MoCKA-KNOWLEDGE-GATE | Active Development | 96日前(2026-03-29) |
| mocka-public | Active Development | 48日前 |

---

## 第3部: 未確定事項

- 「更新頻度」を段階分け(例: 30日以内/90日以内/90日超等)して表示するかどうか、その閾値は本ファイルでは確定していない。閾値の設定は評価行為(何が「活発」かの判定)を伴うため、別途博士裁定が必要
- Activity Frequencyの記録先(既存のどのファイル・DBに格納するか)は本ファイルでは未確定。現時点では概念定義のみ
- Status VocabularyとActivity Frequencyの不一致(例: Active Developmentかつ96日間更新なし)が一定の閾値を超えた場合に何らかの通知・監査対象とするかどうかは、本ファイルの範囲外(評価行為に該当するため)

---

## 改訂履歴

- v0.1(2026-07-03): 博士裁定(STATUS_VOCABULARY_v1.0_CONSTITUTION.md第2部)に基づき新規作成。

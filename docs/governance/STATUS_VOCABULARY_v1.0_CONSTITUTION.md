# Status Vocabulary v1.0 - Constitution

位置づけ: 博士裁定(2026-07-03)に基づき、STATUS_VOCABULARY_v1.0_DRAFT.mdの第1部・第2部・第3部を確定する。DRAFTからの変更点は、博士裁定によりくろこ原案(選択肢A/A/B)の一部が修正された結果を反映したものである。DRAFT.mdは削除せず、検討過程の参照履歴として保持する。

実装・コード変更は一切含まない。既存ファイルの上書きは行わない。

---

## 博士裁定ログ(承認記録)

2026-07-03、博士より以下の裁定が示された。

| 項目 | 裁定 | 備考 |
|---|---|---|
| EN/JP正規表記(Ambiguity-4) | 修正採用 | 正規表記はStatus Vocabulary本体(7段階体系)側の値に依存させる。EN/JPは両方alias化。ステータス値そのものを言語表記から独立させる |
| Active/Active Development混在(Ambiguity-1) | NO(新設なし) | Status Vocabularyには新規段階を含めない。「Activity Frequency」を別軸の補助メタデータとして新設する |
| sirius-lab二重体系(Ambiguity-3) | YES(選択肢B) | 統合せず、product layer / repository layerの境界明示型並列構造として制度化する |

くろこ原案(STATUS_VOCABULARY_v1.0_DRAFT.md)からの修正点として、EN/JP正規表記・Active/Active Development混在の2件について「言語問題とステータス体系の分離」「時間軸(更新頻度)と状態軸(成熟度)の混線の切り分け」という、DECISION_RULE_LAYER_v1.0.mdの類型分類よりさらに一段細かい区別が博士により指摘された。

---

## 第1部: EN-JP不一致(Ambiguity-4)の正規表記 - 確定

対象: m-sirius-k(プロフィール)README。EN版"Research Stage: Active Development"、JP版「研究開発段階」。

確定内容: 正規表記そのものを特定の言語の文字列(EN/JPいずれか)として固定しない。正規表記は、標準7段階語彙(REPOSITORY_STATUS_VOCABULARY_v0.1.md第1部で定義: Research/Active Development/Active/Stable/Frozen/Deprecated/Archived)のうち、当該対象に該当する値そのものに依存する識別子として扱う。ステータス値は言語表記から独立させる。

m-sirius-k(プロフィール)については、標準7段階語彙上の該当値を"Active Development"とする。これは標準7段階語彙自体がこの識別子群で定義されているために生じる帰結であり、EN表記を正規表記として優先したという意味ではない。当該値がたまたま英単語で表記されていることと、EN/JPいずれかの言語を正規表記として選好したこととは区別する。

alias登録:
- EN原文: "Research Stage: Active Development"
- JP原文: 「研究開発段階」

いずれも上記の標準値"Active Development"に対するalias(表示用の言語別文言)として記録する。alias自体がステータス判定の根拠になることはない。

---

## 第2部: Active/Active Development混在(Ambiguity-1)の語彙体系上の扱い - 確定

確定内容: Status Vocabulary(標準7段階語彙)への新規段階追加は行わない。

対象4リポジトリ(mocka-civilization/mocka-external-brain/mocka-transparency/MoCKA-KNOWLEDGE-GATE)で観察された「README表記は"Active Development"のまま、実際の更新は96日間ない」という状態は、状態(成熟度)を表すStatus Vocabularyの問題ではなく、別軸の指標(更新頻度)の問題として切り分ける。

更新頻度は、新設する補助メタデータ「Activity Frequency」(ACTIVITY_FREQUENCY_METADATA_v0.1.md参照)で扱う。Status Vocabularyの7段階はそのまま維持し、変更しない。

個別リポジトリへの実際の当てはめ(7段階のどの値に該当するか)は、Task-I(SATELLITE_REPOSITORY_POSITIONING_OPTIONS_v0.1.md)の選択肢を踏まえてQUEUE-2で扱う。本節では語彙体系そのものへの変更を行わないことのみを確定する。

---

## 第3部: sirius-lab二重体系(Ambiguity-3)の裁定 - 確定

確定内容: 選択肢B(統合せず、意図的並行・境界明示による共存)を採用する。

境界の基準:

| レイヤー | 適用語彙 | 適用範囲 |
|---|---|---|
| repository layer | 標準7段階語彙(Research/Active Development/Active/Stable/Frozen/Deprecated/Archived) | GitHub上の各リポジトリのStatus節。REPOSITORY_STATUS_VOCABULARY_v0.1.mdが対象とする12リポジトリを含む |
| product layer | sirius-lab独自4段階(LIVE/IN DEV/RESEARCH/COMING SOON) | sirius-lab README内の製品一覧表に列挙される個別製品のステータス表記 |

運用規則:
- 標準7段階語彙をsirius-lab配下の個別製品表記に適用しない
- sirius-lab独自4段階をGitHubリポジトリ単位のStatus節に適用しない
- 両語彙間の対応表(例: LIVE≒Active等)は本裁定時点では作成しない。対応表が必要になった場合は、別途裁定を経てから作成する

---

## 改訂履歴

- v1.0(2026-07-03): 博士裁定を反映し確定。STATUS_VOCABULARY_v1.0_DRAFT.mdからの変更点を第1部・第2部・第3部に反映。DRAFT.mdは参照履歴として保持。

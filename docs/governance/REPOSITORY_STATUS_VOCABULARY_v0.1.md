# Repository Status Vocabulary v0.1

位置づけ: くろこ作業指示(2026-07-03、Task-H)に基づき新規作成。Repository Health Report v1.0(同日、チャット内で博士に提示済み、ファイルとしては未保存)のフォローアップ。GitHub上の公開リポジトリ12件のステータス表記が制度上統一されていない問題を解消するため、標準語彙を定義し、各リポジトリの現行表記との対応関係を整理する準備文書である。

本ファイルはコードではなく語彙定義と対応表の作成のみを目的とする。v0.1とし、v1.0は名乗らない。実装・コード変更は一切含まない。既存ファイル(VOCABULARY_PATTERN_AUDIT_TARGET_LIST_v0.1.md等)の上書きは行わない。

Level分離の明記: 本ファイルの記載事実は、2026-07-03時点でRepository Health Report v1.0作成時に取得したGitHub公開情報(README本文・pushed_atタイムスタンプ・リポジトリ構成)に基づくLevel1(観察)の範囲にとどまる。セッション記憶や推測は観察事実として扱わない。原因の推測・断定は行わず、不確かな点は「要確認」と明記する。

---

## 第1部: 標準語彙(7段階)

博士指示により、以下7段階を標準語彙の基本形とする。この7段階は今回博士から提示されたものであり、本ファイルでの新規提案ではない。

| Status | 意味 |
|---|---|
| Research | 概念検証段階 |
| Active Development | 機能追加・設計変更を継続中 |
| Active | 継続運用中(保守・改善を含む) |
| Stable | 大きな変更予定なし、保守中心 |
| Frozen | 意図的に変更停止、保存対象 |
| Deprecated | 後継へ移行中、利用非推奨 |
| Archived | 保管のみ、開発終了 |

---

## 第2部: 12リポジトリの現行表記との対応表

対象は、Repository Health Report v1.0で調査した m-sirius-k 配下の公開リポジトリ12件。「現行表記(原文)」列は README等から確認できた文言をそのまま引用し、「7段階対応」列は字面上もっとも近い語を機械的に当てはめたものである。当てはめが一意にできない場合は「対応不能」とし、第3部のAmbiguity実例に回す。

| リポジトリ | 現行表記(原文) | 出典 | 7段階対応 | 備考 |
|---|---|---|---|---|
| MoCKA(コア) | "v1.0.0 - Active Development" | README Status節 | Active Development | 字面一致 |
| mocka-runtime | "Active Development" | README Status節 | Active Development | 字面一致 |
| mocka-outfield | "Active Development" | README Status節 | Active Development | 字面一致 |
| mocka-civilization | "Active Development" | README Status節 | Active Development(字面) | 最終push 96日前(2026-03-29)という別軸の観察との整合性は要確認。第3部Ambiguity-1参照 |
| mocka-external-brain | "Active Development" | README Status節 | Active Development(字面) | 同上。第3部Ambiguity-1参照 |
| mocka-transparency | "Active Development" | README Status節 | Active Development(字面) | 同上。第3部Ambiguity-1参照 |
| MoCKA-KNOWLEDGE-GATE | "v1.0.0 - Active Development" | README Status節 | Active Development(字面) | 同上。第3部Ambiguity-1参照 |
| mocka-public | "Active Development" | README Status節 | Active Development(字面) | 最終push 48日前。上記4件より短いが、本体(0日)・runtime/outfield(17日)と比べると差がある。要確認 |
| execution-runtime-system | "Closed-loop governance system finalized" / "v1.0-runtime-final" / "FULLY IMPLEMENTED AND VERIFIED" | README冒頭・Status節 | 対応不能 | 第3部Ambiguity-2参照 |
| sirius-lab | リポジトリ単位のStatus表記は確認できず。製品ごとに LIVE / IN DEV / RESEARCH / COMING SOON という別体系を使用 | README 製品一覧表 | 対応不能(対象がリポジトリでなく製品単位のため) | 第3部Ambiguity-3参照 |
| sirius-lab-products | 未確認(Repository Health Report v1.0作成時、README本文は未取得。ディレクトリ構成のみ確認済み) | - | 未確認 | 要確認 |
| m-sirius-k(プロフィール) | EN: "Research Stage: Active Development" / JP: "研究開発段階" | README Status節 | 対応不能 | 第3部Ambiguity-4参照 |

---

## 第3部: Status Vocabulary Ambiguity 実例記録

対応表で「対応不能」または要確認とした事例のうち、単なる未確認ではなく語彙自体の曖昧さに起因すると考えられるものを、以降の本体監査で利用できるよう実例として記録する。

### Ambiguity-1: 表記(Active Development)と更新間隔の不整合の疑い

mocka-civilization / mocka-external-brain / mocka-transparency / MoCKA-KNOWLEDGE-GATE の4件は、いずれもREADME上は7段階語彙の"Active Development"とそのまま一致する表記を持つ。一方、4件とも最終push日時が同一(2026-03-29 03:01)であり、Repository Health Report v1.0作成時点(2026-07-03)で96日間更新がない。

7段階語彙の定義上、"Active Development"は「機能追加・設計変更を継続中」を意味する。96日間更新がない状態がこの定義に該当するかどうかは、語彙定義自体からは判定できない。これは語彙の意味が曖昧という問題ではなく、「表記(自己申告)」と「観察された更新頻度」という異なる2つの情報源が食い違う可能性がある、という事実の記録にとどめる。どちらが実態を反映しているかの判定はTask-Iで扱う。

### Ambiguity-2: execution-runtime-systemの独自語彙

execution-runtime-systemのREADMEは、7段階語彙のいずれの語も直接使用していない。代わりに以下の独自表現を用いている。

- "Closed-loop governance system finalized. No further structural modifications."
- "Status: v1.0-runtime-final"
- "FULLY IMPLEMENTED AND VERIFIED"

これらの語感は7段階のうち"Frozen"(意図的に変更停止、保存対象)に近いと推測されるが、"VERIFIED"(検証済み)という語は完了・品質保証のニュアンスを含み、"Stable"寄りの含意もありうる。README側が7段階語彙を採用していないため、機械的な対応付けができない。どちらの語が実態として近いかの判定はLevel2以降(Task-K)で扱う。

### Ambiguity-3: sirius-labにリポジトリ単位のStatus表記が存在しない

sirius-labのREADMEには、リポジトリ全体を指す単一のStatus節が存在しない。その代わり、製品ごとに LIVE / IN DEV / RESEARCH / COMING SOON という、7段階語彙とは別の4段階体系が使われている。この4段階と7段階語彙の対応関係(例: LIVE≒Active、IN DEV≒Active Development等)は今回の指示範囲では定義されておらず、対応付けを行うと新たな解釈が入るため、本ファイルでは対応付けを行わず、2つの異なる語彙体系が並存している事実のみを記録する。

### Ambiguity-4: m-sirius-k(プロフィール)のEN/JP表記の不一致、および複合語

m-sirius-kのREADMEは、EN版で"Research Stage: Active Development"という複合表現を用いている。これは7段階語彙のうち"Research"と"Active Development"の両方を含んでおり、どちらか一方に一意に対応しない。

さらに、同じREADME内のJP版では、対応する箇所が「研究開発段階」と記載されており、EN版の"Active Development"に相当する語がJP版には見当たらない。同一ファイル内でEN/JP間の表記が完全に対応していない状態であり、これも語彙の対応付けを困難にしている一因として記録する。

### 参考: PHI-OSの状態表記の不一致(Task-J先行観察)

Task-Jの調査過程で、PHI-OSという同一製品について、sirius-lab-products内の`phi-os/README.md`が"Coming Soon"と記載している一方、公開Webサイト(m-sirius-k.github.io/sirius-lab/phi-os/)は"Research Preview"および"Peer-reviewed Research - Under Review"と記載していることが確認された。これは7段階語彙(リポジトリ単位)とは対象の粒度が異なる(製品単位・ページ単位の表記)ため本ファイルの対応表には含めないが、同種のStatus Vocabulary Ambiguityの実例として参考記録する。詳細と出典はTask-J文書(PHI_OS_REFERENCE_PATH_CHECK_v0.1.md)を参照。

---

## 第4部: 提案 - 既存監査対象一覧への観察軸追加

`VOCABULARY_PATTERN_AUDIT_TARGET_LIST_v0.1.md`(Task-F)は、Ledger / Registry / Catalog / Archive / Memory / Loop / Caliber の7対象を扱っている。同ファイルと同じ表形式で、"Status Vocabulary"を新規の観察軸として追加することを提案する。以下はその追加案であり、実際のファイル追記(既存ファイルの上書き)は本指示の範囲外のため行わない。

| 対象 | 今日時点でわかっていること | 出典 | Task-E基準での既知/未知 |
|---|---|---|---|
| Status Vocabulary | リポジトリ12件中7件がREADME上"Active Development"を名乗るが、うち4件は96日間更新がない。execution-runtime-systemは7段階語彙を使わず独自表現("finalized"等)を使用。sirius-labはリポジトリ単位の表記を持たず製品単位の別体系(LIVE/IN DEV等)を使用。m-sirius-kはEN/JPで表記が食い違う | 本ファイル(REPOSITORY_STATUS_VOCABULARY_v0.1.md)第2部・第3部 | Task-Eの4観点(書き込み経路/読み取り経路/失敗時の挙動/参照元一覧)は「ステータス表記」という文書上の語彙が対象であるため、そのままの形では適用しづらい可能性がある。適用可否の判断自体を博士に確認する必要がある(要確認) |

---

## 第5部: 未確定事項

- sirius-lab-productsのREADME本文は本ファイル作成時点でも未取得であり、7段階対応・Ambiguity実例のいずれにも含められていない
- 第4部の観察軸追加案が、Task-E/Fの枠組みにそのまま統合可能かどうかは博士確認が必要
- Ambiguity-1(更新間隔とActive Development表記の不整合疑い)について、「表記が古いだけなのか」「実態が変化しているのか」の判定はTask-Iに委ねる
- Ambiguity-2(execution-runtime-system)の"Frozen"か"Stable"かの判定はTask-Kに委ねる

---

## 改訂履歴

- v0.1(2026-07-03): くろこ作業指示Task-Hに基づき新規作成。

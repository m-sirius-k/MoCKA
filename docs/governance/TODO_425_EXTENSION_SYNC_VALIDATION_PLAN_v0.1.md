# TODO_425 Extension Sync Validation Plan v0.1

作成日: 2026-07-07
対応TODO: TODO_425(Chrome Extension Configuration Sync Pipeline設計)Phase C-0
基準commit: 03227b3(TODO_422-A、mocka-workshop-private main)
前提資料: [TODO_425_EXTENSION_SYNC_INVENTORY_v0.1.md](TODO_425_EXTENSION_SYNC_INVENTORY_v0.1.md)(Phase A) / [TODO_425_EXTENSION_SYNC_DESIGN_v0.1.md](TODO_425_EXTENSION_SYNC_DESIGN_v0.1.md)(Phase B)

本書はPhase Bで推奨候補としたB案(`content.js`のngrok参照をlocalhost:5000へ統一)について、**実装前**に成功条件・失敗条件・切戻し手順を確定する計画書である。本書の作成自体もコード変更・manifest変更・Extension再ビルド・commitを一切伴わない。

**実行主体についての前提**: 本検証は実際のChrome(きむら博士の環境、開発者モードで読み込んだOrchestra拡張、claude.aiへのログイン状態)を用いる必要があり、本セッション単独では実行できない。本書は「何を・どの順で・何をもって合否とするか」の計画であり、実行そのものは別途Human確認ポイント(4節)に沿って行う。

---

## 1. 検証項目

Phase B指示の確認対象5点を、実施可能な具体手順に分解する。

### 1.1 claude.ai上でExtension起動確認

- 対象: `PlanningCaliber/workshop/Orchestra_Project/extension/`(正本パス、TODO_354確定)を`chrome://extensions`の開発者モードで読み込む。
- 手順:
  1. 既存の本番インストール版(Web Store配布版)とは別に、開発者モードで正本パスを「パッケージ化されていない拡張機能を読み込む」で追加する(本番版と同時稼働させる場合は拡張IDの衝突有無を事前確認)。
  2. claude.aiを開き、DevTools Consoleで`[MoCKA]`プレフィックスのログ出力有無を確認する。
  3. `content.js`が正しく注入されていること(`document`上に副作用、例えば`showNotification()`由来のDOM要素が出現しうること)を確認する。

### 1.2 fetchLivingContext()通信確認

- 対象: `content.js`の`fetchLivingContext()`(現行462-490行付近)が実行されるタイミングでのネットワーク挙動。
- 手順:
  1. DevTools Networkタブで`api/handshake`へのリクエストを確認する。
  2. **変更前(現行のngrok URL)**の状態でこのリクエストが実際に成立しているか(200 OK/JSONレスポンス取得)を先に確認する。ここが失敗している場合、そもそも現行版も機能していない可能性があり、その場合は「localhost化で新たに壊す」のではなく「既に壊れているものを直す」という扱いに評価が変わる。
  3. 変更前の結果を記録した上で、次項1.3のlocalhost到達確認に進む。

### 1.3 localhost:5000到達確認

- 対象: `content.js`のホストをngrokから`localhost:5000`へ書き換えた**検証用一時コピー**(開発者モード読込専用、リポジトリにはcommitしない)での動作確認。
- 手順:
  1. COMMAND CENTER(`app.py`、port:5000)が起動していることを確認する(`curl http://localhost:5000/api/handshake`等)。
  2. 検証用一時コピーの`content.js`のみホスト文字列を`http://localhost:5000/api/handshake`に変更し、開発者モードの拡張を「再読み込み」する。
  3. claude.aiをリロードし、1.2節と同じ手順でNetworkタブ上のリクエストが200 OK/JSONレスポンスを返すかを確認する。
  4. `content_orchestra.js`(chatgpt.com等)で既に実績のある挙動(Phase A/B調査で確認済み)と同一の応答が得られるかを比較する。
- 注意: この一時コピーでの検証はリポジトリ本体を変更するものではない。検証後、一時コピーは破棄するか、正式な変更として別途CHANGE_START記録の上でcommitするかを、本検証の結果を踏まえて別途判断する(本書の範囲外)。

### 1.4 ngrok削除時の影響確認

- 対象: `manifest.json`のhost_permissionsに残るngrok URLエントリを**将来削除する場合**の影響範囲(本書時点では削除しない、影響の洗い出しのみ)。
- 手順:
  1. `manifest.json`のhost_permissionsからngrok URLを検索し、他のコード箇所(`background.js`・`content_orchestra.js`等)がこの権限に依存していないかを確認する(Phase Aの棚卸し結果では`content.js`のみが依存)。
  2. Chrome Web Store側で、host_permissions削減がユーザーへの権限再同意プロンプトを発生させるか(削減は通常追加より審査・同意への影響が小さいが、実際の挙動はWeb Store側の審査結果を待つ必要がある)を記録する。
  3. 本書の時点ではhost_permissions自体は変更しない(Phase Bの未決定事項5、manifest変更は本Phaseのスコープ外)。

### 1.5 rollback手順確認

- 対象: 1.3節の変更(`content.js`のホスト文字列変更)を元に戻す手順。
- 手順:
  1. 開発者モード読込のみで検証した場合: 検証用一時コピーを破棄し、リポジトリ側の`content.js`(現行のngrok参照)を再読み込みするだけで完了する(リポジトリ本体は無変更のため実質的なrollbackは発生しない)。
  2. 万一、正式commit後に問題が発覚した場合: TODO_422-Aと同様に対象1ファイル(`content.js`)のみを対象とした`git revert`または旧内容への再Editを行い、CHANGE_START/CHANGE_DONEで記録した上で別コミットとする(TODO_364準拠、`git revert --no-edit`等の一括操作は使わず、対象を明示して差分を確認してから戻す)。

---

## 2. 成功条件

以下をすべて満たした場合に「B案(localhost統一)採用可」と判定する。

1. 1.1節: 開発者モード読込版`content.js`がclaude.ai上で正常に注入され、コンソールエラーが発生しない。
2. 1.2節: 変更前(ngrok参照)の状態で`fetchLivingContext()`のリクエストが実際に成立していることを確認済み(既に壊れている場合は本計画の前提が変わるため、5節「切戻し不要ケース」として別途扱う)。
3. 1.3節: 変更後(localhost参照)の状態で、1.2節と同等以上の応答(200 OK・JSONレスポンス内でLiving Contextパネルが生成される)が得られる。
4. 1.3節: `content_orchestra.js`(chatgpt.com等)で確認済みの挙動と機能的な差異がない(パネル内容・エラーハンドリングの動作が同等)。
5. 1.4節: host_permissionsを変更しない前提のままで動作する(host_permissions変更は本計画のスコープ外のまま成立する)。

---

## 3. 失敗時切戻し条件

| 失敗パターン | 切戻し条件 |
|---|---|
| 1.1節: 開発者モード読込自体が失敗(拡張が有効化されない等) | 検証中止。リポジトリ本体は無変更のため切戻し不要。原因調査を別タスク化する。 |
| 1.2節: 変更前の状態で既にhandshakeが失敗している(ngrok URLが現在無効等) | 「localhost化で壊す」のではなく「既に機能していないものを直す」ケースとして評価を切り替える。この場合、B案の緊急度がむしろ上がる可能性があるため、次工程の判断材料としてきむら博士に報告する。 |
| 1.3節: localhost参照でhandshakeが失敗する(COMMAND CENTER未起動・CORS等) | 検証用一時コピーを破棄し1.5節手順1で切戻す。失敗原因(サーバー未起動か、真の技術的障壁か)を切り分けた上で再検証の要否を判断する。 |
| 1.3節: 応答は得られるが`content_orchestra.js`と機能差がある(パネル内容が異なる等) | 差分の内容を記録し、B案の実装内容(単純なホスト差し替えで足りるか、追加のコード修正が要るか)を見直す。即座に不採用とはせず、Phase Bの原因分析(過去設計残骸)自体を再検証する材料とする。 |
| 正式commit後に本番(Web Store配布版)で問題が発覚した場合 | 1.5節手順2に従い`content.js`のみを対象commitで復元する。`manifest.json`は本計画で変更していないため復元対象に含まれない。 |

---

## 4. Human確認ポイント

本検証はきむら博士の実機(Chrome・claude.aiログイン状態・開発者モード)を用いる必要があり、AIエージェント単独では実行できない。以下の各段階でHuman確認を要する。

1. **検証実施前**: 1.1〜1.3節の手順で問題ないか(特に本番Web Store版と開発者モード版の同時稼働がユーザー環境に支障を与えないか)の最終確認。
2. **1.2節実施後**: 変更前(現行ngrok参照)のhandshakeが実際に成立しているか否かの結果報告。ここで「既に失敗している」場合、本計画の前提(現状動作しているものをlocalhostへ切り替える)自体を見直す必要があるため、結果を博士に報告し次工程の指示を仰ぐ。
3. **1.3節実施後**: localhost参照での動作結果(成功/失敗、`content_orchestra.js`との比較)の報告と、正式commitへ進めてよいかの承認。
4. **1.4節**: host_permissionsのngrokエントリを本当に削除するか、当面残すかの判断(本計画では削除しない前提だが、最終判断は博士に委ねる)。
5. **正式実装移行の可否**: 本計画の1〜3節すべてが成功条件を満たした場合でも、実際の`content.js`修正・CHANGE_START記録・commitは、TODO_422-A同様に博士の明示的な着手指示を得てから行う(本書の完成をもって自動的に実装フェーズへ移行しない)。

---

## 未決定事項

1. 開発者モード版と本番Web Store配布版を同一Chromeプロファイルで同時稼働させる際の拡張ID衝突・干渉有無は未確認(実施前確認事項として4節1.に記載)。
2. 1.2節で「現行ngrok参照が既に機能していない」ことが判明した場合の扱い(緊急度の格上げ)は、実際にその結果が出てから博士と相談する。
3. `manifest.json`のhost_permissions整理(ngrokエントリ削除)の要否は、本計画の範囲外のまま据え置く(Phase Bの未決定事項5を継続保留)。

---

以上、Phase C-0(実機検証計画)完了。実機検証の実施・その結果に基づく`content.js`の正式修正は、本書とは別にきむら博士の明示的な着手指示を得てから行う。

# TODO_425 Extension Sync Validation Result v0.1

作成日: 2026-07-07
対応TODO: TODO_425(Chrome Extension Configuration Sync Pipeline設計)Phase C-1
基準commit: 03227b3(TODO_422-A、mocka-workshop-private main)
前提資料: [TODO_425_EXTENSION_SYNC_VALIDATION_PLAN_v0.1.md](TODO_425_EXTENSION_SYNC_VALIDATION_PLAN_v0.1.md)(Phase C-0)
検証環境: claude-in-chrome MCP経由で接続されたローカルChrome(deviceId: 9a90f68a-62b9-4741-8f22-5373adfc494f、Windows)

本書はPhase C-0計画のステップ1・2(現行ngrok参照状態での動作確認)を実施した結果である。結論から述べると、**計画通りの検証は実施できず、前提条件確認の段階でブロックされた**。コード変更・manifest変更・Extension再ビルド・commitは一切行っていない(`chrome://extensions`へのアクセス自体もツール制約により不可能だった)。

---

## 1. 実施内容

1. `https://claude.ai/new`へ2回(1回目・再現性確認のための2回目)ナビゲーションし、それぞれ2〜3秒待機後にDevTools console messagesとnetwork requestsを取得した。
2. `chrome://extensions`への直接アクセスを試みたが、claude-in-chrome MCPのページ読取ツールは内部ページ(`chrome://`)を「エラーページ表示中」として拒否し、インストール済み拡張機能一覧を確認する手段が本セッションのツールセットには存在しなかった。

## 2. 観測結果

### 2.1 console messages(2回とも同一パターン)

| 出力元 | 内容 |
|---|---|
| `chrome-extension://doapadhfedmognoilmjieekfhijeadnf/content.js`(拡張ID的にはmocka_bridge、`MOCKA_OVERVIEW.json`の`extension_canonical_paths`と照合済み) | `[MOCKA] 送信ボタン待機中...` → `[MOCKA] 送信ボタンクリック成功` → `[MOCKA] DNA注入完了: ⚡MOCKA_v3 HOOKED` |
| Orchestra拡張(`content.js`) | **一切出力なし** |

Orchestra `content.js`の**1行目**には無条件(ガード無し)の`console.log("[Orchestra] content.js loaded")`が存在する(ソース確認済み)。この行が2回のページロードいずれでも一度も出力されていない。

### 2.2 network requests(2回とも同様)

`handshake`を含むURLへのリクエストは0件。観測されたリクエストは全て`anthropic.com`・`googleapis.com`・`datadoghq.com`宛の、claude.ai自体のテレメトリ・通知登録であり、MoCKA関連(ngrok URL・`localhost:5000`のいずれも)への通信は一切確認できなかった。

## 3. 判定

Phase C-0で定めたA/B/Cの判定枠には当てはまらない、第4の結果となった。

- **A(ngrok不要と確認)**: 判定不能。ngrok経由のhandshake自体が試行された形跡がないため「不要と証明された」とは言えない。
- **B(ngrok必要と確認)**: 判定不能。同上の理由で「必要」の証拠も得られていない。
- **C(両方失敗)**: 厳密には異なる。localhost版も試行していないため「両方試して失敗」ではなく、「そもそも試行されていない」。
- **D(新規、本検証の実際の結果)**: **検証環境上でOrchestra拡張自体が実行された形跡がなく、判定不能**。この接続Chrome上でOrchestra拡張が現在有効な状態でインストールされているか自体が未確認。

## 4. 原因の候補(未確定・要Human確認)

1. この接続ブラウザ(claude-in-chrome MCP、deviceId 9a90f68a-...)にOrchestra拡張(開発者モードまたはWeb Store版)がそもそもインストールされていない。
2. インストールはされているが無効化(disable)されている。
3. 別のChromeプロファイル/別デバイスにOrchestra拡張が入っており、本検証で使われた接続ブラウザとは異なる環境である。
4. (可能性は低いが)Orchestra拡張はインストール・有効だが、何らかの理由でcontent_scripts注入自体が失敗している。

`chrome://extensions`はツール制約上AIエージェントからは確認・操作できないため、上記のいずれであるかはHuman(きむら博士)による目視確認が必要。

## 5. Phase C-0計画からの逸脱点

Phase C-0計画のステップ3(検証用一時コピーでlocalhost:5000への変更を試す)には進んでいない。理由: ステップ1・2(現行ngrok版の動作確認)が前提条件の段階でブロックされたため、ここで無理にステップ3へ進んでも「そもそも拡張が動いていない環境でlocalhost版だけ試す」という不整合な比較になり、Before/After比較として意味をなさない。計画の失敗時切戻し条件(パターン「1.1節: 開発者モード読込自体が失敗」に近い状況)に該当するため、ここで一旦停止しHuman確認を仰ぐ。

## Human確認ポイント(次のアクション待ち)

1. この接続Chrome(Windows、deviceId 9a90f68a-62b9-4741-8f22-5373adfc494f)にOrchestra拡張が現在インストール・有効化されているか、`chrome://extensions`で直接確認をお願いしたい。
2. インストールされていない/無効化されている場合: 有効化(または開発者モードで正本パス`PlanningCaliber/workshop/Orchestra_Project/extension/`を読み込み)した上で、本検証(claude.aiでのconsole/network確認)を再実施する。
3. 実は別のブラウザ・プロファイルで運用されている場合: そのブラウザをclaude-in-chrome MCPに接続するか、該当環境での目視確認結果を共有いただく。

いずれの場合も、Phase C-1は「ngrok版が動いているか否か」の判定に到達できておらず、Phase C-2(最小修正)へは進めない状態である。

---

以上、Phase C-1(実機検証)は環境確認のブロッカーにより未完了。次のアクションはHuman確認(上記)を経てからの再実施。

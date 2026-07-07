# TODO_425 Extension Sync Comms Check v0.1

作成日: 2026-07-07
対応TODO: TODO_425(Chrome Extension Configuration Sync Pipeline設計)Phase C-1.3
基準commit: 03227b3(TODO_422-A、mocka-workshop-private main)
前提資料: [TODO_425_EXTENSION_SYNC_VALIDATION_RESULT_v0.1.md](TODO_425_EXTENSION_SYNC_VALIDATION_RESULT_v0.1.md)(Phase C-1) / [TODO_425_EXTENSION_ENV_CHECK_v0.1.md](TODO_425_EXTENSION_ENV_CHECK_v0.1.md)(Phase C-1.1)

本書はユーザー提供のスクリーンショット(chatgpt.com上での`content_orchestra.js`の`Handshake failed: TypeError: Failed to fetch`)を受け、localhost:5000 handshakeの失敗原因を切り分けるための通信基盤確認である。コード変更・commitは一切行っていない(curlによる読取専用確認、既存ブラウザでのナビゲーションのみ)。

**結論を先に述べる**: サーバー・エンドポイント・CORSはすべて正常。実際にchatgpt.com上でExtensionからのhandshakeがライブで成功することも確認した。しかし調査の過程で、**当初の想定より根本的な問題**(claude.ai上でOrchestra `content.js`自体が全く実行されていない)を再現確認した。

---

## 1. Command Center(app.py)起動状態確認

```
netstat -ano | grep ":5000"
→ TCP 127.0.0.1:5000  0.0.0.0:0  LISTENING  12376
```

**起動中**。プロセスがport 5000でLISTENING状態にあることを確認した。

## 2. localhost:5000到達確認

```
curl http://localhost:5000/health
→ {"port":5000,"status":"ok"}
```

**到達可能**。0.21秒でHTTP 200を返した。

## 3. /api/handshake endpoint確認

Extensionが送信するのと同じ形のPOSTリクエストを実際に送信した。

```
curl -X POST http://localhost:5000/api/handshake \
  -H "Content-Type: application/json" -H "Origin: https://chatgpt.com" \
  -d '{"ai_id":"gpt-4o","role":"R01","scope":"mocka","contract_version":"1.0"}'
→ HTTP/1.1 200 OK
→ {"ai_id":"gpt-4o", ..., "handshake":"READY", ...}(11207bytes、正常なLiving Contextペイロード)
```

**正常動作**。`handshake:"READY"`を含む完全なペイロードが返された。

## 4. CORS設定確認

```
curl -X OPTIONS http://localhost:5000/api/handshake -H "Origin: https://chatgpt.com" ...
→ Access-Control-Allow-Origin: https://chatgpt.com / Allow-Credentials: true / Allow-Methods: ...POST...

curl -X OPTIONS http://localhost:5000/api/handshake -H "Origin: https://claude.ai" ...
→ Access-Control-Allow-Origin: https://claude.ai / Allow-Credentials: true / Allow-Methods: ...POST...
```

`app.py`の設定は`CORS(app, origins="*", supports_credentials=True)`(51・54行目)。Flask-CORSは`supports_credentials=True`の場合ワイルドカードを実オリジンへ反映するため、**chatgpt.com・claude.ai双方からのCORSは正しく許可されている**ことを実測で確認した。CORSが原因で失敗する状況ではない。

## 5. Extensionから実際に再fetch確認(claude-in-chrome経由)

接続ブラウザ(deviceId: 9a90f68a-...)で実際にchatgpt.comへナビゲーションし、Extensionの挙動をライブ観測した。

```
[11:52:45] [MoCKA] autoInject: fetch Living Context...
[11:52:46] [MoCKA] Living Context 取得成功: Array(17)
[11:52:46] [MoCKA] injectAndSendContext: start
[11:52:46] [MoCKA] 入力欄を検出: DIV prompt-textarea contentEditable= true
...
[11:52:49] [MoCKA] 送信結果: SUCCESS
```

network requestsにも `http://localhost:5000/api/handshake` POST → `statusCode: 200` が記録された。

**content_orchestra.js(chatgpt.com用)からlocalhost:5000へのhandshakeは、現在完全に成功している**(fetch成功→Living Context取得→入力欄検出→注入→送信まで全工程成功)。

---

## 6. 想定より根本的な発見: claude.ai上でOrchestra content.js自体が実行されていない(再現確認)

上記5でOrchestra拡張自体がこの接続ブラウザ上で確実に稼働していることが証明された(chatgpt.com上で完全動作)。この事実を踏まえて、Phase C-1で確認した「claude.ai上でOrchestra content.jsが動いていない」という結果を**3回目**として再現確認した。

- claude.ai/newへナビゲーション → console messagesを全パターン("."）・エラー限定("onlyErrors")の両方で確認 → **Orchestra `content.js`からの出力(1行目の無条件`console.log("[Orchestra] content.js loaded")`含む)もエラーも一切出力されない**。
- network requestsにも`handshake`関連のリクエストは一切現れない。
- 同一ページで`mocka_bridge`拡張のcontent.jsは正常動作(過去の確認と同じ)。

**結論**: これはネットワーク・CORS・サーバーの問題ではない。Orchestra拡張自体はこのブラウザで稼働しているにもかかわらず、`content.js`(claude.ai専用ファイル)がページに一切注入されていない(スクリプト自体が動いた形跡がゼロ)。

## 7. ユーザー提供スクリーンショットの解釈(再評価)

きむら博士から共有されたスクリーンショット(`content_orchestra.js:451`、`Handshake failed: TypeError: Failed to fetch`)について、本書の6項目の実測結果と合わせて評価すると、**現在は再現しない一過性の事象だった可能性が高い**(本セッションの再検証時点ではサーバー・エンドポイント・CORS・実際のfetch全てが正常)。ただし、スクリーンショットの発生時刻・その時のapp.py起動状態は依然として未確認であり、100%「一過性だった」と断定はできない。

---

## 判定(Phase C-1.3のA/B/C)

| 判定 | 結果 |
|---|---|
| A: server未起動 | **却下**。サーバーは起動中、port 5000 LISTENING確認済み |
| B: server起動 + endpoint失敗 | **却下**。endpoint POSTは200 OK、CORS(chatgpt.com/claude.ai双方)も正常 |
| C: server起動 + endpoint成功 + Extension側問題 | **該当するが限定的**。content_orchestra.js(chatgpt.com用)のExtension側は現在正常に成功している。問題があるのはcontent.js(claude.ai用)自体がページに全く注入されていないという、fetchより手前の段階の問題 |

## 8. 論点の更新(Phase Bへの影響)

当初のPhase C-1の目的は「ngrok URLをlocalhostに変えれば動くか」だったが、本書の発見により論点が変わる。

- content.jsが claude.ai 上で全く注入されていない以上、**ngrok URLをlocalhost:5000に書き換えるだけでは、claude.ai上での動作は直らない可能性が高い**(そもそもスクリプトが起動していないため、URLを変えても効果が測定できない)。
- content.js不実行の原因候補(未確認・要Phase C-1.1で依頼済みのchrome://extensions確認の延長):
  1. 現在インストールされている拡張の実体(バージョン・ソース)が、リポジトリ正本パス(`PlanningCaliber/workshop/Orchestra_Project/extension/`)と異なる可能性(古いWeb Store版が入っている等)。
  2. Developer mode読み込みではなくWeb Store版がインストールされている場合、Web Store版のcontent.jsが正本と異なるコード(古いバージョン・claude.ai向けmatchesが無い等)である可能性。
  3. (可能性は低い)claude.ai側の何らかの変更でcontent_scripts注入自体がブロックされている。

## 未決定事項(更新)

1. **(最優先・Phase C-1.1から継続)** chrome://extensionsでのOrchestra拡張の実体確認(バージョン・Developer mode有無・読み込み元パス)がまだ完了していない。本書7節の発見により、この確認の優先度がさらに上がった——ngrok/localhostの選択以前に、「claude.ai上でcontent.jsが動く状態にあるかどうか」自体を先に直さないと、Phase C(URLの書き換え)自体が無意味になる可能性がある。
2. ユーザー提供スクリーンショットの発生時刻・その時のapp.py状態は依然未確認。

---

以上、Phase C-1.3(通信基盤確認)完了。サーバー・エンドポイント・CORSの健全性は確認できたが、より優先度の高い課題(claude.ai上でのcontent.js不実行)が判明したため、次はPhase C-1.1で依頼済みのchrome://extensions確認(Orchestra拡張のバージョン・読み込み元)を先に完了させることを推奨する。

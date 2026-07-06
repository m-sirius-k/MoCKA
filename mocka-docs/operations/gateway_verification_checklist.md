# Gateway公開後 検証チェックリスト (TODO_266)

作成日: 2026-07-05
対象: gateway.nsjp.org / mcp.nsjp.org が Cloudflare Tunnel経由で外部公開された後の検証手順
前提: Cloudflareのゾーン(nsjp.org)がPending中の間は本チェックリストの一部(1の後半以降)は実行不可。まず下記の「実行可否の確認」を行うこと。

## 0. 実行可否の確認

- [ ] `nslookup -type=NS nsjp.org 8.8.8.8` で chris.ns.cloudflare.com / kinsley.ns.cloudflare.com が返ることを確認する
- [ ] Cloudflareダッシュボードの概要ページで、ドメインステータスが「保留中」ではなく通常表示になっていることを確認する(参考: developers.cloudflare.com/dns/zone-setups/reference/domain-status/#pending)
- 上記いずれかが未達成の場合、以降の項目は実行しても失敗するため、時間を置いてから再確認すること

## 1. DNS/ネットワーク疎通

- [ ] `Invoke-RestMethod https://gateway.nsjp.org/api/v1/health` が200 okで応答する(期待レスポンス: status=ok, service=MoCKA Gateway, port=5010)
- [ ] `Invoke-RestMethod https://mcp.nsjp.org/health` (または該当エンドポイント)が応答する

## 2. 認証

現状(2026-07-05時点)の実装(gateway/auth.py)を確認したところ、以下の既知の暫定状態がある。

- `MOCKA_API_KEYS` 環境変数が未設定のため、auth.pyのVALID_KEYSは空集合になる
- auth.py:47 `if VALID_KEYS and key not in VALID_KEYS` の条件により、VALID_KEYSが空集合の間は、X-MoCKA-Keyヘッダーに何らかの非空値さえ入れれば認証を通過してしまう(実質認証なし状態)
- adapter_gpt.py側もこの前提を自認しており、`MOCKA_API_KEY or "unset-local-dev-key"` というフォールバック値を使っている

チェック項目:

- [ ] X-MoCKA-Keyヘッダー無しで `/api/v1/context` 等の非公開エンドポイントにアクセスし、401が返ることを確認する(auth.py:46)
- [ ] 適当な非空値をX-MoCKA-Keyに入れてアクセスし、現状は通過してしまうことを確認する(既知の暫定状態の再確認であり、合格/不合格の判定対象ではない)
- [ ] 本番運用前にMOCKA_API_KEYSへ実キーを発行する場合は、正しいキーで200・誤ったキーで403になることを別途確認する

`/api/v1/event`(POST)はさらにHMAC検証(timestamp±5分、nonce重複防止、HMAC_SECRET設定時は署名照合)が入る(auth.py:50-90)。HMAC_SECRETも未設定の場合、署名照合自体はスキップされる点に留意する。

## 3. Gateway経由でMCPへの接続

gateway.py自体はMCP(port:5002、mocka_mcp_server.py)を直接呼び出す実装ではない。`POST /api/v1/event` は event_buffer 経由でGate(mocka_events.dbへの単一書込経路、PHI-OS Event Gate)に積む構成になっている(gateway.py:31, get_buffer().push())。よって「Gateway経由でMCPに接続できる」とは、実質的に「Gateway経由で書いたイベントが、MCP側の取得系ツール(mocka_get_todo/mocka_list_events等)から見えるか」という意味になる。

- [ ] `POST https://gateway.nsjp.org/api/v1/event` でテストイベントを投稿し、201が返ることを確認する
- [ ] 投稿したイベントが `mocka_list_events` または `mocka_read_event` 等、MCP経由の別ルートから参照できることを確認する(Gate経由で正しく反映されているかの検証)

## 4. GPT接続

adapter_gpt.pyのhandle_function_call()が実際にPOSTする先は `GATEWAY_BASE` 環境変数(デフォルト `http://localhost:5010`)であり、`gateway.nsjp.org` ではない。外部のGPT(ChatGPT等)からこのGatewayを使わせる場合、GPT側の実行環境で `MOCKA_GATEWAY_URL` を `https://gateway.nsjp.org` に向ける設定変更が別途必要になる点に注意する。

- [ ] `MOCKA_GATEWAY_URL=https://gateway.nsjp.org` を設定した状態で、adapter_gpt.handle_function_call()相当の呼び出しが成功することを確認する
- [ ] GPT側のFunction Calling定義(FUNCTION_SCHEMA)経由で実際に呼び出し、event投稿が反映されることを確認する
- [ ] ReadContext系の経路(存在する場合)も同様に確認する

## 5. Relay接続

現時点でコード上、Relay(Chrome拡張、Free/Pro/One)と `gateway.nsjp.org` が直接接続する経路は確認できていない。関連確認が必要になった場合は、まずMOCKA_OVERVIEW.jsonの`extension_canonical_paths.relay`(正本パス: `C:/Users/sirok/MoCKA/PlanningCaliber/workshop/Relay_Project/extension/`)を参照し、実際の接続先設定を確認してからスコープを定めること。

- [ ] Relay接続の要否・接続方式を別途確認してから、必要な検証項目を追記する(本チェックリストでは保留)

## 6. 記録

- [ ] 上記検証結果を `mocka_write_event` で記録する
- [ ] `mocka_get_incidents` でインシデントが発生していないか確認する
- [ ] 全項目達成後、TODO_266のstatusを完了へ更新し、完了裁定を記録する

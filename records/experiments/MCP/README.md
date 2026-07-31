# records/experiments/MCP/ — MCP OAuth 検証ログ

MoCKA MCP Server に対する OAuth 認可フローと MCP ハンドシェイクの動作検証記録。

- 配置日: 2026-07-31(commit `3baf5dbe3` で正式管理下へ移設)
- 検証実施日: **2026-07-22**
- 種別: **実験証跡**。運用ログではない

---

## 1. 実験目的

MCP クライアントが MoCKA MCP Server へ接続する際の、
**OAuth 認可からツール一覧取得までの一連の通信が成立するか**を確認すること。

具体的には次の3点を見ている。

1. OAuth 認可コードフロー(PKCE 付き)がサーバー側で正しく処理されるか
2. Dynamic Client Registration(`POST /register`)が機能するか
3. 認可後の MCP `initialize` ハンドシェイクでプロトコルバージョンが折り合うか

---

## 2. MCP OAuth 検証の概要

保存ログに現れる通信の流れは以下のとおり。

```
GET  /health                                     疎通確認
  |
GET  /oauth/authorize                            認可要求(PKCE: code_challenge / S256)
  |
POST /oauth/token                                認可コードをトークンへ交換
  |
POST /mcp                                        MCP initialize 要求
  |
GET  /.well-known/oauth-protected-resource/mcp   保護リソースメタデータ
GET  /.well-known/oauth-protected-resource
GET  /.well-known/oauth-authorization-server     認可サーバーメタデータ
  |
POST /register                                   Dynamic Client Registration
  |
POST /oauth/token -> POST /mcp                   登録済みクライアントで再試行
```

検証は2巡している。1巡目は固定のテスト用クライアント識別子、
2巡目は `/register` で動的に払い出された識別子を用いている。

### 2.1 確認できた事項

| 項目 | 結果 |
|------|------|
| 認可エンドポイントの応答 | 成立 |
| トークンエンドポイントの応答 | HTTP 200 |
| Dynamic Client Registration | HTTP 200。クライアント識別子が払い出される |
| `.well-known` メタデータ3種 | いずれも HTTP 200 |
| MCP `initialize` | HTTP 200。サーバーが応答を返す |
| プロトコルバージョン | クライアント要求 `2025-11-25` に対し、サーバー応答 `2024-11-05`。**バージョンが一致していない** |

プロトコルバージョンの不一致は、この検証で観測された事実として記録する。
本 README は原因や是非を判断しない。

---

## 3. 使用環境

| 項目 | 内容 |
|------|------|
| サーバー | MoCKA MCP Server v1.5.0 |
| サーバー識別 | `mocka-memory-caliber` v1.3.0(initialize 応答の `serverInfo`) |
| 公開ツール数 | 23 |
| 実行基盤 | Flask 開発サーバー(`mocka_mcp_server`) |
| 待受 | ローカルホスト上のポート 5002 |
| クライアント | Claude(`clientInfo.name` = Anthropic) |
| リダイレクト先 | `https://claude.ai/api/mcp/auth_callback` |
| 実施日時 | 2026-07-22 |

ログ冒頭に Flask の警告
(`This is a development server. Do not use it in a production deployment.`)が
そのまま残っている。**本検証は開発サーバー上で行われたもの**であり、
本番構成の検証ではない。

---

## 4. 保存ログの意味

`oauth_debug_request_log.txt`(204行)は、検証中のサーバー標準出力をそのまま保存したものである。

| 含まれるもの | 意味 |
|-------------|------|
| リクエストの到達順 | どのエンドポイントがどの順で呼ばれたかの通信フロー |
| HTTP ステータス | 各エンドポイントが成功したか |
| `initialize` の要求と応答の全文 | プロトコルバージョンと capabilities の折衝内容 |
| Dynamic Client Registration の応答構造 | 払い出されるフィールドの構成 |
| 分散トレース識別子 | `x-cloud-trace-context` / `traceparent`。クライアント側から付与された追跡用ID |

このログの価値は**通信フローの再現性**にある。
個々の値ではなく、"どの順で何が呼ばれ、何が返ったか"を残すことが目的である。

---

## 5. マスキング方針

Git 登録前に、認証に関わる値を置換した。**構造と通信フローは保持している**(204行のまま)。

### 5.1 マスクした対象

| 対象 | 件数 | 置換後 | 理由 |
|------|------|--------|------|
| 認可コード | 2 | `<MASKED_AUTH_CODE>` | 一時認証値 |
| PKCE code_verifier | 2 | `<MASKED_CODE_VERIFIER>` | 一時認証値 |
| PKCE code_challenge | 3 | `<MASKED_CODE_CHALLENGE>` | code_verifier の対 |
| OAuth state | 3 | `<MASKED_STATE>` | 一時値 |
| クライアントシークレット | 4 | `<MASKED_CLIENT_SECRET>` | 認証情報 |
| 私有 IP アドレス | 1 | `<MASKED_PRIVATE_IP>` | 内部ネットワーク情報 |

### 5.2 保持した対象

| 対象 | 理由 |
|------|------|
| `x-cloud-trace-context` / `traceparent` の値 | 分散トレース識別子であり資格情報ではない。通信フローの証跡として意味を持つ |
| `grant_types` 配列内の `refresh_token` 文字列 | 対応するグラント種別の宣言であり、実際のトークン値ではない |
| クライアント識別子(`client_id`) | 公開値。シークレットと対で使われるが、単体では認証に用いられない |
| エンドポイントのパス・リダイレクト先 URL | 通信フローそのもの |

### 5.3 検証手順

マスク適用後、以下を実施して機密値の残存がないことを確認した。

1. 9種のパターン(認可コード / code_verifier / code_challenge / state /
   client_secret / access_token / refresh_token / Bearer / 私有IP)で残存走査 -> 全て0件
2. 32文字以上の英数字列を全走査し、資格情報の可能性がある未分類の値が0件であることを確認
3. 上記の通過後にのみ、マスク前の原本を削除

**マスク前の原本は保存していない。** 一時認証値は保存不要という方針による。

---

## 6. 公開可能範囲

| 区分 | 内容 |
|------|------|
| 公開可 | 本ログ(マスク済み)および本 README |
| 公開不可 | マスクした値そのもの。再取得も行わない |

本ディレクトリは git 追跡対象であり、`origin/main` へ公開される。
したがって**ここに新たなログを追加する場合は、追加前に同等のマスク処理と残存検証を行うこと**。

### 6.1 追加時の注意

- 認証情報・トークン類を README に記載しない
- ログを追加する場合、5.3 と同等の検証を行ってから `git add` する
- 検証前のファイルをステージしない(マスク漏れが公開されると取り消せない)
- 本番環境のログを持ち込む場合は、開発サーバーのログとは扱いが異なるため
  公開可否を個別に判断する

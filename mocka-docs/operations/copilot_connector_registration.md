# Copilot Studio Custom Connector 登録手順書

作成日: 2026-06-18
対応TODO: TODO_267
前提条件: TODO_266 (Named Tunnel恒久化) 完了後に本登録を実施

---

## 概要

MoCKA Gateway API (`gateway/openapi.yaml`) を Copilot Studio の Custom Connector として登録する手順。
登録後は Copilot Studio から MoCKA の知識基盤へのアクセス・記録が可能になる。

- API仕様: OpenAPI 3.0.3
- 認証方式: API Key (`X-MoCKA-Key` ヘッダー)
- 本番URL: `https://mocka-api.nsjpkimura-mocka.workers.dev`
- Tunnel URL: TODO_266完了後に確定 (現時点では未定)

---

## 前提確認

1. Named Tunnel が恒久稼働中であること (`cloudflared tunnel list` で確認)
2. `gateway/openapi.yaml` が最新状態であること
3. MoCKA API Key が手元にあること

---

## 登録手順

### Step 1: openapi.yaml の URL を確認・更新

`gateway/openapi.yaml` の `servers[0].url` が実際のエンドポイントと一致しているか確認する。

```yaml
servers:
  - url: https://mocka-api.nsjpkimura-mocka.workers.dev
    description: Production (Cloudflare Workers)
```

Named Tunnel を使う場合はここを Tunnel の公開URLに変更する。

### Step 2: Copilot Studio へのアクセス

1. [Microsoft Copilot Studio](https://copilotstudio.microsoft.com) にサインイン
2. 左ペイン「設定」→「Custom connectors」を開く

### Step 3: コネクタ新規作成

1. 「+ New custom connector」をクリック
2. 「Import an OpenAPI file」を選択
3. `gateway/openapi.yaml` をアップロード
4. コネクタ名: `MoCKA Gateway` (任意)
5. 「Continue」をクリック

### Step 4: 認証設定

1. 「Security」タブを開く
2. Authentication type: `API Key`
3. Parameter label: `X-MoCKA-Key`
4. Parameter name: `X-MoCKA-Key`
5. Parameter location: `Header`
6. 「Create connector」をクリック

### Step 5: 接続テスト

1. 「Test」タブを開く
2. 「+ New connection」をクリック
3. API Key を入力して接続作成
4. `GET /context` でレスポンスが返ることを確認

### Step 6: Copilot への組み込み

1. 対象の Copilot を開く
2. 「Topics」→ 任意のトピックを編集
3. 「+ Add action」→ 作成したコネクタを選択
4. 必要なアクション (`get_context`, `write_event` 等) を設定

---

## エンドポイント一覧 (openapi.yaml 準拠)

| メソッド | パス | 説明 |
|---------|------|------|
| GET | /context | MoCKA コンテキスト取得 |
| GET | /public/todo | TODOリスト取得 |
| POST | /agent/mocka_write_event | イベント記録 |
| GET | /public/events | 最新イベント取得 |
| GET | /health | ヘルスチェック |

---

## トラブルシューティング

- 401 Unauthorized: API Key が正しくヘッダーに設定されているか確認
- 503 Service Unavailable: MoCKA サーバー (localhost:5000) またはTunnelが停止していないか確認
- openapi.yaml の validation error: `servers[0].url` のプロトコルが `https` であることを確認

---

## 注意事項

- 本登録は TODO_266 (Named Tunnel 恒久化) 完了後に実施すること
- Tunnel URL 変更時は openapi.yaml の `servers[0].url` も同期更新が必要
- API Key は環境変数またはキーボルトで管理し、コードに直接記載しないこと

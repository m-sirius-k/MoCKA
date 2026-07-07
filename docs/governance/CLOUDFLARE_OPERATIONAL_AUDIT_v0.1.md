# Cloudflare Operational Audit v0.1(SSOT監査 Phase D-1)

作成日: 2026-07-07
対象: 運用・デプロイ系(Operational SSOT)。DNS・Named Tunnel・Cloudflare Workers Routingの実運用状態を確認する。
制約: 設定変更・削除は一切行っていない(観測のみ)。

---

## 最重要の確定事実: mcp.nsjp.org の実ルーティング(Phase Bの未確定事項に決着)

`C:\Users\sirok\.cloudflared\config.yml`(Named Tunnel ingress設定)を直接確認した結果:

```yaml
tunnel: efb26375-013a-48d3-a31b-a2f70e10e5a6
credentials-file: C:\Users\sirok\.cloudflared\efb26375-013a-48d3-a31b-a2f70e10e5a6.json

ingress:
  - hostname: gateway.nsjp.org
    service: http://localhost:5010
  - hostname: mcp.nsjp.org
    service: http://localhost:5002
  - service: http_status:404
```

**`mcp.nsjp.org` は Cloudflare Worker「mocka-mcp」ではなく、Named Tunnel経由で直接 `localhost:5002`(`mocka_mcp_server.py`本体)にルーティングされている。**

さらに、この設定ファイル自身のコメントに重大なインシデント履歴が残っていた:

> Previous version pointed at a non-existent tunnel name "mocka-mcp"; credentials JSON did not exist locally and was regenerated via: `cloudflared tunnel token --cred-file <path> efb26375-013a-48d3-a31b-a2f70e10e5a6`
> (Updated: 2026-07-05 — reconciled with actual Cloudflare-side tunnel "mocka-gateway")

つまり過去に、Tunnel名として誤って「mocka-mcp」という文字列が使われていた時期があり、これは同名のCloudflare Worker「mocka-mcp」と紛らわしく、実際に2026-07-05に一度修正された経緯がある。**「mocka-mcp」という名前が、Worker(GitHub Snapshotミラー)とTunnel(旧誤設定)の2つの異なる対象を指していたことがある、という名前衝突の実例。**

---

## DNS実解決の確認

| ホスト名 | 解決先IP | 備考 |
|---|---|---|
| `gateway.nsjp.org` | 104.21.89.41 / 172.67.156.87 | Cloudflareプロキシ経由(Anycast) |
| `mcp.nsjp.org` | 104.21.89.41 / 172.67.156.87 | `gateway.nsjp.org`と**完全に同一IP** — 同一Named Tunnelインフラを裏付ける |
| `mocka-api.nsjpkimura-mocka.workers.dev` | 104.21.42.219 / 172.67.210.108 | 上記2つとは別のIP系統(Workers標準ルーティング) |

---

## Cloudflare Workers Routing(3系統、Phase B-2の追認)

| Worker | wrangler.toml内route設定 | 実際の到達経路 |
|---|---|---|
| `mocka-api`(gateway/cloudflare/) | 無し(コメントのみ、有効化されていない) | `mocka-api.nsjpkimura-mocka.workers.dev`(workers.devサブドメインのみ)経由でのみ到達可能。カスタムドメイン未設定 |
| `mocka-mcp`(PlanningCaliber/workshop/mocka-cloudflare/) | 無し(コメントアウト、`mocka.nsjp.org`用のroute設定が用意されているが未有効化) | 同上、workers.devサブドメインのみ |
| `relay-license` | 未確認(対象外) | — |

**⚠️新たな問題候補**: `mocka-api` Worker(TODO_418で本日修正済み)について、コードベース内を検索した結果、`mocka-api.nsjpkimura-mocka.workers.dev`というURLを実際に呼び出している箇所が見つからなかった(`health_check.py`が参照する`nsjpkimura-mocka.workers.dev`系URLは`orchestra-license`という別サブドメイン・別Workerだった)。TODO_417でOpenAPI仕様(`gateway/openapi.yaml`)の`servers.url`が既に`gateway.nsjp.org`直接参照へ切り替わっているため、**`mocka-api` Workerは現在誰からも呼ばれていない可能性がある**(二重ホップの経路が使われなくなった)。ただし、外部クライアント(登録済みのCopilot Studio等、将来のChatGPT Custom GPT Action等)がまだ古いworkers.dev URLを参照している可能性は本監査の範囲外(コードベース検索のみ)であり否定できない。

---

## Phase D-1 判定表

| エンドポイント | DNS正本 | 入口 | Backend | 責務 | コード設定との一致 |
|---|---|---|---|---|---|
| `gateway.nsjp.org` | Cloudflare DNS(Named Tunnel) | Tunnel | `localhost:5010`(gateway.py) | Live | **正常** |
| `mcp.nsjp.org` | Cloudflare DNS(Named Tunnel、gatewayと同一) | Tunnel | `localhost:5002`(mocka_mcp_server.py) | Live | **正常**(Phase Bの「Worker経由では」という推測は誤りと判明、訂正) |
| `mocka-api`(Worker) | workers.devのみ | Worker | `gateway.nsjp.org`(二重ホップ) | Live(冗長化疑い) | **SSOT不明**(実利用者が見つからず、要確認) |
| `mocka-mcp`(Worker) | workers.devのみ、カスタムドメイン未有効化 | Worker | GitHub Content API | Snapshot | **正常**(Phase B-2で確認済み、mcp.nsjp.orgとは無関係) |
| `relay-license`(Worker) | 未確認 | — | KV | License | 対象外 |

---

## 結論

Phase Bで未確定だった`mcp.nsjp.org`の実ルーティングは、Cloudflare Dashboardへのログインを待たず`config.yml`(ローカルファイル)の直接確認だけで完全に解決した。想定していた「Workerに向いているのでは」という仮説は誤りで、実際はTunnel経由でmocka_mcp_server.pyへ直結していた。

新たに`mocka-api` Workerの実利用者不在という「SSOT不明」項目が浮上した。これはTODO_422(ngrok URL統合)とは別の新規Decision対象候補である。

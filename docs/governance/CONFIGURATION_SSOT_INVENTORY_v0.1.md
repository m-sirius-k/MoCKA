# Configuration SSOT Inventory v0.1

作成日: 2026-07-07
対応TODO: TODO_421(Configuration SSOT監査)Phase A
根拠: [[project_mocka_ssot_governance_roadmap]]、TODO_419/420で確立した監査手法の適用

本書はリポジトリ内の設定ファイルを棚卸しし、READ/WRITEの実態を整理する。コード変更・設定変更は一切行っていない。

---

## 1. 環境変数(.env系)

| ファイル | 内容(キー名のみ) | 用途 |
|---|---|---|
| `.env` | `MOCKA_ENDPOINT`・`MOCKA_API_KEYS`・`MOCKA_HMAC_SECRET`・`PHI_OS_HMAC_KEY_ID`・`PHI_OS_HMAC_SECRET` | 実運用の秘密情報。`app.py`(TODO_416)・`gateway/gateway.py`が`load_dotenv()`で読込 |
| `.env.example` | `MOCKA_ENDPOINT`のみ(1項目) | 新規セットアップ用テンプレート |
| `PlanningCaliber/workshop/vasAI_Project/.env.example` | 未確認(別プロジェクト) | vasAI_Project(現在封印済み、project memory参照)専用 |

**⚠️問題候補1**: `.env.example`が実際の`.env`(5項目)のうち1項目しか documentation していない。`MOCKA_API_KEYS`・`MOCKA_HMAC_SECRET`・`PHI_OS_HMAC_KEY_ID`・`PHI_OS_HMAC_SECRET`はテンプレートに存在せず、新規セットアップ時に見落とされるリスクがある。

---

## 2. Cloudflare Workers設定(wrangler.toml、3系統確認)

| ファイル | Worker名 | 用途(コメントから判読) |
|---|---|---|
| `gateway/cloudflare/wrangler.toml` | `mocka-api` | TODO_418で本日修正済み。`MOCKA_BACKEND_URL`を`gateway.nsjp.org`へ変更(Named Tunnel経由) |
| `PlanningCaliber/workshop/mocka-cloudflare/wrangler.toml` | `mocka-mcp` | `mocka-mcp.nsjpkimura.workers.dev`(コメント)。カスタムドメイン`mocka.nsjp.org`をコメントアウトで用意。GITHUB_TOKENをwrangler secretで別管理する旨の注記あり |
| `PlanningCaliber/workshop/Relay_Project/backend/wrangler.toml` | `relay-license` | Relay関連のライセンス管理用、KV namespace(`RELAY_KV`)を使用。目的が明確に異なるため今回の乖離調査の対象外候補 |

**⚠️問題候補2**: `mocka-api`(gateway/cloudflare/)と`mocka-mcp`(PlanningCaliber/workshop/mocka-cloudflare/)という、名前も配置場所も異なる2つのWorkerが存在する。account_idは同一(`3181bc198361c0532500c369d3ebb55e`)。両者が本当に別役割(api用/mcp用)として意図された設計か、あるいはTODO_419のOrchestra乖離と同型の「重複」なのかは、Phase B(Call Graph)での確認が必要。project memoryには「gateway.nsjp.org/mcp.nsjp.org外部公開」(TODO_266)という記述があり、mcp.nsjp.org用が`mocka-mcp`worker、gateway.nsjp.org用が`mocka-api`workerという役割分担の可能性が高いが、未確認。

---

## 3. MCP接続設定

| ファイル | 内容 | 用途 |
|---|---|---|
| `.claude/mocka_config.json` | `mcp_endpoint: https://arnulfo-pseudopopular-unvirulently.ngrok-free.dev` | このリポジトリに紐づくClaude Code設定。MCPサーバーへの接続先 |
| `.claude/settings.local.json` | permissions(`mcp__claude_ai_MoCKA_Memory_Caliber2_01__*`)・PostToolUseフック(`mocka_auto_record.py`) | ツール許可設定。MCPサーバー名が`mocka_config.json`のngrok URLとは別の識別子(`claude_ai_MoCKA_Memory_Caliber2_01`)で登録されている |

**⚠️問題候補3**: `.claude/mocka_config.json`のngrok URL(`arnulfo-pseudopopular-unvirulently.ngrok-free.dev`)は無料枠のngrokトンネルであり、再起動のたびにURLが変わる性質を持つ。実際に今回のセッションで使用しているMCP接続(`claude_ai_MoCKA_Memory_Caliber2_01`という名称)と、このファイルのURLが同一経路を指しているかは未検証。TODO_266の「Cloudflare Tunnel恒久化」により、この設定自体が既に旧式(ngrok前提)のまま取り残されている可能性がある。

---

## 4. Gateway API仕様

| ファイル | 内容 | 状態 |
|---|---|---|
| `gateway/openapi.yaml` | `servers[0].url: https://gateway.nsjp.org` | TODO_417で本日更新済み・整合確認済み |

---

## 5. その他の設定ファイル(概要のみ、Phase B以降で深掘り)

| ファイル | 種別 |
|---|---|
| `runtime/config/config.yaml` | Runtime B(Go)関連設定と推測。中身未確認 |
| `docker-compose.yml` / `docker-compose.reproduce.yml` / `docker-compose.reproduce.l5.yml` | ルート直下、論文再現実験用と推測 |
| `PlanningCaliber/workshop/phi-os/docker-compose.yml` | phi-os関連 |
| `PlanningCaliber/workshop/Relay_Project/docker-compose.yml` | Relay関連 |
| `PlanningCaliber/workshop/vasAI_Project/docker-compose.yml` | vasAI関連(封印済みプロジェクト、project memory参照) |
| `.github/workflows/*.yml`(6件) | GitHub Actions CI設定。設定SSOTというより CI パイプライン定義であり、今回のConfiguration SSOT監査の主対象からは除外候補 |

---

## Phase Aのまとめ・次のアクション

今回の棚卸しで3件の問題候補が浮上した。いずれもPhase B(Call Graph)での裏付けが必要:

1. `.env.example`が実際の`.env`の1/5項目しか記載していない(テンプレート陳腐化)
2. `mocka-api`と`mocka-mcp`という2つのCloudflare Workerの役割分担が未確認(TODO_419型の乖離の可能性)
3. `.claude/mocka_config.json`のngrok URLが、TODO_266のCloudflare Tunnel恒久化以前の旧式設定のまま残っている可能性

次のアクション: Phase B(Call Graph)で、上記3件について「誰が実際にどの設定を読んでいるか」を確認する。

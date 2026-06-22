# Adapter Contract v1 (Phase5 Step4-B)

Status: DRAFT（Step4-Cの前提条件として固定する契約文書）
Date: 2026-06-22

本文書はAPI仕様書ではない。GPT/MCPがMoCKAへ接続する際の契約境界
（何を送ってよいか・何を返してよいか）を実装前に固定する文書である。
本文書の段階ではコード・SDK・Client/Server実装は一切作成しない。

前提: `docs/governance/adapter_governance_v1.md`(Step4-A)で固定された
制度設計(GPT = Advisor、MCP = Transport)をそのまま契約として落とし込む。
権限の値自体(Authority Owner=User等)を変更する場合はStep4-A文書の改訂が必要。

契約は4層に分離する。

```
Authority Contract
Message Contract
Capability Contract
Audit Contract
```

## 1. Authority Contract

Step4-Aの制度をそのまま固定する。

| 主体 | 役割 |
|---|---|
| User | Owner |
| MoCKA | Executor |
| GPT | Advisor |
| MCP | Transport |

### GPT禁止事項（絶対）

- GPT cannot execute
- GPT cannot modify memory
- GPT cannot modify replay
- GPT cannot modify snapshot
- GPT cannot modify event

GPTが行えるのは「提案(proposal)」のみであり、上記5項目はいかなる
Adapter実装(Step4-C)においても迂回されてはならない。

## 2. Message Contract

GPTへ渡せる情報・GPTから受け取れる情報を定義する。

### 許可（GPTへ渡してよい情報）

- `semantic_query`
- `capability_catalog`
- `audit_summary`
- `time_query_result`

### 禁止（GPTへ渡してはならない情報）

- raw database handle
- repository instance
- filesystem write access
- execution token

### メッセージ形式（例）

```json
{
  "type": "semantic_query",
  "payload": {}
}
```

`type`は上記許可リストのいずれかに限定される。`payload`の詳細形式は
`docs/contracts/adapter_message_schema_v1.md`で定義する。

## 3. Capability Contract

GPTが「提案として参照できる」能力を列挙する。これは
`docs/contracts/capability_registry_v1.md`(Phase5 Step2.5)で定義された
既存5能力と完全に一致し、新たな能力を追加しない。

```
event_count
last_snapshot
current_state
replay_state
audit_status
```

### 重要な区別: proposal と execution

GPTはこれらの能力名を「提案(proposal)」できるだけである。
GPTが能力名を出力した時点でその能力が実行(execution)されるわけではない。
実行は常にMoCKA(RelayKernel経由)が行い、GPTの提案を採用するかどうかの
判断もMoCKA/Userに属する(`docs/governance/adapter_governance_v1.md`の
Execution Rule参照)。

## 4. Audit Contract

GPT/MCP経由の全ての提案を監査対象とする。最低限、以下を記録する。

| フィールド | 内容 |
|---|---|
| timestamp | 提案・応答が発生した時刻 |
| actor | GPT / MCP / MoCKA のいずれか |
| request | Userまたは上位層からの要求内容 |
| proposal | GPTが提案した内容(能力名・テキスト等) |
| result | MoCKAが実行した結果、または不採用の場合はその旨 |

この記録方式は、`relay/replay_audit.py`のReplay Audit Layerが採用する
「記録のみ・自動修復なし」の原則をGPT/MCPとのやり取り全体に拡張するもの
であり、Step4-A Audit Ruleと一致する。

## Step4-Bで明示的に禁止する実装

以下はAdapter Contract Design(本文書)の段階では一切実装しない。

- GPT SDK
- OpenAI API
- MCP Client
- MCP Server
- HTTP Connector
- Tool Execution
- Agent Runtime

## 完了条件

- [x] Authority Contract定義
- [x] Message Contract定義（許可/禁止リスト、メッセージ形式例）
- [x] Capability Contract定義（既存5能力のみ、proposal/execution区別の明記）
- [x] Audit Contract定義
- [x] `docs/contracts/adapter_message_schema_v1.md`作成（メッセージスキーマ詳細）
- [x] 上記禁止実装(GPT SDK等)を作成していない

## 次のステップ

Step4-C「Adapter Implementation」は、本文書とAdapter Message Schema v1
が固定した契約のみを実装範囲とする。契約を変更する実装(例: Capability
Contract外の能力を追加する、Message Contractの禁止リストに該当する
情報を渡す)は許可されない。Step4-Cの着手もユーザーの明示的な判断を
得てから行う。

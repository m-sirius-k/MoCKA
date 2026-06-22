# Adapter Message Schema v1 (Phase5 Step4-B)

Status: DRAFT
Date: 2026-06-22

本文書は`docs/contracts/adapter_contract_v1.md`のMessage Contractを
具体的なスキーマとして定義する。これはスキーマ定義であり、実装コード
ではない。GPT SDK/MCP Client/Server等の実装はStep4-Cで扱う。

## AdvisorRequest

MoCKAからGPT(Advisor)へ送られる要求。

```json
{
  "type": "AdvisorRequest",
  "context": {
    "capability_catalog": [
      {"name": "event_count", "description": "..."},
      {"name": "last_snapshot", "description": "..."}
    ],
    "user_query": "string (自然言語、Userの問い合わせそのもの)"
  }
}
```

- `context.capability_catalog`は`GET /time/capabilities`の返却値そのもの。
- `user_query`は生のテキストであり、execution tokenやrepository
  instanceは含まれない(Message Contractの禁止リストに従う)。

## AdvisorResponse

GPT(Advisor)からMoCKAへ返される応答。

```json
{
  "type": "AdvisorResponse",
  "proposal": {
    "capability_name": "string (Capability Contractの5能力のいずれか、またはnull)",
    "rationale": "string (提案理由、人間可読)"
  },
  "confidence": "number (0.0-1.0、省略可)"
}
```

- `proposal.capability_name`がnullの場合、GPTは「該当する能力がない」と
  提案したことを意味する(Step4-A: Semantic Query Layerの`UNRESOLVED_QUERY`
  と同じ思想)。
- `AdvisorResponse`はあくまで提案(proposal)であり、これを受け取った
  MoCKAが実行するかどうかを判断する。AdvisorResponse自体に実行権はない。

## TransportEnvelope

MCP(Transport)がAdvisorRequest/AdvisorResponseを運ぶ際の外側の包み。
MCPはこのEnvelopeの中身を解釈・実行する権限を持たない(Step4-A:
MCP = Option 1 Transportの原則)。

```json
{
  "type": "TransportEnvelope",
  "channel": "string (識別子、MCP実装依存だが本文書では規定しない)",
  "timestamp": "string (ISO8601)",
  "body": "AdvisorRequest | AdvisorResponse"
}
```

- `body`には`AdvisorRequest`または`AdvisorResponse`のいずれかのみが
  入る。`body`の中身を変更・解釈する処理をMCP側に持たせてはならない。

## Audit Record（Audit Contractとの対応）

`docs/contracts/adapter_contract_v1.md`のAudit Contractで定義した
フィールドと、本スキーマの対応関係。

| Audit Contractフィールド | 本スキーマでの対応 |
|---|---|
| timestamp | `TransportEnvelope.timestamp` |
| actor | `TransportEnvelope.body.type`から判定(AdvisorRequest→MoCKA発, AdvisorResponse→GPT発) |
| request | `AdvisorRequest.context.user_query` |
| proposal | `AdvisorResponse.proposal` |
| result | （Step4-C以降、MoCKAが採用/不採用を記録する欄。本文書では未定義） |

## 禁止事項（Message Contractの再確認）

以下のフィールドはいずれのメッセージにも含めてはならない。

- raw database handle
- repository instance
- filesystem write access
- execution token

## 完了条件

- [x] AdvisorRequestスキーマ定義
- [x] AdvisorResponseスキーマ定義
- [x] TransportEnvelopeスキーマ定義
- [x] Audit Contractとの対応関係を明記
- [x] 実装コード(GPT SDK/MCP Client/Server等)は作成していない

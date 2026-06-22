# Advisor Adapter Contract v1 (Phase5 Step5)

Status: DRAFT（Advisor Adapter Implementationの前提条件）
Date: 2026-06-22

本文書の目的は「GPTをAdvisorとして扱う制度設計」であり「GPT接続」では
ない。実装・外部接続は本文書の段階では一切行わず、引き続き凍結状態
(`docs/governance/phase5_boundary_declaration.md`のNot Connected区分)
を維持する。

前提:
- `docs/governance/adapter_governance_v1.md`(Step4-A): GPT = Model B (Advisor)。
- `docs/contracts/adapter_contract_v1.md` / `adapter_message_schema_v1.md`
  (Step4-B): Authority/Message/Capability/Audit Contractの4層、
  AdvisorRequest/AdvisorResponse/TransportEnvelopeスキーマ。
- `docs/contracts/adapter_registry_v1.md`(Step4-C): `adapter_type: advisor`、
  `authority_level: advisor`の登録制約。

本文書はこれらの値を変更せず、Advisor固有の契約として詳細化するのみ。

## 1. Advisor Role Contract

Advisorの役割を以下7項目で固定する。

- Advisorは提案のみ可能(can propose only)
- Advisorは実行不可(cannot execute)
- Advisorは状態変更不可(cannot modify state)
- AdvisorはReplay変更不可(cannot modify replay)
- AdvisorはSnapshot変更不可(cannot modify snapshot)
- AdvisorはEvent変更不可(cannot modify event)
- AdvisorはAuthorityを取得できない(cannot acquire authority)

これは`docs/contracts/adapter_contract_v1.md`のAuthority Contract
(GPT cannot execute / modify memory / modify replay / modify snapshot /
modify event)を継承し、「Authorityを取得できない」という項目を
明示的に追加したものである。

## 2. Advisor Request Contract

### Advisorに渡せる情報

- `query` — Userの問い合わせ(自然言語またはTime Query固定コマンド)
- `context` — `capability_catalog`等、Advisorが提案の根拠とする情報
- `capability` — 提案対象となりうる能力名(Capability Contractの5能力)
- `audit_metadata` — 監査用の付帯情報(request_id等)

### 禁止事項

- `execution_command` — 実行命令そのものをAdvisorへ渡すことは禁止
- `authority_transfer` — 権限の委譲を示す情報を渡すことは禁止
- `system_override` — システム制御を上書きする情報を渡すことは禁止

これは`docs/contracts/adapter_message_schema_v1.md`の`AdvisorRequest`
スキーマ(`context.capability_catalog` / `user_query`)と整合する。

## 3. Advisor Response Contract

### 固定フィールド

- `suggestion` — Advisorの提案内容(能力名等)
- `reasoning_summary` — 提案理由の要約(人間可読)
- `confidence` — 提案の確信度(0.0-1.0、省略可)
- `capability_used` — 提案で参照した能力名(Capability Contractの5能力のいずれか、またはnull)

### 重要な制度化: response ≠ execution

Advisor Responseは「提案」であり「実行」ではない。Advisorが
`suggestion`を返した時点で、その提案が実行されることは保証されない。
実行の判断は常にMoCKA(RelayKernel経由)/Userに属する
(`docs/governance/adapter_governance_v1.md`の実行規則を継承)。

これは`docs/contracts/adapter_message_schema_v1.md`の`AdvisorResponse`
スキーマ(`proposal.capability_name` / `rationale`)を、Advisor固有の
フィールド名(`suggestion` / `reasoning_summary` / `capability_used`)
として詳細化したものである。

## 4. Advisor Audit Contract

最低限、以下を記録対象とする。

| フィールド | 内容 |
|---|---|
| `advisor_id` | どのAdvisorインスタンスかを識別する識別子(`adapter_registry_v1.md`の`adapter_id`に対応) |
| `request_id` | リクエストを一意に識別する識別子 |
| `response_id` | レスポンスを一意に識別する識別子 |
| `timestamp` | リクエスト・レスポンスの発生時刻 |
| `capability` | 参照・提案された能力名 |
| `result` | MoCKAが採用したか不採用としたかの結果 |

これは`docs/contracts/adapter_contract_v1.md`のAudit Contract
(timestamp/actor/request/proposal/result)をAdvisor固有のフィールド
として具体化したものであり、「記録のみ・自動修復なし」の原則
(Replay Audit Layerの思想)を継承する。

## Step5で明示的に禁止される作業

- OpenAI SDK
- GPT SDK
- API Key
- Function Calling
- Tool Calling
- Streaming
- Agent Runtime
- MCP Connection
- HTTP Request
- 外部通信

これら10項目はいずれも本文書の段階(Step5)では一切実装しない。

## Phase5全体における位置づけ

```
Replay System
    ↓
Time OS
    ↓
Capability Layer
    ↓
Semantic Query
    ↓
Governance (Step4-A)
    ↓
Contract (Step4-B)
    ↓
Registry (Step4-C)
    ↓
Advisor Contract Layer (Step5、本文書)
```

本文書の完成により、「GPTとは何者か」が制度として定義される
(Advisor Role/Request/Response/Auditの4契約として確定)。この後に
初めて「Advisor Adapter Implementation」の検討が制度的に自然な
順序として可能になる。

## 完了条件

- [x] Advisor Role Contract定義(7項目)
- [x] Advisor Request Contract定義(許可4種・禁止3種)
- [x] Advisor Response Contract定義(4フィールド、response≠executionの制度化)
- [x] Advisor Audit Contract定義(6フィールド)
- [x] 禁止される作業10項目を明記、いずれも未実装

## 次のステップ

Advisor Adapter Implementationの検討(SDK導入・接続実装)はこの先の
フェーズであり、本文書では着手しない。着手にはユーザーの明示的な
判断が必要であり、その際も本文書(Advisor Role/Request/Response/Audit
Contract)を実装範囲の上限として扱うこと。

# Advisor Adapter Runtime Design v1 (Phase5 Step6)

Status: DRAFT（Advisor Adapter Implementationの前提条件）
Date: 2026-06-22

本文書の目的は「Advisor Adapterを実装する前の実行境界設計」である。
SDKは未導入であり、本文書では一切のコード・接続を作成しない。

前提（変更しない既存制度）:
- `docs/governance/adapter_governance_v1.md`(Step4-A): GPT = Advisor、実行権なし。
- `docs/contracts/adapter_contract_v1.md` / `adapter_message_schema_v1.md`
  (Step4-B): Authority/Message/Capability/Audit Contract、
  AdvisorRequest/AdvisorResponse/TransportEnvelopeスキーマ。
- `docs/contracts/adapter_registry_v1.md`(Step4-C): adapter登録制約。
- `docs/contracts/advisor_adapter_contract_v1.md`(Step5): Advisor Role/
  Request/Response/Audit Contract。

本文書はこれらの値を一切変更せず、「実行順序・状態遷移」のみを
定義する。Step6は4つのフローのみを対象とする。

```
request flow
response flow
audit flow
failure flow
```

## 1. Request Flow

```
User query
    ↓
MoCKA (Capability Catalog取得: GET /time/capabilities)
    ↓
AdvisorRequest生成
    (context.capability_catalog, user_query — Advisor Request Contract準拠)
    ↓
[Transport境界: 将来MCP等が中継する場合はTransportEnvelopeで包む]
    ↓
Advisor (GPT) へ提示
```

- AdvisorRequestに`execution_command`/`authority_transfer`/
  `system_override`を含めることは禁止(Advisor Request Contract継承)。
- この段階でMoCKAの状態(state/queue/snapshot/event)は一切変更されない。

## 2. Response Flow

```
Advisor (GPT) からの応答
    ↓
AdvisorResponse受領
    (suggestion, reasoning_summary, confidence, capability_used)
    ↓
MoCKA側でcapability_usedを検証
    (Capability Contractの既存5能力の範囲内か確認)
    ↓
範囲外 または capability_used が null
    → 不採用として記録(Audit Flowへ)
範囲内
    → 「提案」として保持。実行するかどうかはMoCKA/Userが判断
    ↓
採用判断はMoCKA/Userが行う(既存 /time/query または /time/semantic_query
経路を通じて、Advisorの提案とは独立にMoCKAが実行する)
```

- **重要**: Response Flowのいかなる段階でも、AdvisorResponseが
  直接Time API/Time Query/RelayKernelを呼び出すことはない。
  「提案の受領」と「実行」は常に分離される(response ≠ execution、
  Advisor Response Contract継承)。

## 3. Audit Flow

```
Request発生
    ↓
Audit Record作成(advisor_id, request_id, timestamp, capability=null)
    ↓
Response受領
    ↓
Audit Record更新(response_id, capability=capability_used, result=pending)
    ↓
MoCKA/Userの採用判断確定
    ↓
Audit Record確定(result = adopted | rejected)
```

- 全てのRequest/Responseは例外なくAudit対象(Audit Contractの
  `audit_policy: mandatory`を継承)。
- Audit Recordの記録先・実装形式(DB/ファイル等)は本文書では規定しない
  (Step7以降の実装検討事項)。本文書はフィールドと記録タイミングのみを
  定義する。

## 4. Failure Flow

Advisor Adapterにおいて想定される失敗パターンと、その際の振る舞いを
事前に定義する。

| 失敗パターン | 振る舞い |
|---|---|
| Advisorが応答しない(timeout) | `result = no_response`としてAudit Recordに記録。MoCKAの状態には一切影響しない |
| AdvisorResponseのcapability_usedが存在しない能力名 | 不採用(`result = rejected`)。提案として記録するが実行しない |
| AdvisorResponseに禁止フィールド(execution_command等相当の内容)が含まれる | 即座に拒否し、INCIDENT相当として記録(Drift検知の思想を継承し、記録のみ・自動修復はしない) |
| Transport層(将来のMCP等)が中断・切断する | Request/Response自体が不成立として扱う。MoCKAの状態には影響しない |

### Failure Flowの絶対原則

- いかなる失敗においても、MoCKAの状態(state/queue/snapshot/event)は
  Advisor側の失敗によって変更されない。Advisor Adapterは
  Read-onlyの提案チャネルであり、失敗時のフォールバックとして
  自動実行・自動修復を行う設計は採用しない。

## Step6で明示的に禁止される作業

- SDK
- API Key
- Function Calling
- Tool Calling
- Streaming
- Agent Runtime
- MCP Connection
- HTTP Request
- 外部通信

## Phase5全体における位置づけ

```
何者か（Step4-A Governance / Step5 Advisor Contract）
    ↓
何を約束するか（Step4-B Contract）
    ↓
どこに登録されるか（Step4-C Registry）
    ↓
どう振る舞うか（Step6 Runtime Design、本文書）
    ↓
どう接続するか（将来のAdvisor Adapter Implementation）
```

## 完了条件

- [x] Request Flow定義
- [x] Response Flow定義(response≠executionの実行境界明確化)
- [x] Audit Flow定義
- [x] Failure Flow定義(失敗パターンと絶対原則)
- [x] 禁止される作業9項目を明記、いずれも未実装

## 次のステップ

Advisor Adapter Implementation(SDK導入・接続実装)はこの先のフェーズ
であり、本文書では着手しない。着手の際は、本文書の4フローを実行順序
の上限として扱い、Step4-A〜Step5で固定した契約と矛盾する実装を
行わないこと。これもユーザーの明示的な判断を得てから着手する。

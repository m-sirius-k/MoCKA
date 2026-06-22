# Adapter Registry v1 (Phase5 Step4-C)

Status: DRAFT（Step5 Advisor Adapter Design・将来のAdapter実装の前提条件）
Date: 2026-06-22

本文書はSDK・API・Client/Server・Runtime・External Connectionの実装
ではない。MoCKAに接続されうるAdapter(GPT/MCP/HTTP/Tool/Local Runtime等)
を「識別・登録するための制度」のみを固定する。

前提:
- `docs/governance/adapter_governance_v1.md`(Step4-A): Authority Owner=User、
  Execution Authority=MoCKA、GPT=Advisor、MCP=Transportという権限構造。
- `docs/contracts/adapter_contract_v1.md` / `adapter_message_schema_v1.md`
  (Step4-B): Authority/Message/Capability/Audit Contractの4層契約。

Registryはこれらを変更せず、それぞれのAdapterが「どの権限レベルで」
「どの能力を」「どの監査方針のもとで」登録されているかを管理する
入れ物(レジストリ)としてのみ機能する。

## なぜRegistryが先に必要か

Adapterを識別・登録する制度がない状態でGPT(Advisor)接続の具体設計
(Step5)に進むと、将来MCP/HTTP/Tool/Local Runtimeなど別種のAdapterが
増えた際に「誰がどの権限で何を呼べるのか」の管理境界が曖昧になる。
Registryを先に固定することで、Adapterの種類が増えても同じ枠組みで
管理できる。

## Registry フィールド定義

| フィールド | 説明 | 値の例・制約 |
|---|---|---|
| `adapter_id` | Adapterを一意に識別する文字列 | 例: `gpt-advisor-001`。重複不可 |
| `adapter_type` | Adapterの種別 | `advisor` \| `transport` \| `tool` \| `runtime`（Step4-Aの4モデルA/B/C/Dまたはそれに準じる分類に対応） |
| `adapter_version` | Adapter契約のバージョン | 例: `v1`。`docs/contracts/adapter_contract_v1.md`のバージョンと対応させる |
| `capability_set` | このAdapterが提案可能な能力の集合 | `docs/contracts/capability_registry_v1.md`の既存5能力の部分集合のみ。新規能力の追加はCapability Contractの改訂が必要 |
| `authority_level` | このAdapterに許可された権限レベル | `advisor`（提案のみ） \| `transport`（伝送のみ）。`operator`/`peer`は本v1では登録不可(Step4-Aの暫定固定により、現時点でGPT=Advisor、MCP=Transportのみが許可される) |
| `audit_policy` | このAdapterに適用される監査方針 | `mandatory`固定（Step4-A Audit Rule=Mandatoryに従う。本v1では選択不可） |
| `status` | Adapterの現在の登録状態 | `registered` \| `suspended` \| `revoked`。実装されていないAdapterは登録対象外（registeredにできない） |

## Registry エントリ例（記述形式のみ・実データではない）

```yaml
adapter_id: gpt-advisor-001
adapter_type: advisor
adapter_version: v1
capability_set:
  - event_count
  - last_snapshot
  - current_state
  - replay_state
  - audit_status
authority_level: advisor
audit_policy: mandatory
status: registered
```

```yaml
adapter_id: mcp-transport-001
adapter_type: transport
adapter_version: v1
capability_set: []   # Transportは能力を提案しない。中継のみ
authority_level: transport
audit_policy: mandatory
status: registered
```

上記はRegistryの記述形式を示す例であり、実際のAdapterは未実装のため
`status: registered`のエントリは現時点で存在しない。

## Registry運用規則

1. `authority_level`は`docs/governance/adapter_governance_v1.md`が
   定める権限構造を上書きできない。Registry登録時に矛盾する
   `authority_level`(例: `operator`や`peer`)を設定することは禁止。
2. `capability_set`は`docs/contracts/capability_registry_v1.md`の
   既存5能力の部分集合のみを許可する。新規能力を追加する場合は
   Capability Contract(Step4-B)自体の改訂が先に必要。
3. `audit_policy`は常に`mandatory`。Adapterごとに監査を免除する
   設定は許可されない。
4. `status`が`registered`になるのは、対応するAdapter実装が
   Step4-A/Step4-B/本Registryの制約を満たすことが確認された後のみ。
   本v1の時点では実装が存在しないため、エントリは登録されていない。

## Step4-Cで明示的に禁止する実装

- SDK
- API
- Client
- Server
- Runtime
- External Connection

## 完了条件

- [x] `adapter_id` / `adapter_type` / `adapter_version` / `capability_set` / `authority_level` / `audit_policy` / `status` の定義
- [x] Registry運用規則の定義
- [x] 上記禁止実装(SDK等)は作成していない

## 次のステップ

Phase5 Step5「Advisor Adapter Design」(GPTをAdvisorとして接続するための
制度設計)は、本Registryのフィールド定義(特に`adapter_type: advisor`、
`authority_level: advisor`、`capability_set`の制約)を前提として行う。
SDK導入はさらにその先であり、現時点では一切のコード・接続を作成しない。

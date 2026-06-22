# Adapter Governance v1 (Phase5 Step4-A: Authority Design)

Status: DRAFT（Step4-B/Step4-Cの前提条件として固定する制度設計文書）
Date: 2026-06-22

本文書は技術実装ではない。GPT/MCPをMoCKA Time OSに接続する前に
「誰が決定権を持つのか」を制度として固定するための文書である。
Adapter実装・接続コード作成はStep4-B/Step4-Cで扱う範囲であり、
本文書(Step4-A)の段階では一切行わない。

前提: `docs/governance/phase5_boundary_declaration.md`(Phase5 Step3時点の
境界宣言)において GPT Adapter / MCP Adapter は Not Connected と宣言済み。
本文書はその境界を維持したまま、接続される場合の権限構造のみを設計する。

## 現在の権限構造（閉じた構造）

```
User
 ↓
MoCKA
 ↓
Time OS
```

User → MoCKA → Time OS の一方向のみ。外部主体は存在しない。

## 接続後の候補構造

```
User → MoCKA → GPT
User → MoCKA → MCP
User → MoCKA → GPT → MCP
```

いずれの構造でも、MoCKAがUserとTime OSの間に立つ唯一の制度的境界であることは変わらない。

## 核心質問1: GPTは何者か

| Model | 構造 | 決定権 |
|---|---|---|
| A. Tool | MoCKA → GPT | ゼロ（単なるツール） |
| B. Advisor | MoCKA → GPT | 提案のみ。実行不可 |
| C. Operator | MoCKA → GPT | 限定的実行権 |
| D. Peer | MoCKA ↔ GPT | 共同意思決定 |

### 決定: GPT = Model B (Advisor) に固定する

理由: 現在のReplay監査思想(Replay Audit Layer = 実行結果を比較・記録するが
自動修復はしない、`relay/replay_router.py`の`_emit_drift()`は記録のみで
自律的な訂正動作を一切行わない)と一致するため。GPTは提案を行えるが、
Time OSの状態・Replay・Snapshot・Eventに対する実行権は持たない。

## 核心質問2: MCPは何者か

| Option | 定義 |
|---|---|
| 1. Transport | MCP = 通信路 |
| 2. Execution Layer | MCP = 実行機構 |
| 3. External Authority | MCP = 外部権限 |

### 決定: MCP = Option 1 (Transport) に固定する

理由: MCPはGPT(Advisor)とMoCKAの間の通信経路に過ぎない。MCP自体が
実行権や決定権を持つことを許容すると、Time OS Contract
(`docs/contracts/time_os_contract_v1.md`)が定める「RelayKernelを
唯一の入口とする」という構造契約を迂回する経路になりかねないため、
通信路としての役割のみに限定する。

## 権限マトリクス（暫定案・本Sealで確定）

| 項目 | 値 |
|---|---|
| Authority Owner | User |
| Execution Authority | MoCKA |
| GPT | Advisor（提案のみ・実行不可） |
| MCP | Transport（通信路のみ） |
| Execution Rights | MoCKA以外には付与しない |
| Memory Rights | MoCKA以外には付与しない（Event/Queue/Snapshot Repositoryへの書込はRelayKernel経由のみ） |
| Replay Rights | 読み取り専用。GPT/MCPからのReplay実行要求はAdvisor提案として扱われ、実行はMoCKA(User経由の承認)が行う |
| Snapshot Rights | Modification Prohibited（GPT/MCPからの生成・変更要求は不可） |
| Audit Rights | Mandatory（GPT/MCP経由の全ての提案・やり取りはMoCKAの記録対象。`mocka_write_event`等による記録義務は本構造にも適用される） |

### 規則の詳細

- **Replay Modification = Prohibited**: GPT/MCPはReplayの実行結果を閲覧・提案に利用できるが、ReplayMode変更・ReplayEngine/ReplayRouterの呼び出し方法自体を変更することはできない。
- **Snapshot Modification = Prohibited**: GPT/MCPはSnapshotの生成・更新を要求できない。Snapshotは`RelayKernel.maybe_snapshot()`の既存ルール(event_count % SNAPSHOT_INTERVAL)のみに従う。
- **Event Modification = Prohibited**: GPT/MCPはEvent Repositoryへの追加・変更を一切行えない。Eventの追加は既存のRelayKernel.ingest()経路のみで行われ、GPT/MCPはこの経路を呼び出す権限を持たない。

## 権限移譲規則（Authority Delegation）

1. User → MoCKA: Userは常にMoCKAに対する最終決定権を持つ。MoCKAはUserの代理として動作するが、Userの承認なしにAuthority Ownerの地位を他者へ移譲することはできない。
2. MoCKA → GPT: MoCKAはGPTに対して「提案を求める」権限のみを委譲できる。実行権・書込権・モード変更権は委譲対象に含まれない。
3. MoCKA → MCP: MoCKAはMCPに対して「通信経路として使う」権限のみを許可する。MCP自体に決定権・実行権は委譲されない。
4. 委譲の上限: いかなる委譲も、本文書のExecution Rights/Memory Rights/Replay Rights/Snapshot Rights/Audit Rightsの値を上書きすることはできない。これらの値を変更する場合は本文書自体の改訂(Phase変更レベル)が必要。

## 監査規則（Audit Rule）

- GPT/MCP経由の全ての入出力は記録対象とする(Audit = Mandatory)。
- Replay Audit Layer(`relay/replay_audit.py`)が提供するDrift検知・記録の原則(記録のみ・自動修復なし)を、GPT/MCPとのやり取り全体に拡張適用する。すなわち、GPTの提案とMoCKAの実際の決定が異なった場合も、それ自体を「drift」として記録する設計とする(実装はStep4-B以降で検討)。

## 実行規則（Execution Rule）

- 実行(Time OSの状態に影響する操作、または将来の書込API)は常にMoCKA(RelayKernel経由)のみが行う。
- GPTは実行を「提案」できるが、その提案を実行に移すかどうかの判断はMoCKA/Userに属する。
- MCPは実行主体にはならない。実行要求の伝送経路としてのみ機能する。

## Step4-Aの完了条件

- [x] Authority Owner / Execution Authority / GPT役割 / MCP役割を定義
- [x] Execution Rights / Memory Rights / Replay Rights / Snapshot Rights / Audit Rights を定義
- [x] 権限移譲規則を定義
- [x] 監査規則を定義
- [x] 実行規則を定義
- [x] Adapter実装・接続コードは作成していない（本文書のみ）

## 次のステップ

Step4-B「Adapter Contract Design」は、本文書が定めた権限構造を前提として、
GPT Advisor / MCP Transportの「契約形式」（入出力フォーマット等）を設計する。
これもユーザーの明示的な判断を得てから着手する。Step4-Cの実装着手はさらに
その先であり、現時点では一切のコード・接続を作成しない。

# PHI-OS / MoCKA Integration Architecture Decision Package v0.1

**Status:** PROPOSAL(Decisionを決める文書ではなく、Decisionを可能にする比較資料。Decision Ledger登録はまだ行わない)
**位置づけ:** `PHI_MOCKA_INTEGRATION_SCOPE_PROPOSAL_v0.1.md`(commit `224a7bfe3`)後続、Human Gate Preparation(Phase 1)。
**重要な構成方針:** 全セクションでConfirmed(実測・既存Decision Ledger根拠)とProposal(未採用の候補比較)を完全分離する。本文書は候補案のいずれも採用しない。
**禁止事項(本文書の作成範囲)**: Adapterコード作成・API追加・Runtime変更・MoCKA変更・Test追加は一切行わない。比較・影響分析・Decision材料整理のみ。

---

## 1. Decision Context

### Confirmed

- PHI-OS Runtime Foundation(`phios/runtime/`の`controller_core.py`/`event_runtime.py`/`adapter_runtime.py`/`memory_boundary.py`)は変更しない(`DC_20260729_011`、凍結承認済み)
- MoCKA本体(`C:/Users/sirok/MoCKA/`のうち`PlanningCaliber/`を除く部分)は変更しない
- Integration Scope(対象ファイルパス/新規変更範囲/Test影響/Gap影響)は`PHI_MOCKA_INTEGRATION_SCOPE_PROPOSAL_v0.1.md`によりcommit `224a7bfe3`でSeal済み
- Evidence Foundation(Runtime Foundation Validation、Module Integration Strategy)はcommit `d69121b9e`でSeal済み
- なぜMoCKA統合が必要か: `DC_20260729_012`(HG-MI-01)によりIntegration Target(MoCKA/Memory/Orchestra/Relay、新規モジュール追加なし)が承認済み。MoCKAが最初の統合対象として推奨された理由(HG-MI-02根拠)は「read-only境界・Evidenceの考え方が既に整理されており、接続対象として最も成熟している」ため(Decision Ledger記載をそのまま引用)
- PHI-OS内でのMoCKAの位置づけ: `PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md`(2026-07-28、`DC_20260728_003`)により、MoCKAはPHI-OSの部品ではなく「PHI-OSが正しく動作していることを保証する外部制度層(External Governance Runtime)」と位置づけ済み。本Decision Packageはこの位置づけを変更しない

### Proposal

なし(本セクションは既存確定事項の引用のみ)。

---

## 2. Integration Boundary Analysis

### Confirmed(現在接続可能な境界)

RC-011 PHL Relay Client(`phios/phl/relay_client.py`、commit `9faa421`)が唯一の実装済み接続経路である。実測(grep)により以下を確認済み:

- 通信先は`http://localhost:5002/mcp`(MCP経由のツール呼び出し)と`http://localhost:5000/api/gate/audit`(HTTP直接、優先)の2エンドポイントのみ
- `phios/runtime/*.py`4ファイルはいずれもMoCKA側モジュールをimportしていない
- Read-only tool allowlistが呼び出し前に強制されており、Write系ツールは呼び出せない
- 読み取り失敗時は"insufficient evidence"として扱われ、結果を捏造しない

### Proposal(候補接続方式、いずれも未採用)

現在のRC-011は「MoCKAの個別エンドポイントを直接叩くクライアント」であり、Runtime FoundationとRC-011の間を仲介する層は未実装(前回`PHI_MOCKA_INTEGRATION_SCOPE_PROPOSAL_v0.1.md`§2で指摘済み)。以下はその仲介層の候補案であり、3案とも比較対象としてのみ提示する。

#### Candidate A: PHI-OS Adapter Pattern

```
PHI-OS Runtime
        |
        v
Integration Adapter
        |
        v
RC-011 Relay Client
        |
        v
MoCKA
```

特徴:
- PHI-OS側責任が明確(Adapterのみが新規コンポーネント、RC-011は変更不要)
- MoCKA独立維持(既存のRC-011境界をそのまま利用)
- 最小変更(Runtime Foundation・RC-011とも無変更、Adapterの新規追加のみ)

#### Candidate B: Relay-mediated Pattern

```
PHI-OS Runtime
        |
        v
      Relay
        |
        v
      MoCKA
```

特徴:
- 既存Relay思想(RC-011自体が既に「Relay」という名を持つ、`extension_canonical_paths`のRelay_Project等)との整合
- 中央制御可能(単一のRelay層に統合窓口を集約できる)
- 境界管理が複雑化する可能性(RC-011の既存責務"MoCKAの単一チャネル"と、新たな"Runtime全体の仲介"責務が同一コンポーネントに重なる場合、責務分離が曖昧になるリスク)

**Confirmed観察(採用判断ではない)**: RC-011は名称・実装とも既にこのパターンに近い形(単一の仲介コンポーネントがMoCKA個別エンドポイントを吸収する構造)を部分的に持つ。ただしRC-011は現状「MoCKAとの通信を1箇所に集約するクライアント」であり、「PHI-OS Runtime全体からの呼び出しを仲介する層」としての責務は明示的に持たない(既存23テストはRelay Client単体のunit/failure/boundaryのみで、Runtime Foundationとの結合テストは含まれない)。

#### Candidate C: Event Bridge Pattern

```
PHI-OS
   |
   v
Event Stream
   |
   v
MoCKA
```

特徴:
- 非同期拡張性(Event Runtime(`phios/runtime/event_runtime.py`)の既存Event発行の仕組みと親和性がある可能性)
- 大規模化向き(将来Memory/Relay/Orchestraへの拡張時、Publish/Subscribe型で個別接続を増やさずに済む可能性)
- Decision Ownership設計が難しい(誰が「読み取り成功/失敗」の最終判定を持つかが、同期的なCandidate A/Bより不明確になりやすい。Gap-001(REJECTED状態不足)と同種の課題が拡大するリスク)

---

## 3. Responsibility Matrix

### Confirmed(現在の所有責務、実装から実測)

| 領域 | 現在の所有 | 根拠 |
|---|---|---|
| Decision Evidence生成 | MoCKA(`decision_ledger.jsonl`、`mocka_decision_write`) | MoCKA側Decision Ledgerが唯一の記録先。PHI-OS側`ise/decision_ledger.py`は別データストア(PHI-OS内部専用、`PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md`§1確認済み) |
| Runtime制御 | PHI-OS(`controller_core.py`/`event_runtime.py`/`adapter_runtime.py`) | Runtime Foundation、DC_20260729_011でComplete/凍結 |
| 履歴保持(Read-only Context) | PHI-OS(`memory_boundary.py`) | V-05実装済み。write/update/delete method無し、seed_contextはRuntime Copyであり本体Memoryではないと文書化済み |
| 監査証跡(Audit) | MoCKA(`phi_os/event_gate.py`の`gate_audit()`、`/api/gate/audit`) | `PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md`§2確認済み |
| Human Gate | MoCKA(`phi_os/human_gate.py`) | 同文書§2に記載の通り、現状3系統併存・Phase1B凍結中と過去調査で判明済み(MoCKA側自身の未解決課題であり、本Decision Packageの対象外) |

### Proposal(候補Architectureごとの責務分配案、いずれも未採用)

| 領域 | Candidate A(Adapter) | Candidate B(Relay-mediated) | Candidate C(Event Bridge) |
|---|---|---|---|
| 呼び出し起点の所有 | Integration Adapter(新規) | Relay(RC-011拡張または新規Relay層) | Event Stream Publisher(Runtime側) |
| MoCKA応答の解釈・evidence insufficient判定 | Integration Adapter | Relay | 未確定(Subscriber側候補だが、非同期のため判定タイミングが分散しうる) |
| Runtime Stateへの反映可否 | Adapter経由のみ、Runtime本体は不変(現状のmemory_boundary.py non-interference原則を踏襲可能) | Relay経由のみ、Runtime本体は不変 | 未確定(Event処理タイミングとRuntime State更新タイミングの分離設計が必要) |
| テスト責任の所在 | Adapter単体テスト + Runtime-Adapter結合テスト | RC-011拡張テスト + Runtime-Relay結合テスト | Event Stream単体テスト + 非同期結合テスト(設計難度が相対的に高い) |

---

## 4. Risk Assessment

### Confirmed(観測済みリスク、本セッションでの実測に基づく)

- Gap-001(REJECTED状態不足)・Gap-002(Decision Ledgerフィールド不足)・Gap-003(Freshness閾値未確定)は未解決のまま(`DC_20260729_011`確認事項4・5)
- `phios/context_assembly/`はgit未追跡・Human Gate承認なしのままScope外資産として存在する(`PHI_MOCKA_INTEGRATION_SCOPE_PROPOSAL_v0.1.md`§4)
- `workshop/phi-os`はMoCKA本体と別git repoであり、`docs/audits/`はMoCKA本体側にある。本セッション中に、承認済みDecisionが引用する一次証跡文書が未追跡のまま放置されていた事例を2件(3文書)発見・是正済み(commit `d69121b9e`)。同種の記録漏れが再発するリスクは構造的に残る
- MoCKA側Human Gateは3系統併存・Phase1B凍結中であり(§3 Confirmed参照)、いずれの候補案を採用する場合も、PHI-OS側Human Gateとの二重化・混線の可能性を個別に検証する必要がある

### Proposal(候補案ごとの影響分析、いずれも未採用)

| リスク項目 | Candidate A(Adapter) | Candidate B(Relay-mediated) | Candidate C(Event Bridge) |
|---|---|---|---|
| 循環依存 | 低(単方向: Runtime→Adapter→RC-011→MoCKA) | 低〜中(Relayが将来複数方向の仲介を担うと逆流経路が生まれうる) | 中(Event Streamの購読関係が複雑化すると循環しうる) |
| Authority重複 | 低(Adapterは新規、既存コンポーネントの権限を奪わない) | 中(RC-011拡張の場合、RC-011自体の既存責務"MoCKA単一チャネル"と新責務が重なる) | 中〜高(Publisher/Subscriber双方が判断権限を持ちうる) |
| Memory二重管理 | 低(memory_boundary.pyのread-only原則を踏襲しやすい) | 低〜中 | 中(非同期Eventの一時保持がMemory Boundaryと役割重複しうる) |
| Decision Ownership混在 | 低(Adapterが単一の解釈者) | 中 | 高(Gap-001と同種の課題が拡大するリスク、§2で既述) |
| Runtime Drift | 低(Runtime Foundation本体は不変のまま) | 低 | 中(非同期処理のタイミング差がRuntime Stateとの不整合を生みうる) |

---

## 5. Human Gate Required

**Decision Pending:**
- Integration Adapter形式(Candidate A / B / C、またはその他)
- Responsibility Ownership(§3 Proposalのいずれかの配分、またはその他)
- Authority Boundary(特にMoCKA側Human Gate 3系統併存状態との関係整理)
- Implementation Start Approval

本文書はいずれの候補も推奨・採用しない。次の判断はHuman Gate(きむら博士)に委ねる。

---

## Knowledge Lineage

**Document:** PHI_MOCKA_INTEGRATION_ARCHITECTURE_DECISION_PACKAGE_v0.1.md
**Status:** PROPOSAL
**Created:** 2026-07-29
**Origin:** きむら博士指示「Phase 1: Human Gate Preparation 開始」を受けて作成。
**Parent Documents:** `DC_20260729_011`, `DC_20260729_012`, `docs/audits/PHI_MOCKA_INTEGRATION_SCOPE_PROPOSAL_v0.1.md`(commit `224a7bfe3`), `docs/audits/PHI_RUNTIME_ARCHITECTURE_VALIDATION_v1.0.md`・`PHI_MODULE_INTEGRATION_STRATEGY_PROPOSAL_v0.1.md`(いずれもcommit `d69121b9e`でSeal済み)
**Derived From:** `PHI_MOCKA_INTEGRATION_SCOPE_PROPOSAL_v0.1.md`§2(Integration Adapter未確定の指摘)
**Supersedes:** なし
**Reason For Creation:** Integration Adapter形式・責務境界・権限境界についてHuman Gateが判断できる比較材料を、採用判断を含めずに整備するため。

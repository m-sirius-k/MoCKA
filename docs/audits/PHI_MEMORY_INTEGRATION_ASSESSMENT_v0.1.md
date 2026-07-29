# PHI Memory Integration Assessment v0.1

**Status:** ASSESSMENT(既存Institutional Memory設計とPHI-OS Core実装の整合確認。Architecture再設計ではない。Decision Ledger登録はまだ行わない)
**位置づけ:** `DC_20260729_012`のIntegration Target「Memory」= PHI-OS Institutional Memory(確定、`workshop/memory/`のChrome拡張製品は別層・対象外)について、Phase M-00: Existing Memory Architecture Validation。
**前提資料(既存、本文書より前に確定済み、いずれもgit追跡済み・commit `540983854`)**:
- `docs/audits/PHI_MEMORY_ARCHITECTURE_DESIGN_SCOPE_v0.1.md`
- `docs/audits/PHI_MEMORY_ARCHITECTURE_v1.0.md`
- `docs/audits/PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md`

**目的:** 「Memoryを設計する」のではなく、「既存Institutional Memory設計をPHI-OS Integration対象として評価する」。以下5項目はいずれも実コード実測に基づく。

---

## 1. Existing Memory Architectureの責務確認(Confirmed)

`PHI_MEMORY_ARCHITECTURE_v1.0.md`§2が定義する4分類と、§3 Existing Asset Mappingが対応づける既存機構は以下の通り(引用)。

| Memory Type | 既存機構(文書記載) |
|---|---|
| Event Memory | MoCKA Event Ledger(`data/mocka_events.db`、`phi_os/event_gate.py`) |
| Decision Memory | MoCKA Decision Ledger(`mocka_decision_write/get/list`) |
| Semantic Memory | Docs(`PHI_OS_CONSTITUTION_v1.md`等)/ Constitution |
| Procedural Memory | Runbook / Operational Docs(`MoCKA/.claude/CLAUDE.md`のCHANGE_START/DONEプロトコル等) |

**本Assessmentで追加確認した事実(文書に記載されていない)**: PHI-OS Core側にも`ise/decision_ledger.py`という**別のDecision Ledger実装**が実在する(SHA-256ハッシュチェーン付きの`append_decision`/`read_ledger`/`verify_chain`を持つ、69行、実装済み・稼働可能)。これはMoCKA側Decision Ledgerとは別データストア(`data/ise/decision_ledger.jsonl`)であり、`PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md`が既に「PHI-OS内部の意思決定台帳、MoCKA側とは別物」と確認済みのものと同一である。

**発見(Documentation Gap)**: `PHI_MEMORY_ARCHITECTURE_v1.0.md`§3のExisting Asset Mappingは、Decision Memoryの既存機構としてMoCKA側Decision Ledgerのみを記載しており、PHI-OS自身の`ise/decision_ledger.py`への言及がない。Decision Memoryには実際には**2つの既存ストア**(MoCKA側・PHI-OS側)が存在する。

---

## 2. PHI-OS Coreとの接続境界確認(Confirmed)

`phios/runtime/memory_boundary.py`(V-05、`DC_20260729_011`でRuntime Foundationの一部として凍結)が、Institutional Memoryへの将来的な接続点として自身の docstring で明示的に予告されている。

> 引用(`memory_boundary.py`より): "Memory (Institutional) -> Snapshot -> MemoryBoundary (this class)"

**現状(実測)**:
- `MemoryBoundary.__init__`は`seed_context`(コンストラクタ時に一度だけ渡される静的な辞書)のみを受け取る。MoCKA側Decision Ledger・PHI-OS側`ise/decision_ledger.py`のいずれにも、実行時に問い合わせる経路を持たない
- リポジトリ全体をgrepした結果、`memory_boundary.py`(自身のテストを除く)を参照するコードはゼロ件。`ControllerCore`/`EventRuntime`/`AdapterRuntime`のいずれからも呼び出されていない
- 結論: 接続境界は**設計上予告されているが、実装上は未接続**(スタンドアロンのプロトタイプ)

---

## 3. Existing Access Control Policyとの整合確認(Confirmed)

`PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md`§0のState→Memory Permission Mapping表は、`PHI_SEQUENCE_STATE_MODEL_v1.0.md`(S07)の11状態+UNKNOWNを前提としている。

**構造的整合(実測で確認)**: 表に記載の12状態名(OBSERVED/CLASSIFIED/CONTEXT_READY/VERIFICATION_PENDING/VERIFIED/HUMAN_GATE_REQUIRED/APPROVED/EXECUTING/COMPLETED/AUDITED/MEMORIZED/UNKNOWN)は、`phios/runtime/controller_core.py`の`State`enumと**完全一致**する(1件も欠落・追加なし)。

**別モデルとの区別(実測で確認)**: `ise/state_machine.py`の`ISEState`(INITIALIZING/ACTIVE/DEGRADED/SUSPENDED/SEALED)は、Access Control Policyが参照するS07モデルとは**別の状態モデル**である。Access Control Policyの表がS07(Runtime Foundation側)を指しており、ISEState(PHI-OS Coreのプロセスライフサイクル)を指していないことを確認した。混同のリスクは低い。

**実装との不整合(実測で確認)**: リポジトリ全体をgrepした結果、"Memory Permission"相当のアクセス制御ロジックを実装しているコードはゼロ件。`memory_boundary.py`の`get_context()`/`has_context()`は、呼び出し時の`ControllerCore.state`を一切参照しない(そもそも`ControllerCore`への参照を持たない、§2参照)。**Access Control Policyの表は現時点で紙上の定義のみであり、コードによる強制は存在しない。**

---

## 4. Adapter必要性確認(Proposal、判断ではなく評価)

MoCKA統合(`DC_20260729_013`)で採用したCandidate A(Translation Boundary Adapter)と同種のAdapterが、Memory統合にも必要かを評価する。

| Memory Type | データ源 | 既存の到達経路 | 新規Adapter必要性(評価) |
|---|---|---|---|
| Event Memory | MoCKA Event Ledger | RC-011(`relay_client.get_mocka_state`/`get_mocka_audit`)+`mocka_integration_adapter.get_mocka_context`/`describe_mocka_audit` — **既存経路で到達済み** | 低(MoCKA統合Adapterが既にカバー) |
| Decision Memory(MoCKA側) | MoCKA Decision Ledger | RC-011(`relay_client.get_mocka_decision`/`list_mocka_decisions`)+`mocka_integration_adapter.link_evidence_for_event` — **既存経路で到達済み** | 低(同上) |
| Decision Memory(PHI-OS側) | `ise/decision_ledger.py` | PHI-OS Core内部(同一プロセス、モジュール境界なし) | Adapter不要(直接import可能な範囲。Relay/Adapterパターンは「プロセス境界を越える通信」に対する境界であり、同一Core内の別モジュール参照には適用対象外) |
| Semantic Memory | Docs/Constitution | クエリ可能なストアが存在しない(ファイルシステム上のMarkdown文書のみ) | 評価不能(Adapterの前に、クエリ可能な形にする実装自体が先に必要) |
| Procedural Memory | Runbook/CLAUDE.md | 同上 | 同上 |

**評価(Proposal、確定ではない)**: Event/Decision Memory(MoCKA側)については、新規のMemory専用Adapterは**不要である可能性が高い**。既にMoCKA統合Adapter(`phios/adapter/mocka_integration_adapter.py`)が同じ経路(RC-011)を経由して同じデータに到達しているため、機能的な重複になりうる。むしろ必要なのは、`memory_boundary.py`(またはその後継)を、既存の2つのDecision Ledger(MoCKA側・PHI-OS側)および`mocka_integration_adapter`の出力に実際に接続する**配線作業**であり、新規の通信境界を作る作業ではない。

---

## 5. Implementation Gap確認(Confirmed、観測事実の列挙)

- **Gap-M1**: `memory_boundary.py`が実際のMemory源(MoCKA Decision/Event Ledger、`ise/decision_ledger.py`)のいずれにも配線されていない(§2)
- **Gap-M2**: Access Control PolicyのState→Memory Permission Mappingがコードで強制されていない(§3)
- **Gap-M3**: `PHI_MEMORY_ARCHITECTURE_v1.0.md`§3のExisting Asset Mappingが、PHI-OS自身の`ise/decision_ledger.py`を記載していない(§1のDocumentation Gap)
- **Gap-M4**: Semantic Memory・Procedural Memoryにクエリ可能なストアが存在しない(§4)
- **Gap-003との関連(既存Gap、新規発見ではない)**: `PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md`§3(Memory Freshness Contract)は「具体的な鮮度閾値は本Policyでは決めない」と明記しており、これは`DC_20260729_011`が維持を確認したGap-003(Memory Freshness閾値未確定)と**同一の未解決事項**である。Memory Architecture側の文書とRuntime Foundation側のGap台帳が、独立に同じ未解決事項へ到達している(相互に参照していないが内容は一致)。

---

## 次工程

Human Gateにおいて、以下の判断が必要になる(本文書はいずれも判断しない)。

- §4で評価した「Memory専用Adapterは不要、配線作業が必要」という評価を採用するか、それとも別途Adapterパターンを設計するか
- Gap-M1〜M4のうちどれを、どの順序で解消するか(全て一括ではなく段階的に扱うか)
- `PHI_MEMORY_ARCHITECTURE_v1.0.md`§3のDocumentation Gap(Gap-M3)を、既存文書の改訂として扱うか、新規文書として扱うか

---

## Knowledge Lineage

**Document:** PHI_MEMORY_INTEGRATION_ASSESSMENT_v0.1.md
**Status:** ASSESSMENT
**Created:** 2026-07-29
**Origin:** きむら博士指示「Phase M-00: Existing Memory Architecture Validation」を受けて作成。当初想定していた新規Scope設計(`PHI_MEMORY_INTEGRATION_SCOPE_v0.1.md`)は作成しない。
**Parent Documents:** `docs/audits/PHI_MEMORY_ARCHITECTURE_DESIGN_SCOPE_v0.1.md`、`docs/audits/PHI_MEMORY_ARCHITECTURE_v1.0.md`、`docs/audits/PHI_MEMORY_ACCESS_CONTROL_POLICY_v1.0.md`、`DC_20260729_012`、`DC_20260729_013`
**Derived From:** 上記3文書の内容とPHI-OS Core実装(`phios/runtime/memory_boundary.py`・`ise/decision_ledger.py`・`ise/state_machine.py`・`phios/runtime/controller_core.py`)の突き合わせ
**Supersedes:** なし
**Reason For Creation:** 既存Institutional Memory設計を再発明せず、PHI-OS Core実装との整合・未接続部分(Implementation Gap)を明確化し、Adapter必要性の判断材料を整えるため。

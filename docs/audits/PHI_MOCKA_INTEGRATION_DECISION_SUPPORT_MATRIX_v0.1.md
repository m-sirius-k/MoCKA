# PHI-OS / MoCKA Integration Decision Support Matrix v0.1

**Status:** PROPOSAL(比較軸の固定のみ。採用判断・推奨順位付け・最適案決定は含まない。Decision Ledger登録はまだ行わない)
**位置づけ:** `PHI_MOCKA_INTEGRATION_HUMAN_GATE_DECISION_RECORD_v0.1.md`(commit `20c57228c`)と並行して使う評価補助資料。D-01〜D-04(Decision Record §2)を判断する前提条件(比較軸)を固定する。
**禁止事項**: 推奨順位付け・採用宣言・最適案決定。本文書はいずれのCandidateも選ばない。

---

## 1. Decision Context(Confirmedのみ)

```
Evidence Foundation:     d69121b9e
Scope:                   224a7bfe3
Architecture Package:    51dcbe920
Review:                  8b927ff14
Decision Record Template: 20c57228c
```

いずれもUTF-8検証・SHA-256取得・`mocka_git_safe_commit()`経由でSeal済み(push=False)。

---

## 2. Evaluation Criteria(比較軸の固定)

| 評価軸 | 意味 |
|---|---|
| Boundary Preservation | 既存境界(Runtime Foundation凍結・MoCKA本体不変・RC-011既存責務)を壊さないか |
| Authority Clarity | 読み取り成功/失敗・Runtime State反映可否の最終判断者が一意に説明できるか |
| Evidence Compatibility | 既存Evidence Chain(CHANGE_START〜CHANGE_DONE〜Git Seal)・監査証跡(MoCKA `/api/gate/audit`)と整合するか |
| Runtime Impact | Runtime Foundation・RC-011・MoCKA本体への変更影響範囲 |
| Future Extensibility | `DC_20260729_012`の推奨統合順序(MoCKA→Memory→Relay→Orchestra)で後続モジュール接続時に再利用・拡張できるか |
| Failure Isolation | 一部の接続が失敗した際に、他コンポーネント(Runtime本体・他モジュール接続)へ影響を波及させずに切り離せるか |

**注記:** 6軸に対する重み付けは本文書では行わない。重み付けそのものもHuman Gateの判断対象になり得るため、ここでは軸の定義のみを固定する。

---

## 3. Candidate Comparison(Confirmed / Proposal / Unknownに分離。推奨順位付けなし)

各Candidateについて、既に存在する事実(Confirmed)、`PHI_MOCKA_INTEGRATION_ARCHITECTURE_DECISION_PACKAGE_v0.1.md`(commit `51dcbe920`)で主張済みだが未検証の設計上の見込み(Proposal)、およびまだ分析されていない項目(Unknown)を分ける。Candidate自体が未実装であるため、Candidate固有の挙動に関する記述は全てProposalまたはUnknownであり、Confirmedにはならない。

### Candidate A: PHI-OS Adapter Pattern

**Confirmed**
- RC-011(`phios/phl/relay_client.py`、commit `9faa421`)は既存・無変更で利用可能
- 本Candidateの構造上、Runtime Foundation 4ファイルは呼び出し元としてのみ関与する位置づけ(構造図上の記述であり、実装・検証済みではない)

**Proposal**(Decision Package記載の主張、実測ではない)
- Authority重複リスク: 低(Adapterは新規、既存コンポーネントの権限を奪わないという設計意図)
- Decision Ownership混在リスク: 低(Adapterが単一の解釈者になるという設計意図)
- Runtime Driftリスク: 低(Runtime Foundation本体は不変のままという設計意図)
- テスト設計難度: 低(単体+結合の2層で足りるという見積り)

**Unknown**
- Adapterの正確なInterface(関数シグネチャ・エラー型)は未定義
- Adapterのテスト数の具体的な見積りは未実施
- Memory/Relay/Orchestra統合時に本パターンをそのまま再利用できるかは未検証
- MoCKA側Human Gate(3系統併存・Phase1B凍結中、`PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md`§2)との相互作用の有無は未分析

### Candidate B: Relay-mediated Pattern

**Confirmed**
- RC-011は名称・実装とも、単一の仲介コンポーネントがMoCKA個別エンドポイントを吸収する構造を部分的に既に持つ(commit `9faa421`実測)
- 既存23テストはRC-011単体のunit/failure/boundaryのみで、Runtime Foundationとの結合テストは含まない(実測)

**Proposal**
- Authority重複リスク: 中(既存RC-011責務"MoCKA単一チャネル"と新責務"Runtime全体の仲介"が同一コンポーネントに重なる可能性)
- Decision Ownership混在リスク: 中
- テスト設計難度: 中
- `DC_20260729_012`の推奨統合順序ではRelay自体は3番目の対象であり、MoCKA単体接続の段階でRelay層を拡張する必要性は要検証(Human Gate Review §3に既記載)

**Unknown**
- RC-011拡張が既存23テストに与える回帰影響の具体的範囲は未分析
- 本Candidateの"Relay"と、`extension_canonical_paths`に登録済みの別プロダクト"Relay_Project"(Chrome拡張)との名称混同リスクの有無は未検討
- 拡張後のRC-011の責務境界(既存"MoCKA単一チャネル"と新規"Runtime仲介"の境界線)をどう文書化するかは未定義

### Candidate C: Event Bridge Pattern

**Confirmed**
- Event Runtime(`phios/runtime/event_runtime.py`、V-02実装済み)は既にEvent発行の仕組みを持つ(既存36テストの一部で検証済み)

**Proposal**
- Authority重複リスク: 中〜高
- Decision Ownership混在リスク: 高(Gap-001 REJECTED状態不足と同種の課題が拡大するリスク、という設計上の懸念)
- Runtime Driftリスク: 中(非同期タイミング差による懸念)
- テスト設計難度: 高(非同期結合テストが必要という見積り)

**Unknown**
- 非同期処理の具体的な実装技術(キュー/pub-sub基盤の選定)は未検討
- Event Bridge層の障害時にevidence insufficient判定を非同期文脈でどう保証するかは未設計
- `memory_boundary.py`のnon-interference原則(V-05実装済み)が非同期文脈でも成立するかは未検証

---

## 4. Decision Questions(D-01〜D-04へ接続)

本セクションは`PHI_MOCKA_INTEGRATION_HUMAN_GATE_DECISION_RECORD_v0.1.md`§2への入口であり、判断結果はそちらに記入する。

- **D-01**: どのIntegration Patternを採用するか(§3のConfirmed/Proposal/Unknownを踏まえて判断)
- **D-02**: Adapter責務を誰が所有するか(§2 Authority Clarity軸を踏まえて判断)
- **D-03**: Authority Boundaryをどこに置くか(§2 Boundary Preservation・Evidence Compatibility軸を踏まえて判断)
- **D-04**: Implementation開始を承認するか(§3のUnknown項目が判断に足る程度に解消されているかを踏まえて判断)

---

## 5. Human Gate Entry Condition

```
No Architecture Adoption
No Implementation
No Runtime Change

until Human Gate Decision is recorded
(PHI_MOCKA_INTEGRATION_HUMAN_GATE_DECISION_RECORD_v0.1.md §2 D-01〜D-04 記入完了 + mocka_decision_write によるDecision Ledger記録)
```

---

## 完了後の状態

```
Evidence Foundation:      SEALED   (d69121b9e)
Scope:                    COMPLETE (224a7bfe3)
Architecture Package:     PREPARED (51dcbe920)
Review:                   PREPARED (8b927ff14)
Decision Record:          PREPARED (20c57228c)
Decision Support Matrix:  PREPARED (本文書)
Human Gate:               READY
```

本文書自体はArchitecture決定ではないため、作成は連続実行運用の対象である。以降(D-01〜D-04記入)は真のHuman Gateであり、自動進行しない。

---

## Knowledge Lineage

**Document:** PHI_MOCKA_INTEGRATION_DECISION_SUPPORT_MATRIX_v0.1.md
**Status:** PROPOSAL
**Created:** 2026-07-29
**Origin:** きむら博士指示「Phase 3-B: Human Gate Decision Support Matrix 作成開始。評価軸整理のみ実施し、採用判断は禁止」を受けて作成。
**Parent Documents:** `docs/audits/PHI_MOCKA_INTEGRATION_HUMAN_GATE_DECISION_RECORD_v0.1.md`(commit `20c57228c`), `docs/audits/PHI_MOCKA_INTEGRATION_HUMAN_GATE_REVIEW_v0.1.md`(commit `8b927ff14`), `docs/audits/PHI_MOCKA_INTEGRATION_ARCHITECTURE_DECISION_PACKAGE_v0.1.md`(commit `51dcbe920`)
**Derived From:** `ARCHITECTURE_DECISION_PACKAGE_v0.1.md`§2-4の候補特性を、Confirmed/Proposal/Unknownの3分類へ再整理
**Supersedes:** なし
**Reason For Creation:** D-01〜D-04を判断する前提となる比較軸を固定し、既知事項(Confirmed)・設計上の主張(Proposal)・未分析事項(Unknown)を混同せずにHuman Gateへ提示するため。

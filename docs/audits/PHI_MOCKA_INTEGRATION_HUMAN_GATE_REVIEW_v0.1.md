# PHI-OS / MoCKA Integration Human Gate Review v0.1

**Status:** PROPOSAL(Decision Surfaceの整理。採用判断は含まない。Decision Ledger登録はまだ行わない)
**位置づけ:** `PHI_MOCKA_INTEGRATION_ARCHITECTURE_DECISION_PACKAGE_v0.1.md`(commit `51dcbe920`)後続、Human Gate Preparation Phase 2。
**目的:** 「推奨案を決める」のではなく、「何を判断すればArchitecture決定になるか」を明確化する。
**位置づけの違い:** 前段の`ARCHITECTURE_DECISION_PACKAGE_v0.1.md`は3候補の内容そのものを整理した。本文書はその3候補を前提に、判断者(きむら博士)が何を、どの基準で、どう判断すればよいかという「判断の構造」を整理する。

---

## 1. Current State Summary(Confirmed)

| レイヤー | 状態 | 参照 |
|---|---|---|
| Evidence Foundation | SEALED | commit `d69121b9e` |
| Integration Scope | COMPLETE | commit `224a7bfe3`(`PHI_MOCKA_INTEGRATION_SCOPE_PROPOSAL_v0.1.md`) |
| Architecture Decision Package | PREPARED(PROPOSAL) | commit `51dcbe920`(`PHI_MOCKA_INTEGRATION_ARCHITECTURE_DECISION_PACKAGE_v0.1.md`) |
| Human Gate | PENDING | 本文書 |

不変の前提(いずれの判断でも変更されない):
- Runtime Foundation(`controller_core.py`/`event_runtime.py`/`adapter_runtime.py`/`memory_boundary.py`)は変更しない
- MoCKA本体は変更しない
- Gap-001/002/003はPendingのまま維持
- `phios/context_assembly/`はScope外(未追跡・未承認)のまま

---

## 2. Decision Required Items(Confirmed、判断対象の列挙のみ)

以下4件が今回のHuman Gate対象である(いずれも本文書では判断しない)。

1. **Candidate採用**: Candidate A(PHI-OS Adapter Pattern)/ B(Relay-mediated Pattern)/ C(Event Bridge Pattern)のいずれかを採用するか、いずれも採用せず修正案・再提案を求めるか
2. **Adapter責務境界確定**: 採用candidateにおいて、MoCKA応答の解釈・evidence insufficient判定・Runtime Stateへの反映可否を、どのコンポーネントの責務とするか
3. **Authority Ownership確定**: Decision Evidence生成・Runtime制御・履歴保持・監査証跡・Human Gateの5領域(§3の既存Responsibility Matrix Confirmed行)について、新設コンポーネント(Adapter/Relay拡張/Event Bridge)がどこまで権限を持つか
4. **Implementation開始承認**: 上記1〜3が確定した後にのみ、CHANGE_START〜実装〜Test Evidence〜Git Sealのサイクルに入ってよいか

---

## 3. Candidate Comparison(Confirmed、既存Decision Package §2-4からの要約転記)

| 項目 | Candidate A: Adapter Pattern | Candidate B: Relay-mediated Pattern | Candidate C: Event Bridge Pattern |
|---|---|---|---|
| 構造 | Runtime → Integration Adapter(新規) → RC-011 → MoCKA | Runtime → Relay(RC-011拡張または新規Relay層) → MoCKA | Runtime → Event Stream → MoCKA |
| 新規コンポーネント | Adapterのみ | RC-011拡張(既存コンポーネントの責務変更を伴う可能性) | Event Stream Publisher/Subscriber |
| 既存RC-011との関係 | 無変更(Adapterが上位から呼ぶだけ) | RC-011の既存責務"MoCKA単一チャネル"と新責務"Runtime全体の仲介"が重なりうる | 無変更だが、非同期化により呼び出しパターンが変わる |
| Authority重複リスク | 低 | 中 | 中〜高 |
| Decision Ownership混在リスク | 低 | 中 | 高(Gap-001と同種の課題が拡大) |
| Runtime Drift リスク | 低 | 低 | 中(非同期タイミング差) |
| テスト設計難度 | 低(単体+結合の2層で足りる) | 中 | 高(非同期結合テストが必要) |
| DC_20260729_012の統合順序(MoCKA→Memory→Relay→Orchestra)との整合 | 中立 | Relayという名称上の親和性はあるが、順序上「Relay統合」は3番目であり、MoCKA単体接続の段階でRelay層自体を拡張する必要性は要検証 | 中立 |

**注記:** 本表は`ARCHITECTURE_DECISION_PACKAGE_v0.1.md`の記述を判断しやすい形に再配列したものであり、新たな評価情報は加えていない。

---

## 4. Rejection Conditions(Confirmed、既存の確定境界から直接導出)

以下はいずれかに該当する候補・修正案を機械的に不成立とする条件であり、Candidate間の優劣判断ではない(既存の確定事項からの直接導出のみ)。

- **R-1**: Runtime Foundation 4ファイル(`controller_core.py`/`event_runtime.py`/`adapter_runtime.py`/`memory_boundary.py`)の変更を要する案 → `DC_20260729_011`の凍結条件に抵触するため不成立
- **R-2**: MoCKA本体(`PlanningCaliber/`を除く`C:/Users/sirok/MoCKA/`配下)の変更を要する案 → Integration Target確定事項(PHI-OS側からの接続)に抵触するため不成立
- **R-3**: RC-011の既存read-only tool allowlistを迂回する、またはWrite系呼び出しを新設する案 → RC-011設計原則(read-only first、write path禁止)に抵触するため不成立
- **R-4**: Human Gateを経ない責務追加・権限変更を伴う案 → `DC_20260729_011`確定事項4([[Gap-001/002/003 Pending維持]])および「Human Gateなしの責務追加は禁止」の原則に抵触するため不成立
- **R-5**: Gap-001(REJECTED状態不足)を暗黙に解消したことにする案(例: 失敗判定を曖昧にして事実上REJECTED状態を扱わない設計) → Gap Pending維持の原則に抵触するため不成立

---

## 5. Recommended Evaluation Criteria(Proposal、判断基準の提案。採用candidateの提案ではない)

Candidate選定時に用いる評価軸の提案(重み付けは行わない、判断者が使う基準の列挙のみ):

1. **Authority明確性**: 新設コンポーネントの権限境界が、既存5領域(Responsibility Matrix)のどこに位置づけられるか一意に説明できるか
2. **最小変更性**: Runtime Foundation・RC-011・MoCKA本体への影響が最小か(§4 Rejection Conditionsを満たすことが前提、その上での相対比較)
3. **Test設計可能性**: 既存242+23テストへの回帰なしを維持したまま、新規結合テストを現実的な難度で追加できるか
4. **将来拡張との整合**: `DC_20260729_012`の推奨統合順序(MoCKA→Memory→Relay→Orchestra)において、後続のMemory/Relay/Orchestra接続時にこの構造を再利用・拡張できるか、あるいは個別設計が必要になるか
5. **Decision Ownership明確性**: evidence insufficient判定・Runtime State反映可否の最終判断者が単一かつ一意か(Gap-001と同種の曖昧さを増やさないか)

---

## 6. Human Gate Decision Record(未記入、博士判断待ち)

```
Decision ID:        (承認時にDC_YYYYMMDD_NNN形式で付番)
Decision:           [ ] Approve Candidate __   [ ] Reject All / Revise   [ ] Approve with Modification
Adapter責務境界:      (§2-2の判断結果を記入)
Authority Ownership: (§2-3の判断結果を記入)
Implementation開始承認: [ ] Yes   [ ] No(条件付き、条件: ______)
Rationale:
Approved by:
Approved at:
```

本セクションは記入用テンプレートであり、本文書作成者(Claude)はいずれの項目も記入・推測しない。

---

## Knowledge Lineage

**Document:** PHI_MOCKA_INTEGRATION_HUMAN_GATE_REVIEW_v0.1.md
**Status:** PROPOSAL
**Created:** 2026-07-29
**Origin:** きむら博士指示「Phase 2: Human Gate Decision Package Review準備」を受けて作成。
**Parent Documents:** `docs/audits/PHI_MOCKA_INTEGRATION_ARCHITECTURE_DECISION_PACKAGE_v0.1.md`(commit `51dcbe920`), `docs/audits/PHI_MOCKA_INTEGRATION_SCOPE_PROPOSAL_v0.1.md`(commit `224a7bfe3`), `DC_20260729_011`, `DC_20260729_012`
**Derived From:** `ARCHITECTURE_DECISION_PACKAGE_v0.1.md`§2-4の内容を判断構造(Decision Surface)として再整理
**Supersedes:** なし
**Reason For Creation:** Human Gateが何を・どの基準で判断すればArchitecture決定に至るかを明確化し、判断の見落としと自動確定の両方を防ぐため。

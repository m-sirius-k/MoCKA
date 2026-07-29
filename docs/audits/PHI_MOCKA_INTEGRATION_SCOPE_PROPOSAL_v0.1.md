# PHI-OS / MoCKA Integration Scope Proposal v0.1

**Status:** PROPOSAL(確定事項と審議事項を分離して記録。Decision Ledger登録はまだ行わない)
**位置づけ:** `DC_20260729_012`(Module Integration Strategy Approved)後、最初の統合対象(MoCKA)に関するScope定義提案書。
**重要な構成方針:** 「既にEvidenceで裏付けられた事実」と「これから意思決定する方針」を混在させない。前者は確定事項として、後者は未承認の提案として明確に分離する(`PHI_MODULE_INTEGRATION_STRATEGY_PROPOSAL_v0.1.md`と同じ構成方針)。

---

## 0. Confirmed Prerequisites(確定済み前提、Evidence裏付け済み)

以下はすでに`DC_20260729_011`・`DC_20260729_012`およびその一次証跡(`PHI_RUNTIME_ARCHITECTURE_VALIDATION_v1.0.md`、`PHI_MODULE_INTEGRATION_STRATEGY_PROPOSAL_v0.1.md`、commit `d69121b9e`でSeal済み)により確定している事実であり、本文書によって新たに決定するものではない。

1. Runtime Foundation(Controller Core・Event Runtime・Adapter Runtime・Memory Boundary、`phios/runtime/`配下)は`DC_20260729_011`によりComplete/凍結対象と承認済み(V-06以降の新規Runtime層追加は行わない)
2. RC-011 PHL Relay Client(`phios/phl/relay_client.py`)はcommit `9faa421`で正式資産化済み。MoCKAとの通信は`http://localhost:5002/mcp`と`http://localhost:5000/api/gate/audit`の2エンドポイントのみに限定されている(実測: relay_client.py内grep確認、MoCKA側モジュールのimportなし)
3. Integration Target(MoCKA/Memory/Orchestra/Relay、新規モジュール追加なし)・Integration Order(推奨: MoCKA→Memory→Relay→Orchestra、確定順序ではなく推奨)・Success Criteria は`DC_20260729_012`で承認済み
4. Gap-001(REJECTED状態不足)・Gap-002(Decision Ledgerフィールド不足)・Gap-003(Freshness閾値未確定)はPendingのまま維持されており、本Scope定義によって暗黙に解消しない

---

## 1. 対象ファイルパス(Confirmed、実測)

**PHI-OS Runtime側の接続箇所**
`phios/runtime/controller_core.py`, `event_runtime.py`, `adapter_runtime.py`, `memory_boundary.py`(いずれもMoCKA側モジュールのimportなし。実測確認済み)

**PHL Relay Client利用箇所**
`phios/phl/relay_client.py`(commit `9faa421`でSeal済み、23テスト)

**MoCKA側変更の有無**
対象外。`relay_client.py`はMoCKA本体の既存エンドポイント(`/mcp`、`/api/gate/audit`)を変更せず呼び出すのみ。MoCKA本体(`C:/Users/sirok/MoCKA/`のうち`PlanningCaliber/`を除く部分)には一切変更を加えない。

結論: 「MoCKA本体を変更するのか」「PHI-OS側だけで接続するのか」は後者。PHI-OS側のみで接続する。

---

## 2. 新規/変更範囲(Confirmed原則 + Proposal)

**確定(変更禁止、Confirmed)**
`controller_core.py` / `event_runtime.py` / `adapter_runtime.py` / `memory_boundary.py` は変更禁止(Runtime Foundation凍結、`DC_20260729_011`)。

**Proposal(未承認、Human Gate審議事項)**

Runtime FoundationからRC-011への接続を担う「Integration Adapter」という外側追加コンポーネントを想定している。

```
Runtime Foundation
        |
        +-- Integration Adapter (未実装、名称/配置は未確定)
              |
              +-- PHL Relay Client (RC-011, 既存)
```

**注記:** Integration Adapterは現時点で実在しない(`phios/`配下を検索し、該当ファイル無しを確認済み)。ファイル名・配置場所・責務境界は本文書では確定せず、別途のHuman Gate審議事項とする。

---

## 3. Test影響(Confirmed、実測)

| 区分 | テスト数 | 追跡状態 | 備考 |
|---|---|---|---|
| Runtime Foundation baseline | 242 | 追跡済み(git) | `DC_20260729_011`の根拠数値と一致(実測: `phios/runtime`配下36 + その他追跡済み206) |
| RC-011 (PHL Relay Client) | 23 | 追跡済み(git、commit `9faa421`) | |
| `phios/context_assembly` | 7 | **git未追跡** | Runtime Foundation baselineに算入されていない(§4 Out of Scope参照) |
| 合計(`pytest --collect-only`実測) | 272 | - | 242+23+7 |

成功基準(`DC_20260729_012` HG-MI-03を継承):
- 既存242テストへの回帰なし
- RC-011既存23テスト維持
- 新規MoCKA Integration Test追加(範囲は§2 Integration Adapter確定後に定義)

確認すべき内容(「接続できた」を成功条件にしない):
- 読み取り要求が正しい境界(`/mcp`、`/api/gate/audit`)を通ること
- 取得失敗時に誤った判断をしないこと(evidence insufficient扱い、`relay_client.py`既存実装で確認済み)
- Runtime State(`ControllerCore.state` / `EventRuntime.events`)を勝手に変更しないこと(`memory_boundary.py`のnon-interference原則を継承)

---

## 4. Out of Scope資産(Confirmed、観測済み・Scope外)

**`phios/context_assembly/`**

- 状態: git未追跡(untracked)。テスト7件を含む
- 理由:
  - 現在のIntegration Strategy(`DC_20260729_012`)のScopeにContext Assemblyは含まれていない
  - 未追跡状態であり、正式なEvidence Chain / Git Sealがまだない
  - 統合利用に対するHuman Gate承認が存在しない
  - Test結果はRuntime Foundation baseline(242)に含まれていない
- 扱い: 「存在しない」ではなく「観測済み・Scope外」として記録する。将来Scope Inに検討する場合は別途Human Gate審議を要する。

---

## 5. Gap影響(Confirmed、Pending維持)

- Gap-001(REJECTED状態不足): Pending維持。MoCKA接続によって解消しない
- Gap-002(Decision Ledgerフィールド不足): Pending維持
- Gap-003(Memory Freshness Threshold未確定): Pending維持

**明記事項:** MoCKA接続によってPHI-OS側に自動判断能力を追加しない。本Phaseの目的は「MoCKAの能力をPHI-OSが利用する」であり、「PHI-OSがMoCKA判断を代替する」ではない(`relay_client.py`のfail-closed設計、evidence insufficient扱いはこの原則を実装レベルで反映済み)。

---

## 6. 次工程

Human Gateにおいて`HG-MI-01〜03`と同様の枠組みで、本文書§2のIntegration Adapter設計(名称・配置・責務)について審議・承認を得た後、実装(CHANGE_START〜CHANGE_DONE〜Test Evidence〜Git Seal)に着手する。

---

## Knowledge Lineage

**Document:** PHI_MOCKA_INTEGRATION_SCOPE_PROPOSAL_v0.1.md
**Status:** PROPOSAL
**Created:** 2026-07-29
**Origin:** `DC_20260729_012`の次工程指定「最初の統合対象(MoCKA)のScope定義に4項目確認を経て着手する」を受けて作成。
**Parent Documents:** `DC_20260729_011`, `DC_20260729_012`, `docs/audits/PHI_RUNTIME_ARCHITECTURE_VALIDATION_v1.0.md`, `docs/audits/PHI_MODULE_INTEGRATION_STRATEGY_PROPOSAL_v0.1.md`(いずれもcommit `d69121b9e`でSeal済み)
**Derived From:** `DC_20260729_012`(統合対象・順序・成功条件の引用元)
**Supersedes:** なし
**Reason For Creation:** MoCKA統合実装着手前に、対象範囲・変更禁止範囲・Test基準・Gap非解消・Scope外資産をHuman Gate審議可能な形で固定するため。

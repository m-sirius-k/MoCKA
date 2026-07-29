# PHI Module Integration Strategy Proposal v0.1

**Status:** PROPOSAL(確定事項と審議事項を分離して記録。Decision Ledger登録はまだ行わない)
**位置づけ:** `DC_20260729_011`(HG-PHASE-V-01、Runtime Foundation Complete承認)後の、Module Integration Strategyに関する提案書。
**重要な構成方針(きむら博士指示)**: 「既にEvidenceで裏付けられた事実」と「これから意思決定する方針」を混在させない。前者は確定事項として、後者は未承認の提案として明確に分離する。

---

## 1. 確定事項(Evidence裏付け済み、Confirmed)

以下はすでに`DC_20260729_011`および`PHI_RUNTIME_ARCHITECTURE_VALIDATION_v1.0.md`により確定している事実であり、本文書によって新たに決定するものではない。

1. Runtime Foundation Completeを、Phase Vの到達点とする
2. Runtime Foundationは、Controller Core・Event Runtime・Adapter Runtime・Memory Boundaryの4要素で構成される
3. Runtime Foundationは、Architecture Validationにより「一方向依存・循環依存なし」「242テストによる裏付け」が検証済みである
4. Runtime Foundationは凍結対象とし、V-06以降で新たな汎用Runtime層は追加しない
5. Gap-001(REJECTED状態不足)・Gap-002(Decision Ledgerフィールド不足)・Gap-003(Freshness閾値未確定)はPendingのままとし、暗黙に解消しない

---

## 2. Human Gateで審議・承認を求める事項(未承認、Proposal)

以下はいずれも**「提案」であり「承認済み」ではない**。実際の採否は別途のHuman Gate判断を経る。

### HG-MI-01: 統合対象(提案)

Phase I〜Vで定義済みの4モジュールのみを対象とし、新規モジュールは追加しない。

```
PHI-OS
 +-- MoCKA
 +-- Memory
 +-- Orchestra
 +-- Relay
```

### HG-MI-02: 統合順序(推奨順序、未承認)

**この順序は設計上の推奨であり、Human Gateでの審議・承認前の段階である。**

| 順位 | モジュール | 推奨理由(未承認の設計判断) |
|---|---|---|
| 1 | MoCKA | read-only境界・Evidenceの考え方が既に整理されており、接続対象として最も成熟している |
| 2 | Memory | V-05でMemory Boundaryが完成しており、将来のSnapshot取得元として接続できる |
| 3 | Relay | モジュール間通信を担うため、個々の接続が固まってから統合した方が責務が明確になる |
| 4 | Orchestra | 複数モジュールを調停・協調させる層であり、個別モジュールが接続された後に統合するのが自然 |

**注記**: 将来、別の順序がより合理的と判断された場合でも、この記録は「推奨案の提示」であって「決定の記録」ではないため、記録との整合性は保たれる。

### HG-MI-03: 統合成功条件(提案)

- 各モジュールが定義済みの境界のみを通じて接続される
- Runtime Foundationの責務分離を維持する
- 新たな循環依存を導入しない
- 既存テストが回帰しない
- Module統合用テストが追加される
- EvidenceとCommit/Sealが各段階で残される

### 参考: HG-MI-04相当(境界維持事項)

きむら博士の当初整理では境界維持事項として提示されたが、内容を精査した結果、これは§1の確定事項4・5(Runtime Foundation凍結、Gap-001〜003 Pending維持)および既存のModule Interface Contract(S06/P2-02、公開インターフェース経由のみの接続)と実質的に重複するため、**新たな審議事項としては扱わず、確定事項の再確認としてのみ位置づける**。

---

## 3. 次工程

HG-MI-01〜03(統合対象・統合順序・成功条件)についてHuman Gateの判断が得られた後、最初の統合対象(現時点の推奨: MoCKA)のScope定義に、これまで通り4項目確認(対象ファイルパス/新規・変更範囲/Test影響/Gap影響)を経てから着手する。

---

## Knowledge Lineage

**Document:** PHI_MODULE_INTEGRATION_STRATEGY_PROPOSAL_v0.1.md
**Status:** PROPOSAL
**Created:** 2026-07-29
**Origin:** `DC_20260729_011`後、きむら博士より確定事項と審議事項を分離した記録の指示を受け作成。
**Parent Documents:** DC_20260729_011、docs/audits/PHI_RUNTIME_ARCHITECTURE_VALIDATION_v1.0.md
**Derived From:** DC_20260729_011(確定事項の引用元)
**Supersedes:** なし
**Reason For Creation:** Evidence裏付け済みの事実と、これから意思決定する方針を混在させず、監査上追跡しやすい形で記録するため。
**Affected Components:** MoCKA/Memory/Orchestra/Relay統合戦略(未着手)
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。確定事項5件、審議事項3件(HG-MI-01〜03)、HG-MI-04相当の重複整理、次工程を記載。Decision Ledger登録は無し。

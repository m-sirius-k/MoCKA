# PHI Authority Model Proposal v0.1

**Status:** PROPOSAL(3案比較。Decision Ledger登録前段階)
**位置づけ:** `PHI_AUTHORITY_FLOW_ANALYSIS_v0.1.md`の続き。DC-PHI-ID-002(裁定Decision)に先立ち、Authority Model候補を定義する。
**実装・リネーム・Decision Ledger登録:** 本文書には一切含まない。
**確認済みの前提**: DC-PHI-ID-001(Identity/Alias採用)と本Proposalは別問題である。前者は「何と呼ぶか」、本文書は「誰が最終Authorityを持つか」を扱う。

---

## 1. 3モデル比較表

| 項目 | Model A | Model B | Model C |
|---|---|---|---|
| 名称 | Constitution Authority Model | Runtime Governance Model | 統合候補(PHI-Con/Core/HAB階層モデル) |
| 構造 | PHI-Con → MoCKA全体(統治) | MoCKA Governance Runtime → PHI-Core(外部保証) | PHI-Con → PHI-Core → PHI-HAB(直列階層、仮説) |
| 根拠文書 | `PHI_OS_CONSTITUTION_v1.md` | `PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md`、`PHIOS_CORE_CANONICAL_DESIGN_v1.md`、`PHI-OS_Concept_Memo.md`(非公式) | 一次資料からの直接記述なし。DC-PHI-ID-001のResponsibility Classificationから構造的に類推した設計仮説 |
| 制度上の位置づけ | RATIFIED v1(制度上位文書、2026-06-16) | Human Gate承認済み(DC_20260728_003、2026-07-28)、ただし根拠は非公式構想メモ | 未検証。Decisionでもなく、一次資料の直接確認対象でもない |
| 特徴 | 「制度上の正当性を決める層」 | 「Runtime実行を保証する層」 | 「命名分類(Alias)を階層構造として読み替えた場合の見え方」 |

---

## 2. 各モデル詳細

### Model A: Constitution Authority Model

`PHI_OS_CONSTITUTION_v1.md`第1章1.1(原文、`PHI_AUTHORITY_FLOW_ANALYSIS_v0.1.md`§2で確認済み)を根拠とする。PHI-Con(PHI-REG-01)がMoCKA全体を統治する制度執行機関であり、Event/Knowledge/Gate/Version/Verification/Institution Authorityの6 Authorityを保持する。制度上唯一のRATIFIED文書。

### Model B: Runtime Governance Model

`PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md`(DC_20260728_003)を根拠とする。MoCKA Governance Runtime(`phi_os/event_gate.py`等)がPHI-Core(phios/+ise/+phi_os_core.py)の動作を外部から保証する、対等・非包含の関係。`PHI_AUTHORITY_FLOW_ANALYSIS_v0.1.md`§2で確認済みの通り、この整理の正当性根拠はConstitution本文ではなく非公式な`PHI-OS_Concept_Memo.md`に依拠している。

### Model C: 統合候補(PHI-Con/Core/HAB階層モデル)

```
PHI-Con(制度Authority)
   |
   v
PHI-Core(実行構造)
   |
   v
PHI-HAB(接続・協調)
```

**明記すべき事実**: このモデルは、DC-PHI-ID-001(DC_20260729_008)が確定させたResponsibility Classification(Alias)を、統治の階層構造として読み替えたものであり、**Model A・Model Bのいずれの直接的な合成でもない**。

- Model Aは「PHI-Con → MoCKA全体」であり、「PHI-Con → PHI-Core」という直接記述は一次資料に存在しない。
- Model Bは「MoCKA Governance Runtime → PHI-Core」であり、「PHI-Con → PHI-Core」ではない。「MoCKA Governance Runtime」がPHI-Con(Constitution定義のPHI-OS)と同一実体かどうかは`PHI_AUTHORITY_FLOW_ANALYSIS_v0.1.md`§3(b)でUnknownのまま残されている。
- したがってModel Cは、既存2モデルのいずれからも直接導出されていない**新たな設計仮説**であり、一次資料による裏付けを持つ確定事項ではない。

---

## 3. Evidence対応表

| Model | 直接一次資料 | 一次資料に存在しない部分 |
|---|---|---|
| A | `PHI_OS_CONSTITUTION_v1.md`第1章・第3章 | PHI-Core/PHI-HABという語・実体への言及(0件) |
| B | `PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md`§0・§1、`PHIOS_CORE_CANONICAL_DESIGN_v1.md` | Constitution本文条項への参照(0件、既報告済み) |
| C | なし(DC-PHI-ID-001からの構造的類推のみ) | PHI-Con→PHI-Coreの直接統治関係を記す一次資料そのもの |

---

## 4. 未解決点

1. Authority方向(a): PHI-ConとPHI-Coreの上下関係を直接論じた一次資料が存在しない(`PHI_AUTHORITY_FLOW_ANALYSIS_v0.1.md`§3(a)より継続)
2. 別レイヤーか(b): 「MoCKA Governance Runtime」とPHI-Conの同一性が未確認(同§3(b)より継続)
3. MoCKA範囲の二義性(c): Model Aの「MoCKA=制度体系全体」とModel Bの「MoCKA=Governance Runtime(特定サブシステム)」が同じ語で異なる範囲を指している(同§3(c)より継続)
4. Model C自体の妥当性: 一次資料による直接確認を経ていない設計仮説であり、Model A/Bと同列の「確定した記述」としては扱えない

---

## 5. Decision対象外(本文書・次のDC-PHI-ID-002いずれでも今回決めない事項)

- Model A/B/Cのいずれを正式採用するかの最終裁定
- 「MoCKA」という語の公式スコープ定義の変更
- `PHI_OS_CONSTITUTION_v1.md`本文の改定
- 既存Decision(DC_20260728_002、DC_20260728_003、DC_20260729_001、DC_20260729_008)の変更・撤回
- PHI-REG-04(Compliance Issue)の扱い(別トラックのまま)

---

## Knowledge Lineage

**Document:** PHI_AUTHORITY_MODEL_PROPOSAL_v0.1.md
**Status:** PROPOSAL
**Created:** 2026-07-29
**Origin:** PHI_AUTHORITY_FLOW_ANALYSIS_v0.1.md確認後、きむら博士よりDC-PHI-ID-002に先立つAuthority Model候補定義の指示を受け作成。
**Parent Documents:**
- PHI_AUTHORITY_FLOW_ANALYSIS_v0.1.md
- PHI_OS_CONSTITUTION_v1.md
- docs/consolidation/PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md(workshop/phi-os/)
- docs/consolidation/PHIOS_CORE_CANONICAL_DESIGN_v1.md(workshop/phi-os/)
- DC_20260729_008(DC-PHI-ID-001)
**Derived From:** PHI_AUTHORITY_FLOW_ANALYSIS_v0.1(Model A/B並記・未解決点の継承元)
**Supersedes:** なし
**Reason For Creation:** DC-PHI-ID-002(Authority Flow Resolution)のDecision化に先立ち、Model A/B/Cを比較可能な形で提示し、Decision対象外事項を明示することで、次のHuman Gate判断の範囲を限定するため。
**Affected Components:** PHI-REG-01、PHI-REG-02(a)(b)、DC_20260728_002、DC_20260728_003、DC_20260729_008
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。Model A/B/C比較表・Evidence対応表・未解決点・Decision対象外を記載。Decision化・実装・リネームは無し。

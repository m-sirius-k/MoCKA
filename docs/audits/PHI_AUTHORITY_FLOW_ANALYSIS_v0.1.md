# PHI-Con / PHI-Core Authority Flow Analysis v0.1

**Status:** DRAFT(Analysis。Decision Ledger登録前段階)
**位置づけ:** DC-PHI-ID-001(DC_20260729_008、Identity/Alias採用)確定後の次フェーズ。「何と呼ぶか」ではなく「誰が誰を統治するか」を評価する。
**実装・リネーム・Decision Ledger登録:** 本文書には一切含まない。

---

## 1. 対象Evidence

- `PHI_OS_CONSTITUTION_v1.md`(2026-06-16、RATIFIED v1)
- `PlanningCaliber/workshop/phi-os/docs/consolidation/PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md`(2026-07-28)
- `PlanningCaliber/workshop/phi-os/docs/consolidation/PHIOS_CORE_CANONICAL_DESIGN_v1.md`(2026-07-28)
- `docs/audits/PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1.md`(2026-07-29)
- `DC_20260728_002`(Canonical PHI-OS Core確定)
- `DC_20260728_003`(PHI-OS/MoCKA Boundary確定、判定区分E)
- 参考(RC-008が引用する非公式資料): `Desktop/PHI-OS_Concept_Memo.md`(作成日不明、RC-008系がここから「役割分担が一致する」と主張)

---

## 2. 現行2モデルの並記(原文引用)

### Model A: Constitution系

出典: `PHI_OS_CONSTITUTION_v1.md`第1章1.1(原文)
> 「PHI-OS(Persistent History Intelligence OS)は、MoCKA全体の**唯一の制度執行機関(Institutional Authority)**である。」

構造:
```
PHI-Con(=PHI-REG-01)
   |
   v (統治)
MoCKA全体
```

第3章ではEvent/Knowledge/Gate/Version/Verification/Institution Authorityの6 Authorityを、PHI-Con(当時の呼称でPHI-OS)自身が保持すると定める。制定日2026-06-16、Status: RATIFIED v1(本文書内で唯一「制度上位」と明示された文書)。

### Model B: RC-008系

出典: `PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md`§0(DC_20260728_003、原文)
> 「E. External Governance Runtime — PHI-OSとMoCKAは同一階層の候補(どちらがCanonicalか)ではなく、そもそも別レイヤーである。MoCKAはPHI-OSの部品ではなく、PHI-OSが正しく動作していることを保証する外部制度層として位置づける。」

構造:
```
MoCKA Governance Runtime(phi_os/event_gate.py等)
   |
   v (外部から動作を保証、対等/非包含)
PHI-Core(=PHI-REG-02(b)、phios/+ise/+phi_os_core.py)
```

制定日2026-07-28、承認: きむら博士(DC_20260728_003)。

**根拠の出所についての事実(Confirmed)**: `PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md`§7はこの整理の妥当性を「当初のPHI-OS構想メモにおける役割分担(PHI-OS: 知的シーケンサー / MoCKA: Runtime Governance / Memory: Institutional Memory / Orchestra: 協調制御 / Relay: 状態同期)と一致する」と述べている。この「構想メモ」は`Desktop/PHI-OS_Concept_Memo.md`を指すと考えられ(前回セッションで内容確認済み)、`PHI_OS_CONSTITUTION_v1.md`ではない。**RC-008系4文書のいずれにもConstitution本文条項への直接参照は存在しない(grep 0件、既報告済み)。** つまりModel Bは非公式な構想メモとの整合を根拠にしており、RATIFIED制度憲法であるConstitutionそのものとの整合確認は行われていない。

---

## 3. 判断対象ごとの評価

### (a) PHI-ConとPHI-Coreは上下関係か

**Pending Resolution。**

Model Aの文言(「MoCKA全体の唯一の制度執行機関」)からは、PHI-Con配下にMoCKAの全構成要素(PHI-Core相当のものを含む)が入るという解釈が構造的には成り立つが、Constitution本文はPHI-Coreという語・`phios/`/`ise/`という実体に一切言及しておらず、直接の上下関係の記述はない。
Model Bは「MoCKA(Governance Runtime)がPHI-Coreを外部から保証する」という記述のみで、これも上下関係というより非対称な保証関係であり、明確な「統治する/される」の言明ではない。
**両モデルとも、PHI-ConとPHI-Coreという2つの名称を直接並べて上下関係を論じた一次資料は存在しない。** RC-008は「PHI-Con」という語自体を一度も使用していない(本Aliasは2026-07-29のDC-PHI-ID-001で導入されたばかりである)。

### (b) PHI-ConとPHI-Coreは別レイヤーか

**Unknown(判定保留の理由: 参照対象のズレ)。**

DC_20260728_003が「別レイヤー」と宣言しているのは、正確には「MoCKA(Governance Runtime)」と「PHI-OS(Core)」の関係であり、「PHI-Con」という語は登場しない。「MoCKA Governance Runtime」の実装物(`phi_os/event_gate.py`等)は、Constitutionが定義するEvent Authority/Gate Authorityの実装物(root`phi_os/`パッケージ、Constitutionと同日2026-06-16にgit初出、既存監査で確認済み)と物理的に同一である可能性が高い。もしこれが同一実体であれば、DC_003が「別レイヤー」と呼んでいるものの少なくとも一方(MoCKA Governance Runtime)は、実質的にPHI-Con自身(またはその執行部分)である可能性がある。この同一性の確認自体が行われていない。

### (c) MoCKAはPHI-Con内部か外部Runtimeか

**Contradicted寄り(ただし参照範囲の不一致により確定はできない)。**

- Model A: 「PHI-Con=MoCKA全体の制度執行機関」という文言は、PHI-ConがMoCKAという制度の**内部**にあってその頂点に立つ、という包含関係を示している(PHI-ConはMoCKAの一部でありながら最高権威を持つ、という構造)。
- Model B: 「MoCKAはPHI-OSの部品ではなく外部制度層」という文言は、MoCKAをPHI-OS(Core)の**外側**に置く。

この2つの文は、「MoCKA」という語が指すスコープが同一である場合には方向が逆転しており矛盾するが、Model Aの「MoCKA全体」(文明モデル全体)とModel Bの「MoCKA」(Governance Runtimeという特定サブシステムのみ)が異なるスコープを指している可能性があり、その場合は文字通りの矛盾ではなく単に別の対象を語っているだけになる。**このスコープの異同はいずれの資料でも明示的に検討されておらず、Unknownのまま残る。**

### (d) PHI-HAB/Orchestra/Relay/Memoryはどの層に接続するか

**Confirmed(既存監査により部分的に確定済み)。**

`MOCKA_PHI_OS_IDENTITY_AUDIT_v1.md`§6の確定事項:
- PHI-REG-02(PHI-HABの親Registry)のみがOrchestra/Relay/Memoryと直接の制度的・技術的連結を持つ(`PHI-OS_Core_Spec_v1.0_addendum.md`のnode_id命名規則、`extension/adapters/*.js`が実コードとして存在)
- PHI-REG-01(PHI-Con)はOrchestra/Relay/Memoryと直接連結しない(Constitution本文に言及なし)

したがって、**PHI-HABはOrchestra/Relay/Memoryの直接接続層であり、PHI-Conはこの3製品と直接の制度的関係を持たない、という点はConfirmed**。一方、PHI-Core(phios/+ise/+phi_os_core.py)がOrchestra/Relay/Memoryとどう接続するか(あるいは接続しないか)は、RC-008系4文書のいずれにも記述がなくUnknown。

---

## 4. 総括

| 判断対象 | 判定 |
|---|---|
| (a) PHI-Con/PHI-Core上下関係 | Pending Resolution(直接論じた一次資料なし) |
| (b) 別レイヤーか | Unknown(「MoCKA Governance Runtime」とPHI-Conの同一性未確認) |
| (c) MoCKAは内部/外部か | Contradicted寄り、ただしスコープ不一致の可能性がありUnknown | 
| (d) PHI-HAB等の接続層 | Confirmed(PHI-HABのみ直接接続、PHI-Conは非接続。PHI-Coreは不明) |

**中心的な未解決事項(Pending Resolution)**: Model Bの正当性は、RATIFIED Constitutionではなく非公式なConcept Memo(構想メモ)から引かれている。この根拠の非対称性(Constitution=制度上位文書 vs Concept Memo=非公式構想文書)を解消しない限り、Model A/Bのどちらを優先すべきかという判断自体が成立しない。また「MoCKA Governance Runtime」(DC_003)とPHI-Con(Constitution)が同一実体を指すか否かの確認が、(a)(b)(c)いずれの判断保留にも共通する前提条件になっている。

---

## Knowledge Lineage

**Document:** PHI_AUTHORITY_FLOW_ANALYSIS_v0.1.md
**Status:** DRAFT
**Created:** 2026-07-29
**Origin:** DC-PHI-ID-001(DC_20260729_008)確定後、Authority Flow(統治関係)の評価をきむら博士より指示され作成。
**Parent Documents:**
- PHI_OS_CONSTITUTION_v1.md
- docs/consolidation/PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md(workshop/phi-os/)
- docs/consolidation/PHIOS_CORE_CANONICAL_DESIGN_v1.md(workshop/phi-os/)
- docs/audits/PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1.md
- docs/audits/MOCKA_PHI_OS_IDENTITY_AUDIT_v1.md
**Derived From:** PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1(Authority Flow Pending Resolution項目の継承元)
**Supersedes:** なし
**Reason For Creation:** DC-PHI-ID-002(Authority Flow Resolution)のDecision化に先立ち、現行2モデルをEvidenceとして並記し、判断対象ごとの現状を確定させるため。
**Affected Components:** PHI-REG-01、PHI-REG-02(a)(b)、DC_20260728_002、DC_20260728_003、DC_20260729_008
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。Model A/B並記、4判断対象の評価、Pending Resolution事項を記載。Decision化・実装・リネームは無し。

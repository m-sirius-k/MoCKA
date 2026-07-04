# Cross Reference Decision Brief v0.1 (Decision-02)

位置づけ: R01 Decision Preparation指示書v1.0 Decision-02に基づく。入力資料は`CROSS_REFERENCE_ANALYSIS_v0.1.md`(Analysis-02)のみとし、新規調査は行っていない。本文書は博士の裁定に必要な資料を整理するものであり、採択・却下・優先順位付け・修正案・実装案の提示、および裁定の代行は一切行わない。

---

## 1. Analysis要約

Analysis-02(入力: CROSS_REFERENCE_AUDIT_AND_GIT_STATUS_v0.1.md)で確認された内容は以下の通り。

- Human Gate監査シリーズ10件(2026-06-24/25作成)は、VOCABULARY_CONSTITUTION_v0.1.md(2026-07-03作成)より約8〜9日前に既に存在していた。
- KN-002・KN-003・TERM-001は「参照文書」相当の独立節を持つ。KN-001、KN-004〜007、VOCABULARY_CONSTITUTION_v0.1には同節が存在しない。
- 既存記録は「KN-001/002/003/TERM-001は同じ様式」と記載しているが、直接確認するとKN-001にはその節が存在しなかった。
- 参照関係はすべて「後発文書が先行文書を引用する」一方向のみであり、逆方向の参照追加は確認されなかった。相互参照(AとBが互いを引用し合う関係)は1件も観測されていない。
- 参照文書節の欠落は、KN-004以降4文書連続で構造的に生じている(KN-001〜003・TERM-001とは異なる特徴)。
- REGISTRY_SCHEMA_v1.0.mdの物理的重複(正本配置コミットの存在にもかかわらずPlanningCaliber/fp側が更新されない)と、KN-004以降の参照文書節欠落は時期的に近接している。
- REGISTRY_STATE_MODEL_v1.0.md(KN-006)§5.1「Human Gate Boundary」は`phi_os/human_gate.py`を実装参照先として明記するが、Human Gate監査シリーズおよび`semantic/query_engine/human_gate.py`には言及していない。
- VOCABULARY_CONSTITUTION_v0.1.md:110の記述(「human_gate.py自体は単一実装」)と、先行するHuman Gate監査シリーズの記述(「Human Gateという名称が複数の分類にまたがる」)との間には文言上の不一致が存在する。この不一致は「誤り」と断定されておらず、参照の有無自体が文書内から確認できないため、参照した上での判断か未参照によるものかは判別されていない。

## 2. 博士裁定事項

- Cross Reference Analysis(Analysis-02)を正式採択するか。
- Reference Completeness(参照完全性)を正式評価軸として採用するか。
- Cross Reference Auditを独立シリーズとするか。
- VOCABULARY_CONSTITUTION_v0.1.md:110の記述内容について、Constitution記述の確認を正式レビュー対象とするか。
- KN-004〜007、およびKN-001への「参照文書」節の追加要否。
- VOCABULARY_CONSTITUTION_v0.1.mdとHuman Gate監査シリーズとの間の記述の不一致を、どちらの記述を優先するか・両論併記とするか等、どう扱うか。
- REGISTRY_SCHEMA_v1.0.mdの物理的重複について、正本配置コミットの意図をPlanningCaliber/fp側にも反映するかどうか。

## 3. 判断後の影響範囲

- Registry Series文書群(KN-001〜KN-007・TERM-001)の様式統一。
- VOCABULARY_CONSTITUTION_v0.1.mdの正本性、およびHuman Gate監査シリーズとの記述関係。
- REGISTRY_SCHEMA_v1.0.md(docs/governance側・PlanningCaliber/fp側)の正本管理。

## 4. 未判断事項

- KN-001に「参照文書」節が存在しない理由(既存記録との食い違いの原因)は未確認。
- VOCABULARY_CONSTITUTION_v0.1.md:110の記述が、Human Gate監査シリーズを参照した上での記述か、参照せずに書かれた記述かは、文書内に出典記載がないため判別できない。
- KN-004〜007に「参照文書」節がない状態が、シリーズ設計上の意図(Scope Freezeの一部としての省略等)によるものか、単純な作成時の見落としかは判別できない。
- 相互参照が0件であることが、本監査が扱った文書群以外のMoCKA制度文書全体でも一般的な傾向かどうかは確認されていない。

---

## 改訂履歴

- v0.1(2026-07-04): R01 Decision Preparation指示書v1.0 Decision-02に基づき新規作成。入力資料はCROSS_REFERENCE_ANALYSIS_v0.1.mdのみ。くろこ起草。

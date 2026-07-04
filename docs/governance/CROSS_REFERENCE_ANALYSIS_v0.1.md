# Cross Reference Analysis v0.1 (Analysis-02)

位置づけ: R01分析指示書v1.0 Analysis-02に基づく。入力資料は`CROSS_REFERENCE_AUDIT_AND_GIT_STATUS_v0.1.md`のみとし、新規調査は行っていない。分析軸はReference Completeness（参照完全性）: 文書間参照・相互参照・一方向参照・参照欠落・Constitutionとの整合性。VOCABULARY_CONSTITUTION_v0.1.mdの記述を「誤り」とは断定せず、確認された事実との不整合の有無のみを整理する。制度判断は行わない。他のAnalysis（Vocabulary Audit／CI Failure）とは独立に扱い、それらの結論をここでの分析根拠として用いていない。

---

## 1. 確認できた事実（Cross Reference Audit Fact Collectionより、要約引用）

- Human Gate監査シリーズ10件（2026-06-24/25作成）は、VOCABULARY_CONSTITUTION_v0.1.md（2026-07-03作成）より約8〜9日前に存在していた。
- KN-002（CATEGORY_REGISTRY_v2.0）・KN-003（REGISTRY_RECORD_SPEC）・TERM-001は「参照文書」相当の独立節を持つ。KN-001（REGISTRY_CHARTER）・KN-004〜007（SCHEMA/SEMANTICS/STATE_MODEL/VALIDATION）・VOCABULARY_CONSTITUTION_v0.1には同節が存在しない。
- 既存記録（REGISTRY_SERIES_V1_1_CANDIDATE）は「KN-001/002/003/TERM-001は同じ様式（参照文書節を持つ）」と記載しているが、直接確認するとKN-001にはその節が存在しなかった。
- REGISTRY_STATE_MODEL_v1.0.md（KN-006）§5.1「Human Gate Boundary」は`phi_os/human_gate.py`を実装参照先として明記するが、Human Gate監査シリーズおよび`semantic/query_engine/human_gate.py`には言及していない。
- VOCABULARY_CONSTITUTION_v0.1.md:110「内部下位区分｜特になし（human_gate.py自体は単一実装だが、接続元は複数存在し断片的に接続されている）」という記述が存在する。
- `docs/governance/REGISTRY_SCHEMA_v1.0.md`の2件目コミットは「正本配置(Human Approval Gate承認済み)」と明記しているが、`PlanningCaliber/fp/REGISTRY_SCHEMA_v1.0.md`は初回コミット以降更新されておらず、現在も同一内容で残存している。

## 2. 事実から導かれる分析（Reference Completeness の観点）

### 2-1. 参照の方向性: 一方向・後方引用のみ

KN-002→KN-001、KN-003→KN-001/002/TERM-001、TERM-001→KN-001/002という参照関係はいずれも「後発文書が先行文書を引用する」一方向のみであり、逆方向（先行文書が後発文書を更新して参照を追加する）は確認されなかった。これはTERM-001が明記する「KN-001・KN-002への遡及編集は行わない」という設計方針と整合的であり、一方向参照はこのシリーズにおいて偶発的な欠落ではなく、明示された運用方針の帰結として観測できる。

### 2-2. 参照完全性がシリーズ途中（KN-004）で途切れる

KN-001〜003・TERM-001では「参照文書」節の有無に一部ばらつきがある（KN-001に節がなく、KN-002/003/TERM-001にはある）ものの、KN-004以降は4文書連続で当該節自体が存在しない。参照完全性は特定の1文書ではなく、KN-004以降という範囲全体で構造的に欠落している。

### 2-3. 相互参照（Mutual Reference）は一件も確認されていない

本Fact Collectionで確認された参照関係は、すべて「AがBを引用する」という片方向の記載であり、「AとBが互いを引用し合う」相互参照は1件も観測されていない。KN-006§5.1のように、内容上はHuman Gate監査シリーズと強い関連を持つ節（同一の対象・同時期以降に作成）であっても、相互参照どころか一方向の参照even追加されていない事例が確認された。

### 2-4. 参照欠落と正本重複の共起

REGISTRY_SCHEMA_v1.0.mdの物理的重複（正本配置コミットの存在にもかかわらずPlanningCaliber/fp側が更新されない）と、KN-004以降の参照文書節の欠落は、時期的に近接している（KN-004の初回作成2026-07-01、正本配置コミット2026-07-02、参照文書節の欠落はKN-004からKN-007まで一貫）。参照の仕組み（どの文書が正本かを明示する仕組み）と、正本管理の実務（複製の解消）が、同じ時期に同様に手薄になっているという共起が観測される。

### 2-5. Constitution（VOCABULARY_CONSTITUTION_v0.1.md）との整合性

VOCABULARY_CONSTITUTION_v0.1.md:110の記述「human_gate.py自体は単一実装」について、本分析ではこれを「誤り」とは断定しない。確認できる事実との関係を整理すると以下の通りである。

- 本文書が作成された2026-07-03時点で、Human Gate監査シリーズ（`docs/audits/MOCKA_HUMAN_GATE_REGISTRY_AUDIT_v1.md`等、2026-06-25作成）は既に存在しており、そこでは「Human Gateという名称が複数の分類（HG-REG-01〜04）にまたがる」という所見が記録されていた。
- VOCABULARY_CONSTITUTION_v0.1.mdの当該記述と、既存の先行文書（Human Gate監査シリーズ）の記述内容との間には、文言上の不一致が存在する。
- この不一致が、VOCABULARY_CONSTITUTION_v0.1.md作成時に先行文書を参照しなかったことによるものか、参照した上で異なる評価に至ったものかは、本Fact Collectionの範囲では判別できない（該当する参照文書節・出典記載がないため、参照の有無自体を文書内から確認できない）。

## 3. 未確認事項

- KN-001に「参照文書」節が存在しない理由（既存記録が「同じ様式」と述べていることとの食い違いの原因）は未確認。
- VOCABULARY_CONSTITUTION_v0.1.md:110の記述が、Human Gate監査シリーズを参照した上での記述か、参照せずに書かれた記述かは、文書内に出典記載がないため判別できない。
- KN-004〜007に「参照文書」節がない状態が、シリーズ設計上の意図（例: Scope Freezeの一部としての省略）によるものか、単純な作成時の見落としかは、Fact Collectionの範囲では判別できない。
- 相互参照が0件であることについて、MoCKAの制度文書全体（本監査が扱った文書群以外）でも同様の傾向が一般的かどうかは確認していない。

## 4. 博士判断が必要な事項

- KN-004〜007への「参照文書」節の追加、およびKN-001への追加要否は、Registry Series文書の様式統一に関わる制度運営上の判断であり、本分析の範囲を超える。
- VOCABULARY_CONSTITUTION_v0.1.mdとHuman Gate監査シリーズとの間の記述の不一致（2-5）をどう解消するか（どちらの記述を優先するか、両論併記とするか等）は、制度文書の正本性に関わる判断であり、本分析では行わない。
- REGISTRY_SCHEMA_v1.0.mdの物理的重複（2-4）について、正本配置コミットの意図をPlanningCaliber/fp側にも反映するかどうかは、実装・運用上の判断であり本分析の範囲を超える。

---

## 改訂履歴

- v0.1（2026-07-04）: R01分析指示書v1.0 Analysis-02に基づき新規作成。入力資料はCROSS_REFERENCE_AUDIT_AND_GIT_STATUS_v0.1.mdのみ。くろこ起草。

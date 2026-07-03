# Guarantee Matrix Audit v0.1

位置づけ: 博士指示（2026-07-03、Task-H）に基づき新規作成。MoCKA・PHI-OS・Orchestra・Relay・Memoryで使用される主要概念を「何を保証するための仕組みか」という機能的な観点で棚卸しする監査文書。

本監査は同日先行して行った`CONCEPT_AUDIT_v0.1.md`（構造的な重複＝「実装が同じか」の監査）や`VOCABULARY_PATTERN_AUDIT_CRITERIA_v0.1.md`（4観点による重複判定基準）とは軸が異なる。あちらは「実装として同一か」を問うたが、本監査は「同じ約束（保証）を果たそうとしているか」を問う。実装が別物でも保証が重複することはあり得るし、実装が別物であることが直ちに保証の非重複を意味しない。

本ファイルはコードではなく監査文書である。v0.1とし、実装・コード変更は一切含まない。新規のコード調査は行わず、本日までに作成済みの以下の文書、および事前に確認済みの既存ガバナンス文書の記載を再構成した分析である。

- `docs\governance\CONCEPT_AUDIT_v0.1.md`
- `docs\caliber\CALIBER_TO_SKILL_MD_GAP_ANALYSIS_v0.1.md`
- `docs\governance\WRITER_CHECKER_INSTITUTIONAL_DESIGN_v0.1.md`
- `docs\caliber\LOOP_HEALTH_INDEX_DESIGN_v0.1.md`
- `docs\governance\VOCABULARY_PATTERN_AUDIT_CRITERIA_v0.1.md` / `_TARGET_LIST_v0.1.md`
- `docs\governance\DECISION_POLICY_v0.1.md` / `ACTIVATION_POLICY_v0.1.md` / `gl7_execution_kernel_spec_v1.md` / `LOOP_DESIGN_PRINCIPLES.md`
- `MOCKA_OVERVIEW.json`のConstitution節

---

## 第1部: 現状把握

### 1.1 MoCKA Constitutionが明示する根本保証

`MOCKA_OVERVIEW.json`のConstitutionには以下5項目が明記されている。これが本監査における保証類型の出発点になる。

1. Event ledger is append only（イベント台帳は追記専用である）
2. All decisions preserve 5W1H（すべての決定は5W1Hを保持する）
3. Infield is internal memory（Infieldは内部記憶である）
4. Outfield is collaborative interface（Outfieldは協働インターフェースである）
5. Event history is the single source of truth（イベント履歴が単一の真実の源である）

これらに加え、本日までの調査で確認された派生的な保証主張（Human-First原則、GL7のDefault Deny、Decision Policyの責務境界等）を合わせて、以下の10種の保証類型に整理する。

### 1.2 保証類型（10種、本監査での作業分類）

| 記号 | 保証類型 | 意味 |
|---|---|---|
| G1 | 存在保証 | システム内に何が存在するかが把握・検索可能である |
| G2 | 不変性・改ざん検知保証 | 一度記録された情報は不当に書き換えられない、または書き換えられれば検知される |
| G3 | 網羅性保証 | 行われた作業・判断はすべて記録される（「記録なき作業は存在しない」） |
| G4 | 実行前安全性保証 | 危険な実行は行われる前に止められる |
| G5 | 人間最終決定保証 | 最終的な承認・決定は必ず人間が行う |
| G6 | 暴走・停滞検知保証 | 制御不能な自己拡張、または見かけ上の作業で進捗がない状態が検知される |
| G7 | 品質・妥当性保証 | 生成物が一定の基準を満たすことが確認される |
| G8 | 単一正本保証 | 同じ情報について複数の食い違う正本が並立しない |
| G9 | 権限分離保証 | 判定・実行・記録・承認の権限が別主体に分かれ、一つの主体が全権を持たない |
| G10 | 文脈・経験継承保証 | セッション・時間を超えて必要な文脈が失われない |

この10分類は本監査のための作業分類であり、MoCKA公式の分類として確定しているものではない（要確認）。

### 1.3 概念/機構ごとの保証主張の棚卸し

| 概念/機構 | 主張している保証 | 出典 |
|---|---|---|
| Ledger（ledger.json / mocka_events.db+audit_trigger.py / decision_ledger.jsonl(PHI-OS) / KN_SERIES_LEDGER） | G2（不変性）、G3（網羅性） | CONCEPT_AUDIT_v0.1.md 1.2節、Constitution原則1 |
| Registry（KN-004等） | G1（存在） | CONCEPT_AUDIT_v0.1.md 1.1節 |
| Catalog（MODULE_CATALOG_v1等） | G1（存在）、G8（索引の一貫性という意味での単一正本） | CONCEPT_AUDIT_v0.1.md 1.4節 |
| Archive（TIC/Phase/Module） | G2の派生（凍結後の不変性）、TIC Archiveのみ本来はG1寄り（採用履歴の保管） | CONCEPT_AUDIT_v0.1.md 1.4節、3.1節 |
| Memory（Memory拡張/Infield/working_memory.py/Knowledge Assets） | G10（文脈継承） | CONCEPT_AUDIT_v0.1.md 1.3節 |
| Approval（Human Gate/phi_os/human_gate.py、Decision Policyのescalate_if_needed()、LOOP_DESIGN Human-First原則、ACTIVATION_POLICYのReview Gate） | G5（人間最終決定）、G9（権限分離） | DECISION_POLICY_v0.1.md、LOOP_DESIGN_PRINCIPLES.md、ACTIVATION_POLICY_v0.1.md |
| Loop Health（LOOP_DESIGN 3制約/DRIFT_STANDARD/Loop Health Index案） | G6（暴走・停滞検知） | LOOP_HEALTH_INDEX_DESIGN_v0.1.md |
| Caliber（6系統） | G7（品質・妥当性、ただし系統ごとに対象が異なる局所的な保証） | CALIBER_TO_SKILL_MD_GAP_ANALYSIS_v0.1.md |
| GL7（execution_governance.py） | G4（実行前安全性） | WRITER_CHECKER_INSTITUTIONAL_DESIGN_v0.1.md（GL7の役割整理箇所） |
| Decision Policy | G8（単一の裁定アルゴリズム）、G9（判定/実行/記録/承認の権限分離を明文化） | DECISION_POLICY_v0.1.md 第0節 |
| Writer/Checker（Hard Gate: Test・再現性検証・構造チェック） | G7（事後的な品質・妥当性） | WRITER_CHECKER_INSTITUTIONAL_DESIGN_v0.1.md |
| UTF-8/CP932再発防止規約 | G7の一種（エンコーディング整合性という技術的品質） | CLAUDE.md |

---

## 第2部: 提案 — 保証マトリクス、重複疑い、未保証領域

### 2.1 保証類型ごとの担当機構（逆引き表）

| 保証類型 | 担当を主張する機構（複数可） | 単一/複数 |
|---|---|---|
| G1 存在保証 | KN-004 Registry、MODULE_CATALOG_v1 | **複数（重複疑い、後述2.2）** |
| G2 不変性・改ざん検知保証 | ledger.json、mocka_events.db+audit_trigger.py、decision_ledger.jsonl(PHI-OS)、KN_SERIES_LEDGER(実体未確認) | **複数（重複疑いだが判定保留、後述2.2）** |
| G3 網羅性保証 | file_edit_rule、event_gate（単一経路保証、TODO_322）、PostToolUse自動記録フック | 単一系統（event_gateへの一元化が明記されているため、意図的な統合と考えられる） |
| G4 実行前安全性保証 | GL7のみ | 単一だが**未保証の穴あり（後述2.3）** |
| G5 人間最終決定保証 | Human Gate（phi_os/human_gate.py）、Decision Policyのescalate_if_needed()（human_gate.pyのsubmit()を再利用） | 単一系統に統合済み（Decision PolicyはHuman Gateを再実装せず再利用しているため、意図的な統合の好例） |
| G6 暴走・停滞検知保証 | LOOP_DESIGN 3制約（暴走側）、DRIFT_STANDARD（逸脱側）、Loop Health Index案（停滞側、未実装） | 対象範囲が異なるため役割分担と考えられるが、**実装の実在性に疑義あり（後述2.3）** |
| G7 品質・妥当性保証 | Caliber各系統（対象がテキスト濃縮/候補スコア等で異なる）、Writer/CheckerのHard Gate（対象はコード成果物）、UTF-8規約（対象は文字エンコーディング） | 対象が異なるため重複ではないと考えられる |
| G8 単一正本保証 | Decision Policy（「唯一の裁定アルゴリズム」を明言）、単一ルート規則（MCP配置ガード） | 対象が異なる（前者は知識資産間の裁定、後者はファイル配置）ため重複ではない。ただしG1の重複（KN-004/MODULE_CATALOG_v1）はG8の観点からも問題になりうる |
| G9 権限分離保証 | Decision Policy責務境界、Human Approval Gateとの権力分離 | 単一の設計思想に基づく一貫した主張 |
| G10 文脈・経験継承保証 | Memory拡張、Infield、working_memory.py、Knowledge Assets | 粒度が異なるため役割分担（CONCEPT_AUDIT_v0.1.mdで確認済み） |

### 2.2 一つの保証を複数機構が担っている疑い（重複候補）

**(a) G1 存在保証: KN-004 Registry と MODULE_CATALOG_v1**

両者とも「システム内の何かが存在すること」を台帳化する仕組みであり、対象（KN-004=すべての成果物、MODULE_CATALOG=モジュールという成果物の一種）に包含関係がある可能性がある。`CONCEPT_AUDIT_v0.1.md`第2.2節で既に「未検証の重複疑い」として指摘済みであり、本監査でも同一の結論に至った。**新規の発見ではなく、既存の指摘を「保証」という別の軸から見ても同じ結論になることを確認したものである。**

**(b) G2 不変性保証: Ledgerクラスタの3〜4系統**

ledger.json（ハッシュチェーン）、mocka_events.db+audit_trigger.py（SQLiteトリガー）、decision_ledger.jsonl（PHI-OS ISE独自のverify_chain()）は、いずれも「記録が改ざんされていないことを検証可能にする」という同じ保証を、それぞれ別の検証方式で独立に提供しようとしている。ただし`VOCABULARY_PATTERN_AUDIT_CRITERIA_v0.1.md`第2.4節のワークド・イグザンプルで、この4系統は4観点（書込/読取/失敗時挙動/参照元）のいずれも判明していない項目があり「判定保留」となっている。**したがって、本監査でも「重複している」と断定はせず、「同じ保証を主張する候補が複数存在し、それらが実際に整合しているか・冗長なだけなのかは未検証」という表現に留める。**

### 2.3 保証されていない、または保証が未接続になっている領域（ギャップ）

以下は、MoCKAの制度文書上は保証が謳われているにもかかわらず、実際の接続・実装が確認されていない、または確認の結果ギャップが判明している箇所である。特にG4・G5はMoCKAの根幹（「AIを信じるな、システムで縛れ」「Human-First」）に直結するため、重点的に記載する。

**(a) G4 実行前安全性保証（GL7）の穴**

`WRITER_CHECKER_INSTITUTIONAL_DESIGN_v0.1.md`作成時の調査で、GL7のFORBIDDEN_EXECUTIONSが実行経路に未接続であること（gl7_execution_kernel_spec_v1.md 10章で「未接続」として確定済みとされる）が言及されている。これは「危険な実行は行われる前に止められる」という保証が、少なくとも一部の条件について宣言はされているが実行時には機能していないことを意味する。GL7-UNENFORCED-CONDITIONS-BUGとして一部は修正済みとの記録もあるため、**現時点でどこまで解消されているかは要確認**（本監査では新規に実コードを確認していない）。

**(b) G5 人間最終決定保証の複数の未接続点**

- GL7のDry Run通過後、Human Gateへ接続する経路が未実装（`WRITER_CHECKER_INSTITUTIONAL_DESIGN_v0.1.md`が参照するgl7_execution_kernel_spec_v1.md 10章の記載による）
- Knowledge Activation PolicyのReview Gate（Reason Unit→Knowledge Assets昇格の審査点）が「方針決定のみ・未実装」（`ACTIVATION_POLICY_v0.1.md`第3節「実装注記（未実装・TODO_393-B以降の課題）」に明記）
- `WRITER_CHECKER_INSTITUTIONAL_DESIGN_v0.1.md`自身が「Checker PASSが形式的な追認に堕さないか」というリスクを未確定事項として明記している

これら3点はいずれも「最終的に人間が決定する」という保証の実装が、制度文書レベルでは要求されているものの、コードレベルでは接続されていない、または接続の確実性が担保されていない箇所である。G5はMoCKAが最も繰り返し強調してきた保証（[[feedback_flag_autonomy_risk_in_governance_design]]的な観点でも最重要）であるにもかかわらず、複数箇所で「宣言はあるが未接続」という同じパターンが繰り返されている点は、個別の実装漏れというより構造的な傾向として注視すべきと考えられる。**ただし、これは断定的な欠陥指摘ではなく、既存文書の記載を集約した結果そう見える、という段階の指摘である。**

**(c) G6 暴走・停滞検知保証の実装疑義**

`LOOP_HEALTH_INDEX_DESIGN_v0.1.md`作成時の調査で、`MOCKA_OVERVIEW.json`に記載されているcalc_drift_v3等の関数が実際の`interface\router.py`に存在せず、同ファイルに構文エラー・BOM混入がありast.parseが失敗することが検証済みである。これが事実であれば、DRIFT_STANDARD_v1.1.mdが謳う「Drift基準による逸脱検知」という保証は、少なくとも記載されている実装経路においては機能していない可能性がある。**この点はドキュメントと実コードの乖離という別種の問題（`VOCABULARY_PATTERN_AUDIT_TARGET_LIST_v0.1.md`第2.2節で本Vocabulary Auditのスコープ外と整理済み）だが、Guarantee Matrixの観点では「G6が実際には保証されていないかもしれない」という点で重要な関連事項のため、ここでも改めて記載する。**

**(d) G1 存在保証の全体網羅性の穴**

KN-004 Registryはまだ設計フェーズであり（正式帰属先ディレクトリ未確定）、「システム内のすべての成果物が存在確認できる」という保証は、現状は各製品のローカルregistry（PHI-OS schema-registry、SEO-OS CapabilityRegistry等）が個別に部分的な存在保証を提供しているに過ぎず、統合された単一の存在保証はまだ成立していない。

**(e) G10 文脈継承保証の未接続点**

`CONCEPT_AUDIT_v0.1.md`で確認済みの通り、`mocka-infield`リポジトリはBINDING_GAP_REPORT_v1でORPHAN（制度未接続）と明記されている。Infieldという構想上の内部記憶保証は、`data\storage\infield`という本体側の実装で部分的に代替されているが、独立リポジトリとして設計された`mocka-infield`自体は機能していない。

---

## 第3部: 未確定事項

- 本監査の10種の保証類型は本監査のための便宜的な作業分類であり、MoCKA公式の分類として確定していない。分類の妥当性自体、博士確認が必要
- 2.2節(a)(b)、2.3節(a)〜(e)はいずれも既存文書の記載を集約したものであり、本監査で新規にコードを確認したものではない。特にGL7の10章記載内容・router.pyの実態は、それぞれ`WRITER_CHECKER_INSTITUTIONAL_DESIGN_v0.1.md`・`LOOP_HEALTH_INDEX_DESIGN_v0.1.md`作成時の調査結果を再掲したものであり、本監査独自の裏取りではない
- G5（人間最終決定保証）の複数の未接続点を「構造的な傾向」と表現した箇所は、3件という限られたサンプルからの推測であり、断定はしていない。他にも同様の未接続点が存在するかどうかは、Vocabulary and Pattern Audit本体（Task-E/F、git回復後実行予定）と合わせて確認する価値があると考えられる
- Orchestra/Relay/Memory等の個別製品固有の保証（例: 決済の整合性保証、配信の到達保証等）は、今回の集約対象文書に情報がなく本監査では扱っていない（不明・要確認）

---

## 改訂履歴

- v0.1（2026-07-03）: 博士指示Task-Hに基づき新規作成。

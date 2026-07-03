# Contradiction Audit v0.1

位置づけ: 博士指示（2026-07-03、Task-Q）に基づき新規作成。本日一連の監査（Concept Audit、Guarantee Matrix Audit、Human Gate Connectivity Audit、Guarantee Verification Matrix、Guarantee Maturity Index、First Principles Audit）を横断し、「制度では保証すると書いてあるが、現実はまだ保証されていないもの」を一覧化する。

**重要な位置づけ:** 本監査は欠陥探しではない。MoCKAが「事故→記録→分析→制度化→文明の進化」（`FIRST_PRINCIPLES_AUDIT_v0.1.md`のP4）という思想を持つのと同じように、ここで記録するギャップは「次に何を接続すべきか」という進化のロードマップとして扱う。実装は一切含まない。新規のコード調査は行わず、本日作成済みの文書の統合のみを行う。

---

## 第1部: 現状把握 — 本日発見されたギャップの出典

本監査が統合する一次情報は以下の6文書である。

- `docs\governance\CONCEPT_AUDIT_v0.1.md`
- `docs\governance\GUARANTEE_MATRIX_AUDIT_v0.1.md`
- `docs\governance\HUMAN_GATE_CONNECTIVITY_AUDIT_v0.1.md`
- `docs\governance\GUARANTEE_VERIFICATION_MATRIX_v0.1.md`
- `docs\governance\GUARANTEE_MATURITY_INDEX_v0.1.md`
- `docs\governance\FIRST_PRINCIPLES_AUDIT_v0.1.md`

---

## 第2部: 提案 — 宣言と現実のギャップ一覧（ロードマップ形式）

各項目は「宣言（設計・文書上の約束）」「現実（確認された実態）」「ギャップの性質」「次のマイルストーン（提案・非確定）」の4点で整理する。

### G-1: Human-First原則は宣言済みだが、複数の接続点で未接続

- **宣言:** 「人間の決定は必ず人間が行う」（Human-First原則、`LOOP_DESIGN_PRINCIPLES.md`）
- **現実:** GL7のDry Run後Human Gate未接続、Knowledge ActivationのReview Gate未実装、Writer/CheckerのHuman Gate接続方式未設計、という3箇所で「宣言はあるが接続コードがない」状態（`HUMAN_GATE_CONNECTIVITY_AUDIT_v0.1.md`）
- **ギャップの性質:** 制度の中核原則であるにもかかわらず、新しい系統が追加されるたびに接続作業が後回しになっている可能性がある構造的パターン
- **次のマイルストーン案:** GL7→Human Gateの接続を最優先で設計する（Approval Gate本体は既に実装済みであり、接続先を新設する必要はなく、既存のsubmit()相当を呼び出す設計で足りる可能性がある。ただしこれは提案であり実装判断ではない）

### G-2: Loop Health/Drift検知は概念定義済みだが、実装の実在性に疑義

- **宣言:** DRIFT_STANDARD_v1.1.mdによる逸脱検知（NORMAL/WARNING/DANGER/CRITICAL）
- **現実:** `MOCKA_OVERVIEW.json`記載のcalc_drift_v3等の関数がinterface\router.pyに実在しない疑いがあり、同ファイルに構文エラー・BOM混入も検出されている（`LOOP_HEALTH_INDEX_DESIGN_v0.1.md`調査時に判明）
- **ギャップの性質:** ドキュメントが実コードより先行し、実コードが追いついていない、あるいは過去に存在した実装が失われた可能性がある（どちらかは本監査では判別できない）
- **次のマイルストーン案:** router.pyの実態確認（本Vocabulary/Guarantee Audit群の範囲外だが、優先度の高い別作業として位置づける）

### G-3: KN-004による存在保証は構想済みだが完成待ち

- **宣言:** KN-004 Registryが「MoCKA内に存在するすべての成果物」の存在確認台帳になる、という設計思想（`docs\governance\REGISTRY_*_v1.0.md`）
- **現実:** 正式帰属先ディレクトリが未確定（`PlanningCaliber\workshop\registry_kn004\`配下で`.gitignore`により管理外）であり、加えてMODULE_CATALOG_v1という別の存在台帳との役割分担が未検証（`CONCEPT_AUDIT_v0.1.md`第2.2節）
- **ギャップの性質:** 単純な未完成に加え、完成した場合に別の既存機構と重複する可能性がある、という二重のリスクを抱えている
- **次のマイルストーン案:** KN-004の帰属先を確定する前に、MODULE_CATALOG_v1との関係整理を先に行う（順序を誤ると、確定後に重複が発覚し手戻りになるリスクがあるため）

### G-4: Ledgerの不変性保証は複数系統で主張されているが、整合性は未検証

- **宣言:** 「Event ledger is append only」（Constitution原則1）
- **現実:** ledger.json・mocka_events.db+audit_trigger.py・decision_ledger.jsonl（PHI-OS）・KN_SERIES_LEDGER（実体未確認）という4系統が並存し、`VOCABULARY_PATTERN_AUDIT_CRITERIA_v0.1.md`の4観点判定ではいずれも「判定保留」（重複していると断定する材料も、別物と断定する材料も不足）
- **ギャップの性質:** 「保証されていない」のではなく「保証の実体が一つなのか複数なのか自体が不明」という、他のギャップとは性質が異なるメタ的なギャップ
- **次のマイルストーン案:** KN_SERIES_LEDGERの実体確認を最優先とする（`VOCABULARY_PATTERN_AUDIT_TARGET_LIST_v0.1.md`第2.1節で既に同じ優先順位が提案されている）

### G-5: 単一正本保証（Decision Policy）は明文化されているが、実例で複数正本の疑いがある

- **宣言:** Decision Policyが「唯一の裁定アルゴリズム」であること（`DECISION_POLICY_v0.1.md`第0節）
- **現実:** KN-004とMODULE_CATALOG_v1が同じ情報（存在）を別々に管理している可能性（G-3と同一の事象を単一正本保証の観点から見たもの）
- **ギャップの性質:** G-3と表裏一体。個別の機構レベル（KN-004/MODULE_CATALOG）の重複が、より抽象的な制度原則（単一正本保証）の観点からも問題になる、という二層構造
- **次のマイルストーン案:** G-3と同一（重複関係なので別々に対応する必要はない）

### G-6: AUTO_SEALの自動実行経路とHuman-First原則の関係が未確認

- **宣言:** Human-First原則により、人間の判断が必要な事項はAIが自動決定してはならない
- **現実:** AUTO_SEALに「auto_audit_loop（daemon）」という常駐自動実行経路が存在することが判明しているが、これがHuman Gateと接続すべき性質の処理か、機械的処理として自動化して問題ないものかは未調査（`HUMAN_GATE_CONNECTIVITY_AUDIT_v0.1.md`第2.2節(3)）
- **ギャップの性質:** これは他の項目と異なり「ギャップが存在するかどうか自体が不明」という、調査不足に起因する暫定的な要注意項目である
- **次のマイルストーン案:** AUTO_SEALの各経路が扱う判断の性質を確認する調査を、Human Gate関連の追加調査として位置づける

### G-7: Infield（内部記憶）は制度原則として宣言されているが、独立実装はORPHAN状態

- **宣言:** 「Infield is internal memory」（Constitution原則3）
- **現実:** 構想上の独立実装である`mocka-infield`リポジトリがBINDING_GAP_REPORT_v1でORPHAN（制度未接続）と明記されている。本体側の`data\storage\infield`が部分的に代替している（`CONCEPT_AUDIT_v0.1.md`第2.3節(e)）
- **ギャップの性質:** 原則は宣言されており、機能の一部（`data\storage\infield`）は代替実装で満たされているが、制度が本来想定していた独立構造としては未接続
- **次のマイルストーン案:** `data\storage\infield`による代替が恒久的な解として十分なのか、`mocka-infield`の接続が必要なのかを判断する（この判断自体が博士判断を要する）

---

## 第3部: ロードマップとしての優先順位（提案、非確定）

以下は、各ギャップの「MoCKAの根幹原則への近さ」（`FIRST_PRINCIPLES_AUDIT_v0.1.md`のP1〜P5との対応）を基準にした優先順位案である。確定した優先順位ではない。

1. **G-1（Human-First接続）**: P3に直結する最重要原則であり、かつ`HUMAN_GATE_CONNECTIVITY_AUDIT_v0.1.md`で「構造的傾向」の可能性が指摘されているため
2. **G-6（AUTO_SEAL調査）**: G-1と同じくP3に関わる可能性があり、かつ現状「調査不足」でありG-1より着手コストが低い（まず調べるだけで良い）
3. **G-3/G-5（KN-004とMODULE_CATALOG_v1の関係整理）**: 二層構造のギャップであり、1回の調査で2つのギャップが解消しうる
4. **G-4（Ledgerの実体確認）**: `VOCABULARY_PATTERN_AUDIT_TARGET_LIST_v0.1.md`で既に合意形成済みの優先順位と一致
5. **G-2（router.py実態確認）**: G6（暴走・停滞検知保証）に関わるが、他のギャップと異なり「用語監査」の範囲外の技術的問題であるため、別トラックとして扱うことを提案
6. **G-7（Infield ORPHAN）**: 既知の欠落であり、緊急性は他項目より低いと考えられる

---

## 第4部: 未確定事項

- 上記7項目の優先順位案は、本監査独自の基準（第一原理への近さ）による提案であり、実際の着手判断は博士が行う
- G-2とG-6は「そもそもギャップが存在するのか」自体が未確認の項目であり、他の5項目（存在が確認されたギャップ）とは性質が異なる。この区別を優先順位づけの際に混同しないよう注意が必要
- 本監査は本日作成した6文書の統合であり、それ以前から存在していた可能性のあるギャップ（例えば今回の監査群が対象にしなかったOrchestra/Relay固有の保証）は含まれていない

---

## 改訂履歴

- v0.1（2026-07-03）: 博士指示Task-Qに基づき新規作成。

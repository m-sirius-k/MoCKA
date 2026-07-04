# Vocabulary Audit Evaluation v0.3

位置づけ: `VOCABULARY_INDEX_SCAN_EVIDENCE_v0.1.md`(v0.2、事実収集フェーズ)を受けて、きむら博士から評価フェーズへの移行指示（2026-07-04、8項目の確認質問＋層別採点表の要求）があったため作成する。事実収集フェーズは「評価・採否の判断をしない」ことが厳守事項だったが、本文書はその後続として明示的に評価を行う。v0.2では、v0.1に対するきむら博士の査読指摘（評価基準の明文化・呼び出し関係の追加検証・命名ガバナンス軸の追加）を反映した。v0.3では、くろこ指示書（VOCABULARY_AUDIT_EVALUATION v0.3作成指示）に基づき、評価結果(A〜D)は変更せず理由のみ具体化し、加えて発見事項を「制度上の論点」として、優先順位・採否・改善案を含まない形で整理した（第11・12節）。本作業をもってR01の役割を終了し、最終裁定をきむら博士へ委ねる。

前提: 本文書は「Gemini」による評価（きむら博士のご発言から把握できる範囲: 「完全適合」「正常」「分散思想なので問題ない」「動的接続だから問題ない」等）を直接検証したものではない。Gemini自身の発言原文は本セッションで確認できないため、きむら博士のご質問文に現れた要約のみを参照し、Evidence v0.2および本文書で新たに確認した一次データと突き合わせる形で回答する。

## 0. 評価基準の明文化

本文書全体でA〜Dの4段階を用いる。各段階の意味は以下で固定する（この定義自体も査読対象とする）。

- **A**: 一次データで確認した範囲において、指摘すべき不備が見当たらない、または軽微な形式差のみ。
- **B**: 中核部分は妥当だが、看過できない差異・未確認事項が残る（例: 個別実装は意図的だが、全体設計としての統一的な意図表明は確認できない）。
- **C**: 複数の構造的な不備が確認され、既存文書側も自己申告で不備を認めている箇所がある。
- **D**: 根本的な不備、または既存の複数監査で繰り返し指摘されながら未解決の事項が確認される。

段階の割当は「発見された不備の件数・深刻度・既存文書内での自己申告の有無」を基準とする。本文書のいずれの評価も、Evidence v0.2または本文書で直接確認した一次データに紐づけて記載し、紐づけられない推測は「未確認事項」（第9節）に切り分ける。

---

## 1. 「独立実装＝設計意図」の根拠確認

**質問**: Human Gate2実装・Registry3実装は「意図的な独立設計」と証明できるか、それとも「現在は独立実装である」という観測事実だけか。

**確認した一次データ**:
- `phi_os/human_gate.py`: 冒頭コメントに「仕様根拠: docs/governance/control_map_v2.md」と明記。自身の設計原則（"PHI-OSがHuman Gateの唯一の状態管理責務を持つ"）を文書化している。
- `semantic/query_engine/human_gate.py`: 冒頭コメントに「契約: docs/contracts/phase7_b6_human_gate_ruling_v1.md」と明記。
- `interface/ai_capability_registry.py`: ファイル冒頭コメントで「既存の capability_registry.py（core_kernel/core_store/）は...本ファイルとは独立した別物」と**明示的に**記載。
- `core_kernel/core_store/capability_registry.py`・`PlanningCaliber/workshop/seo-os/caliber/capability_registry.py`: 互いへの参照・言及は確認できなかった。

**回答（事実と推論を分離）**:
- **事実として証明できること**: 各実装は「個別に」設計文書・契約文書を持ち、それぞれの狭い責務範囲内では意図的に設計されている（アドホックな複製ではない）。
- **事実として証明できないこと**: 「同じ名称（Human Gate／CapabilityRegistry）を複数の異なる概念に割り当てることそのものが意図的な制度設計である」と述べる上位文書（ADR・憲章・命名規則）は、本調査で発見できなかった。`interface/ai_capability_registry.py`が「別物」と自己申告している1件を除き、**名称の衝突を認識した上でそれを意図的に許容する、という明文の合意は見当たらない**。
- 結論: 「各実装単体は意図的設計」は事実。「複数実装が同一名称を共有すること自体が意図的な制度設計」は**観測事実のみ**であり、設計意図としての裏付け文書はない。この2つを混同すると「原則①完全独立性の証明」という結論は論理的に飛躍している。

---

## 2. Human Gate二重実装の責務境界

**質問**: 状態管理・判定・UI・APIで役割が重複していないか。

**確認した一次データ（コード全文読了）**:

| 観点 | phi_os/human_gate.py | semantic/query_engine/human_gate.py |
|---|---|---|
| 対象領域 | 汎用承認ワークフロー（submit/approve/reject/expire/cancel） | 意味クラスタ間の衝突裁定（accept/reject/defer/split） |
| 状態管理 | SQLite(`data/mocka_events.db`, テーブル`human_gate_events`)、イベントソーシング | インメモリの`list`（`self._records`）、永続化なし |
| 判定対象 | request_id（承認リクエスト） | from_cluster/to_cluster（意味クラスタの衝突ペア） |
| UI/API | Flask Blueprint、`/api/human_gate/*`エンドポイントあり（App層からのUIトリガ用と明記） | HTTP/UI層への露出なし。純粋なPythonクラス |
| 禁止事項 | request_id重複禁止・不正遷移禁止 | merge裁定の受理禁止・元データ変更禁止・裁定の自動生成禁止 |

**回答**:
- 状態管理・判定対象・永続化方式・UI/API露出のいずれも**重複していない**（機能面では別ドメインを扱う別実装であることをコードレベルで確認した）。
- ただし、既存の`docs/audits/MOCKA_HUMAN_GATE_IDENTITY_CONSOLIDATION_AUDIT_v1.md`が指摘する「Human Gateという名前が4概念にまたがる」という所見と、今回のコード読了結果は整合する。両実装は機能的には衝突していないが、**「Human Gate」という同一名称が、承認ワークフロー（Approval State Machine）と意味裁定装置（Semantic Ruling）という全く異なる2概念を指している**。
- 結論: 「重複実装」ではなく「同名異義（合成語の名称衝突）」。責務境界は曖昧ではなく明確に分離されているが、**用語としての同一性が誤解を招く状態**にある。これは実装上の問題ではなく語彙索引上の問題である。

**追加検証（呼び出し関係、v0.2で実施）**: `grep`によるimport解析で以下を確認した。
- `phi_os/human_gate.py`を参照するのは`phi_os/migrate_prevention_queue.py`・`phi_os/tests/test_human_gate.py`のみ（いずれも`phi_os`内部）。
- `semantic/query_engine/human_gate.py`を参照するのは`semantic/query_engine/human_gate_interface.py`・`semantic/query_engine/observation_surface.py`のみ（いずれも`semantic/query_engine`内部）。
- **両ファイル間の相互import・循環参照は確認されなかった**。互いに独立しており、一方が他方を呼ぶ／循環するという構造ではない。
- 注記（未確認事項）: 本確認は静的import解析（grep）のみであり、文字列ベースの動的ディスパッチ・実行時のモジュールロード等がある場合は検出できない。その可能性までは排除できない。

---

## 3. capability_registry 3実装の保存内容比較

**質問**: 3つとも保持する情報は違うか。同期問題か分散か。

**確認した一次データ（コード全文読了）**:

| ファイル | 管理対象 | 保存構造 | 用途 |
|---|---|---|---|
| `core_kernel/core_store/capability_registry.py` | capability名 → module_idの集合（Pythonモジュールの能力逆引き） | インメモリdict（`_providers`） | MoCKA本体のモジュール間capability解決 |
| `interface/ai_capability_registry.py` | AI名（ChatGPT/Perplexity/Gemini等） → 能力ドメインスコア(0.0-1.0)・vendor・制約 | Pythonのdictリテラル定数(`AI_CAPABILITY_REGISTRY`) | 外部AI（合議先AI）の能力に基づく選定・ルーティング |
| `PlanningCaliber/workshop/seo-os/caliber/capability_registry.py` | capability文字列 → Workerクラスのリスト（SEO-OS内プラグインWorker自動登録） | クラス変数dict（シングルトン、スレッドロック付き） | SEO-OS内のWorkerプラグイン機構 |

**回答**:
- 3つは**保持する情報・管理対象が完全に異なる**（Pythonモジュール能力／外部AI能力／SEO-OSワーカープラグイン）。同一実体（例:「CapabilityA」）を3箇所が別々に保持して不整合を起こす、という**同期問題の構造にはなっていない**（キーの意味空間自体が異なるため）。
- 分散でも同期問題でもなく、これも**同名異義**（3つの無関係な概念が"CapabilityRegistry"という同一クラス名を共有）に分類される。
- ただし`PlanningCaliber/workshop/seo-os/caliber/capability_registry.py`は他の2つと相互参照が一切なく、SEO-OSという別サブプロジェクトの内部実装である可能性が高い（本調査ではこの帰属関係の妥当性判断は行わない）。

**追加検証（呼び出し関係、v0.2で実施）**:
- `core_kernel/core_store/capability_registry.py`の実利用者: `gateway/connector_caliber.py`・`gateway/connector_router.py`・`interface/proposal_schema.py`。
- `interface/ai_capability_registry.py`の実利用者: `gateway/connector_caliber.py`・`gateway/connector_router.py`（`from interface.ai_capability_registry import registry as _reg`等）。
- **`gateway/connector_router.py`は上記2つの異なるcapability_registryを同時にimportしている**ことを確認した。これは「気づかず並存している」のではなく、**同一のルーティング層が両者をそれぞれ別目的（モジュール能力解決／外部AI選定）で意図的に使い分けている**ことを示す一次証拠であり、実装レベルでの混乱・衝突は起きていないことの裏付けを補強する。
- `PlanningCaliber/workshop/seo-os/caliber/capability_registry.py`を参照する箇所は本調査では確認できなかった（SEO-OSサブプロジェクト内で完結している可能性が高い）。

---

## 4. Human Gate監査シリーズ非参照 — 分散設計と索引不足は別軸か

**質問**: 制度辞典が既存監査シリーズを引用しないことは「分散思想」とは別問題ではないか。

**回答**:
- ご指摘の通り、**分散設計（アーキテクチャ上、複数の独立実装が存在するという事実）**と、**索引不足（それを記述する制度辞典が既存の関連文書を網羅的に引用できていないという文書管理上の不備）は別軸である**。
- 分散設計それ自体は、MoCKAの制度がその是非を判断していない（Registry Neutrality Principle等、判断保留を許容する設計思想がある）。
- 一方、`VOCABULARY_CONSTITUTION_v0.1.md`は自らを「制度辞典（責務・保証・境界・禁止事項・依存関係を定めた制度文書）」と位置づけている。制度辞典を名乗る文書が、同一の対象（Human Gate）についてより詳細な調査を既に行った10件の既存監査シリーズ（`docs/audits/MOCKA_HUMAN_GATE_*_AUDIT_v1.md`等）を参照文書リストに含めていないことは、「分散設計の是非」とは独立した**索引・引用網羅性の不備**である。
- 結論: 「分散思想だから問題ない」という評価は、分散設計の是非（本評価では判断しない）と索引不備の是非（本評価では問題ありと判断する）を混同している。両者は別々に評価されるべきであり、後者は明確な不備である。

---

## 5. semantic_dictionary — イベント0件は「制度上存在しない」の証明か

**質問**: 別の証跡（Git履歴・コミット・PR・Issue）も確認したか。

**追加確認した一次データ**:
- `git log --follow --diff-filter=A -- docs/reference/semantic_dictionary/` の結果、単一コミット`b77d1148a`（2026-06-16、Author: NSJP_kimura）で追加されていることを確認した。
- **このコミットのメッセージは「add: MoCKA v1.1 + v1.2 — Semantic Timeline / Decision Log Analyzer / Cognitive Loop」であり、semantic_dictionary・用語索引・duplicate_candidates等への言及は一切ない**。timeline/cognitive/phi_os配下の別機能追加コミットに、説明なく同梱される形で追加されている。
- GitHub PR/Issueの照合はGitHub API接続待ち（本セッションでは未実施、リモート照会は別途必要）。

**回答**:
- mocka_searchでイベント0件という事実に加え、**コミットメッセージ自体にもsemantic_dictionaryへの言及がない**ことを新たに確認した。これは「記録なき作業はMoCKAとして存在しない」という制度原則（`.claude/CLAUDE.md`・MOCKA_OVERVIEW.json記載）に照らすと、二重の意味で記録が欠落している（event記録なし、かつコミットメッセージでの説明もなし）。
- 「イベントが存在しないだけで制度上存在しないと断定できるか」という問いには、**断定はできない**（ファイル自体は実在し、機能している可能性がある）。しかし「制度が定める記録義務を経て導入された成果物」としては**現時点で確認できる証跡がない**というのが正確な表現であり、「未登録」という評価は妥当だが「存在しない」と同義ではない。両者を区別して報告する。

---

## 6. KN_SERIES_LEDGER — 「動的接続」の根拠文書

**質問**: 動的生成という仕様はどの文書で定義されているか。

**追加確認した一次データ**:
`docs/governance/*.md`全体に対し「動的生成」「動的接続」「dynamic generat」等のキーワードをKN_SERIES_LEDGER/Ledger/Atlas文脈で検索したが、**該当する記述は1件も発見できなかった**。KN_SERIES_LEDGERが言及される文書（CATEGORY_REGISTRY_v2.0.md、REGISTRY_CHARTER_v1.0.md、TERM-001等）はいずれも「KN_SERIES_LEDGERに従い」等、既存の実体として参照するのみで、動的生成・動的接続という設計方式を定義した記述は確認できなかった。

**回答**: 「動的接続だから問題ない」という評価の根拠となる設計文書は、本調査では**発見できなかった**。Evidence v0.2の「実体なし」という事実に対し、動的生成という仕様上の説明を与える文書は現時点で存在しないと考えられる（断定はしない。未読の文書に記載がある可能性は残る）。

---

## 7. Atlas — 「将来動的構成」の根拠文書

**質問**: 将来動的構成という根拠文書はあるか、それとも設計提案か。

**回答**: TERM-001・REGISTRY_SEMANTICS_v1.0.md等がAtlas Seriesを「Category/Series間の関係性・Topologyの管轄」として繰り返し予告しているが、これは**将来のシリーズとして着手前であることの宣言**であり、「動的に構成される」という技術的性質を定義した記述ではない。「動的構成」という性質を裏付ける文書は本調査で発見できなかった。Atlasは現時点で「未着手の予告」であり、「動的構成という設計が既に確定している」という評価は文書上の裏付けを欠く。

---

## 8. 命名ガバナンス（追加評価軸、v0.2で新設）

きむら博士のご指摘により追加。今回の監査全体（Evidence v0.2・本文書1〜7節）を通じて最も繰り返し現れたパターンは、個々の実装の欠陥ではなく「同一名称が複数の無関係な概念に割り当てられる」という**命名ガバナンスの欠如**である。

**確認した一次データ**:
- Human Gate: 承認ワークフロー(phi_os)と意味裁定装置(semantic/query_engine)という2概念（既存監査`MOCKA_HUMAN_GATE_IDENTITY_CONSOLIDATION_AUDIT_v1.md`はさらに細分化し4概念と判定）。
- Registry語根: capability_registry(3実装)・recurrence_registry・beta_registry・ai_capability_registry・各製品ローカルregistry等、Evidence v0.2で確認しただけで6系統以上。
- Ledger語根: ledger.json・mocka_events.db+audit_trigger.py・decision_ledger.jsonl(PHI-OS)・KN_SERIES_LEDGER(実体不明)の4候補、既存の`VOCABULARY_PATTERN_AUDIT_CRITERIA_v0.1.md`が4候補すべて「判定保留」と結論。
- Archive語根: TIC Archive層／Phase ARCHIVE層／Module ARCHIVED状態という3つの同語異義（既存文書が明記済み）。
- **`docs/NAMING_CONVENTION.md`という命名規則文書は実在する**（2026-03-29作成、Authority: nsjp_kimura、Status: FIXED — 変更には統治承認が必要）。ただし対象は`mocka_Receptor`・`mocka_insight_system`・`mocka_Movement`・`shadow_Movement`・`acceptor:infield/outfield`等の**最上位アーキテクチャ名の固定**であり、Human Gate・Registry・Ledger・Caliber等、本監査で扱う**モジュール／概念レベルの語彙はこの文書の適用範囲外**である。同文書冒頭の理念（"Names are the language of civilization. When names drift, civilization drifts."）は本監査の主題そのものを言い当てているが、その理念をモジュール語彙レベルまで運用する規則は本調査では見つからなかった。

**評価**: 命名ガバナンス = **D**
理由: (1)最上位アーキテクチャ名には命名規則が存在し統治対象になっているが、(2)本監査が扱う語彙層（Human Gate/Registry/Ledger/Archive等）には同等の規則・審査プロセスが及んでいないことが、複数の独立した事象（4件のHuman Gate概念、6系統以上のRegistry、4候補のLedger、3つのArchive同語異義）として繰り返し確認された。これは個別の実装判断の誤りではなく、**語彙層全体を横断する統治の空白**であり、他のどの評価軸よりも本監査の発見全体を集約的に説明する。

---

## 9. 未確認事項（本評価の範囲外・限界）

以下は本文書・Evidence v0.2のいずれでも検証していない、または静的解析の限界により確認しきれなかった事項である。将来の監査・きむら博士の判断の参考として明記する。

- **動的呼び出し**: Human Gate・capability_registryのimport関係はgrepによる静的解析のみで確認した。文字列ベースのモジュールロード（`importlib`等）・設定ファイル経由の動的ディスパッチがある場合は本調査では検出できない。
- **GitHub PR/Issue履歴**: semantic_dictionaryについて、mocka_search（events.db）とgitコミット履歴は確認したが、GitHub側のPR・Issueでの言及有無は本セッションでは未確認（GitHub接続待ち）。
- **他の16語(Human Gate/Registry/Artifact以外)の呼び出し関係**: 本文書で呼び出し関係を実証的に確認したのはHuman GateとRegistry(capability_registry)のみ。Ledger4候補・Archive3層・Caliber6系統等、他の同名異義候補については呼び出し関係の相互参照確認を行っていない。
- **`PlanningCaliber/workshop/seo-os/caliber/capability_registry.py`の帰属**: SEO-OSという別サブプロジェクトの内部実装である可能性を述べたが、SEO-OS自体の独立性・MoCKA本体との統治関係は本調査の範囲外。
- **NAMING_CONVENTION.mdの全文**: 全170行を確認済み（v0.2で追加確認）。"Registry"・"Human Gate"・"Capability"への言及は0件、"Ledger"・"Caliber"は比喩的な1〜2件の言及のみで、本監査が扱う語彙層への規定は含まれていないことを確認した。

---

## 10. Step1: 評価確定 — 層別評価表（理由を一段具体化。評価結果はv0.2から変更しない）

**質問**: 「MoCKAの思想には適合する」と「現状のリポジトリが設計通り実装されている」は別評価であり、分離した採点表を提示せよ。

以下、評価結果(A〜D)はv0.2から変更しない。各行の理由を、具体的な件数・ファイルパス・文書名まで一段具体化した。

| 評価対象 | 結果 | 理由（具体化） |
|---|---|---|
| 設計思想との整合（Design Philosophy） | B | Aでない理由を3点で特定する。(1) 個々の実装は意図的だが接続文書が異なる: `phi_os/human_gate.py`は`docs/governance/control_map_v2.md`、`semantic/query_engine/human_gate.py`は`docs/contracts/phase7_b6_human_gate_ruling_v1.md`を根拠とし、両者を橋渡しする上位文書は確認できない。(2) 同一名称の複数概念への割当を制度として許容/禁止するかを定める規定が存在しない: `docs/NAMING_CONVENTION.md`(2026-03-29、Status:FIXED、全170行)は`mocka_Receptor`等7つの最上位アーキテクチャ名のみを対象とし、"Registry"「Human Gate"「Capability"への言及は0件。(3) Constitution 5原則の1つ「Event history is the single source of truth」と、Ledger4候補(`ledger.json`/`mocka_events.db`+`audit_trigger.py`/`decision_ledger.jsonl`/`KN_SERIES_LEDGER`)が並立し`VOCABULARY_PATTERN_AUDIT_CRITERIA_v0.1.md`で4候補とも「判定保留」とされている状態との間に、文書上明示的に解消されていない緊張がある。Dでない理由: 各実装は個別には契約文書を伴う意図的設計であり、アドホックな複製ではないことが第1〜3節で確認されている。 |
| 文書整合性（Documentation Consistency） | C | 具体的な未統合箇所: (1) `VOCABULARY_PATTERN_AUDIT_TARGET_LIST_v0.1.md`第3部が「本Audit(および先行するCONCEPT_AUDIT_v0.1.md)で見つかった曖昧語彙...は、次回TERM-001改訂時に合わせて解消するのが効率的」と自己申告し、統合時期・方法が確定していない。(2) `VOCABULARY_CONSTITUTION_v0.1.md`第3部が「Catalogの禁止事項は未確認のままである」と明記。(3) `TERM-001_REGISTRY_TERMINOLOGY.md`のSource定義が「Sourceの確定は将来の設計課題として残されている」と明記されたまま、12語の用語集に正式収録されている。3件とも既存文書が自ら不備を認めている箇所であり、本評価による新規指摘ではない。 |
| 索引整合性（Vocabulary Index Completeness） | D | 具体的な欠損: governance配下での出現件数がGL7=137件、TIC=168件、Decision Policy=66件、Guarantee系(4専用文書: GUARANTEE_MATRIX_AUDIT/GUARANTEE_MATURITY_INDEX/GUARANTEE_COVERAGE_MAP/GUARANTEE_VERIFICATION_MATRIX)=58件、Writer=48件・Checker=51件、Knowledge Assets=25件、Decision Evidence=20件、Reason Unit=16件、BEE=9件。これらはいずれも19語辞典(TERM-001の12語+VOCABULARY_CONSTITUTION_v0.1の8語)に独立エントリを持たない。加えて、`VOCABULARY_CONSTITUTION_v0.1.md`が「Approval（Human Gate）」を1エントリとして扱う一方、`docs/audits/MOCKA_HUMAN_GATE_*_AUDIT_v1.md`(5件)+`PHASE10_3_HUMAN_GATE_*_v1.md`(5件)=計10件の既存監査シリーズを参照文書リストに含めていない。 |
| 実装整合性（Implementation Consistency） | B | 確認済み事実: Human Gate2実装(状態管理方式・永続化先・API有無すべて相違を確認、第2節)、capability_registry3実装(管理対象キー空間が完全に相違、第3節)とも機能的重複なし。v0.2で静的import解析を追加実施し、`phi_os/human_gate.py`↔`semantic/query_engine/human_gate.py`間、および3capability_registry間で相互import・循環参照がないことを確認した。`gateway/connector_router.py`が2つのcapability_registryを同時利用している点は意図的併用の証拠として第3節に記載済み。Aでない理由: 静的import解析のみであり、`importlib`等による動的ディスパッチの有無は未検証（第9節）。他16語（Ledger4候補・Archive3層・Caliber6系統等）については呼び出し関係の検証自体を行っていない。 |
| 正本管理（Canonical Source Management） | D | 具体的な不備: (1) `docs/governance/REGISTRY_SCHEMA_v1.0.md`と`PlanningCaliber/fp/REGISTRY_SCHEMA_v1.0.md`が同一内容(identifierフィールド定義部分を含め一致)で物理的に2箇所存在。(2) `KN_SERIES_LEDGER`は`data/MOCKA_TODO_ACTIVE.json`内のTODO ID文字列としてのみ存在し、独立実体(JSON/DB等)は確認できず(第6節)。(3) `Atlas`はTERM-001・REGISTRY_SEMANTICS_v1.0.md等で繰り返し予告されるが、文書実体は本調査時点で存在しない(第7節)。(4) KN-004とMODULE_CATALOG_v1のスコープ重複が`GUARANTEE_MATRIX_AUDIT_v0.1.md`・`CONCEPT_AUDIT_v0.1.md`・`VOCABULARY_PATTERN_AUDIT_TARGET_LIST_v0.1.md`の少なくとも3文書で繰り返し指摘されながら未解決。 |
| ガバナンス証跡（Governance Audit Trail） | C | 具体的な対比: TERM-001・CONCEPT_AUDIT_v0.1・HUMAN_GATE_*_AUDIT等の正規監査文書群はCHANGE_START/CHANGE_DONE events記録とHuman Approval Gate承認(きむら博士)を伴うことを本調査・前回セッションの事実収集で確認済み。一方、`docs/reference/semantic_dictionary/raw/`配下7ファイル(all_terms.json 282MB等)は、(a) mocka_searchでイベント0件、(b) 追加コミット`b77d1148a`(2026-06-16)のコミットメッセージ「add: MoCKA v1.1 + v1.2 — Semantic Timeline / Decision Log Analyzer / Cognitive Loop」にも一切の言及がない、という二重の記録欠落が確認された。 |
| **命名ガバナンス（Naming Governance）** | **D** | 独立に確認された4件の同名異義事象: Human Gate(2実装・既存監査は4概念と分類)、Registry語根(capability_registry 3実装を含め6系統以上)、Ledger語根(4候補、判定保留)、Archive語根(TIC Archive層／Phase ARCHIVE層／Module ARCHIVED状態の3同語異義、既存文書が明記済み)。これらを横断的に規律する命名規則文書は、`NAMING_CONVENTION.md`(最上位アーキテクチャ名7件のみが対象)を除き確認できなかった。4件の独立事象が同一パターンを示している点で、他のいずれの軸よりも本監査結果を集約的に説明する。 |

**総括**: 「MoCKAの思想（Registry Neutrality・記録主義・Human-First等）への適合」は概ね妥当（B）だが、「現状のリポジトリが設計通りに実装・文書化・索引化・正本管理されているか」は複数の層でC〜Dの不備が確認される。「完全適合」という単一の評価に集約することは、この2層の違いを覆い隠す。特に索引整合性(D)・正本管理(D)・命名ガバナンス(D)は、事実収集フェーズ(Evidence v0.2)で確認された具体的な未解決事項に直接対応しており、「分散思想だから問題ない」「動的接続だから問題ない」という説明では解消されない。未確認事項（第9節）を踏まえると、実装整合性(B)は「現時点で確認できた範囲では良好」という留保付きの評価であり、動的呼び出し等の追加監査により変わる可能性がある。

---

## 11. Step2/3: 論点整理と判断対象の分離

以下は評価（第10節）を踏まえ、発見事項を「制度上の論点」として整理したものである。各論点について、影響範囲・関連文書・関連モジュール・未確認事項・博士判断が必要な理由のみを記載する。優先順位・採否・改善方法・ロードマップ・実装案は記載しない（Step4）。

### 論点A: 命名統治の問題

**論点**: 同一名称（Human Gate／Registry／Ledger／Archive等）が複数の無関係な概念に割り当てられている状態を、モジュール／概念レベルで規律する制度的な仕組みが確認されていない。

- **影響範囲**: Human Gate（2実装、既存監査は4概念と分類）／Registry語根（capability_registry 3実装を含め6系統以上）／Ledger語根（4候補）／Archive語根（3同語異義）。
- **関連文書**: `docs/NAMING_CONVENTION.md`（最上位アーキテクチャ名のみ対象）、`VOCABULARY_CONSTITUTION_v0.1.md`、`TERM-001_REGISTRY_TERMINOLOGY.md`、`docs/audits/MOCKA_HUMAN_GATE_*_AUDIT_v1.md`系列、`VOCABULARY_PATTERN_AUDIT_CRITERIA_v0.1.md`。
- **関連モジュール**: `phi_os/human_gate.py`、`semantic/query_engine/human_gate.py`、`core_kernel/core_store/capability_registry.py`、`interface/ai_capability_registry.py`、`PlanningCaliber/workshop/seo-os/caliber/capability_registry.py`、`runtime/main/ledger.json`、`mocka_events.db`+`audit_trigger.py`、PHI-OS `decision_ledger.jsonl`、`KN_SERIES_LEDGER`（実体未確認）。
- **未確認事項**: `NAMING_CONVENTION.md`以外にモジュール語彙レベルの命名規則文書が存在しないかどうかは、未読文書に記載がある可能性を完全には排除できない。Ledger4候補・Archive3層の相互呼び出し関係は検証していない。
- **博士判断が必要な理由**: 「同一名称の多義化」を制度的に許容する（同名異義として公式に位置づける）か、命名規則の対象範囲をモジュール／概念レベルまで拡張するかは、Registry Neutrality Principle等の既存設計思想との整合を要する制度設計判断であり、事実収集・評価の範囲を超える。

### 論点B: 索引管理の問題

**論点**: 制度用語索引（TERM-001／VOCABULARY_CONSTITUTION_v0.1）が、実際に高頻度で使用されている制度語を網羅しておらず、また既存の関連監査文書群を参照文書リストに含めていない。

- **影響範囲**: 欠損語候補（GL7 137件／TIC 168件／Decision Policy 66件／Guarantee系58件／Writer 48件・Checker 51件／Knowledge Assets 25件／Decision Evidence 20件／Reason Unit 16件／BEE 9件）。VOCABULARY_CONSTITUTION_v0.1・TERM-001が扱う19語という範囲。Human Gate監査シリーズ10件の非参照。
- **関連文書**: `VOCABULARY_CONSTITUTION_v0.1.md`、`TERM-001_REGISTRY_TERMINOLOGY.md`、`VOCABULARY_PATTERN_AUDIT_TARGET_LIST_v0.1.md`、`docs/audits/MOCKA_HUMAN_GATE_*_AUDIT_v1.md`系列（10件）。
- **関連モジュール**: なし（文書レベルの索引問題であり、特定コードモジュールとは直接紐付かない）。
- **未確認事項**: 欠損語候補として挙げた語彙以外にも、本調査で走査していない制度語彙が存在する可能性がある（19語＋追加候補10語のみを対象としており、リポジトリ全体の網羅的な用語抽出ではない）。
- **博士判断が必要な理由**: 索引の対象範囲（19語に留めるか、GL7等を追加するか）、既存監査シリーズとの統合時期・方法（`VOCABULARY_PATTERN_AUDIT_TARGET_LIST_v0.1.md`が既に「次回TERM-001改訂時に解消」と記録済み）の確定は、TERM-001改訂の体制・時期に関わる制度設計判断であり、事実収集・評価の範囲を超える。

### 論点C: 正本管理の問題

**論点**: 複数の文書・実体について「どれが正本か」が確定していない、または物理的な複製が存在する。

- **影響範囲**: `REGISTRY_SCHEMA_v1.0.md`（2箇所に物理的複製）／`KN_SERIES_LEDGER`（実体不在）／`Atlas`（実体不在）／KN-004とMODULE_CATALOG_v1のスコープ重複（複数監査で指摘、未解決）／TERM-001自身が「Sourceの確定は将来の設計課題」と明記。
- **関連文書**: `docs/governance/REGISTRY_SCHEMA_v1.0.md`、`PlanningCaliber/fp/REGISTRY_SCHEMA_v1.0.md`、`TERM-001_REGISTRY_TERMINOLOGY.md`、`REGISTRY_CHARTER_v1.0.md`、`CATEGORY_REGISTRY_v2.0.md`、`GUARANTEE_MATRIX_AUDIT_v0.1.md`。
- **関連モジュール**: 特定なし（文書の物理配置および実体不在の問題）。
- **未確認事項**: `REGISTRY_SCHEMA_v1.0.md`の2箇所複製が意図的な配布用複製か更新漏れかは未確認。`KN_SERIES_LEDGER`が将来動的生成される設計であることを裏付ける文書は発見できなかった（第6節）。
- **博士判断が必要な理由**: どちらを正本とするか、複製の扱い、`KN_SERIES_LEDGER`／`Atlas`の今後の扱い（実装を待つか、概念自体を見直すか）は、Registry Series設計の方針に関わる意思決定であり、事実収集・評価の範囲を超える。

### 論点D: 文書参照の問題

**論点**: 制度文書間の相互参照・統合が未了のまま並立している箇所がある。

- **影響範囲**: TERM-001とVOCABULARY_CONSTITUTION_v0.1の統合未了（自己申告済み）。VOCABULARY_CONSTITUTION_v0.1のApproval（Human Gate）項目がdocs/audits配下の10件監査シリーズを参照していない。Source・Catalogの禁止事項欄が「未確認」のまま用語集に掲載。
- **関連文書**: `TERM-001_REGISTRY_TERMINOLOGY.md`、`VOCABULARY_CONSTITUTION_v0.1.md`、`docs/audits/MOCKA_HUMAN_GATE_*_AUDIT_v1.md`系列。
- **関連モジュール**: なし（文書間の参照関係の問題）。
- **未確認事項**: 「次回TERM-001改訂時に合わせて解消するのが効率的」（`VOCABULARY_PATTERN_AUDIT_TARGET_LIST_v0.1.md`第3部記載）が、実際にいつ・誰によって着手される予定かは確認していない。
- **博士判断が必要な理由**: どの文書を統合の起点とするか、統合の時期をいつにするかは制度運営上の判断であり、事実収集・評価の範囲を超える。

### 論点E: 実装構造の問題

**論点**: 同一名称を持つ複数の実装が、物理的に異なるモジュール・ディレクトリに分散して存在する。機能的な衝突は本調査の範囲では確認されなかったが、構造として同名の実体が複数箇所に存在する状態そのものは残っている。

- **影響範囲**: `phi_os/human_gate.py`・`semantic/query_engine/human_gate.py`（相互import・循環なしを静的解析で確認済み）。`core_kernel/core_store/capability_registry.py`・`interface/ai_capability_registry.py`・`PlanningCaliber/workshop/seo-os/caliber/capability_registry.py`（`gateway/connector_router.py`が前2者を同時利用）。
- **関連文書**: 各実装が個別に参照する設計文書（`docs/governance/control_map_v2.md`、`docs/contracts/phase7_b6_human_gate_ruling_v1.md`）。
- **関連モジュール**: 上記5ファイル、および利用元の`phi_os/migrate_prevention_queue.py`、`semantic/query_engine/human_gate_interface.py`、`semantic/query_engine/observation_surface.py`、`gateway/connector_caliber.py`、`gateway/connector_router.py`、`interface/proposal_schema.py`。
- **未確認事項**: 静的import解析のみで確認しており、動的ディスパッチ（`importlib`等）による呼び出しの有無は未検証。Ledger4候補・Archive3層・Caliber6系統など、Human Gate／capability_registry以外の同名異義候補については呼び出し関係の相互参照確認そのものを行っていない。
- **博士判断が必要な理由**: 現状の分散構造を維持するか、将来的な整理・命名変更等を検討するかは実装方針の判断であり、事実収集・評価の範囲を超える。

### 論点F: ガバナンス証跡の問題

**論点**: 一部の大規模な成果物が、MoCKAの記録義務（mocka_write_event）を経ずに追加されている。

- **影響範囲**: `docs/reference/semantic_dictionary/raw/`配下7ファイル（`all_terms.json` 282MB等）。
- **関連文書**: なし（記録が存在しないこと自体が論点）。
- **関連モジュール**: `docs/reference/semantic_dictionary/raw/`配下の`all_terms.md`／`all_terms.json`／`category_candidates.md`／`duplicate_candidates.md`／`phrase_frequency.md`／`synonym_candidates.md`／`unused_terms.md`の7ファイル。
- **未確認事項**: GitHub側のPR・Issueでの言及有無は本セッションでは未確認（GitHub接続待ち）。同様に記録を経ずに追加された成果物が他に存在するかは、本監査の対象語彙（19語＋関連候補）に関連する範囲でのみ確認しており、リポジトリ全体を悉皆調査したものではない。
- **博士判断が必要な理由**: 過去に遡って記録を補完するか、当該成果物の位置づけ（正式な制度成果物として扱うか、参考データとして扱うか）を確定するかは、記録原則の遡及適用に関わる制度判断であり、事実収集・評価の範囲を超える。

---

## 12. Step4確認: 優先順位付けを行っていないことの確認

以下を明示的に確認する。

- 論点A〜Fについて、どれを先に対応すべきかという優先順位は記載していない。
- スコアリング・ランキング・重要度判定・緊急度判定のいずれも行っていない。
- 各論点の記載順（A〜F）は評価対象一覧（第10節の表）に現れた順であり、重要度の序列を意味しない。
- 改善案・対応方法・ロードマップ・実装案は一切記載していない。
- 上記をもって完了条件（評価理由の明文化・論点の分類・博士が裁定すべき事項の明確化・改善案/優先順位/採否判断の不記載）を満たしたと判断し、R01の役割を終了する。最終裁定はきむら博士に委ねる。

---

## 改訂履歴

- v0.1（2026-07-04）: きむら博士のご質問8項目に基づき新規作成。Human Gate 2実装・capability_registry 3実装のコード読了、KN_SERIES_LEDGER/Atlasの動的生成根拠文書の不在確認、semantic_dictionaryのgit履歴追加確認を経て、層別評価表を提示。くろこ起草。
- v0.2（2026-07-04）: きむら博士の査読指摘3点を反映。①評価基準(A〜D)を第0節として明文化。②Human Gate・capability_registryの呼び出し関係（静的import解析）を実施し第2・3節に追記、実装整合性の注記を更新。③命名ガバナンス軸を第8節として新設(D評価)、NAMING_CONVENTION.mdの適用範囲外であることを全170行読了の上で確認。④未確認事項を第9節として独立記載。設計思想(B)の根拠を明記し、層別評価表に命名ガバナンス行を追加。くろこ起草。
- v0.3（2026-07-04）: くろこ指示書（VOCABULARY_AUDIT_EVALUATION v0.3作成指示）に基づき改訂。Step1: 評価結果(A〜D)は変更せず、第10節の理由を具体的な件数・ファイルパス・文書名まで一段具体化。Step2/3: 発見事項を論点A〜F（命名統治・索引管理・正本管理・文書参照・実装構造・ガバナンス証跡）として第11節に整理し、各論点について影響範囲・関連文書・関連モジュール・未確認事項・博士判断が必要な理由のみを記載（改善案・優先順位は不記載）。Step4: 優先順位付け・スコアリングを行っていないことを第12節で明示的に確認。本改訂をもってR01の役割を終了し、最終裁定をきむら博士へ委ねる。くろこ起草。

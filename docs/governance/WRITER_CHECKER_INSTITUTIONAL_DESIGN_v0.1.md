# Writer/Checker Institutional Design v0.1

位置づけ: くろこ並行作業指示（2026-07-03）Task-Bに基づき新規作成。DECISION_POLICY_v0.1.md / EXTERNAL_KNOWLEDGE_ADOPTION_POLICY_v0.1.mdと同形式で管理する外部ファイル（参照可能・監査可能・差分追跡可能）。

本ファイルはコードではなく制度設計文書である。実装は一切含まない。EXTERNAL_KNOWLEDGE_ADOPTION_POLICY_v0.1.md 2.3節で「保留（Hold）または実験対象」と暫定分類されたWriter/Checker案件について、GL7との役割分担とHard Gate範囲を明確化し、再分類の材料を提供することを目的とする。

---

## 第1部: 現状把握

### 1.1 GL7（execution_governance.py / governance_pipeline.py）の実際の中身

`docs/governance/gl7_execution_kernel_spec_v1.md`（Status: CONFIRMED、実コードからの抽出）を読み込んだ結果、以下が確認できた。

- GL7の責務は「推論が正しくてもRepositoryを破壊しないための実行制御」のみであり、データの正しさは見ない。「この行為（tool呼び出し）を実行してよいか」だけを見る事前ガードである（同spec 1節）。
- 固定順序: Task -> Grounding(GL1) -> Policy確認(GL1) -> Conflict検出 -> Dry Run -> Approval(Human Gate) -> Execute -> Verify（同spec 2節）。
- `governance_pipeline.py`が全Tool呼び出しの単一窓口であり、`before_tool()`がDefault Deny判定（READ_ONLY_TOOLS以外は全てDry Run対象）を行う（同spec 3-4節）。
- ABORT_CONDITIONSは5条件定義されているが、実際に発火するのは`grounding_not_completed` / `deletion_outside_scope` / `new_directory_detected` / `unexpected_file_count`の4条件のみ。`encoding_mismatch`は定義のみで発火ロジック未実装（同spec 6節、10.2）。
- FORBIDDEN_EXECUTIONS（8項目）は定義のみで、`check_abort_conditions()`を含むいずれの関数からも参照されておらず、コードレベルでは実効していない（同spec 10.1、REAL_GAPとして確定済み）。
- 重要な事実: 「Dry Run通過後のHuman Gate承認」は、`structural/`配下のいずれのファイルからも呼び出しコードが存在せず、現状実装されていない（同spec 10.3、10.4）。類似の別機構としてapp.pyのPREVENTION QUEUE + DECISION（`/decision/approve`・`/decision/reject`）が存在するが、GL7の`pre_execution_check()`とはコード上一切接続されていない。

結論: GL7は「事前ガード」として機能しているが、その事前ガードは「実行してよいレポジトリ操作か（破壊防止）」を判定するものであり、「実行した結果の正しさ・品質」は一切評価しない。Human Gateとの接続も未実装のギャップがある。

### 1.2 Decision Policy v0.1の責務境界とDecision Evidence

`docs/governance/DECISION_POLICY_v0.1.md`を読み込んだ結果、以下が確認できた。

- Decision Policyの責務境界（不変の制約）: 「判定するのみ」「実行しない」「保存しない」「Approvalを持たない」（同文書0節）。承認権（Approval）はHuman Approval Gateにあり、Decision Policyは委任されて動く下位アルゴリズムである。
- Decision Evidenceの制度用語定義（同文書4節）: 裁定について後続層（Execution・Audit）が制度的正当性を検証できる最小証跡。3主体構造は「生成主体=Decision Policy（裁定を行った主体自身）」「読者=event_gate（存在確認）/ Execution（実行判断の根拠）/ Audit（事後検証）」「検証主体=Execution・Audit」。
- event_gateはEvidenceの「存在確認のみ」を行い、内容検査は行わない（layer_2_constraint、同文書3節）。

### 1.3 既存CI workflows（.github/workflows/）の実態調査

6ファイルすべてを実際に読み込んだ。推測ではなく以下の実測結果に基づく。

| workflow | トリガー | 実行内容 | pytest | lint/typecheck |
|---|---|---|---|---|
| mocka_guard.yml | push/PR全件 | grep/findによる構造チェック（tempフォルダ・二重階層検出のみ） | なし | なし |
| mocka_regression.yml | push(main/master、パス限定)/PR/手動 | `reproduce_mocka.py`実行（ubuntu/windows）。サーバー試験はSKIP前提 | なし（reproduce_mocka.py内部にpytestがある可能性は本調査では未確認・要確認） | なし |
| phios_regression.yml | push/PR(phi-os配下パス限定)/手動 | `reproduce_phios.py`実行（docker/windows/macos）。macOSはcontinue-on-error | なし（reproduce_phios.py内部の詳細は未確認・要確認） | なし |
| canary_overrides.yml | 毎週月曜cron/手動 | `pytest tests/test_canary_overrides.py::test_override_evidence_gap_is_rejected_by_event_gate` を明示実行 | あり（1件のみ、OVERRIDES enforcement専用） | なし |
| phase18_determinism_matrix.yml | push(main) | `verify_chain.py`実行（ubuntu/windows x python3.12/3.13） | なし | なし |
| research-gate-demo.yml | 手動(workflow_dispatch)のみ | `tools/mocka_research_run.ps1`実行 | なし | なし |

`tests/`ディレクトリの実ファイルを確認したところ、`test_canary_overrides.py`と`test_gate_validator.py`の2件のみ存在する。`test_gate_validator.py`はいずれの既存workflowからも呼び出されていない（grep検索で該当なし）。

結論（本調査で確定できる事実のみ）:
- 全workflowを通じてlintツール（flake8/ruff等）・型チェッカー（mypy等）の実行は一件も確認できなかった。
- pytestが明示実行されているのはcanary_overrides.ymlの1テストケースのみ。
- 「Build」に相当するものはreproduce_mocka.py / reproduce_phios.py / verify_chain.pyという各領域の再現性検証スクリプトであり、汎用的なビルド手順ではない。
- reproduce_mocka.py等のスクリプト内部で追加のpytest実行やlintが行われている可能性は本調査の読み込み範囲（workflowファイルのみ）では確認できていない。断定せず「不明・要確認」とする。

### 1.4 MoCKAに既存する「事後評価」的仕組みの洗い出し

- `phi_os/audit_trigger.py`（TODO_323）: SQLite TRIGGERでGATE外からのINSERT/UPDATEを検知し、`audit_violations`テーブルへ記録する仕組み。「物理的封鎖ではなく迂回しても即検知」という制度的抑止力として設計されている（同ファイル冒頭docstring）。これは実行後の事後検知であり、Writer/Checkerの「事後客観評価」と機能的に近い先例である。
- `canary_overrides.yml`の`test_override_evidence_gap_is_rejected_by_event_gate`: OVERRIDES enforcementの3層構造（evaluation/constraint/audit）のうち、constraint層（event_gate）が正しく機能しているかを事後的に検証するカナリアテスト。CI定期実行（常駐監視プロセスは不採用、DECISION_POLICY_v0.1.md 3節）という設計判断が既に前例として存在する。
- `mocka_regression.yml` / `phios_regression.yml`: 「Proof of Reproducibility」を掲げる再現性検証。事後（コミット後）にシステム全体の動作を再現し記録する仕組みであり、個々のtool呼び出し単位ではなくシステム単位の事後評価である。
- Loop暴走防止3制約（`docs/caliber/LOOP_DESIGN_PRINCIPLES.md` 55-58行、122-126行）: 「同一問題への再試行: 最大3回。3回で復元率が向上しない場合 -> 強制停止 -> 人間介入を要求」という既存の制約が確定済みで存在する。これはWriter/CheckerのRetryループ上限設計と直接関連する先例である。

いずれも「Writer→Checker→Retry→Ledger」という一連のフローそのものは現状MoCKAに存在しない。個別要素（事後検知＝audit_trigger、事後検証＝canary test、再試行上限＝Loop暴走防止3制約）は存在するが、これらを一つの制度フローとして接続した前例は確認できなかった。

---

## 第2部: 提案

### 2.1 Writer -> Objective Checker -> Retry -> Ledger フローの制度設計

```
Task入力
    |
Writer（成果物生成）
    - 入力: Task仕様（人間またはくろこが定義したスコープ）
    - 出力: 成果物候補（コード差分・ドキュメント案等）+ 生成メタデータ（試行回数・入力ハッシュ）
    - 責任範囲: 「作る」のみ。自己採点・自己承認は行わない
    |
Objective Checker（客観評価）
    - 入力: Writerの成果物候補 + Hard Gate基準（2.3節）
    - 出力: PASS/FAIL判定 + 判定根拠（どの基準に照らしたか）
    - 責任範囲: 「判定するのみ」。実行しない。保存しない（Decision Policyの責務境界と同形の制約を課す。2.2節で詳述）
    - 「客観」の担保: Checkerが評価する基準はHard Gate（Build/Test/Lint/Type等の機械的合否基準）に限定し、Writer自身が定義した基準や主観評価は用いない
    |
Retry判定
    - FAILの場合: Writerへ差し戻す。上限は3回（2.5節で根拠を示す）
    - 3回到達してもPASSしない場合: 強制停止し、人間介入を要求（Loop暴走防止3制約と同形）
    |
Ledger記録
    - PASSまたは強制停止のいずれの場合も記録する（PASSのみを記録する設計は「都合の良い記録」になりmocka_write_eventの精神に反する）
    - 記録内容は2.4節で詳述
    |
Human Gate（最終確認）
    - Checker PASSは「次工程に進めてよい」という機械的合否のみを意味し、最終的な採用可否・マージ可否の決定ではない
    - この境界は2.2節で必須事項として扱う
```

### 2.2 GL7との役割分担の検証

EXTERNAL_KNOWLEDGE_ADOPTION_POLICY_v0.1.mdおよびくろこ指示が提示する「GL7=事前ガード、Checker=事後客観評価」という整理について、1.1節の事実確認を踏まえて検証する。

**成立するか: 成立する。ただし境界の明文化が必要。**

- GL7は「この行為（tool呼び出し）を実行してよいか」を実行前に判定する（gl7_execution_kernel_spec_v1.md 1節）。判定対象は「行為」であり「成果物の品質」ではない。
- Checkerは「生成された成果物がHard Gate基準を満たすか」を実行後（Writer出力後）に判定する。判定対象は「成果物」であり「行為の許可可否」ではない。
- 両者の判定対象（行為 vs 成果物）と判定タイミング（事前 vs 事後）が異なるため、責務は重複しない。

**重複の懸念点（指摘事項）:**

- GL7のFORBIDDEN_EXECUTIONSには「bulk_rewrite_without_diff_review」という項目が定義されているが、1.1節で確認した通りこれは実行経路に未接続（REAL_GAP）。Writer/Checkerフローで「diff review」に相当する機能をCheckerに持たせる場合、これはGL7が本来担うべきだった領域をCheckerが肩代わりする形になる。責務の重複ではなく「GL7の未実装部分をCheckerが補完する」関係として明文化すべきであり、将来GL7側のFORBIDDEN_EXECUTIONSが実装された場合は重複が生じうる点をここに記録しておく。
- GL7の「Dry Run通過後のHuman Gate承認」は未実装（1.1節、gl7_execution_kernel_spec_v1.md 10.3）。Writer/Checkerフローの「Human Gate（最終確認）」ステージが、GL7が本来持つべきだった機能を代替する形にならないよう、Writer/CheckerのHuman GateはGL7のexecution許可とは別軸（成果物の採否）であることを明記する。

### 2.3 Hard Gateの範囲定義

1.3節の実測結果に基づき、以下のように定義する。推測による要否判断は行わない。

| 項目 | Hard Gate必須化 | 根拠 |
|---|---|---|
| Test（pytest） | 必須。ただし「既存の該当テストを実行し、既存テストを壊していないこと」の確認に限定する | canary_overrides.ymlで既にpytest実行の前例があり、既存の合否判定の仕組みとして機能している。ただしtests/配下は現状2ファイルのみで、test_gate_validator.pyはどのworkflowからも呼ばれていない（1.3節）ため、「新設した成果物に対応するテストが存在しない」ケースが常態化しうる。この場合Checkerは「テストが存在しないため判定不能」を明示し、FAILではなく別区分（判定保留）として扱う必要がある |
| Build | 必須（ただしMoCKAには汎用的な「ビルド」工程が現状存在しない） | 1.3節の通り、reproduce_mocka.py / reproduce_phios.py / verify_chain.pyが実質的なBuild+検証を兼ねている。Writer/Checkerが対象とする成果物がこれらのスクリプトのスコープ内（schema/, runtime/governance/, phi-os/等）であれば、該当workflowの実行成否をHard Gateとする。スコープ外の成果物（例: 本ドキュメントのような単発Markdown）にはBuild概念自体が適用されない |
| Lint | 必須にしない（現状不採用） | 1.3節の実測により、6workflow中いずれもlintツールを実行していないことを確認した。既存の合否基準が存在しない領域を新規にHard Gate化することは、Checker導入と同時に新たな不確定要素を持ち込むことになるため、v0.1では見送る。将来lintワークフローが新設された場合に再評価する |
| Type | 必須にしない（現状不採用） | Lintと同じ理由。型チェッカー実行は6workflowいずれにも存在しない |
| 構造チェック（mocka_guard.yml相当） | 必須 | 既に全push/PRに対して稼働している最も基礎的な合否基準であり、Writer成果物にも当然適用されるべき既存ゲートである |

結論: v0.1のHard Gateは「既存テスト（該当する場合）」「該当スコープの再現性検証スクリプト（該当する場合）」「構造チェック（mocka_guard.yml相当）」の3種に限定し、Lint/Typeは既存インフラが存在しないため対象外とする。これは「既存の実態を根拠にする」という指示に基づく判断であり、Lint/Typeの有用性を否定するものではない。

### 2.4 Ledgerの記録粒度

DECISION_POLICY_v0.1.md 4節のDecision Evidence 3主体構造との整合を意識し、以下のように設計する。

- 生成主体: Objective Checker（判定を行った主体自身が証跡を生成する）。Decision Evidenceの「生成主体=Decision Policy」と同形の設計とし、Writerが自らの成果物についてPASS証跡を生成することは禁止する（自己証明の禁止）。
- 読者: event_gate相当（Ledger記録の存在確認）/ Human Gate（最終確認の根拠として参照）/ Audit（事後検証）。Decision Evidenceの読者構造をそのまま踏襲する。
- 検証主体: Human Gate・Audit。Checker自身は検証主体に含めない（Checkerの判定結果を無条件に最終確定として扱わない。2.6節で詳述）。

記録内容（1件のLedgerエントリに含めるべき最小項目）:
- Task識別子、Writer試行回数（1〜3）
- Checker判定結果（PASS/FAIL/判定保留）とその根拠（どのHard Gate項目で判定したか）
- FAILの場合は差し戻し理由の要約
- 3回到達後の強制停止か、PASSによる正常終了かの区別
- mocka_write_event経由での記録（author、tags等の既存フォーマットに準拠）

いずれの結果（PASS/FAIL/強制停止）も記録対象とする。これはEXTERNAL_KNOWLEDGE_ADOPTION_POLICY_v0.1.md 2.2節の「採用以外の判定結果も、判断自体を記録対象とする」という設計方針、およびMoCKA Constitutionの"Event ledger is append only"原則と整合する。

### 2.5 Retryループの上限

Loop暴走防止3制約（LOOP_DESIGN_PRINCIPLES.md 55-58行）の「同一問題への再試行: 最大3回。3回で復元率が向上しない場合 -> 強制停止 -> 人間介入を要求」に合わせ、Writer/CheckerのRetry上限も**3回**とする。

根拠: 異なる値を採用する積極的な理由が本調査では見当たらなかった。既存の確定済み制約と異なる値を設定すると、同種のループ制御が2つの異なる上限値で並存することになり、運用上の混乱（どちらの制約がどの場面に適用されるか）を招くリスクがある。既存前例への統一を優先する。

### 2.6 自律裁定化リスクの自己点検（必須事項）

くろこ指示の「AIが自身の判断を自身で確定させる自動承認ループを作らない」という原則に照らし、本設計案を自己点検する。

**懸念点:** 「Checkerの合格判定だけで人間確認なしに最終確定してしまう経路」が生じていないか。

**点検結果:** 2.1節のフロー図において、Checker PASSは「次工程に進めてよい」という機械的合否判定に留め、Human Gate（最終確認）を独立したステージとして必須で経由する設計とした。これはDecision Policy v0.1の責務境界（「判定するのみ」「Approvalを持たない」）と同形であり、Checkerに承認権（Approval）を持たせない設計である。

ただし、以下の点は本設計のv0.1時点で未確定であり、明示的に指摘する。

- Hard Gate（Build/Test/構造チェック）がすべてPASSした場合に、Human Gateを「形式的な追認」として扱う運用が定着すると、実質的にCheckerの判定がそのまま確定する自動承認ループと同じ結果になるリスクがある。これはコード上の経路の有無ではなく運用上のリスクであり、本ポリシー文書だけでは防げない。Human Gateが実質を伴うことを担保する仕組み（例: サンプリング監査、PASSであっても一定確率で人間が内容を確認する運用等）は本v0.1の設計範囲外であり、**要確認・今後の課題**とする。
- GL7のDry Run通過後のHuman Gateが未実装である（1.1節）のと同様の欠落が、Writer/Checkerフローでも「設計上はHuman Gateを経由すると書いているが、実装時に接続されない」形で再発するリスクがある。実装フェーズに進む場合は、GL7-UNENFORCED-CONDITIONS-BUGの再発防止の観点から、Human Gateへの接続を「定義するだけでなく実行経路として検証する」テスト（canary_overrides.ymlの前例に倣う）を合わせて設計することを推奨する。

**結論:** v0.1の設計自体はHuman Gateを必須ステージとして明記しており、コード上の自動承認ループを意図的に作る設計にはなっていない。ただし上記2点（運用上の形骸化リスク、実装時の未接続リスク）は本文書のみでは解消できないため、「保留」を完全に解消するものではなく、次のHuman確認事項として引き継ぐ。

---

## 第3部: 未確定事項（要確認）

- reproduce_mocka.py / reproduce_phios.py内部で追加のpytest実行やlintが行われているかは、workflowファイルの読み込みのみでは確認できていない。実装検討時にスクリプト本体の確認が必要。
- Checkerの「判定保留」区分（対応テストが存在しない場合）の具体的な運用ルールは本v0.1では骨子のみで、詳細設計は未着手。
- Human Gateの形骸化防止策（サンプリング監査等）は設計範囲外とした。次フェーズの検討事項とする。
- Writer/Checkerを実際にどのtool・どの成果物種別に適用するか（対象スコープ）は、本文書では未定義。EXTERNAL_KNOWLEDGE_ADOPTION_POLICY_v0.1.mdのStep 3（Human Gateによる最終確認）を経て確定すべき事項とする。

---

## 改訂履歴

- v0.1（2026-07-03）: くろこ並行作業指示Task-Bに基づき新規作成。

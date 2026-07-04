# CI Failure Analysis v0.1 (Analysis-03)

位置づけ: R01分析指示書v1.0 Analysis-03に基づく。入力資料は`CI_FAILURE_FACT_COLLECTION_MOCKA_GLOBAL_RULE_GUARD_v0.1.md`のみとし、新規調査は行っていない。分析対象はStep3失敗の事実・Workflow構造・Rule Guardの役割・失敗継続の背景に限定する。修正方法・Workflow変更・実装修正・GitHub設定変更・原因断定は対象外とし、事実から読み取れる範囲で分析を終了する。他のAnalysis（Vocabulary Audit／Cross Reference）とは独立に扱い、それらの結論をここでの分析根拠として用いていない。

---

## 1. 確認できた事実（CI Failure Fact Collectionより、要約引用）

- workflow「MoCKA Global Rule Guard」は単一ジョブ`rule-check`のみで構成される。
- ジョブは4ステップ（Set up job／Checkout／Validate MoCKA Structure／Post Checkout／Complete job）からなり、失敗するのは常に「Validate MoCKA Structure」（ステップ3）である。認証・Checkout・fetchの各処理は成功として記録されている。
- ステップ3は`grep -r "mocka_v0.1" --include="*.py" --include="*.md" -l .`を実行し、一致があれば「RULE VIOLATION: temp folder detected」と出力して`exit 1`する。同様に`mcp/mcp`・`relay/relay`・`event/event`という3種のディレクトリ二重ネストパターンも検査対象になっている。
- 直近実行・最古実行（2026-06-22T01:58:20Z）とも、grepの一致箇所は`./docs/mocka_global_rules.md`であり、同ファイル19行目に`- mocka_v0.1`という記載が現在も存在する。
- workflowの記録済み全実行（total_count=700、2026-06-22T01:58:20Z〜2026-07-04T00:03:11Z）のうち、成功（conclusion=success）は0件。全件が同一の失敗パターンを示す。
- ステップ「Post Checkout」で`fatal: No url found for submodule path 'PlanningCaliber/sirius-lab-products' in .gitmodules`という別のgit警告（exit code 128）が発生しているが、当該ステップはconclusion=successであり、ジョブ全体の失敗（ステップ3のexit 1）とは別事象として記録されている。

## 2. 事実から導かれる分析

### 2-1. Step3失敗の機構

ステップ3の失敗は、シェルスクリプトが明示的に実行する`exit 1`によるものであり、外部要因（ネットワーク・認証・GitHub側の障害等）によるジョブの異常終了ではない。スクリプトは`grep -r "文字列" ... .`という単純な全文字列検索を用いており、検索対象がコードとして書かれた実体（例: 実際に存在する一時フォルダ名）であるか、文書内でその文字列に言及しているだけの記述（例: 命名規則を説明する文中の例示）であるかを区別しない。この検索方式の性質自体は、ログ上の一致箇所がドキュメントファイル（`docs/mocka_global_rules.md`）であるという事実と整合する。

### 2-2. Workflow構造の特徴

このworkflowは`on: push, pull_request`で発火し、単一ジョブ・単一ステップ（実質的なチェック本体）という単純な構造を持つ。ジョブ内に条件分岐や除外パス設定（例: 特定ファイルを検査対象から除外する仕組み）は、収集された事実（ワークフロー定義全文）の範囲では確認されなかった。

### 2-3. Rule Guardの役割（記載内容から読み取れる範囲）

ステップ名「Validate MoCKA Structure」および出力メッセージ（"RULE VIOLATION: temp folder detected" / "double nesting detected"）から、本workflowの役割は「一時フォルダ的な命名規則違反」および「ディレクトリの二重ネスト」という、MoCKAの構造規約からの逸脱を検出することにあると読み取れる。これは、本Fact Collectionとは別に、これまでの一連の監査（Vocabulary Audit等）で繰り返し確認されてきた「野良フォルダ・二重階層・命名の混乱」という同種の懸念領域と、名称上・目的上、対応関係にあるように読み取れる（ただし、この対応関係の実質的な有効性・カバレッジについては本分析の範囲外とする）。

### 2-4. 失敗継続の背景（時系列的特徴）

記録が存在する全期間（2026-06-22〜2026-07-04、約12日間、700実行）を通じて、成功が1件も記録されていない。この期間中、実行間隔はおおむね10分前後（例: 22:52:43→23:02:47→23:12:51等の連続する実行時刻から算出）であり、高頻度な自動トリガー（push起因、"auto sync"という命名のコミットに紐づく）によって同一の失敗が反復して記録され続けてきたことが、実行ログの時系列から読み取れる。この「高頻度な自動実行×一貫した失敗」という組み合わせ自体が、記録上の特徴として観測される。

### 2-5. 別事象（exit code 128）との構造的分離

ステップ3の失敗（exit 1）と、Post Checkoutステップの警告（exit 128、submodule関連）は、実行ログ上明確に異なるステップに帰属しており、Actions側の集計（ステップ単位のconclusion）でも両者は独立して記録されている。2つの異なる終了コード・2つの異なるエラーメッセージが同一run内に同居している状態そのものが、本Fact Collectionから確認できる構造的特徴である。

## 3. 未確認事項

- ステップ3のgrepパターンが、ドキュメント内の言及とコード実体としての一時フォルダを区別する設計になっているかどうかは、ワークフロー定義の文言そのもの（区別する分岐が見当たらない）以上には確認していない。
- `docs/mocka_global_rules.md`の19行目`- mocka_v0.1`という記載が、いつ・どのような経緯で追加されたか（本行自体の作成日時・作成意図）は、CI Failure Fact Collectionの範囲では確認されていない。
- workflow定義ファイル（`.github/workflows/mocka_guard.yml`）自体の変更履歴（このgrepパターンや対象パターンがいつ設定されたか）は、Fact Collectionの範囲では確認されていない。
- 700件より前の実行記録（total_countの範囲外）が存在するかどうかは、GitHub API側の保持期間・仕様に依存し、本分析では確認できない。

## 4. 博士判断が必要な事項

- 本workflowの検出方式（文字列一致による一時フォルダ検出）が、ドキュメント内の言及も一律に検出する設計を意図したものか、区別を要する設計上の課題であるかは、Rule Guardの制度上の役割・設計意図に関わる判断であり、本分析の範囲を超える。
- `docs/mocka_global_rules.md`19行目の記載を維持するか、workflow側の検査方式を見直すか、あるいは双方をそのまま維持するかは、実装・運用上の判断であり本分析では行わない（指示書により明示的に対象外とされている）。
- 700件・約12日間にわたり成功実績が0件という状態を、どの時点まで遡って制度上の懸案として扱うか（記録の遡及確認範囲）は、きむら博士の判断事項である。

---

## 改訂履歴

- v0.1（2026-07-04）: R01分析指示書v1.0 Analysis-03に基づき新規作成。入力資料はCI_FAILURE_FACT_COLLECTION_MOCKA_GLOBAL_RULE_GUARD_v0.1.mdのみ。くろこ起草。

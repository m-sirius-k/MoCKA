# Phase10-3 Human Gate Decision Brief v1

Status: DECISION BRIEF（既存5監査資料の圧縮統合のみ。採択禁止・
推奨禁止・結論禁止・契約作成禁止・実装禁止・コード変更禁止）
Date: 2026-06-24

本文書は以下5資料の内容を、Human Gateが論点1〜3を裁定できる単一
資料へ圧縮統合したものである。新たな分析・評価軸の追加は行わず、
既存資料の事実のみを再配置する。

```
入力資料:
1. PHASE10_3_REASONING_DEFINITION_COMPARISON_v1.md
2. PHASE10_3_CANDIDATE_AUTHORITY_MATRIX_v1.md
3. PHASE10_3_PROJECTION_BOUNDARY_MATRIX_v1.md
4. PHASE10_3_DECISION_DEPENDENCY_MAP_v2.md
5. PHASE10_3_LONG_TERM_INSTITUTIONAL_AUDIT_v1.md
```

---

## 論点1: Reasoning Definition

### Option一覧

```
Option A: Reasoning = 候補生成主体
Option B: Reasoning = 候補生成＋候補派生主体
Option C: Reasoning = 意味的推論主体（候補生成は結果の一部）
```

### Option A の利点

```
- 定義・権限が単一操作(generate)のみで最も単純、現在断面では
  最小権限原則に最も高く整合する。
- Observerとの違いが「生成権限の有無」という単一軸で説明でき、
  将来も比較的安定。
- 生成物が単純なため、現在断面ではHuman Gateの裁定材料も単純。
```

### Option A のリスク

```
- Projection層（Phase9 SemanticProjectionLayer）との機能重複が
  3 Option中最大。
- Advisorに禁止された操作（新規候補生成）をReasoningに許可する
  形になり、Advisor/Reasoningの機能境界が事実上消滅しうる。
- 長期的にはProjection層との重複が固定化し、Reasoning Nodeが
  事実上Projection層の代替・拡張になっていく構造的傾向がある。
- Phase11以降、生成頻度・生成規模が拡大した場合、Human Gateの
  裁定対象数が線形に増加し続ける構造的リスク。
```

### Option A の未解決事項

```
- 入力仕様が既存文書に明記なし（未確定）。
- 将来Observerの役割が「観測+簡易説明」へ拡張された場合、
  生成権限の有無のみでは境界が説明しきれなくなる可能性。
```

### Option B の利点

```
- Option Aの生成権限に加え既存candidateからの派生（derive）を
  扱えるため、候補生成が主目的だがOption Aより表現力が高い。
- Model A〜D（論点2）のうちModel B（generate+derive）と定義が
  直接対応する。
```

### Option B のリスク

```
- Advisorの「代替候補提示」とReasoningの「候補派生」が表面上
  類似するため、Advisorとの機能境界がOption Aより不明瞭。
- 候補生成＋候補派生の両方がcollisionを生む可能性を持ち、
  問題化範囲がOption Aより広い（生成由来＋派生由来の両方）。
- 派生履歴が世代を経るごとに、Human Gateが各世代の出自を
  遡って検証する負荷がPhase経過に応じて増加。
- 「派生」の定義が将来expand/reconstruct（論点2 Model C/D）と
  地続きになり、論点1と論点2の定義が将来分離不能になっていく
  リスクがある。
- 「生成+派生」という複数性質の操作を最初から持つため、将来の
  権限追加への抵抗が構造的に低い（前例が将来の拡張を正当化
  しやすい）。
```

### Option B の未解決事項

```
- 派生(derive)が「candidate merge」（Phase9-2恒久禁止）に
  該当しないことの境界確認が既存文書では未確定。
- 派生元candidateがPhase9生成物である前提が将来固定化すると、
  Reasoningが実質的にPhase9-3Aの「内部拡張」として機能してしまう
  リスクの解消方法が未確定。
```

### Option C の利点

```
- 候補生成が主目的でないため、論点2のModel A〜Dいずれを選んでも
  Option Cの定義との直接的な矛盾は生じにくい。
- Projection層の責務（候補生成そのもの）との分離が他のOptionより
  明確になる可能性がある（Projectionとの境界: 最も遠い）。
- 抽象度の高い定義は将来のPhase（Drift解釈の自動化等）を
  吸収しやすい。
```

### Option C のリスク

```
- Advisorとの機能重複が3 Option中最大（Advisor役割2-4「候補の
  説明/代替案の提示/矛盾点の指摘」との重複が最も大きい）。
  Advisor/Reasoningの境界が最も不明瞭になるリスク。
- Human Gateへの提示物が「候補」ではなく「解釈・関係性の説明」に
  なる場合があり、Phase7-B6裁定タイプ（accept/reject/defer/
  split）が候補単位の裁定を前提としている既存構造との接続が
  新たな論点になる。この不整合はPhase経過に応じて累積しうる。
- 抽象度の高い定義は、将来「解釈」の名目のもとに実質的な操作
  権限が追加されやすい。
- 誤った解釈がHuman Gateの裁定材料そのものを汚染するリスクが
  あり、被害がReasoning Node単体を越えてHuman Gateの判断品質
  全体に波及しうる（3 Option中、制度崩壊時の被害半径が最大）。
```

### Option C の未解決事項

```
- 入力・出力の具体的仕様が既存文書では未確定。
- 「最小権限原則」を操作単位ではなく解釈単位でどう評価するか、
  評価方法自体の再定義が将来必要になる可能性。
- Human Gateへの提示物形式（解釈・関係性中心）と既存裁定タイプ
  （候補単位）との接続方法が未解決。
```

---

## 論点2: Candidate Authority

### Model一覧

```
Model A: generateのみ
Model B: generate + derive
Model C: generate + derive + expand
Model D: generate + derive + expand + reconstruct
（Model A ⊂ Model B ⊂ Model C ⊂ Model D の累積構造）
```

### Model A の利点

```
- 最小権限原則に最高評価（操作1種のみ）。
- Human Gate保護能力が高い（生成物が単純なため裁定材料も単純、
  将来も安定）。
- Projection衝突率・誤作動時被害範囲ともに低い。
```

### Model A のリスク

```
- Projection侵食リスク（PHASE10_3_LEAST_AUTHORITY_AUDIT_v1.md
  指摘の評価軸、本文書のProjection衝突率とは別軸）は逆に最高。
  操作数の少なさが全観点での安全性を保証しない非単調な傾向。
- Projection層との重複を解消しない限り、長期的な権限肥大化の
  圧力は常に残る。
```

### Model A の未解決事項

```
- 「最小だが重複」という一見矛盾した評価（最小権限原則は最高
  だがProjection侵食リスクは最高）の解釈・解消方法が未確定。
```

### Model B の利点

```
- 論点1 Option Bと定義が直接対応する。
- メタデータ付与等を伴わない範囲では、Model C/Dより制度整合性が
  高い。
```

### Model B のリスク

```
- Human Gate保護: 派生履歴の追跡が必要になり、裁定時の参照情報量
  がPhase経過に応じて増加。
- Projection衝突率: 派生candidateが既存candidateと矛盾する場合、
  collisionが増える。
- 誤作動時被害範囲: 派生元candidateの誤りが派生先candidateに
  伝播する。
- 前例（複数操作許容）が将来の追加操作への抵抗を弱める。
```

### Model B の未解決事項

```
- deriveの起点として許される既存candidateの範囲（何を派生の
  起点に許すか）が将来Phaseで段階的に拡大しうる点の歯止めが
  未確定。
```

### Model C の利点

```
- メタデータ付与のみであれば同一性は変えないため、Human Gate
  保護能力は4 Model中最高（裁定負荷は最小）。
- Projection衝突率も低い（candidate自体の矛盾構造を変えない）。
- 誤作動時被害範囲も低〜中（メタデータの誤りのみでcandidate
  構造自体は不変）。
```

### Model C のリスク

```
- 制度整合性は低い。「変更ではなく付与」という説明が将来Phaseで
  拡大解釈され、実質的な変更権限へ横滑りするリスク。
- メタデータ変更権限が将来「意味の再定義権限」へ拡大解釈される
  構造的リスク（Semantic Layer侵食リスク: 中）。
- 前例3操作が将来「expand範囲の拡張」を正当化しやすい。
```

### Model C の未解決事項

```
- メタデータがProjection層のwhy_generated等の出力構造と将来
  重複・競合するかどうかが未確定。
- Observerの集計機能との将来的な重複可能性（メタデータ付与が
  「観測の一種」と解釈される余地）が未解決。
```

### Model D の利点

```
- 機能的な拡張性は4 Model中最高（複数candidateの組合せまで
  対応可能）。
```

### Model D のリスク

```
- 最小権限原則: 最低評価（操作4種）。
- Human Gate保護能力: 最低。複数candidateの合成結果は出自が
  混在し、Human Gateが「何が元の候補で何が合成結果か」を区別
  する負荷が最大。
- Projection衝突率: 最高（複数candidateの組合せは新たな矛盾を
  生む可能性が最大）。
- 誤作動時被害範囲: 最高（合成結果の誤りが「どのcandidateから
  影響が始まったか」を遡及不能にする可能性）。
- 「candidate merge」（Phase9-2恒久禁止）との境界が4 Model中
  最も不明瞭。
- 4操作という前例が将来「expand範囲の拡張」「reconstruct後の
  自動採択」等への段階的拡張を正当化しやすい最も強い前例。
```

### Model D の未解決事項

```
- reconstructとcandidate merge（恒久禁止）の運用上の判定基準が
  既存文書では未確定（同一視されうるリスクが指摘済みのみで
  判定方法自体は未解決）。
```

---

## 論点3: Projection Boundary

### Case一覧

```
Case A: Projection内部
Case B: Projection後段
Case C: Projectionとは独立
```

### Case A の利点

```
- （既存資料に積極的な利点の記載は無し。比較表上、相対的な
  利点として記載されている項目は無い。）
```

### Case A のリスク

```
- Projectionとの重複が最大。Phase9-2で確定済みのメソッド署名を
  変更せずに内部統合できるかという前提問題があり、解決されない
  限り実現可能性自体が評価できない。
- Observerとの重複: 低（既存Node配置パターンの外側にあるため、
  将来の境界説明が常に特殊扱いを要する）。
- Semantic Layer侵食リスク: 最大。Phase9-3A Ranking Policyの
  適用範囲拡張が、Phase9-3A自体の改変圧力として固定化する。
- 制度崩壊時の被害半径: 最大。Projection層内部の誤作動が
  Meaning Generation層全体（Phase7-A以降の全機能）に及ぶ可能性。
- 内部統合という前例が、将来「他の層も内部統合する」という
  拡張要求を正当化しやすい最も強い前例になる（権限肥大化
  リスク: 高）。
```

### Case A の未解決事項

```
- Phase9-2/Phase10-0で禁止済みの「既存メソッド署名変更」の
  対象範囲にProjection層内部への統合が含まれるかという解釈問題
  が未解決。
```

### Case B の利点

```
- Phase10-1/10-2が既に確立した「後段Node」パターン
  （Observer/Advisorと同型配置）をそのまま適用できる。
- 4観点（Projection重複・Advisor重複・Observer重複・侵食
  リスク）の比較表でいずれも既存パターンとの整合性が最も
  高く出ている（観察、優劣の結論ではない）。
- Human Gate保護能力: 高（既存のHuman Gate依存関係確認パターン
  をそのまま適用しやすい）。
- 後段Nodeの誤作動はPhase9層の出力を汚染しない構造的な防火壁が
  将来も維持されやすく、制度崩壊時の被害半径は中程度に留まる。
```

### Case B のリスク

```
- Advisorとの重複が最大（既存candidate群を受け取る点でAdvisorと
  同型配置のため）。将来双方の機能拡張のたびに重複が再検証を
  要する。
- Source分類（Source-A/B/C）拡張のたびに既存candidate群の
  受け渡し方法を将来も再確認する必要が生じる。
```

### Case B の未解決事項

```
- Reasoning固有のcandidate生成（論点1のB-1等）を行う場合、
  その生成がPhase9-3Aの分類の外側で発生する点の整理が未解決。
```

### Case C の利点

```
- Projectionとの重複が最小。Phase9層への直接依存が無くなる
  ため、将来Phase9層の変更による影響を受けにくい。
- Advisorとの重複: 低〜中（独自経路のため、Advisorが扱う既存
  candidate群との関係が薄い）。
- Observerとの重複: 低。
```

### Case C のリスク

```
- 独自candidateを生成する場合、Phase9-3A Source分類の外側に
  第4のSourceとして並立するリスク。
- Phase9-3A原則（Projection層主体で記述）を独立経路に同一文言で
  適用できるかが未解決のまま残り、Semantic Layer解釈の揺れを
  生む可能性。
- 独立経路自体がHuman Gateの裁定対象として将来増える分、
  制度全体の監査範囲が拡大し続ける。
- 「独立性」と「既存制度との接続コスト」が表裏の関係にあり、
  既存パターンほどの抑制構造を持たないため将来の権限肥大化に
  対する歯止めが弱い。
```

### Case C の未解決事項

```
- Phase7-B6既存裁定タイプとの接続を別途設計する必要があるが
  方法は未確定。
- 独立経路で生成されるcandidateの構造（フィールド定義等）が
  Phase9-3A生成物とどう整合するかが未確定。
```

---

## 依存関係まとめ

```
（PHASE10_3_DECISION_DEPENDENCY_MAP_v2.mdより）

Reasoning Definition（論点1）
├─ Candidate Authority（論点2）
├─ Projection Boundary（論点3）
│
├─ Collision Amplification（論点4）
└─ Advisor/Reasoning Separation（論点5）

- 論点1は論点2〜5すべての上位論点。
- 論点2・論点3は論点1から直接波及するが、論点2・3相互間の
  依存は確認されていない（並列関係）。
- 論点4・論点5は論点1単独ではなく、論点1・2の裁定結果を前提
  とする（論点1・2裁定後の再評価が必要）。

（PHASE10_3_LONG_TERM_INSTITUTIONAL_AUDIT_v1.mdより、組合せ時に
追加検証を要する観察事項）

- 論点1 Option A/B + 論点3 Case A: Semantic Layer侵食リスクが
  単純合算以上に拡大する可能性。
- 論点1 Option B + 論点2 Model C/D: 論点1と論点2の定義境界が
  将来分離不能になる可能性が単独評価より高い。
- 論点1 Option C + 論点3 Case C: Human Gate保護能力への負荷が
  複合する可能性。
```

## 裁定後に解決される論点

```
- 論点1〜3それぞれについて、どのOption/Model/Caseを選ぶかが
  確定する（構造上の選択そのもの）。
- 論点1の裁定により、論点2・論点3それぞれの「定義との整合性が
  取れる選択肢」の範囲が絞られる（PHASE10_3_DECISION_
  DEPENDENCY_MAP_v1/v2の波及関係に基づく）。
- 論点1・論点2の裁定が完了することで、論点4
  （Collision Amplification）・論点5（Advisor/Reasoning
  Separation）の再評価着手条件
  （PHASE10_3_DECISION_READINESS_REPORT_v1.md）が満たされる。
```

## 裁定後も残る論点

```
- 論点4（Collision Amplification）・論点5（Advisor/Reasoning
  Separation）自体は論点1〜3裁定後も未裁定のまま残る
  （再評価が必要な状態に移るのみ）。
- 各Option/Model/Caseの「未解決事項」節に記載した個別の論点
  （入力仕様未確定、reconstruct/merge判定基準未確定、Phase7-B6
  裁定タイプとの接続方法未確定等）は、選択したOption/Model/
  Case自体に付随する課題として裁定後も残る。
- phase10_3_reasoning_node_contract_v1.md本体の作成は、論点1〜3
  裁定後も別途実施が必要（契約作成は本文書の対象外）。
- Phase10-1/10-2のGit固定作業（候補A/B/C、PHASE10_FIXATION_
  PACKAGE_OPTIONS_v1.md）は論点1〜3の裁定とは独立した未決事項
  として残る。
- Phase9-3B（Intent Projection最小候補生成器の実装）は引き続き
  凍結状態のまま残る。
```

---

## 注記

本文書は既存5資料の事実を圧縮統合したものであり、新たな評価軸の
追加・採択・推奨・結論・契約作成・実装・コード変更のいずれも
行っていない。

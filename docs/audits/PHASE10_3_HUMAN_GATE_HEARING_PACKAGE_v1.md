# Phase10-3 Human Gate Hearing Package v1

Status: HEARING PACKAGE（既存事実の再整理のみ。採択禁止・推奨禁止・
契約作成禁止・実装禁止・評価追加禁止）
Date: 2026-06-24

本文書はPHASE10_3_HUMAN_GATE_DECISION_BRIEF_v1.mdを入力として、
Human Gate裁定セッションを実施可能な状態へ整理したものである。
新たな評価軸の追加は行わない。

---

# 第1部: 裁定対象一覧

```
論点1: Reasoning Definition
    対象: Option A / Option B / Option C
    内容: Reasoning Nodeの定義そのもの

論点2: Candidate Authority
    対象: Model A / Model B / Model C / Model D
    内容: Reasoning Nodeに許可するcandidate操作の範囲

論点3: Projection Boundary
    対象: Case A / Case B / Case C
    内容: Reasoning NodeとSemanticProjectionLayer(Phase9)の
          配置関係
```

---

# 第2部: 各論点の選択肢一覧

## 論点1: Reasoning Definition

### Option A: 候補生成主体

```
概要: ReasoningはEventCandidate/NLCandidateそのものを生成する
      行為主体である。

主な利点:
- 操作が単一(generate)のため最小権限原則に最も高く整合（現在断面）。
- Observerとの違いが「生成権限の有無」という単一軸で説明できる。

主なリスク:
- Projection層（Phase9）との機能重複が3 Option中最大。
- Advisorに禁止された操作をReasoningに許可する形になり、
  Advisor/Reasoning境界が事実上消滅しうる。
- 長期的にProjection層との重複が固定化し、Reasoning Nodeが
  Projection層の代替・拡張になっていく構造的傾向。

未解決事項:
- 入力仕様が既存文書に明記なし。
- 将来Observer役割拡張時の境界再説明が必要になる可能性。
```

### Option B: 候補生成＋候補派生主体

```
概要: Reasoningは新規候補の生成に加え、既存candidateからの派生
      （derive_candidate）も担う行為主体である。

主な利点:
- Option Aの表現力に派生を加え、論点2 Model Bと定義が直接対応。

主なリスク:
- Advisorの「代替候補提示」と「候補派生」が表面上類似し、
  Advisorとの機能境界がOption Aより不明瞭。
- collision問題化範囲が生成由来＋派生由来の両方に拡大。
- 派生履歴の世代増加に伴いHuman Gate裁定負荷がPhase経過で増加。
- 論点1と論点2(Model C/D)の定義境界が将来分離不能になるリスク。

未解決事項:
- derive操作がcandidate merge（恒久禁止）に該当しないことの
  境界確認が未確定。
- 派生元がPhase9生成物である前提固定化時のPhase9-3A内部拡張化
  リスクの解消方法が未確定。
```

### Option C: 意味的推論主体（候補生成は結果の一部）

```
概要: Reasoningの本質は候補間・観測結果間の意味的関係を推論
      することであり、候補生成はその派生的な出力に過ぎない。

主な利点:
- 論点2のいずれのModelを選んでも定義上の直接的矛盾が生じにくい。
- Projection層との分離が他Optionより明確になる可能性。

主なリスク:
- Advisorとの機能重複が3 Option中最大。
- Human Gateへの提示物が「解釈」中心となり、既存裁定タイプ
  （候補単位、Phase7-B6）との接続が新たな論点になる。
- 抽象度の高さゆえ将来「解釈」名目での権限追加が生じやすい。
- 制度崩壊時の被害半径が3 Option中最大
  （Human Gate判断品質全体への波及）。

未解決事項:
- 入力・出力の具体的仕様が未確定。
- 最小権限原則の評価方法（操作単位か解釈単位か）の再定義が
  必要になる可能性。
```

## 論点2: Candidate Authority

### Model A: generateのみ

```
概要: 操作1種（generate）のみを許可。

主な利点:
- 最小権限原則・Human Gate保護能力・Projection衝突率・
  誤作動時被害範囲のいずれも4 Model中最高評価。

主なリスク:
- Projection侵食リスク（別軸）は逆に最高（非単調な傾向）。
- Projection層との重複を解消しない限り、長期的な権限肥大化の
  圧力は常に残る。

未解決事項:
- 「最小だが重複」という評価の解釈・解消方法が未確定。
```

### Model B: generate + derive

```
概要: 操作2種（generate+derive）を許可。

主な利点:
- 論点1 Option Bと定義が直接対応。

主なリスク:
- Human Gate保護: 派生履歴追跡負荷がPhase経過で増加。
- Projection衝突率: 派生candidateと既存candidateの矛盾でcollision
  が増える。
- 誤作動時被害範囲: 派生元の誤りが派生先に伝播。
- 前例が将来の追加操作への抵抗を弱める。

未解決事項:
- deriveの起点として許される既存candidateの範囲の歯止めが未確定。
```

### Model C: generate + derive + expand

```
概要: 操作3種（generate+derive+expand）を許可。expandはcandidateに
      メタデータを付与する操作（同一性は変えない）。

主な利点:
- Human Gate保護能力: 4 Model中最高（メタデータのみで裁定負荷
  最小）。
- Projection衝突率: 低（candidate自体の矛盾構造を変えない）。

主なリスク:
- 制度整合性: 低。「変更ではなく付与」の説明が将来拡大解釈され、
  実質的な変更権限へ横滑りするリスク。
- メタデータ変更権限が「意味の再定義権限」へ拡大解釈される
  構造的リスク。

未解決事項:
- メタデータがPhase9の出力構造（why_generated等）と将来重複・
  競合するかが未確定。
- Observer集計機能との将来的重複可能性が未解決。
```

### Model D: generate + derive + expand + reconstruct

```
概要: 操作4種すべてを許可。reconstructは複数candidateの情報を
      組み合わせる操作。

主な利点:
- 機能的拡張性は4 Model中最高。

主なリスク:
- 最小権限原則・Human Gate保護能力・Projection衝突率・誤作動時
  被害範囲のいずれも4 Model中最低評価。
- 「candidate merge」（恒久禁止）との境界が4 Model中最も不明瞭。
- 4操作という前例が将来の段階的拡張を正当化しやすい最も強い前例。

未解決事項:
- reconstructとcandidate mergeの運用上の判定基準が未解決。
```

## 論点3: Projection Boundary

### Case A: Projection内部

```
概要: Reasoning NodeがPhase9 SemanticProjectionLayerの内部構成
      要素として位置づく。

主な利点:
- （既存資料に積極的な利点の記載は無し。）

主なリスク:
- Projectionとの重複が最大。Phase9-2確定済みメソッド署名を
  変更せず内部統合できるかが未解決の前提問題。
- Semantic Layer侵食リスク・制度崩壊時の被害半径ともに最大。
- 内部統合という前例が将来「他の層も内部統合する」という拡張
  要求を正当化しやすい。

未解決事項:
- 既存メソッド署名変更禁止の対象範囲にProjection層内部統合が
  含まれるかという解釈問題が未解決。
```

### Case B: Projection後段

```
概要: Reasoning NodeはProjection層が生成したProjectionResultを
      受け取る、Projection層の外側にあるNode（Observer/Advisorと
      同型配置）。

主な利点:
- 既存の後段Nodeパターン（Phase10-1/10-2）をそのまま適用できる。
- Human Gate保護能力: 高（既存パターンの適用が容易）。
- Projection層の出力を汚染しない構造的な防火壁が維持されやすい。

主なリスク:
- Advisorとの重複が最大（既存candidate群を受け取る点で同型配置）。
- Source分類拡張のたびに受け渡し方法の再確認が必要。

未解決事項:
- Reasoning固有のcandidate生成がPhase9-3A分類の外側で発生する
  点の整理が未解決。
```

### Case C: Projectionとは独立

```
概要: Reasoning Nodeは入力に対しProjection層を経由せず独自に
      意味的判断を行う、Projection層と並列の別経路。

主な利点:
- Projectionとの重複が最小。Phase9層への直接依存が無くなる。

主なリスク:
- 独自candidateを生成する場合、Phase9-3A Source分類の外側に
  第4のSourceとして並立するリスク。
- Phase9-3A原則を独立経路に同一文言で適用できるかが未解決。
- 独立経路自体がHuman Gateの裁定対象として増え、制度全体の
  監査範囲が拡大し続ける。

未解決事項:
- Phase7-B6既存裁定タイプとの接続方法が未確定。
- 独立経路で生成されるcandidateの構造がPhase9-3A生成物とどう
  整合するかが未確定。
```

---

# 第3部: 裁定記録欄

```
Human Gate Decision

論点1（Reasoning Definition）:
[未記入]

論点2（Candidate Authority）:
[未記入]

論点3（Projection Boundary）:
[未記入]
```

---

# 第4部: 裁定結果依存マップ

```
裁定後に解放される作業:

- 論点4（Collision Amplification）の再評価着手
    前提: 論点1・論点2の裁定完了
        （PHASE10_3_DECISION_READINESS_REPORT_v1.md判定:
        論点4=NEEDS ADDITIONAL ANALYSIS）

- 論点5（Advisor/Reasoning Separation）の再評価着手
    前提: 論点1・論点2の裁定完了
        （同上判定: 論点5=NEEDS ADDITIONAL ANALYSIS）

- Reasoning Node Contract（phase10_3_reasoning_node_contract_
  v1.md）作成可否判定
    前提: 論点1・論点2・論点3すべての裁定完了
        （未裁定の間は契約本体作成は禁止されたままである）
```

```
裁定後も論点1〜3の裁定とは独立に残る未決事項（参考）:

- Phase10-1/10-2のGit固定作業（候補A/B/C、
  PHASE10_FIXATION_PACKAGE_OPTIONS_v1.md）
- Phase9-3B（Intent Projection最小候補生成器の実装）の凍結状態
```

---

## 注記

本文書はPHASE10_3_HUMAN_GATE_DECISION_BRIEF_v1.mdの内容を裁定
セッション用に再整理したものであり、新たな評価軸の追加・採択・
推奨・契約作成・実装のいずれも行っていない。

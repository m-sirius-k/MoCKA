# Phase10-3 Reasoning Preparation Note v1

Status: PREPARATION NOTE ONLY（事前調査・論点可視化のみ。
契約作成禁止・コード変更禁止）
Date: 2026-06-23

```
本文書の目的:
    「Reasoning Nodeを設計する」ことではない。
    「Reasoning Nodeを設計するための論点を可視化する」ことである。
```

本文書はPhase10-3（Reasoning Node Contract）の契約を作成する
ものではない。`phase10_3_reasoning_node_contract_v1.md`は本作業
では作成しない。論点の列挙・整理のみを行い、いずれの論点も
本文書時点では採択・固定しない。次回裁定までこの状態を維持する。

```
本文書で行わないこと（確定）:
    phase10_3_reasoning_node_contract_v1.md 作成
    コード追加
    テスト追加
    Runtime変更
    Core変更
    Projection変更
    Phase9-3B開始
    Human Gate条件の設定
    いずれの論点（A〜D）の採択・固定
```

## A. Reasoning Definition候補

Reasoningとは何か、まだ定義しない。論点のみ列挙する。

```
論点A-1: Reasoningは「候補を生成する」行為そのものか、それとも
    「候補生成の前提となる意味的判断」を指すのか。
    （Phase10-0第1章Category 3は「候補間の関係について説明を
      生成するNode」と仮置きしているが、これは候補生成と
      候補間説明のどちらに重心があるか未確定。）

論点A-2: Reasoning Nodeは新規candidateを生成する権限を持つのか、
    それとも既存candidate（Phase9 Projection層が生成したもの）
    に対する解釈のみを担うのか。
    （前者ならPhase9 SemanticProjectionLayerの責務と重複する
      可能性があり、後者ならAdvisor Nodeとの差分が薄くなる
      可能性がある。）
```

```
Observerとの差分（論点）:
    Observer = 状態をそのまま記述する（解釈を加えない）。
    Reasoning = 状態間の関係を解釈する（仮）。
    この差分が「説明」という言葉の中でAdvisorの役割3
      （候補の説明）とどう区別されるかが未確定。

Advisorとの差分（論点）:
    Advisor = 既存candidate群に基づき助言・代替案を提示する
        （Phase10-2第1〜3章）。
    Reasoning = candidateそのものを生成・派生・拡張する（仮、
        Phase10-0第1章Category 3の「候補を生成する」記述に
        基づく仮説）。
    この差分が「Advisorの代替候補提示」（既存candidate群の
      再提示に限定、Phase10-2第2章）と「Reasoningの候補生成」
      （新規candidate生成）の境界線をどこに引くかが最大の論点。
```

## B. Candidate Authority候補

Reasoningが可能な行為候補を列挙する。まだ採択しない。

```
候補B-1: candidate生成
    既存のEventCandidate/NLCandidateと同じ型構造で、新たな
    候補インスタンスを生成する行為。

候補B-2: candidate派生
    既存candidateを起点に、関連する別のcandidateを導出する行為
    （例: あるclusterの候補から、関連clusterの候補を派生させる）。

候補B-3: candidate拡張
    既存candidateにメタデータ（why_generated相当の追加情報等）
    を付与する行為。candidateの同一性は変えない。

候補B-4: candidate再構成
    複数の既存candidateの情報を組み合わせて、新たな表現形式の
    candidateを構成する行為（mergeとは異なるか、同一視されるか
    が論点）。
```

これら4候補は相互に重なりうる（例: B-2とB-4の境界が不明瞭）。
本文書ではこの重なりを整理せず、列挙のみに留める。

## C. 禁止事項候補

候補列挙のみ。まだ固定しない。

```
候補C-1: candidate採択
    （Phase9-3A Ranking Policy・Phase10-0第4章で既に確定済みの
      禁止事項と同方向。Reasoning Nodeにも適用される可能性が
      高いが、本文書では「適用される」と確定しない。）

候補C-2: candidate削除
    （Phase9-2恒久禁止6項目・Phase10-1/10-2の既存禁止と同方向。）

候補C-3: collision解消
    （Phase7-B5・Phase10-0/10-1/10-2の既存禁止と同方向。
      ただしReasoning Nodeが「候補を生成する」権限を持つ場合、
      生成行為自体が新たなcollisionを生む可能性があり、
      「生成によるcollision増加」と「既存collisionの解消」の
      違いを論点として残す。）

候補C-4: Human Gate代行
    （Phase10-0第4章三分離・Phase10-1/10-2の既存禁止と同方向。）

候補C-5: Runtime実行
    （Phase10-0第4章・Phase10-1/10-2の既存禁止と同方向。）
```

候補C-1〜C-5はいずれもPhase10-1（Observer）・Phase10-2（Advisor）
で既に確定している禁止事項と方向性が一致する。ただしReasoning
Nodeが「候補生成」権限を持つ場合に特有の新規禁止事項（例:
生成candidate数の上限、生成の自動トリガー禁止等）が必要かどうか
は、本文書では論点として提起するのみで結論を出さない。

## D. Projection境界

Reasoningが「Projection前」「Projection後」のどちらを扱うべきか
調査する。結論は出さない。

```
論点D-1: Projection前（text -> Projection層への入力側）を扱う場合
    Reasoning Nodeが自然言語入力やintentの解釈を担い、Projection
    層（SemanticProjectionLayer）への入力を加工・補強する立場に
    なる可能性。この場合、Phase9-3A Source-A/B/C（Intent Path/
    Explanation Path/Hybrid Path）との役割重複が生じる懸念がある。

論点D-2: Projection後（ProjectionResult -> 候補群の解釈側）を扱う場合
    Reasoning NodeはAdvisor Nodeと同様、Projection層が既に生成した
    候補群を受け取って処理する立場になる。この場合、Phase10-2第5章
    「Advisor -> Reasoning の境界は候補生成に踏み込む境界」という
    記述と整合させる必要がある（Reasoningが後段にいながら新規
    candidateを生成する、という構図の整理が必要）。

論点D-3: 両方を扱う場合（Projection前後の双方向）
    Reasoning Nodeが入力側の解釈と出力側の候補生成の両方に関与する
    構図。Phase9-1の「2方向投影」（nl_to_event_candidates /
    event_to_nl_candidates）との関係をどう位置づけるかが未確定。
    Reasoning NodeがPhase9 Projection層そのものの一部なのか、
    Projection層の外側にあるNodeなのか、という根本的な分類問題が
    残る。
```

```
未解決のまま残す根本論点:
    Reasoning Nodeは「Phase10のNode体系」に属する存在なのか、
    それとも「Phase9 Projection層の拡張」に属する存在なのか。
    この帰属が確定しない限り、Projection前/後のどちらを扱うべきか
    も確定しない。
```

## 結論

本文書はA〜Dの論点を列挙したのみであり、いずれも採択・固定して
いない。`phase10_3_reasoning_node_contract_v1.md`の作成、コード・
テストの追加、Runtime/Core/Projectionの変更、Phase9-3Bの開始、
Human Gate条件の設定はいずれも行っていない。

```
次回裁定までの状態:
    Phase10-3 = 論点整理済み・契約固定は次回裁定待ち
```

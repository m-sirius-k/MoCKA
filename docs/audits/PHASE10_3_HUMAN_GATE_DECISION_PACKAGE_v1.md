# Phase10-3 Human Gate Decision Package v1

Status: DECISION PACKAGE ONLY（論点・選択肢・影響範囲の提示のみ。
推奨案禁止・採択禁止・契約作成禁止）
Date: 2026-06-23

本文書はPHASE10_3_REASONING_DEFINITION_OPTIONS_v1.md、
PHASE10_3_CANDIDATE_AUTHORITY_OPTIONS_v1.md、
PHASE10_3_PROJECTION_BOUNDARY_OPTIONS_v1.md、
PHASE10_3_COLLISION_AMPLIFICATION_AUDIT_v1.md、
PHASE10_3_ADVISOR_REASONING_SEPARATION_v1.mdを統合し、
Human Gateが裁定すべき論点一覧のみを提示する。推奨案・優劣判断・
採択は一切含まない。

## 論点1: Reasoning Definitionの確定

```
出典: PHASE10_3_REASONING_DEFINITION_OPTIONS_v1.md

選択肢:
    Option A: Reasoning = 候補生成主体
    Option B: Reasoning = 候補生成＋候補派生主体
    Option C: Reasoning = 意味的推論主体（候補生成は結果の一部）

影響範囲:
    - Advisor Nodeとの差分の大きさ（A/B=最大、C=最小）
    - Phase9 Projection層との近接度（A/B=高、C=低）
    - Human Gateへの提示物の形式（A/B=candidate単位、
      C=解釈・関係性中心、Phase7-B6既存裁定タイプとの接続方式に
      影響）
```

## 論点2: Candidate Authority範囲の確定

```
出典: PHASE10_3_CANDIDATE_AUTHORITY_OPTIONS_v1.md

選択肢:
    Model A: generateのみ
    Model B: generate + derive
    Model C: generate + derive + expand
    Model D: generate + derive + expand + reconstruct

影響範囲:
    - 制度整合性（A→Dの順でPhase9-2恒久禁止「candidate merge」
      との境界が不明瞭化、Dで最も低下）
    - collision影響（A→Dの順で新規矛盾を生む可能性が増加、
      Dで最も高い）
    - Projection影響（A/Bで高、Cで一旦低下、Dで再上昇という
      非単調傾向）
    - Human Gate影響（A→Dの順で裁定時の参照情報量・区別負荷が増加）
```

## 論点3: Projection層との帰属関係の確定

```
出典: PHASE10_3_PROJECTION_BOUNDARY_OPTIONS_v1.md

選択肢:
    Case A: Projection内部（SemanticProjectionLayerの一部）
    Case B: Projection後段（Advisor/Observerと同型の外部Node）
    Case C: Projectionとは独立（別経路）

影響範囲:
    - Phase9整合性（Case Aは既存メソッド署名変更禁止との抵触
      可能性、Case Bは既存パターンに最も整合、Case Cは新たな
      整合性設計が必要）
    - Candidate Source整合性（Phase9-3A Source-A/B/C分類との
      関係、Case Bは既存candidateを入力として扱う点でAdvisorと
      同型、Case Cは第4のSourceとして扱う必要が生じる可能性）
    - Ranking整合性（Case AはPhase9-3A Ranking Policy自体の
      改変リスクを伴う、Case B/Cは既存禁止事項の適用がしやすい）
    - Human Gate整合性（三分離原則自体はいずれのCaseでも維持
      されるが、Case AはPhase9-1絶対禁止の解釈問題、Case Cは
      Human Gateへの提示物形式の再設計を要する）
```

## 論点4: collision増幅に関する制度的空白の扱い

```
出典: PHASE10_3_COLLISION_AMPLIFICATION_AUDIT_v1.md

選択肢:
    （本論点は3案の並列提示ではなく、空白そのものへの対応方針が
    論点である。以下は対応の方向性の選択肢として整理する）
    方向1: 明示的に禁止を新設する
    方向2: 明示的に許可する（条件付き許可を含む可能性）
    方向3: 未規定のまま維持する（既存契約と同様、明文化しない）

影響範囲:
    - 既存4契約系列（Phase7-B5/Phase9層/Phase10-1/10-2）のうち
      「解消」のみが一貫して明記され、「生成」「維持」「増幅」は
      明記が無いか暗示的記述に留まるという既存パターンとの整合性
    - Reasoning Nodeがcandidate生成権限（論点2）を持つ場合、
      この空白が実際の運用上どう影響するかは論点2の決定と連動する
```

## 論点5: Advisor Nodeとの機能的差分の確定

```
出典: PHASE10_3_ADVISOR_REASONING_SEPARATION_v1.md

選択肢:
    （3案の並列提示ではなく、6操作それぞれについて
    Advisor/Reasoningの担当をどう切り分けるかが論点である）
    操作別の論点:
        候補生成: Advisor禁止・Reasoning未確定
                  （論点1のOption選択と連動）
        候補比較: Advisor許可・Reasoning未確定
                  （重複領域、機能の同一性or別概念化が論点）
        推薦:     Advisor許可（Recommendation確定済み）・
                  Reasoning未確定（出力形式の共有or独自定義が論点）
        説明:     Advisor許可・Reasoning未確定
                  （重複度最大、Option C採用時に特に顕著）
        派生:     Advisor禁止（解釈上）・Reasoning未確定
                  （論点1のOption B選択と連動）
        再構成:   Advisor禁止（candidate統合として明示禁止）・
                  Reasoning未確定（論点2のModel D選択、および
                  mergeとの同一視リスクと連動）

影響範囲:
    - 説明・候補比較の2操作はAdvisorとの機能重複度が最も高く、
      Reasoning Node設計時にAdvisor Node契約（Phase10-2）自体の
      再解釈・境界再定義が必要になる可能性がある
    - 候補生成・派生・再構成の3操作はAdvisorで明確に禁止されて
      いるため、Reasoningがこれらを担う場合は新規権限の追加と
      なり、論点1・論点2の決定に直接従属する
```

## 論点間の依存関係（事実整理）

```
論点1（Reasoning Definition）の選択は、論点2（Candidate
Authority）・論点3（Projection帰属）・論点5（Advisor境界）の
すべてに影響する上位論点である。

論点2（Candidate Authority）の選択は、論点4（collision増幅）の
実際の影響度に直接連動する。

論点3（Projection帰属）の選択は、論点2のModel選択時の
「Projection影響」評価の前提を変える。

論点5（Advisor境界）は論点1・論点2の決定後でなければ、
操作別の最終的な切り分けが確定しない。
```

## 結論

```
本文書は論点1〜5について、選択肢と影響範囲のみを提示した。
推奨案・優劣判断・採択のいずれも行っていない。

Phase10-3 Reasoning Node Contract（phase10_3_reasoning_node_
contract_v1.md）の作成は、論点1〜5についてのHuman Gateの
明示裁定を待つ。
```

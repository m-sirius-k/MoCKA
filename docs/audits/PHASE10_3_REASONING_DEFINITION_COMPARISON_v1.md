# Phase10-3 Reasoning Definition Comparison v1

Status: COMPARISON ONLY（比較のみ。結論禁止・採択禁止・契約作成禁止）
Date: 2026-06-24

本文書はPHASE10_3_REASONING_DEFINITION_OPTIONS_v1.mdで並列比較した
Option A/B/Cについて、定義/権限/入力/出力/禁止事項/制度上の危険性の
6項目のみで再整理し、それぞれのObserverとの違い・Advisorとの違い・
Human Gateとの違いを明示する。結論・採択は行わない。

## Option A: Reasoning = 候補生成主体

### 定義
ReasoningはEventCandidate/NLCandidateそのものを生成する行為主体である。

### 権限
```
候補生成(generate)のみ。

Observerとの違い: Observerは生成権限を一切持たない（Phase10-1第2章
    禁止: Candidate変更）。Option Aは候補生成という新規権限を
    Reasoningに与える点で質的に異なる。
Advisorとの違い: Advisor Nodeは代替候補提示を既存candidate群の
    再提示に限定し、新規生成は明示的に禁止（Phase10-2第4章）。
    Option Aはこの禁止操作をReasoningに許可する形になる。
Human Gateとの違い: 採択(adopt)・実行(execute)はHuman Gate/
    Orchestratorに専有されたまま（Phase10-0三分離）。Option Aは
    生成のみであり採択・実行には踏み込まない。
```

### 入力
既存文書に入力仕様の明記なし（未確定）。Phase9 SemanticProjectionLayer
と同様の入力（自然言語等）を前提とする可能性があるが、本文書では
確定情報として扱わない。

### 出力
EventCandidate/NLCandidate（候補そのもの）。

### 禁止事項
```
- 採択(adopt)・実行(execute)・collision解消は禁止
  （Phase10-0三分離より全Option共通）。
- Observer/Advisorに既に禁止されている操作（candidate削除・統合・
  ranking改変等）はOption Aでも禁止のまま（変更なし）。
```

### 制度上の危険性
```
- Projection層（Phase9 SemanticProjectionLayer）との機能重複が
  最大（PHASE10_3_REASONING_DEFINITION_OPTIONS_v1.md
  「Projectionとの境界: 最も近接」）。
- Advisorに禁止された操作をReasoningに許可することで、
  Advisor/Reasoningの機能境界が事実上消滅するリスク。
```

## Option B: Reasoning = 候補生成＋候補派生主体

### 定義
Reasoningは新規候補の生成に加え、既存candidateからの派生
（derive_candidate）も担う行為主体である。

### 権限
```
候補生成(generate) + 候補派生(derive)。

Observerとの違い: Option Aと同様、生成権限の有無が質的差
    （Observerは生成権限なし）。
Advisorとの違い: 最大かつOption Aより広い。Advisorの
    「代替候補提示」（既存candidate群の再提示）とReasoningの
    「候補派生」（既存candidateから新candidateを導出）が表面上
    類似するため、機能境界がOption Aより不明瞭。
Human Gateとの違い: 採択・実行はHuman Gate専有のまま変更なし。
    ただし派生元candidateの出自（why_generated等）が複数世代に
    渡って積み重なる場合、Human Gateが裁定時に参照する情報量が
    増える。
```

### 入力
既存candidate（派生の起点）＋（Option Aと同様に）未確定の新規入力。

### 出力
EventCandidate/NLCandidate（新規生成分＋既存candidateからの派生分）。

### 禁止事項
```
- Option Aの禁止事項を継承（採択・実行・collision解消禁止）。
- 派生(derive)が「candidate merge」（Phase9-2恒久禁止）に該当
  しないことの境界確認が必要（既存文書では未確定）。
```

### 制度上の危険性
```
- 候補生成＋候補派生の両方がcollisionを生む可能性を持つ
  （PHASE10_3_COLLISION_GOVERNANCE_STUDY_v1.md確認事項1）。
  Option Aより問題化範囲が広い（生成由来＋派生由来の両方）。
- Advisorとの機能境界整理がOption Aより複雑
  （PHASE10_3_REASONING_DEFINITION_OPTIONS_v1.md
  「Advisorとの差分: 最大かつOption Aより広い」）。
```

## Option C: Reasoning = 意味的推論主体（候補生成は結果の一部）

### 定義
Reasoningの本質は候補間・観測結果間の意味的関係を推論することであり、
候補生成はその推論プロセスの派生的な出力（結果の一部）に過ぎない。

### 権限
```
意味的関係の推論が主、候補生成は結果として付随。

Observerとの違い: 中程度。Observerの「状態説明」（Phase10-1第2章、
    解釈を加えない）に対し、Option Cは「意味的関係の解釈」を中心に
    置く点で差があるが、候補生成が主目的でないためOption A/Bより
    差は小さい。
Advisorとの違い: 最小。Advisor Nodeの役割2-4（候補の説明/代替案の
    提示/矛盾点の指摘）はいずれも「意味的関係の解釈」という点で
    Option Cの定義と重なりが大きい。
Human Gateとの違い: 採択・実行はHuman Gate専有のまま変更なし。
    ただし「意味的推論」という性質上、Human Gateへの提示物が
    「候補」ではなく「解釈・関係性の説明」になる場合があり、
    Phase7-B6裁定タイプ（accept/reject/defer/split）が候補単位の
    裁定を前提としている既存構造との接続が新たな論点になる。
```

### 入力
候補群および観測結果（既存candidate/既存説明等）。未確定要素を含む。

### 出力
意味的関係の解釈・説明。候補生成はこれに付随する場合がある。

### 禁止事項
```
- Option A/Bの禁止事項を継承（採択・実行・collision解消禁止）。
- 単一解への収束は禁止（Phase9-1継承）。
```

### 制度上の危険性
```
- Advisorとの機能重複が3 Option中最大
  （PHASE10_3_REASONING_DEFINITION_OPTIONS_v1.md
  「Advisorとの差分: 最小」）。Advisor/Reasoningの境界が最も
  不明瞭になるリスク。
- Human Gateへの提示物形式（解釈・関係性中心）が既存裁定タイプ
  （候補単位）と整合するかが未解決のまま残る。
```

## 比較表（事実整理のみ）

```
                  Option A         Option B            Option C
Observerとの違い   最大(生成権限)   最大(生成権限)       中(解釈の有無)
Advisorとの違い    最大(低重複)     最大(中重複)         最小(高重複)
Human Gateとの違い 中(候補単位裁定) 中(派生履歴増加)      中〜高
                                                          (提示形式が論点)
```

## 注記

本文書はOption A/B/Cを定義/権限/入力/出力/禁止事項/制度上の危険性の
6項目のみで再整理したものであり、結論・採択は行っていない。

# Phase10-1: Observer Node Contract v1

Status: DRAFT (Phase10-1。契約のみ。コード禁止・テスト禁止。
実装は本契約では行わない・要承認)
Date: 2026-06-23

本文書はPhase10-0（Cognitive Integration Concept Contract）の
Node Definition第1章Category 2「Observer Node」を制度化する。
Phase7（Semantic OS Core）、Phase8（HAB Runtime Integration
Layer）、Human Gate（Phase7-B6/B7）、Phase9-1〜9-3A（Projection
Layer全契約）、Phase10-0のいずれのクラス・メソッド署名・絶対
禁止・凍結状態も本文書では変更しない。

```
本文書で行わないこと（確定）:
    コード追加
    テスト追加
    Runtime変更（Phase8）
    Core変更（Phase7）
    Human Gate変更
    Projection Layer変更（Phase9全体）
    Phase9-3B（Intent Projection）の凍結解除・開始
```

## 0. 位置づけ

```
Phase10-0: Node体系全体の概念契約
              （Advisor Node / Observer Node / Reasoning Node）
Phase10-1: 上記のうち最も権限の弱いObserver Nodeの制度化（本文書）
```

Phase10-0で定義された3カテゴリのうち、Observer Nodeは「書き込み
権限を一切持たない読み取り専用Node」として最初に定義されている
（Phase10-0第1章Category 2）。本契約はこれをさらに具体化し、
Observer Nodeが将来実装される際の境界を固定する。Observer Node
を最初に制度化する理由は、Phase10-0第5章Future Roadmapが
「Phase10-1（Observer Nodeの最小実装検討）が最も安全な着手点」
と見込んだことに基づく。ただし本契約も契約のみであり、実装の
承認を含まない。

## 1. Observer Node Definition（確定）

```
Observer Node とは:
    Phase9 Projection層およびPhase8-4 Observation Surfaceの出力を
    読み取り、観測・集計・状態説明を行うだけのNode。
```

役割は以下の3点に限定する。

```
役割1: Projection結果の読取のみ
    ProjectionResult / EventCandidate / NLCandidate /
    ProjectionLogEntry（Phase9-1第5章）を読み取り専用で参照する。

役割2: Candidate観測のみ
    候補群（candidates: Sequence）をそのまま観測対象とする。
    候補の内容を加工・選別・並び替えしない。

役割3: 状態説明のみ
    観測した内容について「今どういう状態か」を説明する。
    「どうすべきか」「どれを採るべきか」という判断は含まない。
```

Observer Nodeは、Phase10-0第1章で定義したNodeの一般的性質
（読み取り専用参照、出力はHuman GateまたはAudit Logにのみ記録、
PHI-OS Core/Runtimeへの直接書き込み権限なし）をすべて継承する。

## 2. Observer Permissions（最重要・確定）

```
許可:
    読取（read）
    集計（aggregate）
    可視化（visualize）
    説明生成（describe）

禁止:
    採択（adopt）
    実行（execute）
    Candidate変更（modify candidate）
    Ranking変更（modify ranking / re-score / re-order）
    Collision解消（resolve collision）
```

許可される4操作の境界を明確化する。

```
読取: 既存データ構造（ProjectionResult等）をそのまま参照する。
集計: 件数・分布等の統計値を計算する（例: candidate数、
      namespace別件数）。元データは変更しない。
可視化: 集計結果・観測結果を人間が読める形に整形する。
      整形は表示のためのものであり、データの書き換えではない。
説明生成: 「なぜこの状態に見えるか」を記述する。これは
      Phase10-0第4章Reasoning Ownership Ruleの「Reasoning」には
      該当しない（Reasoning NodeはCandidate間の関係を説明する
      が、Observer Nodeは状態をそのまま記述するのみであり、
      候補間の意味的関係の解釈・統合は行わない）。
```

禁止される5操作はPhase9-3A（Ranking Policy）・Phase7-B5
（Collision Governance）・Phase10-0第4章（Reasoning Ownership
Rule）の既存禁止事項をObserver Nodeに対してそのまま適用した
ものであり、新規の禁止事項ではない。Observer Nodeがこれらを
代行・迂回することも禁止する。

## 3. Observer Data Access（確定）

```
読取可能（Phase8-4 Observation Surface 4 View Channel）:
    trace_view
    cluster_view
    collision_view
    ruling_view

書込権限:
    なし
```

4 View Channelは既存のPhase8-4契約
（`docs/contracts/phase8_4_observation_surface_v1.md`）で定義
された「統合・比較・差分表示は提供しない」「相互呼び出し無し」
という分離構造をそのまま維持する。Observer Nodeはこの4チャネル
を独立に読むのみであり、本契約によってチャネル間の統合・比較
機能を追加することはない。

```
Observer Nodeの書込権限が「なし」であることの意味:
    - 4 View Channelへの書き込みを行わない
    - Audit Logへの直接書き込みも行わない（観測結果の記録は
      Human Gateの既存記録経路、またはNode Governanceで別途
      定義される間接経路を経由する。本契約では経路自体を
      新設しない）
```

## 4. Observer Governance（確定）

```
ObserverはHuman Gateを代行しない。
ObserverはOrchestratorを代行しない。
ObserverはProjectionへ介入しない。
```

この3原則を以下のように具体化する。

```
Human Gate代行禁止:
    Observer Nodeの説明・観測結果がいかなる形であっても
    「採択された」「承認された」という効力を持つことはない。
    採択権は常にHuman Gate（Phase7-B6/B7）のみが持つ
    （Phase10-0第4章Reasoning Ownership Ruleの継承）。

Orchestrator代行禁止:
    Observer NodeはPhase8-3 Execution Orchestratorの処理順序
    （MeaningCycleExecutor -> OrderNormalizer -> CollisionGovernor）
    を呼び出さない、変更しない、迂回しない。

Projection介入禁止:
    Observer NodeはPhase9 SemanticProjectionLayerの内部メソッドへ
    候補生成・削除・並び替えの指示を送らない（Phase10-0第3章
    Projection Connection Ruleの継承）。
```

また、Node Governance全般規則（Phase10-0第2章）のうち、
Observer Nodeにも以下がそのまま適用される。

```
Node間の直接通信は禁止（規則2）:
    Observer Nodeが他のNode（Advisor Node/Reasoning Node）と
    直接通信する経路は本契約では定義しない。

Nodeはcollisionを解消しない（規則3）:
    Observer Nodeがcollision_viewを観測しても、衝突状態を
    解消・統合・優先順位確定してはならない。

Node追加・削除は人間ゲート承認必須（規則4）:
    Observer Node自体の実装着手・変更・廃止は人間ゲート承認を
    要する。
```

## 5. Future Integration（確定）

```
将来のGPT/Claude/Gemini接続時も、最初はObserver Nodeとして
接続することを推奨対象として記録する。
```

- 既存のAdvisor Adapter Governance（Phase5 Step4-A〜C, Step5,
  Step6）はGPTを「Model B (Advisor)」に固定し、提案のみ・実行
  不可と定義している。これはAdvisor Nodeの権限構造として
  Phase10-0でも継承されている。
- 本契約はその上で、外部AI（GPT/Claude/Gemini等）が実際に
  MoCKAへ接続される際の「最初の段階」として、Advisor Nodeより
  さらに権限の弱いObserver Nodeから始めることを推奨記録する。
  理由: Observer Nodeは書込権限を一切持たないため、接続初期の
  リスクが最小になる。
- これは設計判断の記録であり、接続実装の承認ではない。実際の
  外部AI接続（SDK導入・API Key設定等）はPhase5
  `advisor_adapter_runtime_v1.md`およびPHASE5_STEP3_SEALの
  禁止事項（GPT Adapter実装/MCP Adapter実装/外部接続等の禁止）
  に従い、依然未着手・凍結のままである。本契約はこの凍結状態を
  解除しない。

## 6. 変更ルール

この契約に変更を加える場合は「Phase変更レベル」として扱い、
ユーザーの明示的承認を要する。第2章（Observer Permissions）の
許可4操作・禁止5操作の境界は、他のいかなる変更からも独立して
維持される。

本契約はPhase9-3B（Intent Projection）の凍結状態に影響しない。
Phase9-3Bの着手条件（`docs/audits/phase9_artifacts_audit_v1.md`
第3章）は本契約と独立して維持される。

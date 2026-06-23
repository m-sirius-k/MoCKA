# Phase10-0: Cognitive Integration Concept Contract v1

Status: DRAFT (Phase10-0。契約のみ。コード禁止・テスト禁止。
実装はPhase10-1以降・要承認)
Date: 2026-06-23

本文書はPhase9（認知統合フェーズ第一層・Semantic Projection Layer）
の上に、Phase10（Cognitive Integration、認知統合フェーズ第二層）の
概念契約を固定する。Phase7（Semantic OS Core: A〜E）、Phase8（HAB
Runtime Integration Layer: Runtime Bridge/Execution Orchestrator/
Observation Surface）、Human Gate（Phase7-B6/B7: HumanGateRulingStore/
CollisionStateTracker等）、Phase9-1〜9-3A（Projection Contract/
Projection Skeleton/Projection Strategy Contract）のいずれのクラス・
メソッド署名・絶対禁止・凍結状態も本文書では変更しない。

```
本文書で行わないこと（確定）:
    コード追加
    テスト追加
    Runtime変更（Phase8）
    Core変更（Phase7）
    Human Gate変更
    Phase9-3B（Intent Projection）の凍結解除
```

## 0. 位置づけ

```
Phase7:  意味生成（Meaning Generation/Fixation/Audit/Execution/Human Gate接続）
Phase8:  実行基盤（HAB Runtime Integration Layer）
Phase9:  認知統合 第一層（Semantic Projection Layer、自然言語<->Event投影）
Phase10: 認知統合 第二層（Cognitive Integration、本契約はその入口）
```

Phase9は「投影」（自然言語とEventの間を複数候補のまま往復させる
こと）を定義した。Phase10はその投影結果を、複数の認知単位（Node）
が読み取り・参照し合う構造をどう成立させるかを定義する。Phase9が
「1つの問いに対する複数候補」を扱う層であったのに対し、Phase10は
「複数の認知単位が同じ複数候補をどう扱うか」を扱う層である。

## 1. Node Definition（確定）

```
Node とは:
    Projection結果（EventCandidate/NLCandidate/ProjectionResult）を
    読み取り、何らかの観測・提案・記録を行う認知単位の総称。
```

Nodeは以下の性質を満たすものとして定義する。

```
Nodeである条件（すべて満たす）:
    - Projection層（Phase9）の出力を読み取り専用で参照できる
    - 自身の出力（提案・観測結果）をHuman Gateまたは
      Audit Log（append-only）にのみ記録できる
    - PHI-OS Core（Phase7）・Runtime（Phase8）への直接書き込み
      権限を持たない

Nodeでない例:
    - Phase8 Execution Orchestrator（実行経路、本契約のNodeには
      含まれない。既存のOrchestratorは変更しない）
    - Human Gate自体（裁定権を持つ既存制度、Nodeとして再定義しない）
    - PHI-OS Core / Event Gate（事実の書き込み経路、Nodeではない）
```

Node種別は本契約時点で以下の3カテゴリに分類する（実装は行わない、
分類のみ）。

```
Category 1: Advisor Node
    既存のAdvisor Adapter（Phase5 Step4-A〜C, Step5, Step6）が
    確立した「提案のみ・実行不可」の権限構造をそのまま継承する
    Nodeの一種。GPT等の外部Advisorはここに属する。

Category 2: Observer Node
    Phase8-4 Observation Surfaceの4 View Channel
    （trace_view/cluster_view/collision_view/ruling_view）を
    読み取るのみのNode。書き込み権限を持たない。

Category 3: Reasoning Node（本契約で新規定義）
    Projection結果を複数参照し、候補間の関係について「説明」
    （説明であって裁定ではない）を生成するNode。第4章
    Reasoning Ownership Ruleで権限境界を定義する。
```

## 2. Node Governance（確定）

Nodeの権限構造はPhase5 Step4-A（Adapter Governance v1）の権限
マトリクスをそのまま継承し、Phase10固有の制約を追加する。

```
Authority Owner: User（変更なし）
Execution Authority: MoCKA（変更なし）
Node Execution/Memory/Replay/Snapshot Rights:
    Nodeには付与しない（Phase5 Step4-Aの原則を継承）
Audit: Mandatory（変更なし）
```

Phase10固有のNode統治規則:

```
規則1: Node登録は提案のみ
    新規Nodeを追加する場合、本契約またはその後継契約に種別・
    権限範囲・参照可能なProjection出力を明記すること。
    登録時点で自動的に実行権・書き込み権を得ることはない。

規則2: Node間の直接通信は禁止
    Node同士が互いの出力を直接読み書きする経路は本契約では
    定義しない。Node間の情報共有は、必ずProjection層の
    ProjectionLogEntry（Phase9-1第5章）またはAudit Log
    （append-only）を経由する。

規則3: Nodeはcollisionを解消しない
    Phase7-B5「衝突は解消しない」原則をNode Governanceにも
    継承する。Reasoning Nodeが複数候補間の関係を説明する際も、
    候補を1つに絞り込む、または優先順位を確定させることは
    禁止する。

規則4: Nodeの追加・削除は人間ゲート承認必須
    Node種別・権限範囲の追加・変更・削除は、Phase5 Step4-C
    Adapter Registry運用規則（authority_levelはStep4-Aの権限
    構造を上書き不可等）に準じ、Human Gate承認を必須とする。
```

## 3. Projection Connection Rule（確定）

NodeはPhase9 Semantic Projection Layerと以下の規則でのみ接続する。

```
許可される接続:
    Node -> ProjectionResult（読み取り専用）
    Node -> EventCandidate / NLCandidate の個別フィールド参照
        （cluster_id/canonical_trace_id/why_generated等、
          Phase9-3A第5章Explainabilityで定義された情報を含む）
    Node -> ProjectionLogEntry（読み取り専用、append-only前提）

禁止される接続:
    Node -> SemanticProjectionLayerの内部メソッド呼び出しを経由した
        候補生成への介入（候補追加・削除・並び替えの指示）
    Node -> ProjectionResultの書き換え
    Node -> Phase9-3Aで禁止されたRanking Policy違反操作
        （top-1選択・winner選択・自動採択）の代行・迂回
```

Node自身が新たな候補を生成したい場合、それはPhase9の
SemanticProjectionLayerの責務に属する操作であり、Phase10の
Nodeが独自に「候補生成相当の処理」を行うことは禁止する。Node
の役割はあくまでProjection結果を読み、観測・説明・提案を加える
ことに限定される。

## 4. Reasoning Ownership Rule（最重要・確定）

```
Reasoningの所有権は明確に分離する。
```

```
誰が「推論（reasoning）」を行えるか:
    Reasoning Node（Category 3）:
        Projection結果に基づく「説明」を生成できる。
        ただし、説明は常に複数候補を前提とした記述であり、
        単一の結論として提示してはならない。

    Advisor Node（Category 1）:
        既存のAdvisor Role Contract（Phase5
        advisor_adapter_contract_v1.md）をそのまま継承。
        提案のみ可能、実行不可、状態変更不可、
        Authority取得不可。

誰が「採択（adoption）」を行えるか:
    Human Gateのみ。
    いかなるNodeも採択権・裁定権を持たない。
    これはPhase9-3A第4章Ranking Policy
    （「採択するのはProjection層ではない」）の直接継承であり、
    Phase10においても変更しない絶対原則とする。

誰が「実行（execution）」を行えるか:
    既存のExecution Orchestrator（Phase8-3）のみ。
    Nodeは実行権を一切持たない。Reasoning Nodeがいかなる
    説明・提案を生成しても、それが直接Runtimeを起動する経路は
    本契約では一切定義しない。
```

この三分離（Reasoning/Adoption/Execution）が、Phase10において
最も重要な制度的境界である。Reasoning Nodeが将来高度化しても、
Adoption（採択）とExecution（実行）の権限がNode側に流れ込む
ことを本契約は恒久的に禁止する。

## 5. Future Roadmap（確定・概念のみ）

本契約は概念定義のみであり、以下は実装順序の見込みを示す
ロードマップであって、着手の承認ではない。各段階の着手には
個別にHuman Gateの明示的な「開始する」裁定を要する
（Phase9-3Bと同じ運用パターン）。

```
Phase10-0（本文書）: Cognitive Integration Concept Contract。
    Node Definition/Node Governance/Projection Connection Rule/
    Reasoning Ownership Ruleの確定。コードゼロ。

Phase10-1（未着手・要承認）: Observer Nodeの最小実装検討。
    Phase8-4 Observation Surfaceの既存4 View Channelを読むだけの
    最小Node。新規の権限を要求しないため、最も安全な着手点になる
    見込み。

Phase10-2（未着手・要承認）: Reasoning Nodeの契約詳細化。
    「説明の生成」と「採択」の境界をコード設計レベルでどう強制するか
    （型レベルでの分離等、Phase9-2の手法の継承を検討）。

Phase10-3（未着手・要承認）: Advisor Node統合検討。
    既存Advisor Adapter Runtime（Phase5 Step6）との接続方式検討。
    Phase5で凍結されているGPT/MCP Adapter実装の解除を意味しない
    （PHASE5_STEP3_SEALの禁止事項6項目は本契約でも継続する）。

Phase10-4（未着手・要承認）: Node間情報共有の監査設計。
    規則2（Node間直接通信禁止）の下で、ProjectionLogEntry/Audit Log
    を経由した間接共有がDrift Monitor（Phase7-C）の監視対象に
    どう統合されるかの検討。
```

## 6. 変更ルール

この契約に変更を加える場合は「Phase変更レベル」として扱い、
ユーザーの明示的承認を要する。第4章（Reasoning Ownership Rule）の
三分離原則（Reasoning/Adoption/Execution）は他のいかなる変更からも
独立して維持される。

本契約はPhase9-3B（Intent Projection）の凍結状態に影響しない。
Phase9-3Bの着手条件（`docs/audits/phase9_artifacts_audit_v1.md`
第3章）は本契約と独立して維持される。

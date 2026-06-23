# Phase9成果物監査・整理 v1

Status: AUDIT ONLY（監査・整理のみ。コード追加禁止・テスト追加禁止）
Date: 2026-06-23

本文書はPhase9-3B（Intent Projection最小候補生成器）が凍結状態に
あることを前提に、Phase9-1/9-2/9-3Aの成果物を一覧化し、依存関係を
整理し、Phase9-3B着手条件を明文化するものである。本文書自体は
監査・整理作業の記録であり、以下への変更は一切含まない。

```
禁止（本文書で変更しないもの）:
    Phase7 Core
    Phase8 Runtime
    Human Gate
    Projection Strategy Contract v1（phase9_3a_projection_strategy_contract_v1.md）
    コード（追加禁止）
    テスト（追加禁止）
```

## 1. Phase9関連成果物一覧

### Phase9-1: Semantic Projection Layer Contract v1

```
種別: 契約文書（コードゼロ）
ファイル: docs/contracts/phase9_1_semantic_projection_v1.md
内容:
    - 投影の2方向確定（nl_to_event_candidates / event_to_nl_candidates）
    - 核心原則: 単一解を作らず複数候補を保持したまま流す
    - データソース: RealClusterReader.find_clusters_by_intent()（読取専用）
                    ExplanationResult（読取専用）
    - 絶対禁止: PHI-OS Core変更/Runtime変更/Human Gate変更/
                単一候補への収束/ログ上書き削除/既存再計算
記録: E20260623_446301261ac77（CHANGE_START）
      -> E20260623_503559103fc13（CHANGE_DONE）
```

### Phase9-2: SemanticProjectionLayer最小スケルトン

```
種別: 実装（構造体+空メソッドのみ）
ファイル:
    semantic/query_engine/projection_candidate.py
        （EventCandidate / NLCandidate）
    semantic/query_engine/projection_result.py
        （ProjectionResult、candidatesは常にSequence、
          単一値フィールド無し）
    semantic/query_engine/semantic_projection_layer.py
        （SemanticProjectionLayer、2メソッドともNotImplementedError）
    semantic/query_engine/tests/test_smoke_projection.py
        （5テスト、全PASS）
内容:
    - 型レベルでの単一解収束の不可能化（ProjectionResultに
      best_candidate等のフィールドが存在しない）
    - 恒久禁止6項目をコード冒頭に明記:
      自動採択/confidence最大選択/候補削除/candidate merge/
      Human Gate代行/Runtime直接起動
    - 候補生成アルゴリズム自体は意図的に未実装（Phase9-3へ分離）
記録: E20260623_5949237537827（CHANGE_START）
      -> E20260623_6804783367126（CHANGE_DONE）
監査結果: 「完了」判定（くろこ監査、E20260623記録）。
          単一解の構造的不可能化とNotImplementedError固定が
          MoCKAの思想と整合と評価。
```

### Phase9-3A: Projection Strategy Contract v1

```
種別: 契約文書（コードゼロ）
ファイル: docs/contracts/phase9_3a_projection_strategy_contract_v1.md
内容:
    - Purpose: Projectionは裁定器ではない
    - Candidate Generation Sources:
          Source-A: Intent Path（find_clusters_by_intent()）
          Source-B: Explanation Path（ExplanationResult）
          Source-C: Hybrid Path（Intent+Explanation+Namespace）
      進行順序 A -> B -> Hybrid 固定
    - Collision Policy: 候補間競合は解消しない
    - Ranking Policy:
          許可: score/confidence/source_count付与
          禁止: top-1選択/winner選択/自動採択
    - Explainability: why_generated（生成理由、推奨）
記録: E20260623_857921288f1fe（CHANGE_START）
      -> E20260623_917514110c90b（CHANGE_DONE）
Human Gate裁定: E20260623_089692329089c
    「Phase9-3A承認。Phase9-3B着手準備完了。
      実装開始はHuman Gate指示待ち」
```

## 2. 依存関係図

```
                    Phase7-A4-Intent
                  RealClusterReader
                  .find_clusters_by_intent()
                  （実データ接続済み・読取専用）
                            |
                            | 読取専用参照
                            v
Phase9-1 ----------> Phase9-2 ----------> Phase9-3A
(契約:               (構造:               (契約:
 投影方向確定)         型レベルで           候補生成境界確定)
                       単一解不可能化)            |
   |                      |                       |
   | 読取専用参照          | 型定義は               | 着手条件として
   v                      | 変更禁止               | 補強
Phase7-A3                 v                       v
ExplanationResult    SemanticProjectionLayer  Phase9-3B
（読取専用）           （2メソッド共に           （Intent Projection
                       NotImplementedError      最小候補生成器）
                       のまま凍結）              【凍結・未着手】
                                                  Human Gate「開始」
                                                  裁定待ち
```

```
横方向の不可侵関係（Phase9から見て変更禁止の既存層）:

    Phase7 Core（Semantic OS Core: A〜E）  -- 変更禁止 --> Phase9全体
    Phase8 Runtime（Runtime Bridge/        -- 変更禁止 --> Phase9全体
        Execution Orchestrator/
        Observation Surface）
    Human Gate（HumanGateRulingStore/      -- 変更禁止 --> Phase9全体
        CollisionStateTracker等）
```

Phase9-1が確定した「2方向・複数候補保持」の上に、Phase9-2が型
レベルで単一解収束を不可能化し、Phase9-3Aがその型の上で初めて
「候補をどう生成してよいか」の境界（Source A/B/C、Collision
Policy、Ranking Policy）を固定した。Phase9-3Bはこの3層全ての
制約を継承した状態でのみ着手可能であり、現時点ではいずれの層
にもコードの追加・変更は発生していない。

## 3. Phase9-3B着手条件（明文化・確定）

Phase9-3B（Intent Projection最小候補生成器）の着手には、以下の
条件をすべて満たすことを要する。1つでも欠落している場合は着手
不可とする。

```
条件1: Human Gate開始裁定が存在すること
    -> 「Phase9-3Bを開始する」という明示的な裁定がHuman Gateから
       出され、mocka_write_eventで記録されていること。
       本文書時点ではこの裁定は存在しない（E20260623_089692329089c
       は「着手準備完了」止まりであり「開始」裁定ではない）。

条件2: Intent Path以外へ拡張しないこと
    -> Phase9-3BはSource-A（Intent Path）のみを対象とする。
       Source-B（Explanation Path）・Source-C（Hybrid Path）への
       拡張はPhase9-3C/9-3Dとして別途着手条件を満たすまで行わない。

条件3: top-1選択を実装しないこと
    -> find_clusters_by_intent()の戻り値から最も確からしい1件を
       選んで返す処理（ソート後の先頭採用、confidence最大値の
       単独採用等を含む）を実装しない。戻り値は常に候補列
       （Sequence）として保持する。

条件4: candidate削除を実装しないこと
    -> 生成された候補を後段で取り除く処理（閾値未満の除外、
       重複除去による削減等を含む）を実装しない。

条件5: Runtime実行権を持たせないこと
    -> SemanticProjectionLayerおよびその候補生成メソッドが
       Phase8 Runtime（Execution Orchestrator等）を直接呼び出す
       経路を持たない。投影結果はあくまで候補の提示であり、
       実行・状態変更を一切引き起こさない。
```

## 4. 結論

Phase9-1/9-2/9-3Aの成果物・依存関係・Phase9-3B着手条件を本文書
として整理した。これは監査・整理作業であり、Phase7 Core・Phase8
Runtime・Human Gate・Projection Strategy Contract v1・コード・
テストのいずれにも変更を加えていない。

```
Phase9-3B（Intent Projection最小候補生成器）は、
Human Gateによる「開始する」の明示裁定が出るまで凍結状態とする。
```

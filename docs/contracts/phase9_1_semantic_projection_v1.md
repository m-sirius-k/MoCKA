# Phase9-1: Semantic Projection Layer Contract v1

Status: DRAFT (Phase9-1。契約先行。コードゼロ。実装はユーザー承認後)
Date: 2026-06-23

本文書はPhase9（認知統合フェーズ）の最初の層、Semantic Projection
Layerの契約を固定する。Phase7（A〜E、意味生成・固定・監査・実行・
人間接続）およびPhase8（HAB Runtime Integration Layer: Runtime
Bridge/Execution Orchestrator/Observation Surface）のいずれの
クラス・メソッド署名・絶対禁止も変更しない。

## 0. 位置づけ

```
Phase7: 意味生成
Phase8: 実行基盤
Phase9: 認知統合（本契約はその第一層）
```

Phase9-1が成立すれば、MoCKAは初めて「AIが利用する意味OS」になる。
本契約はその入口——自然言語とEventの間の双方向投影——を定義する。

## 1. 投影の方向（2方向・確定）

```
方向1: nl_to_event_candidates(text) -> Sequence[EventCandidate]
        自然言語 -> Event候補群

方向2: event_to_nl_candidates(identifier) -> Sequence[NLCandidate]
        Event -> 自然言語説明候補群
```

両方向とも**単一の戻り値ではなく候補の列（Sequence）を返す**。

## 2. 核心原則（最重要・確定）

```
単一解を作らず、複数候補を保持したまま流す
```

- 投影層は「最も確からしい1つ」を選んで返すことを禁止する。
  ランキング情報（類似度スコア等）を候補に付与すること自体は許容
  するが、それに基づいて1件に絞り込む（top-1を返す）ことは禁止する。
- これはPhase7-B5（Collision Governance）が確立した「衝突は解消しない」
  原則の投影層への継承である。自然言語とEventの対応関係の曖昧さは
  「エラー」ではなく「収束させてはいけない多重性」として扱う。

## 3. データソース（既存読み取り専用機能の参照・確定）

```
EventCandidate生成の基盤:
    semantic/query_engine/data_binding.py の
    RealClusterReader.find_clusters_by_intent()（Phase7-A4-Intent）
    を読み取り専用で呼び出す。既存メソッドの署名・実装は変更しない。

NLCandidate生成の基盤:
    semantic/query_engine/explanation_builder.py の
    ExplanationResult（Phase7-A3）の既存フィールド
    （why_this_meaning/final_judgement等）を読み取り専用で参照する。
```

本契約はこれら既存コンポーネントを**呼び出すだけ**であり、内部実装・
embedding生成方式・閾値（INTENT_MATCH_THRESHOLD等）には一切手を
入れない。

## 4. 絶対禁止 / 許可（確定）

禁止:
- PHI-OS Core（イベント原本）への書き込み・変更
- Runtime（Phase8: Runtime Bridge/Execution Orchestrator/Observation
  Surface）のクラス・メソッド署名・絶対禁止の変更
- Human Gate（Phase7-B6/B7: HumanGateRulingStore/CollisionStateTracker等）
  のクラス・メソッド署名・絶対禁止の変更
- 投影結果を単一候補に収束させること（トップ1選択・自動採用）
- 投影ログの上書き・削除（append-onlyのみ）
- 既存embedding・既存cluster・既存decision_traceの再計算

許可:
- 既存読み取り専用コンポーネント（RealClusterReader等）の呼び出し
- 複数候補をそのまま列として保持・返却すること
- 投影ログの新規追加（append-only）

## 5. 出力構造

```
EventCandidate = {
    cluster_id: str,
    canonical_trace_id: str | None,   # 既存ClusterReaderの戻り値をそのまま
    rationale: str | None,             # 任意。判断ではなく参考情報。
}

NLCandidate = {
    identifier: str,
    text: str,                          # ExplanationResultの既存フィールドをそのまま
    source_field: str,                  # "why_this_meaning" | "final_judgement"
}

ProjectionLogEntry = {
    direction: "nl_to_event" | "event_to_nl",
    query: str,
    candidates: Sequence[EventCandidate] | Sequence[NLCandidate],
    recorded_at: str | None,            # 呼び出し側提供値。システム生成しない。
}
```

## 6. 段階フロー

1. **Phase9-1（本文書）**: 契約設計のみ。コードゼロ。
2. Phase9-2（未着手・要承認）: `SemanticProjectionLayer`の最小スケルトン
   実装（既存コンポーネントの呼び出しのみ、Fake/実データでの動作確認）。
3. Phase9-3（未着手）: 投影ログのHuman Gateへの接続検討
   （投影結果の多重性自体をHuman Gateの観測対象にできるか、要設計）。

## 7. 変更ルール

この契約に変更を加える場合は「Phase変更レベル」として扱い、ユーザーの
明示的承認を要する。第2章の核心原則（複数候補保持）は他のいかなる
変更からも独立して維持される。

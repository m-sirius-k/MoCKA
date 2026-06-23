# Meaning Query Engine Contract v1 (Phase7-A-1)

Status: DRAFT (Phase7-A-1。コード実装はゼロ。Phase7-A-2着手前にユーザー承認を要する)
Date: 2026-06-23

本文書はPhase7（Semantic Operating Layer）のうちPhase7-Aで導入する
Meaning Query Engineの外部契約を固定する。Time OS Contract v1（FROZEN、
phi_os/api/time_api.py）は本契約の対象外であり、一切変更しない。

## 0. 位置づけ

```
PHI-OS (immutable event core)
    -> Adapter Layer (Phase6)
    -> Canonical Meaning Layer (Phase5: cluster / dictionary)
    -> Semantic Operating Layer (Phase7)
         -> Meaning Query Engine (Phase7-A) <- 本文書
```

Phase7-Aの本質は「意味を作る」ではなく「意味を引く」。
新規のクラスタ生成・embedding生成・意味推論は一切行わない。

## 1. モジュール配置（確定）

```
phi_os/
    api/
        time_api.py        <- 不変。Phase7は触れない。

MoCKA/
    semantic/
        query_engine/
            contracts/                  (本ディレクトリに将来スキーマ追記)
            meaning_query_engine.py     (Phase7-A-2で新設)
            intent_search.py            (Phase7-A-2で新設)
            explanation_builder.py      (Phase7-A-3で新設)
```

既存の `MoCKA/semantic/`（intent_classifier.py / semantic_registry.py 等、
チャット意図分類用）および `phi_os/semantic/query_resolver.py`
（Time Query向け固定キーワード変換、Phase5 Step3）とは責務が異なる別系統
として扱う。既存ファイルへの変更・再利用の強制は行わない。

## 2. 責務分離

| レイヤ | 責務 |
|---|---|
| PHI-OS | 現実イベント（不変・append only） |
| time_api | 時間情報のみ（state/events/replay/audit） |
| Meaning Query Engine | 意味検索・解釈（読み取りのみ） |

## 3. 提供機能（3機能統合体）

### 3.1 canonical_trace_id search（anchor — 座標決定）
- 入力: `canonical_trace_id`
- 出力: 対応するクラスタ・decision_traceへの参照（index lookupのみ）
- 新規index構築は許可されるが、既存clusterの再計算は禁止。
- **依存方向（確定）**: canonical_searchは他の機能に依存しない単独の座標決定。
  intent_search・explanation generationの起点（anchor）として扱う。

### 3.2 intent search（意味場 — canonical anchorへの依存）
- 入力: 自然文 または intentキー
- 出力: 既存cluster/embeddingへの参照一覧
- 既存embeddingの再生成は禁止。既存ベクトル・既存cluster mappingの参照のみ。
- **依存方向（確定）**: intent_searchはcanonical_searchが返すanchor（固定点）を
  基準に、その周囲の意味場（latent含む複数構造）を展開する。並列実行ではなく
  「canonical anchor確定 → intent展開」の順序を前提とする。canonical anchorが
  無い状態でのintent単独展開は許可するが、その場合は結果に
  `anchor: null` を明示し、anchor確定済みの結果と区別する。

### 3.3 explanation generation（"なぜこのクラスタか"、主軸=canonical）
- 入力: cluster_id（canonical_trace_idから解決されたものを主軸とする）
- 出力: decision_trace由来の説明（reasoning summary）
- decision_traceの再実行・改変は禁止（読み取りのみ）。Phase7-Bの
  Decision Replay Systemと機能境界を分離し、本契約では説明文生成のみを扱う。
- **入力主軸（確定）**: explanation builderはcanonical_trace_id由来のcluster_idを
  主軸入力とする。intent_search結果から得られた複数clusterを説明したい場合は、
  各clusterのcanonical_trace_idを個別に解決してから本機能を呼び出す
  （intent結果を直接の主軸入力としては受け付けない）。

## 4. 絶対禁止 / 許可

禁止:
- PHI-OSへの書き込み
- cluster再計算
- embedding再生成
- 6h diameter制約の変更
- 6,563クラスタ（ベースライン）の変更

許可:
- 読み取りのみ
- 既存cluster参照
- 既存decision_trace参照

## 5. 段階実装フロー（確定・固定）

1. **Phase7-A-1（本文書）**: contracts設計のみ。コードゼロ。
2. **Phase7-A-2**: 最小実装（read-only query engine）。
   `meaning_query_engine.py` / `intent_search.py` を新設し、
   3.1/3.2のみ実装。explanation generationは含めない。
3. **Phase7-A-3**: explanation layer追加（`explanation_builder.py`）。

各段階の開始前にCHANGE_START、完了後にCHANGE_DONEをmocka_write_eventで
記録すること。Phase7-A-2着手はユーザーの明示的承認を要する。

## 6. 変更ルール

この契約に変更を加える場合は「Phase変更レベル」として扱い、ユーザーの
明示的承認を要する。Time OS Contract v1（FROZEN）との関係は「並立・
非干渉」であり、本契約がTime OS Contractを上書き・拡張することはない。

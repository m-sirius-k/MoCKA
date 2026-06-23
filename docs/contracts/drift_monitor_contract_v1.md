# Drift Monitor Contract v1 (Phase7-C-1)

Status: DRAFT (Phase7-C-1。コードゼロ。最小スケルトンはユーザー承認後)
Date: 2026-06-23

本文書はPhase7-C（Drift Monitor）の外部契約を固定する。Time OS Contract
v1（FROZEN）、Meaning Query Engine Contract v1、Explanation Builder
Contract v1、Decision Replay System Contract v1はいずれも本文書に
よって変更されない。

## 0. 位置づけ（意味OSの自己免疫層）

Phase7-A（意味生成）とPhase7-B（意味固定）が揃った時点で必要になるのは、
その意味が壊れていないことを保証する層である。

```
PHI-OS（封印） -> Adapter（既存） -> Semantic（Phase7-A/B） -> Drift（本契約）
```

Drift Monitorは新しい意味を作らない。既存の意味生成・固定結果を
読み取り、一貫性の逸脱を検知するだけの監査層である。

## 1. 重要な用語整理（混同防止・必読）

既存`relay/replay_audit.py`（Phase4.5、ReplayEngine v1/v2比較による
`REPLAY_DRIFT`検知）は、RelayKernelの**状態レベル**のdrift
（v1とv2の再構築結果が一致するか）を扱う。本契約のDrift Monitorは
**意味レベル**のdrift（canonical/intent/explanation/replayの意味的
整合性が時間とともに崩れていないか）を扱う。両者は対象が異なる
別概念であり、統合しない（decision_replay_system_contract_v1.md
1章の整理パターンを継承）。

| | 既存replay_audit（Relay層） | Drift Monitor（Phase7-C） |
|---|---|---|
| 対象 | ReplayEngine v1/v2の再構築結果 | canonical/intent/explanation/replayの意味的整合性 |
| 検知単位 | state_hash不一致 | consistency_vectorの逸脱 |
| 依存層 | RelayKernel | Meaning Query Engine(7-A) + Decision Replay System(7-B) |
| 契約 | Time OS Contract v1（間接） | 本文書 |

## 2. drift_definition（何を"ズレ"とするか）

意味レベルのdriftを以下の3種に分類する。

1. **Canonical Drift**: 同一`canonical_trace_id`が異なる
   `cluster_id`に解決される（time-stable anchorの前提が崩れる）。
2. **Explanation Drift**: 同一canonicalに対する複数スナップショット
   間で`final_judgement`の趣旨が変化する（`compare_snapshots`の
   `changed_fields`に`final_judgement`または`why_this_meaning`が
   含まれる状態が一定回数以上連続する）。
3. **Intent Drift**: 同一intent入力に対する`activated_structures`が
   時間とともに変化する（canonicalは同一だがintent側の一致点が変動する）。

baseline（6,563クラスタ固定）自体の変更はdrift検知の対象外
（baseline変更は別途「Phase変更レベル」の人間承認事項であり、
Drift Monitorが検知すべきは「baselineを変えずに意味が動いた」ケース）。

## 3. consistency_vector（4軸）

各観測時点で以下4軸のスナップショットを束ねたベクトルを構成する。

```
consistency_vector = {
    canonical: CanonicalSearchResult,      # Phase7-A
    intent:    IntentSearchResult | None,  # Phase7-A
    explanation: ExplanationResult,        # Phase7-A/B
    replay:    ReplayedTrace | None,       # Phase7-B
}
```

- 4軸はいずれも既存の読み取り専用結果オブジェクトをそのまま束ねる
  だけであり、Drift Monitor自身が新しい計算（cluster再計算・
  embedding再生成）を行うことはない。
- `consistency_vector`同士の比較（時系列での前回観測との差分）が
  drift検知の唯一の入力である。

## 4. anomaly scoring（意味レベルの逸脱検知）

- スコアは「ズレの種類（drift_definition 1〜3）×検知回数」の
  単純カウントベースから始める（Phase7-C-1では数式・閾値は未確定、
  Phase7-C-2実装時にdocs/contracts/配下へ別途固定する）。
- スコアリング自体はdriftの記録・分類のみを行い、自動修復・
  自動ロールバック・cluster再計算トリガーは一切行わない
  （Relay層のreplay_audit.pyが採用した「記録のみ・自動修復なし」
  の原則をDrift Monitorにも継承する）。
- 異常検知後のアクションは常にHuman Gate（人間承認）に委ねる。

## 5. 絶対禁止 / 許可

禁止:
- PHI-OSへの書き込み
- cluster再計算・embedding再生成
- decision_traceの改変
- 既存スナップショット（Phase7-B）の上書き・削除
- 自動修復・自動ロールバック・自動cluster再計算
- 既存Relay層（replay_audit.py等）への変更・統合

許可:
- Phase7-A/Bの既存結果オブジェクトの読み取りのみ
- consistency_vectorの構成・時系列比較
- drift記録の新規追加（append-only、Phase7-Bのスナップショット
  store設計を継承）

## 6. 段階実装フロー

1. **Phase7-C-1（本文書）**: 契約設計のみ。コードゼロ。
2. Phase7-C-2（未着手・要承認）: consistency_vectorの構成 +
   drift記録のみの最小スケルトン（`semantic/query_engine/drift_monitor.py`
   想定）。スコアリング数式・閾値はこの段階で別途固定する。
3. Phase7-C-3（未着手）: anomaly scoringの閾値運用 + Human Gate
   への通知経路設計。

## 7. 変更ルール

この契約に変更を加える場合は「Phase変更レベル」として扱い、ユーザーの
明示的承認を要する。

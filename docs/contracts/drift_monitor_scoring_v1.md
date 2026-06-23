# Drift Monitor Scoring Contract v1 (Phase7-C-2)

Status: DRAFT (Phase7-C-2。最小スケルトン実装を伴う。実データ接続なし)
Date: 2026-06-23

本文書は[drift_monitor_contract_v1.md](drift_monitor_contract_v1.md)4章で
予約されていた「数式・閾値」を確定する。drift_monitor_contract_v1.mdの
drift_definition（Canonical/Explanation/Intent Drift）・consistency_vector
（4軸）の定義は変更しない。

## 1. Drift Scoring Structure

各drift種別に固定重みを与え、観測されたdrift件数の単純加重和とする
（カウントベース、Phase7-C-1で予告した方式そのまま）。

```
DRIFT_WEIGHTS = {
    "canonical_drift":   3,   # time-stable anchorの前提が崩れる。最重
    "explanation_drift": 2,
    "intent_drift":      1,
}

score = sum(weight[drift_type] * count[drift_type] for drift_type in DRIFT_WEIGHTS)
```

- 重みは初期値であり、運用データが無い段階での仮置き。Phase7-C-3で
  実データに基づき見直す（変更は本文書の更新としてユーザー承認を要する）。
- スコアそのものはdriftの「記録・分類」のみに使う。閾値超えによる
  自動アクションは行わない（4章参照）。

## 2. Consistency Evaluator仕様

`ConsistencyEvaluator`は2つの`consistency_vector`（前回観測・今回観測）
を受け取り、以下の比較のみを行う（新規計算・推論は行わない）。

| 比較対象 | drift種別 |
|---|---|
| `canonical.cluster_id`（前回 vs 今回、同一`canonical_trace_id`） | canonical_drift |
| `explanation`の`why_this_meaning`/`final_judgement`（前回 vs 今回） | explanation_drift |
| `intent.cluster_refs`のうちcanonical一致分（前回 vs 今回） | intent_drift |

`replay`軸（`ReplayedTrace`）は本v1では直接比較対象にせず、
canonical/explanation driftの裏付け情報（trace_pathが同一か）として
将来のC-3で参照する余地のみを残す（v1では未使用）。

## 3. Anomaly Record Schema

```
AnomalyRecord = {
    canonical_trace_id: str,
    drift_type: "canonical_drift" | "explanation_drift" | "intent_drift",
    detected_at: str,          # ISO8601、生成時に呼び出し側が渡す
    before: dict,               # 比較対象フィールドの前回値（読み取り専用コピー）
    after: dict,                # 比較対象フィールドの今回値
    weight: int,
}
```

- AnomalyRecordはdrift_monitor_contract_v1.md5章の通りappend-onlyで
  記録する。上書き・削除メソッドは設けない。
- 記録のみであり、AnomalyRecord生成自体が何らかの修復・通知の
  トリガーになることはない（通知は4章のHuman Gate Hookに限る）。

## 4. Human Gate Hook契約

```
class HumanGateHook:
    def notify(self, records: list[AnomalyRecord]) -> None:
        """記録のみ。実際の通知手段(Slack/メール等)はPhase7-C-3以降で
        具象実装する。本v1では空実装(pass)のみを許可する。"""
```

- `notify()`は副作用を持たない空実装がデフォルト。具象実装（実際の
  通知）はPhase7-C-3以降、ユーザー承認後に追加する。
- `notify()`内でcluster再計算・自動修復・自動ロールバックを行うことは
  恒久的に禁止（drift_monitor_contract_v1.md5章を継承、本契約でも
  解除しない）。

## 5. 段階実装フロー（更新）

1. Phase7-C-1: Drift Monitor契約（完了）
2. **Phase7-C-2（本文書 + 最小スケルトン）**: scoring構造 +
   ConsistencyEvaluator + AnomalyRecord + 空のHuman Gate Hook。
3. Phase7-C-3（未着手・要承認）: 実データ接続 + Human Gate Hookの
   具象実装（実際の通知）+ 重みの再調整。

## 6. 変更ルール

この契約に変更を加える場合は「Phase変更レベル」として扱い、ユーザーの
明示的承認を要する。

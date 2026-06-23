# Phase7-B-5: Collision Governance Contract v1

Status: DRAFT (Phase7-B-5。最後の純設計フェーズ。解消しない設計)
Date: 2026-06-23

本文書はPhase7-B-4（[phase7_b4_order_normalization_v1.md](phase7_b4_order_normalization_v1.md)）
が検出した`OrderCollision`を前提に、**衝突解消をアルゴリズムではなく
権限設計として扱う**ことを契約として固定する。既存`OrderNormalizer`/
`StructuralTraceReader`のメソッド・出力構造は変更しない。

## 0. 前提（B-4からの継承）

```
decision_traceとmerge_graphは一致しない
どちらも"正しい可能性"がある
差分はエラーではなくOrderCollisionとして存在する
```

どちらを正とするかはデータでは決められない。本契約はこの事実を
受け入れ、解消ではなく**裁定権の設計**を行う。

## 1. 衝突の分類（固定・3種、この段階では解消しない）

```
structural_collision: 一方のソースにedge自体が存在しない、または
                       構造形状が一致しない（例: from/toの非対称）。
semantic_collision:    両ソースが同等の情報量を持ちながらrelation_type
                       が異なる（フィールド欠落で説明できない不一致）。
source_collision:      フィールド欠落差（例: merge_graph.jsonが
                       diameter_limit_hitを持たないこと）で説明可能な
                       不一致（B-4で実際に観測したケースはこれに該当）。
```

分類自体は構造的事実（どのフィールドが欠けているか）に基づく機械的
判定であり、「どちらが正しいか」の意味判断は含まない。

## 2. 解消権限の3層分離（確定）

```
Layer A: Algorithmic Layer
    - 非決定的・提案のみ。classification理由をalgorithmic_noteとして
      記録するが、これは「採用すべき結論」ではなく参考情報に過ぎない。
    - 状態を変更する権限を持たない。

Layer B: System Layer
    - 保留のみ。マージ禁止。GovernedCollisionRecordをそのまま保持する。
    - 自動的にstateを進める権限を持たない。

Layer C: Human Gate
    - 最終裁定のみ。state遷移（unresolved -> resolved等）はHuman Gateの
      明示的な判断によってのみ発生する（本契約のスコープでは遷移
      メカニズム自体は実装しない。エスカレーション通知のみを行う）。
```

## 3. 絶対禁止（完全禁止・確定）

```
自動マージ                禁止
スコアリングによる決定     禁止
"最適解"生成              禁止
collision logの圧縮・削除  禁止（完全保存）
```

## 4. 出力仕様

```
GovernedCollisionRecord = {
    from_cluster: str,
    to_cluster: str,
    classification: "structural_collision" | "semantic_collision" | "source_collision",
    algorithmic_note: str,        # Layer Aの非決定的な提案メモ（参考情報）
    relation_types: tuple,        # OrderCollisionから継承（生データ）
    sources: tuple,                # OrderCollisionから継承（生データ）
    state: "unresolved",          # 本契約のスコープでは常にunresolvedで開始
    escalated: bool,               # Human Gateへの通知を行ったか
}
```

- `state`は`"unresolved"`を必ず許容する（デフォルトかつ唯一の初期値）。
  解消済み状態への遷移メカニズムは本契約では実装しない（Human Gate側の
  別途の仕組みに委ねる、将来フェーズ）。
- collision logは完全保存する（`OrderCollision`の生フィールドを
  `GovernedCollisionRecord`にそのまま引き継ぐ、圧縮・削除しない）。

## 5. Human Gateエスカレーション構造（必須化）

`GovernedCollisionRecord`が生成された時点で、エスカレーション経路
（`CollisionEscalationHook.escalate()`）への通知を必須とする。
v1ではHookは空実装（記録のみ）がデフォルトであり、実際の通知手段
（Slack/メール等）の具象実装は将来フェーズ（要承認）。Drift Monitor
契約の`HumanGateHook`と同型の「記録のみ・自動アクション禁止」原則を
継承するが、型として混在させず別プロトコルとする（衝突ガバナンスと
drift監査は対象が異なるため、phase7_b4と同様に統合しない）。

## 6. 段階フロー

1. **Phase7-B-5（本文書 + CollisionGovernor実装）**: 完了対象。これが
   Phase7の最後の純設計フェーズ。
2. 以降は運用・統治設計フェーズへ移行（Human Gate裁定プロセス自体の
   設計、未着手・要承認）。

## 7. 変更ルール

この契約に変更を加える場合は「Phase変更レベル」として扱い、ユーザーの
明示的承認を要する。

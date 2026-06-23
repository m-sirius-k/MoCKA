# Phase7-B-7: Human Gate Interface Contract v1 (Cognitive Connection Layer)

Status: DRAFT (Phase7-B-7。データ/ロジック設計ではなく認知接続設計)
Date: 2026-06-23

本文書はPhase7-B-6（[phase7_b6_human_gate_ruling_v1.md](phase7_b6_human_gate_ruling_v1.md)）
が確立した裁定制度（`HumanGateRulingStore`、4種の裁定タイプ、非破壊原則）
を、人間が構造の一部として参加できる形に変換する契約を固定する。
既存`HumanGateRulingStore`/`GovernedCollisionRecord`のメソッド・出力
構造は変更しない。

## 0. 位置づけ（重要）

Phase7-B-6までは制度（裁定の規則）が完成した。本契約は制度そのものを
変更せず、その上に「保持された矛盾を人間が見える形に変換する層」を
追加する。これはUI実装ではなく、UIが従うべき**データ・状態・イベントの
契約**である。

## 1. 状態モデル（4種・判断ではなく状態遷移）

```
pending     - GovernedCollisionRecordが存在し、RulingRecordが一件も無い
observed    - 人間が確認したが裁定はまだ無い、またはdefer裁定がある
decided     - accept/reject/splitのいずれかの裁定が存在する
conflicted  - decided後に同一collisionが再び検出された（再衝突）
```

状態は**RulingRecord履歴とGovernedCollisionRecordの再検出有無から
導出されるものであり、状態自体を直接設定するメソッドは存在しない**
（状態を書き込む行為そのものが「判断」になってしまうため）。

```
状態遷移（導出ロジックのみ・確定）:
ruling履歴が空                              -> pending
ruling履歴の最新がdefer                     -> observed
ruling履歴にaccept/reject/splitが存在し、
  かつ同一collisionが再検出されていない      -> decided
ruling履歴にaccept/reject/splitが存在し、
  かつ同一collisionが再検出された            -> conflicted
```

## 2. 裁定UIの役割（確定・誤解の防止）

```
誤解: UIは「決定する場所」
正解: UIは「collisionの可視化と選択点の提示装置」
```

UIが表示すべき最小情報（`CollisionView`、読み取り専用射影）:

```
- 何が衝突しているか        (relation_types, sources)
- どの層でズレているか      (classification: structural/semantic/source)
- どの履歴に依存しているか  (ruling履歴、algorithmic_note)
- 現在の状態                (state: pending/observed/decided/conflicted)
```

`CollisionView`は既存`GovernedCollisionRecord`とruling履歴を束ねる
だけであり、新たな判断・推論・要約生成は行わない。

## 3. 通知経路（イベント化された判断）

```
裁定は即時ではなくeventとして流れる
historyに積まれる（append-only、Phase7-B-6から継続）
他レイヤへは非同期反映される（本契約は反映の受信側を実装しない）
```

`HumanGateRulingStore.submit_ruling()`の呼び出しを`RulingEvent`として
記録する`HumanGateEventLog`を追加する。既存`HumanGateRulingStore`の
内部実装は変更せず、外側から呼び出しをラップしてイベント化する。

```
RulingEvent = {
    from_cluster, to_cluster, ruling_type, rationale, recorded_at,
    emitted_at: None,   # システムによる時刻生成は行わない(契約継承)。
                          呼び出し側が必要なら別途記録する。
}
```

## 4. 絶対禁止 / 許可

禁止:
- 状態（pending/observed/decided/conflicted）を直接設定するメソッドの提供
  （状態は常に導出値であり、書き込み対象にしない）
- `CollisionView`内での新たな判断・要約・推論生成
- 既存`HumanGateRulingStore`/`GovernedCollisionRecord`のメソッド・
  出力構造の変更
- イベントの削除・上書き（append-onlyのみ）

許可:
- ruling履歴とcollision再検出有無からの状態導出（読み取りのみの計算）
- `CollisionView`の構成（既存データの束ねのみ）
- `RulingEvent`の新規追加（append-only）

## 5. 段階フロー

1. **Phase7-B-7（本文書 + CollisionStateTracker/CollisionView/HumanGateEventLog）**: 完了対象。
2. 以降（未着手・要承認）: 実際のUI実装、他レイヤへの非同期反映の具象化
   （Drift Monitor契約のHumanGateHookとの接続検討含む）。

## 6. 変更ルール

この契約に変更を加える場合は「Phase変更レベル」として扱い、ユーザーの
明示的承認を要する。

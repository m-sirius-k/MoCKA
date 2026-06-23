# Phase7-B-6: Human Gate Ruling Contract v1

Status: DRAFT (Phase7-B-6。統治設計。実装は最小スケルトンのみ)
Date: 2026-06-23

本文書はPhase7-B-5（[phase7_b5_collision_governance_v1.md](phase7_b5_collision_governance_v1.md)）
が定義した`GovernedCollisionRecord`（常に`state=unresolved`で開始）に
対する裁定制度を固定する。既存`CollisionGovernor`/`OrderNormalizer`/
`StructuralTraceReader`のメソッド・出力構造は変更しない。

## 0. Human Gateの再定義（最重要）

```
誤解: 人間が最終チェックする仕組み/フィルタリング層/例外処理の出口
正解: 矛盾を"意味として成立させる唯一の層"
```

Human Gateは最適化装置でも解決装置でも正規化装置でもない。
**「矛盾の意味的分岐点を固定する装置」**である。裁定は矛盾を消す
ことではなく、矛盾に対する人間の立場（accept/reject/defer/split）を
記録として固定することに等しい。

## 1. 裁定タイプ（固定・4種のみ）

```
accept  - この衝突における特定の解釈を採用する
reject  - この衝突における特定の解釈を採用しない
defer   - 裁定を保留する（unresolvedのまま維持する人間の明示的判断）
split   - 単一に統合せず、両方の解釈を分岐として保持する
```

**`merge`（統合）は選択肢に含めない。** 統合はPhase7-B-5が確立した
「衝突は解消しない」という原則の否定になるため、本契約では恒久的に
除外する。

## 2. 裁定の対象（確定）

- 裁定の対象は**collision単位**（`GovernedCollisionRecord`の
  `(from_cluster, to_cluster)`組）に限定する。
- `trace_chain`や`merge_graph`そのものへの直接裁定は禁止する。
  必ず`GovernedCollisionRecord`という中間レイヤを介して裁定する。
- これにより、裁定がPhase7-B-3/B-4の構造復元・整列ロジックに
  直接影響を与えることを構造的に防ぐ。

## 3. 非破壊原則（絶対条件）

```
元データ（decision_trace.json/merge_graph.json/adapter_enrichment.jsonl）
                              の変更は禁止
GovernedCollisionRecordの変更・上書きは禁止
裁定は必ず新しい解釈レイヤ(RulingRecord)として追加保存する
```

裁定はGovernedCollisionRecordを書き換えるのではなく、それを参照する
**別レイヤのRulingRecord**として独立に保存される。同一collisionに対し
複数のRulingRecordが時系列で積み重なることを許容する（最新の裁定が
過去の裁定を上書き・削除することはない、append-only）。

## 4. 出力構造（確定）

```
RulingRecord = {
    from_cluster: str,
    to_cluster: str,
    ruling_type: "accept" | "reject" | "defer" | "split",
    rationale: str | None,     # 人間が記録する裁定理由(任意・テキスト)
    recorded_at: str | None,   # 呼び出し側(Human Gate運用者)が提供する値。
                                # システムによる時刻生成は行わない。
}
```

- `recorded_at`はシステムが現実時刻を生成・推測するものではなく、
  人間（または既存の`mocka_write_event`等の記録主体）が明示的に渡す
  値を素通しするだけである（既存契約群の「timestamp生成禁止」は
  システムによる時刻の創出を禁止する趣旨であり、人間が提供する記録
  時刻の保存自体は禁止しない）。

## 5. 絶対禁止 / 許可

禁止:
- `merge`（統合）を裁定タイプとして受理すること
- collision以外（trace/graph fragment）への直接裁定
- 元データ・GovernedCollisionRecordの変更・上書き
- RulingRecordの削除・上書き（append-onlyのみ）
- 裁定の自動生成・自動推論（裁定は常に人間からの明示的入力を要する）

許可:
- collision単位でのRulingRecord新規追加（複数回・時系列で積み重ね可）
- 既存RulingRecord履歴の読み取り

## 6. 段階フロー

1. **Phase7-B-6（本文書 + HumanGateRulingStore最小スケルトン）**: 完了対象。
2. 以降（未着手・要承認）: Human Gateが裁定を生成する内部モデル
   （裁定UI・通知経路の具象化、CollisionEscalationHookとの接続）。

## 7. 変更ルール

この契約に変更を加える場合は「Phase変更レベル」として扱い、ユーザーの
明示的承認を要する。

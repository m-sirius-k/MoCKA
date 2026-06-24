# Phase10-4: Operational Observation Layer（宣言のみ）

## 1. 位置づけ

Phase10-3（FROZEN、`WP_PHASE10_3_BASELINE`としてwatchpoint化済み）を基点とし、
Phase10-4は「意味を増やす段階」ではなく「**意味が動くかを見る段階**」として開始する。

本文書はPhase10-4の**宣言のみ**であり、実装・拡張・設計深化は含まない。

## 2. 目的

Signal / Reasoning（およびその他観測系: Drift Monitor / tech_watcher / Essence pipeline / Advisor）の
**動作挙動をログ化**する。再定義ではなく「振る舞いの収集」。意味ではなく**差分**の蓄積。

## 3. 禁止事項

- Phase10-3の再設計
- Signal / Reasoningの再定義・再再定義
- 追加理論の生成
- Relay / Orchestra / PHI-OSの再設計
- 実装・拡張・設計深化（本フェーズはまだ「宣言」段階）

## 4. 観測の定義（固定）

```
Observation = Signal/Reasoningの状態変化ではなく、差分発生の事実記録
```

評価・解釈・状態変化そのものの記述ではなく、「差分が存在したという事実」のみを観測対象とする。

## 5. 計測対象（3種類に限定、固定）

1. Structure Drift
   - ファイル構造の変化
   - パス・参照・依存関係の変化
2. Semantic Drift
   - 意味定義の変化（再定義は禁止、差分の有無のみ）
3. Operational Drift
   - 実行手順・イベント順序の変化

この3種以外を計測対象に加えない。

## 6. 評価禁止（重要制約）

以下は禁止：

- 良い/悪いの判定
- 正しい/間違いの判定
- 変化の説明

許可される記録はこれだけ：「差分が存在したという事実の記録」。

## 7. Phase10-3との関係（固定）

- Phase10-3 = baseline（`WP_PHASE10_3_BASELINE`、不変）
- Phase10-4 = baselineとの差分観測層
- 相互作用は禁止（干渉なし。Phase10-4の観測はPhase10-3契約本体・Signal/Reasoning定義を変更しない）

## 8. 最小ログ形式（固定）

```
event_id
target
drift_type
before_ref
after_ref
timestamp
```

解釈フィールド（reason / meaning / evaluation等）は禁止。

## 9. Trigger Model（固定）

### 9.1 発火条件（単一化）

```
Trigger = Phase10-3 baselineとの差分を伴う状態変更イベント発生時
```

### 9.2 トリガー対象イベント（4種に限定）

1. Git state change（commit / tag / branch変更）
2. Event log write（mocka_write_event発生）
3. File structure change（path追加 / 削除 / 移動）
4. Semantic declaration change（definition fileの更新、宣言のみ。再定義は対象外）

この4種以外をトリガー対象に加えない。

### 9.3 禁止事項（重要制約）

- polling監視
- continuous inference
- 推測ベース検知

許可されるのは「明示イベントが発生した瞬間のみ観測」。

### 9.4 観測フロー（固定順序）

1. Event発生検知
2. Phase10-3 baseline参照
3. Drift type判定（3種のみ。第5章参照）
4. ログ記録

これ以外の処理は禁止。

### 9.5 Phase10-4の性質（再固定）

Phase10-4 = 「イベント駆動型・無推論差分記録機構」。
観測層（非常駐・event-only）/ 非推論（no interpretation）/ 非評価（no judgment）。

## 10. 状態

DECLARED（Trigger Model確定・宣言のみ）。実装（ログ出力フォーマット・ストレージ位置）着手は次回Human Gate明示裁定待ち。

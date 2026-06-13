# Self-Learning Kernel (Phase 4-1)

## 目的

Feedback Loop(Phase 3-2)が生成する`FeedbackProposal`を、MoCKAの
内部状態(重みパラメータ)へ反映可能な「学習アクション」へ変換し、
**Validation → Queue → Governance確認 → Applier**の三段階適用構造を
通じて、安全に・遅延を伴って・検証済みのみ反映する層である。

これにより、MoCKAは「改善提案を出すシステム」から「改善が内部状態に
反映されるシステム」へ進化する。

> **本層はMoCKAの中で最も危険性が高い層である。**
> 設計原則は一つ:「学習は必ず遅延され、必ず検証されること」。
> 本フェーズはMoCKAの「自己進化の最終ゲートウェイ」である。

## 絶対禁止事項

- 自動コード書き換え
- 即時学習反映(Queueを経由しない適用)
- Governanceバイパス
- 破壊的更新(rollback不可能な更新)
- 無制限パラメータ変更(`MAX_DELTA`/`PARAM_BOUNDS`を超える変更)

## 許可範囲

- 重み調整(`decision.priority_weights` / `decision.risk_weights` /
  `decision.rationale_weight_bias`)
- パラメータ更新提案(`memory.*` / `semantic.*`)
- キュー化(`LearningQueue`への登録)
- 段階適用(`approve` → `apply`、Governance確認後のみ)

## 学習構造(三段階適用構造)

```
FeedbackProposal
   |
   v
Validation Layer (Governance)
   |
   v
Learning Queue
   |
   v
Kernel Update
```

具体的なファイル構成:

```
learning_kernel/
    learning_registry.py      — 学習対象パラメータ定義/範囲/閾値/rollbackルール
    learning_state.py          — LearningState (frozen dataclass)
    weight_state_store.py      — LearningStateのJSON永続化・apply_delta/rollback
    learning_model.py           — LearningAction / ValidationResult / LearningUpdate
    update_validator.py         — 安全性検証(Governance/範囲/risk/stability)
    learning_engine.py           — FeedbackProposal -> LearningAction 変換
    learning_queue.py            — LearningUpdateのキュー管理(JSON永続化)
    learning_applier.py          — approved Updateの適用(WeightStateStore反映)
    learning_pipeline.py         — Feedback -> Learning -> Queue の実行、
                                    approve_and_apply / rollback
    learning_integration_test.py
    learning_safety_test.py
    learning_queue_test.py
```

## Feedbackとの関係

`learning_engine.LearningEngine.convert()`は、Feedback Loopが生成する
`FeedbackProposal.suggested_change["weight_adjustment"]`から
`parameter` / `suggested_delta` / `direction`を取り出し、
`learning_registry.LEARNING_PARAM_MAP`を用いてLearning Stateの
パラメータパス(例: `decision.priority_weights.intent_clarity`)へ
変換する。

`LEARNING_PARAM_MAP`に対応エントリが存在しない場合(例:
`rationale_improvement` や `registry_candidate` のような「重み更新で
はない提案」)は`convert()`が`None`を返し、Learning Kernelの対象外
となる(提案としては引き続きFeedback Loop側に残る)。

`invert`フラグが`True`の場合(例: `memory.intent_match`の増加提案 →
`memory.relevance_decay_rate`の減少として学習する)、deltaの符号を
反転して適用する。

## Governance制御構造

`LearningPipeline.run()`は内部で`FeedbackPipeline().run()`を実行し、
その結果(`FeedbackBatch.governance_status`、
`structural/GOVERNANCE_REGRESSION_SUMMARY.md`の"Overall PASS"確認に
基づく)を`UpdateValidator.validate()`へ渡す。

`governance_status != "PASS"`の場合、`update_validator`の
`governance_compliance`チェックが`False`となり、
`ValidationResult.passed = False`となる。この場合
`LearningQueue.enqueue()`は当該Updateを`status="rejected"`として
登録し、Queueには積まれるが適用対象にはならない。

`LearningApplier.apply()`もまた、適用直前に
`governance_status == "PASS"`であることを再確認し、そうでない場合は
`ValueError`を発生させ、Learning Stateを一切変更しない。

## 更新ルール(Update Flow)

```
FeedbackProposal
   |
   v
Learning Engine        (feedback解析・layer分類・delta変換)
   |
   v
Update Validator         (governance/範囲/risk/stability検証)
   |
   v
Learning Queue           (pending / rejected として保管)
   |
   v
Governance Check          (approve_and_apply時に再確認)
   |
   v
Learning Applier           (approved のみ WeightStateStore へ適用)
   |
   v
Updated Learning State
```

`LearningPipeline.run()`は上記フローのうち「Learning Queueへの登録」
までを行い、Learning State自体は変更しない(即時反映禁止)。承認
(`LearningQueue.approve()`)と適用(`LearningApplier.apply()`、または
`LearningPipeline.approve_and_apply()`)は別途明示的に呼び出す必要が
ある。

### Update Validatorの検証項目

| チェック | 内容 |
|---|---|
| `governance_compliance` | `governance_status == "PASS"` であること |
| `allowed_target` | パラメータが`PARAM_BOUNDS`で許可された学習対象であること |
| `max_delta` | `\|delta\|` が `MAX_DELTA`(0.10)以下であること |
| `bounds` | 適用後の値が`PARAM_BOUNDS`の範囲内であること |
| `risk_increase` | `decision.risk_weights.*`を増加させる場合、増加量が`RISK_INCREASE_LIMIT`(0.05)以下であること |
| `stability` | 直近`STABILITY_WINDOW`件中の`applied`割合から算出する`stability_score`が`STABILITY_THRESHOLD`(0.5)以上であること |

いずれか1つでも不合格の場合、`ValidationResult.passed = False`となり、
`LearningQueue.enqueue()`は`status="rejected"`として登録する。

## Queue設計

`LearningQueue`は`learning_kernel/data/learning_queue.json`に
`{"updates": [LearningUpdate, ...]}`の形式で永続化する。

`LearningUpdate`の構造:

| フィールド | 内容 |
|---|---|
| `update_id` | `LU-{連番}-{action_id}` 形式の一意なID |
| `action` | 変換元の`LearningAction`(`target_layer`/`parameter`/`delta`等) |
| `status` | `pending` / `approved` / `rejected` / `applied` / `rolled_back` |
| `validation_result` | `UpdateValidator`による検証結果(`passed`/`checks`/`reasons`) |

状態遷移は以下のみ許可される:

```
pending  --approve()-->  approved  --apply()-->  applied  --rollback-->  rolled_back
pending  --reject()-->   rejected
(validation失敗)  -->     rejected  (enqueue時点で即時rejected)
```

`approved`以外からの`apply()`、`pending`以外からの`approve()`、
`applied`以外からの`mark_rolled_back()`は、いずれも`ValueError`と
なる。

## Safety設計

1. **自動コード変更禁止**: Learning Kernelはコード(.py)を一切変更
   しない。変更対象は`learning_kernel/data/learning_state.json`内の
   数値パラメータのみであり、これは元来Decision/Memory/Semantic
   Layerの実コード・Registryとは独立した「shadow weight-state」
   である。
2. **Governance未承認の適用禁止**: `governance_status != "PASS"`の
   場合、Validatorは`governance_compliance`で不合格とし、
   `LearningApplier.apply()`もこれを再検証して適用を拒否する。
3. **即時反映禁止(キュー経由必須)**: `LearningPipeline.run()`は
   `LearningQueue.enqueue()`までで処理を終え、Learning Stateの
   変更は一切行わない。Learning Stateの変更は`apply()`経由のみで
   発生する。
4. **破壊的更新禁止**: `apply_delta()`は常に直前の`LearningState`を
   `WeightStateStore`の`history`へ退避してから値を更新するため、
   すべての更新は`rollback()`で復元可能である。
5. **無制限パラメータ変更禁止**: `MAX_DELTA`(全パラメータ共通の
   最大変化量)、`RISK_INCREASE_LIMIT`(risk重み増加の上限)、
   `PARAM_BOUNDS`(パラメータごとの値域)により、1回の更新で変化
   できる範囲を厳格に制限する。

## Rollback設計

`WeightStateStore`は`apply_delta()`実行前の`LearningState`を
`history`(リスト)に追加してからJSONへ保存する。

`WeightStateStore.rollback(steps=1)`は`history`から直前の
`LearningState`を取り出し、現在の状態として復元・保存する。

`LearningPipeline.rollback(steps=1)`は、`WeightStateStore.rollback()`
に加えて、`LearningQueue`上の直近`status="applied"`の
`LearningUpdate`を新しい順に`status="rolled_back"`へ更新する
(Queueの履歴とLearning Stateの整合性を保つ)。

Rollbackが推奨されるトリガー(`learning_registry.ROLLBACK_TRIGGERS`):

- `performance_degradation`(性能劣化)
- `audit_failure`(Self-Audit Layerの評価悪化)
- `stability_drop`(stability_scoreの低下)

これらは将来、Self-Audit Layer/Feedback Loopとの連携により自動検知
される想定だが、本フェーズではrollback機構そのものの提供のみを行い、
トリガー判定の自動化は範囲外とする。

## 将来の自律進化構想

現状、`LearningQueue`の`approve`/`reject`、および
`LearningApplier.apply()`の呼び出しは、人間または上位プロセスが
明示的に行う。将来的には:

1. Self-Audit Layerが`apply`後の`AuditReport`を再評価し、
   `stability_score`の悪化を検知した場合に自動で
   `LearningPipeline.rollback()`を呼び出す「監視ループ」
2. 承認パターンの蓄積(どのような`LearningAction`が承認されやすいか)
   を、Feedback Loopの`confidence`/`priority`調整へフィードバックする
   メタ学習
3. 複数の`LearningUpdate`を束ねた「学習バッチ」の承認・適用、および
   バッチ単位のrollback

という段階を想定する。いずれの段階でも、Learning Kernel自身が
Governanceをバイパスして適用を行うことはなく、「変換 → 検証 →
キュー → Governance確認 → 適用」という非破壊的な多段構成を維持する。

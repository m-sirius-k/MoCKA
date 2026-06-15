# PRE_CONSTRAINT_ARCHITECTURE_LIFECYCLE_v1.md
# Pre-Constraint Architecture — 設計思想 / PlanningCaliber〜MoCKA移行基準文書

Document ID: PRE_CONSTRAINT_ARCHITECTURE_LIFECYCLE_v1
Version: 1.0.0
正本: [docs/architecture/PRE_CONSTRAINT_ARCHITECTURE_v1.md](../architecture/PRE_CONSTRAINT_ARCHITECTURE_v1.md)
機械可読展開: [runtime/constraints/pre_constraint_layer_v1.json](../../runtime/constraints/pre_constraint_layer_v1.json)

---

## 1. なぜ「初期制約固定」が必要か

MoCKAでは仕様揺れが事故の発生源になりやすい（過去のChatGPTインシデント等）。
Pre-Constraint Architectureは、**初期に重い設計コストを払うことで、後工程（実行・圧縮・再生成）の
コストとリスクを構造的に下げる**ための制度。

「初期設計の重さ」は負債ではなく、後工程削減のための投資として位置づける。

## 2. PlanningCaliber → MoCKA 昇格の基準

| 段階 | 内容 | Pre-Constraint Layerとの関係 |
|---|---|---|
| P0 | 実験開始（PlanningCaliber workshop） | Pre-Constraint Layerの制約下で自由に試行 |
| P1 | 構造検証 | 制約適合性をAudit/Verification Layerで確認 |
| P2 | Human Gate審査 | 制約違反がないことを人間が確認 |
| P3 | MoCKA本体への統合候補化 | Pre-Constraint Layerは不変のまま統合準備 |
| P4 | MoCKA本番稼働 | Pre-Constraint Layer適用のまま本番運用 |

いずれの段階でもPre-Constraint Layer自体は変更されない。変更が必要になった場合は
P0に戻るのではなく、**Pre-Constraint Architectureの新バージョン（v2）を分岐**し、
新バージョン適用下で再度P0からの検証を行う。

## 3. 既存構造との関係（再掲・運用視点）

- **Shadow Execution Layer（shadow_Movement）**: 部分障害時の縮退運用。Pre-Constraint Layerの
  制約はshadow運用中も維持される（75%機能維持の対象は機能、制約は対象外）。
- **Audit / Verification Layer**: `mocka-seal` / `verify_all.py` のALL CHECKS PASSEDは、
  Pre-Constraint Layerに対する適合性証明として機能する。
- **PlanningCaliber実験ループ**: 実験は自由だが、Pre-Constraint Layerという「変わらない土台」の
  上で行われることで、実験結果の再現性・比較可能性が保証される。

## 4. 運用ルール（まとめ）

1. Pre-Constraint Layerは変更禁止。新バージョン分岐のみ許可。
2. Execution Layerの実装・生成物は、必ずPre-Constraint Layerの制約セット
   （`runtime/constraints/pre_constraint_layer_v1.json` の `active_constraints`）を参照する。
3. Compression Layer（要約・圧縮・再生成）は、Pre-Constraint Layerを書き換える権限を持たない。
4. 本ドキュメント・正本・JSON展開の3つは常にバージョン番号を一致させる。

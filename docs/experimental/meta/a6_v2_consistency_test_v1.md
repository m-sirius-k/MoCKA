# A6-v2 Consistency Test v1 (検証仕様 + 実判定結果)

Status: EXPERIMENTAL / META / NON-CANONICAL
Date: 2026-06-24
作成者: Claude(別チャット, Claude Code環境) / 整理・登録: Claude-sonnet-4-6
対象: A6-v2(seal_a6_final_v1 + seal_a6_v2_final_v1で確定したファイル群)

## 0. 必須ラベル(本文書の位置づけ、最重要)

- 本文書は検証仕様の定義と、それを既存アーティファクトに適用した実判定結果の
  両方を含む。実行・データ処理・Trigger Wiring(A7)には一切踏み込まない(検証は
  ファイル内容の静的読解のみによって行われた)。
- 正式governanceではない。判定結果は`docs/experimental/meta/`内の整合性確認に
  限定され、`docs/governance/`配下の正式文書の正当性を判定するものではない。
- 出力形式: PASS(整合) / WARN(境界注意、是正済みまたは是正不要だが記録要) /
  FAIL(構造破綻、即時対応要)。

## 1. 検証対象アーティファクト一覧

1. `interface_contract_formalization_experiment_v1.md`
2. `boundary_of_formal_system_v1.md`
3. `external_dependency_structure_v1.md`
4. `integrated_architecture_compressed_v1.md`(レイヤ番号v1.1の正)
5. `l0_l3_locked_institutional_diagram_v1.svg`
6. `institutional_locked_diagram_v1.md`
7. `structural_consistency_layer_v2.md`

## 2. 構造整合性(Structural Integrity)

| 検証項目 | 判定 | 詳細 |
|---|---|---|
| SVGノードとContract定義の1対1対応 | PASS | `structural_consistency_layer_v2.md`3.1節の対応表で全SVGノード/要素(L0枠/L1 4モジュール/L2 4モジュール/L3枠/各矢印/3アニメーション)がいずれかのMarkdown条項に対応づけられている。逆方向(条項→図形)も一意。 |
| L0-L3レイヤの重複・欠落検知 | PASS | `integrated_architecture_compressed_v1.md`でL0-L3各1回のみ定義。重複・欠落なし。 |
| 矢印方向の規約違反検知 | PASS | SVG実装(L3→L2/L2→L1/各層→L0実線/L0→L3のみ破線)と`institutional_locked_diagram_v1.md`第3章の記述が完全一致。 |

## 3. 意味整合性(Semantic Consistency)

| 検証項目 | 判定 | 詳細 |
|---|---|---|
| 公理(A1-A6)間の論理矛盾検出 | PASS | `structural_consistency_layer_v2.md`2.4節(公理系メタ整合性検査v1)で循環依存なし・非冗長・過剰制約なしを確認済み。 |
| L0非構造ルールの侵害検知 | PASS | SVG・`institutional_locked_diagram_v1.md`・`external_dependency_structure_v1.md`のいずれもL0をノード化していない。一貫性あり。 |
| 概念重複・意味衝突の検出 | **WARN** | `boundary_of_formal_system_v1.md`・`external_dependency_structure_v1.md`の本文(第1-9/10章)は旧レイヤ番号(L0=実在/L1=正式governance/L2=形式体系/L3=メタ境界)を使用したままであり、`integrated_architecture_compressed_v1.md`のv1.1番号(L0=外部/L1=実行層/L2=監査制御層/L3=メタ境界)と字面上は一致しない。両ファイルの0a節に互換注釈(legacy semantics明記)を追加済みのため実害はないが、本文自体は未更新。将来この2ファイルを読む者が0a節を読み飛ばすと誤読しうる。是正は任意(本文書での記録により対応済みとみなす)。 |

## 4. 制約整合性(Constraint Validity)

| 検証項目 | 判定 | 詳細 |
|---|---|---|
| Lock MDの禁止事項違反チェック | PASS | `structural_consistency_layer_v2.md`第4章で「L0機能化/監査層化/自動化/削除統合」「既存SVG/Lock MDへの逆方向書き込み」のいずれも発生していないことを確認。 |
| v1/v2ルール衝突検出 | PASS | v2(`structural_consistency_layer_v2.md`)は既存v1ファイル群を無変更のまま追加されたのみ(git実績: 1ファイル新規のみ、既存ファイルへの変更なし)。衝突なし。 |
| 優先順位ルールの適用確認 | **WARN** | `structural_consistency_layer_v2.md`3.2節の公理優先順位ルール(A6最優先、A3次点)は定義済みだが、実際に優先順位判定が必要になった衝突事例はこれまで発生していない(理論定義のみ、実適用未検証)。FAILではないが、未実証であることを記録する。 |

## 5. 差分整合性(Version Consistency)

| 検証項目 | 判定 | 詳細 |
|---|---|---|
| v1→v2での変更影響範囲特定 | PASS | git実績確認: `seal_a6_v2_final_v1`コミットは`structural_consistency_layer_v2.md`1ファイルの新規追加のみ(137 insertions、既存ファイル変更0件)。 |
| 非影響領域の固定確認 | PASS | A6-v1で確定した6アーティファクト(Interface Contract/HAB境界/外部依存構造/統合アーキテクチャ/SVG/ロックMD)はv2作成時点で内容変更なし。 |
| 意味差分/構造差分/拡張差分の分類検証 | PASS | `structural_consistency_layer_v2.md`5節の自己分類(拡張差分)は、上記git実績(新規追加のみ・既存変更なし)と一致する。分類の自己整合性が取れている。 |

## 6. 不変条件(Hard Constraints)の確認

| 条件 | 判定 | 詳細 |
|---|---|---|
| L0は非構造アンカーであること | PASS | 全アーティファクトで一貫してノード化されていない。 |
| A6は実行層を持たないこと | PASS | いずれの文書にも実行コード・トリガー条件は含まれない。 |
| A7(Trigger Wiring)への接続禁止 | PASS | 全文書で明示的に「A7不接続」を記載。実装も存在しない。 |
| runtime stateとの統合禁止 | PASS | git seal時にPlanningCaliber/workshop/phi-os/ise/data/current_state.json(実際のランタイム状態ファイル)を明示的にstage対象から除外し、混入を防止済み。 |

## 7. 総合結論

- PASS: 11項目
- WARN: 2項目(いずれもFAILではなく、是正済みまたは実害なしの記録)
- FAIL: 0項目

**A6-v2は構造的・意味的・制約的・版管理的に矛盾なく成立していることが、既存
アーティファクトの実際の内容確認によって確認された。** 2件のWARNは将来の参照者
向けの注意記録であり、いずれもA6-v2の閉包性(seal_a6_v2_final_v1)を損なうもの
ではない。

## 8. 実装状態

本文書はいかなる実装・コード変更も含まない。コード・実行システムは一切
実装していない。判定はファイル内容の読解のみによって行われた。

## 9. 現在の運用状態(本文書の効力範囲外の事実)

2026-06-24時点の実際の状態は本文書により変化しない:
FROZEN=不変、Extension=DRAFT、Human Gate=未裁定、pre-authorization state=継続中、
Trigger Wiring=凍結継続。

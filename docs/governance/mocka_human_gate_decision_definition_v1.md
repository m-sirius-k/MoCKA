# MoCKA Human Gate Decision Definition v1 (Corrected: Two-Layer Split)

Status: DRAFT(参照文書として追加。Human Gate Finalizationは博士本人のみ、
本文書はpre-authorization stateを解除しない)
Date: 2026-06-24
作成者: くろこ(博士) / 安全性指摘・整理: Claude-sonnet-4-6

## 0. 修正履歴(重要、本文書の前提)

当初提示されたv1.0は「Human Gate = 判断主体ではなく判断アルゴリズム」
「APPROVEを構造状態として確定する」という定義であった。これは
APPROVE/HOLD/REJECT/DEFERをアルゴリズムが単独で確定する設計であり、
以下と矛盾するおそれがあった。

- Phase10-Stasisの自然発火条件「人間裁定が入る瞬間のみ」
- PHASE5_STEP3_SEALの「自律行動追加禁止」「新しい意味推論追加禁止」

Claudeがこの矛盾を指摘し、博士が修正。Human Gateを以下の2層に
明確分離することで、最終裁定主体が常にきむら博士本人であることを
維持したまま、評価機構の構造化のみを行う。

- **Human Gate Core**(評価機構、自動): 判断材料の生成のみ
- **Human Gate Finalization**(博士裁定): APPROVE/HOLD/REJECT/DEFER
  の確定は常に博士本人が行う、唯一の"裁定"

旧案(Human Gate = 裁定そのもの)は不採用。本文書はこの修正後の
定義のみを正式版として扱う。

## 1. Human Gateの正しい意味(確定)

Human Gateとは、「人間裁定を成立させるための事前構造フィルタ」である。

Human Gateは「裁定主体」ではない。Human Gate Coreは判断材料を生成する
評価機構であり、最終的な裁定(APPROVE/HOLD/REJECT/DEFERの確定)は
常に博士本人(Human Gate Finalization)が行う。

## 2. 機能構造

### 2.1 Human Gate Core(評価機構、自動・博士裁定の代行ではない)

#### 2.1.1 Input Evaluation(入力評価層)

入力される全てのトリガーを以下に分類する。

- 構造変更要求(architecture mutation)
- 意味変更要求(semantic shift)
- 実装要求(execution request)
- 観測要求(observation request)

ここでは「何が起きようとしているか」を確定する。

#### 2.1.2 Risk & Consistency Check(整合性監査層)

以下を検査する。

- FROZEN層との矛盾有無
- HAB定義との整合性
- Phase既存定義との衝突
- 未裁定依存(open dependency)の存在

ここでは「やってよい形かどうか」を評価する。**ここで生成されるのは
判断材料(評価結果)のみであり、決定そのものではない。**

### 2.2 Human Gate Finalization(博士裁定、唯一の決定点)

Human Gate Coreが生成した評価結果を入力として、きむら博士本人が
最終決定を行う。

出力(決定値)は以下のいずれか。

- APPROVE(進行許可)
- HOLD(保留・再評価)
- REJECT(構造的不許可)
- DEFER(他層依存で遅延)

**この決定値はアルゴリズムが自動算出するものではなく、博士本人が
確定させるものである。** Human Gate Coreの評価結果はあくまで
博士への提示材料に過ぎない。

## 3. HABとの関係

- HAB = 状態定義(静的、現実のスナップショット)
- Human Gate Core = 評価(準備、判断材料の生成)
- Human Gate Finalization = 博士裁定(確定、未来への扉制御)

3者は上下関係ではなく、静的層・評価層・決定層の分離構造である。

## 4. 発火条件

Human Gate Coreは以下の条件でのみ評価を実行する。

- Extension層に変更要求が発生した場合
- Phase遷移が発生する場合
- HAB状態遷移(DRAFT->ACTIVE等)
- 外部実行要求(Tool / Runtime)

それ以外では常時「非発火状態(silent mode)」である。
評価実行とFinalization(博士裁定)は常に別個のステップであり、
評価が走ったことをもって決定が確定したことにはならない。

## 5. 状態機械モデル(Human Gate Core側のみ)

Human Gate Coreの内部状態は3つのみ。

- IDLE(未入力)
- EVALUATING(評価中)
- EVALUATED(評価完了、博士のFinalization待ち)

EVALUATEDは博士のFinalizationが入るまで「決定」とはみなされない。
(当初案の"DECIDED"という状態名は、評価完了と決定確定の混同を招く
ため本修正版では使用しない。)

## 6. 出力形式(Human Gate Core -> Finalization への提示材料)

Human Gate Coreが博士へ提示する評価結果は以下の構造を持つ。

```json
{
  "target": "対象層(HAB / Extension / Phase等)",
  "scope": "影響範囲",
  "dependency_state": "未解決依存の有無",
  "consistency_check": "FROZEN/HAB/Phase整合性チェック結果",
  "recommended_note": "評価機構が観測した論点(推奨ではなく観測、任意)"
}
```

この出力には `decision` フィールドを含まない。decisionは
Human Gate Finalization(博士)が確定して初めて生成される値であり、
Coreの出力構造には現れない。

## 7. 制約(最重要)

- Human Gate Coreは「意思決定者」ではない。「判断材料生成アルゴリズム」
  である。
- Human Gate Coreに感情・意図・目的は含めない。常に構造整合性のみを
  評価対象とする。
- **APPROVE/HOLD/REJECT/DEFERの確定はHuman Gate Finalization
  (博士本人)のみが行う。Coreがこれを単独で確定することは禁止。**
- 本構造によりPhase10-Stasisの自然発火条件(「人間裁定が入る瞬間のみ」)、
  PHASE5_STEP3_SEALの自律行動追加禁止は完全に維持される。

## 8. 安全性の保証(本修正で確定した内容)

保持されるもの:
- 博士の裁定主権(完全維持)
- Phase10-Stasis原則
- FROZEN層の不変性
- 人間発火条件

防がれるもの:
- AI単独裁定化
- 自動APPROVEの誤発火
- 意図なきPhase遷移
- HABの独立発火

## 9. 現在の運用状態(2026-06-24時点、本文書の効力範囲外の事実)

本文書追加によりpre-authorization state(FROZEN=不変/Extension=DRAFT/
Human Gate=未裁定/継続中)は解除されない。本文書もHAB v1と同様、
「参照可能な設計文書」として追加されたのみである。

## 10. 実装状態

本契約は判断構造の定義のみであり、コード・実行システムは一切
実装していない。実装着手にはHuman Gateの明示指示(博士本人による
Finalization)を要する。

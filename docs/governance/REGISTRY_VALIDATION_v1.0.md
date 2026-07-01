# REGISTRY_VALIDATION_v1.0

KN-007: Registry Validation(検証機構の仕様設計)

## 1. Scope

本文書は検証の対象・タイミング・失敗時の扱いを仕様として定義する
ものであり、検証ロジックの実コード化は本書の対象外である。実装は
別途起票する実装フェーズTODOの範囲とする。

対象:
- 何を検証するか(Structure/Semantic/State の3種)
- いつ検証するか(呼び出しタイミング)
- 検証失敗時の扱い(Error/Warning/Info)
- Validatorが実効していることの制度要求(実装方法は規定しない)

対象外:
- 検証ロジックの実コード化
- Category/Series間のTopology(Atlas Seriesの範囲)

## 2. Validation Principles

- 検証は「仕様が正しく定義されているか」を確認するものであり、
  仕様そのもの(KN-004/005/006)を変更する権限を持たない。
- 検証結果は機械的に決定できるものと、人間判断を要するものを
  明確に分ける(Failure Handling参照)。
- 検証は「存在するだけ」では不十分であり、実効性の継続的な
  確認要求を伴わなければならない(Verification Assurance参照)。

## 3. Validation Targets

| 種別 | 対応 | 検証内容 |
|---|---|---|
| Structure Validation | KN-004 | 必須項目・型・enum・Schema整合性 |
| Semantic Validation | KN-005 | Category意味・境界違反・用語整合性 |
| State Validation | KN-006 | 状態遷移の許可/禁止・status_changed_at更新 |

## 4. Validator Specification

Registry Recordの作成・更新・状態遷移要求を受け付ける処理経路上に、
軽量な検証層として配置することを推奨する。具体的な実装位置・関数
構成は実装フェーズで決定する。

- 呼び出しタイミング：Registry Recordの作成・更新・状態遷移要求時
- 本章は配置方針の設計のみであり、特定の関数・モジュール・既存
  実装への直接依存は記述しない

## 5. Failure Handling

| 判定 | 動作 | 判断主体 |
|---|---|---|
| Error | Reject(書き込み拒否) | 機械的(Validator自身) |
| Warning | Human Review(保留・人間確認待ち) | 人間(Human Approval Gate) |
| Info | Continue(記録のみ、処理継続) | 機械的(Validator自身) |

## 6. Verification Assurance

本章は制度要求を定義する。実装方法は規定しない。

本仕様に基づくValidatorは、実装後に定期的な検証(例：Canary Test等)
によって、本仕様が実効していることを継続的に確認できる設計であること
を推奨する。

制度要求(存在要件のみ、実装方法は規定しない):
- Canary：代表的な違反パターンが実際にRejectされることの定期確認
- Self Test：Validator自身の起動時整合性チェックの存在
- Regression：既存の正常パターンが誤ってRejectされないことの確認
- Audit：Validation結果の記録がevent_gate等で追跡可能であること

GL7-UNENFORCED-CONDITIONS-BUG(掲げている安全条件が実行経路に未接続
だった事例)の再発防止として、上記4要件のうち最低1つ以上の存在を
実装フェーズの完了条件に含めることを推奨する。

## 7. Boundary

### 7.1 Schema Boundary
本文書はKN-004で定義されたSchema自体を変更しない。Structure
Validationはあくまでその検証を行うのみである。

### 7.2 State Boundary
本文書はKN-006で定義された遷移ルール自体を変更しない。State
Validationはあくまでその検証を行うのみである。

### 7.3 Execution Boundary
本文書は検証仕様の定義に留まり、実際の検証コード・Validator
実装は本書の対象外とする。

## 8. Extension Policy

- 新規Validation Targetの追加は、KN-004/005/006いずれかに新規
  カテゴリの仕様が追加された場合にのみ検討する。
- 将来、Atlas Series等で新たな仕様カテゴリが定義された場合は、
  本章にValidation Targetを追加できる。
- Failure Handlingの判定基準変更は本文書の改訂として扱う。

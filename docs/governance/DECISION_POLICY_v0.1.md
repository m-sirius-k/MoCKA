# Decision Policy v0.1

位置づけ: TODO_399(Decision Policy実体設計) / TODO_400(conflict_resolution_order設計) / TODO_401(OVERRIDES enforcement設計) の三部作で確定した裁定アルゴリズムの運用ポリシー文書。ACTIVATION_POLICY_v0.1.md と同形式で管理する（外部ファイルとして参照可能・監査可能・差分追跡可能）。

本ファイルはコードではなく運用ポリシーである。固定仕様（Architecture Contract/LOCKED）ではなく、運用実績に基づき随時見直す前提とする。

## 0. Decision Policyの制度的位置づけ

Decision Policyは、MoCKA制度において以下の階層構造の下で動作する唯一の裁定アルゴリズムである。

```
Human（最終主権者）
  |
Approval Gate（Human Gateによる人間承認ゲート）
  |
Decision Policy（唯一の裁定アルゴリズム。制度上の主権者ではない）
  |
Execution（実行層）
```

Decision PolicyはKnowledge Assets間の競合を機械的に裁定するが、その権力の源泉はHuman Approval Gateの委任にある。Decision Policy自身が主権者となることはなく、Human Gateで解決できない競合はescalate_if_needed()を通じて人間判断へ差し戻す。この権力分離は変更不可の設計原則である（TODO_399「唯一の裁定者」確立の根拠）。

### 責務境界（不変の制約）

Decision Policyは以下の制約を持つ。この境界はいかなる設計改訂でも変更しない。

- 「判定する」のみを行う: Knowledge Assets間の競合を裁定する。それ以外の行為を行わない。
- 「実行しない」: 裁定結果の実行はExecution層の責務であり、Decision Policyは実行に関与しない。
- 「保存しない」: Decision Evidenceの記録はaudit_triggerの責務であり、Decision Policy自身はデータを保存しない。
- 「Approvalを持たない」: 承認権（Approval）はHuman Approval Gateにある。Decision PolicyはそのApprovalを委任されて動く下位アルゴリズムであり、自身がApprovalを行使する権限を持たない。

## 1. 構造: 5段の決定オートマトン

Decision Policy v0.3確定構造（TODO_399 note準拠）:

```json
{
  "decision_automaton": {
    "stage_1": {
      "name": "detect_conflicts",
      "sub": [
        {
          "name": "detect_explicit_conflicts",
          "description": "knowledge_relationships上のCONFLICTS_WITH（制度的に確定済みの矛盾）を検出"
        },
        {
          "name": "detect_implicit_conflicts",
          "description": "同一domain x category内の重複（未確定の暗黙的競合）を検出。confidence差が一定マージン（初期値0.3）以上開いている場合は競合とみなさない閾値を適用（TODO_400）",
          "implicit_conflict_confidence_margin": 0.3
        }
      ]
    },
    "stage_2": {
      "name": "rank_candidates",
      "description": "評価ベクトル方式による候補ランキング（合成スコア化しない）",
      "evaluation_vector": "(decision_effect_rank, -confidence, authority_rank, -created_at)",
      "comparison": "辞書式順序（lexicographic order）による比較",
      "note": "confidence算出方法・算出主体は依然未定義（TODO_402へ継続）"
    },
    "stage_3": {
      "name": "apply_policy",
      "sub": [
        {
          "name": "evaluate_override",
          "description": "override_requested（優先してほしいという要求フラグ）の評価のみ。採否の決定権はDecision Policy側にあり、要求者に絶対権限はない（absolute_priority廃止・TODO_399最重要設計判断）"
        },
        {
          "name": "resolve_competition",
          "description": "override非該当時の通常競合解決のみ"
        },
        {
          "name": "finalize_selection",
          "description": "純粋な最終確定処理のみ"
        }
      ],
      "override_resolution": {
        "count_0": "none（選択肢なし）",
        "count_1": "単独採用",
        "count_N": "confidence上位者を採用（authority_orderで同値判定）",
        "tie": "全員却下しescalate_if_needed()へ委ねる（機械的に説明できない勝者を作らない設計）"
      }
    },
    "stage_4": {
      "name": "escalate_if_needed",
      "description": "Human Gateへの薄いラッパー。機械的に解決できないケースを人間判断へ差し戻す。既存human_gate.pyのsubmit()を再利用し、gate_type=decision_policyで区別（新規Gateは新設しない・TODO_401）"
    }
  }
}
```

## 2. OVERRIDES（override_requested）の定義

override_requestedとは、Knowledge Assetが「Decision Policyに優先採用を要求する」フラグである。

- 旧称: absolute_priority（絶対優先権）
- 改名理由: 採否の最終決定権は常にDecision Policy側（evaluate_override）にあることをフィールド名に埋め込むため（TODO_399最重要設計判断）
- 意味: 「絶対優先権（権利）」ではなく「優先してほしいという要求」である。Decision Policyが評価した結果に付随する監査可能な要求フラグとして扱う（TODO_401 v0.1確定）
- 強制保証: 下記「3. OVERRIDES enforcement」参照

## 3. OVERRIDES enforcement（強制制御・ゲート設計）

OVERRIDESが「掲げているが実効していない」状態（GL7-UNENFORCED-CONDITIONS-BUG参照）を防ぐための3層強制保証構造（TODO_401 v0.1確定）:

```json
{
  "enforcement_layers": {
    "layer_1_evaluation": {
      "component": "Decision Policy（evaluate_override）",
      "role": "override_requestedの評価・採否決定"
    },
    "layer_2_constraint": {
      "component": "event_gate",
      "role": "Decision Evidenceの存在を確認し、存在しない裁定結果をリジェクトする制約層。Evidenceの内容検査は行わない（存在確認のみ）。",
      "trigger": "trg_detect_override_evidence_gap（DBトリガー、audit_trigger.pyパターン踏襲）"
    },
    "layer_3_audit": {
      "component": "audit_trigger",
      "role": "裁定履歴の監査可能性を保証する記録層"
    }
  },
  "canary_test": {
    "name": "test_override_evidence_gap_is_rejected_by_event_gate",
    "execution": "CI定期実行（A案採用・常駐監視プロセス不採用）",
    "rationale": "TODO_399のPHI-OS内統合判断・TODO_396のhuman_gate再利用判断と一貫性を保つ。常駐プロセス追加はTODO_364で確認した経路増殖リスクに反する",
    "liveness_guarantee": {
      "description": "カナリアテストの最終実行日時をmocka_write_eventへ記録する。最終実行日時が7日更新されない場合にhealth_check.py等の既存仕組みで検知する（カナリアテストのカナリア）",
      "status": "v0.2設計として明記済み・未実装（TODO_401 v0.2課題）"
    }
  }
}
```

## 4. Decision Evidence の制度用語定義

Decision Evidenceとは、Decision Policyが行った裁定について、後続層（Execution・Audit）が制度的正当性を検証できる最小証跡である。

Decision Evidenceの3主体:
- 生成主体: Decision Policy（裁定を行った主体が証跡を生成する責務を持つ）
- 読者: event_gate（存在確認）/ Execution（実行判断の根拠として参照）/ Audit（事後検証）
- 検証主体: Execution・Audit（後続層が制度的正当性を検証する）

event_gateはDecision Evidenceの「存在を確認する」のみであり、Evidence内容の検査は行わない。存在しない裁定結果をリジェクトする（layer_2_constraint）。これによりDecision EvidenceのないOVERRIDES採用が制度的に不可能な構造を保証する。

## 5. conflict_resolution_orderのルール記述形式

ルール記述: DECISION_POLICY_v0.1.md内JSON埋め込み（本ファイル）
バージョニング: X.Y形式（X=構造変更、Y=パラメータ調整）
domain x categoryをまたぐ横断的競合: 自動検出せず、knowledge_relationshipsへの明示的記録（人間判断）に依存する制約を維持

## 6. 意図的に先送りした事項（次フェーズの設計対象）

以下はDecision Policy v0.1の設計範囲外として明示的に先送りされた事項（TODO_399 note準拠）:

- confidence算出方法・算出主体の確定 -> TODO_402
- rank_candidatesの評価層化（単一ソートから特徴量評価層への進化）
- escalation条件の3分類（structural/policy/ambiguity failureの区別）
- policyの「解釈可能なルール空間」への進化
- detect_implicit_conflictsの論理的競合への拡張
- カナリアテストのCI実行担保の仕組みの実装 -> TODO_401 v0.2

## 7. 改訂履歴

- v0.1（2026-07-01）: TODO_399/400/401三部作の確定設計に基づき新規作成。TODO_403監査（補充判定A）完了に伴い、以下を反映（TODO_404）:
  - セクション0: 階層表現修正（Human/Approval Gate/Decision Policy/Executionの4層構造を明示。Decision Policyが制度的主権者ではないことを明記）
  - セクション4: Decision Evidence制度用語定義を追記

# Phase10-3 Contract Readiness Report v1

Status: READINESS JUDGEMENT ONLY（契約を書ける状態かの判定のみ。
phase10_3_reasoning_node_contract_v1.md作成禁止）
Date: 2026-06-23

本文書はPHASE10_3_REASONING_AUTHORITY_MATRIX_v1.md、
PHASE10_3_CANDIDATE_LIFECYCLE_AUDIT_v1.md、
PHASE10_3_COLLISION_GOVERNANCE_STUDY_v1.md、
PHASE10_3_HUMAN_GATE_DEPENDENCY_AUDIT_v1.md、および前回の
PHASE10_3_REASONING_PREPARATION_NOTE_v1.mdの結果を統合し、
Phase10-3契約（Reasoning Node Contract）を現時点で書ける状態か
否かを判定する。判定区分はREADY/PARTIAL READY/NOT READYの
3区分とする。本文書は契約本体の作成を行わない。

## 判定区分ごとの根拠整理

```
確定済み事項（契約に書ける状態にある論点）:

    1. 採択権の不在
        Phase10-0第4章の全称表現により、Reasoning Nodeが
        採択権を持たないことは既存契約の論理的帰結として既に
        確定している（PHASE10_3_HUMAN_GATE_DEPENDENCY_AUDIT_v1.md
        確認事項1）。

    2. 実行権の不在
        同様にExecution Orchestratorのみが実行権を持つことは
        既に確定している（同確認事項2）。

    3. collision解消禁止の高い確度での継承可能性
        Observer/Advisor双方でresolve_collisionが「不可」で
        一貫しており、Phase7-B5「衝突は解消しない」原則の
        継承パターンから類推可能（PHASE10_3_REASONING_AUTHORITY_
        MATRIX_v1.md観察1、PHASE10_3_COLLISION_GOVERNANCE_
        STUDY_v1.md確認事項3）。ただし「類推可能」と「契約として
        確定」は異なるため、契約文には書けるが根拠として
        「既存原則の継承」である旨を明記する必要がある。
```

```
未確定のまま残る事項（契約に書けない論点）:

    1. Reasoning Definition自体
        Reasoningが「候補を生成する行為」なのか「候補生成の
        前提となる意味的判断」なのかが未確定
        （PHASE10_3_REASONING_PREPARATION_NOTE_v1.md論点A-1）。
        これが確定しない限り、契約第1章（Node Definition）が
        書けない。

    2. Candidate Authority（B-1〜B-4）
        generate_candidate/derive_candidate/expand_candidate/
        reconstruct_candidateのいずれを許可するか、複数許可する
        場合の相互関係（B-2とB-4の境界が不明瞭、と前回ノートで
        既に指摘済み）が未確定。これが確定しない限り、契約第2章
        （Permissions）の核心部分が書けない。

    3. Projection層との帰属関係
        Reasoning NodeがPhase9 Projection層の一部なのか外側の
        Nodeなのか（PHASE10_3_REASONING_PREPARATION_NOTE_v1.md
        論点D全体、PHASE10_3_CANDIDATE_LIFECYCLE_AUDIT_v1.md
        論点D-1）が未確定。これが確定しない限り、Ranking変更権・
        Projection変更権の扱い（PHASE10_3_HUMAN_GATE_DEPENDENCY_
        AUDIT_v1.md確認事項3・4で「未確定」と判定済み）も確定
        できない。

    4. collision増幅に関する制度的空白
        既存契約のいずれにもcollision「増幅」を禁止する規定が
        存在しないことが確認された（PHASE10_3_COLLISION_
        GOVERNANCE_STUDY_v1.md確認事項2）。これを契約に明記
        するかどうかの判断自体が未確定。

    5. Advisor Nodeとの機能的差分
        Reasoning Nodeの比較・説明機能がAdvisor Nodeの同名機能と
        どう区別されるか（PHASE10_3_CANDIDATE_LIFECYCLE_AUDIT_v1.md
        論点D-2）が未整理。これが未確定のままだと、契約第5章
        相当（既存のObserver/Advisor Boundaryパターンに倣う
        Reasoning境界の記述）が書けない。
```

## 判定

```
区分: PARTIAL READY
```

```
根拠:
    Human Gate依存関係（採択権・実行権の不在）という、契約上
    最も重要な「三分離原則の継承」については既存契約の論理的
    帰結として既に確定しており、これは契約第4章（Governance）
    相当部分の記述に十分な根拠がある。

    一方、Node Definition（第1章相当）・Permissions（第2章相当、
    特にcandidate生成系4操作）・Projection層との帰属関係
    （Ranking/Projection変更権の扱いに直結）という、契約の
    核心となる3つの論点が未確定のまま残っている。これらは
    「既存契約からの帰結」では確定できず、新たな制度設計判断
    （ユーザー裁定）を要する。

    したがって、Phase10-3契約は「全く書けない（NOT READY）」
    状態ではないが、「そのまま書ける（READY）」状態でもない。
    Governance部分の一部は既存契約の引用で構成可能だが、
    Definition・Permissions・Projection帰属の3論点に関する
    裁定が無い限り、契約全体としては未完成にしかならない。
```

## 次に必要な裁定事項（契約作成のための前提、本文書では裁定しない）

```
裁定事項1: Reasoning Definitionの確定
    （候補生成行為か、候補生成の前提となる意味的判断か）

裁定事項2: Candidate Authority範囲の確定
    （generate/derive/expand/reconstructのいずれを許可するか、
    複数許可する場合の相互関係）

裁定事項3: Projection層との帰属関係の確定
    （Reasoning NodeはProjection層の一部か、外側のNodeか）

裁定事項4: collision増幅に関する制度的空白の扱い
    （明示的に許可/禁止/未規定のままとするかの判断）

裁定事項5: Advisor Nodeとの機能的差分の確定
    （比較・説明機能の重複をどう整理するか）
```

## 結論

```
Phase10-3 Reasoning Node Contract Readiness: PARTIAL READY

本文書はphase10_3_reasoning_node_contract_v1.mdを作成していない。
上記5裁定事項についての次回明示裁定を待つ。
```

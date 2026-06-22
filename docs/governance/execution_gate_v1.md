# MoCKA Phase5 実装移行前 最終安全チェックリスト（Execution Gate v1）

Status: PROPOSED（working_memory.json破損インシデントの事後対応。即時コード変更を伴わない）
Date: 2026-06-23
関連文書: `docs/governance/state_dependency_risk_map_v1.md`、
`docs/incidents/INCIDENT_IMPORT_APP_SIDE_EFFECT.md`

## 1. 前提: このチェックの意味

これは単なる動作確認ではない。「app.pyへの変更が、再び全write系停止
事故を引き起こさないことを制度的に保証するためのゲート」である。
目的は技術検証ではなく、構造的安全性の証明である。

## 2. 必須条件（MUST PASS）

### 2.1 State Layer健全性

チェック項目: `working_memory.json`が単一JSONを維持していること、
`MOCKA_TODO.json`に破損が無いこと、event storeがappend-onlyを
維持していること。

判定基準: `json.load`が全て成功すること。`Extra data`系エラーが
0件であること。

### 2.2 Write Path安全性

チェック項目: 全write関数がatomic writeに統一されていること、
`open("w")`単体書き込みの残存が無いこと、`os.replace`使用が
統一されていること。

判定基準: race conditionが再現不能であること。同時2write発生でも
破損しないこと。

### 2.3 Gate Layer安定性（最重要）

チェック項目: `before_tool()`がstate破損で停止しない設計になって
いること、groundingがcache fallback可能であること、`json.load`依存
が単一点でないこと。

判定基準: state破損時でもwrite systemが完全停止しないこと。
fail closedが「部分制御」に落ちること。

### 2.4 依存関係分離

チェック項目: `app.py`がPhase5 modulesに直接依存しないこと、
Phase5 modulesが`app.py`の状態に依存しないこと、import side effect
が無いこと。

判定基準: circular dependencyがゼロであること。import時副作用が
ゼロであること。

## 3. 推奨条件（SHOULD PASS）

### 3.1 State Cache設計

`working_memory`は「キャッシュ」であり「真実」ではない。event store
がsource of truthである。

### 3.2 Write分離構造

理想構造:

```
WRITE -> event store（永続）
      -> working_memory（派生キャッシュ）
```

### 3.3 Fail Mode設計

| 状態 | 現在 | 推奨 |
|---|---|---|
| state破損 | 全停止 | degraded mode |
| grounding失敗 | write停止 | cache fallback |

## 4. 禁止条件（FAIL = 即停止）

以下が1つでもあればapp.py移行は禁止とする。

- `json.load`が直接ゲート判断に使用されている
- write pathに非atomic処理が残っている
- state file破損が全停止に直結する構造
- import時に副作用（write/read）が発生する

## 5. 現在の評価（2026-06-23時点）

### PASS済み

- `working_memory`のatomic化
- `mocka_write_event`の復旧確認
- gate再起動確認
- インシデント分離完了（Import Side Effect Incident本体とState Cache
  Corruption Incidentが相互干渉していないことを確認済み）

### 部分PASS

- TODO / event store の棚卸し未完
  （`docs/governance/state_dependency_risk_map_v1.md`「5. 必須1」参照）
- grounding cacheの改善余地あり

### FAIL（ただし非ブロッカー）

- gate fail closedの粒度が粗い（state依存で全面停止する構造自体は
  まだ残っている）

## 6. 最終判定（移行可否）

結論: app.py移行は「条件付きで許可」。

条件: 「state破損＝全停止」構造を理解した上で進むこと。本構造の
恒久的解消（degraded mode化）は本チェックリストの対象外であり、
`docs/governance/minimal_safe_architecture_v1.md`に設計案として
別途記録する。

## 7. システム健全性評価

```
[System Health]
Core Execution Layer     OK
State Layer              FIXED
Write Layer              FIXED
Gate Layer               STABLE（ただし設計余地あり）

[Risk Level]
LOW -> MEDIUM（設計改善領域のみ残存）
```

## 8. 実務的な判断

現在の状態は「壊れているシステム」ではなく「弱い設計が可視化された
システム」である。

## 関連文書

- `docs/governance/state_dependency_risk_map_v1.md`
- `docs/governance/minimal_safe_architecture_v1.md`
- `docs/governance/runtime_boundary_v1.md`
- `docs/governance/import_safety_rule_v1.md`
- `docs/incidents/INCIDENT_IMPORT_APP_SIDE_EFFECT.md`
- `docs/incidents/CHANGE_PLAN_IMPORT_APP_SIDE_EFFECT_v1.md`

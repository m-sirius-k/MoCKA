# MoCKA Phase5 実装用 最小安全アーキテクチャ（Minimal Safe Architecture v1）

Status: PROPOSED（設計提案。即時コード変更を伴わない）
Date: 2026-06-23
関連文書: `docs/governance/execution_gate_v1.md`、
`docs/governance/state_dependency_risk_map_v1.md`

目的は機能追加ではなく、再び同種の停止事故（State Cache Corruption）
を起こさない構造の固定である。

## 1. 設計原則（最上位制約）

前提は1つに集約される: 「状態破損は避けられない前提でシステムを
止めない構造にする」。

設計思想の転換:

- ❌ 状態を守る設計
- ⭕ 状態が壊れても動く設計

## 2. 全体構造（3層分離固定）

```
[APP LAYER]
  app.py（純粋制御）
        |
[GATE LAYER]
  before_tool()
  grounding (cache + fallback)
        |
[STATE LAYER]
  event_store（source of truth）
  working_memory（cache）
  todo.json（projection）
```

## 3. 必須構造変更（最小セット）

### 3.1 Stateの役割再定義

現在: `working_memory` = 参照元 + 判断材料。

改善後: `working_memory` = キャッシュ（壊れてもよい）。真実の位置は
`event_store`のみとする。

### 3.2 Gateの依存を2段階化

```
before_tool()
   |
(1) fast path: cache read
   | fail?
(2) fallback path: event_store derive
```

### 3.3 Fail Closed -> Fail Degraded

現在: state load error = 全write停止。

変更後:

| 状態 | 動作 |
|---|---|
| cache OK | normal |
| cache broken | fallback mode |
| event store OK | write継続 |
| total failure | controlled stop |

### 3.4 Write Pathの単一化

全writeは以下の経路に統一する。

```
write_event()
   |
append-only event_store
   |
async projection update
   |
working_memory更新（非必須）
```

## 4. app.pyの最小責務

`app.py`は以下以外を行わない。

❌ やってはいけない:

- state read
- `json.load`直接使用
- `working_memory`参照
- gating判断

⭕ やるべきこと:

- tool routing
- request dispatch
- result return

## 5. grounding設計（重要修正）

現在の問題: groundingがstate fileに直接依存している。

修正後:

```
grounding engine
   |
cache (working_memory)
   | fallback
event_store projection
```

## 6. 破壊防止構造（最重要）

今回の事故を防ぐ核心は「壊れる前提の階層化」である。

| 層 | 役割 | 壊れても |
|---|---|---|
| cache | 高速参照 | OK |
| projection | 再構築可能状態 | OK |
| event store | 真実 | 必須（壊れてはならない） |

## 7. 最小安全チェック（実装前条件）

app.pyに進む前に以下を満たすこと（`execution_gate_v1.md`の必須条件と
対応する）。

- event_store単独で状態再構築可能であること
- working_memory破損でwrite停止しないこと
- gateがcache依存のみで停止しないこと

本v1時点では上記3点は未達であり、設計提案の段階に留まる
（`docs/governance/execution_gate_v1.md`「6. 最終判定」の条件付き許可
を参照）。

## 8. 禁止構造（再発源）

以下がある場合は設計失敗とする。

- `json.load`がgate判断に直結している
- cache破損＝write停止になっている
- state readとwriteが同一パスを共有している
- import時副作用でstate参照が発生する

## 9. 最終システム評価（理想状態）

```
[Resilience]
Cache failure       -> OK
State corruption    -> OK
Partial write race  -> OK
Gate failure        -> degraded mode

[System behavior]
Always writable (unless total failure)
Never full freeze due to JSON corruption
```

## 10. 結論

この設計に到達すると、MoCKAは「状態依存システム」から「イベント駆動
耐障害システム」へ移行する。

本v1は設計提案であり、実装(`before_tool()`の2段階化、Fail Degraded化、
write path単一化等)はCore System File Change Approvalと同様の審査
プロセスを経て別途着手する。本文書の記録時点ではコード変更は一切
行っていない。

最終目標は「app.pyを進めること」ではなく「壊れても止まらない書き込み
構造にすること」である。

## 関連文書

- `docs/governance/execution_gate_v1.md`
- `docs/governance/state_dependency_risk_map_v1.md`
- `docs/governance/runtime_boundary_v1.md`
- `docs/governance/import_safety_rule_v1.md`

# Phase8: HAB Runtime Integration Layer Contract v1

Status: DRAFT (Phase8-1。契約設計のみ。コードゼロ）
Date: 2026-06-23

本文書はPhase7が確立したA（Meaning Generation）〜E（Human Gate
Interface）構造を、外部接続可能な単一の「動作するOS」として統合する
契約を固定する。Phase7の全契約（13本）が定義したクラス・メソッド
署名はいずれも変更しない。本契約はそれらを呼び出す統合ルーティング
のみを定義する。

## 0. 位置づけの転換

```
Phase7まで: 「意味を保持するOS」
Phase8:     「意味が実際に動くOS」
```

Phase7のA〜Eは個別に完成しているが、外部（Drift Monitorの実運用・
外部イベント・人間の観測）に対しては未接続のままである。Phase8は
分岐（UI専用化/接続専用化/理論専用化）ではなく、3層への統合として
これを実現する。

## 1. 3層構造（確定）

```
Runtime Bridge Layer       - 現実と接続する唯一の入口
        |
Execution Orchestrator     - HABを1つの動く単位にする
        |
Observation Surface        - 人間が触れる唯一の面
```

### 1.1 Runtime Bridge Layer（接続層）

- 既存`DriftMonitor`（Phase7-C）への接続点を定義する。Drift Monitor
  自体のメソッド・絶対禁止（自動修復禁止等）は変更しない。
- 外部イベント受信口・trace/collision流入口を定義する。本契約では
  「入口の形」のみを固定し、具体的な外部接続（HTTP/MCP/ファイル
  watch等の実装手段）はPhase8-2以降に委ねる。
- Runtime Bridgeは現実データを**取り込むだけ**であり、取り込んだ
  データの意味解釈・cluster再計算は行わない（Phase7-A4契約群の
  絶対禁止を継承）。

### 1.2 Execution Orchestrator（実行統合層）

- 既存`MeaningCycleExecutor`（Phase7-D-2）・`CollisionGovernor`
  （Phase7-B-5）・`HumanGateEventLog`（Phase7-B-7）を、固定順序で
  ルーティングするだけの統合層。
- ルーティング順序（確定）:
  ```
  1. MeaningCycleExecutor.run_cycle(...)        -> A/B/C/Dの1サイクル
  2. サイクル結果からcollisionが検出された場合
     -> CollisionGovernor.govern(...)            -> B-5: 分類+エスカレーション
  3. GovernedCollisionRecordが生成された場合
     -> HumanGateEventLog経由でRulingEventとして記録可能な状態にする
        （裁定の実行自体は人間が行う。Orchestratorが裁定を代行することはない）
  ```
- Orchestratorは「ルーティングするだけ」であり、新たな意味判断・
  衝突解消・裁定の代行は一切行わない（Phase7-B-5/B-6の絶対禁止を継承）。

### 1.3 Observation Surface（可視層）

- 既存`CollisionView`/`build_collision_view`（Phase7-B-7）を、
  人間が触れる唯一の観測面として位置づける。
- 状態観測ダッシュボード・Human Gate UIの実装はPhase8-3以降に委ねる。
  本契約では「観測面が読み取るべきデータ形」のみを固定する
  （`CollisionView`そのまま、新規フィールド追加は本契約では行わない）。

## 2. 絶対維持条件（Phase7からの継承・再確認）

```
merge禁止                  継続（Phase7-B-6で恒久的除外）
collision削除禁止          継続（Phase7-B-5/B-6でappend-only確定）
非破壊構造維持              継続（元データ・GovernedCollisionRecord変更禁止）
Human Gateは唯一の裁定点    継続（Orchestratorが裁定を代行しない）
```

これらはPhase8のいかなる実装によっても解除されない。

## 3. 段階フロー

1. **Phase8-1（本文書）**: 契約設計のみ。コードゼロ。
2. Phase8-2（未着手・要承認）: Runtime Bridge Layerの最小スケルトン
   （外部イベント受信口の抽象インターフェースのみ、具体的な接続手段は含めない）。
3. Phase8-3（未着手・要承認）: Execution Orchestratorの最小スケルトン
   （既存MeaningCycleExecutor/CollisionGovernor/HumanGateEventLogの
   呼び出しのみ、Fake実装での統合動作確認）。
4. Phase8-4（未着手・要承認）: Observation Surfaceの最小スケルトン
   （CollisionViewの一覧取得API程度、UI実装そのものは対象外）。

## 4. 変更ルール

この契約に変更を加える場合は「Phase変更レベル」として扱い、ユーザーの
明示的承認を要する。Phase7の13契約のいずれも、本契約によって変更
されない。

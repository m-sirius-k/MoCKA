# State Dependency Risk Map v1

Status: PROPOSED（working_memory.json破損インシデントの事後分析。即時コード変更を伴わない）
Date: 2026-06-23
関連インシデント: `data/working_memory.json`破損（State Cache Corruption Incident, L2）

## 1. 前提: 今回の事故の構造的定義

今回の障害は単一ファイル破損ではなく、以下4条件が重なって発生した。

必須条件:

- ゲート層が「外部状態ファイル」に依存する
- その状態が`json.load`で同期的に読み込まれる
- 書き込みが atomic でない
- 同時更新 or 再入呼び出しが発生可能

結果: 「状態キャッシュ破損 → 全write系Fail Closed」

詳細は`docs/incidents/INCIDENT_IMPORT_APP_SIDE_EFFECT.md`関連イベント
（2026-06-23、`data/working_memory.json`破損・復旧）を参照。

## 2. 危険領域の分類（MoCKA全体）

MoCKA内の危険領域は3種類に分かれる。

### I. State Gate Dependency Zone（最重要）

特徴:

- `before_tool`/prehook/grounding系
- 外部JSON・DBを毎回参照
- write系の可否判断に直結

該当箇所（典型）:

- `data/working_memory.json`（今回の事故箇所、対応済み）
- `data/MOCKA_TODO.json`
- event ledger cache
- grounding index（`structural/repository_index.json`）

危険性: 最高。破損すると全write停止。

再発条件: `json.load`依存、キャッシュ再生成なし、同期I/O。

### II. Shared Write Surface Zone（競合領域）

特徴:

- 複数ルートから書き込み可能
- 実質ロックなし
- 同一ファイルを複数コンポーネントが更新

該当箇所:

- `structural/working_memory.py`（対応済み、atomic write化）
- event store
- todo writer
- relay snapshot writer

危険性: 高頻度再発領域。

典型バグ: truncate不足、appendモード混入、`os.replace`未使用、async競合。

### III. Gate Preprocessor Zone（今回の本丸）

特徴:

- `before_tool()`
- `_refresh_grounding()`
- validation hook
- input normalization

危険性: 全体停止トリガ。

今回の挙動:

```
working_memory破損
  -> grounding失敗
  -> before_tool fail closed
  -> 全write系停止
```

本質: 「外部状態を毎回ゲート判断に使っている設計」。

## 3. 再発パターン分類

### パターンA: Partial Write Corruption

JSON途中で中断、競合上書き、truncate漏れ。

対象: working_memory / todo / event

### パターンB: Dual Writer Collision

2つ以上のコンポーネントが同一ファイルを更新、lockなし、非atomic write。

対象: Relay + Memory + Engine同時更新

### パターンC: Gate Dependency Collapse

`before_tool`が状態依存、依存先が壊れると全停止。

対象: 今回の現象そのもの

## 4. MoCKA構造上の設計的地雷

特に危険な構造:

```
write_event
  |
working_memory update
  |
before_tool grounding read
  |
write permission decision
```

これは設計的に「書くために読むが、その読む対象が壊れると書けなくなる」
という循環依存構造になっている。

## 5. 再発防止に必要な最小構造変更

### 必須1: Atomic Write統一

すべてのstate fileに適用: temp file write + fsync + `os.replace`。

`structural/working_memory.py`の`_save()`は2026-06-23時点で対応済み
（`docs/incidents/INCIDENT_IMPORT_APP_SIDE_EFFECT.md`関連イベント参照）。

未対応（将来TODO化候補）:

- `data/MOCKA_TODO.json`の書込み経路
- event ledger / `events.db`周辺のキャッシュファイル
- `structural/repository_index.json`の書込み経路（存在する場合）

### 必須2: Gateの状態依存削減

`before_tool`から以下を排除する方向性を検討する。

- JSON直接load
- runtime state file依存

代わりに: snapshot cache、memory mirror（メモリ内保持）。

### 必須3: Write PathとRead Gateの分離

現状: 同じ`working_memory`をreadとwriteが共有。

修正案: WRITE = event-driven log、READ = derived snapshot（別系統）。

### 必須4: Fail Closed条件の再定義

現状: state load failure = 全停止。

改善案: state load failure = degraded mode（writeは継続可能、gateは
キャッシュフォールバック）。これはGL7のFail Closed原則自体を変える話
であり、Import Safety Ruleと同様に人間ゲート審査の対象とすべき。

## 6. 構造的結論

MoCKAは「状態を真実として使うゲート設計」になっているため、状態破損
がそのままシステム停止になる。これはバグでも実装ミスでもなく、構造
依存の単一点障害（SPOF）である。

## 7. 評価

- 情報系: 正常
- 実行系: 正常
- 状態依存ゲート: 危険（SPOF）

リスクレベル: L2 → L3境界（再発するとシステム停止級）。

## 8. 次の一手（優先順位）

1. `working_memory`のatomic化（完了、2026-06-23）
2. gate dependencyのcache化（中、未着手）
3. read/write完全分離設計（長期、未着手）

## 関連文書

- `docs/incidents/INCIDENT_IMPORT_APP_SIDE_EFFECT.md`
- `docs/governance/runtime_boundary_v1.md`
- `docs/governance/import_safety_rule_v1.md`

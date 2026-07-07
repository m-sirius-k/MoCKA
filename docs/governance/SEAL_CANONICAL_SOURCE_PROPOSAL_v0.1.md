# Seal Canonical Source 決定案 v0.1

## 位置づけ

本文書はTODO_371(正本記録の信頼性実測、AUTO_SEAL等補助機構の本流化根本原因検証)のDecision化準備として、
監査官R01(きむら博士)指示に基づき作成する提案文書である。基礎資料はIC_20260707_005。

**本文書は提案(案)であり、Decision Ledgerへの正式記録・app.py変更・ledger.json/anchor_record.json変更・
seal値修正・commit・Legacy削除のいずれも行っていない。** Human Gate承認後、別途Decision Ledgerへ記録し、
実装はさらに別のMigration Spec(ESSENCE_MIGRATION_SPEC群と同様の手順)を経てから行う。

## 背景

TODO_371は2026-06-26、きむら博士の指摘「正本ルール(events.db/mocka_write_event経由の5W1H記録)が
正しく機能していれば本来不要な補助ルール(AUTO_SEAL_50EVT等)が、実際には本流化してしまっている」を
発端とする診断TODOである。当初仮説は「正本記録への不信から生まれた独立補助機構」というパターンの検証
だった。

Living Context整合性監査(Essence Resolver導入、DC_20260707_019/020)の過程で、COMMAND CENTERの
`civilization_loop.audit.last_seal`が2026-03-26のまま停滞している事象を発見(前回報告)。当初はこれを
TODO_371の仮説通り「本流seal機構が停止し、補助機構だけが動いている」証拠と解釈したが、詳細調査
(IC_20260707_005)の結果、**仮説の一部訂正が必要**であることが判明した。

## Seal機能分類表

「sealとは何か」を、ファイル単位ではなく機能的役割で分類する。

| Seal分類 | 役割 | 対象 |
|---|---|---|
| **監査証跡seal** | commit単位で再封印される、改ざん検知・証跡保存のための一次記録 | `governance/anchor_record.json`(+ミラー) |
| **表示用seal** | COMMAND CENTER等のUIが「最終seal時刻」として提示するための参照値 | `runtime/main/ledger.json`(現状は廃止済みファイルを誤って参照) |
| **状態説明seal** | 人間向けの状態要約文書内で、seal状況を説明するための転記値 | `MOCKA_OVERVIEW.json` `governance.latest_seal` |
| **未使用候補** | コード上は参照されるが実体・実績が確認できないもの | `data/seal_log.json`(別Decision対象、後述) |

## 現状構造(IC_20260707_005より)

```
Seal概念A: governance/anchor_record.json(+ mocka-governance-kernel/anchors/のミラー)
    書込み主体: anchor_update.py(git commitのたびに再封印)
    最終更新: 2026-07-07T09:04:00Z(調査時点の約1時間前)
    git log: 「anchor: re-seal after <commit>」の健全な連続履歴(直近: 318763e83)
    → 現役・健全。監査証跡seal正本候補

Seal概念B: runtime/main/ledger.json
    最終更新: 2026-04-16(git log上も1コミットのみ、以降更新なし)
    ファイルmtime: 2026-03-27
    関連スクリプト24本(下記「変更対象候補一覧」参照)は現在いずれも稼働プロセスなし
    → 廃止済み・Legacy候補
    ↑
    COMMAND CENTER(app.py 1554-1566行目)のcivilization_loop.audit.last_sealが
    この廃止済みファイルを参照し続けている

Seal概念C: MOCKA_OVERVIEW.json governance.latest_seal
    2026-06-18時点の値(sha256形式、anchor_record.jsonの過去のsealed_summary_hashと推測される
    が一致は未確認)。専用の自動同期経路(export_for_cloudflare.py/sync_watch.pyいずれも非該当)は
    発見できず、手動スナップショットの可能性が高い

Seal概念D: data/seal_log.json(/audit/status・/audit/seal POSTルートが参照)
    ファイル自体が存在しない(2026-07-07時点で未確認)。/audit/seal(手動トリガー)が
    一度も実行されていないか、実行後の書込みが別の理由で失敗している可能性がある
```

## 訂正: TODO_371仮説の精緻化

当初仮説「AUTO_SEAL等補助機構が本流化し、正本(events.db/mocka_write_event)が機能不全」について、
Seal機構に関する限り、以下のように精緻化する。

- **本流(anchor_record.json)は健全に稼働している。** 「本流が死んでいる」わけではない。
- 問題は「COMMAND CENTER表示が、健全な本流(anchor_record.json)ではなく、廃止済みの旧ファイル
  (ledger.json)を参照し続けている表示配線の古さ」である。
- これはEssence Resolver対応(IC_20260707_001〜003、Legacy Essence Store→Canonical Essence参照
  への切替)と**同型の構造的問題**である。MoCKAで繰り返されているテーマ、「データが壊れているのでは
  なく、正本への接続境界が古い」の具体例と位置づけられる。

## Decision案: Seal Canonical Source確定

> **候補**: `governance/anchor_record.json`(+ `mocka-governance-kernel/anchors/`のミラー)を
> 監査証跡sealの正本(Canonical Seal Source)とする。

### 決定根拠

`governance/anchor_record.json`を正本候補とする根拠は、IC_20260707_005で確認した以下3点である。

1. **継続更新されている**: git commitのたびに`anchor_update.py`が再封印しており、
   調査時点で最終更新は2026-07-07T09:04:00Z(約1時間前)と現役であることを実測確認済み
2. **git履歴上の連続性がある**: `git log --oneline -- governance/anchor_record.json`が
   「anchor: re-seal after `<commit>`」という健全な連続履歴を持つ(直近: 318763e83)。
   途切れや欠番が確認されていない
3. **最新seal情報を保持している**: 他のSeal概念(B/C/D)がいずれも古い・未使用・実体不明である中、
   唯一「今何がsealされているか」を正しく反映している値を持つ

ただし、`anchor_record.json`が保持する`sealed_summary_hash`の計算元である`calc_summary_hash.py`
自体の計算ロジックの健全性は、本調査の範囲外であり未検証である。これは実装前確認項目として
「Human Gate対象箇所」に追加する(下記「実装前リスク」参照)。

### 方針(5点)

1. `governance/anchor_record.json`を唯一の監査seal基準とする
2. COMMAND CENTER表示は将来的に`anchor_record.json`参照へ変更する(実装は別Migration Specで、
   Essence Resolverと同様のSpec→Impact Analysis→Human Gate承認→実装の手順を踏む)
3. `runtime/main/ledger.json`及び関連スクリプト群は「Legacy Ledger System」として凍結する
   (Essence Migrationにおける「Legacy Essence Store」と同じ扱い。新規Writer追加禁止、既存Writer
   の新規起動も慎重に扱う)。**これは単なる不要ファイルの塩漬けではなく、(a)rollback時の比較対象
   (b)将来の比較監査(anchor_record.jsonとの整合性検証) (c)Legacy Ledger System自体の移行検証、
   という3つの積極的な保持価値を持つ資産として扱う**
4. 削除は別Decisionとする(本Decisionのスコープ外)
5. `MOCKA_OVERVIEW.json`の`governance.latest_seal`は、`anchor_record.json`からの表示同期対象として
   扱う(同期方式の具体設計は別途、OVERVIEW本文更新の半自動seal方式の設計確定と合わせて検討)

## 変更対象候補一覧(Phase C、調査のみ・変更は行っていない)

### COMMAND CENTERのledger参照箇所

| 箇所 | 内容 |
|---|---|
| app.py 1512行目 | `LEDGER_JSON = Path(r"...\runtime\main\ledger.json")` |
| app.py 1554-1566行目 | `civilization_loop.audit.last_seal`/`last_seal_hash`の算出ロジック(ledger.jsonの末尾エントリを読む) |
| app.py 2091-2100行目 | `/audit/status`ルート、`data/seal_log.json`を参照(ファイル不在) |
| app.py 2102行目以降 | `/audit/seal`(POST)ルート、`anchor_update.py`を手動起動し`data/seal_log.json`へ書込む設計(現状ファイル不在から、書込みが機能していないか一度も実行されていない可能性) |
| app.py 2064-2070行目 | AUTO-AUDIT日次seal自動実行ループ、`anchor_update.py`を起動(ledger.jsonには無関係) |

### Legacy Ledger関連スクリプト(24ファイル、いずれも現在プロセス非稼働)

```
docs/archive/simulate_branch.py       docs/archive/tamper_demo.py
make_movement_map.py                  node_heartbeat.py
node_timeout.py                       reproduce_mocka.py
runtime/rebuild_logger.py             scripts/ledger/ledger_audit.py
scripts/ledger/ledger_compress.py     scripts/ledger/ledger_consensus.py
scripts/ledger/ledger_replay.py       scripts/ledger/ledger_seal.py
scripts/ledger/ledger_segment.py      scripts/ledger/ledger_sync.py
scripts/ledger/ledger_time_travel.py  scripts/ledger/ledger_visualize.py
scripts/ledger/rebuild_state.py       scripts/seal/seal_commit.py
scripts/seal/seal_head_with_observer.py  scripts/seal/seal_scheduler.py
scripts/shadow/multi_shadow_sync.py   scripts/shadow/shadow_sync.py
scripts/shadow/shadow_verify.py       scripts/snapshot/snapshot_scheduler.py
scripts/state/state_engine.py
```

これらは旧Movement/Shadow分散合意アーキテクチャ(OVERVIEW.jsonの`structure.mocka_Movement`/
`shadow_Movement`概念)の一部だったと推測されるが、現時点では推測の域を出ない。個別の役割・
最終稼働時期の特定は本Decisionのスコープ外とし、必要であれば別途調査する。

## data/seal_log.json の扱い(別Decision対象)

`data/seal_log.json`(`/audit/status`・`/audit/seal`POSTルートが参照)は、以下の理由により
**本Decisionのスコープ外とし、別Decision対象として切り出す**。

- 実害が確認されていない(参照コードはあるが、ファイル不在によるエラーや機能不全の実例は未確認)
- 使用実績が確認されていない(`/audit/seal`が過去に実行された記録の有無は本調査の範囲外)
- 参照コードのみが存在し、実データが一度も生成されていない状態であるため、
  「復活させるべきか」「廃止すべきか」を判断する材料が現時点では不足している

## 実装前リスク(Human Gate対象箇所への追加)

以下は実装(Phase3)着手前に確認すべき項目として、Human Gate対象箇所に追加する。

- [ ] `calc_summary_hash.py`(anchor_record.jsonの`sealed_summary_hash`計算元)の計算ロジック
      自体の健全性確認(本Decisionでは未検証)
- [ ] Legacy Ledger System(24スクリプト)が、タスクスケジューラ等の不定期トリガー経由で
      起動する経路が本当に存在しないことの確認(現状は「プロセスとして現在見当たらない」ことのみ
      確認済みで、起動経路の不在そのものは未確認、IC_20260705_015と同種の限界)
- [ ] `data/seal_log.json`について、`/audit/seal`の実行履歴(過去に呼ばれたことがあるか)の確認

## Human Gate対象箇所

以下はいずれも本文書のDecision案が承認された後、別途Migration Spec→Impact Analysis→実装の
手順で扱う、Human Gate対象の変更である。

- [ ] app.py: `LEDGER_JSON`参照を`anchor_record.json`ベースに切替(Resolver方式の応用を想定)
- [ ] app.py: `/audit/status`・`/audit/seal`ルートの`data/seal_log.json`参照の扱い(別Decision対象、
      上記参照)
- [ ] Legacy Ledger System(24スクリプト)の凍結方針の正式承認(新規Writer追加禁止等)
- [ ] MOCKA_OVERVIEW.json `governance.latest_seal`の同期方式設計
- [ ] 上記「実装前リスク」3項目の確認

## 次工程(Phase境界、同時変更禁止)

| Phase | 内容 | 状態 |
|---|---|---|
| Phase 1 | Decision承認(本文書のHuman Gate承認・Decision Ledgerへの正式記録) | 次工程 |
| Phase 2 | COMMAND CENTER参照切替設計(Seal Migration Spec作成、ESSENCE_MIGRATION_SPEC群と同様の手順) | Phase 1完了後 |
| Phase 3 | 実装(CHANGE_START→変更→UTF-8検証→CHANGE_DONE) | Phase 2のHuman Gate承認後 |
| Phase 4 | Runtime Validation・Legacy凍結確認 | Phase 3完了後 |

**Phase間の同時進行・並行着手は禁止する。** 各Phaseは前段のHuman Gate承認を得てから着手し、
複数Phaseを跨いだ変更を一度のcommitやセッションでまとめて行わない。

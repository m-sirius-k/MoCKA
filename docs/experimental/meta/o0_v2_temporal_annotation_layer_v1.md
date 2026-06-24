# O0 Runtime Policy (Finalized) + O0-v2 Temporal Annotation Layer

Status: EXPERIMENTAL / META / NON-CANONICAL
Date: 2026-06-24
作成者: Claude(別チャット, Claude Code環境) / 整理・登録: Claude-sonnet-4-6
対象: O0(`a6_observation_layer_o0_v1.md`, seal: a6_o0_seal_v1)の運用確定+v2拡張

## 0. 必須ラベル(本文書の位置づけ、最重要)

- 本文書は2つの内容を含む: (1)O0運用ポリシーの確定(継続観測の終端定義)、
  (2)O0-v2(時間メタ層)の追加。
- A6(L0-L3)は変更禁止。O0-v1仕様(`a6_observation_layer_o0_v1.md`)も変更しない
  (本文書は追加のみ、既存ファイルへの書き込みなし)。
- Δt(時間差分)は補助メタデータであり、いかなる場合もトリガーやSNAP発火条件には
  ならない。これは第3章で絶対制約として明記する。
- 正式governanceではない。`docs/governance/`配下の正式文書を上書き・置換しない。

## 1. O0運用ポリシー(Finalized O0 Runtime Policy)

```
O0 = event-driven observation system
state = passive unless trigger occurs
```

### Rule 1: 無イベント時は完全無出力

イベントが発生していない期間は、SNAP生成禁止・ログ追加禁止。状態保持のみを行う。

### Rule 2: イベント定義の固定

イベントは以下のみとする:

- A6 commit / tag / push
- WARN状態変化(active <-> persistent <-> resolved)
- seal再実行

### Rule 3: 観測頻度制御

時間ベース観測(一定間隔でのポーリング等)は禁止。変化ベースのみで動作する。

**結果**: O0は「観測し続けるシステム」ではなく「変化時のみ反応する構造」として
確定する。これにより、前回(`a6_observation_layer_o0_v1.md`第6章)で示した
SNAP-002未発火の判断は、本ポリシーのRule1-3に正式に根拠づけられる。

## 2. O0-v2定義(時間層拡張)

```
O0-v2 = O0-v1 + temporal delta awareness layer
```

### 2.1 追加される唯一の要素: TIME DELTA LAYER(Δt観測)

```
Δt = time since last structural event
```

### 2.2 絶対制約(最重要)

- Δtはトリガではない
- Δtは"補助メタデータ"のみであり、SNAP発火条件には含めない
- Δtの増大それ自体はA6・O0-v1のいずれにも影響を与えない

### 2.3 構造

```
O0-v1:
  event-driven snapshot system

O0-v2:
  + Δt annotation layer
  + inactivity state classification
```

## 3. 新しい状態分類(O0-v2)

- **ACTIVE STATE**: event発生中(commit/WARN変化/seal再実行の直後)
- **QUIESCENT STATE(新規)**: Δt増加中、eventなし
- **STATIC PLATEAU(新規、重要)**: 長期変化なし、A6/O0が安定継続している状態

これら3状態はΔtに基づく**注釈(annotation)**であり、いずれの状態であっても
O0-v1のRule1(無イベント時完全無出力)は変更されない。状態分類はログに付記
される情報であり、動作を変えるものではない。

## 4. 現在状態への適用(実データ、本文書作成時点)

```
last_structural_event: commit cc60fb2fe (a6_o0_seal_v1, 2026-06-24)
current_time_reference: 2026-06-24(同日)
Δt: 同日内(数値的な長期化は未観測)
classification: ACTIVE STATE(直前のseal実行から連続するイベント境界内)
```

本文書の作成自体は新たな構造変更ではない(拡張差分)ため、次にΔtがQUIESCENT
判定に移行するのは、本文書のseal完了後、次のイベント(A6 commit/tag/push、
またはWARN状態変化)が発生しない期間が続いた場合である。

## 5. 統合結果(A6 + O0-v1 + O0-v2)

```
A6    = structural static system(空間)
O0-v1 = event-based observer(イベント検知)
O0-v2 = temporal annotation layer, non-trigger(時間文脈付与)
```

3層は相互に非干渉。変化はA6で発生し、O0-v1が検知し、O0-v2が時間文脈
(ACTIVE/QUIESCENT/STATIC PLATEAU)を付与するが、いずれの層も他層の構造・
発火条件を変更しない。

## 6. 保留事項(本文書では扱わない、将来の論点として記録のみ)

「Δtが長期化したときに意味変化が起きるかどうか(意味論的ドリフト問題)」は、
本文書のスコープ外として保留する。これに着手する場合、Δtを補助メタデータから
判定要素に格上げする可能性を含むため、第2.2節の絶対制約(Δtは非トリガー)との
整合を別途検討する必要がある。現時点では着手しない。

## 7. 実装状態

本文書はいかなる実装・コード変更も含まない。コード・実行システムは一切
実装していない。状態分類(ACTIVE/QUIESCENT/STATIC PLATEAU)は本文書内の静的
定義であり、自動判定機構は存在しない。

## 8. 現在の運用状態(本文書の効力範囲外の事実)

2026-06-24時点の実際の状態は本文書により変化しない:
FROZEN=不変、Extension=DRAFT、Human Gate=未裁定、pre-authorization state=継続中、
Trigger Wiring=凍結継続。

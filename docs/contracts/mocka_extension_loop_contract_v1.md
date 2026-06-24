# MoCKA Extension - Loop Contract v1 (Input -> Store -> Extract -> Reinput)

Status: DRAFT(裁定済み構造、擬似アルゴリズムとして確定。実装はまだ無し)
Date: 2026-06-24
裁定者: Human Gate(きむら博士)
作成者: Claude-sonnet-4-6

## 0. 本契約の位置づけ

本契約は既存のFROZEN構造を置き換えるものではない。
既存の Event Layer 最小定義(Core Event) / Essence pipeline(既存4系統) /
Phase10-3 Signal Non-Layer Contract / Phase10-Stasis制約は、
本契約により一切変更されない。

本契約はMoCKA extensionの既存3契約
([Analytical Event](mocka_extension_analytical_event_contract_v1.md) /
[index](mocka_extension_index_contract_v1.md) /
[meta-essence](mocka_extension_meta_essence_contract_v1.md))
の上に乗る最終層であり、これら3契約のスキーマ・ルールを一切変更しない。

本契約は「処理定義」であって「実行システム」ではない。
実装コード化は行わず、擬似アルゴリズムのレベルに留める。
本契約をもってMoCKA extension三層+ループの設計は構造契約として閉じる。

## 1. 基本定義

MoCKA Loop は、既存3層を変更せず、その上で
「データがどう循環し、再び意味として再投入されるか」を
定義する動作契約である。

4段階: Input -> Store -> Extract -> Reinput

```
Input        : 新しい観測の発生
   |
   v
Store        : Analytical Event 生成 + index への追記
   |
   v
Extract      : indexグラフからmeta-essenceへの圧縮
   |
   v
Reinput      : meta-essenceの結果を次のInputの文脈として提供
   |
   '----------> (Inputへ循環)
```

## 2. 各段階の擬似アルゴリズム

### 2.1 Input

```
function on_observation(core_event):
    # core_event は既存Event Core(FROZEN)が成立させたものを
    # 参照するのみ。ここでCore Eventを生成・変更しない。
    require core_event.exists_and_immutable()
    pass_to(Store, core_event)
```

### 2.2 Store

```
function store(core_event):
    analytic_event = build_analytical_event(
        core_ref = core_event.id,
        analytic_diff = observe(core_event)
    )
    # mocka_extension_analytical_event_contract_v1.md のスキーマに従う

    index_entry = append_index_entry(
        analytic_event_id = analytic_event.id,
        core_ref = analytic_event.core_ref,
        prev_index_id = current_tail_index_id()
    )
    # mocka_extension_index_contract_v1.md のスキーマに従う
    # append-only、書き換え・削除は行わない

    pass_to(Extract, index_entry)
```

### 2.3 Extract

```
function extract(index_entry):
    # 即時実行を強制しない。クラスタ単位 or 連続区間単位で
    # バッチ的に実行されることを許容する(タイミングは本契約の対象外)
    cluster = collect_cluster(index_entry)
    # mocka_extension_meta_essence_contract_v1.md の入力対象ルールに従う
    # Core Eventへは一切戻らない

    if cluster.ready_for_compression():
        meta = compress(cluster, compression_type)
        # semantic_cluster | drift_summary | causal_fold のいずれか
        pass_to(Reinput, meta)
```

### 2.4 Reinput

```
function reinput(meta_essence):
    # meta_essenceの結果は「次の観測の文脈」としてのみ提供される。
    # Core Event / index への逆書き込みは行わない
    #(meta_essence_contract_v1.md 第8章で禁止済み)
    context = as_context(meta_essence)
    provide_context_for_next_observation(context)
    # ここでループはInputへ戻るが、
    # 「次に何を観測するか」を強制・誘導するものではない
```

## 3. 循環の性質(重要な制約)

### 3.1 Reinputは強制発火ではない

Reinputが提供する文脈は、次のInputの「参考情報」に過ぎない。
これは新しい観測を自動生成するトリガーではない。
Trigger Wiring/起動主体の議論(Phase10-Stasis下で停止中)とは
無関係であり、本契約はその議論を再開しない。

### 3.2 ループは情報の流れであり、制御の流れではない

本契約が定義するのは「データの循環経路」のみである。
「いつ・誰が・どの条件で各段階を起動するか」という制御主体の
問題は本契約の対象外とする(Trigger Wiringの領域、未裁定のまま)。

### 3.3 各段階の独立性

Input/Store/Extract/Reinputの4段階は、それぞれ独立した
既存契約(Core Event/Analytical Event/index/meta-essence)の
ルールに従うのみであり、本契約は新しいルールを追加しない。
本契約は「既存ルールをどの順で通過するか」という経路図のみを
定義する。

## 4. 禁止事項(本契約v1の範囲)

- Input段階でCore Eventを生成・変更すること(禁止、Core Eventの
  成立は既存Event Core契約の専管事項)
- Store段階でindexへの書き換え・削除を行うこと(禁止、append-onlyのみ)
- Extract段階でCore Eventへ戻って再評価すること(禁止)
- Reinput段階でCore Event/Analytical Event/indexへ逆書き込みする
  こと(禁止、meta-essenceからの逆書き込みは既存契約で禁止済み)
- 本契約をもってループの自動実行・自動トリガーを実装すること
  (禁止、本契約は処理定義のみであり実行系統ではない)
- 既存Essence pipeline(4系統)とのループ統合(禁止、parallel essence
  layerの非干渉原則を維持する)

## 5. 全体構造(最終形、MoCKA extension完成図)

```
[FROZEN: Core Event] --reference only--> [Analytical Event]
                                                |
                                                v
                                          [index (trace graph)]
                                                |
                                                v
                                          [meta-essence]
                                                |
                                                v
                                  [Reinput: context for next Input]
                                                |
                                                '--> (戻る: Input)
```

## 6. 実装状態

本契約は擬似アルゴリズムによる動作契約の最終定義のみであり、
コード・実行システムは一切実装していない。MoCKA extension
(Analytical Event / index / meta-essence / Loop)の構造設計は
本契約をもって構造契約として閉じる。実装着手にはHuman Gateの
明示指示を要する。

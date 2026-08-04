# JARVIS HG-J04 観測記録 — M-1 / M-2 / M-3 v0.1
## Human Gate 5系統の状態モデル・記録先・イベント照合

**文書番号:** JARVIS-HGJ04-EV-001
**調査日:** 2026-08-04
**状態:** **観測記録のみ(裁定なし・Decision作成なし・採用判断なし・実装なし・設定変更なし)**

## 0. 調査条件(きむら博士指示)

| 条件 | 遵守状況 |
|---|---|
| 実装変更禁止 / 設定変更禁止 | 遵守(読み取りのみ) |
| Decision 作成禁止 / 採用判断禁止 | 遵守 |
| 観測結果のみ記録 / Unknown 保持 | 本文書 / §6 |
| **既存 Human Gate イベントとの照合** | §4 |

---

## 1. Human Gate 5系統 一覧(Confirmed)

| # | 実体 | 状態記録先 | 状態語彙 |
|---|---|---|---|
| **HG-1** | `phi_os/human_gate.py` | `mocka_events.db` の **`human_gate_events`** テーブル | `PENDING / APPROVED / REJECTED / EXPIRED / CANCELED` |
| **HG-2** | `app.py` `/decision/approve` `/decision/reject` | **`data/prevention_queue.json`**(JSONファイル) | `NEW / approved / rejected`(+ `approved_at` / `rejected_at`) |
| **HG-3** | `governance/mocka_git_safe_commit.py` の Core System File 除外 | git 作業ツリー(未コミット状態として保持) | 状態語彙なし(コミット有無) |
| **HG-4** | `semantic/query_engine/human_gate.py` | **インメモリ**(`HumanGateRulingStore._records: list`)。永続化なし | `accept / reject / defer / split`(**merge は恒久的に除外**) |
| **HG-5** | `governance/human_gate_continuity.py` | **`data/decisions/pending_decision_units.jsonl`**(2件) | `WAITING_FOR_HUMAN_GATE` のみ |

**Confirmed:** **5系統は状態記録先が全て異なり、状態語彙も一致しない。**

---

## 2. M-1: HG-2(`/decision/approve` `/decision/reject`)

### 2.1 実装(Confirmed / コード実測)

```python
# app.py:2360  /decision/approve
data = _load_pqueue()                      # data/prevention_queue.json を読む
for item in data["queue"]:
    if item.get("id") == pid and _is_pending_status(item.get("status")):
        item["status"] = "approved"
        item["approved_at"] = datetime.now().isoformat()
_save_pqueue(data)                         # 同ファイルへ書き戻す
append_event({ "what_type": "DECISION_APPROVED",
               "who_actor": "kimura_hakase",   # ← ハードコード
               "free_note": pid, ... })        # → Gate経由(get_buffer().push)
```

`/decision/reject` も同型(`status="rejected"` / `rejected_at` / `what_type="DECISION_REJECTED"`)。

**観測:**
- 状態の**正本は `data/prevention_queue.json`** であり、`human_gate_events` テーブルではない。
- Event 記録は `append_event()` 経由 = **Canonical Ledger 経路を通る**(`DC_20260725_003` が保護対象と名指しした経路)。
- `who_actor` は **`"kimura_hakase"` がコード内にハードコード**されている。
  呼出者を検証する処理は本ルート上に発見できなかった(認証・セッション確認なし)。

### 2.2 状態の実測

| ストア | 実測 |
|---|---|
| `data/prevention_queue.json`(mtime 2026-08-04 14:06) | **1,941件**。`rejected` 1,799 / `NEW` 137 / `approved` 5 |
| 対応する Event | `DECISION_APPROVED` **5件** / `DECISION_REJECTED` **1件** |

### 2.3 Confirmed な不一致 — 一括却下 1,799件が Event 化されていない

バックアップ `data/prevention_queue.json.bak_bulk_reject_20260628_090221`(mtime 2026-06-28 09:02)の実測:

| 時点 | 件数 | status 分布 |
|---|---|---|
| 一括却下**直前**(バックアップ) | 1,805 | `NEW` **1,799** / `approved` 5 / `rejected` **1** |
| 現在 | 1,941 | `rejected` **1,799** / `NEW` 137 / `approved` 5 |

すなわち **2026-06-28 に `NEW` 1,799件が一括で `rejected` へ変更された。**

| 照合項目 | 実測 |
|---|---|
| `DECISION_REJECTED` イベント総数 | **1件**(`E20260628_0053418841871` / 2026-06-28T08:30:05 / `_source='buffered'`) |
| 同イベントの時刻 vs 一括却下 | イベント **08:30:05** → バックアップ **09:02** の順。バックアップ時点で `rejected` は1件 = **このイベントが唯一の正規ルート経由の却下** |
| 一括却下 1,799件に対応する Event | **0件** |
| 一括却下 1,799件に対応する `human_gate_events` の reject 記録 | **0件**(§4.1) |
| 一括却下を実施したスクリプト | リポジトリ内に発見できず(`bulk_reject` grep、`archive/`・`venv/` 除外)= **Unknown**(U-30) |

**観測(事実のみ):** 状態ファイルは 1,799件を `rejected` として保持しているが、
その遷移は Event Ledger にも `human_gate_events` にも記録されていない。

---

## 3. M-2: HG-4 / HG-5 の状態モデルと HG-1 との異同

### 3.1 HG-4 `semantic/query_engine/human_gate.py`(Confirmed)

```
Phase7-B-6 - Human Gate Ruling v0 (institutional design, not resolution)
契約: docs/contracts/phase7_b6_human_gate_ruling_v1.md

重要な前提: Human Gateは最適化装置・解決装置・正規化装置ではない。
「矛盾の意味的分岐点を固定する装置」である。裁定はGovernedCollisionRecord
を書き換えるのではなく、別レイヤのRulingRecordとして追加保存される。

絶対禁止（契約5章より）:
  - mergeを裁定タイプとして受理すること
  - collision以外(trace/graph fragment)への直接裁定
  - 元データ・GovernedCollisionRecordの変更・上書き
  - RulingRecordの削除・上書き（append-onlyのみ）
  - 裁定の自動生成・自動推論
```

| 項目 | 内容 |
|---|---|
| 裁定型 | `accept` / `reject` / `defer` / `split`。`merge` は `ValueError` で拒否 |
| データ構造 | `RulingRecord(from_cluster, to_cluster, ruling_type, rationale, recorded_at)` |
| 永続化 | **なし**(`HumanGateRulingStore.__init__` の `self._records: list` = プロセス内メモリ) |
| 上書き・削除 | **メソッドが構造的に存在しない**(append-only) |
| 対象 | collision(意味衝突)。**request / 承認要求ではない** |

**HG-1 との異同:**
- 対象が異なる(HG-1 = 承認要求 / HG-4 = 意味衝突の裁定)
- 状態語彙が異なる(`PENDING/APPROVED/...` vs `accept/reject/defer/split`)
- **HG-4 には遷移(TRANSITIONS)の概念がない**。RulingRecord を積むのみ
- HG-4 は永続化しない

### 3.2 HG-5 `governance/human_gate_continuity.py`(Confirmed)

```
Phase C-4: Deferred Human Gate Protocol (DHGP) — 縮小版。
MCP接続断を障害として扱うのではなく、Human Gate承認待ちという正式な
状態(WAITING_FOR_HUMAN_GATE)として記録し、Pending Decision Unitとして
永続化する。Core System Fileのcommitを自動化・代替承認することは
一切行わない。
```

| 項目 | 内容 |
|---|---|
| 状態 | `WAITING_FOR_HUMAN_GATE` のみ |
| 永続化先 | `data/decisions/pending_decision_units.jsonl`(**実測 2件**) |
| 分離理由(原文) | 「WAITING状態は『まだ決定していない』ことを表し、決定済み記録である Decision Ledger に混在させると approved/aborted のみを前提とする既存の集計・監査ロジックの意味が壊れるため」 |
| **構造的制約(原文)** | 「本ファイルは WAITING_FOR_HUMAN_GATE へ遷移した時点で処理を止める構造であり、**governance_state をそこから先に進める関数自体を実装しない**(『実装しない』を運用ルールではなく構造で担保する)」 |
| スコープ外(明記) | Human Gate 再接続方式 / event_id 取得経路 / 自動 resume 可否判定 / resume 後の commit 許可条件 → **TODO_429 の裁定対象**(2026-07-08 博士裁定により Phase C-4 スコープ外と確定済み) |

**HG-1 との異同:**
- HG-5 は**状態を1つしか持たず、前進させる関数を意図的に持たない**
- 永続化先が Decision Ledger とも `human_gate_events` とも別
- HG-1 の `PENDING` と HG-5 の `WAITING_FOR_HUMAN_GATE` の対応関係は**どの文書にも記載がない**(U-31)

---

## 4. 既存 Human Gate イベントとの照合(指示事項)

### 4.1 `human_gate_events` 全数分析(Confirmed / 1,779件)

| 観測項目 | 実測 |
|---|---|
| 総数 | 1,779 |
| `type` | `HUMAN_GATE_EVENT` 1,779(単一) |
| **`action`** | **`submit` 1,774 / `approve` 5**。**`reject` / `expire` / `cancel` は 0件** |
| `next_state` | `PENDING` 1,774 / `APPROVED` 5 |
| `previous_state` | `None` 1,774 / `PENDING` 5 |
| 日付分布 | **2026-06-23: 1,776** / 2026-07-08: 1 / 2026-07-31: 2 |
| `request_id` 接頭辞 | `TECH` 1,768 / `PQ` 8 / `INC-LIFECYCLE-` 2 / `TEST` 1 |

**Confirmed:** **1,774件(全体の99.7%)が `PENDING` のまま解決されていない。**
`reject` アクションの記録は **1件も存在しない**。

### 4.2 移行イベントの特定(Confirmed)

`PQ` 接頭辞 8件は、2026-06-23T01:57:15〜16 の 0.4 秒間に生成された submit/approve の4対である。

| request_id | submit payload | approve payload |
|---|---|---|
| `PQ_7A0EB099` | `{"component":"router","original_status":"approved",...}` | `{"note":"pseudo-transition from migration, no original PENDING history"}` |
| `PQ_A8B940A3` | 同型(`router`) | 同型 |
| `PQ_2FAC1DD2` | 同型(`router`) | 同型 |
| `PQ_DAAAB02E` | 同型(`claude_mcp`) | 同型 |

この note 文字列は `phi_os/migrate_prevention_queue.py:73` のハードコード値と一致する(Confirmed)。
すなわち **これらは `migrate_prevention_queue.py` による移行記録である。**

続く `TECH_ALERT_*` 1,768件も同時刻帯(01:57:16.759〜)から連続生成されており、
同一移行処理によるものと読める(**Confirmed: 時刻連続性 / Unknown: 実行主体の直接証拠**、U-32)。

### 4.3 `prevention_queue.json` との突合(Confirmed)

| 照合 | 実測 |
|---|---|
| `prevention_queue.json` の `id` と `human_gate_events.request_id` の一致 | **1,773 / 1,941** |
| 不一致 168件 | 移行(2026-06-23)以降に `prevention_queue` へ追加された項目と読める |

### 4.4 **2ストア間の状態不一致(本調査の中心的観測)**

同一の 1,773 項目について、2つのストアが異なる状態を保持している。

| 項目 | `human_gate_events`(HG-1) | `prevention_queue.json`(HG-2) |
|---|---|---|
| 状態 | **`PENDING` 1,774** | **`rejected` 1,799** |
| 却下の記録 | **0件** | 1,799件 |
| 最終更新 | 2026-07-31 | 2026-08-04 14:06 |

**時系列(Confirmed):**

```
2026-06-23 01:57  migrate_prevention_queue.py 実行
                  → human_gate_events へ 1,776件(submit 1,772 + submit/approve 4対)
                  → 全て PENDING(4件のみ APPROVED)

2026-06-28 08:30  /decision/reject が1件実行(DECISION_REJECTED イベント1件)

2026-06-28 09:02  prevention_queue.json 一括却下
                  → NEW 1,799 → rejected 1,799
                  → Event 0件 / human_gate_events 0件

2026-07-08        human_gate_events に submit 1件(TEST_CLI_VERIFY_001)
2026-07-31        human_gate_events に submit/approve 各1件(INC-LIFECYCLE-INC-20260401-001)
2026-08-04        prevention_queue.json は更新継続(NEW 137件)
```

**すなわち 2026-06-28 の一括却下以降、2ストアは乖離した状態のまま現在に至る。**
本文書はこの乖離の是非を評価しない(**裁定禁止**)。

---

## 5. M-3: Core / Finalization 2層と実装の対応

### 5.1 定義文書側(`mocka_human_gate_decision_definition_v1.md`、Confirmed)

| 層 | 役割 | 状態 / 出力 |
|---|---|---|
| **Human Gate Core** | 評価機構(自動)。**判断材料の生成のみ** | 内部状態 `IDLE / EVALUATING / EVALUATED`。出力に **`decision` フィールドを含めてはならない**(§6) |
| **Human Gate Finalization** | **きむら博士本人**。唯一の決定点 | `APPROVE / HOLD / REJECT / DEFER` |

§7(最重要、原文):
> APPROVE/HOLD/REJECT/DEFER の確定は Human Gate Finalization(博士本人)のみが行う。Core がこれを単独で確定することは禁止。

### 5.2 実装側の状態語彙との対応(Confirmed)

| 定義文書 | HG-1 `phi_os/human_gate.py` | HG-2 `app.py` | HG-4 `semantic/…` | HG-5 `continuity` |
|---|---|---|---|---|
| **APPROVE** | `APPROVED`(action `approve`) | `approved` | `accept` | — |
| **HOLD** | **対応なし** | **対応なし** | **対応なし** | `WAITING_FOR_HUMAN_GATE`(?) |
| **REJECT** | `REJECTED`(action `reject`) | `rejected` | `reject` | — |
| **DEFER** | **対応なし** | **対応なし** | `defer` | `WAITING_FOR_HUMAN_GATE`(?) |
| (定義文書に対応なし) | `PENDING` / `EXPIRED` / `CANCELED` | `NEW` | `split` | — |
| Core 内部状態 `IDLE/EVALUATING/EVALUATED` | **実装なし** | **実装なし** | **実装なし** | **実装なし** |

**Confirmed:**
- **`HOLD` に対応する状態を持つ実装は存在しない。**
- **`DEFER` は HG-4 のみが持つ**(`defer`)。
- **Core の3状態(`IDLE/EVALUATING/EVALUATED`)を実装した系統は1つもない。**
- 逆に実装側にのみ存在する状態が複数ある(`PENDING` `EXPIRED` `CANCELED` `NEW` `split`)。
- HG-5 の `WAITING_FOR_HUMAN_GATE` が `HOLD` / `DEFER` のどちらに対応するかは
  **いずれの文書にも記載がない**(U-31)。

### 5.3 HG-1 の遷移モデル(Confirmed / コード実測)

```python
STATES = {"PENDING", "APPROVED", "REJECTED", "EXPIRED", "CANCELED"}
TRANSITIONS = {
    "submit":  {None},                              # 新規生成のみ
    "approve": {"PENDING"},
    "reject":  {"PENDING"},
    "expire":  {"PENDING"},
    "cancel":  {"PENDING", "APPROVED", "REJECTED"},
}
ACTION_NEXT_STATE = {"submit":"PENDING","approve":"APPROVED","reject":"REJECTED",
                     "expire":"EXPIRED","cancel":"CANCELED"}
```

`get_state()` は「request_id の現在状態を **event 列から再構築**する」(docstring)= イベントソーシング。

### 5.4 **Core / Finalization を判別する情報がスキーマに存在しない(重要)**

`human_gate_events` のカラム(Confirmed):

```
event_id, timestamp, type, action, request_id, payload, previous_state, next_state
```

**`actor` に相当するカラムが存在しない。**

| 観測 | 内容 |
|---|---|
| 定義文書 §7 の要求 | `APPROVE` の確定は **博士本人のみ**が行える |
| HG-1 のスキーマ | `approve` を **誰が実行したかを記録する欄がない** |
| HG-2 の実装 | `who_actor` に `"kimura_hakase"` を**ハードコード**(呼出者の検証なし) |
| 結果 | **記録から Core 実行と Finalization 実行を区別できない** |

**観測(事実のみ):** 定義文書が求める2層分離は、現行のいずれの実装にも
**構造として表現されていない**。本文書はこの是非を評価しない。

---

## 6. Unknown(本調査で確定できなかった事項)

| # | Unknown |
|---|---|
| **U-30** | 2026-06-28 の `prevention_queue.json` 一括却下(1,799件)を実施した主体・手段。リポジトリ内に該当スクリプトを発見できず(`bulk_reject` grep、`archive/`・`venv/` 除外) |
| **U-31** | HG-5 の `WAITING_FOR_HUMAN_GATE` が定義文書の `HOLD` / `DEFER` のいずれに対応するか。文書に記載なし |
| **U-32** | `TECH_ALERT_*` 1,768件の生成主体の直接証拠(時刻連続性から `migrate_prevention_queue.py` と読めるが、payload に移行を示す文字列は含まれない) |
| **U-33** | HG-3(`mocka_git_safe_commit.py` の Core System File 除外)の「承認」がどこに記録されるか。本調査では状態語彙・記録先を特定できず |
| **U-34** | HG-4 の `HumanGateRulingStore` が実行時に生成されるか(外部 import 0件のため、生成箇所自体が未発見) |
| **U-35** | `pending_decision_units.jsonl` 2件の内容と、TODO_429(WAITING 状態からの前進方式)の現況 |
| **U-36** | `prevention_queue` の 168件(移行後追加分)が HG-1 側へ反映される経路の有無 |
| **U-37** | `/decision/approve` `/decision/reject` の呼出元(UI / 拡張 / 手動 HTTP)と実運用での使用頻度 |
| U-01 / U-02 | (HG-J03 から継続)拡張の有効/無効、service worker の実稼働 |

---

## 7. HG-J04 判断材料としての整理(観測のみ・評価を含まない)

`JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md` §4.5 の Option への対応。

| Option | 本調査で得られた事実 |
|---|---|
| **J04-A**(HG-1 を唯一の接続先) | 状態記録先は `human_gate_events`(1,779件)。イベントソーシングで遷移モデルを持つ唯一の系統。ただし 1,774件が `PENDING` のまま。HTTP Blueprint は未登録。`actor` カラムなし |
| **J04-B**(HG-2 を接続先) | 状態正本は JSON ファイル。Event は Canonical Ledger 経路を通る。ただし `who_actor` ハードコード、2026-06-28 の一括却下 1,799件が Event 化されていない |
| **J04-C**(専用接続先を定めず提示のみ) | 「提示」と「submit」の境界を定める材料は本調査では得られていない |
| **J04-D**(Human Gate 実装整理を先行) | 整理対象の規模: 5系統 / 状態記録先5種 / 状態語彙の不一致(§5.2)/ 2ストア乖離(§4.4)/ Unknown 8件(U-30〜U-37) |

**いずれの Option についても、本文書は採否・優劣を評価しない。**

**変わらない点(§2.2 で既述、再掲):**
`mocka_human_gate_decision_definition_v1.md` §7 により
**JARVIS が確定権を持たない点は J04-A〜D のいずれを選んでも変わらない。**
`JARVIS_CONSTITUTION_DRAFT.md` の P-2 / P-3 / P-14 はこの禁止を継承しており、
J04 の結果によって変更される条項ではない(観測)。

---

## 8. 本調査で行っていないこと

- 裁定・Decision 作成・採用判断・優劣評価
- 実装変更・設定変更
- 2ストア乖離(§4.4)の是正
- U-30(一括却下の主体)の追跡 — **本調査は HG-J04 の材料収集であり、原因追跡は別 Scope**
- `pending_decision_units.jsonl` の内容読み取り(U-35)
- TODO_429 の現況確認

---

## Knowledge Lineage

**Document:** JARVIS_HGJ04_EVIDENCE_M1_M2_M3_v0.1.md
**Status:** 観測記録(裁定なし、Decision Ledger 未登録)
**Created:** 2026-08-04
**Origin:** きむら博士指示「HG-J04 観測開始。対象: M-1 / M-2 / M-3。条件: 実装変更禁止・設定変更禁止・Decision作成禁止・採用判断禁止・観測結果のみ記録・Unknown保持・既存Human Gateイベントとの照合を行う」
**Parent Documents:**
- `docs/governance/JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md`(§4 HG-J04、§10.3 M-1〜M-3)
- `docs/governance/JARVIS_HGJ03_EVIDENCE_COMPLETE_v0.1.md`(§7 次工程)
- `docs/governance/mocka_human_gate_decision_definition_v1.md`
**Primary Evidence:**
`phi_os/human_gate.py`(`STATES` / `TRANSITIONS` / `ACTION_NEXT_STATE` / `get_state`)、
`phi_os/migrate_prevention_queue.py`(L71/L73)、`governance/human_gate_cli.py`、
`governance/human_gate_continuity.py`、`semantic/query_engine/human_gate.py`、
`app.py`(L2264 `_load_pqueue` / L2360 `/decision/approve` / L2395 `/decision/reject`)、
`data/prevention_queue.json`(1,941件)、`data/prevention_queue.json.bak_bulk_reject_20260628_090221`(1,805件)、
`data/decisions/pending_decision_units.jsonl`(2件)、
`data/mocka_events.db`(`human_gate_events` 1,779件全数分析 / `events` の `DECISION_APPROVED` 5件・`DECISION_REJECTED` 1件)
**Affected Components:** なし(読み取りのみ。コード・設定の変更ゼロ)
**Revision History:**
- R1(2026-08-04): 新規作成。M-1 / M-2 / M-3 と既存 Human Gate イベントの照合を記録。
  Unknown を U-30〜U-37 として保持。裁定・Decision 作成・採用判断・実装のいずれも行っていない。

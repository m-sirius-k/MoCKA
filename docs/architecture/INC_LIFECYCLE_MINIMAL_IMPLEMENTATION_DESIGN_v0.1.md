# INC Lifecycle Minimal Implementation Design v0.1

RC-B 最小実装(M-1 / M-2 / M-3)の設計。承認軸は既存 Human Gate 基盤を再利用する。

- 作成日: 2026-07-31
- 最終更新: 2026-07-31(改訂1)
- 種別: Design(実装方式設計)。**NON-CANONICAL / 未実装**
- 根拠Decision: DC_20260731_003 (RC-B採択) / DC_20260731_004 (Stage 1a-1d細分化) /
  **DC_20260731_005 (承認軸=既存Human Gate基盤の再利用、2軸モデルの基本設計化)**
- 先行文書: INC_LIFECYCLE_IMPLEMENTATION_SCOPE_v0.1.md / INC_LIFECYCLE_STATE_MODEL_v0.1.md
- 本工程での禁止事項遵守: コード変更なし / INC生成ロジック変更なし / restrictions.py変更なし /
  events.csv変更なし / Stage 1d未着手
- 基準commit: baddd113d0202eb08b33bcadf4c115a228234c17(作業ツリーは Stage 1a / 1b 適用済)

---

## 改訂履歴

| 改訂 | 日付 | 内容 | 根拠 |
|------|------|------|------|
| 初版 | 2026-07-31 | M-1/M-2/M-3 の方式比較。候補(a)から(e)を並列に提示 | DC_20260731_003 / 004 |
| 改訂1 | 2026-07-31 | INC専用State Machine案(候補c)を削除。human_gate.py再利用を正式候補として確定。2軸モデルを基本設計へ昇格。Human Gate凍結領域への影響確認(第5節)を追加 | **DC_20260731_005** |
| 改訂2 | 2026-07-31 | 第2節(INC進行軸の保持場所)を案A/案B/案Cの比較へ拡張。調査3件(生成更新主体の全確認 / 公開境界 / 既存台帳との責務分離)の結果を追加。案Cの二分(C-1/C-2)を明示 | 比較設計指示(実装は行わない) |
| 改訂3 | 2026-07-31 | 案B前提の State Schema v0.1(6.6)、Human Gate 境界の明記(6.7)、restrictions.py 接続方式と Fail Closed 条件(6.8)、実装対象ファイル一覧(6.9)、回帰影響ベースライン(6.10)を追加。既存 INL との衝突確認(2.8)、保存場所の命名候補(2.9)、復元可能性(2.10)を追加 | 接続方式確定指示(実装は行わない) |
| 改訂4 | 2026-07-31 | **INL との責務分離境界を確定(2.11)。state ディレクトリ名称を `data/inc_lifecycle/` に確定(2.12)。初期状態投入方式を設計(6.11)。Stage 1c Implementation Ready 判定を追加(6.12)** | 3点確定指示(実装は行わない) |
| 改訂5 | 2026-07-31 | **実装前提3点の確定を反映。request_id 形式 `INC-LIFECYCLE-<incident_id>`、INC-20260401-001 の承認軸を `PENDING` 開始、submit 自動投入の不採用(方式3-A採用)。判定を Conditionally Ready から Implementation Ready へ更新** | **DC_20260731_006** |

初版で並列候補として扱っていた承認軸の保持先は、DC_20260731_005 により確定した。
本改訂以降、承認軸は比較対象ではない。未確定は**進行軸の保持場所のみ**である。

---

## 0. 設計の前提となる事実

いずれもコード読解および読取専用DBアクセスで確認した実測値である。

### 0.1 汎用承認エンジンが既に存在する

`phi_os/human_gate.py`(320行)は、汎用の承認状態機械として既に稼働している。

| 項目 | 実測値 |
|------|--------|
| 状態集合 | `PENDING` / `APPROVED` / `REJECTED` / `EXPIRED` / `CANCELED` (L23) |
| 遷移検証 | `TRANSITIONS` により previous_state を検証。`approve` は `PENDING` からのみ (L26-32) |
| 保存先 | `data/mocka_events.db` の `human_gate_events` テーブル (L21, L57) |
| 方式 | event-sourced。状態はevent列から再構築する (L88 `get_state`) |
| 実績 | `human_gate_events` に **1777件** の記録 |
| 公開API | `submit` / `approve` / `reject` / `expire` / `cancel` / `list_pending` |

モジュール冒頭(L5-6)に責務の所在が明記されている。

> PHI-OSがHuman Gateの唯一の状態管理責務を持つ。
> GL7およびApp層はHuman Gate状態を保持しない(本モジュールが単一の真実)。

L207-213 には再利用の原則と先例(reason promotion)が記述されている。

> Review Gateは新しい状態機械ではない。Human Gateが持つ汎用承認エンジン
> (submit/approve/reject、PENDING/APPROVED/REJECTED状態)を(中略)
> 同一テーブル・同一状態機械のまま集計・監査できる。

### 0.2 人間による承認手段が既に存在し、TTY必須で強制されている

`governance/human_gate_cli.py`(133行)は Human Gate CLI Provider として実装済みである。

| 項目 | 実測値 |
|------|--------|
| 呼び出し先 | `phi_os.human_gate` の `submit` / `approve` / `reject` / `get_state` / `list_pending` (L33) |
| コマンド | `submit` / `status` / `pending` / `approve` / `reject` |
| **S-1の技術的強制** | `approve` / `reject` は `_require_tty()` により**対話端末からの実行のみ許可**(L36, L68, L84)。非対話実行(パイプ等)は拒否される |
| 明示的な非対象 | `phi_os/human_gate.py` の変更 / Event Store の複製・変更 / Event形式の変更 / Router・Policyの実装 / commit実行(L13-23) |

**帰結**: 条項 S-1(自動承認の禁止)は、設計上の約束ではなく**既存コードが技術的に強制している**。
自動ロジックが `approve` を呼ぼうとしても TTY 判定で拒否される。

### 0.3 既存の自動承認経路(条項 S-1 に対する要注意事項)

`app.py:2075-2094` の `_auto_approve_prevention()` は、Prevention案に対して
機械が承認を書き込む。

```python
severity = item.get("severity", "NORMAL").upper()
if severity in ("HIGH", "CRITICAL"):
    continue  # Human Gate
item["status"] = "approved"
item["approved_by"] = "AUTO_GATE"
```

対象は Prevention Queue であり INC ではないため、現時点で条項 S-1 の違反ではない。
またこの経路は `phi_os/human_gate.py` を通らない別系統である。
ただし"severityが低ければ機械が承認する"運用パターンが既に存在する事実は、
INC の承認設計において明示的に排除しておく必要がある。

**設計上の要件**: INC の承認軸に対して、severity 等を条件に機械が自動遷移する経路を
作らないこと。承認軸を human_gate 経由に限定することで、この要件は構造的に満たされる。
回帰確認項目 R-26 はこの経路を含めて検査する。

### 0.4 公開境界(git追跡状況)

進行軸の保持場所の選定を左右する実測値。

| 保存先候補 | 実在 | git追跡 | origin/mainへの公開 |
|------------|------|---------|---------------------|
| docs/incidents/INC-*.md | あり | **tracked** | **公開される** |
| data/mocka_events.db | あり | untracked(gitignored) | されない |
| data/decisions/decision_ledger.jsonl | あり | untracked(gitignored) | されない |

`.gitignore:2` の `data/*` により data/ 配下は全除外。
docs/incidents/ の INC ファイルは5件すべて tracked である。

---

## 1. 基本設計: 2軸モデル

DC_20260731_005 により、2軸モデルを基本設計とする。以降の設計はこれを前提とする。

| 軸 | 状態 | 進める主体 | 保持場所 |
|----|------|------------|----------|
| **INC進行軸** | `DETECTED` / `ANALYZED` / `PUBLISHED` / `CLOSED` | 機械 | **未確定**(第2節) |
| **承認軸** | `PENDING` / `APPROVED` / `REJECTED` | **人間のみ** | **確定**: `phi_os/human_gate.py` + `human_gate_events` |

### 1.1 2軸に分ける理由

機械が進める状態と人間のみが進める状態を同一フィールドに置くと、条項 S-1 を
実装で保証しにくくなる。2軸に分けることで、書込主体を物理的に分離できる。

この分離は既存の裁定 DC_20260705_008(Active)の責務分離と同型である。

> (1) 自動検知系は、PENDING状態への投入のみを担当し、可否判断には一切関与しない。
> (2) Human Gate は、PENDING状態の保持・一覧表示・状態遷移の受付窓口としてのみ機能する。
> (3) approve()/reject()の呼び出しは、実際に人間がUI/APIを操作した場合にのみ許可する。
>     自動ロジック・推論結果による呼び出し経路は一切設けない。

INC パイプラインを (1) の"自動検知系"に位置づけると、本設計は既存の責務分離に
そのまま収まる。新しい原則を追加する必要がない。

### 1.2 承認軸の確定内容

| 項目 | 内容 |
|------|------|
| 状態管理 | `phi_os/human_gate.py`(変更しない) |
| 保存先 | `data/mocka_events.db` の `human_gate_events`(スキーマ変更しない) |
| 人間の操作手段 | `governance/human_gate_cli.py`(既存。TTY必須) |
| INCとの対応付け | **`request_id` = `INC-LIFECYCLE-<incident_id>`(DC_20260731_006で確定)**。例: `INC-LIFECYCLE-INC-20260401-001` |
| 条項S-1の担保 | `TRANSITIONS` による遷移検証 + CLI の `_require_tty()` |
| 投入方式 | **RC-B から `submit()` を自動投入しない(DC_20260731_006)**。承認投入は人間が `governance/human_gate_cli.py` を使用する |

### 1.3 不採用となった案

| 案 | 状態 | 理由 |
|----|------|------|
| INC専用の状態機械を新設(初版の候補c) | **削除** | 重複状態機械。`human_gate.py` L5-6 の単一真実源原則、L207-213 の再利用原則に反する(DC_20260731_005) |
| 6状態を単一軸として実装 | **削除** | 機械が進める状態と人間のみが進める状態が同居し S-1 を保証しにくい(DC_20260731_005) |
| Decision Ledger に全遷移を記録(初版の候補d) | **削除** | 裁定と進行度が混在し粒度が細かすぎる(DC_20260731_005) |

---

## 2. M-1: INC進行軸の保持場所(比較中)

承認軸は DC_20260731_005 で確定済みのため、本節の比較対象は**進行軸のみ**である。
案A(INC本文) / 案B(別管理ファイル) / 案C(既存イベント基盤)を比較する。

### 2.0 調査結果1: INC-*.md の生成・更新主体(全確認)

`.py` 全走査(`__pycache__` 除く)により、docs/incidents/ を参照する全モジュールを確認した。

| モジュール | 操作 | 内容 |
|------------|------|------|
| tools/mocka_risk_engine.py:82, :109-110 | **生成(w)** | `auto_generate_incident()` がINCファイルを新規作成する |
| tools/mocka_5w1h.py:104, :135-136 | **更新(w)** | 既存本文を読み、`## 5W1H分析` を末尾へ追記して全文書き戻す |
| tools/mocka_restrictions.py:10, :12-19 | 読取 | glob と本文抽出のみ |
| runtime/governance/preventive_rule_engine.py:20, :24 | 読取 | listdir + 全文読取 |
| runtime/governance/semantic_engine.py:27, :30 | 読取 | listdir + 全文読取 |
| runtime/governance/library_engine.py:32, :35 | 読取 | listdir + 全文読取 |
| archive/ledger_old/record/self_doubt_engine.py:17 | 読取 | archive配下(廃止系) |

**書込主体は2つのみ**である。`mocka_risk_engine.py`(生成)と `mocka_5w1h.py`(追記更新)。
`restrictions.py` は読取専用であり、公開処理はINCファイルを書き換えない。

読取専用4モジュールのパース方式(案Aの影響評価に必要):

| モジュール | パース方式 | `## Lifecycle` 追加の影響 |
|------------|------------|---------------------------|
| tools/mocka_restrictions.py | `split("## 再発防止")[1].split("##")[0]` | `## 再発防止` より**後方**に置けば抽出内容は不変。**内部に置くと再発防止欄が汚染される** |
| semantic_engine.py | `re.sub` で記号除去後 `text.split()` の語彙集合化 | 状態値がトークンとして語彙集合に混入する |
| library_engine.py | `if keyword in text` の全文一致 | キーワードが状態値と衝突する場合に誤検出しうる |
| preventive_rule_engine.py | 全文読取 | 同上 |

いずれも見出し階層を解釈しないため、`## Lifecycle` セクションの追加で**壊れることはない**。
ただし semantic / library 系の語彙解析に状態値が混入する副作用がある。

### 2.1 調査結果2: 公開境界(実測)

`git check-ignore` による判定結果。

| 保存先 | 判定 | 公開 |
|--------|------|------|
| `docs/incidents/INC-*.md` | 追跡対象(gitignoreされない) | **origin/main へ公開される** |
| `data/incidents/state/INC-xxxx.json` | `.gitignore:2` の `data/*` に該当 | されない |
| `data/incidents/INC-xxxx.json` | 同上 | されない |
| `data/mocka_events.db` | 同上 | されない |

`data/incidents/` は現時点で**存在しない**(新規作成が必要)。
判定は空パスに対する `git check-ignore` で実施し、確認後に作成した空ディレクトリは撤去済み。

### 2.2 調査結果3: 既存 Decision / Event Ledger との責務分離

`docs/mocka3/DECISION_LEDGER_SCHEMA_v1.md` 第1節が責務を明示している。

> イベント基盤(Foundation/Lifecycle/Protocol)が"何が・どう変化したか"を管理するのに対し、
> Decision Ledgerは"なぜそう決定されたか"を記録し、設計継承性・監査性・再現性を保証する。

これに INC進行軸を重ねると、次のようになる。

| 層 | 責務 | 実体 | 件数 |
|----|------|------|------|
| Event基盤 | **何が・どう変化したか**(履歴) | `events` テーブル | 18578件 |
| Decision Ledger | **なぜそう決定されたか**(理由) | `decision_ledger.jsonl` | 201行 |
| Human Gate | **承認されたか**(承認状態) | `human_gate_events` | 1777件 |
| **INC進行軸** | **今どの段階にあるか**(現在状態) | **未定** | - |

INC進行軸は"現在状態"であり、履歴でも理由でも承認でもない。
**既存3層のいずれの責務とも一致しない**。これが案Cの責務混同リスクの実体である。

### 2.3 既存 `lifecycle_phase` との名称衝突(案Cの実測懸念)

`events` テーブルには既に `lifecycle_phase` 列が存在し、別の意味で使われている。

| 値 | 件数 | 意味 |
|----|------|------|
| `in_operation` | 11159 | 通常運用 |
| (NULL) | 6857 | - |
| `N/A` | 523 | - |
| `normal` | 21 | - |
| `incident` | 1 | リスク検知時(`tools/mocka_risk_engine.py:68-73` が設定) |

これは**イベントのリスク段階**であり、INC進行軸(`DETECTED`/`ANALYZED`/`PUBLISHED`/`CLOSED`)とは
別の軸である。案Cで同一テーブルに進行軸を持たせると、名称と意味が二重化する。

なお `events.related_event_id` が `INC-` で始まる行は **1件のみ**であり、
現状 events と INC の紐付けはほぼ機能していない(D-4 / D-5 の帰結)。

### 2.4 案A / 案B / 案C の比較

| 観点 | 案A: INC本文 | 案B: 別管理ファイル | 案C: 既存イベント基盤 |
|------|--------------|---------------------|----------------------|
| 例 | `## Lifecycle` / `state: ANALYZED` | `data/incidents/state/INC-xxxx.json` | `data/mocka_events.db` |
| 公開境界 | **公開される** | されない(`data/*`) | されない(`data/*`) |
| 人間の確認 | **INC単体で完結**。ファイルを開けば判る | 対応ファイルを別途開く必要がある | DB照会が必要 |
| 自動処理適性 | 中(テキストパース) | **高**(JSON) | 高(SQL) |
| 責務分離 | 文書と状態の二重管理 | **状態専用層として明確** | **履歴と現在状態の混同リスク**(2.2) |
| 既存資産の活用 | 既存ファイルのみ | なし(新規ディレクトリ) | **既存監査基盤** |
| 名称衝突 | なし | なし | **`lifecycle_phase` と二重化**(2.3) |
| 対応関係の管理 | 不要(同一ファイル) | **必要**(INC ID とファイル名の対応) | 必要(`related_event_id` 等) |
| 書込主体への影響 | 既存2主体(risk_engine / 5w1h)が触る場所と同居 | 書込主体を分離できる | 書込主体を分離できる |
| 既存INC 2件の移行 | 本文編集が必要 | 状態ファイル2件の新規作成 | レコード2件の投入 |
| DC_20260731_005 との関係 | - | - | **新テーブル新設なら不採用済の候補(c)と同一**(2.5) |

### 2.5 案Cの二分(重要)

案Cは実装形態により2つに分かれ、一方は既に不採用である。

| 形態 | 内容 | 状態 |
|------|------|------|
| C-1 | 既存 `events` テーブルへ進行軸を記録(新テーブルを作らない) | 比較対象。ただし 2.2 の責務混同と 2.3 の名称衝突を伴う |
| C-2 | INC進行軸専用のテーブルを新設する | **不採用済**。DC_20260731_005 が候補(c)"INC専用の状態機械を新設"として却下している |

案Cを検討する場合は C-1 に限られる。C-2 を採るには DC_20260731_005 の見直しが必要となる。

### 2.6 選定に影響する事実(整理)

1. 進行軸は機械が進めるため、承認軸と異なり条項 S-1 の担保を必要としない。
   "機械が書ける場所"であることは進行軸では欠点にならない
2. 案Aで公開されるのは進行度であって承認結果ではない。承認結果は非公開の
   `human_gate_events` にあるため、判断結果の露出は生じない。
   ただし"どのINCがどこまで進んでいるか"は公開される
3. 案Aは `## 再発防止` より後方に配置する限り `restrictions.py` の抽出を壊さない。
   ただし semantic / library 系の語彙解析に状態値が混入する
4. 案Bは `data/incidents/` の新規作成が必要。同ディレクトリは現存しない
5. 案C(C-1)は既存監査基盤を使えるが、2.2 の責務分離と 2.3 の名称衝突の
   2点を設計で解決する必要がある
6. 書込主体の観点では、案A は既存2主体が触るファイルに状態が同居し、
   案B / 案C は書込主体を分離できる

### 2.7 既存INC 2件の書式不一致(実測)

案Aで既存の `## 承認` 欄を流用する場合の懸念。ただし本改訂では承認軸を
human_gate へ分離したため、`## 承認` 欄を進行軸に流用する必要はない。

| ファイル | 記述 |
|----------|------|
| INC-20260401-001.md | `## 承認：Claude Sonnet 4.6 / 2026-04-01`(同一行) |
| INC-20260401-002.md | `## 承認：` の次行に `自動生成 / 要Claude確認`(別行) |
| INCIDENT_TEMPLATE.md | `## 承認：` のみ(空) |

新規の進行軸フィールドを別に設ければ、この書式差の影響を受けない。
既存 `## 承認` 欄の扱い(残置 / 廃止 / 移行)は第7節の未確定事項とする。

### 2.8 既存 Incident Navigation Layer (INL) との衝突確認

`data/` 配下に、同じ `INC-YYYYMMDD-NNN` 形式のIDを用いる**既存のインシデント台帳が存在する**。

| ファイル | 実測 | 内容 |
|----------|------|------|
| `data/incident.json` | 3156B / 2026-07-02 更新 | INL Layer 1。個別事象の単票。**`status` フィールドを既に持つ**(`open` / `resolved` / `monitoring`) |
| `data/class_registry.json` | 5918B / 2026-07-02 更新 | INL Layer 2/3。分類と階層構造 |
| `data/incident_links.json` | 1650B / 2026-07-02 更新 | INL 横断リンク |
| 設計文書 | `docs/governance/DESIGN_MEMO_INL_v0.1.md`(2026-07-02) | 3ファイル構成の設計メモ |

`data/incident.json` の `_meta.fields` は `incident_id` を"一意ID。 INC-YYYYMMDD-NNN 形式"と定義しており、
`docs/incidents/INC-*.md` と**同一のID体系**である。

現況(実測):

| 項目 | 値 |
|------|----|
| INL 側の登録件数 | 1件(`INC-20260702-001`、status: `resolved`) |
| `docs/incidents/` 側 | 2件(`INC-20260401-001` / `-002`) |
| 実レコードの重複 | **なし**(日付が異なる) |
| INLを読み書きする `.py` | **0件**。完全な手動運用 |

DESIGN_MEMO_INL_v0.1.md 第3節が"v0.1では自動検証コードはまだ実装していない(意図的にスコープ外)"と
明記しており、コード参照が0件であることと一致する。

**確認された衝突リスク**

1. **ID採番の衝突**: `tools/mocka_risk_engine.py:76-81` の採番は `docs/incidents/` 内の
   当日ファイル数+1 であり、INL側のIDを参照しない。同一日にINL側とrisk_engine側が
   採番すると同じIDが生成されうる。現時点では未発生(2026-07-02 と 2026-04-01 で日付が異なる)
2. **状態軸の三重化**: INL の `status`(open/resolved/monitoring)は、本設計の進行軸
   (DETECTED/ANALYZED/PUBLISHED/CLOSED)とも承認軸(PENDING/APPROVED/REJECTED)とも異なる
   **第3の状態軸**である。案Bで state ファイルを新設すると、INCの状態を持つ場所が
   INL・進行軸・承認軸の3箇所になる
3. **命名の紛らわしさ**: `data/incident.json`(単数形)が既に存在するため、
   `data/incidents/`(複数形)を新設すると視認上の区別が付きにくい

**本設計での扱い**: INL は変更対象外(指示による固定領域ではないが、本工程のスコープ外)。
上記1と2は第7節の未確定事項として記録する。INLと進行軸の統合可否は別途の判断を要する。

### 2.9 保存場所の命名候補(案B)

`data/` 配下のディレクトリ命名規則は lowercase snake_case(実測21件: `decisions` /
`integrity` / `context_snapshots` / `pending_reviews` / `watcher_queue` 等)。

| 候補 | 公開 | 2.8との紛らわしさ | 備考 |
|------|------|-------------------|------|
| `data/incidents/state/` | されない | **高**(`data/incident.json` と単複の差のみ) | 指示書の例示 |
| `data/inc_lifecycle/` | されない | 低 | 進行軸専用であることが名称から判る |
| `data/incident_state/` | されない | 中 | 既存 `incident_links.json` と同系の命名 |

いずれも `.gitignore:2` の `data/*` により非公開。選定は第7節の未確定事項とする。

**参考(1エンティティ=1JSONの先例)**: `records/master/` に `E20260326_001.json` 形式で
1279件が**git追跡済み**で存在する。ファイル分割の先例はあるが、公開境界が data/ とは逆である。

### 2.10 復元可能性(バックアップ・復旧)

state ファイルが破損・消失した場合の復元手段を実測で確認した。

**(1) INC本文からの復元: 不完全**

| INCファイル | `## 5W1H分析` の有無 | GPT_RESTRICTIONS.md への掲載 | 本文から導出される状態 | 実態 |
|-------------|----------------------|------------------------------|------------------------|------|
| INC-20260401-001 | **なし** | あり | `DETECTED`(誤り) | `PUBLISHED` |
| INC-20260401-002 | あり | あり | `ANALYZED` | `DETECTED` 相当(未分析) |

`## 5W1H分析` の有無を `ANALYZED` の判定に使うと、**旧形式のINC-20260401-001を誤判定する**。
同ファイルは人間が手作業で作成したもので、5W1H自動分析を経ていないためである。
また `CLOSED` は本文からもGPT_RESTRICTIONS.mdからも導出できない。

**(2) Event Ledger からの追跡: 現状不可**

`events.related_event_id` が `INC-` で始まる行は **1件のみ**(実測)。
D-4 / D-5 の帰結として INC と events の紐付けがほぼ機能していないため、
Event Ledger から進行軸を再構築することはできない。

**(3) 結論**

進行軸の状態は、state ファイル以外から**完全には復元できない**。
したがって案Bを採る場合、state ファイル自体のバックアップが必要である。
`data/backups/` が既存の保管先として存在するが、現在の用途は拡張機能の
zip/ディレクトリ退避であり、ファイル単位のスナップショット規約は未定である
(PHI_OS_ENCODING_MIGRATION_PLAN_v0.2.md 6.2 と同じ論点)。

### 2.11 INL との責務分離境界(確定)

2.8 で確認したとおり、`data/incident.json` を中心とする Incident Navigation Layer (INL) は
同一の `INC-YYYYMMDD-NNN` 形式のIDを用い、独自の `status` を持つ。
本節で両者の責務境界を確定する。

#### 2.11.1 責務の分離

| 観点 | INL | INC Lifecycle(本設計) |
|------|-----|----------------------|
| 問い | **この障害は何であり、過去のどれと同類か** | **このINCはパイプラインのどこまで進んだか** |
| 目的 | 分類・到達・再発検知 | 公開制御 |
| 状態語彙 | `open` / `resolved` / `monitoring` | `DETECTED` / `ANALYZED` / `PUBLISHED` / `CLOSED` |
| 状態の意味 | **障害そのものの収束度** | **処理工程の進行度** |
| 時間軸 | 障害の発生から解決まで | INC生成から公開まで |
| 実体 | `data/incident.json` ほか2ファイル | `data/inc_lifecycle/INC-*.json` |
| 記入主体 | 人間(手動運用。`.py` 参照0件) | 機械(パイプライン) |
| 記載内容 | root_cause / resolution_path / symptom_tags 等の分析情報 | 状態のみ(6.6.3の禁止項目に従う) |

**両者は同じ対象(INC)の異なる属性を記録する。** 障害が `resolved` であることと、
そのINCが `PUBLISHED` であることは独立に成立しうる。

#### 2.11.2 境界規則

| # | 規則 |
|---|------|
| L-1 | **INC Lifecycle は INL を参照しない。** 公開判定に INL の `status` を用いない |
| L-2 | **INC Lifecycle は INL へ書き込まない。** `data/incident.json` 他2ファイルは本設計の変更対象外 |
| L-3 | **INL の `status` と進行軸の `state` を相互変換しない。** 語彙も意味も異なる |
| L-4 | INL は人間が手動運用する層であり続ける。本設計は INL の自動化を行わない |
| L-5 | 両者を統合する場合は別Decisionを要する。本設計では統合しない |

#### 2.11.3 残る接点: ID空間の共有

責務は分離できるが、**ID空間は共有されたままである**。これは解消していない。

`tools/mocka_risk_engine.py:76-81` の採番は `docs/incidents/` 内の当日ファイル数+1 であり、
INL側のIDを参照しない。同一日に両者が採番すると同じ `INC-YYYYMMDD-NNN` が生成されうる。

| 状況 | 現況 |
|------|------|
| 実際の重複 | **なし**(INL: 2026-07-02 / docs/incidents: 2026-04-01) |
| 将来の重複可能性 | **あり**。同一日に両系統が採番した場合 |
| 本設計での対処 | **行わない**。第7節の未確定事項として残す |

本設計は `data/inc_lifecycle/INC-*.json` を `docs/incidents/INC-*.md` と1対1で対応させる。
INL の incident_id とは対応させない。したがって ID が偶然一致しても、
本設計の state ファイルが INL のレコードを指すことはない。
ただし**人間が両者を取り違える可能性**は残るため、未確定事項として記録する。

### 2.12 state ディレクトリ名称(確定)

**確定名: `data/inc_lifecycle/`**

#### 2.12.1 選定根拠

| 候補 | 空き | 判定 | 理由 |
|------|------|------|------|
| `data/incidents/state/` | 空き | **不採用** | 既存 `data/incident.json` と単複の差のみで視認上の区別が付かない。名称衝突の回避要件を満たさない |
| `data/incident_state/` | 空き | **不採用** | `incident_` 接頭辞が INL 系(`incident.json` / `incident_links.json`)と同系に見え、2.11 で分離した責務が名称上は混ざる |
| **`data/inc_lifecycle/`** | 空き | **採用** | `incident` で始まらないため INL 系と視覚的に区別できる。`lifecycle` が進行軸専用であることを示す |
| `data/inc_pipeline_state/` | 空き | 不採用 | 意味は明確だが3語で冗長。既存21ディレクトリの命名(1-2語が主)から外れる |

#### 2.12.2 既存命名規則との整合(実測)

`data/` 直下のディレクトリ21件はすべて lowercase snake_case。
語数は1語が18件、2語が3件(`context_snapshots` / `pending_reviews` / `watcher_queue`)、
3語が1件(`chrome_cdp_profile`)。`inc_lifecycle` は2語であり規則内に収まる。

#### 2.12.3 衝突確認(実測)

| 確認項目 | 結果 |
|----------|------|
| `data/inc_lifecycle` の実在 | **存在しない**(空き) |
| `data/` 配下で `inc` から始まる既存名 | `incident.json` / `incident_links.json` の2件。いずれも `incident` であり `inc_` ではない |
| 公開境界 | `.gitignore:2` の `data/*` により**非公開** |

#### 2.12.4 確定内容

```
data/inc_lifecycle/
    INC-YYYYMMDD-NNN.json      <- 1 INC = 1 ファイル
```

ファイル名は `docs/incidents/INC-YYYYMMDD-NNN.md` の basename に `.json` を付けたものとする。
サブディレクトリは設けない(件数が増えた場合の分割は将来の判断)。

---

## 3. M-2: DETECTED 状態付与方式

### 3.1 付与位置

`tools/mocka_risk_engine.py:75-111` `auto_generate_incident()` の content 構築(L84-107)。

### 3.2 方式比較(2軸前提)

| 方式 | 進行軸 | 承認軸 | 判定 | 備考 |
|------|--------|--------|------|------|
| **3-A** | state ファイルに付与 | 付与しない(人間が投入) | **採用(DC_20260731_006)** | RC-B から Human Gate への書込が発生しない。区分1(読取)のみとなり凍結領域に触れない |
| 3-B | 付与しない | `submit()` で `PENDING` 生成 | 不採用 | 区分2に該当。進行状態も残らない |
| 3-C | state ファイルに付与 | `submit()` で `PENDING` 生成 | 不採用 | 区分2に該当。DC_20260705_008 が持ち越しとした配線作業に触れうる |

改訂5時点の注記: 改訂3までは 3-A の懸念として"承認待ちINCを `list_pending()` で
一覧できない"を挙げていたが、DC_20260731_006 により承認軸の投入は人間が
`governance/human_gate_cli.py submit` で行うことが確定したため、
投入後は `list_pending()` で一覧できる。当該懸念は解消した。

### 3.3 選定に影響する事実

- 3-C の不整合リスクは、どちらを正とするかを定めれば運用上解消できる
  (承認軸を正とし、INC本文の進行軸は表示用の写しとする等)
- 3-B / 3-C は `tools/mocka_risk_engine.py` から `phi_os/human_gate.py` への
  依存が発生する。依存方向の妥当性は未評価(第5節)
- `submit()` の呼び出しは DC_20260705_008 (1) の"自動検知系は PENDING 投入のみを担当"に
  合致する。機械が `submit` を呼ぶこと自体は既存裁定の想定内である

### 3.4 既存INC 2件の扱い

| ファイル | 承認軸の初期値(候補) | 進行軸の初期値(候補) |
|----------|----------------------|----------------------|
| INC-20260401-001.md | `APPROVED` | `PUBLISHED` |
| INC-20260401-002.md | `PENDING` | `DETECTED` または `ANALYZED` |

INC-20260401-002 の進行軸は条項 S-3 の決定に依存するが、**承認軸を `PENDING` に
すれば公開対象から外れる**ため、進行軸の確定は完全実装まで保留できる。

INC-20260401-001 を `APPROVED` として扱ってよいかは第7節の未確定事項とする。
承認欄に人間名の記載はあるが、本状態モデルによる承認手続きを経たものではない。

---

## 4. M-3: APPROVED 条件による公開制御

### 4.1 実装位置は1箇所

`tools/mocka_restrictions.py:12-19` の抽出ループが、公開対象を選別する唯一の箇所である。
GPT_RESTRICTIONS.md への書込も同ファイル L52-53 のみ(`.py` 全走査で確認済)。

```python
for path in sorted(incidents):          # L12  glob "INC-*.md" (L10)
    with open(path, encoding="utf-8") as f:
        content = f.read()
    if "## 再発防止" in content:         # L15  唯一の採否判定
        ...
```

### 4.2 取得元(承認軸確定により第一候補が定まる)

| 方式 | 取得元 | 評価 |
|------|--------|------|
| **4-1** | `phi_os.human_gate.get_state("INC-LIFECYCLE-<incident_id>")` を参照 | **採用**。DC_20260731_006 の request_id 規約確定により実装可能な形で定まった。承認軸の正本を直接参照し、遷移検証済みの状態を得られる |
| 4-2 | 承認済みINCの一覧(公開許可リスト)を別に持つ | 不採用。一覧の生成主体と更新契機の設計が別途必要となる(DC_20260731_006 impact) |
| 4-3 | INC本文の状態行を読む | 不採用。INC本文には進行軸しか置かないため、承認判定の根拠にならない |

4-1 により `tools/mocka_restrictions.py` から `phi_os/human_gate.py` への依存が生じる。
**1方向・読取のみ**であり、接触度は区分1(凍結領域に触れない)に収まる(5.2 / DC_20260731_006)。

### 4.3 失敗時の挙動(必須要件)

**要件 F-CLOSED**: 承認状態が取得できない場合、当該INCを公開してはならない(fail-closed)。

該当する場合:

- 承認軸に対応するレコードが存在しないINC(既存2件、手動作成INC)
- 状態の取得に失敗した場合(DB接続失敗等)
- 状態が `APPROVED` 以外のすべて(`PENDING` / `REJECTED` / `EXPIRED` / `CANCELED`)

fail-open を選ぶと D-1 の是正が状況次第で無効化される。回帰確認項目 R-27 に対応する。

### 4.4 副次的な影響

M-3 実装後、GPT_RESTRICTIONS.md の掲載内容は**減る方向**に変化する。
現行掲載2件のうち INC-20260401-002 は脱落する。全件脱落は R-04 で確認する。

### 4.5 D-2 に対する効果

`tools/mocka_risk_engine.py:154-159` の起動順序はそのまま残るが、公開対象が
承認済みに限定されるため、分析前の内容が公開されることはなくなる。
順序そのものの是正(F-3)は完全実装の範囲である。

---

## 5. Human Gate 凍結領域への影響確認

DC_20260731_005 が実装着手前の先行条件として要求する確認事項。

### 5.1 凍結の実在と範囲(一次データで確認)

| 記録 | status | 内容 |
|------|--------|------|
| **DC_20260706_001** | Active | "Human Gate Phase1Bの凍結状態は本件と独立に維持し、変更しない" |
| DC_20260705_008 | Active | 責務分離を確定。ただし"実際の配線作業(human_gate_bpのapp.py登録、prevention_queueからPENDING投入への接続)は本Decisionの範囲外とし、次回セッションの実装課題として持ち越す" |

DC_20260706_001 は却下案として"別レイヤーの完了をもって凍結解除を自動的に判断する"ことを
**自律裁定化リスクとして明示的に退けている**。本設計はこれに該当してはならない。

関連するTODOの現況(data/MOCKA_TODO.json):

| TODO | status | 内容 |
|------|--------|------|
| PHI-OS-HUMAN-GATE-STATE-MODEL-V1 | 進行中 | Human Gate State Model v1 + GL7最小カーネル仕様v1(確定仕様・未実装) |
| GL7-UNENFORCED-CONDITIONS-BUG | 未着手 | GL7の安全条件3点が実行経路に未接続(Human Gate含む) |
| TODO_207 | 未着手 | TIC Layer 4 — Human Gate UI(COMMAND CENTER TICパネル) |

### 5.2 接触度による区分

RC-B 最小実装が Human Gate 基盤に対して行う操作を、接触度で3区分する。

| 区分 | 操作 | 凍結領域への接触 | 評価 |
|------|------|------------------|------|
| **区分1** | `get_state()` / `list_pending()` の**読取のみ** | **接触しない** | 既存状態を変更しない。M-3(4-1)が該当 |
| **区分2** | `submit()` による `PENDING` 投入 | **要確認** | DC_20260705_008 (1) の"自動検知系はPENDING投入のみ"に合致するが、同Decisionは配線作業を持ち越しとしている。M-2(3-B/3-C)が該当 |
| **区分3** | `approve()` / `reject()` の呼び出し配線 | **接触しない(実装不要)** | `governance/human_gate_cli.py` が既に人間側の手段を提供済み。RC-B側で新規に配線する必要がない |

### 5.3 確認結果

1. **区分1(読取)は凍結領域に触れない。** 状態を読むだけであり、Human Gate の状態も
   スキーマも変更しない。M-3 の第一候補(4-1)はこの区分に収まる
2. **区分3は実装不要である。** 初版作成時点では"人間が承認を与えるインタフェースが未確定"と
   していたが、`governance/human_gate_cli.py` が既に存在し、`approve`/`reject` を
   TTY必須で提供していることを確認した。TODO_207(Human Gate UI)は未着手だが、
   CLI が代替手段として機能する
3. **区分2(submit投入)のみが要確認である。** DC_20260705_008 は自動検知系による
   PENDING 投入を責務として認めているが、その配線作業自体を"次回セッションの実装課題"
   として持ち越している。RC-B から新たに投入経路を作ることが、この持ち越し扱いの
   作業に該当するか否かは判断を要する

### 5.4 凍結解除との関係(明示)

本設計および RC-B 最小実装の完了は、**Human Gate Phase1B の凍結解除の根拠にならない**。
DC_20260706_001 が維持する凍結は本件と独立である。
RC-B 最小実装が完了しても、凍結は凍結のまま維持される。

### 5.5 区分2を回避する構成(選択肢)

区分2の判断を待たずに最小実装を進める必要がある場合、以下の構成が成立しうる。

- M-2 を方式 3-A(進行軸のみINC本文に付与、`submit()` を呼ばない)とする
- 承認軸のレコードは、人間が `governance/human_gate_cli.py submit` を実行して作る
- M-3 は区分1(読取のみ)で承認状態を参照する

この構成では、RC-B 側のコードから Human Gate への書込が一切発生しない。
ただし承認待ちINCの `PENDING` 投入が人手作業になるため、運用負荷と投入漏れの
リスクが生じる。採否は第7節の未確定事項とする。

---

## 6. 最小実装案

### 6.1 構成

| # | 項目 | 確定内容 | 未確定 |
|---|------|----------|--------|
| M-1 | 状態保持 | 2軸モデル。**承認軸=human_gate 再利用で確定** | 進行軸の保持場所((a)/(b)) |
| M-2 | `DETECTED` 付与 | `auto_generate_incident()` 内で付与 | 方式(3-A / 3-B / 3-C)。区分2の判断に依存 |
| M-3 | 公開制御 | `restrictions.py:12-19` に承認状態の確認を追加。**F-CLOSED 必須** | 取得元(4-1 / 4-2) |

### 6.2 達成されること

| 目的 | 達成 | 根拠 |
|------|------|------|
| 露出窓を閉じる(未承認INCの自動公開の停止) | 達成 | M-3 + F-CLOSED |
| D-1 の解消 | 達成 | 公開の事前条件が成立する |
| D-2 の実害の消滅 | 達成(構造は残る) | 4.5 |
| 条項 S-1 の保証 | 達成 | `TRANSITIONS` の遷移検証 + CLI の `_require_tty()` により**技術的に強制済み** |
| Stage 1c の解除条件の充足 | 達成 | 露出窓が閉じるため Stage 1d の前提が整う |

### 6.3 達成されないこと

| 項目 | 状態 | 理由 |
|------|------|------|
| **D-3 の解消** | **残る** | 条項 S-3(ANALYZED の成果物契約)は完全実装の範囲。承認済みINCでも `## 再発防止` 欄が `（要分析）` のままなら、その内容が公開される |
| D-5 の解消 | 対象外 | INC生成の発火判定であり本モデルの範囲外 |
| `CLOSED` / `REJECTED` の運用 | 部分的 | 承認軸の `REJECTED` は human_gate が提供する。進行軸の `CLOSED` は未実装 |
| Human Gate Phase1B の凍結解除 | **対象外** | 5.4 |

**注意**: 最小実装の完了をもって"INCパイプラインが是正された"と見なさないこと。

### 6.4 実装順序の案(選定は行わない)

```
1. 進行軸の保持場所の確定 + M-2 方式の確定(区分2の判断を含む)
      |
      v
2. M-2 の実装(この時点では公開挙動は変わらない)
      |
      v
3. 既存INC 2件への初期状態の割り当て(承認軸のみ)
      |
      v
4. M-3 の実装 + F-CLOSED
   (この時点で GPT_RESTRICTIONS.md の内容が変化する)
      |
      v
5. 回帰確認(R-01/02/04/20/21/26/27/30)
      |
      v
6. Stage 1c 解除の判定(Human Gate)
```

手順3を手順4より前に置く理由: 逆順にすると、承認軸のレコードを持たない既存INC 2件が
F-CLOSED により両方とも脱落し、GPT_RESTRICTIONS.md の該当節が一時的に空になる。

### 6.5 回帰確認項目

| ID | 項目 | 備考 |
|----|------|------|
| R-01 | 承認なしINCが反映されないこと | - |
| R-02 | 承認済みのみ反映されること | - |
| R-04 | 全件脱落が起きないこと | - |
| R-20 | 既存の有効な禁止事項が失われないこと | - |
| R-21 | 常時禁止セクションが維持されること | - |
| R-26 | 機械が `APPROVED` を書き込む経路が存在しないこと | 0.3 の `_auto_approve_prevention()` 型の経路を含めて検査する |
| R-27 | 承認状態が取得できないINCが公開されないこと(F-CLOSED) | - |
| R-30 | Stage 1a/1b の結果が退行していないこと | RC-A と RC-B の独立性の確認 |

R-03(承認欄の書式差異)は、承認軸を human_gate へ分離したため**対象外**となった。

### 6.6 INC Lifecycle State Schema v0.1(案B前提)

**目的**: 現在状態の保持のみ。履歴管理ではない。

```json
{
  "schema_version": "0.1",
  "incident_id": "INC-YYYYMMDD-NNN",
  "state": "DETECTED",
  "updated_at": "2026-07-31T00:00:00+00:00"
}
```

#### 6.6.1 項目の必要性検証

| 項目 | 必要性 | 根拠 |
|------|--------|------|
| `schema_version` | **必要** | 本Schemaは v0.1 であり変更が見込まれる。読み手が解釈規則を判定できないと、将来の形式変更時に fail-closed 判定と区別が付かなくなる |
| `incident_id` | **必要** | ファイル名からも導出できるため冗長だが、ファイル名の破損・改名時に内容だけで対象を特定できる自己記述性を持つ。不整合検出(ファイル名との照合)にも使える |
| `state` | **必要** | 本Schemaの本体 |
| `updated_at` | **必要** | 鮮度判定に用いる。**最終更新の1点のみ**を保持し、履歴配列は持たない |
| `source_incident`(指示書の候補) | **不要と判断** | 命名規約で `INC-YYYYMMDD-NNN.json` と `docs/incidents/INC-YYYYMMDD-NNN.md` の1対1対応を保証すれば導出可能であり、冗長。ただし将来INCの配置が変わる可能性を考慮する場合は再検討の余地がある(第7節) |

#### 6.6.2 `state` の値域

`DETECTED` / `ANALYZED` / `PUBLISHED` / `CLOSED` の4値のみ。

**承認軸の値(`PENDING` / `APPROVED` / `REJECTED` / `EXPIRED` / `CANCELED`)を
本Schemaに書いてはならない。** 値域を4値に限定することで、進行軸ファイルに承認状態が
混入することを構造的に防ぐ。

#### 6.6.3 保存しないもの(禁止項目)

| 禁止項目 | 理由(責務の所在) |
|----------|------------------|
| Decision の理由・根拠 | Decision Ledger の責務("なぜそう決定されたか") |
| Human 承認の理由・承認者 | Human Gate の責務(`human_gate_events` の payload) |
| Event 履歴・遷移履歴の配列 | Event基盤の責務("何が・どう変化したか")。本Schemaは現在状態のみを持つ |
| AI の判断結果・分析内容 | 5W1H等の分析成果はINC本文の責務 |

具体的に、以下のフィールドを設けない: `approved_by` / `approved_at` / `reason` /
`rationale` / `history[]` / `transitions[]` / `analysis` / `risk_level` / `severity`。

#### 6.6.4 ファイル名規約

`<state-dir>/INC-YYYYMMDD-NNN.json`

INC ID をそのままファイル名に用いる。ディレクトリは 2.9 の候補から選定する(未確定)。

### 6.7 Human Gate との境界(明記事項)

DC_20260731_005 で確定した2軸構造を維持する。以下を設計上の遵守事項として明記する。

| # | 遵守事項 | 実装上の担保 |
|---|----------|--------------|
| B-1 | **`APPROVED` 状態は Human Gate のみを参照して判定する** | 進行軸 state ファイルは4値のみを持ち、承認状態を保持しない(6.6.2) |
| B-2 | **INC Lifecycle 側が承認を代行しない** | 進行軸の遷移(`DETECTED` -> `ANALYZED` 等)は公開可否に影響しない。公開判定は承認軸のみが決める |
| B-3 | **自動処理が approve / reject を発行しない** | `governance/human_gate_cli.py` の `_require_tty()` により、非対話実行からの `approve`/`reject` は既に拒否される(0.2)。RC-B側から `approve`/`reject` を呼ぶコードを一切書かない |
| B-4 | 2つの軸を同一状態値に統合しない | 進行軸と承認軸で値集合が重複しない(4値 vs 5値、共通要素なし) |

#### 6.7.1 二軸が同時に成立する状態の例

| INC | 進行軸 | 承認軸 | 公開されるか |
|-----|--------|--------|--------------|
| 生成直後 | `DETECTED` | (レコードなし) | されない(F-CLOSED) |
| 5W1H付与後・未承認 | `ANALYZED` | `PENDING` | されない |
| 承認済み | `ANALYZED` | `APPROVED` | **される** |
| 公開反映後 | `PUBLISHED` | `APPROVED` | される |
| 却下 | `ANALYZED` | `REJECTED` | されない |

**公開可否を決めるのは承認軸のみ**である。進行軸が `PUBLISHED` であっても、
承認軸が `APPROVED` でなければ公開されない。

### 6.8 restrictions.py 接続方式と Fail Closed 条件

#### 6.8.1 現行と変更後

```
[現行]
INC.md
  |
  v
restrictions.py  (L15: "## 再発防止" の有無のみが採否判定)
  |
  v
GPT_RESTRICTIONS.md

[変更後]
INC.md ------------+
                   |
INC state.json ----+--> restrictions.py --> GPT_RESTRICTIONS.md
                   |     (採否判定に承認軸の確認を追加)
human_gate --------+
```

進行軸(state.json)は**参照するが公開可否は決めない**(6.7.1)。
承認軸(`human_gate.get_state`)が `APPROVED` であることが公開の必要条件である。

state.json を参照する目的は、対象INCが本Lifecycle管理下にあるかの判定と、
不整合検出(進行軸と承認軸の組合せが想定外でないか)である。

#### 6.8.2 Fail Closed 条件(必須)

**原則: Fail Open は禁止。状態不明ならば公開しない。**

| # | 条件 | 動作 |
|---|------|------|
| FC-1 | state.json が存在しない | **公開しない** |
| FC-2 | state.json が読めない(I/Oエラー) | **公開しない** |
| FC-3 | state.json が JSON として不正 | **公開しない** |
| FC-4 | `schema_version` が未知 | **公開しない** |
| FC-5 | `state` が4値以外 | **公開しない** |
| FC-6 | `incident_id` がファイル名と一致しない | **公開しない** |
| FC-7 | 承認軸に対応するレコードが存在しない | **公開しない** |
| FC-8 | 承認軸の状態が `APPROVED` 以外(`PENDING`/`REJECTED`/`EXPIRED`/`CANCELED`) | **公開しない** |
| FC-9 | 承認軸の取得に失敗(DB接続失敗等) | **公開しない** |

いずれの場合も、公開しないことに加えて**理由を記録する**(記録先は第7節の未確定事項)。
無言でスキップすると、D-5(重複判定の常時成立によるINC生成の無言停止)と同型の
"気づけない停止"を新たに作ることになる。

#### 6.8.3 全件が公開されなくなる可能性

現時点で state.json は1件も存在しないため、FC-1 により**全INCが公開対象から外れる**。
GPT_RESTRICTIONS.md の"インシデントから導出された禁止事項"節が空になる。

これを避けるため、実装順序では**既存INC 2件への state 付与および承認軸レコードの投入を、
restrictions.py の変更より前に行う**(6.4 手順3が手順4より前にある理由)。

"常時禁止(全タスク共通)"8項目(`restrictions.py:28-36`)はINCに依存しないため、
全件脱落が起きても当該節は維持される(R-21)。

### 6.9 実装対象ファイル一覧(確定)

本設計に基づき実装時に触れるファイル。**本工程では変更しない。**

| # | ファイル | 変更種別 | 内容 | Stage |
|---|----------|----------|------|-------|
| 1 | `<state-dir>/INC-*.json` | **新規作成** | 進行軸 state ファイル。ディレクトリ名は未確定(2.9) | M-1 |
| 2 | `tools/mocka_risk_engine.py` | 変更 | `auto_generate_incident()`(L75-111)で state ファイルを生成し `DETECTED` を付与 | M-2 |
| 3 | `tools/mocka_restrictions.py` | 変更 | 抽出ループ(L12-19)に承認軸の確認と Fail Closed を追加 | M-3 |
| 4 | 既存INC 2件分の state ファイル | **新規作成** | 移行データ。`INC-20260401-001` / `-002` | 移行 |

**変更対象外(最小実装では触れない)**

| ファイル | 理由 |
|----------|------|
| `tools/mocka_5w1h.py` | `ANALYZED` への遷移は露出窓の閉鎖に不要。公開可否は承認軸のみが決めるため、進行軸が `DETECTED` のままでも最小実装は成立する。完全実装(F-2)で扱う |
| `phi_os/human_gate.py` | 再利用のみ。変更しない(DC_20260731_005) |
| `human_gate_events` | スキーマ変更しない |
| `docs/incidents/INC-*.md` | 本文を変更しない(進行軸は別ファイルへ保持するため) |
| `docs/governance/GPT_RESTRICTIONS.md` | 生成物であり直接編集しない |
| `data/incident.json` 他 INL 3ファイル | 本工程のスコープ外(2.8) |
| `data/events.csv` | Stage 1d の対象。RC-B では触れない |

`tools/mocka_5w1h.py` を最小実装の対象外にできる点は、本改訂で新たに確定した境界である。

### 6.10 回帰影響のベースライン(実測)

実装後に退行していないことを確認するための基準値。**本工程の作業後も全て不変であることを確認済み。**

| 対象 | 項目 | ベースライン |
|------|------|--------------|
| RC-A / Stage 1a | `data/events.csv` MD5 | `052d344c09445cb76638cdc5e4ad1536` |
| | 先頭3バイト(BOM状態) | `EF BB BF` |
| | レコード数 / 列数 | 132 / 23 |
| | event_id 先頭3件 | `E20260616_061` / `_062` / `_063` |
| D-5 遮蔽 | `docs/incidents/` の INC件数 | 2件 |
| | GPT_RESTRICTIONS.md 生成日時 | `2026-04-01 13:45:06` |
| Human Gate | `human_gate_events` 件数 | 1777件 |

#### 6.10.1 Lifecycle 追加が INC生成条件を変えないことの確認

INC生成の条件は `tools/mocka_risk_engine.py` の以下3箇所で決まる。

| 位置 | 条件 |
|------|------|
| L124 | `row.get("risk_level") != risk`(risk_levelが変化したか) |
| L129 | `risk in ("CRITICAL","HIGH") and reasons` |
| L131-136 | 重複判定(D-5の本体) |

M-2 の state ファイル生成は `auto_generate_incident()`(L75-111)の**内部または直後**に
位置し、上記3条件のいずれにも介入しない。したがって **D-5 の遮蔽状態は維持される**。

実装時は R-30(Stage 1a/1b の結果が退行していないこと)および
INC生成0件の維持を、6.10 のベースラインと照合して確認する。

### 6.11 初期状態投入方式

state ファイルをどのように最初に作るか。定常運用と一度きりの移行を分けて設計する。

#### 6.11.1 定常投入(新規INC生成時)

| 項目 | 内容 |
|------|------|
| 投入位置 | `tools/mocka_risk_engine.py` の `auto_generate_incident()`(L75-111)。INC本文の書込(L109-110)が**成功した直後** |
| 投入値 | `state: "DETECTED"` |
| 順序の理由 | 逆順(state を先)にすると、INC本文の書込が失敗した場合に state だけが残る孤児が発生する |
| 冪等性 | **既に state ファイルが存在する場合は上書きしない**。再実行で進行状態を巻き戻さないため |
| 戻り値の扱い | `auto_generate_incident()` の返り値(inc_id)は変更しない。既存呼出側(L137-139)への影響を避ける |

**state 書込に失敗した場合**

| 選択肢 | 帰結 |
|--------|------|
| (i) INC生成自体を失敗扱いにしてロールバック | INC本文の削除が必要。検知記録が失われるため不適 |
| (ii) **INC本文は残し、state 無しのまま続行する** | 当該INCは FC-1 により公開されない(安全側)。ただし**無言で落ちるため記録が必須** |

**(ii) を採る。** ただし 6.8.2 と同じ原則により、state 書込失敗は必ず記録する。
無言スキップは D-5(重複判定の常時成立による無言停止)と同型の欠陥を新設することになる。

#### 6.11.2 移行投入(既存INC 2件、一度きり)

| 対象 | 進行軸の投入値 | 承認軸の初期値 | 根拠 |
|------|----------------|----------------|------|
| `INC-20260401-001` | `PUBLISHED` | **`PENDING`(DC_20260731_006)** | 進行軸は GPT_RESTRICTIONS.md に掲載済み(実測)。承認軸は既存の公開実績を Human Gate 承認とみなさないため `PENDING` から開始する |
| `INC-20260401-002` | `DETECTED` | **`PENDING`** | `## 再発防止` 欄が `（要分析）` のまま。5W1H分析は付与済みだが、条項 S-3 未確定のため `ANALYZED` とはしない |

**両件とも承認軸は `PENDING` から開始する。** したがって移行完了直後は、
承認済みのINCが存在せず、GPT_RESTRICTIONS.md の"インシデントから導出された禁止事項"節が
一時的に0件になる(6.8.3 / DC_20260731_006 impact)。
"常時禁止(全タスク共通)"8項目は INC に依存しないため維持される(R-21)。

**自動導出を行わないこと(必須)**

2.10 の実測により、INC本文からの状態導出は誤判定する
(`INC-20260401-001` は `## 5W1H分析` が無いため `DETECTED` と誤判定される)。
したがって移行値は**人間が明示的に指定する**。導出ロジックを実装しない。

| 項目 | 内容 |
|------|------|
| 実施主体 | 人間の明示指示に基づく一度きりの作業 |
| 常設スクリプト | **作らない**。移行後に再実行されうる自動処理を残さない |
| 実施タイミング | `tools/mocka_restrictions.py` の変更(M-3)より**前**(6.8.3) |

#### 6.11.3 承認軸の初期投入との関係

進行軸の投入だけでは公開されない。公開には承認軸が `APPROVED` である必要がある(6.7.1)。

```
移行は2段階になる

第1段階: 進行軸の投入(本節)
  data/inc_lifecycle/INC-20260401-001.json  <- PUBLISHED
  data/inc_lifecycle/INC-20260401-002.json  <- DETECTED
        |
        v  この時点ではまだ公開されない(承認軸が無いため FC-7)
        |
第2段階: 承認軸の投入(人間。DC_20260731_006により確定)
  governance/human_gate_cli.py submit  --request-id INC-LIFECYCLE-INC-20260401-001
        |                                <- PENDING を作る
        v
  governance/human_gate_cli.py approve --request-id INC-LIFECYCLE-INC-20260401-001
        |                                <- 人間がTTYで承認
        v  ここで初めて公開対象になる
```

**第2段階は全工程を人間が行う(DC_20260731_006 決定3)。**
RC-B 側のコードから `submit()` / `approve()` を呼ばない。
上記のコマンド引数は `governance/human_gate_cli.py` の実装に依存するため、
実行時に `--help` で確認すること(本文書ではオプション名を確定しない)。

#### 6.11.4 投入後の検証

| # | 確認項目 | 期待値 |
|---|----------|--------|
| V-1 | state ファイル数 | `docs/incidents/INC-*.md` の件数と一致(移行時は2) |
| V-2 | ファイル名と `incident_id` の一致 | 全件一致(FC-6 の前提) |
| V-3 | JSON の妥当性 | 全件パース可能(FC-3) |
| V-4 | `state` の値域 | 全件が4値のいずれか(FC-5) |
| V-5 | `schema_version` | 全件 `"0.1"`(FC-4) |
| V-6 | 副作用の不在 | `docs/incidents/INC-*.md` と `docs/governance/GPT_RESTRICTIONS.md` が無変更 |
| V-7 | RC-A への非干渉 | `data/events.csv` の MD5 が 6.10 のベースラインと一致 |
| V-8 | Human Gate への非干渉 | `human_gate_events` 件数が 6.10 のベースラインと一致(第1段階の時点) |

#### 6.11.5 不整合の扱い

| 状況 | 扱い |
|------|------|
| INC本文あり / state なし | FC-1 により非公開。定常運用では 6.11.1 の記録により検知する |
| state あり / INC本文なし | 孤児。`restrictions.py` は `INC-*.md` を glob するため公開判定には影響しない。検出は別途(未確定) |
| ファイル名と `incident_id` の不一致 | FC-6 により非公開 |

### 6.12 Stage 1c Implementation Ready 判定

#### 6.12.1 確定済み項目

| # | 項目 | 確定内容 | 出典 |
|---|------|----------|------|
| 1 | 承認軸の保持先 | `phi_os/human_gate.py` + `human_gate_events` | DC_20260731_005 |
| 2 | 2軸モデル | 進行軸4値 / 承認軸5値。統合しない | DC_20260731_005 / 1.1 |
| 3 | 進行軸の保持方式 | 案B(別管理ファイル) | 2.4 / 改訂3以降の前提 |
| 4 | **state ディレクトリ名** | **`data/inc_lifecycle/`** | 2.12 |
| 5 | State Schema | `schema_version` / `incident_id` / `state` / `updated_at` の4項目 | 6.6 |
| 6 | Human Gate 境界 | B-1 から B-4 | 6.7 |
| 7 | restrictions.py 接続方式 | 承認軸を参照。進行軸は公開可否を決めない | 6.8.1 |
| 8 | Fail Closed 条件 | FC-1 から FC-9 | 6.8.2 |
| 9 | 実装対象ファイル | 4件(変更対象外7件を明示) | 6.9 |
| 10 | 初期状態投入方式 | 定常投入 / 移行投入 / 検証8項目 | 6.11 |
| 11 | **INL との責務分離** | L-1 から L-5 | 2.11 |
| 12 | 回帰ベースライン | 実測値7項目 | 6.10 |

#### 6.12.2 実装をブロックしていた未確定事項(すべて解消)

| # | 未確定 | 確定内容 | 根拠 |
|---|--------|----------|------|
| B-a | 区分2の扱い(RC-B から `submit()` を呼ぶか) | **呼ばない**。方式 3-A を採用し、承認投入は人間が既存 Human Gate 経路で行う | DC_20260731_006 決定3 |
| B-b | `request_id` の採番規約 | **`INC-LIFECYCLE-<incident_id>`** | DC_20260731_006 決定1 |
| B-c | `INC-20260401-001` の承認軸初期値 | **`PENDING` から開始**。既存公開実績を Human Gate 承認とみなさない | DC_20260731_006 決定2 |

#### 6.12.3 判定

### **Implementation Ready**

| 判定項目 | 状態 |
|----------|------|
| 承認軸の保持先 | 確定(DC_20260731_005) |
| 進行軸の保持方式・場所 | 確定(案B / `data/inc_lifecycle/`) |
| State Schema | 確定(6.6) |
| Human Gate 境界 | 確定(6.7、B-1からB-4) |
| restrictions.py 接続方式・取得元 | 確定(6.8 / 4.2 方式4-1) |
| Fail Closed 条件 | 確定(FC-1からFC-9) |
| 初期状態投入方式 | 確定(6.11) |
| INL との責務分離 | 確定(2.11、L-1からL-5) |
| 実装対象ファイル | 確定(6.9) |
| 実装をブロックする未確定 | **なし**(B-a / B-b / B-c すべて解消) |

#### 6.12.4 確定した実装構成(要約)

```
[生成時]  tools/mocka_risk_engine.py
             INC本文を書く -> 成功したら state を書く
             data/inc_lifecycle/INC-YYYYMMDD-NNN.json  { state: "DETECTED" }
             submit() は呼ばない

[承認時]  人間 (TTY)
             governance/human_gate_cli.py submit  INC-LIFECYCLE-<incident_id>
             governance/human_gate_cli.py approve INC-LIFECYCLE-<incident_id>

[公開時]  tools/mocka_restrictions.py
             glob docs/incidents/INC-*.md
               -> data/inc_lifecycle/<id>.json を読む (FC-1からFC-6)
               -> human_gate.get_state("INC-LIFECYCLE-<id>") を読む (FC-7からFC-9)
               -> APPROVED のもののみ GPT_RESTRICTIONS.md へ出力
```

RC-B 側から Human Gate への**書込は一切発生しない**。接触は読取(区分1)のみ。

#### 6.12.5 実装着手時の順序(6.4を本確定で具体化)

```
1. data/inc_lifecycle/ の作成
2. 既存INC 2件の state ファイル作成(進行軸: 001=PUBLISHED / 002=DETECTED)
3. 検証 V-1 から V-8
4. tools/mocka_risk_engine.py の変更(定常投入)
5. tools/mocka_restrictions.py の変更(M-3 + Fail Closed)
6. 回帰確認(R-01/02/04/20/21/26/27/30)
   この時点で GPT_RESTRICTIONS.md のINC由来項目は0件になる(想定内)
7. 人間による承認投入(submit + approve)
8. 再実行し、承認済みINCが公開されることを確認
```

手順6と手順7の間、GPT_RESTRICTIONS.md の"インシデントから導出された禁止事項"節は
空になる。これは DC_20260731_006 で想定済みの状態であり、異常ではない。
"常時禁止(全タスク共通)"8項目は維持される。

#### 6.12.6 実装着手に残る留意点(ブロッカーではない)

| # | 留意点 | 扱い |
|---|--------|------|
| N-1 | Fail Closed 時の記録先が未定(6.8.2) | 実装時に決める。記録すること自体は必須 |
| N-2 | state ファイルのバックアップ規約が未定(2.10) | 実装後の運用課題。復元が state 以外から完全にはできないため要対応 |
| N-3 | INL との ID空間の共有が未解消(2.11.3) | 責務は分離済み。ID重複は現時点で未発生 |
| N-4 | `governance/human_gate_cli.py` のコマンド引数を未確認 | 実行時に `--help` で確認する |
| N-5 | 孤児(state あり / INC本文なし)の検出方法が未定(6.11.5) | 公開判定には影響しない |

---

## 7. 未確定事項(Human Gate判断待ち)

改訂5時点で、**実装をブロックする未確定事項は存在しない**(6.12.3)。
以下は実装着手後または別工程で扱う。

### 7.1 実装時に決める(ブロッカーではない)

| # | 項目 | 参照 |
|---|------|------|
| 1 | Fail Closed 時の記録先(Event Ledger / ログ / 標準出力) | 6.8.2 / N-1 |
| 2 | 孤児(state あり / INC本文なし)の検出方法 | 6.11.5 / N-5 |
| 3 | `governance/human_gate_cli.py` のコマンド引数 | N-4 |

### 7.2 実装後の運用課題

| # | 項目 | 参照 |
|---|------|------|
| 4 | state ファイルのバックアップ規約。復元が state 以外から完全にはできないため要対応 | 2.10 / N-2 |
| 5 | INL との ID空間の共有。責務分離は確定したが `INC-YYYYMMDD-NNN` の重複可能性は未解消 | 2.11.3 / N-3 |
| 6 | 既存 `## 承認` 欄の扱い(残置 / 廃止 / 移行) | 2.7 |

### 7.3 完全実装(RC-B全体)で扱う

| # | 項目 | 参照 |
|---|------|------|
| 7 | 条項 S-3(ANALYZED の成果物契約)。**D-3 の解消はここで行う** | 5.3 F-1 |
| 8 | `ANALYZED` への遷移(`tools/mocka_5w1h.py`) | 5.3 F-2 |
| 9 | 状態遷移の順序強制 | 5.3 F-3 |
| 10 | 遷移の記録(条項 S-4) | 5.3 F-4 |
| 11 | `CLOSED` の実装 | 5.3 F-5 |
| 12 | `source_incident` 項目の要否再検討 | 6.6.1 |

### 7.4 Stage 判断(Human Gate)

| # | 項目 | 参照 |
|---|------|------|
| 13 | **最小実装をもって Stage 1c を解除するか**。D-3 が残ったまま Stage 1d(events.csv 正規化)へ進むことの可否 | 6.3 / PHI_OS_ENCODING_MIGRATION_PLAN_v0.2.md 第3節 |

### 7.5 解決済み(改訂5時点)

| 項目 | 確定内容 | 根拠 |
|------|----------|------|
| 進行軸の保持場所 | 案B | 改訂3以降の前提 |
| state ディレクトリ名 | `data/inc_lifecycle/` | 2.12(改訂4) |
| M-2 の方式 | 3-A | DC_20260731_006 |
| 区分2 の扱い / 5.5 回避構成 | 回避構成を採用。RC-Bから書き込まない | DC_20260731_006 |
| M-3 の取得元 | 4-1 | DC_20260731_006 |
| `request_id` の採番規約 | `INC-LIFECYCLE-<incident_id>` | DC_20260731_006 |
| 既存INC 2件の承認軸初期値 | 両件とも `PENDING` | DC_20260731_006 |
| `tools/` から `phi_os/` への依存 | 1方向・読取のみ。区分1に収まる | DC_20260731_006 |

---

## 8. 本文書の限界

- 本文書は設計であり、実装・検証は行っていない。第7節の方式選定も行っていない
- 第0節・第5節の事実は、コード読解、`data/mocka_events.db` の読取専用アクセス、
  Decision Ledger および data/MOCKA_TODO.json の参照に基づく。
  当該基盤が現在どの用途で実運用されているかの追跡は行っていない
- 区分2 の評価(5.3-3)は Decision Ledger の記述に基づく解釈であり、
  持ち越し作業の範囲の最終的な確定は Human Gate の判断による
- 走査範囲は C:\Users\sirok\MoCKA 配下に限定される

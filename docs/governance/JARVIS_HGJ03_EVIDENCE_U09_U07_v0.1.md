# JARVIS HG-J03 追加証拠調査 — U-09 / U-07 観測記録 v0.1

**文書番号:** JARVIS-HGJ03-EV-002
**調査日:** 2026-08-04
**状態:** **観測記録のみ(裁定なし・採用判断なし・設計変更なし・実装なし)**
**Decision Ledger 登録:** なし

## 0. 調査条件(きむら博士指示)

| 条件 | 遵守状況 |
|---|---|
| 実装変更禁止 | 遵守(コード変更ゼロ) |
| 設定変更禁止 | 遵守(読み取りのみ) |
| 裁定禁止 | 遵守(採否・優劣・推奨を記載しない) |
| 接続先・権限・イベント経路のみ観測 | 本文書 |
| Unknown 保持 | §5 |

**対象:** U-09(`phi-os/extension` → MoCKA 接続経路)/ U-07(`tools/mocka-bridge/extension` 内容)

---

## 1. U-09: `phi-os/extension` → MoCKA 接続経路 — **発見した**

前回調査(`JARVIS_HGJ03_EVIDENCE_M4_M5_v0.1.md` U-09)で「本調査範囲で未発見」としていた経路を、
`extension/` 配下の全 `.js` に対する `fetch` / `http` / `sendMessage` grep により特定した。

### 1.1 完全な経路(Confirmed / コード実測)

```
claude.ai のページ
   |
   |  content.js(content_scripts, matches https://claude.ai/*)
   v
core/auto-trigger.js:95
   chrome.runtime.sendMessage({ type: 'PHI_COMMIT_DONE', trigger: reason })
   |
   v
background.js:68  (service worker, case 'PHI_COMMIT_DONE')
   |
   |  background.js:70
   |  fetch('http://127.0.0.1:5000/api/phi-os-event', {
   |    method: 'POST',
   |    headers: { 'Content-Type': 'application/json' },
   |    body: { type:'PHI_COMMIT_DONE', source:'phi-os',
   |            workspace: msg.workspace, payload: msg.payload,
   |            timestamp: new Date().toISOString() }
   |  })
   |  ※ catch で握りつぶす: '[PHI OS BG] MoCKA送信失敗(オフライン時は無視)'
   v
app.py:3405  @app.route("/api/phi-os-event", methods=["POST"])
   |
   |  from interface.db_helper import write_event, get_next_event_id
   |  write_event({...})          ← channel 引数なし
   v
interface/db_helper.py:135  write_event(row, channel=None)
   |
   |  tag_source(None) → _source = 'direct_violation'
   |  INSERT OR IGNORE INTO events (...)
   v
events テーブル
```

### 1.2 この経路の Governance 上の性格(観測、事実のみ)

**app.py 自身が、この呼び方を禁止事項として明記している**(app.py:266-269、Confirmed):

> \# TODO_347: Gate直叩きの同期書き込みは廃止。Local Bufferへpushし
> \# chat応答等のレイテンシに影響を与えず、非同期でGate経由でSQLiteへ永続化する
> \# **(禁止事項: db_helper.write_event()の直接呼び出し)**。
> get_buffer().push(row)

`interface/db_helper.py:135` の docstring も同旨(Confirmed):

> Phase5-1 Gate Enforcement: 通常イベントはGate(`get_buffer().push()`)経由で
> 書き込むべきであり、本関数の直接呼び出しはGate Policy(gate_policy.py)で
> 許可されたchannel(bootstrap/maintenance/migration/restore/recovery)の
> 場合のみ正当化される。**channel未指定の呼び出しは監査上 'direct_violation' として検出される**。

すなわち **`/api/phi-os-event` は `process_event()` を経由せず、`channel` 指定もない。**

### 1.3 ただし発火実績はない(Confirmed / DB 実測)

| 観測 | 実測値 |
|---|---|
| `events._source = 'direct_violation'` | **0件** |
| `who_actor LIKE '%phi-os%'` | 7件、最新 **2026-06-11**、いずれも `_source='legacy'`、内容は `phi-os-test-poll-00X` |

**すなわち、この経路は構造として存在するが、Gate 迂回の書き込みが実際に発生した記録はない。**

### 1.4 付随観測: Connected Mode 判定の宛先不一致(Confirmed)

`extension/core/state-store.js:30`:

```javascript
const res = await fetch('http://localhost:5000/b/health', { signal: AbortSignal.timeout(500) });
_modeCache = res.ok ? 'CONNECTED' : 'STANDALONE';
```

実測(同日):

| リクエスト | 応答 |
|---|---|
| `GET http://127.0.0.1:5000/b/health` | **404** |
| `GET http://127.0.0.1:5003/b/health` | **200**(`mocka_runtime_b.exe`) |

`/b/health` は **Runtime B(:5003)のエンドポイント**であり、`app.py`(:5000)には存在しない。
`ui/options.js` の UI 文言は「Connected Mode は localhost:5000 の MoCKA サーバー起動時に自動有効化されます」
と説明しているが、判定に使う `/b/health` は :5000 で 404 を返す。

**観測:** 現在の構成では `detectMode()` は `res.ok === false` により **STANDALONE を返す**と読める。
ただし本調査では拡張を実行していないため、実際の動作は **Unknown**(U-11)。

### 1.5 `phi-os/extension` の MoCKA 向け読み取り経路(Confirmed)

| ファイル:行 | 宛先 | 用途 |
|---|---|---|
| `background.js:70` | `POST http://127.0.0.1:5000/api/phi-os-event` | commit 完了通知(§1.1) |
| `core/state-store.js:30` | `GET http://localhost:5000/b/health` | Connected/Standalone 判定(§1.4) |
| `ui/options.js:281` | `GET http://127.0.0.1:5000/api/phi-os-status` | UI 表示用ステータス |

`extension/` 配下に、これ以外のネットワーク送信は発見できなかった
(調査範囲: `extension/` 配下全 `.js` に対する `fetch(` / `XMLHttpRequest` / `localhost` / `127.0.0.1` /
`https?://` / `connectNative` / `sendNativeMessage` の grep)。

---

## 2. U-07: `tools/mocka-bridge/extension` 内容確認

### 2.1 基本情報(Confirmed)

| 項目 | 値 |
|---|---|
| path | `C:\Users\sirok\MoCKA\tools\mocka-bridge\extension` |
| Extension ID | `doapadhfedmognoilmjieekfhijeadnf` |
| manifest name | **"MoCKA Bridge"** |
| version | **2.4** |
| manifest_version | 3 |
| permissions | `tabs`, `scripting`, `contextMenus`, `notifications`, `storage`, `clipboardRead` |
| background | `background.js`(service worker) |
| content_scripts | `content.js` → `https://claude.ai/*` / `mocka_perplexity.js` → `perplexity.ai` |
| ディレクトリ最終更新 | 2026-07-23 08:51(`content.js` は 2026-07-23 08:50) |

`host_permissions`(12件、Confirmed):
`http://127.0.0.1:5000/*`, `http://localhost:5000/*`, `http://127.0.0.1/*`,
`https://claude.ai/*`, `https://chatgpt.com/*`, `https://*.openai.com/*`,
`https://gemini.google.com/*`, `https://*.microsoft.com/*`, `https://genspark.ai/*`,
`https://perplexity.ai/*`, `https://*.perplexity.ai/*`, `https://www.perplexity.ai/*`

### 2.2 接続先エンドポイント一覧(Confirmed / コード実測)

**すべて MoCKA 本体(:5000)宛てである。** 外部AI各社サイトへの `fetch` は発見できなかった
(各社サイトへの関与は `chrome.scripting.executeScript` / content script による **DOM 読み取り**)。

| ファイル:行 | メソッド | エンドポイント |
|---|---|---|
| `background.js:14` | GET | `http://127.0.0.1:5000/get_intent/{name}` |
| `background.js:89,101,135,150` | POST | `http://localhost:5000/ask` |
| `background.js:107,119` | POST | `http://localhost:5000/orchestra` |
| `background.js:142,157` | POST | `http://localhost:5000/success` |
| `background.js:193,210` | POST | `http://127.0.0.1:5000/collect` |
| `background.js:244` | — | `http://127.0.0.1:5000` + 可変 `endpoint` |
| `content.js:115` | POST | `http://127.0.0.1:5000/user_voice` |
| `content.js:198,318,360` | GET | `http://127.0.0.1:5000/get_latest_dna` |
| `content.js:266` | GET | `http://127.0.0.1:5000/get_restore_packet_v1` |
| `content.js:303` | GET | `http://127.0.0.1:5000/get_restore_packet` |
| `content.js:483-485` / `turn_counter_patch.js:43-45` | GET | `/public/todo`, `/loop/status`, `/public/events?n=5` |

`background.js:244` は **エンドポイント可変**(`'http://127.0.0.1:5000' + endpoint`)であり、
呼出側が指定した任意パスへ到達しうる。呼出元の網羅は本調査では未実施(**Unknown**、U-12)。

### 2.3 収集内容(Confirmed / コード実測)

| 経路 | 収集対象 |
|---|---|
| `content.js:115` → `/user_voice` | `{ text, url, timestamp }`。claude.ai 上の発話テキスト |
| `background.js:193` → `/collect` | `chrome.scripting.executeScript` でページから `[role] text` 形式に整形した本文(50文字超のとき)。`{ source, text, url, mode:'script', timestamp }` |
| `background.js:210` → `/collect` | content script 経由の **クリップボード取得**(CSPブロックサイト用)。`{ source, text, url, mode:'clipboard', timestamp }` |

### 2.4 書き込み経路の Governance 上の性格(Confirmed / 重要)

`/user_voice`(`app.py:432`)と `/collect`(`app.py:1009`)の永続化方式を追跡した。

```
POST /user_voice
   |
   |  app.py:501  append_event({ what_type:'user_voice', who_actor:'kimura',
   |                             where_component:'claude.ai',
   |                             how_trigger:'chrome_extension_v15',
   |                             channel_type:'chat', ... })
   v
app.py:242  append_event(meta)
   |  ... FIELDNAMES へ正規化 + _sanitize_utf8 ...
   |  app.py:269  get_buffer().push(row)      ← Local Buffer
   v
interface/event_buffer.py
   |  POST http://localhost:5000/api/gate/event/batch
   v
phi_os/event_gate.py  process_buffered_event() → _write()
   v
events / event_signatures
```

`/collect` も同様に `get_buffer().push(...)` を使用する(実測)。

**すなわち `tools/mocka-bridge/extension` の書き込みは Gate を経由している。**

### 2.5 実データによる裏付け(Confirmed / DB 実測)

| 観測項目 | 実測値 |
|---|---|
| `how_trigger = 'chrome_extension_v15'` の event | **753件** |
| 同・最新 | `E20260730_5323194763ee1` / `2026-07-29T23:58:52.303Z` / `who_actor='kimura'` / `where_component='claude.ai'` / **`_source='buffered'`** |
| `where_component='claude.ai'` の最新3件 | いずれも `what_type='user_voice'`、**`_source='buffered'`** |
| `what_type='user_voice'` 全体の `_source` 分布 | `legacy` 7,052 / `buffered` 235 / `new` 44 |

`_source='buffered'` は Local Buffer → Gate batch 経由で書かれたことを示す(`gate_policy.tag_source` 由来)。

**観測:** `legacy` 7,052 件は現行 Gate 経路が導入される以前のデータと読めるが、
その移行時期・経緯は本調査では未確認(**Unknown**、U-13)。

### 2.6 未ロードの設定ファイル(Confirmed)

`tools/mocka-bridge/extension/config.js`(462 bytes、2026-06-09):

```javascript
// MoCKA Gateway — クライアント設定
// Phase1: localhost:5010 / Phase2以降: Cloudflare Workers URL
const MOCKA_CONFIG = {
  BASE_URL:   "https://mocka-api.nsjpkimura-mocka.workers.dev",
  API_KEY:    "OPR-XXXXXXXX",   // X-MoCKA-Key ヘッダー値(プレースホルダ値)
  MODE:       "compact",
  TIMEOUT_MS: 5000,
};
Object.freeze(MOCKA_CONFIG);
```

**観測:**
- `config.js` は `manifest.json` の `content_scripts` にも `background` にも登録されておらず、
  他の `.js` からの参照も発見できなかった(`MOCKA_CONFIG` の出現は `config.js` 自身の2箇所のみ)。
  → **ロードされていないと読める**(実行時検証は未実施、**Unknown** U-14)。
- `BASE_URL` の `mocka-api.nsjpkimura-mocka.workers.dev` は、
  `JARVIS_CAPABILITY_INVENTORY.md` 作成時に参照した既往記録で
  **Legacy(廃止候補、TODO_424)** とされている Worker と同名である(照合は既往記録ベース、本調査では未再検証)。
- `API_KEY` の値は `OPR-XXXXXXXX` であり **プレースホルダ**である(実鍵ではない)。

### 2.7 同ディレクトリ内の非稼働ファイル(Confirmed)

`background.js.bak`(2026-04-09)、`content.js.bak_TODO134`(2026-05-11)、
`content.js.bak_relay_mode`(2026-05-16)、`mataka_patch.js`(144 bytes)、
`turn_counter_patch.js`(2026-06-18)。
`manifest.json` に登録されているのは `background.js` / `content.js` / `mocka_perplexity.js` のみ。
`turn_counter_patch.js` は manifest 未登録だが `content.js:483-485` と同一の3エンドポイント呼出を含む
(重複実装。どちらが有効かは **Unknown**、U-15)。

---

## 3. HAB-D 3実体の比較(観測のみ・評価を含まない)

前回 §3.1 で HAB-D-1 / HAB-D-2 に分離したが、U-07 の結果 **第3の実体**を加える必要がある。

| | **HAB-D-1** | **HAB-D-2** | **HAB-D-3** |
|---|---|---|---|
| 実体 | `phi-os/extension/` | `phi-os/core/` + `phi-os/adapters/` | `tools/mocka-bridge/extension/` |
| 種別 | Chrome 拡張(MV3) | Node/Chrome 両対応 JS モジュール | Chrome 拡張(MV3) |
| 名称 | "PHI OS" v1.0.0 | change-tracker / file-guard / tool-hook | **"MoCKA Bridge" v2.4** |
| Chrome 登録 | あり(`bieancja…`) | なし(拡張ではない) | あり(`doapadhf…`) |
| host_permissions | `claude.ai` のみ | — | **localhost:5000 + 外部AI 9ドメイン** |
| MoCKA 接続 | `POST /api/phi-os-event`(§1.1) | `mocka-bridge.js` → `https://mcp.nsjp.org/mcp` | `POST /user_voice` `/collect` `/ask` `/orchestra` `/success` ほか |
| 書込の Gate 経由 | **経由しない**(`db_helper.write_event` 直呼び) | **Unknown**(MCP 先の処理は未確認) | **経由する**(`append_event` → Local Buffer → `/api/gate/event/batch`) |
| 発火実績(events) | **0件**(`direct_violation` 0) | 未確認 | **753件**(`how_trigger='chrome_extension_v15'`、最新 2026-07-29) |
| RESPONSIBILITY_MAP 記載 | あり(PHI-REG-02(a)) | あり(同上に含まれる) | **なし** |
| 由来 | `DESIGN_v1.md`(2026-06-01) | `CHANGE_TRACKER_README.md`(TODO_144 / TODO_217) | 未特定(**Unknown**、U-16) |

### 3.1 きむら博士の論点への対応(事実のみ)

論点: **「HAB-D 経由の操作が MoCKA Governance Boundary を維持できるか」**

本調査で得られた事実:

| 実体 | Boundary に関する観測事実 |
|---|---|
| HAB-D-1 | 経路は `process_event()` を経由せず、`channel` 未指定の `db_helper.write_event()` を呼ぶ。**app.py 自身がこの呼び方を「禁止事項」と明記している**(app.py:268)。ただし **発火実績は 0件** |
| HAB-D-2 | 接続先は外部公開エンドポイント `https://mcp.nsjp.org/mcp`。認証なし POST に 202(前回調査)。**MoCKA 側での扱いは未確認** |
| HAB-D-3 | `append_event` → Local Buffer → `/api/gate/event/batch` → `process_event` 系。**Gate を経由している**。実データ 753件が `_source='buffered'` |

**本文書はこの3者の優劣・採否を評価しない。** 裁定は Human Gate Finalization の領域である。

---

## 4. 前回記録の更新

| 前回の Unknown | 本調査後 |
|---|---|
| **U-09**(extension → MoCKA 経路) | **解消**。§1.1 に経路を特定。ただし発火実績は 0件 |
| **U-07**(`tools/mocka-bridge/extension` 内容) | **解消**。§2 に記録。**HAB-D-3 として第3の実体に分離** |
| U-01(拡張の有効/無効) | **未解消**(継続 Unknown) |

---

## 5. Unknown(本調査で確定できなかった事項)

| # | Unknown |
|---|---|
| U-01 | 9件の未パック拡張の有効/無効(継続) |
| U-02 | service worker の実稼働(継続) |
| U-11 | `state-store.js` の `detectMode()` が実行時に返す値。コード上は STANDALONE と読めるが拡張を実行していない |
| U-12 | `mocka-bridge/background.js:244` の可変 `endpoint` に渡される値の全体像(呼出元未網羅) |
| U-13 | `user_voice` の `_source='legacy'` 7,052件が書かれた時期・経路と、`buffered` への移行時期 |
| U-14 | `config.js` が実行時にロードされていないことの実測確認(静的 grep のみ) |
| U-15 | `turn_counter_patch.js` と `content.js` の重複実装のうち有効なもの |
| U-16 | `tools/mocka-bridge/extension` の設計文書・由来 Decision(RESPONSIBILITY_MAP 未記載) |
| U-17 | `tools/mocka-extension` / `~/mocka_extension` の内容(本調査対象外) |
| U-18 | `mocka-bridge.js`(HAB-D-2)が `mcp.nsjp.org` へ送ったデータの MoCKA 側での扱い |
| U-19 | `audit_violations` の NEW 6件(2026-07-22〜23、`write_path.runtime.generator`)と、`mocka-bridge/content.js` の更新日(2026-07-23 08:50)の関係。**日付が近接しているという観測のみ。因果は未確認** |

---

## 6. 本調査で行っていないこと

- 採用判断・優劣評価・推奨(**裁定禁止**)
- 設計変更・実装・設定変更(**禁止**)
- 拡張の実行・有効化・再読み込み
- `tools/mocka-extension` / `~/mocka_extension` の内容調査(U-17)
- 外部エンドポイントへの追加リクエスト(前回の GET/POST 以降、新規送信なし)

---

## Knowledge Lineage

**Document:** JARVIS_HGJ03_EVIDENCE_U09_U07_v0.1.md
**Status:** 観測記録(裁定なし、Decision Ledger 未登録)
**Created:** 2026-08-04
**Origin:** きむら博士指示「HG-J03追加証拠調査。対象: U-09 extension → MoCKA 接続経路 / U-07 tools/mocka-bridge/extension 内容確認。条件: 実装変更禁止・設定変更禁止・裁定禁止・接続先/権限/イベント経路のみ観測・Unknown保持」
**Parent Documents:**
- `docs/governance/JARVIS_HGJ03_EVIDENCE_M4_M5_v0.1.md`(U-09 / U-07)
- `docs/governance/JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md`
- `docs/governance/JARVIS_CONSTITUTION_DRAFT.md`(§7.1 HG-J03)
**Primary Evidence:**
`PlanningCaliber/workshop/phi-os/extension/{background.js,content.js,core/auto-trigger.js,core/state-store.js,ui/options.js}`、
`tools/mocka-bridge/extension/{manifest.json,background.js,content.js,config.js,turn_counter_patch.js,mocka_perplexity.js}`、
`app.py`(L242 `append_event` / L266-269 禁止事項コメント / L432 `/user_voice` / L1009 `/collect` / L3405 `/api/phi-os-event`)、
`interface/db_helper.py`(L42 `CSV_FIELDNAMES` / L135 `write_event`)、`interface/event_buffer.py`、
`phi_os/event_gate.py`、`data/mocka_events.db`(`events` 実測)、HTTP 実測(`:5000/b/health` 404 / `:5003/b/health` 200)
**Affected Components:** なし(読み取りのみ。コード・設定の変更ゼロ)
**Revision History:**
- R1(2026-08-04): 新規作成。U-09 経路を特定、U-07 を HAB-D-3 として分離。
  Unknown を U-11〜U-19 として追加保持。裁定・採用判断・設計変更・実装のいずれも行っていない。

# JARVIS HG-J03 追加証拠調査 — M-4 / M-5 観測記録 v0.1

**文書番号:** JARVIS-HGJ03-EV-001
**調査日:** 2026-08-04
**状態:** **観測記録のみ(裁定なし・採用判断なし・設計変更なし・実装なし)**
**Decision Ledger 登録:** なし

## 0. 調査条件(きむら博士指示)

| 条件 | 遵守状況 |
|---|---|
| 実装変更禁止 | 遵守(コード・設定ファイルの変更ゼロ) |
| 設定変更禁止 | 遵守(`.claude/mocka_config.json` 等を読み取りのみ) |
| 裁定禁止 | 遵守(採否・優劣・推奨を記載しない) |
| 観測結果のみ記録 | 本文書 |
| Unknown 保持 | §4 に明示 |

**対象:**
- **M-4**: Chrome Extension 実体確認 — 設計資産なのか現行 Runtime なのかの区別
- **M-5**: `https://mcp.nsjp.org` 到達性・認証要件 — HAB-D を「実行境界」として扱えるかの確認

---

## 1. M-4: Chrome Extension 実体確認

### 1.1 結論(観測)

**PHI OS 拡張は Chrome に未パック拡張として登録されている。設計資産ではなく、登録済みの実体である。**
ただし **有効/無効の別、および service worker が現に稼働しているかは確認できていない(Unknown、§4)。**

### 1.2 登録の一次証拠(Confirmed)

出典: `C:\Users\sirok\AppData\Local\Google\Chrome\User Data\Default\Secure Preferences`
→ `extensions.settings`(43件)

| 項目 | 値 |
|---|---|
| Extension ID | `bieancjajjieckhmgkmcpigpahodiodb` |
| path | `C:\Users\sirok\MoCKA\PlanningCaliber\workshop\phi-os\extension` |
| location | `4` |
| `active_permissions.api` | `['storage', 'tabs', 'sidePanel']` |
| `active_permissions.explicit_host` | `['https://claude.ai/*']` |
| `state` | `None` |
| `was_installed_by_default` | `False` |

`active_permissions` が記録されていることは、**Chrome が当該拡張の権限を実際に付与した状態にある**ことを示す
(付与前であればこの構造は生成されない)。

**方法上の注意(記録):** 初回の走査で `Preferences` の `extensions.settings` を参照し「0件」を得たが、
これは **キーパスの誤り**であった。現行 Chrome では `Secure Preferences` 側に格納されている。
`Preferences.extensions` の実キーは `alerts / chrome_url_overrides / commands / cws_info_fetch_error_timestamp /
cws_info_timestamp / enterprise_promotion / install_signature / last_chrome_version / pinned_extensions / theme` であり
`settings` を含まない(Confirmed)。**「0件」を「未インストール」と結論しなかった。**

### 1.3 同一プロファイル内の未パック拡張 全9件(Confirmed / 重要)

`location=4` のエントリを全列挙した。**うち7件が MoCKA エコシステム配下である。**

| # | Extension ID | path |
|---|---|---|
| 1 | `bieancjajjieckhmgkmcpigpahodiodb` | `MoCKA\PlanningCaliber\workshop\phi-os\extension` |
| 2 | `lbjcmlkcjgjibcmlaokldopjokajjlgc` | `MoCKA\PlanningCaliber\workshop\Orchestra_Project\extension` |
| 3 | `okocleheboabgenhlhliingbpjlkmpcf` | `MoCKA\PlanningCaliber\workshop\Relay_Project\extension` |
| 4 | `nheoiflmnjkgobnahglbbeoihaddacnp` | `MoCKA\PlanningCaliber\workshop\memory\extension` |
| 5 | `kbmliimnlfemkkijfbjbjepiilnihpib` | `MoCKA\PlanningCaliber\workshop\seo-os\extension` |
| 6 | `doapadhfedmognoilmjieekfhijeadnf` | `MoCKA\tools\mocka-bridge\extension` |
| 7 | `impamkjmlflhhjaabhaenkgmnmpflobd` | `MoCKA\tools\mocka-extension` |
| 8 | `endlgfdpmpobmjbcnjjfojdicmlbknlg` | `C:\Users\sirok\mocka_extension` |
| 9 | `kaojcdljbbamckcnhgbcclnicpjaalfi` | `X:\down\NTP\FCK_chromeExt_v1.1`(MoCKA 配下ではない) |

**観測:**
`DESIGN_v1.md` §1 は PHI OS を「Chrome 拡張機能群(Orchestra / Relay / Memory / Prism 等)の共有神経系」と定義している。
そのうち **Orchestra / Relay / Memory の3拡張は実際に登録されている**(#2/#3/#4)。
**Prism は `location=4` の一覧に存在しない。**

`PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1.md` の PHI-REG 対応表は
PHI-REG-02(a) として `phi-os/extension/, core/, adapters/` のみを挙げており、
**#6〜#8 の3拡張(`tools/mocka-bridge/extension`, `tools/mocka-extension`, `~/mocka_extension`)は
同表に記載がない。**

### 1.4 権限範囲の比較(Confirmed)

| Extension | `explicit_host` |
|---|---|
| `phi-os/extension` | `https://claude.ai/*` のみ |
| `tools/mocka-bridge/extension` | `http://127.0.0.1/*`, `http://127.0.0.1:5000/*`, `http://localhost:5000/*`, `https://claude.ai/*`, `https://chatgpt.com/*`, `https://*.openai.com/*`, `https://gemini.google.com/*`, `https://*.microsoft.com/*`, `https://genspark.ai/*`, `https://perplexity.ai/*`, `https://*.perplexity.ai/*`, `https://www.perplexity.ai/*` |
| `~/mocka_extension` | `https://*.copilot.microsoft.com/*`, `https://*.google.com/*`, `https://*.perplexity.ai/*` |

`tools/mocka-bridge/extension` の `active_permissions.api` は
`['clipboardRead', 'contextMenus', 'notifications', 'storage', 'tabs', 'scripting']`。

**観測:** `tools/mocka-bridge/extension` は **localhost:5000(MoCKA 本体)と外部AI各社サイトの両方**に
明示的ホスト権限を持ち、`scripting` / `clipboardRead` を保有している。
`phi-os/extension` は `claude.ai` のみで、localhost への権限を持たない。

### 1.5 `phi-os/extension` の manifest 実測(Confirmed)

```
manifest_version : 3
name             : "PHI OS"
version          : "1.0.0"
description      : "PHI OS - Persistent History Interface for claude.ai"
permissions      : storage, tabs, sidePanel
host_permissions : https://claude.ai/*
background       : service_worker = background.js
content_scripts  : matches https://claude.ai/*, js=content.js, run_at=document_idle
side_panel       : ui/sidepanel.html
externally_connectable : ids=["*"], matches=["https://claude.ai/*"]
```

**観測 — "PHI OS" の第3の展開形:**

| 出典 | 展開形 |
|---|---|
| `PHI_OS_CONSTITUTION_v1.md` | Persistent History **Intelligence** OS |
| `DESIGN_v1.md`(2026-06-01) | Platform Hub **Integration** OS |
| **`extension/manifest.json`(実装)** | **Persistent History **Interface** for claude.ai** |

`PHI_OS_CONSTITUTION_v1.md` 末尾の「追加記録: PHI-OS名称の二義性について」(2026-07-25)は
前2者のみを記録している。**manifest の第3の展開形は同追記に含まれていない。**

### 1.6 ディレクトリ構成の実測 — RESPONSIBILITY_MAP の記載との差(Confirmed / 重要)

`PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1.md` は PHI-REG-02(a) の実体を
`phi-os/extension/`, `core/`, `adapters/` の3つと記載している。
しかし実測の結果、**`extension/` 配下と repo 直下の `core/` `adapters/` は別の資産である。**

| ディレクトリ | 内容 | 実行環境 |
|---|---|---|
| `phi-os/extension/core/` | `event-bus.js` `state-store.js` `schema-registry.js` `permission-manager.js` `auto-trigger.js` `commit-engine.js` `restore-engine.js` `i18n.js` | **Chrome 拡張**(`chrome.storage.local` を直接使用) |
| `phi-os/extension/adapters/` | `phi-adapter.js` `orchestra-adapter.js` `relay-adapter.js` `memory-adapter.js` `_template-adapter.js` | Chrome 拡張 |
| **`phi-os/core/`**(repo直下) | `change-tracker.js` `change-record-store.js` `file-guard.js` | `chrome.storage.local` + **Node.js 向けメモリ fallback** の両対応 |
| **`phi-os/adapters/`**(repo直下) | **`mocka-bridge.js`** `tool-hook.js` | `mocka-bridge.js` は **`import fs from 'node:fs'`** を使用 |

**Confirmed な事実:**
1. **`mocka-bridge.js` は `extension/` 配下に存在しない。**
   `extension/` 内での言及は `extension/core/permission-manager.js:102` のコメント1行のみ
   (「不正アクセスを mocka-bridge.js 経由で記録する」)で、import は存在しない。
2. `mocka-bridge.js` は `node:fs` を import しており、`_CONFIG_PATH` としてローカル絶対パスを
   `fs.readFileSync` で読む。
3. `mocka-bridge.js` を import しているのは `phi-os/core/change-tracker.js:6` と
   `phi-os/core/file-guard.js:8` の2つのみ。
4. repo 直下 `core/` + `adapters/` は `CHANGE_TRACKER_README.md`(E20260603_060 / TODO_144 / 2026-06-03)が
   定義する **change-tracker(変更前後強制記録制度)** の構成であり、
   `adapters/tool-hook.js` は **TODO_217「PostToolUse 自動フック」**である。

**観測:** すなわち §3.4bis(Decision Package)で観測した `https://mcp.nsjp.org/mcp` 接続は、
**Chrome 拡張バンドルの経路ではなく、change-tracker / file-guard / PostToolUse フック側の経路**である。
`phi-os/extension/` 自身が MoCKA へ接続する経路は、本調査では発見できなかった
(調査範囲: `extension/` 配下の全 `.js` に対する `mocka-bridge` / `node:` / `require(` grep)。

### 1.7 Chrome の稼働状態(Confirmed)

| 項目 | 実測 |
|---|---|
| `chrome.exe` プロセス数 | **37** |
| 最古プロセス起動時刻 | **2026-08-04 14:06:03**(ローカル時刻) |

---

## 2. M-5: `https://mcp.nsjp.org` 到達性・認証要件

### 2.1 実測結果(Confirmed)

| リクエスト | 結果 |
|---|---|
| `GET https://mcp.nsjp.org/` | **404**(応答時間 1.42s、remote_ip `104.21.89.41`) |
| `GET https://mcp.nsjp.org/mcp` | **200** |
| `POST https://mcp.nsjp.org/mcp`(`Content-Type: application/json`、body `{}`、**認証ヘッダなし**) | **202** |

### 2.2 認証要件についての観測

**認証ヘッダを一切付与しない POST が HTTP 202 を返した。**

比較(いずれも同日実測):

| エンドポイント | 認証なしアクセス |
|---|---|
| `https://mcp.nsjp.org/mcp` | POST → **202** |
| `http://127.0.0.1:5010/`(`gateway.py`) | GET → **401** `X-MoCKA-Key header missing` |

**Unknown(断定しない):**
- 202 は「受理」を意味するステータスだが、**受理後に何が行われたかは本調査では確認していない**。
  破棄された可能性、後段で認証が課される可能性、内容不正として無視された可能性のいずれも排除できない。
- `mcp.nsjp.org` と `gateway.py`(:5010)が同一の実体かどうかは未確認。
- 認証方式(ヘッダ名・トークン形式)は未確認。

### 2.3 副作用の確認(Confirmed)

POST プローブ後に MoCKA の Event Ledger を確認した。

| 項目 | 実測 |
|---|---|
| `events` 総数(プローブ後) | 19,059 |
| プローブ時刻(2026-08-04 06:0x UTC)前後の新規 event | **プローブ由来の event は無し**。直近6件はすべて本セッションの `Claude-opus-5` による MCP 書込と `script:mocka_git_safe_commit` による自動同期 |

**すなわち、本プローブは MoCKA の Event Ledger に記録を生成していない。**

### 2.4 プローブ手法の記録(透明性のため明記)

- 送信したのは **空 JSON オブジェクト `{}` のみ**。認証情報・個人情報・MoCKA のデータは一切送信していない。
- 設定ファイル・環境変数は読み取りのみで変更していない。
- `GET` に加えて `POST` を1回実施した。これは「認証要件の確認」には認証なし要求の応答を見る必要があったためである。
  結果として **202 を返す = 認証なしで受理される**という観測が得られた。

---

## 3. HG-J03 の判断材料としての位置づけ(観測のみ)

きむら博士が提起した論点
**「HAB-D を採用するか、だけでなく HAB-D 経由の操作が MoCKA Governance Boundary を維持できるか」**
に対応する観測を、事実のみ整理する。**評価・採否は記載しない。**

### 3.1 「HAB-D」が指す実体が単一でないことの観測

`PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1.md` が PHI-REG-02(a) として括った
`extension/` + `core/` + `adapters/` は、実測では **2つの独立した資産**である。

```
[HAB-D-1] phi-os/extension/            … Chrome拡張。claude.ai のみ。localhost 権限なし。
                                          MoCKA への接続経路は本調査で未発見
[HAB-D-2] phi-os/core/ + adapters/     … change-tracker / file-guard / PostToolUse フック
                                          (TODO_144 / TODO_217)。node:fs 依存。
                                          mocka-bridge.js が https://mcp.nsjp.org/mcp へ接続
```

Decision Package §3.4bis で観測した外部エンドポイント接続は **HAB-D-2 の性質**であり、
HAB-D-1(Chrome拡張)の性質ではない。

### 3.2 Governance Boundary に関わる観測(事実のみ)

| # | 観測 | 出典 |
|---|---|---|
| B-01 | `phi_os/event_gate.py: process_event()` は自らを「これ以外に events 保存を行う経路は制度上存在しない」と宣言 | コード実測 |
| B-02 | `JARVIS_CONSTITUTION_DRAFT.md` §4.1 は write を `process_event()` 経由のみと規定(**【起案】=未裁定**) | 同 Draft |
| B-03 | HAB-D-2 の接続先 `https://mcp.nsjp.org/mcp` は、認証なし POST に 202 を返す | 本調査 §2.1 |
| B-04 | `gateway.py`(:5010)は認証なしで 401 を返す。両者の認証要件は同一でない | 本調査 §2.2 |
| B-05 | `app.py:3405` `/api/phi-os-event` は `db_helper.write_event()` を channel 未指定で呼び、`process_event()` を経由しない | コード実測(Decision Package §3.4) |
| B-06 | ただし `events._source` の `direct_violation` は **0件**であり、B-05 の経路が発火した実績はない | DB 実測 |
| B-07 | `mocka-bridge.js` は MoCKA 未接続時に `RecordStore` へフォールバックする設計(`import { RecordStore } from '../core/change-record-store.js'`) | コード実測 |
| B-08 | `tools/mocka-bridge/extension` は `localhost:5000` と外部AI各社への明示的ホスト権限、および `scripting` / `clipboardRead` を保有 | Secure Preferences 実測 |

### 3.3 M-4 / M-5 の当初目的に対する到達度

| 目的(博士提示) | 到達度 |
|---|---|
| M-4「設計資産なのか、現行 Runtime なのかを区別する」 | **区別できた**: `phi-os/extension` は Chrome に登録済みの実体であり、単なる設計資産ではない。Orchestra / Relay / memory の各拡張も同様に登録済み。ただし**有効/無効・稼働中か否かは Unknown**(§4) |
| M-5「HAB-D を『実行境界』として扱えるか確認する」 | **部分的に到達**: エンドポイントは到達可能(GET 200 / POST 202)。ただし**認証なしで 202 を返す**という観測が得られた一方、202 の意味・後段処理・認証方式は Unknown(§4) |

---

## 4. Unknown(本調査で確定できなかった事項)

| # | Unknown | 理由 |
|---|---|---|
| U-01 | 9件の未パック拡張の **有効/無効** | `Secure Preferences` の `state` が43件すべて `None`。有効フラグは別の格納先にあると推測されるが未特定 |
| U-02 | `phi-os/extension` の service worker が現に稼働しているか | 登録の記録と稼働は別。実行中の service worker の確認は行っていない |
| U-03 | `location=4` の Chrome 内部的な正確な意味 | `location` 分布は `1:16 / None:9 / 4:9 / 5:8 / 10:1`。`4` が未パック拡張のパスと一致することは観測したが、Chrome の enum 定義は本調査で検証していない |
| U-04 | `https://mcp.nsjp.org/mcp` の 202 が示す後段処理 | 受理後の挙動を確認していない |
| U-05 | `mcp.nsjp.org` と `gateway.py`(:5010)/ `mocka_mcp_server.py`(:5002)の対応関係 | 未確認 |
| U-06 | `mcp.nsjp.org` の認証方式(ヘッダ名・トークン形式) | 未確認 |
| U-07 | `tools/mocka-bridge/extension` / `tools/mocka-extension` / `~/mocka_extension` の内容と、PHI-REG 体系上の位置 | RESPONSIBILITY_MAP に記載がなく、本調査でも中身を読んでいない |
| U-08 | Prism 拡張の所在 | `DESIGN_v1.md` は Prism を挙げるが `location=4` 一覧に無い。`core_kernel/prism/`(Python、外部import 0件)との関係も未確認 |
| U-09 | `phi-os/extension` から MoCKA への接続経路の有無 | `extension/` 配下に発見できなかった。**「存在しない」ではなく「本調査範囲で未発見」** |
| U-10 | Chrome の 37 プロセスのうち、どの拡張の service worker が含まれるか | 未確認 |

---

## 5. 本調査で行っていないこと

- 採用判断・優劣評価・推奨(**裁定禁止**)
- 設計変更・実装(**禁止**)
- 設定ファイル・環境変数の変更(**禁止**)
- 拡張の有効化/無効化・再読み込み
- `mcp.nsjp.org` への認証付きアクセス、意味のあるペイロードの送信
- `tools/mocka-bridge/extension` 等3拡張の内容調査(U-07)

---

## Knowledge Lineage

**Document:** JARVIS_HGJ03_EVIDENCE_M4_M5_v0.1.md
**Status:** 観測記録(裁定なし、Decision Ledger 未登録)
**Created:** 2026-08-04
**Origin:** きむら博士指示「HG-J03追加証拠調査を実施。対象: M-4 Chrome Extension 実体確認 / M-5 mcp.nsjp.org 到達性・認証要件確認。条件: 実装変更禁止・設定変更禁止・裁定禁止・観測結果のみ記録・Unknown保持」
**Parent Documents:**
- `docs/governance/JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md`(§10.3 M-4 / M-5)
- `docs/governance/JARVIS_CONSTITUTION_DRAFT.md`(§7.1 HG-J03)
**Primary Evidence:**
`C:\Users\sirok\AppData\Local\Google\Chrome\User Data\Default\Secure Preferences`(`extensions.settings` 43件)、
`PlanningCaliber/workshop/phi-os/extension/manifest.json`、
`PlanningCaliber/workshop/phi-os/{extension/core,extension/adapters,core,adapters}/`、
`PlanningCaliber/workshop/phi-os/DESIGN_v1.md`、`CHANGE_TRACKER_README.md`、
`adapters/mocka-bridge.js`、`adapters/tool-hook.js`、`core/change-tracker.js`、`core/file-guard.js`、
`C:\Users\sirok\MoCKA\.claude\mocka_config.json`、
`https://mcp.nsjp.org`(HTTP 実測)、`data/mocka_events.db`(副作用確認)、`Get-Process chrome`
**Affected Components:** なし(読み取りのみ。コード・設定の変更ゼロ)
**Revision History:**
- R1(2026-08-04): 新規作成。M-4 / M-5 の観測を記録。Unknown を U-01〜U-10 として保持。
  裁定・採用判断・設計変更・実装のいずれも行っていない。

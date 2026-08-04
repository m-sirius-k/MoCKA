# JARVIS Human Gate Decision Package v0.1
## HG-J01 〜 HG-J04 裁定準備資料

**文書番号:** JARVIS-HGP-001
**作成日:** 2026-08-04
**状態:** **裁定待ち(Human Gate Finalization 未実施)**
**Decision Ledger 登録:** なし
**実装:** なし(コード変更・新規Runtime作成・HAB実装・MCP拡張・Skill Layer実装のいずれも行っていない)

---

## 0. 本 Package の性格

### 0.1 出力構造の制約【継承】

`mocka_human_gate_decision_definition_v1.md` §6 に従い、
**本文書は `decision` フィールドを一切含まない。**

同 §2.1.2 の定義により、本文書が提供するのは以下のみである。

- **判断材料**(評価結果・依存構造・選択肢の列挙)
- **観測**(`recommended_note` は「推奨ではなく観測」と同 §6 が定義)

**推奨・優劣評価・採用すべき案の提示は行わない。**
APPROVE/HOLD/REJECT/DEFER の確定はきむら博士本人(Human Gate Finalization)のみが行う。

### 0.2 Draft のレビュー対象化について

本 Package の提出をもって
`docs/governance/JARVIS_CONSTITUTION_DRAFT.md` はレビュー対象となる。
ただし同文書の Status を DRAFT から変更する行為自体が Human Gate の裁定事項(HG-J09)であるため、
**本 Package では Status を変更しない。**

レビュー範囲は §6 に整理した。

### 0.3 証拠ラベル

| ラベル | 意味 |
|---|---|
| **Confirmed** | 本 Package 作成時に一次データ(コード本文・DB実測・ファイル実在)で直接確認した |
| **Active Decision** | Decision Ledger に status=Active で登録済み |
| **Unknown** | 一次資料が存在せず確定できない |

---

## 1. 現在状態

| 項目 | 状態 |
|---|---|
| Phase 0(現状調査) | 完了。成果物5文書(`docs/audits/JARVIS_*.md`、untracked) |
| Phase 1(制度定義) | 完了。`docs/governance/JARVIS_CONSTITUTION_DRAFT.md`(untracked、未裁定) |
| **Human Gate Finalization** | **待機中 — 本 Package が対象** |
| Phase 2(HAB境界確定) | 未開始 |
| 実装 | **禁止継続**(JARVISコード / MCP拡張 / HAB実装 / Skill Layer のいずれも未着手) |

---

## 2. 判断対象と依存構造

### 2.1 判断対象

| ID | 判断事項 |
|---|---|
| HG-J01 | `ジャビス.md` を JARVIS の定義出典(憲法上の起点)として採用するか |
| HG-J02 | JARVIS の帰属 Institution と Authority 上の位置 |
| HG-J03 | "PHI-HAB" が指す対象の確定 |
| HG-J04 | JARVIS が接続する Human Gate の実体の確定 |

### 2.2 依存構造(観測)

```
        [DC_20260729_009 Authority Flow = Pending Resolution]
                          |
                          | 未解決のまま
                          v
                       HG-J02  ← 依存先が Pending のため単独で確定できない
                          ^
                          |
   HG-J03 ──────┐        |
  (PHI-HAB定義) │        |
                v        |
             HG-J01 ─────┘
          (原典採用)
                ^
                |
             HG-J04
        (Human Gate接続先)
```

### 2.3 依存の内容

| 依存 | 内容 |
|---|---|
| HG-J03 → HG-J01 | `ジャビス.md` を原典採用すると、同文書の PHI-HAB 定義(HAB-C)も同時に採用される可能性がある。HAB-C は Active な `DC_20260729_008`(HAB-D)と同語異義であるため、**J03 を先に確定しないと J01 の採用範囲が定まらない** |
| HG-J04 → HG-J01 | `ジャビス.md` §5 の Context Compiler フローは Human Gate を内包している。接続先 Gate が未確定のまま原典採用すると、内包された Human Gate がどの実体を指すか不定になる |
| HG-J02 ← DC_20260729_009 | PHI-Con/PHI-Core 間の Authority 階層は Active Decision により **Pending Resolution**。JARVIS の Authority 位置はこの Pending の下流にある |

### 2.4 依存から導かれる順序制約(観測)

きむら博士が提示した順序 `HG-J03 → HG-J04 → HG-J01 → JARVIS仕様確定` は、
上記 2.3 の依存構造と矛盾しない(観測)。

HG-J02 は `DC_20260729_009` の Pending が解けるまで、
**「JARVIS の Authority 位置は未確定」という状態を維持する裁定** 以外の選択肢を持たない可能性がある(§3.2 参照)。

---

## 3. HG-J03: "PHI-HAB" が指す対象の確定

### 3.1 問題

**同一の語 "PHI-HAB" が、2つの異なる対象を指している。** うち1つのみが Active Decision を持つ。

| # | 呼称 | 定義 | 制度状態 | 実体の有無 |
|---|---|---|---|---|
| **HAB-C** | PHI-HAB(構想) | 人間とAIが活動する環境。Context Core / Context Compiler / Context Doctor / AI Adapter | **Decision Ledger 未登録** | **実装なし**(Confirmed) |
| **HAB-D** | PHI-HAB(制度) | PHI-REG-02(a) = Chrome拡張JSハブスタック(Connection/協調層) | **`DC_20260729_008` Active** | **実体あり**(Confirmed) |

参考: 同名衝突は他に2件ある(いずれも JARVIS 接続候補としては挙がっていない)。

| HAB-A | Human Authority Boundary(`mocka_hab_v1_contract.md`) | MoCKA 内部の統治層 | DRAFT |
| HAB-B | HAB spine(`phase8_hab_runtime_integration_v1.md` / `semantic/query_engine/`) | Phase7 A〜E 構造の実行系 | DRAFT・外部import 0件 |

### 3.2 HAB-D の一次証拠(Confirmed)

**Decision:**
`DC_20260729_008`(`[DC-PHI-ID-001]`、approved_at 2026-07-29T01:44:27Z、approved_by きむら博士、status Active)
> PHI-HAB(PHI-REG-02内部区分(a): Chrome拡張JSハブスタック)を、PHI-REG体系に対する
> Responsibility Classification(Alias)として採用する。

**責務分類表**(`docs/audits/PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1.md` L15):
> PHI-REG-02(a) | Chrome拡張JSハブスタック(`PlanningCaliber/workshop/phi-os/extension/`, `core/`, `adapters/`。DESIGN_v1.md原義) | **PHI-HAB**(Connection/協調層) | 高確度

**原義**(`PlanningCaliber/workshop/phi-os/DESIGN_v1.md`、2026-06-01、TODO_186、確定イベント E20260526_044):
> PHI OS（Platform Hub Integration OS）は Chrome 拡張機能群（Orchestra / Relay / Memory / Prism 等）の
> **共有神経系**として機能するサービスワーカー常駐型ランタイム層である。
> UI を持たず、イベントバス・状態ストア・スキーマ管理・権限管理の 4 機能のみを提供する。

**物理実体**(ファイル実在を確認、Confirmed):
- `PlanningCaliber/workshop/phi-os/extension/`(`background.js` `content.js` `manifest.json` `core/` `adapters/` `ui/` `popup.html` ほか)
- `PlanningCaliber/workshop/phi-os/core/`(`change-record-store.js` `change-tracker.js` `file-guard.js`)
- `PlanningCaliber/workshop/phi-os/adapters/`(`mocka-bridge.js` `tool-hook.js`)

### 3.3 HAB-C の一次証拠(Confirmed)

**出典:** `C:\Users\sirok\Desktop\aimd\ジャビス.md` §4(2026-08-04 09:33)
> PHI-HABは単なる記憶庫ではない。
> 役割: 人間とAIが活動する環境 / Context管理 / 知識継承 / AI作業状態管理 / Context品質管理
> 構成要素: Context Core / Context Compiler / Context Doctor / AI Adapter

**制度状態:** Decision Ledger 未登録。
`DC_20260729_001`(Active)は同文書を含む PHI-OS 構想メモの扱いを
**Deferred(将来のPHI-OS全体再設計時に再評価)** と裁定している。

**実装:** Context Compiler / Context Doctor に対応する実装は
MoCKA repo 全体 + `Desktop\aimd\` の範囲で発見できなかった(`JARVIS_GAP_ANALYSIS.md` G-06/G-07)。

### 3.4 HAB-D と MoCKA の接続状態(Confirmed / 重要)

HAB-D は「MoCKA に接続する層」として設計されているため、その接続実態を実測した。

| 観測項目 | 実測結果 |
|---|---|
| 設計文書上の接続先 | `DESIGN_v1.md` §2 図: `sync/mocka-bridge.js → MoCKA localhost:5000 /api/phi-os-event` |
| 実装上の接続先 | `adapters/mocka-bridge.js` → **§3.4bis の R2 訂正を参照**(当初記載「`http://localhost:5002/mcp`(既定値)」は不正確) |
| **差分** | **設計文書(`/api/phi-os-event`)と実装(`/mcp`)でエンドポイント種別が一致しない** |
| MoCKA 側受け口の実在 | `app.py:3405` `@app.route("/api/phi-os-event", methods=["POST"])` は実在(Confirmed) |
| 受け口の書込経路 | `interface.db_helper.write_event()` を **channel 未指定**で呼ぶ |
| `db_helper.write_event()` の性格 | docstring: 「通常イベントはGate(`get_buffer().push()`)経由で書き込むべきであり、本関数の直接呼び出しは…許可されたchannelの場合のみ正当化される。**channel未指定の呼び出しは監査上 `direct_violation` として検出される**」 |
| 実データ上の `direct_violation` | `events._source` 分布に **`direct_violation` は 0件**(Confirmed) |
| `who_actor LIKE '%phi-os%'` の event | 7件。最新は **2026-06-11**、`_source='legacy'`、内容は `phi-os-test-poll-00X` |
| `channel_type='browser_extension'` の event | 128件。最新は **2026-06-01** |

**観測(推奨ではない):**
- `/api/phi-os-event` は経路として実在するが、**現在稼働している形跡がない**(最新の phi-os 由来 event は 2026-06-11 のテストポーリング)。
- したがって「HAB-D が現に MoCKA へ接続している」とは実測から言えない。
- また `/api/phi-os-event` の書込経路は `process_event()` を経由しないため、
  `phi_os/event_gate.py` の「これ以外に events 保存を行う経路は制度上存在しない」という宣言と
  **構造上の不整合がある**(実際に発火した記録は 0件のため、現時点で違反実績はない)。

### 3.4bis 【R2 訂正 2026-08-04】HAB-D の接続先の再実測

§3.4 の初版は `mocka-bridge.js` の接続先を「`http://localhost:5002/mcp`(既定値)」と記載した。
セルフレビューで再読した結果、**これは fallback リテラルであって解決結果ではない**ことが判明した。

**実際の解決順序(コード実測、Confirmed):**

```javascript
// adapters/mocka-bridge.js
const _CONFIG_PATH = 'C:/Users/sirok/MoCKA/.claude/mocka_config.json';   // L9(絶対パス直書き)
const _MOCKA_ENDPOINT_ENV    = process.env.MOCKA_ENDPOINT || null;        // L21-23
const _MOCKA_ENDPOINT_CONFIG = _MOCKA_ENDPOINT_ENV ? null : _readConfigEndpoint();  // L24
const _RESOLVED_ENDPOINT     = _MOCKA_ENDPOINT_ENV || _MOCKA_ENDPOINT_CONFIG;       // L25
if (!_RESOLVED_ENDPOINT) { console.error('[MocKABridge] ERROR: MOCKA_ENDPOINT が未設定です…'); }  // L26-28
export const MOCKA_ENDPOINT = _RESOLVED_ENDPOINT ? `${_RESOLVED_ENDPOINT}/mcp`
                                                 : 'http://localhost:5002/mcp';     // L29
```

**設定ファイルの実測内容(Confirmed):**

```json
// C:/Users/sirok/MoCKA/.claude/mocka_config.json (45 bytes, mtime 2026-07-08)
{ "mcp_endpoint": "https://mcp.nsjp.org" }
```

**訂正後の事実:**

| 項目 | 訂正後 |
|---|---|
| 解決される接続先 | `MOCKA_ENDPOINT` 環境変数が未設定の場合、**`https://mcp.nsjp.org/mcp`**(外部公開エンドポイント) |
| `localhost:5002/mcp` の位置づけ | 設定も環境変数も無い場合の **fallback リテラル**。この分岐に入る場合は直前に `console.error` が出る |
| 設定ファイルのパス | **`C:/Users/sirok/MoCKA/.claude/mocka_config.json` が絶対パスで直書き**(L9、コメントに TODO_218「ngrok URLは mocka_config.json に集約」) |

**観測(推奨ではない):**
- HAB-D の MoCKA 接続は **localhost 内の直結ではなく、外部公開ゲートウェイ経由**として構成されている。
  これは `DESIGN_v1.md` §2 図(`MoCKA localhost:5000 /api/phi-os-event`)とも、
  §3.4 初版の記載(localhost:5002)とも異なる。
- JARVIS の下流に HAB-D を置く場合(J03-A)、その経路は
  **ブラウザ拡張 → 外部公開エンドポイント → MoCKA** となり、
  `JARVIS_CONSTITUTION_DRAFT.md` §4.1 が規定した経路(`process_event()` 経由)との関係の確認が必要になる(観測)。
- 本 R2 は §3.4 の他の行(受け口の実在、`db_helper.write_event` の性格、`direct_violation` 0件、
  phi-os 由来 event の最新日)を変更しない。それらは再確認済みで初版のまま有効。

> **【R3 2026-08-04 — HG-J03 は Evidence Complete へ移行した】**
> きむら博士の指示により、HG-J03 は **Evidence Complete / Decision Required** として閉じた。
> M-4 / M-5 / U-09 / U-07 / U-16 の追加観測により **HAB-D が3系統(HAB-D-1/2/3)に分離**したため、
> 下記 §3.5 の Option J03-A〜D は「HAB-D が単一実体」という前提で書かれており **現状と合わない**。
> **統合後の選択肢(論点1: P-1〜P-4 / 論点2: E-1〜E-5)および確定比較表は
> `docs/governance/JARVIS_HGJ03_EVIDENCE_COMPLETE_v0.1.md` を参照すること。**
> §3.5 は経緯記録として残置する。

### 3.5 選択肢(列挙のみ。優劣評価ではない)【R3: 上記のとおり EVIDENCE_COMPLETE へ移行済み】

| Option | 内容 | この Option を選んだ場合に必要になる後続判断 |
|---|---|---|
| **J03-A** | "PHI-HAB" = HAB-D(`DC_20260729_008` の定義)に一本化し、HAB-C には別名を与える | HAB-C の新名称の決定 / `ジャビス.md` の記述を別名で読み替える運用ルール / JARVIS の下流が「Chrome拡張接続層」となることの是非 |
| **J03-B** | "PHI-HAB" = HAB-C(認知環境)を採用し、HAB-D を別名へ改称する | `DC_20260729_008` の変更または上書き Decision が必要(同 Decision は「PHI-REG-01〜04のIDは維持し、変更・廃止しない」と制約している) |
| **J03-C** | 両者を別概念として併存させ、文脈ごとに完全修飾名を必須とする | 完全修飾名の命名規則の決定 / 既存文書の表記をどこまで遡って統一するか |
| **J03-D** | 確定させず Pending Resolution として保持する | Pending 中に JARVIS 設計を進める場合の暫定表記ルール / 再評価条件(どの Evidence が得られたら確定するか) |

**先例(観測):**
`PHI_OS_CONSTITUTION_v1.md` 末尾「追加記録: PHI-OS名称の二義性について」(2026-07-25、HG-3 承認済み)は、
同種の名称衝突に対し **憲法本体への追記により両者の系譜を記録し、統合しないまま併存させる**
という処理を行った先例である。同追記は
「両者は名称が同一であるが、頭字語の展開・作成日・機能領域がそれぞれ異なり、
現時点では直接の系譜関係はConfirmedされていない(Hypothesisの段階に留まる)」と記している。

### 3.6 この判断が JARVIS 設計に与える影響(観測)

`ジャビス.md` §8 の階層図 `Human → JARVIS → PHI-HAB → Institutional Runtime` は、
J03 の結果により次のいずれかに解釈が固定される。

```
[J03-A を採る場合]              [J03-B を採る場合]
Human                           Human
  ↓                               ↓
JARVIS                          JARVIS
  ↓                               ↓
Chrome拡張接続層                 認知環境(Context管理)
(event-bus/state-store/          (Context Core/Compiler/
 schema-registry/permission)      Doctor/AI Adapter)
  ↓                               ↓
MoCKA                           MoCKA
```

**この2つは同じ設計図ではない。** 前者は既存実体があり未稼働、後者は実体がない。

---

## 4. HG-J04: JARVIS が接続する Human Gate の実体

### 4.1 問題

Human Gate を名乗る実装が **5系統**並存している。
`phi_os/human_gate.py` は自らを「単一の真実」と宣言しているが、実測は宣言と一致していない。

### 4.2 5系統の実測比較(Confirmed)

| # | 実体 | 到達経路 | 状態記録先 | 稼働実績 |
|---|---|---|---|---|
| **HG-1** | `phi_os/human_gate.py` | **CLI のみ**(`governance/human_gate_cli.py` が import)。**HTTP Blueprint `human_gate_bp` は `app.py` に未登録 = HTTP到達不能** | `human_gate_events`(1,779行) | **稼働中**。最新 2026-07-31T09:01:43Z |
| **HG-2** | `app.py` `/decision/approve` `/decision/reject` | HTTP :5000(稼働中) | 未追跡(本 Package では未確認) | route 実在(Confirmed)。呼出実績は未確認 |
| **HG-3** | `governance/mocka_git_safe_commit.py` の Core System File 除外 | git write path | 未コミット状態として保持 | **稼働中**(未コミット4件が実在) |
| **HG-4** | `semantic/query_engine/human_gate.py` + `human_gate_interface.py` | `semantic/` 内部のみ。外部 import 0件 | 未確認 | **未配線** |
| **HG-5** | `governance/human_gate_continuity.py` | `tests/test_human_gate_continuity.py` からのみ参照 | 未確認 | 未配線 |

### 4.3 HG-1 の稼働実績(Confirmed / Phase 0 記載の精緻化)

`human_gate_events` の実データを確認した結果、**HG-1 のモジュール本体は現に使われている**。

| event_id | timestamp | action | request_id |
|---|---|---|---|
| `HG20260731_503234669eed6` | 2026-07-31T09:01:43Z | **approve** | `INC-LIFECYCLE-INC-20260401-001` |
| `HG20260731_422433419af2d` | 2026-07-31T09:00:22Z | submit | `INC-LIFECYCLE-INC-20260401-001` |
| `HG20260708_40524292157c2` | 2026-07-08T01:16:45Z | submit | `TEST_CLI_VERIFY_001` |
| `HG20260623_191616555ac1a` | 2026-06-23T02:03:11Z | submit | `TECH_ALERT_20260623_064709_phi_os_audit` |

2026-07-31 の submit→approve 対は `DC_20260731_007`
(「Human Gate 実装開始承認 — RC-B最小実装(INC Lifecycle)の実装着手を承認」)に対応する。

**Phase 0 記載の訂正:**
`JARVIS_CAPABILITY_INVENTORY.md` §2.4 は HG-1 を
「Implemented / Unwired(HTTP API)」と記載したが、正確には
**モジュール本体は稼働中であり、未配線なのは HTTP Blueprint のみ**である。

> **【R2 精緻化 2026-08-04 — 呼出主体は「CLI」と断定できない】**
> 初版は「**CLI 経路で**稼働中」と記載したが、セルフレビューで呼出元を実測した結果、
> **実際にどのプロセスが 2026-07-31 の submit/approve を発行したかは特定できていない(Unknown)**。
>
> `phi_os.human_gate` の submit/approve を呼ぶコードは以下3系統のみ(Confirmed、`archive/`・`venv/` 除外):
>
> | 呼出元 | 判定 |
> |---|---|
> | `governance/human_gate_cli.py:33` | `--note` 引数を受け付ける(L104/116/121)ため、note=`"RC-B minimal implementation migration"` を**生成可能**。**候補として整合する** |
> | `phi_os/migrate_prevention_queue.py:71,73` | note が固定文字列 `"pseudo-transition from migration, no original PENDING history"` であり、実データの note と**一致しない → 除外できる** |
> | `phi_os/tests/test_human_gate.py` | テスト。`conn` を注入しており本番DBへは書かない |
>
> `event_id` の `HG` prefix は `phi_os/human_gate.py:73`(`f'HG{d}_{micros_of_day:09d}...'`)が唯一の生成元であり、
> **`phi_os/human_gate.py` を経由したことは Confirmed**。
> ただし CLI 経由か、Python 直接呼出かは実データから判別できない。
>
> **訂正後の言明:** 「HG-1 のモジュール本体は本番DBに対して稼働実績がある(Confirmed)。
> 呼出経路は CLI と整合するが断定できない(Unknown)。`migrate_prevention_queue.py` 由来ではない(除外済み)。」

### 4.4 HG-1 の設計上の性格(Confirmed / コード本文)

```
基本原則: PHI-OSがHuman Gateの唯一の状態管理責務を持つ。
          GL7およびApp層はHuman Gate状態を保持しない(本モジュールが単一の真実)。
永続ルール: stateそのものは保存しない。eventのみ保存する。
            stateはevent列から都度再構築する(イベントソーシング)。
STATES:      PENDING / APPROVED / REJECTED / EXPIRED / CANCELED
TRANSITIONS: submit{None} / approve{PENDING} / reject{PENDING} / expire{PENDING}
```

`mocka_human_gate_decision_definition_v1.md` が定める Core/Finalization 2層分離との対応は、
コード上に明示されていない(**Unknown**)。

### 4.5 選択肢(列挙のみ)

| Option | 内容 | この Option を選んだ場合に必要になる後続判断 |
|---|---|---|
| **J04-A** | HG-1(`phi_os/human_gate.py`)を JARVIS の唯一の接続先とする | HTTP Blueprint を登録するか CLI 経路のみとするか(**実装判断のため別 Decision が必要**) / HG-2〜HG-5 の位置づけ整理 |
| **J04-B** | HG-2(`/decision/approve`)を接続先とする | HG-1 の「単一の真実」宣言との矛盾の処理 / HG-2 の状態記録先の特定 |
| **J04-C** | JARVIS 専用の接続先を定めず、既存 Gate への直接接続を禁止し、人間への提示のみとする | JARVIS の出力が Human Gate へ届く経路の定義 / 「提示」と「submit」の境界 |
| **J04-D** | 確定させず、Human Gate 実装整理(5系統の統廃合)を先行させる | 整理作業自体の Scope 定義 / 整理完了までの JARVIS 設計の凍結範囲 |

**観測(推奨ではない):**
- `mocka_human_gate_decision_definition_v1.md` §7 は Core が APPROVE を単独確定することを禁止しており、
  J04-A〜J04-D のいずれを選んでも **JARVIS が確定権を持たない点は変わらない**。
- `JARVIS_CONSTITUTION_DRAFT.md` P-2/P-3/P-14 はこの禁止を継承しており、
  J04 の結果によって変更される条項ではない(観測)。

---

## 5. HG-J01 / HG-J02

### 5.1 HG-J01: `ジャビス.md` を定義出典として採用するか

**問題:**
JARVIS の定義文は `ジャビス.md` §8 にしか存在しない。
一方 `DC_20260729_001`(Active)は同構想の扱いを **Deferred** と裁定している。

**`DC_20260729_001` の原文(該当部分、Confirmed):**
> きむら博士より提示されたPHI-OS構想メモ(Sequence Controller/JARVIS構想、
> **原本はローカルDesktopのためこのセッションからは未検証**)を…
> Deferred(将来のPHI-OS全体再設計時に再評価)

**Phase 0/1 で判明した事実:**
同 Decision が「未検証」とした原本の所在を特定した(`C:\Users\sirok\Desktop\aimd\ジャビス.md`)。
すなわち **Deferred の理由の一つ(原本未検証)は解消している**。
ただし Deferred 裁定自体は Active のまま変更されていない。

**選択肢(列挙のみ):**

| Option | 内容 | 必要になる後続判断 |
|---|---|---|
| **J01-A** | `ジャビス.md` を JARVIS 憲法の起点として正式採用する | `DC_20260729_001` の Deferred を解除する Decision が必要 / 採用範囲(全章か、§8定義のみか) / HAB-C 定義の同時採用の可否(**HG-J03 依存**) |
| **J01-B** | 採用せず、`DC_20260729_001` の Deferred を維持する | JARVIS Constitution Draft §1.1 の定義出典の代替 / Draft 全体の扱い |
| **J01-C** | 部分採用(§8「人間の意図をInstitutional AI環境へ接続するインターフェース」の定義文のみを採用し、§4 PHI-HAB・§5 Context Governance は採用しない) | 部分採用の境界の明文化 / 不採用部分の扱い |
| **J01-D** | 原本を Evidence として Seal した上で、採否は別途とする | Seal 対象範囲 / Seal 後も Deferred が継続することの明示 |

**観測(推奨ではない):**
- `DC_20260729_007`(Active)は「Status/Decision ID/承認日以外の文言追加は事前承認対象」という運用ルールを定めている。
  `ジャビス.md` は MoCKA repo 外(Desktop)にあり、この運用ルールの対象範囲に含まれるかは **Unknown**。
- `ジャビス.md` の mtime は 2026-08-04 09:33 であり、**本 Phase の直前に更新されている**。
  Seal 対象とする場合、どの時点の内容を正典とするかの指定が必要になる(観測)。

### 5.2 HG-J02: JARVIS の帰属 Institution と Authority 上の位置

**問題:**
`PHI_OS_CONSTITUTION_v1.md` 原則7 は
「すべてのArtifactは単一の主Institutionに帰属する」「Institution未所属のArtifactはOrphan状態であり、
制度的操作の対象となれない」と定める(RATIFIED)。

一方 `DC_20260729_009`(Active)は PHI-Con/PHI-Core 間の Authority 関係を
**Option D(条件付き Pending Resolution)= 未解決のまま保持**と裁定している。

**同 Decision の Next Resolution Condition(原文、Confirmed):**
> PHI Authority関係(PHI-Con/PHI-Core間の統治方向)を確定的に定義する
> 新たな一次資料(Evidence)が得られた場合に、本Pendingを再評価する。

**同 Decision の Impact(原文、Confirmed):**
> Planner/Sequence Engine等の実装でAuthority判断が必要になった場合は、
> 既存EvidenceとHuman Gateによる個別判断を行い、その判断は別Decisionとして記録する。

**観測(推奨ではない):**
- 上記 Impact 文は「Authority が Pending でも、個別判断を別 Decision として行う」経路を既に用意している。
  JARVIS の帰属判断がこの「個別判断」に該当するかは **Human Gate の判断事項**である。
- 本 Package は HG-J02 について選択肢を列挙しない。
  理由: 帰属先候補(PHI-Con / PHI-Core / MoCKA / 新設 Institution)のいずれを挙げても、
  その妥当性を評価する Authority 階層自体が Pending であり、
  **選択肢の列挙が Pending の実質的な先取りになる可能性がある**(観測)。
  選択肢を提示すべきか否かを含めて Human Gate の判断を仰ぐ。

---

## 6. JARVIS Constitution Draft のレビュー範囲

`docs/governance/JARVIS_CONSTITUTION_DRAFT.md` のうち、
本 Package の裁定結果に依存する箇所と、独立に評価できる箇所を分離する。

| Draft 章 | 内容 | 依存 | レビュー可否 |
|---|---|---|---|
| 第0章 | 制度的位置づけ・表記規約 | なし | **独立に評価可** |
| 第1章 §1.1 | JARVIS 定義(`ジャビス.md` 由来) | **HG-J01** | J01 確定後 |
| 第1章 §1.2-1.4 | 否定形定義・責務範囲・問いの分担 | 一部 HG-J01 | 部分的に独立評価可 |
| 第2章 | 上位規範からの継承 | なし(既存 Active/RATIFIED の引き写し) | **独立に評価可 — 引き写しの正確性が検証点** |
| 第3章 §3.1-3.2 | 権限境界 A-1〜A-6 / P-1〜P-14 | なし | **独立に評価可** |
| 第3章 §3.3 | 自己適用原則 | なし | **独立に評価可** |
| 第3章 §3.4 | 自動裁定化リスク自己点検表 | なし | **独立に評価可 — HG-J08、起草者の自己申告のため要検証** |
| 第4章 | 接続経路・新規Runtime禁止 | **HG-J04**(§4.1 の Human Gate 経路) | 一部 J04 依存 |
| 第5章 | Context 規律 | **HG-J03**(§5.3 Context Compiler の位置づけ) | 一部 J03 依存 |
| 第6章 | 記録義務 | HG-J06(記録形式) | 原則部分は独立評価可 |
| 第7章 | 未解決問題の記録 | なし(観測の記録) | **独立に評価可** |
| 第8章 | 決めない事項 | なし | **独立に評価可** |
| 第9章 | Human Gate 提示事項 | — | 本 Package が具体化 |
| 第10章 | 発効条件 | HG-J09 | J09 依存 |

**観測:** 第2章(継承)と第3章(権限境界)は本 Package の4件の裁定に依存しない。
すなわち **HG-J03/J04/J01 が未確定でも、JARVIS の禁止事項の妥当性は独立に検証できる**(観測)。

---

## 7. 本 Package で判断しない事項

| # | 事項 | 理由 |
|---|---|---|
| N-1 | HAB の実装 | 禁止事項(博士指示) |
| N-2 | JARVIS コード / MCP 拡張 / Skill Layer 実装 | 禁止事項(博士指示) |
| N-3 | Human Gate 5系統の統廃合の実施 | J04-D を選んだ場合に別途 Scope 定義が必要 |
| N-4 | `/api/phi-os-event` の書込経路の是正 | §3.4 は観測のみ。是正は `DC_20260801_002` HG-1(自動修復禁止)の趣旨に従い別判断 |
| N-5 | `DC_20260730_001/002/003` の ID 重複の修復 | `DC_20260801_002` HG-1 により自動修復禁止。観測記録済み |
| N-6 | `audit_violations` の NEW 6件の処理 | §8 に観測として記録するのみ |
| N-7 | HG-J05〜HG-J09 | 本 Package の対象外(博士指示は HG-J01〜J04) |

---

## 8. 付随観測(判断対象外・記録のみ)

本 Package 作成中に実測した事項のうち、HG-J01〜J04 の判断対象ではないが記録すべきもの。

| # | 観測 | 実測根拠 |
|---|---|---|
| O-1 | `audit_violations` の未処理(status=NEW)が **6件**。すべて 2026-07-22〜23、actor `write_path.runtime.generator`、operation `DIRECT_INSERT` / `DIRECT_UPDATE`、対象 event 3件(`E20260723_56210636180de` / `E20260723_586035295387d` / `E20260723_5032066978763`) | DB 実測 |
| O-2 | `events._source` に `direct_violation` は **0件**。最多は `legacy` 10,662 / `live` 4,434 / `buffered` 2,623 | DB 実測 |
| O-3 | ~~`adapters/mocka-bridge.js` の既定接続先が `localhost:5002/mcp`~~ → **【R2 訂正】解決される接続先は `https://mcp.nsjp.org/mcp`(外部公開)。`localhost:5002/mcp` は設定・環境変数がいずれも無い場合の fallback リテラル。詳細は §3.4bis** | コード実測 + `.claude/mocka_config.json` 実測 |
| O-6 | `adapters/mocka-bridge.js:9` が設定ファイルパス `C:/Users/sirok/MoCKA/.claude/mocka_config.json` を**絶対パスで直書き**している(コメントに TODO_218 の言及あり) | コード実測 |
| O-4 | `who_actor LIKE '%phi-os%'` の event は 7件、最新 2026-06-11。`channel_type='browser_extension'` は 128件、最新 2026-06-01 | DB 実測 |
| O-5 | `PlanningCaliber/workshop/phi-os/` 直下に `adapter/`(単数)と `adapters/`(複数)が **併存**する | ファイル実測 |

---

## 9. 状態

| 項目 | 状態 |
|---|---|
| 本 Package | **提出済み・裁定待ち** |
| HG-J01 | 未裁定 |
| HG-J02 | 未裁定(`DC_20260729_009` Pending の下流) |
| HG-J03 | 未裁定。**【R3】Evidence Complete / Decision Required へ移行**(`JARVIS_HGJ03_EVIDENCE_COMPLETE_v0.1.md`)。技術調査完了・採用判断未実施 |
| HG-J04 | 未裁定。**【R3】次の観測対象**(M-1〜M-3、着手は指示待ち) |
| `JARVIS_CONSTITUTION_DRAFT.md` の Status | **DRAFT のまま変更していない** |
| 実装 | **未着手・禁止継続** |
| 次工程 | Human Gate Finalization(きむら博士本人) |

**本 Package は `decision` フィールドを含まない。**
APPROVE/HOLD/REJECT/DEFER の確定は Human Gate Finalization のみが行う。

---

## 10. 検証記録(セルフレビュー、2026-08-04)

きむら博士の指示(作業候補1〜3: Package レビュー / HG-J03・HG-J04 判断材料確認)に基づき、
本 Package の記載を一次データに対して再検証した。**裁定は行っていない。**

### 10.1 検証項目と結果

| # | 検証項目 | 結果 |
|---|---|---|
| V-01 | `DC_20260729_008` の引用文が原文と一致するか | **一致**(Decision Ledger 実読) |
| V-02 | `DC_20260729_001` / `DC_20260729_009` / `DC_20260731_007` の引用 | **一致** |
| V-03 | `DESIGN_v1.md` の引用文・日付・TODO_186・E20260526_044 | **一致** |
| V-04 | PHI-REG-02(a) の物理実体(`extension/` `core/` `adapters/`) | **実在** |
| V-05 | `mocka-bridge.js` の接続先 | **誤り検出 → §3.4bis で R2 訂正** |
| V-06 | HG-1 の稼働実績の呼出主体 | **過剰断定を検出 → §4.3 で R2 精緻化(Unknown へ後退)** |
| V-07 | `db_helper.write_event` docstring の引用 | **一致** |
| V-08 | `events._source` / `audit_violations` の集計値 | **一致** |
| V-09 | 本文に `decision` フィールドが混入していないか | **混入なし** |
| V-10 | 本文に推奨・優劣評価が混入していないか | **混入なし**(「観測(推奨ではない)」の明示のみ) |
| V-11 | HG-J02 で選択肢を列挙していないか | **列挙していない**(§5.2 の方針どおり) |

### 10.2 検出した自誤 2件

| # | 箇所 | 初版の記載 | 訂正 |
|---|---|---|---|
| E-1 | §3.4 / O-3 | 「`mocka-bridge.js` の既定接続先は `localhost:5002/mcp`」 | fallback リテラルと解決結果を混同していた。実際の解決先は `https://mcp.nsjp.org/mcp`(§3.4bis) |
| E-2 | §4.3 | 「モジュール本体は **CLI 経路で**稼働中」 | `phi_os/human_gate.py` 経由は Confirmed だが、**呼出主体は特定できていない(Unknown)**。CLI は整合する候補、`migrate_prevention_queue.py` は note 不一致で除外(§4.3 R2) |

いずれも `feedback` として既知の failure mode(コード上の fallback を実効値と読む / 整合する候補を実測なしに断定する)に該当する。

### 10.3 判断材料として不足していると観測される事項

裁定に必要でありながら、本 Package が提供できていない材料。**埋める作業は未着手。**

| # | 不足 | 影響する判断 |
|---|---|---|
| M-1 | HG-2(`/decision/approve`)の状態記録先と呼出実績が未確認 | HG-J04(J04-B の評価材料) |
| M-2 | HG-4 / HG-5 の状態モデルと `phi_os/human_gate.py` との異同が未確認 | HG-J04(J04-D の Scope 見積) |
| M-3 | `mocka_human_gate_decision_definition_v1.md` の Core/Finalization 2層と、`phi_os/human_gate.py` の STATES/TRANSITIONS の対応関係が未確認 | HG-J04 全般 |
| M-4 | ~~HAB-D(Chrome拡張)の現在の稼働有無~~ **【R3 解消】** 登録は Confirmed(ID 実測一致)。有効/無効・稼働は Unknown 継続(U-01/U-02)。→ `JARVIS_HGJ03_EVIDENCE_M4_M5_v0.1.md` | HG-J03 |
| M-5 | ~~`https://mcp.nsjp.org` の到達性・認証要件~~ **【R3 解消】** GET /mcp → 200、認証なし POST → 202。202 の意味は Unknown(U-04)。→ 同上 | HG-J03 |
| M-6 | `ジャビス.md` の版管理(Seal 対象とする場合の正典時点)が未定 | HG-J01(J01-D) |

**観測:** M-1〜M-3 は HG-J04、M-4〜M-5 は HG-J03 の材料である。
博士の提示順(J03 → J04)に従う場合、先に必要になるのは M-4/M-5 である(観測。着手指示は受けていない)。

---

## Knowledge Lineage

**Document:** JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md
**Status:** 裁定待ち(Decision Ledger 未登録)
**Created:** 2026-08-04
**Origin:** きむら博士より「実装ではなく HG-J01〜J04 の裁定準備が先」との指示を受けて作成
**Parent Documents:**
- `docs/governance/JARVIS_CONSTITUTION_DRAFT.md`(第9章 HG-J01〜HG-J09)
- `docs/audits/JARVIS_{ARCHITECTURE_CURRENT,CAPABILITY_INVENTORY,BOUNDARY_ANALYSIS,GAP_ANALYSIS,RUNTIME_FLOW}.md`
**様式の先例:** `docs/governance/decision_identity/HUMAN_GATE_DECISION_PACKAGE_v0.1.md`
**Referenced Decisions:** `DC_20260729_001` / `DC_20260729_007` / `DC_20260729_008` / `DC_20260729_009` /
`DC_20260731_007` / `DC_20260801_002`
**Primary Evidence:** `PlanningCaliber/workshop/phi-os/DESIGN_v1.md`(2026-06-01、TODO_186、E20260526_044)、
`PlanningCaliber/workshop/phi-os/{extension,core,adapters}/`(ファイル実在)、
`adapters/mocka-bridge.js:29`、`app.py:3405`(`/api/phi-os-event`)、`interface/db_helper.py:135`(`write_event`)、
`phi_os/human_gate.py`、`governance/human_gate_cli.py`、
`data/mocka_events.db`(`events` / `human_gate_events` / `audit_violations` 実測)、
`C:\Users\sirok\Desktop\aimd\ジャビス.md`
**Affected Components:** なし(コード変更・Runtime作成・HAB実装・MCP拡張・Skill Layer実装のいずれも行っていない)
**Revision History:**
- R1(2026-08-04): 新規作成。HG-J01〜J04 の判断材料・依存構造・選択肢を整理。
  `decision` フィールドなし。実装・Decision Ledger 登録なし。
- R2(2026-08-04): セルフレビュー実施(§10)。自誤2件を訂正 —
  §3.4bis 追加(`mocka-bridge.js` の解決先は `https://mcp.nsjp.org/mcp`。`localhost:5002` は fallback リテラル)、
  §4.3 精緻化(HG-1 の呼出主体は Unknown へ後退。`migrate_prevention_queue.py` は除外)。
  O-6 追加(設定パス絶対直書き)。§10.3 に不足材料 M-1〜M-6 を記載。裁定は行っていない。

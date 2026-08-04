# JARVIS HG-J03 追加証拠調査 — U-16 観測記録 v0.1
## HAB-D-3(`tools/mocka-bridge/extension`)の制度的所属

**文書番号:** JARVIS-HGJ03-EV-003
**調査日:** 2026-08-04
**状態:** **観測記録のみ(裁定なし・採用判断なし・設計変更なし・実装なし)**
**Decision Ledger 登録:** なし

## 0. 調査条件と結論

| 条件 | 遵守状況 |
|---|---|
| 実装変更禁止 / 設定変更禁止 / 裁定禁止 | 遵守(読み取りのみ、コード・設定の変更ゼロ) |
| Unknown 保持 | §5 |

**結論(観測):**
**U-16 は解消した。HAB-D-3 には制度的所属がある。**
ただし所属先は `PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1.md` の PHI-REG 体系ではなく、
**`data/MOCKA_OVERVIEW.json` の `extension_canonical_paths` 正本台帳**である。

前回記録(`JARVIS_HGJ03_EVIDENCE_U09_U07_v0.1.md` §3 表)の
「RESPONSIBILITY_MAP 記載: なし」は事実として正しいが、
**「制度的所属が無い」という含意を持たせるのは誤りであった**(§4 で訂正)。

---

## 1. 正本台帳 `extension_canonical_paths`(Confirmed / 一次データ)

出典: `data/MOCKA_OVERVIEW.json`(mtime 2026-08-04 15:17、`sync_watch` allowlist 対象ファイル)

```json
"extension_canonical_paths": {
  "purpose": "拡張機能・複数コピーが作られうる資産の変更前に必ず参照する正本パス一覧（TODO_354）。Chrome Secure Preferences実測により確定。",
  "established": "2026-06-27",
  "reference_event": "E20260621_378795484b70f（発端INCIDENT）",
  "relay":        { "extension_id": "okocleheboabgenhlhliingbpjlkmpcf", "canonical_path": ".../Relay_Project/extension/" },
  "orchestra":    { "extension_id": "lbjcmlkcjgjibcmlaokldopjokajjlgc", "canonical_path": ".../Orchestra_Project/extension/" },
  "memory":       { "extension_id": "nheoiflmnjkgobnahglbbeoihaddacnp", "canonical_path": ".../memory/extension/" },
  "phi_os":       { "extension_id": "bieancjajjieckhmgkmcpigpahodiodb", "canonical_path": ".../phi-os/extension/" },
  "mocka_bridge": { "extension_id": "doapadhfedmognoilmjieekfhijeadnf", "canonical_path": "C:/Users/sirok/MoCKA/tools/mocka-bridge/extension/",
                    "note": "2026-06-21移行後の新ID。旧ID impamkjmlflhhjaabhaenkgmnmpflobd は旧パス参照の死骸エントリとしてChrome内に残存（実害なし・手動削除可、TODO_354 note参照）。" }
}
```

### 1.1 Chrome 実測との突合(Confirmed / 全件一致)

前回 M-4 で Chrome `Secure Preferences` から抽出した Extension ID と、本台帳を突合した。

| 台帳エントリ | 台帳の Extension ID | Chrome 実測 | 一致 |
|---|---|---|---|
| relay | `okocleheboabgenhlhliingbpjlkmpcf` | 同一 | ✔ |
| orchestra | `lbjcmlkcjgjibcmlaokldopjokajjlgc` | 同一 | ✔ |
| memory | `nheoiflmnjkgobnahglbbeoihaddacnp` | 同一 | ✔ |
| phi_os(**HAB-D-1**) | `bieancjajjieckhmgkmcpigpahodiodb` | 同一 | ✔ |
| **mocka_bridge(HAB-D-3)** | `doapadhfedmognoilmjieekfhijeadnf` | 同一 | ✔ |

**5件すべてが一致した。** 台帳は実測に基づき維持されている。

---

## 2. HAB-D-3 の由来(Confirmed / git + commit message)

### 2.1 正本パス確定 commit

```
commit 701df7c62d705432ec9de464b43666eacd6c57ef
Date:   2026-06-21 18:26:27 +0900
Subject: MoCKA Bridge正本パス統一移行: tools/mocka-extension -> tools/mocka-bridge/extension (TODO_354)

  きむら博士確定方針により\extension\を1階層下に置く構造ルールに統一。
  新Chrome Extension ID: doapadhfedmognoilmjieekfhijeadnf
  旧ID impamkjmlflhhjaabhaenkgmnmpflobd は死骸エントリとして残存（実害なし）
  動作監査7項目PASS。MOCKA_OVERVIEW.jsonにextension_canonical_paths新設。
```

**Confirmed な事実:**
- 由来根拠: **TODO_354**、および **「きむら博士確定方針」**(commit message 明記)
- 移行前の path: `tools/mocka-extension`(現在は実体なし、§3)
- 新 Extension ID は Chrome 実測値と一致(§1.1)
- **動作監査7項目 PASS** の記載あり(監査内容の詳細は本調査では未確認 = Unknown、U-20)
- 本 commit で `extension_canonical_paths` が新設された

### 2.2 より古い系譜(Confirmed / git log)

| commit | 内容 |
|---|---|
| `381b31e2c` | `fix(bridge): 正しいパスに修正 tools/mocka-extension` |
| `989bee550` | `feat: MoCKA Bridge v2.0 - Ghost Badge実装・送信汚染廃止・DNA注入基盤整備 E20260412_001` |
| `701df7c62`(2026-06-21) | 正本パス統一移行(§2.1) |

`989bee550` は Event ID `E20260412_001` を引用しており、v2.0 時点で Event 記録を伴っていたことが読める
(当該 Event の内容照合は本調査では未実施 = Unknown、U-21)。

現在の manifest は **v2.4**。v2.0 → v2.4 の変更経緯は本調査では未追跡(Unknown、U-22)。

---

## 3. 死骸エントリの確認(Confirmed / 前回記録の精緻化)

前回 M-4 で「MoCKA 配下の未パック拡張7件」として列挙したもののうち、**2件は実体が存在しない**。

| Chrome 登録 path | 実体の有無 | 台帳上の扱い |
|---|---|---|
| `C:\Users\sirok\MoCKA\tools\mocka-extension`(ID `impamkjmlflhhjaabhaenkgmnmpflobd`) | **存在しない**(実測) | `extension_canonical_paths.mocka_bridge.note` が **「旧パス参照の死骸エントリ」と明記** |
| `C:\Users\sirok\mocka_extension`(ID `endlgfdpmpobmjbcnjjfojdicmlbknlg`) | **存在しない**(実測) | 台帳に記載なし |

`~/mocka_extension` については `TODO_440`(完了)の note に
**「mocka_extension第三コピーの件はレジストリ残留のみ・実体なしと訂正済み(event_id `E20260711_10913007456a7`)」**
との記録があり(Confirmed)、本調査の実測と一致する。

**前回記録の精緻化:** M-4 §1.3 の一覧は「Chrome に登録されている」点では正確だが、
**うち2件は実体を伴わない登録残骸である**。実体を持つ MoCKA 配下の拡張は **5件**
(phi-os / Orchestra_Project / Relay_Project / memory / seo-os / tools\mocka-bridge のうち、
seo-os を含めて数えると6件。ただし **seo-os は `extension_canonical_paths` に記載がない** = §5 U-23)。

---

## 4. HAB-D-3 の制度的位置づけ — 3系統の比較(観測のみ)

きむら博士が提起した論点
**「存在する → 動いている → 正当な制度位置を持つ、は別段階である」**
に対応する観測を整理する。**評価・採否は記載しない。**

| 段階 | HAB-D-1(`phi-os/extension`) | HAB-D-2(`phi-os/core`+`adapters`) | **HAB-D-3(`tools/mocka-bridge/extension`)** |
|---|---|---|---|
| **実体の存在** | Confirmed | Confirmed | Confirmed |
| **Chrome 登録** | Confirmed(ID一致) | 該当なし(拡張ではない) | Confirmed(ID一致) |
| **正本台帳登録** | **あり**(`extension_canonical_paths.phi_os`) | なし(拡張台帳の対象外) | **あり**(`extension_canonical_paths.mocka_bridge`) |
| **由来 Decision / 方針** | `DESIGN_v1.md`(2026-06-01、TODO_186、確定イベント `E20260526_044`) | `CHANGE_TRACKER_README.md`(TODO_144 / TODO_217、`E20260603_060`) | **TODO_354 +「きむら博士確定方針」**(commit `701df7c62`)。系譜は `E20260412_001`(v2.0)まで遡る |
| **PHI-REG 体系への登録** | あり(PHI-REG-02(a)) | あり(同上に含まれる) | **なし** |
| **Runtime 稼働実績** | **0件**(`direct_violation` 0) | 未確認 | **753件**(`how_trigger='chrome_extension_v15'`、最新 2026-07-29) |
| **書込経路の Gate 経由** | しない(`db_helper.write_event` 直呼び) | Unknown | **する**(`append_event` → Local Buffer → `/api/gate/event/batch`) |

### 4.1 書込経路に関する Active Decision(Confirmed / 重要)

`DC_20260725_003`(Active、2026-07-25、きむら博士)の条件3(原文):

> 3. **Canonical Ledger経路(`get_buffer().push()`)には一切変更を加えないこと**を本Decisionの前提条件として明記する

すなわち **`get_buffer().push()` は Active Decision により「Canonical Ledger 経路」と名指しされている。**
前回 §2.4 で観測した HAB-D-3 の書込経路(`append_event` → `get_buffer().push()`)は、この経路と一致する。

関連 Decision(いずれも Active):

| Decision | 内容 |
|---|---|
| `DC_20260723_006` | Phase 8-4 Extension / Consumption Layer Initiation。対象に「(3)content.js等既存Consumerとの接続」を含む |
| `DC_20260725_001` | IDR-003 Phase1 遡及承認: 案C(既存 `/collect` 経路を **Event Ingestion Gateway 化**)を採用。Phase1 は `mcp/adapters/browser.py` 新規作成と `mcp_router.py` の `SOURCE_TYPE_MAP` への `browser` 追加のみ。「app.py・**mocka-bridge**・既存adapterには変更がない」と明記 |
| `DC_20260725_003` | IDR-003 Phase2 条件付き承認(app.py `/collect` への RelayKernel projection)。§4.1 の条件3を含む |

**観測:** `DC_20260725_001` は `mocka-bridge` を名指しで言及しており、
**HAB-D-3 は Decision Ledger 上で認識されている対象である。**

### 4.2 config.js に関する制度記録(Confirmed / 前回観測の補完)

前回 §2.6 で「`config.js` は manifest 未登録・参照ゼロでロードされていないと読める」と観測した。
これに対応する制度記録が存在する。

`TODO_418`(完了)の description(原文、Confirmed):

> `tools/mocka-bridge/extension/config.js` が worker.js 経由で gateway にアクセスする経路
> (**X-MoCKA-Sig方式**、TODO_415/417 の X-MoCKA-Key 方式とは別)に影響する可能性がある。

**観測:**
- `config.js` は制度上「gateway アクセス経路の一部」として **認識されている**。
- ただし TODO_418 の記述は「影響する**可能性がある**」であり、稼働の断定ではない。
- 静的解析(前回)では manifest 未登録・参照ゼロ。両者は矛盾しない(認識されているが現在ロードされていない、と読める)。
- **X-MoCKA-Sig 方式**という第3の認証方式の存在が記録されている(本調査では実装未確認 = Unknown、U-24)。

### 4.3 関連する既存 TODO(Confirmed)

| TODO | status | HAB-D 系への関わり |
|---|---|---|
| TODO_354 | (完了、archive) | 正本パス統一移行。`extension_canonical_paths` 新設 |
| TODO_422 | 完了 | `mocka-bridge.js`(**HAB-D-2**)の解決済み `MOCKA_ENDPOINT` を export し `file-guard.js` が import。独自ハードコード削除 |
| **TODO_425** | **未着手** | Extension 設定同期設計(`content.js` / `manifest.json`)。TODO_422 から切り出し |
| TODO_440 | 完了 | `tools/mocka-bridge/extension/` 配下全 JS の `chrome.storage` 実測調査。`~/mocka_extension` を「レジストリ残留のみ・実体なし」と訂正 |
| TODO_418 | 完了 | `config.js` の gateway 経路(X-MoCKA-Sig 方式)に言及 |

---

## 5. Unknown(本調査で確定できなかった事項)

| # | Unknown |
|---|---|
| U-01 / U-02 | 拡張の有効/無効、service worker の実稼働(継続) |
| U-11〜U-15, U-17〜U-19 | 前回記録から継続 |
| **U-20** | commit `701df7c62` の「動作監査7項目」の内容 |
| **U-21** | `E20260412_001`(MoCKA Bridge v2.0 の引用 Event)の内容 |
| **U-22** | v2.0 → v2.4 の変更経緯 |
| **U-23** | `seo-os/extension`(ID `kbmliimnlfemkkijfbjbjepiilnihpib`)が `extension_canonical_paths` に記載されていない理由 |
| **U-24** | `X-MoCKA-Sig` 方式の実装実体(TODO_418 が言及するのみ) |
| **U-25** | HAB-D-3 が `PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1.md` の PHI-REG 体系に登録されていない理由。台帳が2系統(PHI-REG / `extension_canonical_paths`)存在し、両者の関係が未定義 |

**U-25 について(観測):**
`extension_canonical_paths` には **phi_os(HAB-D-1)と mocka_bridge(HAB-D-3)が並列に登録されている**。
一方 `PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1.md` は phi_os のみを PHI-REG-02(a) として扱う。
**同一対象を扱う台帳が2系統あり、収録範囲が異なる。** 両者の上下関係・正典性は本調査では未確認。

---

## 6. HG-J03 判断材料としての到達状況(観測のみ)

きむら博士の整理に対応させた現状。

| 項目 | 前回まで | 本調査後 |
|---|---|---|
| HAB-D は3系統存在 | Confirmed | Confirmed(変更なし) |
| HAB-D-1 は Gate 非経由コード存在 | Confirmed | Confirmed(変更なし) |
| HAB-D-3 は Gate 経由イベント実績あり | Confirmed | Confirmed + **`DC_20260725_003` が当該経路を「Canonical Ledger経路」と名指し** |
| **HAB-D-3 の正式 Decision** | **Unknown** | **解消**: TODO_354 +「きむら博士確定方針」+ `extension_canonical_paths` 正本登録 + `DC_20260725_001` での名指し言及 |
| HAB-D-2 の Runtime 実態 | Unknown | Unknown(変更なし) |
| HAB-D-1 が本番利用されているか | Unknown | Unknown(変更なし) |
| JARVIS が参照すべき HAB 定義 | **Unknown** | **Unknown(裁定事項。本調査では確定させない)** |

---

## 7. 本調査で行っていないこと

- 採用判断・優劣評価・推奨(**裁定禁止**)
- 設計変更・実装・設定変更(**禁止**)
- U-19(`audit_violations` NEW 6件との因果)の追跡 — **博士より「HG-J03 裁定から逸れる」との整理があったため着手していない**
- U-20〜U-24 の追跡
- 死骸エントリ2件の削除(台帳 note は「手動削除可」と記すが、**実施していない**)

---

## Knowledge Lineage

**Document:** JARVIS_HGJ03_EVIDENCE_U16_v0.1.md
**Status:** 観測記録(裁定なし、Decision Ledger 未登録)
**Created:** 2026-08-04
**Origin:** きむら博士の整理「最優先追加観測 U-16: HAB-D-3の由来Decision・設計根拠。理由: 実体と稼働実績が確認できても、制度上の所属が不明なままだとJARVIS Constitutionへ継承できません」
**Parent Documents:**
- `docs/governance/JARVIS_HGJ03_EVIDENCE_U09_U07_v0.1.md`(U-16)
- `docs/governance/JARVIS_HGJ03_EVIDENCE_M4_M5_v0.1.md`
- `docs/governance/JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md`
**Primary Evidence:**
`data/MOCKA_OVERVIEW.json`(`extension_canonical_paths`)、
git commit `701df7c62`(message 全文)、`989bee550`、`381b31e2c`、
`data/decisions/decision_ledger.jsonl`(`DC_20260723_006` / `DC_20260725_001` / `DC_20260725_003` / `DC_20260707_017` / `DC_20260707_018`)、
`data/MOCKA_TODO.json`(TODO_418 / TODO_422 / TODO_440)、
`C:\Users\sirok\AppData\Local\Google\Chrome\User Data\Default\Secure Preferences`、
ファイル実在確認(`~/mocka_extension` / `tools/mocka-extension` = いずれも不存在)
**Affected Components:** なし(読み取りのみ。コード・設定の変更ゼロ)
**Revision History:**
- R1(2026-08-04): 新規作成。U-16 を解消。HAB-D-3 の制度的所属を `extension_canonical_paths` + TODO_354 と特定。
  前回記録の「RESPONSIBILITY_MAP 記載なし」に制度的所属の不在という含意を持たせないよう §0/§4 で訂正。
  Unknown を U-20〜U-25 として追加保持。裁定・採用判断・設計変更・実装のいずれも行っていない。

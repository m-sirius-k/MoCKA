# JARVIS HG-J03 — Evidence Complete / Decision Required

**文書番号:** JARVIS-HGJ03-EC-001
**作成日:** 2026-08-04
**状態:** **Evidence Complete / Decision Required**

| 区分 | 状態 |
|---|---|
| 技術調査 | **完了** |
| 採用判断 | **未実施** |
| HAB 境界の選択 | **Human Gate 裁定事項** |
| Decision Ledger 登録 | なし |
| 実装・設定変更 | なし |

**本文書は `decision` フィールドを含まない**(`mocka_human_gate_decision_definition_v1.md` §6)。
推奨・優劣評価を含まない。提供するのは判断材料と観測のみである。

---

## 0. HG-J03 の問いの変遷(記録)

| 時点 | 問い |
|---|---|
| Phase 1(Constitution Draft §7.1) | "PHI-HAB" が HAB-C(構想)/ HAB-D(制度)のどちらを指すか |
| M-4 / M-5 後 | HAB-D が単一でないことが判明 → どの HAB-D か |
| U-09 / U-07 後 | HAB-D が3系統に分離 → 実行経路・ガバナンス境界が系統ごとに異なる |
| **現在** | **JARVIS の Human Authority Boundary として、どの責務境界を採用するか** |

**観測:** 問いは「採用の可否」から「複数実在する候補のうちどれを制度境界として認定するか」へ変化した。
これは調査の失敗ではなく、**裁定対象が実測により正確化された結果**である。

---

## 1. 確定事項(Confirmed)

### 1.1 "HAB" は4つの異なる対象を指す

| # | 呼称 | 出典 | 制度状態 | 実装 |
|---|---|---|---|---|
| HAB-A | Human Authority Boundary | `docs/governance/mocka_hab_v1_contract.md` | DRAFT | 文書のみ |
| HAB-B | HAB spine | `docs/contracts/phase8_hab_runtime_integration_v1.md` + `semantic/query_engine/execution_orchestrator.py` | DRAFT | コード実在・外部import 0件 |
| HAB-C | PHI-HAB(構想) | `Desktop\aimd\ジャビス.md` §4 | **未登録** | 実装なし |
| HAB-D | PHI-HAB(制度) | `DC_20260729_008`(Active) | **Active** | **3系統に分離(§1.2)** |

### 1.2 HAB-D は3系統である

| | **HAB-D-1** | **HAB-D-2** | **HAB-D-3** |
|---|---|---|---|
| 実体 | `PlanningCaliber/workshop/phi-os/extension/` | `phi-os/core/` + `phi-os/adapters/` | `tools/mocka-bridge/extension/` |
| 名称 / 版 | "PHI OS" v1.0.0 | change-tracker / file-guard / tool-hook | "MoCKA Bridge" v2.4 |
| 種別 | Chrome 拡張(MV3) | Node/Chrome 両対応 JS モジュール | Chrome 拡張(MV3) |
| **実体の存在** | Confirmed | Confirmed | Confirmed |
| **Chrome 登録** | Confirmed(ID `bieancja…`、実測一致) | 該当なし | Confirmed(ID `doapadhf…`、実測一致) |
| host_permissions | `claude.ai` のみ | — | localhost:5000 + 外部AI 9ドメイン |
| **MoCKA 接続先** | `POST http://127.0.0.1:5000/api/phi-os-event` | `https://mcp.nsjp.org/mcp` | `POST :5000/user_voice` `/collect` `/ask` `/orchestra` `/success` ほか |
| **Canonical Ledger 経路** | **非経由**(`db_helper.write_event` 直呼び、`channel` 未指定) | **Unknown** | **経由**(`append_event` → `get_buffer().push()` → `/api/gate/event/batch`) |
| **Runtime 発火実績** | **0件**(`_source='direct_violation'` 0件) | 未確認 | **753件**(`how_trigger='chrome_extension_v15'`、最新 2026-07-29、`_source='buffered'`) |
| **正本台帳登録** | あり(`extension_canonical_paths.phi_os`) | 対象外 | あり(`extension_canonical_paths.mocka_bridge`) |
| **PHI-REG 体系** | あり(PHI-REG-02(a)) | あり(同上に含まれる) | **なし**(§1.4 / U-25) |
| **由来根拠** | `DESIGN_v1.md`(2026-06-01、TODO_186、確定イベント `E20260526_044`) | `CHANGE_TRACKER_README.md`(TODO_144 / TODO_217、`E20260603_060`) | TODO_354 + 「きむら博士確定方針」(commit `701df7c62`)。系譜は `E20260412_001`(v2.0)まで遡る |
| **Decision Ledger での言及** | `DC_20260729_008`(PHI-REG-02(a) として) | 同左に含まれる | **`DC_20260725_001` が `mocka-bridge` を名指し言及** |

### 1.3 Canonical Ledger 経路の制度的裏付け

`DC_20260725_003`(Active、2026-07-25、きむら博士)条件3(原文):

> 3. **Canonical Ledger経路(`get_buffer().push()`)には一切変更を加えないこと**を本Decisionの前提条件として明記する

HAB-D-3 の書込経路はこの `get_buffer().push()` と一致する(コード実測 + DB 実測)。
すなわち **HAB-D-3 の経路は、Active Decision が保護対象として名指しした経路である。**

対して HAB-D-1 の経路は `db_helper.write_event()` を `channel` 未指定で呼ぶ。
**app.py:266-269 自身が「禁止事項: db_helper.write_event()の直接呼び出し」と明記している**(TODO_347)。
ただし発火実績は 0件である。

### 1.4 正本台帳 `extension_canonical_paths`

`data/MOCKA_OVERVIEW.json`(established 2026-06-27、reference_event `E20260621_378795484b70f`):

> purpose: 拡張機能・複数コピーが作られうる資産の変更前に必ず参照する正本パス一覧(TODO_354)。
> Chrome Secure Preferences実測により確定。

登録5件(relay / orchestra / memory / phi_os / mocka_bridge)の Extension ID は、
Chrome `Secure Preferences` の実測値と **全件一致**した。

**この台帳は「存在管理 + 正本管理 + 変更制御」を担う制度資産である**(purpose 文より)。
`seo-os/extension` は Chrome に登録されているが本台帳に記載がない(U-23)。

### 1.5 登録残骸(死骸エントリ)

Chrome に登録されているが実体が存在しないもの(実測):

| Chrome 登録 path | 台帳上の扱い |
|---|---|
| `MoCKA\tools\mocka-extension`(旧 ID `impamkjm…`) | `extension_canonical_paths.mocka_bridge.note` が「旧パス参照の死骸エントリ」と明記 |
| `C:\Users\sirok\mocka_extension` | 台帳記載なし。`TODO_440` note が「レジストリ残留のみ・実体なし」と訂正(`E20260711_10913007456a7`) |

**登録 ≠ 実体** である。

---

## 2. 選択肢(列挙のみ。優劣評価・推奨を含まない)

**注記:** Decision Package v0.1 §3.5 の初版 Option(J03-A〜D)は
「HAB-D が単一実体である」前提で作成されていた。
HAB-D の3系統分離を受け、**選択肢の構造を更新する**。
これは選択肢の整形であって、採否の判断ではない。

### 2.1 論点1 — "PHI-HAB" という語の帰属

| Option | 内容 | 必要になる後続判断 |
|---|---|---|
| **P-1** | HAB-D(`DC_20260729_008`)に一本化し、HAB-C(`ジャビス.md`)に別名を与える | HAB-C の新名称 / `ジャビス.md` の読み替え運用ルール |
| **P-2** | HAB-C を採用し、HAB-D を改称する | `DC_20260729_008` を変更または上書きする Decision(同 Decision は「PHI-REG-01〜04のIDは維持し、変更・廃止しない」と制約) |
| **P-3** | 両者を別概念として併存させ、完全修飾名を必須とする | 命名規則 / 既存文書の表記統一範囲 |
| **P-4** | 確定させず Pending Resolution とする | 暫定表記ルール / 再評価条件 |

**先例(観測):** `PHI_OS_CONSTITUTION_v1.md` 末尾「追加記録: PHI-OS名称の二義性について」(2026-07-25、HG-3 承認済み)は、
同種の名称衝突を **憲法本体への追記により両者の系譜を記録し、統合しないまま併存させる**方法で処理した。

### 2.2 論点2 — JARVIS の Human Authority Boundary として認定する実体

| Option | 内容 | この Option に固有の留意点(優劣評価ではない) |
|---|---|---|
| **E-1** | **HAB-D-1**(`phi-os/extension`)を境界とする | 書込経路が Canonical Ledger 経路を経由しない。app.py が禁止事項と明記した呼び方に該当する。発火実績 0件。PHI-REG-02(a) に登録済み |
| **E-2** | **HAB-D-2**(`phi-os/core`+`adapters`)を境界とする | 接続先が外部公開エンドポイント。MoCKA 側での扱いが Unknown。Chrome 拡張ではないため `extension_canonical_paths` の対象外 |
| **E-3** | **HAB-D-3**(`tools/mocka-bridge/extension`)を境界とする | Canonical Ledger 経路を経由。753件の稼働実績。正本台帳登録あり。**ただし PHI-REG 体系には未登録**(U-25 に依存) |
| **E-4** | 複数を層として併存させ、責務を分離して定義する | 3系統それぞれの責務境界の定義 / 相互の呼出関係の規定 |
| **E-5** | いずれも JARVIS の境界とせず、別途定義する | 新規定義の是非(`JARVIS_CONSTITUTION_DRAFT.md` §4.3「新規Runtime禁止」との関係) |

### 2.3 論点3 — `ジャビス.md` の階層図の読み方

`ジャビス.md` §8: `Human → JARVIS → PHI-HAB → Institutional Runtime`

論点1・論点2の結果により、この図の "PHI-HAB" が指す対象が確定する。
**本文書はこの図の解釈を確定させない。**

---

## 3. Residual Unknown(裁定後も残る、または裁定時に参照すべき事項)

### 3.1 U-25 — 複数台帳間の正典関係(**HG-J01 / HG-J02 判断時に再参照**)

**きむら博士の整理に従い、本項を HG-J03 の Residual Unknown として明示する。**

| 観測 | 内容 |
|---|---|
| Confirmed | 同一対象(Chrome 拡張群)を扱う台帳が **2系統存在する** |
| 台帳1 | `PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1.md`(PHI-REG-01〜04 体系)。phi_os を PHI-REG-02(a) として収録 |
| 台帳2 | `data/MOCKA_OVERVIEW.json` の `extension_canonical_paths`。relay / orchestra / memory / phi_os / mocka_bridge を収録 |
| Confirmed | **収録範囲が異なる**。HAB-D-3 は台帳2 のみ、HAB-D-2 は台帳1 のみ |
| **Unknown** | **2台帳間の優先順位・上下関係・正典性** |
| **Unknown** | **JARVIS Constitution が継承すべき台帳がどちらか** |

**位置づけ:** 本項は HG-J03(技術的存在確認)ではなく、
**HG-J01(正典継承)/ HG-J02(帰属・Authority 位置)に影響する制度問題**である。
HG-J03 の裁定でこれを掘ると裁定対象が広がるため、**本文書では確定させない。**
**HG-J01 / HG-J02 の判断時に本項を再参照すること。**

### 3.2 その他の Residual Unknown

| # | Unknown | 影響 |
|---|---|---|
| U-01 | 9件の未パック拡張の有効/無効(`Secure Preferences` の `state` が43件すべて `None`) | E-1 / E-3 の実効性 |
| U-02 | service worker の実稼働 | 同上 |
| U-11 | `state-store.js` の `detectMode()` が実行時に返す値(コード上は STANDALONE と読める) | E-1 |
| U-12 | `mocka-bridge/background.js:244` の可変 endpoint に渡される値の全体像 | E-3 |
| U-13 | `user_voice` の `_source='legacy'` 7,052件の書込時期・経路 | E-3 |
| U-14 | `config.js` が実行時にロードされていないことの実測確認 | E-3 |
| U-15 | `turn_counter_patch.js` と `content.js` の重複実装のうち有効なもの | E-3 |
| U-17 | `tools/mocka-extension` / `~/mocka_extension` の内容(いずれも実体なし=死骸) | 低 |
| U-18 | `mcp.nsjp.org` へ送られたデータの MoCKA 側での扱い | E-2 |
| U-19 | `audit_violations` NEW 6件(2026-07-22〜23)と `mocka-bridge/content.js` 更新日(2026-07-23 08:50)の近接。**時系列近接 Confirmed / 因果 Unknown**。博士の整理により HG-J03 では追跡しない | 別件 |
| U-20 | commit `701df7c62` の「動作監査7項目」の内容 | E-3 |
| U-21 | `E20260412_001`(MoCKA Bridge v2.0 引用 Event)の内容 | E-3 |
| U-22 | v2.0 → v2.4 の変更経緯 | E-3 |
| U-23 | `seo-os/extension` が `extension_canonical_paths` 未記載である理由 | U-25 に関連 |
| U-24 | `X-MoCKA-Sig` 方式の実装実体(TODO_418 が言及するのみ) | E-3 |

---

## 4. 一次証拠索引

| 種別 | 証拠 |
|---|---|
| **Decision** | `DC_20260729_008`(PHI-HAB = PHI-REG-02(a))/ `DC_20260729_001`(JARVIS構想 Deferred)/ `DC_20260725_001`(IDR-003 Phase1、mocka-bridge 名指し)/ `DC_20260725_003`(Canonical Ledger 経路の保護)/ `DC_20260723_006`(Phase 8-4)/ `DC_20260728_003`(PHI-OS/MoCKA 境界) |
| **TODO** | TODO_354(正本パス統一)/ TODO_144・TODO_217(change-tracker / PostToolUse)/ TODO_186(DESIGN_v1)/ TODO_418(X-MoCKA-Sig)/ TODO_422(HAB-D-2 の SSOT)/ **TODO_425(未着手、Extension 設定同期)**/ TODO_440(拡張 storage 実測)/ TODO_347(Gate 直叩き廃止) |
| **Event** | `E20260621_378795484b70f`(台帳成立の発端 INCIDENT)/ `E20260526_044`(DESIGN_v1 確定)/ `E20260603_060`(change-tracker)/ `E20260412_001`(Bridge v2.0)/ `E20260711_10913007456a7`(第三コピー訂正) |
| **commit** | `701df7c62`(正本パス統一 + `extension_canonical_paths` 新設)/ `989bee550`(Bridge v2.0)/ `381b31e2c` |
| **コード** | `app.py`(L242 `append_event` / L266-269 禁止事項 / L432 `/user_voice` / L1009 `/collect` / L3405 `/api/phi-os-event`)/ `interface/db_helper.py` L135 / `interface/event_buffer.py` / `phi_os/event_gate.py`(`process_event` 「唯一の保存経路」宣言)/ `phi-os/extension/{background.js,core/auto-trigger.js,core/state-store.js}` / `phi-os/adapters/mocka-bridge.js` / `tools/mocka-bridge/extension/*` |
| **実測** | Chrome `Secure Preferences`(`extensions.settings` 43件)/ `data/mocka_events.db`(events 19,059、`_source` 分布、`how_trigger` 集計)/ HTTP(`mcp.nsjp.org` GET 200・POST 202、`:5000/b/health` 404・`:5003/b/health` 200、`:5010` 401) |
| **本調査文書** | `JARVIS_HGJ03_EVIDENCE_M4_M5_v0.1.md` / `JARVIS_HGJ03_EVIDENCE_U09_U07_v0.1.md` / `JARVIS_HGJ03_EVIDENCE_U16_v0.1.md` |

---

## 5. 調査過程で発生した自誤と訂正(記録)

Evidence Supremacy の実効性の証跡として記録する。**いずれも本文書には訂正後の内容のみを反映している。**

| # | 初版の誤り | 訂正 | 検出契機 |
|---|---|---|---|
| 1 | HAB を「三義性」と記載 | **四義性**。`DC_20260729_008` の PHI-HAB を見落とし(grep 範囲に `.jsonl` を含めず) | Phase 1 |
| 2 | P-DERS を「Missing」と判定 | 取消。`DC_20260730_001/002/003` と `DC_20260730_009` が実在。同じく `.jsonl` 未走査 | Phase 1 |
| 3 | `mocka-bridge.js` の接続先を「既定 = `localhost:5002/mcp`」と記載 | fallback リテラルを実効値と誤読。実際は `https://mcp.nsjp.org/mcp` | セルフレビュー |
| 4 | HG-1 を「CLI 経路で稼働中」と断定 | 呼出主体は **Unknown** へ後退。整合する候補と実行された事実は別 | セルフレビュー |
| 5 | Chrome `Preferences.extensions.settings` が0件 | キーパス誤り(現行 Chrome は `Secure Preferences`)。**0件を「未インストール」と結論しなかった** | M-4 |
| 6 | 「RESPONSIBILITY_MAP 記載なし」に「制度的位置づけ不明」の含意 | 別系統の正本台帳に登録済み。**「見つからない」と「存在しない」の混同** | U-16 |

---

## 6. 本文書で行っていないこと

- 採用判断・優劣評価・推奨(**裁定は Human Gate Finalization の専権**)
- 設計変更・実装・設定変更
- U-25 の追跡(§3.1 の方針により HG-J01 / HG-J02 へ送る)
- U-19 の因果追跡(博士の整理により HG-J03 対象外)
- 死骸エントリ2件の削除
- `JARVIS_CONSTITUTION_DRAFT.md` の Status 変更(HG-J09 の裁定事項)

---

## 7. 次工程

きむら博士の提示順:

```
HG-J03(本文書で Evidence Complete)
   ↓
HG-J04(Human Gate 接続先)     ← 次の観測対象
   ↓
HG-J01 / HG-J02 再確認         ← ここで U-25(§3.1)を再参照する
   ↓
JARVIS Constitution Finalization
```

**HG-J04 観測準備の対象**(Decision Package §10.3 の M-1〜M-3):

| # | 観測対象 |
|---|---|
| M-1 | HG-2(`app.py` `/decision/approve` `/decision/reject`)の状態記録先と呼出実績 |
| M-2 | HG-4(`semantic/query_engine/human_gate.py`)/ HG-5(`governance/human_gate_continuity.py`)の状態モデルと `phi_os/human_gate.py` との異同 |
| M-3 | `mocka_human_gate_decision_definition_v1.md` の Core / Finalization 2層と、`phi_os/human_gate.py` の `STATES` / `TRANSITIONS` の対応関係 |

**着手は指示待ち。**

---

## Knowledge Lineage

**Document:** JARVIS_HGJ03_EVIDENCE_COMPLETE_v0.1.md
**Status:** Evidence Complete / Decision Required(裁定なし、Decision Ledger 未登録)
**Created:** 2026-08-04
**Origin:** きむら博士の指示「HG-J03 は Evidence Complete として閉じる。状態: 技術調査完了 / 採用判断未実施 / HAB境界選択はHuman Gate裁定事項。資料には Residual Unknown として U-25(複数台帳間の正典関係は未定義。HG-J01/J02判断時に再参照する)を追記」
**Parent Documents:**
- `docs/governance/JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md`(§3 HG-J03、§10.3)
- `docs/governance/JARVIS_HGJ03_EVIDENCE_M4_M5_v0.1.md`
- `docs/governance/JARVIS_HGJ03_EVIDENCE_U09_U07_v0.1.md`
- `docs/governance/JARVIS_HGJ03_EVIDENCE_U16_v0.1.md`
- `docs/governance/JARVIS_CONSTITUTION_DRAFT.md`(§7.1 / HG-J03)
**Supersedes:** 上記3証拠文書の Option 部分(`JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md` §3.5 の J03-A〜D を §2 で更新)。証拠記録本体は各文書を正本として維持する
**Affected Components:** なし(コード・設定の変更ゼロ)
**Revision History:**
- R1(2026-08-04): 新規作成。HG-J03 を Evidence Complete として統合。
  HAB-D 3系統の確定比較、選択肢を P-1〜P-4 / E-1〜E-5 へ再構成、Residual Unknown に U-25 を明示。
  `decision` フィールドなし。裁定・採用判断・実装のいずれも行っていない。

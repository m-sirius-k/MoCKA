# Decision Identity Incident Triage

```
Document ID : DECISION_IDENTITY_INCIDENT_TRIAGE
Date        : 2026-08-01
作成        : くろこ (Claude Code, Claude-opus-5)
Authority   : Human Gate 確定 (2026-08-01) により本ディレクトリへ配置
Decision    : DC_20260801_001
Incident    : INC-DECISION-ID-COLLISION-20260730 (仮ID / 正式登録しない)
実施条件    : 読み取り専用。変更・修正なし
配置        : 既提出内容からのファイル化。内容追加・判断変更なし
```

記載は [事実] (コード・データ実測) / [観測] (測定結果) / [考察] (推論) で区別する。

---

## 1. Incident Record Draft

```
仮ID  : INC-DECISION-ID-COLLISION-20260730
Status: DRAFT (未登録)
```

注: Human Gate 確定 (2026-08-01) により、本 Incident は Integrity Ledger へ
正式登録しないことが決定した。本節は Draft のまま記録として保持する。

### 1-1. 発生日

2026-07-30 (JST)。該当行の書込時刻は以下。

| 行 | decision_id | approved_at (UTC) | JST |
|----|-------------|-------------------|-----|
| 193 | DC_20260730_001 | 2026-07-30T04:26:58Z | 07-30 13:26 |
| 194 | DC_20260730_002 | 2026-07-30T08:28:03Z | 07-30 17:28 |
| 196 | DC_20260730_003 | 2026-07-30T08:43:23Z | 07-30 17:43 |

### 1-2. 検出日

2026-07-31。CETR-001 基準状態監査の付随調査で decision_id の重複を検出。

[補足・事実] 同型の事象は 2026-07-29T23:01:00Z (JST 07-30 08:01) に一度検知され、
その場で回避されている。line 186 の context に記録が残る。

> 提示された案では本Decisionを"DC_20260730_002"として記録するよう案内されていたが、
> そのIDは本セッションで既にDC_20260730_002(Current Verified Stateテンプレート拡張)
> として使用済みであり、ID衝突である。(中略) よって本Decisionは自動採番の正しいIDで
> 記録する。

この時点では、明示指定された decision_id と既存 Ledger 状態の不一致が実行前に
認識され、自動採番へ切り替えられた。

### 1-3. 対象データ

`data/decisions/decision_ledger.jsonl` (当時 204行 / 730,796 bytes)

| ID | 行 | 主題 |
|----|----|------|
| DC_20260730_001 | 184 | Evidence Level階層・役割固定・セッション同期プロトコルの採用 |
| | 193 | p-DERS形式理論トラック(Track A) — Causal Projection 選定から部分証明 |
| DC_20260730_002 | 185 | Current Verified State テンプレートへ Verification Timestamp/Scope 追加 |
| | 194 | p-DERS Track A — Sound Local Approximation の証明 |
| DC_20260730_003 | 186 | PHI-OS Milestone 1 Architecture Investigation — 限定承認 |
| | 196 | MoCKA Governance Function G の実態調査 |

### 1-4. 発生事象

3つの decision_id それぞれに、系列関係を持たない別主題の記録が2件ずつ存在する状態。

[事実] 成立経路として観測された事項:

1. 明示指定された decision_id と既存 Ledger 状態の不一致
   後発3件の context には起案指示書名が記録されており、指示書側で ID が
   名指しされていた (例: line 193 のくろこ実行指示書
   "Decision Ledger記録(Track A成果確定、DC_20260730_001)")。

2. 重複検証機構未実装による通過
   `mocka_decision_write` の検証 (mocka_mcp_server.py:976-985) は必須項目・
   alternatives 形状・status enum のみを検査し、decision_id の重複・形式は
   検査しない。`_append_decision()` (同:396-400) は無条件 append。

3. 採番責任境界未定義
   decision_id は自動採番 (`_next_decision_id()`、当日最大値+1) と呼び出し側の
   明示指定の双方を受け付けるが、どちらが採番責任を負うかの規定が schema・Policy
   いずれにも存在しない。

[事実] line 195 (DC_20260730_010、08:42:23Z) の1分後に line 196
(DC_20260730_003、08:43:23Z) が書かれている。自動採番であればこの時点で 011 が返る。

原因断定は行わない。どの主体のどの操作が採番を決定したか、および 07-29 に機能した
確認がなぜ 07-30 に機能しなかったかは、記録から特定できない。

### 1-5. 影響範囲

| 面 | 影響 |
|----|------|
| MCP mocka_decision_get / mocka_decision_list | あり (最新行のみ返却) |
| governance/write_path/runtime/adapter.py | あり (同規則)。ただし未配線 |
| tools/audit/*.py (7本) | なし (全行走査) |
| JSONL 直接読み取り | なし |
| /decision/log・/decision/log/detail | なし (events.db 参照、Decision Ledger 非参照) |
| /api/ise/ledger | なし (PHI-OS 側の別 ledger) |
| Command Center / Dashboard / 全 HTML・JS / エクスポート | なし (参照 0件) |

参照解決の誤り: 3 ID を参照する ledger 内相互参照 11件のうち、7件が意図と異なる
記録に解決される。

| 参照元行 | 参照先 | 意図 | API 解決 | 判定 |
|---------|--------|------|----------|------|
| 185, 186, 187, 188, 189, 192 | _001 | line 184 | line 193 | 誤 (6件) |
| 186 | _002 | line 185 | line 194 | 誤 (1件) |
| 194, 196 | _001 | line 193 | line 193 | 正 |
| 196 | _002 | line 194 | line 194 | 正 |
| 197 | _003 | line 196 | line 196 | 正 |

影響を受ける利用者: MCP 経由の AI エージェントのみ。

### 1-6. データ損失有無

損失なし。

- JSONL 原本に6行すべて保持 (append-only 遵守、既存行の書き換え・削除なし)
- companion event 6件すべて存在。event title で区別可能
- ただし companion event から復元可能なのは 14フィールド中8つ。
  alternatives / approved_at / related_events / related_documents /
  supersedes / superseded_by は構造的に未格納

### 1-7. 到達不能経路

| 経路 | 到達不能な記録 |
|------|---------------|
| mocka_decision_get | line 184 / 185 / 186 |
| mocka_decision_list | 同上 |
| adapter.py::_read_decision (未配線) | 同上 |

### 1-8. 到達可能経路

| 経路 | 備考 |
|------|------|
| tools/audit/*.py (7本) | 全行処理。重複行も両方到達可能 |
| JSONL 直接読み取り | 全204行 |
| events.db (companion event) | 6件すべて。復元は8/14フィールドに限定 |
| git 履歴 | decision_ledger.jsonl は .gitignore により untracked。参照不可 |

### 1-9. 再発可能性

[事実] 再発を防ぐ機構は現時点で存在しない。

| 項目 | 状態 |
|------|------|
| decision_id 重複検査 | 未実装 |
| decision_id 形式検査 | 未実装 |
| 明示指定の禁止規定 | なし |
| 採番責任の規定 | なし |
| 第2書込経路 (SealGovernanceGate、DC_{execution_id} 形式) | 配線済み・実績0件 |

[観測] 2026-07-29 の1件は検知・回避されたが、その検知は実行時の確認に依存しており、
機構によるものではない。同一条件下での再発可能性は残存する。

### 1-10. 未決定事項

1. 対処方針 (A 現状維持 / B 全件返却 / C Alias・Canonical / D 解消レコード追加)
2. decision_id 重複検査の追加可否と、fail-closed / 警告の選択
3. 明示 ID 指定の可否
4. Incident の正式登録要否と仮ID の確定
   -> Human Gate 確定 (2026-08-01): 正式登録しない
5. 本 Triage 資料のリポジトリ配置先と記録手順
   -> Human Gate 確定 (2026-08-01): docs/governance/decision_identity/ へ配置

---

## 2. Decision Ledger Integrity Matrix v0.1

対象: 全204行 (2026-08-01 の DC_20260801_001 追記前の状態)

### 2-1. 分類原則

同一ID複数行 = 必ず異常、ではない。

schema §7 は append-only を定め、同一決定の状態更新は新規行の追記で表現される。
したがって同一 ID の複数行は正常な運用形態である。

問題は、同一 ID 複数行で系列関係が存在しない場合、すなわち別個の決定が同一 ID を
共有している状態である。

### 2-2. 系列関係の判定材料 (実測)

| ID | 行 | title 共通接頭辞 | supersedes=self | status=Superseded | 判定 |
|----|----|------------------|-----------------|-------------------|------|
| DC_20260707_020 | 37, 38 | 66文字 | - | - | STATE_UPDATE |
| DC_20260712_008 | 66, 67 | 45文字 | あり | - | STATE_UPDATE |
| DC_20260713_003 | 73, 74 | 30文字 | - | - | STATE_UPDATE |
| DC_20260719_MOCKA_REINFORCEMENT_001 | 119, 122 | 74文字 | - | あり | STATE_UPDATE |
| DC_20260730_001 | 184, 193 | 0文字 | - | - | COLLISION |
| DC_20260730_002 | 185, 194 | 0文字 | - | - | COLLISION |
| DC_20260730_003 | 186, 196 | 0文字 | - | - | COLLISION |

[観測] title 共通接頭辞は STATE_UPDATE 群で 30-74文字、COLLISION 群で一律 0文字と
明確に分離する。

[考察] 後続行が自 ID を言及する signal は7件すべてで真であり、系列判定の材料に
ならない (p-DERS 群も継続の意図で先行 ID を参照しているため)。系列判定には
主題の一致が必要である。

### 2-3. 分類結果

| 分類 | ID 数 | 行数 | 内訳 |
|------|-------|------|------|
| NORMAL (一意ID・形式適合) | 189 | 189 | - |
| STATE_UPDATE (同一ID・系列関係あり) | 4 | 8 | DC_20260707_020 / DC_20260712_008 / DC_20260713_003 / DC_20260719_MOCKA_REINFORCEMENT_001 |
| COLLISION (同一ID・別主題) | 3 | 6 | DC_20260730_001 / _002 / _003 |
| FORMAT_EXCEPTION (schema 形式外) | 2 | 3 | DC_20260719_MOCKA_REINFORCEMENT_001 (2行) / DC-WP-001 (1行) |
| UNKNOWN (判定不能) | 0 | 0 | - |

検算: 単一行ID 190 (うち形式外 DC-WP-001 が1) + 重複ID 7 = 197 distinct。
行数 189 + 8 + 6 + 1 = 204。

### 2-4. 分類の重複について

FORMAT_EXCEPTION は他分類と直交する軸である。DC_20260719_MOCKA_REINFORCEMENT_001 は
STATE_UPDATE かつ FORMAT_EXCEPTION に該当する。上表では重複計上している。

### 2-5. 健全性サマリ

| 観点 | 状態 |
|------|------|
| append-only 遵守 | 204/204 行が追記のみ (違反 0) |
| JSON パース成功 | 204/204 (broken 0) |
| 14フィールド構造 | 204/204 (欠落・過剰 0) |
| schema §4 重複禁止 | 7 ID が違反状態 (うち4件は意図された状態更新) |
| schema §3 ID 形式 | 201/204 行が適合 |
| 系列関係を欠く重複 | 3 ID / 6行 |
| 判定不能 (UNKNOWN) | 0 |

---

## 3. Human Gate Decision Sheet v0.1

### 3-1. Immediate Decision

HG-1: 対処方針 A / B / C / D
  判断事項: A 現状維持 / B 読み取り時に全件返却 / C Alias・Canonical 方式 /
            D Append-only 解消レコード の選択
  判断理由: 参照11件中7件が誤解決し、3件が MCP 経由で到達不能。append-only 制約下では
            既存行の書き換えによる是正は取り得ない
  判断保留時の影響: 誤解決7件が継続。誤った Decision を根拠に後続判断が積み上がる
            リスクが時間とともに増加。データ損失は生じない

HG-3: decision_id 重複検査追加方針
  判断事項: 重複検査を追加するか。追加する場合 fail-closed か警告のみか
  判断による影響: fail-closed は再発を確実に防ぐ一方、STATE_UPDATE 4件のような
            正当な同一ID追記も阻害する。警告のみでは再発を防げない

HG-4: 明示 ID 指定可否
  判断事項: decision_id の明示指定を許容するか、自動採番へ一本化するか
  判断による影響: 自動採番一本化により衝突は構造的に発生しなくなる。ただし
            STATE_UPDATE (同一ID での追記) が実行不能になる

注記: HG-3 と HG-4 は同じ制約に触れる。いずれも同一 ID での正当な追記を許すか否かの
線引きを含むため、独立に決めると矛盾しうる関係にある。

### 3-2. Deferred Decision

| # | 事項 | 現状 (事実) |
|---|------|------------|
| HG-6a | superseded_by 設計 | schema §7 は旧レコードの superseded_by 更新を規定するが、既存行書き換えを要求し append-only と不整合。実装は常に None、全204行で非 null は 0件 |
| HG-6b | SealGovernanceGate 第二書込経路 | DC_{execution_id} 形式・18フィールド・配線済み・実績 0件 |
| HG-6c | companion event 拡張 | 14中6フィールドが復元不可 |
| HG-6d | Decision Ledger UI 表示 | 表示面 0件。/decision/log 系は別データ源 |
| HG-6e | MCP description 重複 | mocka_mcp_server.py:472 と :1215 に同一定義が重複記載 |

---

## 4. Current Freeze Status (調査時点)

以下は当時未承認のため実施禁止であり、Triage 実施時点ですべて未実施であった。

| # | 凍結対象 | 状態 |
|---|---------|------|
| 1 | Decision Ledger 変更 | 204行 / 730,796 bytes (不変) |
| 2 | 既存 ID 変更 | 197 distinct ID (不変) |
| 3 | 行削除 | append-only 遵守、削除0 |
| 4 | history rewrite | 未実施 |
| 5 | schema 変更 | DECISION_LEDGER_SCHEMA_v1.md 不変 |
| 6 | API 変更 | 返却規則不変 |
| 7 | Policy 変更 | GOV-PROC-CETR-001 / EHCR-001 不変 |
| 8 | hook 導入 | 未実施 |

Triage 実施時の変更件数: 変更 0件 / commit 0件 / push 0件 / Event Ledger 記録 0件。

---

## 5. 後続

本 Triage を含む調査5資料の受領、および完全凍結の範囲限定解除と段階的実施方針は
DC_20260801_001 として Decision Ledger に記録された (2026-08-01、approved_by:
human_authority)。

HUMAN_GATE_DECISION_PACKAGE v0.1 第7章の未判断事項のうち項目1から12 は
本 Triage 時点および DC_20260801_001 時点で未判断のまま残る。

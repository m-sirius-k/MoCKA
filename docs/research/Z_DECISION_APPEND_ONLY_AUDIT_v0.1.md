# Z_DECISION_APPEND_ONLY_AUDIT_v0.1

- **Audit ID:** Z_DECISION_APPEND_ONLY_AUDIT_v0.1
- **Date:** 2026-07-15
- **Author:** Claude-opus-4-8 (くろこ / executor)
- **Trigger:** きむら博士指示 — Z_DECISION_CONNECTION_AUDIT_v0.1 完了確認後の次フェーズ
- **CHANGE_START:** E20260715_004921248dd54
- **Nature:** READ-ONLY 監査 + 本文書の新規作成のみ（DC新規作成・遡及登録・判断変更・推測補完は一切行わない）

---

## Scope

本監査の目的は、先行成果物 **Z_DECISION_CONNECTION_AUDIT_v0.1** が確認した
「**現行Decision一覧でZ関連DCなし**」という結論を、**append-only 全履歴レベル**へ拡張することである。

### 対象

- **正本:** `data/decisions/decision_ledger.jsonl`（全 **109 行**）
  - 全行（append-only の全レコード）
  - superseded 行 / 過去 version 行（`supersedes` / `superseded_by` フィールドを含む）
  - 各レコードの `context` / `rationale` / `related_events` / その他全フィールド
- **副次（限界補強のため）:** `data/ise/decision_ledger.jsonl`（27 行、2026-06-12 更新の旧系）

### 検索語（14件）

`Z` / `0.6036` / `0.8190` / `0.2154` / `0.7477` / `n=218` / `event_z` /
`trajectory` / `canonical` / `正典`(U+6B63,U+5178) / `捏造`(U+637D,U+9020) /
`Gemini` / `statistical` / `z_score`

### 制約（遵守事項）

- **禁止:** DC新規作成 / 遡及登録 / 判断変更 / 推測補完
- **変更禁止成果物:** MOCKA_EVIDENCE_PACKAGE_v0.1.md, Z_CANONICAL_INVESTIGATION_v0.1.md,
  Z_CANONICAL_VERIFICATION_PHASE1.md, Z_DECISION_CONNECTION_AUDIT_v0.1.md（本監査では一切参照変更していない）

---

## Method

1. **正本ledger特定** — `find` により MoCKA 配下の `decision_ledger.jsonl` を列挙。
   `data/decisions/decision_ledger.jsonl`（109行・350,775 bytes・2026-07-15 12:56 更新）を正本、
   `data/ise/decision_ledger.jsonl`（27行・旧系）を副次と同定。
2. **全行パース** — 109行を UTF-8 で読み込み、全行が有効な JSON として parse 可能であることを確認
   （PARSE_FAIL 0件）。レコード構造キー:
   `decision_id, title, context, alternatives, decision, rationale, impact,
   related_events, related_documents, approved_by, approved_at, supersedes, superseded_by, status`。
3. **フィールド単位全文検索** — 各検索語について、上記14フィールド全てを対象に大小文字非依存で
   部分一致検索（`related_events` を含む）。ヒット行・ヒットフィールドを記録。
4. **日本語語のコードポイント確定検索** — 端末が cp932 であり heredoc 経由の日本語リテラルが
   文字化けするため、`正典`=`chr(0x6B63)+chr(0x5178)`、`捏造` は第一字候補域 U+637B..U+6383（`捏`=U+637D を含む）× `造`(U+9020) を UTF-8 スクリプトで直接走査し、誤字リスクを排除。
5. **`Z` 文字の文脈弁別** — `Z` は多義（ISO-8601 の Zulu マーカー、英単語内の Z）。
   `approved_at` 以外の全フィールドで `Z` 出現を前後文脈付きで抽出し、統計的「Z」との弁別を実施。
6. **構造検査** — `status` 分布、`supersedes` / `superseded_by` の充填状況、重複 `decision_id` 行の有無を確認。
7. **副次ledger走査** — `data/ise/decision_ledger.jsonl` に対しても同一14語を走査。

---

## Evidence

### E-1. 全履歴の構造

| 項目 | 値 |
|---|---|
| 総行数 | 109 |
| JSON parse 成功 | 109 / 109（失敗 0） |
| `status` 分布 | **Active: 109（全行）** |
| `superseded_by` 充填行 | **0 行** |
| `supersedes` 充填行 | 6 行（L9, L20, L25, L37, L67, L105） |
| 重複 decision_id | DC_20260707_020(L37,L38), DC_20260712_008(L66,L67), DC_20260713_003(L73,L74) |

`supersedes` 充填の内訳:
`DC_20260705_009→008` / `DC_20260707_003→002` / `DC_20260707_008→007` /
`DC_20260707_020→019` / `DC_20260712_008→008`(自己参照) / `DC_20260715_004→001`。

> **構造上の要点:** 本ledgerの supersession は「新レコード側の `supersedes` による前方宣言」で表現され、
> 被 supersede 側は `superseded_by` を付与されず **Active のまま残置**される。
> したがって「superseded 行 / 過去 version 行」は Active 行とは**別集団として物理的に分離保存されていない**。
> 全 Active 109 行を精査することが、すなわち append-only 全レコードの精査に等しい。

### E-2. 検索語別ヒット数（正本ledger・全109行）

| 検索語 | ヒット行数 | 判定 |
|---|---|---|
| `0.6036` | **0** | 該当なし |
| `0.8190` | **0** | 該当なし |
| `0.2154` | **0** | 該当なし |
| `0.7477` | **0** | 該当なし |
| `n=218` | **0** | 該当なし |
| `event_z` | **0** | 該当なし |
| `trajectory` | **0** | 該当なし |
| `statistical` | **0** | 該当なし |
| `z_score` | **0** | 該当なし |
| `正典` (U+6B63,U+5178) | **0** | 該当なし |
| `捏造` (U+637D,U+9020, 候補域U+637B..U+6383×造) | **0** | 該当なし |
| `Z`（文字） | 109（全て時刻/英単語内・下記E-3参照） | 統計的Zの該当なし |
| `canonical` | 12（全て別文脈・下記E-4参照） | 統計的Z正典と無関係 |
| `Gemini` | 9（全て別文脈・下記E-5参照） | 統計的Zと無関係 |

### E-3. `Z` 文字の弁別

`Z` は 109 行全てにヒットするが、その全数が `approved_at` の ISO-8601 Zulu タイムスタンプ末尾 `...Z` である。
`approved_at` を除外した `Z` 出現は **5件のみ**で、いずれも統計的「Z」とは無関係:

- L33 (DC_20260707_016) `context`: 本文中に埋め込まれた ISO タイムスタンプ 2件
  （`2026-06-09T11:19:50Z` / `2026-06-10T00:13:52Z`）
- L58 (DC_20260711_003) `decision` / `rationale`: 英単語 **AUTHORI`Z`ED** 内の Z
- L98 (DC_20260714_002) `impact`: 英語句 **NOT FINALI`Z`ED** 内の Z

→ **統計量としての「Z」「event Z」「z_score」に該当する Z は 0 件。**

### E-4. `canonical` 12件の文脈（全て別事象）

| L | DC | 文脈要旨 |
|---|---|---|
| 10 | DC_20260705_010 | KN-004 へ canonical な identity として登録する対象の議論 |
| 36–38 | DC_20260707_019/020 | ESSENCE_CANONICAL_MODEL / Canonical Essence 主表示の承認 |
| 39 | DC_20260707_021 | Seal Canonical Source 確定（anchor_record.json） |
| 63 | DC_20260712_005 | Anchor の canonical 40桁 hash |
| 70 | DC_20260712_011 | canonical hash の cross-actor 再現性 |
| 97 | DC_20260714_001 | Canonical doc recorded (D-11) |
| 99–100 | DC_20260714_003/004 | GL7 の canonical 定義 |
| 107, 109 | DC_20260715_006/008 | concept record の `canonical_name` フィールド |

→ いずれも MoCKA の統治概念（identity / essence / seal / anchor / GL7 / concept schema）であり、
**「Z 正典」「捏造された正典」等の統計的争点とは無関係。**

### E-5. `Gemini` 9件の文脈（全て別事象）

- L18–25 (DC_20260707_001/002/003/005/008): Gemini **AIアダプタ接続 / マルチAI E2E送信試験**
- L84–88 (DC_20260713_013/014/016/017): **Gemini二次レビュー（GEM-001/GEM-004 等 findings）** by AUTO_SEAL S0.5

→ AI連携・レビュー体制の文脈であり、**Z-score / trajectory / 統計的捏造とは無関係。**

### E-6. 副次ledger（data/ise/decision_ledger.jsonl・27行）

14語全て **0 ヒット**（`造`(U+9020) の出現自体も 0）。`approved_at` 以外の `Z` 出現も 0。

---

## Finding

**分類: Confirmed（全履歴確認済みで該当なし）**

- append-only 全履歴（正本 109 行 = Active 全行、副次 ise 27 行）を全行・全フィールド精査した結果、
  Z 統計値（0.6036 / 0.8190 / 0.2154 / 0.7477）・`n=218`・`event_z`・`trajectory`・
  `statistical`・`z_score`・`正典`・`捏造` に該当する記載は **一切存在しない（0件）**。
- `Z` の全出現は ISO-8601 時刻マーカーまたは英単語（AUTHORIZED / FINALIZED）内であり、
  統計的「Z」に該当するものは **0件**。
- `canonical`(12) / `Gemini`(9) は存在するが、文脈精査の結果いずれも MoCKA 統治・AI連携の別事象であり、
  Z 統計/正典/捏造の争点とは **無関係**。
- **Conflict（既存判断発見）: なし。** Z の件を扱う既存 Decision が全履歴に存在しないため、
  本監査で新たに発見された相反判断は無い。

本 Finding は先行の Z_DECISION_CONNECTION_AUDIT_v0.1「現行Decision一覧でZ関連DCなし」を
**append-only 全履歴レベルへ拡張し、同一結論（該当なし）を確認**するものである。

---

## Limitation

1. **superseded 行 / 過去 version 行の別集団は存在しない（Not Confirmed 該当ではなく構造事実）。**
   本ledgerは supersession を新レコードの `supersedes` で前方宣言し、被 supersede 行を
   `superseded_by` 付与せず Active 残置する方式のため、「過去 version 行」を Active 行と別に
   走査対象化できない。全 Active 行の精査でカバレッジは満たされるが、
   *`superseded_by` を用いた版管理を前提とした確認*は構造上実施不能。
2. **ledger ファイルの git 過去リビジョン / バックアップ（`MoCKA_backups/` 等）は本監査の走査対象外。**
   本監査は現時点のファイル内容（append-only 累積結果）を対象とし、過去コミット断面や
   別コピーの独立走査は行っていない。
3. **events / integrity 台帳・KN-004・他ドキュメント群は対象外。**
   本監査の scope は decision_ledger（正本 + ise）に限定。`related_events` フィールドは
   走査したが、参照先イベント実体（events.db）の内容までは追跡していない。
4. **`Z` 単一文字の網羅性。** `Z` は多義のため文脈弁別を要した。本監査は全出現を目視弁別したが、
   将来的に統計文脈の `Z` が導入された場合は再走査が必要。

---

## Conclusion

`data/decisions/decision_ledger.jsonl` の **append-only 全履歴（全109行・全 Active・全フィールド）**、
および副次 `data/ise/decision_ledger.jsonl`（27行）を精査した結果、

> **Z 統計値・n=218・event_z・trajectory・z_score・statistical・正典・捏造 に関連する
> Decision は、全 append-only 履歴上に一件も存在しない（Confirmed: 該当なし）。**
> **既存判断との Conflict も検出されなかった。**

`canonical` および `Gemini` の出現は全て MoCKA 統治／AI連携の別事象であり、Z の争点とは無関係である。

これにより、先行 Z_DECISION_CONNECTION_AUDIT_v0.1 の結論は append-only 全履歴レベルにおいても
維持・拡張された。本監査は READ-ONLY であり、DC新規作成・遡及登録・判断変更・推測補完は行っていない。

未確認事項（git 過去リビジョン / バックアップ / events 実体 / KN-004）は上記 Limitation の通り、
別途の監査 scope として残置する。

---

*本文書は監査記録であり、Decision ではない。いかなる判断変更・遡及登録も含まない。*

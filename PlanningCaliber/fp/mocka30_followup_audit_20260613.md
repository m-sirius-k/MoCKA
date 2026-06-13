# MoCKA 3.0 追加検証レポート（Follow-up Audit）
**発行日**: 2026-06-13
**基準文書**: mocka30_architecture_review_20260613.md（正本・上書きなし）
**方針**: 推測禁止・状態確定のみ・実コード/Git履歴ベース

---

## 1. Truth Status Table

| Issue | Report記載 | 実態確認結果 | Final |
|---|---|---|---|
| `interface/router.py` 128行目 `def write_safe_csv(row); write_sqlite(row):` | 「DEPENDENCY_BREAK修正済み」 | **現在も存在**。`python -c "import interface.router"` は L5でSyntaxError、修正後もL128で同様にSyntaxError（`;` を含む不正なdef構文）。 | **FAIL** |
| `interface/router.py` 5行目 mojibake BOM (`﻿`混入) | 未言及 | **現在も存在**。utf-8/utf-8-sig双方でAST解析失敗。 | **FAIL（別件）** |
| DEPENDENCY_BREAK修正コミット | 「修正済み」 | `git status --porcelain interface/router.py` = クリーン（コミット済み状態がそのまま壊れている）。直近3コミット（3827abc01, 64de07c3b, 8e604b60c = Phase4-1/3-2/3-1）はrouter.pyに触れていない。最終変更は `33a6eca6`（2026-04-18, "No-Token Architecture完成"）で、この時点から壊れた状態。 | **FAIL（未修正のまま2ヶ月以上経過）** |

---

## 2. Critical Findings（実害ありのみ）

### Finding 1: `interface/router.py` は import 不可能（2重のSyntaxError）
- **L5**: `﻿import csv, os` — リテラル文字列 `﻿`（6文字、BOMバイトではない）が `import` 文の先頭に混入。`fix_mojibake_final.py` 等の文字化け修正スクリプトの誤爬痕跡と推定されるが、原因追跡は対象外（**状態のみ確定**）。
- **L128**: `def write_safe_csv(row); write_sqlite(row):` — Python構文として無効（`def`内に`;`と関数呼び出しが混在）。意図は `def write_safe_csv(row):` と思われるが、これは**現状のコード**であり修正提案は最後のみとする。

### Finding 2: 影響範囲 — 2ファイルが直接 import している
```
main.py:1            from interface.router import MoCKARouter
runtime/action_executor.py:14   from interface.router import MoCKARouter
```
- これら2モジュールは `interface.router` を import する箇所で**必ず例外発生**（モジュールロード時にSyntaxError）。
- **一方**、商用稼働中の主要エントリポイントである `app.py`（COMMAND CENTER, port 5000）、`mocka_mcp_server.py`（MCP, port 5002）、`caliber/chat_pipeline/mocka_caliber_server.py`（Caliber, port 5679）、`runtime/main_loop.py` は `router`/`MoCKARouter` を一切参照していない（grep結果ゼロ件）。
- → **現在の主要稼働系（5000/5002/5679/main_loop）には影響なし**。影響は `main.py` と `runtime/action_executor.py` 経由の呼び出し経路に限定。これらが現行稼働パスで呼び出されているかは本調査の対象データのみでは**未確認**。

---

## 3. Commercial Risk Update（再スコア 0–100、100=最高リスク）

| 項目 | 評価対象 | スコア | 根拠 |
|---|---|---|---|
| PHI-OS | state破損リスク | **未確認（スコアなし）** | 本follow-upの調査範囲はrouter.py/DEPENDENCY_BREAK/E20260613_087に限定。PHI-OSコードへの新規確認は実施せず、既存レポート記載を変更する根拠なし。 |
| Orchestra | loop/scheduling risk | **未確認（スコアなし）** | 同上。`runtime/main_loop.py`がrouter.pyを参照しないことのみ確認済み（router.py破損の直接波及なし）。 |
| Relay | session restore risk | **未確認（スコアなし）** | 本調査範囲外。 |
| Memory | index consistency risk | **未確認（スコアなし）** | `data/mocka_events.db`等への直接調査は本follow-upでは未実施。 |

**router.py破損自体の商用リスク**: **35/100**
- 根拠: 主要4エントリポイント（app.py / mcp_server / caliber_server / main_loop）は無影響。ただし `main.py`・`runtime/action_executor.py` 経由のパスが商用フローに含まれる場合は実行時クラッシュが確定（FAIL確定要素のため、影響範囲が確認されない限り0扱いにはできない）。

---

## 4. Regression Risk

- **再発可能性**: 高。L5のmojibake混入は文字化け修正スクリプト（`fix_mojibake_final.py`等）の自動処理に起因する可能性があるパターンであり、同種スクリプトが他ファイルにも適用されていれば同様の破損が他ファイルにも存在し得る（**本follow-upでは他ファイルへの横展開調査は未実施**）。
- **hidden dependency**: `main.py` / `runtime/action_executor.py` が実際にどの起動経路（cron, MCP, Orchestra）から呼ばれるかは未確認。これが判明しない限り「実害なし」と確定できない。
- **runtime risk**: router.py破損は**2026-04-18から継続**（最終コミット33a6eca6以降、後続のPhase3-1/3-2/4-1コミットでも未修正）。約2ヶ月間検知されずに存在していたことは、CI/起動時インポートチェックの欠如を示す。

---

## 5. mocka_write_event（E20260613_087）整合性確認

- イベント自体は `mocka_events.db` へ記録済み（前回agent報告: event_id E20260613_087）。
- 本イベントの内容（「アーキテクチャ整理レポート生成完了」）と、今回のrouter.py FAIL検出は**別事象**であり、E20260613_087はrouter.py破損の修正完了を意味しない。
- 既存レポート（mocka30_architecture_review_20260613.md）の「DEPENDENCY_BREAK修正済み」記載と、E20260613_087時点の実コードとの間に**矛盾あり**（記載＝修正済み、実態＝未修正）。これは既存レポート本文の修正ではなく、本follow-up文書での矛盾指摘として記録する。

---

## 6. Final Verdict

# **SELLABLE BUT FIX REQUIRED**

判定根拠:
- 主要4商用エントリポイント（app.py / mocka_mcp_server.py / mocka_caliber_server.py / runtime/main_loop.py）は `interface/router.py` を参照せず、即時の商用停止リスクはない。
- ただし `interface/router.py` は現状**インポート不可能**（2重のSyntaxError）であり、これに依存する `main.py` / `runtime/action_executor.py` 経路は確実にクラッシュする。既存レポートの「修正済み」記載は実態と不一致（FAIL確定）。
- PHI-OS / Orchestra / Relay / Memory の再スコアは本follow-upの調査範囲では実施しておらず、既存レポートのスコアを変更する根拠はない。

---

## 7. 修正提案（最後のみ・本follow-upでは未実施）

1. `interface/router.py` L5の `﻿` リテラル文字列除去。
2. `interface/router.py` L128 `def write_safe_csv(row); write_sqlite(row):` の構文修正（`def write_safe_csv(row):` への変更が妥当と推定されるが、実装は別タスクとする）。
3. 修正後、`main.py` および `runtime/action_executor.py` のimportが正常に解決することを確認。
4. CI/起動時に主要モジュールのimport健全性チェック（`python -m compileall` 等）を追加し、同種の破損の早期検知を可能にする。
5. `fix_mojibake_final.py` 等の文字化け修正スクリプトが他ファイルにも同様の破損を生んでいないか、別タスクで横展開調査を実施。

---
*本文書は mocka30_architecture_review_20260613.md を上書きしない。矛盾点はFollow-up文書として本ファイルに記録した。*

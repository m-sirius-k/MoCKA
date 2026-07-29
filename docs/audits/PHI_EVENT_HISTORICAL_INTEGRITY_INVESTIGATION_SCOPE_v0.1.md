# PHI Event Historical Integrity Investigation Scope v0.1

**Status:** SCOPE(調査対象・仮説の固定。原因確定はまだ行わない)
**位置づけ:** PHI-REG-04 Compliance Review Observation(`E20260729_609117955548c`)を受けたHistorical Integrity Investigationの開始文書。
**目的(きむら博士指定):** 2026-06-07に生成されたPHI-REG-04由来Eventが現在Ledger上に存在しない理由を、Evidence Chainに基づいて特定する。対象は**原因究明**であり、**違反者・責任追及ではない**。
**実装・Decision Ledger登録:** 本文書には一切含まない。

---

## 1. 確定している事実(前提、`PHI_REG04_COMPLIANCE_REVIEW_FINDINGS_v0.1.md`より)

- 2026-06-07 15:29:23: `seo_os.log`にINSERT成功ログあり(`event_id=EPHIOS_DEC_20260607_152923`)
- 現在: 該当Eventなし(`data/mocka_events.db`に0件)
- 現在Ledger: 全18,253件が署名済み(unsigned 0件)

**避けるべき結論(きむら博士指定)**: 「Eventが消えた=改ざん」と断定しないこと。消失経路が判明するまでは**Integrity Issue**として扱い、原因分類は保留する。

---

## 2. 対象Evidence

| 対象 | 確認内容 |
|---|---|
| `seo_os.log` | INSERT+COMMIT成功記録の保存状態(確認済み、本文書§1に反映) |
| `event_id` | `EPHIOS_DEC_20260607_152923`相当レコードの追跡(現DB・バックアップ・他ストア横断) |
| TODO_322関連資料 | DB移行方針・実施記録の原文確認 |
| 移行スクリプト | CSV→SQLite移行時の処理内容確認 |
| 移行前データ | 元イベントの存在確認(CSV等の移行元データ) |
| 移行後Validation | 件数・Hash・整合性確認記録(TODO_322記載のseal値等) |

---

## 3. 仮説管理

### Hypothesis H1
> 「2026-06-16 DB移行時にCSV廃止・SQLite一本化処理の過程で対象Eventが移行対象外となった」

**状態:** 未検証

### Hypothesis H2
> 「別経路による削除・除外が発生した」

**状態:** 未検証

### Unknown

- 実際の移行元ファイル
- 移行スクリプトの対象条件
- 対象Eventの最終確認地点

---

## 4. 調査手順(読み取り専用)

1. `event_id`横断追跡: 現DB以外(バックアップファイル、`.EMPTY_GHOST_*`等の疑わしい命名ファイル、他のデータストア)に`EPHIOS_DEC_20260607_152923`または類似パターンが残存しないか確認
2. TODO_322の原文・関連ドキュメントを`MOCKA_TODO_ARCHIVE.json`等から再確認
3. 2026-06-16前後のCSV→SQLite移行スクリプトを特定し、対象条件(何を移行し何を除外したか)を確認
4. 移行元CSVデータ(存在すれば)に該当Eventの痕跡があるか確認
5. TODO_322記載の"seal: 70998382 ALL CHECKS PASSED"等、移行後Validation記録の内容を確認

---

## 5. 分岐条件(調査完了後)

- **移行処理起因確認** → Change/Process改善(別トラック)
- **削除経路確認** → Incident扱い(別トラック)
- **証拠不足継続** → Known Unknownとして保存

いずれの分岐が発生した場合も、本Scope文書自体は変更せず、`PHI_EVENT_HISTORICAL_INTEGRITY_INVESTIGATION_REPORT_v0.1.md`(調査完了後に作成)側で結果を記載する。

---

## Knowledge Lineage

**Document:** PHI_EVENT_HISTORICAL_INTEGRITY_INVESTIGATION_SCOPE_v0.1.md
**Status:** SCOPE
**Created:** 2026-07-29
**Origin:** PHI-REG-04 Compliance Review Observation(`E20260729_609117955548c`)を受け、きむら博士よりHistorical Integrity Investigation開始の承認と、Scope文書先行作成の指示を受けた。
**Parent Documents:**
- docs/audits/PHI_REG04_COMPLIANCE_REVIEW_FINDINGS_v0.1.md
- Event Ledger: E20260729_609117955548c
**Derived From:** PHI_REG04_COMPLIANCE_REVIEW_FINDINGS_v0.1
**Supersedes:** なし
**Reason For Creation:** Investigation本体着手前に、目的限定・対象Evidence・仮説管理・分岐条件を固定するため。
**Affected Components:** PHI-REG-04(`phi_os_bridge.py`)、`data/mocka_events.db`、TODO_322関連資料
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。対象Evidence・仮説H1/H2・Unknown・調査手順・分岐条件を記載。調査本体・実装・Decision Ledger登録は無し。

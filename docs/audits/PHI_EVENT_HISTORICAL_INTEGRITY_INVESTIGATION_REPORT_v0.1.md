# PHI Event Historical Integrity Investigation Report v0.1

**Status:** REPORT(調査結果。原因分類は依然として保留)
**位置づけ:** `PHI_EVENT_HISTORICAL_INTEGRITY_INVESTIGATION_SCOPE_v0.1.md`に基づく調査結果。
**実施した調査行為:** 5件のバックアップDB(`data/mocka_events.db.bak_20260619_094742`等)への読み取り専用SQLクエリ、`mocka_search`によるEvent Ledger検索、`scripts/`ディレクトリの静的検索。**DBへの書込・スキーマ変更・コード変更は一切行っていない。**
**実装・Decision Ledger登録:** 本文書には一切含まない。

---

## 1. Hypothesis H1(当初形)の反証(Confirmed)

Scope文書のHypothesis H1は「2026-06-16 DB移行時にCSV廃止・SQLite一本化処理の過程で対象Eventが移行対象外となった」というものだったが、その根拠として当初想定していた`mocka_events.db.EMPTY_GHOST_20260616`(0バイト)は、**調査の結果まったくの無関係と判明した**。

Event Ledger(`E20260616_023`、原文):
> 「追加スコープ: root直下ゴーストファイル(mocka_events.db, size=0, **2026-05-01作成**)を`mocka_events.db.EMPTY_GHOST_20260616`にリネーム済み。承認根拠: `data/mocka_events.db`(34MB・正規)との混同リスク排除。**誰も書き込んでいない空ファイル**の無効化処置として妥当。」

このファイルは`MoCKA/mocka_events.db`(root直下)にあった、2026-05-01作成時点から一度も書き込まれたことのない別ファイルであり、正規の`data/mocka_events.db`(`phi_os_bridge.py`が接続する対象)とは物理的に別物である。2026-06-16に行われたのは、この無関係な空ファイルを紛らわしくないよう改名しただけの整理作業であり、**正規DBのリセット・空化ではない**。

**結論: 当初想定したH1(ゴーストファイルによるリセット説)は誤りであり、棄却する。**

---

## 2. Phase4移行の実態(Confirmed、Event Ledger原文)

`E20260616_059`(2026-06-16T01:08:43 UTC、`PHASE4_DONE + TODO_322完了`)の原文:

> 「Phase 4完了・TODO_322全Phase完了。seal: commit 70998382 ALL CHECKS PASSED / DB確定値: 11,929件。
> Step1: legacy_tagger 10,662件変換
> Step2: unknown_actor_fixer 3,205件変換
> Step3: csv_migrator 21件追加
> Step4: スキップ
> **Step5: 破損26件削除 ALL CHECKS PASSED**
> Step6: events.csv→archive/legacy/ SHA-256:31591b2a封印
> Step7: mocka-seal commit 70998382 ALL CHECKS PASSED」

この記録から確認できること(Confirmed):
- Phase4移行は**既存の`data/mocka_events.db`に対する加工処理**(再タグ付け・actor修正・CSV由来21件の追加・破損26件の削除)であり、DB全体を空にして作り直す全面リセットではなかった
- CSVからの新規追加は21件のみ(Step3)であり、CSVへの一本化=既存SQLiteデータの置き換えではない
- **Step5で「破損」と判定された26件が削除されている**

---

## 3. 精緻化されたHypothesis H1'(未確定、新規)

**Hypothesis H1'**: 2026-06-07の`phi_os_bridge.py`由来イベント(`EPHIOS_DEC_20260607_152923`)は、`phi_os/event_gate.py`の`process_event()`/`_write()`を経由しない手書きINSERTで生成されたため、正規のGate経由イベントが満たすスキーマ・整合性条件を満たしていなかった可能性がある。Phase4 Step5の「破損26件削除」は、まさにこの種の非正規フォーマットの行を「破損」と判定し削除する処理だった可能性がある。

**状態: 未検証。** 以下の理由により、これ以上の直接確認ができなかった:
- Step5が「破損」と判定した26件の具体的な`event_id`一覧は、`mocka_search`で検索した範囲のEvent Ledlogには記載されていない
- Step1〜3で言及される`legacy_tagger`・`csv_migrator`・`unknown_actor_fixer`という処理名に対応するスクリプトファイルは、`scripts/`配下に現存しない(検索0件。一回限りの使い捨てスクリプトとして実行後に保存されなかった可能性がある)

---

## 4. バックアップDB調査結果(Confirmed)

Scope文書で列挙した5件のバックアップDB(いずれも2026-06-19/06-20付、Phase4完了後のスナップショット)に対する読み取り専用クエリ結果:

| ファイル | 総件数 | `EPHIOS%`該当件数 |
|---|---|---|
| `mocka_events.db.bak_20260619_094742` | 12,259 | 0 |
| `mocka_events_pre_event_integrity_20260620_170031.db` | 12,564 | 0 |
| `mocka_events_pre_event_integrity_20260620_170129.db` | 12,565 | 0 |
| `mocka_events_pre_phase522_backfill_20260620_173943.db` | 12,599 | 0 |
| `mocka_events_pre_source_check_20260620_162028.db` | 12,540 | 0 |
| (参考)現行`data/mocka_events.db` | 18,258 | 0 |

いずれのスナップショットにも該当イベントは存在しない。これらはすべてPhase4(2026-06-16)完了**後**のスナップショットであるため、この結果は「Phase4完了後は一貫して存在しない」ことを示すのみで、Phase4完了**前**の状態は直接確認できていない(Phase4完了前のDBスナップショットは発見できなかった)。

### 4.1 CSVバックアップの確認(Confirmed、対象外)

`data/events_backup_20260401_132453.csv`・`events_backup_20260416_121018.csv`・`events_backup_before_idfix.csv`(2026-04-11)・`events_legacy_backup.csv`(2026-03-26)はいずれも2026-06-07(対象イベント発生日)より前の日付であり、時系列上、対象イベントを含み得ない。これらに`EPHIOS`文字列がヒットしないことも確認済みだが、これは調査上の意味を持たない(該当時期より前のため)。

---

## 5. 追加確認: 誤検知の訂正(重要、自己修正)

本調査中に`data/mocka_events.db`ファイル全体をバイト文字列として`grep`した際、`EPHIOS_DEC_20260607_152923`という文字列がヒットした。しかし内容を直接確認した結果、**これは本Investigation自身が本セッション内で書き込んだObservationイベント(`E20260729_609117955548c`、タイトル「OBSERVATION: EPHIOS_DEC_20260607_152923 Historical Integrity Gap」等)の説明文中に、調査対象のevent_idを文字列として引用していたことによる誤検知だった。** 元の2026-06-07イベント本体のものではない。

この誤検知を踏まえ、より意味のある確認として以下を追加実施した(いずれもConfirmed、0件):
- `data/events_corrupted.csv`(Step5「破損26件削除」に関連しそうな名称のファイル)を検索 — 該当event_idヒットなし
- `archive/legacy/events.csv`(Step6でCSVが封印されたとされる先)を検索 — 該当event_idヒットなし
- `data/events.csv`・`data/events_before_repair.csv`を検索 — 該当event_idヒットなし

これらのファイルにも痕跡がなかったことは、Hypothesis H1'(破損26件に含まれていた)を直接支持も反証もしない。これらのCSVがStep5の削除対象と直接対応する保証がないためである(移行プロセスの内部詳細が未追跡のため)。

**教訓として明記**: grep等の全文検索で得たヒットは、調査対象そのものの痕跡か、調査プロセス自身が生成した参照(本Investigationの記録等)かを必ず区別する必要がある。今回は区別を怠らず、誤った結論(「現DBに痕跡が残っている」)として報告する前に発見・訂正できた。

---

## 6. 総括

| 項目 | 判定 |
|---|---|
| 当初Hypothesis H1(ゴーストファイル説) | **棄却(Confirmed反証)** |
| Hypothesis H1'(Phase4 Step5「破損26件削除」に含まれていた可能性) | 未検証(具体的根拠と整合するが直接確認不能) |
| Hypothesis H2(別経路削除) | 未検証(否定も肯定もする材料が増えていない) |
| Phase4移行がDB全体をリセットしたか | **Confirmed: していない**(既存データへの加工処理) |
| Phase4完了前のDBスナップショット | 発見できず(調査の限界) |
| 移行スクリプト実体 | 発見できず(scripts/配下に現存しない) |
| 現在のLedger整合性 | Confirmed: 18,258件全件署名済み、異常なし |

**結論**: 「Eventが消えた=改ざん」と断定できる根拠は見つからなかった一方、「通常のGate経由データがそのまま消えた」という単純な説明もできない。最も証拠と整合するのは**Hypothesis H1'(非正規フォーマットの行としてPhase4 Step5で「破損」判定・削除された)**だが、これを確定させる一次資料(削除された26件のevent_id一覧、または当時のスクリプト実体)は今回の調査範囲では発見できなかった。

きむら博士の指示通り、**原因分類は保留し、Known Unknownとして本Reportに記録する。** 追加のEvidence(削除された26件のリストやスクリプトの発見等)が得られない限り、これ以上の追跡は困難である。

---

## Knowledge Lineage

**Document:** PHI_EVENT_HISTORICAL_INTEGRITY_INVESTIGATION_REPORT_v0.1.md
**Status:** REPORT
**Created:** 2026-07-29
**Origin:** PHI_EVENT_HISTORICAL_INTEGRITY_INVESTIGATION_SCOPE_v0.1.mdに基づき調査を実施。
**Parent Documents:**
- docs/audits/PHI_EVENT_HISTORICAL_INTEGRITY_INVESTIGATION_SCOPE_v0.1.md
- docs/audits/PHI_REG04_COMPLIANCE_REVIEW_FINDINGS_v0.1.md
- Event Ledger: E20260616_023、E20260616_059
**Derived From:** PHI_EVENT_HISTORICAL_INTEGRITY_INVESTIGATION_SCOPE_v0.1
**Supersedes:** なし
**Reason For Creation:** Scope文書で固定した調査手順を実施し、Hypothesis H1/H2の検証結果と新規Hypothesis H1'を記録するため。
**Affected Components:** PHI-REG-04(`phi_os_bridge.py`)、`data/mocka_events.db`(参照のみ、変更なし)
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。H1(当初形)の反証、Phase4移行の実態、精緻化H1'、バックアップDB調査結果、総括を記載。原因分類は保留(Known Unknown)。DBへの書込・コード変更・Decision Ledger登録は無し。

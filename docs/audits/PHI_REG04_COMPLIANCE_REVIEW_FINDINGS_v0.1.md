# PHI-REG-04 Compliance Review Findings v0.1

**Status:** FINDINGS(レビュー本体の結果。Decision化・実装修正はまだ行わない)
**位置づけ:** `PHI_REG04_COMPLIANCE_REVIEW_SCOPE_DRAFT_v0.1.md`で定義したScopeに基づき実施したレビュー結果。
**実施した調査行為:** `data/mocka_events.db`(`events`/`event_signatures`テーブル)への読み取り専用SQLクエリ、`seo_os.log`の全文検索、`phi_os/integrity.py`の読解、`seo-os`配下の静的import検索。**書込・スキーマ変更・コード変更は一切行っていない。**
**実装・Decision Ledger登録:** 本文書には一切含まない。

---

## 1. Registration事実確認

### 1.1 コード実装(Confirmed、既報告の再確認)

`phi_os_bridge.py`(`PlanningCaliber/workshop/seo-os/mocka/`)は`push_decision_audit()`・`push_policy_violation()`の両メソッドで`sqlite3.connect(MOCKA_DB)`により`data/mocka_events.db`へ直接接続し、生の`INSERT INTO events`文を実行する設計になっている。`phi_os/event_gate.py`の`process_event()`/`_write()`を経由せず、`integrity.sign_event()`も呼び出さない。

### 1.2 実行実績(Confirmed、新規確認)

`PlanningCaliber/workshop/seo-os/logs/seo_os.log`(2026-06-07〜2026-07-29、5,897行)を全文検索した結果、`PHIOSBridge`関連のログ出力は以下の1件のみ:

```
2026-06-07 15:29:23,548 [INFO] [PHIOSBridge] 監査記録: EPHIOS_DEC_20260607_152923
```

このログはコード上、`conn.commit()` + `conn.close()`実行後にのみ出力される(`push_decision_audit()`のtry節末尾)。したがって**2026-06-07 15:29:23時点で、当時のDB接続先に対してINSERT + COMMITが成功したことをコード自身が記録している**。

### 1.3 現在のDB状態(Confirmed、新規確認・読み取り専用クエリ)

`data/mocka_events.db`に対する読み取り専用クエリの結果:

| クエリ | 結果 |
|---|---|
| `event_id LIKE 'EPHIOS%'` | **0件**(1.2のログが記録した`EPHIOS_DEC_20260607_152923`を含め、EPHIOS接頭辞のイベントは現在DBに1件も存在しない) |
| `where_component='phi_os_bridge' OR who_actor='SEO-OS/PHI-OS'` | **0件** |
| 現在の`events`テーブル総件数 | 18,253件 |
| うち`event_signatures`(署名)が存在しない件数 | **0件(100%署名済み)** |

### 1.4 呼び出し元の静的検索(Confirmed、限定的)

`seo-os`配下の`*.py`を対象に`phi_os_bridge`/`PHIOSBridge`をgrep検索した結果、ヒットするのは`phi_os_bridge.py`自身のみ(クラス定義・ログ文字列)。**`seo-os`配下の静的コードには、`PHIOSBridge`をimport・インスタンス化する呼び出し元が見つからなかった。**

**限定範囲(Scope-limited、Unknown)**: この検索は`seo-os`ディレクトリ配下の`.py`ファイルに限定しており、動的import・他リポジトリからの参照・subprocess経由の呼び出し等は検索対象外である。「呼び出し元が見つからない」ことは「呼び出されていない」ことの証明ではない。

---

## 2. Constitution照合

`PHI_OS_CONSTITUTION_v1.md`第2章原則4「DBは保存媒体であり真実ではない」(「DBへの直接書き込みによるEvent生成は制度違反である」)、第5章5.1「DB直接更新によるEvent生成」禁止事項に照らすと:

- **コード設計としては、原則4・5.1に抵触する(Confirmed、1.1参照)。** この評価はコードが実際に実行されたかどうかとは独立して成立する(違反可能な設計自体が禁止事項に該当するため)。
- **ただし、現在のライブDB(`data/mocka_events.db`)には、この設計上の違反が生み出した具体的なレコードは1件も現存しない(Confirmed、1.3参照)。** 2026-06-07の実行実績はコード自身のログにより裏付けられるが、その結果生成されたはずのイベント行は現在のDBに存在しない。

**結論**: 本Compliance Reviewが確認すべき「登録機構がConstitutionに従って動作しているか」という問いに対しては、**「コードは違反可能な設計のままであるが、現時点のライブデータには違反の痕跡が残っていない」**という二層の答えになる。「違反が今も進行中でDBを汚染し続けている」という状態ではない。

---

## 3. Evidence Chain確認

期待される流れ(Constitution → Implementation → Decision Reference → Event Ledger → Verification Result)に沿って整理する。

| 段階 | 状態 |
|---|---|
| Constitution | 原則4・5.1、RATIFIED v1として存在(Confirmed) |
| Implementation | `phi_os_bridge.py`が原則4・5.1に抵触する設計であることをコード読解で確認済み(Confirmed) |
| Decision Reference | `MOCKA_PHI_OS_IDENTITY_AUDIT_v1.md`§7(2026-06-24)が本違反候補を「別途確認要」として初めて記録。**本日(2026-07-29)まで、この違反候補を正式に解消・裁定するDecision(`DC_`)は作成されていない(未検索でヒット無し)。** |
| Event Ledger | `phi_os/integrity.py`の`verify_chain()`は`unsigned_event`(署名なしイベント)を明示的に検知する機構を備えている(Confirmed、コード確認済み)。**しかし現在のDBには署名なしイベントが1件も存在しない(1.3参照)ため、この検知機構が phi_os_bridge由来のレコードを捕捉する機会自体が現時点では存在しない。** |
| Verification Result | 上記の通り、現在のDBは`verify_chain()`的な意味で「異常なし」の状態にある。これは違反が是正されたことの証明ではなく、**違反によって生成された記録が(理由不明のまま)現存しないために検知対象が無いだけ**という可能性がある。 |

### 3.1 2026-06-07の記録が現存しない理由について(Hypothesis、未確定)

`EVENT_GATE_CANONICAL_PATH_REPORT_v1.md`(本セッション既読)が引用するTODO_322原文は「2026-06-16 Phase1〜4完了...(1)CSV廃止(2)SQLite一本化...DB: 11,929件...CSV時代終了・GATE単一経路確立」と記録しており、2026-06-07の9日後にあたる2026-06-16にDB/スキーマの大規模な移行(CSVからSQLiteへの一本化)が完了している。

**Hypothesis(未確定)**: この2026-06-16移行が、移行前(CSV時代)に書き込まれた`phi_os_bridge.py`由来の06-07レコードを引き継がなかった可能性がある。時系列は整合するが、本レビューでは移行スクリプト自体を追跡しておらず、この因果関係を直接確認したわけではない。**削除・改ざんという別種のConstitutional Violationが発生した可能性も、この時点では排除できていない。**

---

## 4. 総括

| 項目 | 判定 |
|---|---|
| コード設計上の原則4・5.1抵触 | Confirmed(継続中、コードは現状のまま) |
| 2026-06-07の実行実績 | Confirmed(ログ証跡) |
| 現在DBへの残存 | Confirmed: 残存なし(0件) |
| 署名なしイベントの現存 | Confirmed: 0件(現在のDBは100%署名済み) |
| 記録消失の原因 | Hypothesis(TODO_322の2026-06-16移行が原因である可能性、未確定) |
| 呼び出し元の有無(seo-os内) | Confirmed: 静的には見つからず。Unknown: 検索範囲外の呼び出しは排除できない |
| 2026-06-24監査以降の正式Decision | Confirmed: 存在しない(未検索でヒット無し) |

**Authority Pending状態(`DC_20260729_009`)との関係**: 本Findingsはいずれも`PHI_OS_CONSTITUTION_v1.md`原則4・5.1という、Authority Flow(PHI-Con/PHI-Core間の統治方向)の確定・未確定に依存しない条項のみを判定基準としており、Scope Draft§2の前提通り`DC_20260729_009`への影響はない。

---

## Knowledge Lineage

**Document:** PHI_REG04_COMPLIANCE_REVIEW_FINDINGS_v0.1.md
**Status:** FINDINGS
**Created:** 2026-07-29
**Origin:** PHI_REG04_COMPLIANCE_REVIEW_SCOPE_DRAFT_v0.1.mdの承認を受け、レビュー本体を実施。
**Parent Documents:**
- docs/audits/PHI_REG04_COMPLIANCE_REVIEW_SCOPE_DRAFT_v0.1.md
- docs/audits/MOCKA_PHI_OS_IDENTITY_AUDIT_v1.md
- PHI_OS_CONSTITUTION_v1.md
- docs/consolidation/EVENT_GATE_CANONICAL_PATH_REPORT_v1.md(workshop/phi-os/)
**Derived From:** PHI_REG04_COMPLIANCE_REVIEW_SCOPE_DRAFT_v0.1
**Supersedes:** なし
**Reason For Creation:** Scope Draftで定義した3段階(Registration事実確認/Constitution照合/Evidence Chain確認)を実施し、次のHuman Gate判断(Observationのみ/新規Decision/Change Record+修正工程のいずれに分岐するか)の材料とするため。
**Affected Components:** PHI-REG-04(`phi_os_bridge.py`)、`data/mocka_events.db`(参照のみ、変更なし)
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。Registration事実確認(コード設計/実行実績/現DB状態/呼び出し元検索)、Constitution照合、Evidence Chain確認、総括を記載。DBへの書込・コード変更・Decision Ledger登録は無し。

# E-001 Technical Specification v1.0

**文書種別:** MoCKA技術仕様書。E-001事象そのものの技術記録。判断の手順を定める文書ではない（手順はE001_HUMAN_GATE_TECHNICAL_SPECIFICATION_v1.0.mdが担う。本文書はその適用結果としての技術記録に専念する）。

---

## 1. Overview

**対象事象:** PROJECT_501/MRS-001（`mocka-knowledge-gate`リポジトリ内の追加物一式）のcommit・push。

**発生日時:** 2026-07-11 14:20:10 +0900

**対象リポジトリ:** `mocka-knowledge-gate`（`C:/Users/sirok/mocka-knowledge-gate`、remote: `https://github.com/m-sirius-k/MoCKA-KNOWLEDGE-GATE.git`、公開）

**対象成果物:** `docs/research/PROJECT_501_NIST_RUNTIME_GOVERNANCE_ASSESSMENT/`一式（23ファイル、commit `ecab6c005aa773329a0dd0d4c80c0aba89d59b01`にて1324行挿入）

**作成目的:** 本事象をMoCKA Governance Architecture上の技術事例として記録し、今後の再現性・検証性・制度設計改善に利用可能な仕様書へ変換する。

---

## 2. Authorization Context

commit・pushは、きむら博士（最高責任者）の承認済み操作として記録する（Decision Ledger `DC_20260711_003`、E001-DEC-A = Yes）。

**許可経路:** Human Gate裁定入力（チャット、2026-07-11）→ Decision Ledger登録（`DC_20260711_003`）→ 読み戻し確認（`mocka_decision_get`）→ `E001_HUMAN_GATE_DECISION_SHEET_v1.0.md`への反映、という経路で記録された。これはPC所有者であることの技術的証明ではなく、Human Gateにおいて最高責任者としての裁定入力が提示されたことに基づく記録である。

**記録上の位置づけ:** 操作の正当性（Operation）と記録タイミング（Recording）を別属性として管理する。

| 属性 | 値 |
|---|---|
| Operation | AUTHORIZED |
| Recording | POST_FACTO_RECORDING |

Operation属性は操作自体がきむら博士の承認済みであったことを示す。Recording属性は、対応するCHANGE_START/CHANGE_DONEおよび事前Decision Record接続が操作実行より後追いであったことを示す。両属性は独立して管理され、一方が他方の評価を変更しない。

---

## 3. System Architecture Context

### 3.1 Component Flow Diagram

本事象が関与したコンポーネント間の接続を、実行時点(操作時)と事後補完(2026-07-11)の2段に分けて示す。

```
[実行時点: 2026-07-11 14:20 JST]

  mocka-knowledge-gate (working tree)
        |
        | git commit ecab6c0
        v
  local commit (ecab6c005aa773329a0dd0d4c80c0aba89d59b01)
        |
        | git push
        v
  origin/main (public remote, github.com/m-sirius-k/MoCKA-KNOWLEDGE-GATE.git)
        |
        X-- CHANGE_START/CHANGE_DONE --> MoCKA Event Ledger   [未接続, EV-001-F5/F6]
        |
        X-- 事前許可記録 --> MoCKA Decision Ledger            [未接続, EV-001-F7]


[事後補完: 2026-07-11 (本日)]

  E001_FACT_COLLECTION_REPORT_v1.0.md (EV-001-F1〜F9)
        |
        v
  E001_HUMAN_GATE_DECISION_SHEET_v1.0.md (DEC-A〜D記入)
        |
        v
  MoCKA Decision Ledger: DC_20260711_003
    (Operation=AUTHORIZED / Recording=POST_FACTO_RECORDING)
        |
        v
  E001_TECHNICAL_SPECIFICATION_v1.0.md (本文書)
```

実行時点のフローでは、commit/pushの結果は公開リモート(origin/main)まで到達したが、Event LedgerおよびDecision Ledgerへの接続(上図の「X--」)は発生していない。この2本の未接続を事後補完したものが、下段のDecision Ledger `DC_20260711_003`および本仕様書である。

### 3.2 Component Impact Table

| コンポーネント | 本事象との関係 | 影響(Impact) |
|---|---|---|
| Event Ledger | 本操作に対応するCHANGE_START/CHANGE_DONEイベントは操作実行時点では記録されていなかった（EV-001-F5/F6）。 | 操作実行から本仕様書作成(2026-07-11)までの期間、Event Ledger上には当該commit/pushの直接記録が存在しない空白区間が生じた。本仕様書自体がその区間を埋める補完記録として機能する。 |
| Decision Ledger | 本操作を事前に許可する決定記録は存在しなかった（EV-001-F7）。`DC_20260711_003`により事後的に記録された。 | Decision Ledgerのスキーマに「Operation」「Recording」という2属性を用いた記録パターンが1件追加された。以後、同種の「操作は許可されていたが記録が後追い」の事例で再利用可能な記録形式となる。 |
| Knowledge Gate | `mocka-knowledge-gate`はMoCKAの知識取り込み経路の一つであり、PROJECT_501/MRS-001は当該リポジトリ内の追加物として位置づけられる。 | リポジトリ自体の内容(PROJECT_501/MRS-001)はDEC-D=Allowedにより参照可能な状態になったが、Knowledge Gate側の取り込み処理(MoCKA本体への正式反映)は本仕様書の範囲に含まれず、別途の判断事項として残る。 |
| Transparency Layer | 本仕様書・`E001_HUMAN_GATE_DECISION_SHEET_v1.0.md`・`E001_FACT_COLLECTION_REPORT_v1.0.md`の相互参照により、事後からでも経緯を追跡可能な状態を構成する。 | 3文書間の相互参照(related_documents)により、operation-recording分離モデルの適用事例として第三者が後から検証できる経路が確立された。 |
| Institutional Memory | Decision Ledger・Event Ledgerへの記録により、本事例は今後のMoCKA運用改善検討における参照事例として保持される。 | DEC-C(記録経路の改善対象)確定により、Authorization・Execution Evidence・Ledger Recordの接続タイミング改善が、今後のMoCKA運用改善のTODO候補として制度記憶に残る。 |
| Verification Debt | 本事象は`VERIFICATION_DEBT_PHASE1_CLOSURE_REPORT_v1.0.md`においてE-001としてPENDING_DECISIONに分類されていた。 | DEC-A〜Dの確定によりOperationの側面は解消したが、DEC-E（§7参照）が未確定のため、Human Gate全体としてのTerminal Stateには未到達であり、当該報告書のE-001エントリ更新は本仕様書の範囲に含めない。 |

---

## 4. Execution Flow

| 項目 | 期待フロー | 実行フロー |
|---|---|---|
| CHANGE_START | 変更着手前に`mocka_write_event(CHANGE_START)`を記録 | 記録なし（EV-001-F5/F6） |
| 作業実行 | Writeツールによるファイル生成、CP932汚染防止規約準拠 | PROJECT_501/MRS-001一式23ファイルを作成（生成手順の詳細は本仕様書のEvidence範囲外） |
| commit | `mocka_git_safe_commit()`経由での実行 | commit `ecab6c0`として実行（実行経路の詳細確認は本仕様書のEvidence範囲外） |
| push | 検証ステップを経由した`push=True`運用に沿う | 公開リモートへ直接push。`git reflog show origin/main`にて`refs/remotes/origin/main@{0}: update by push`として反映確認済み（EV-001-F3） |
| CHANGE_DONE | 変更後に`mocka_write_event(CHANGE_DONE)`を記録 | 記録なし（EV-001-F5/F6） |
| Ledger記録 | 操作前にDecision Ledgerでの許可記録が存在する | 操作時点では記録なし（EV-001-F7）。2026-07-11、Decision Ledger`DC_20260711_003`として事後記録（POST_FACTO_RECORDING） |

---

## 5. Technical Gap Analysis

| Control Point | 設計状態 | 実績状態 | 改善点 |
|---|---|---|---|
| Decision Record接続 | 変更操作は事前のDecision Ledger記録を伴う設計（MoCKA CLAUDE.md「Decision Ledgerへの記録義務」） | 事前記録なし。事後記録（`DC_20260711_003`）で補完 | Authorization → Execution Evidence → Ledger Recordの接続を操作前に完了させる運用フックの検討 |
| CHANGE_START/CHANGE_DONE記録 | ファイル変更・git操作の前後に`mocka_write_event`で記録する設計 | 記録なし（EV-001-F5/F6） | push等の外部反映を伴う操作について、記録の有無を事前に検知する仕組み（例: pre-push hookでのLedger照合）の検討余地 |
| Human Gate個別分解 | 単一の可否判定ではなく、許可・指示逸脱判定・記録是正・参照可否・表記是正を独立した決定点として分離する設計（`E001_HUMAN_GATE_TECHNICAL_SPECIFICATION_v1.0.md`） | 5項目中4項目（DEC-A〜D）が確定。1項目（DEC-E）は論点分離の上でPending維持 | 複数の論点が混在する事象を単一の裁定に集約せず、独立した決定点として扱う設計が機能した実例として記録する |

---

## 6. Evidence Chain

### 6.1 Chain Table

| 項目 | 内容 |
|---|---|
| commit hash | `ecab6c005aa773329a0dd0d4c80c0aba89d59b01` |
| timestamp | 2026-07-11T14:20:10+09:00（author_date = commit_date、一致確認済み） |
| artifact scope | `docs/research/PROJECT_501_NIST_RUNTIME_GOVERNANCE_ASSESSMENT/`一式、23ファイル・1324行挿入 |
| repository state | `git reflog show origin/main`にて`refs/remotes/origin/main@{0}: update by push`として反映確認済み（EV-001-F3） |
| ledger reference | Decision Ledger `DC_20260711_003`（2026-07-11、Operation=AUTHORIZED / Recording=POST_FACTO_RECORDING）、Event Ledger `E20260711_524194598f38a`（本仕様書作成着手のCHANGE_START） |

### 6.2 Chain Linkage（証拠項目間の技術的接続）

上表の各項目は独立した証拠ではなく、以下の順で連結して1本の証跡を構成する。

1. **commit hash**が対象commitを一意に特定する起点となる（`git show ecab6c0`で内容を独立に再取得可能、EV-001-F1）。
2. **timestamp**はそのcommitオブジェクトに埋め込まれたauthor_date/commit_dateであり、commit hashと不可分（同一コマンドの出力から取得、改ざんにはhash自体の変化を伴う）。
3. **artifact scope**は同じcommitの`--stat`出力から得られる変更ファイル一覧であり、commit hashに直接紐づく（EV-001-F2）。
4. **repository state**は、上記commit hashが実際に公開リモートの先端として反映されているかを、commitオブジェクト単体とは別の情報源（`git reflog show origin/main`、ローカルのreflogという別ファイル）で照合するステップである。ここでcommit hashが一致することにより、「commitが存在する」ことと「そのcommitが公開リモートへ到達した」ことが別々に検証・接続される（EV-001-F3）。
5. **ledger reference**は、1〜4で確定した技術的事実（commitの存在・内容・公開リモートへの到達）に対し、MoCKAの制度的な扱い（Operation/Recording属性、DEC-A〜Dの確定）を接続する最終リンクである。Decision Ledger `DC_20260711_003`は`mocka_decision_get`による読み戻しで内容の反映を確認済みであり、`related_documents`に本仕様書自身を含む形で相互参照が成立している。

この5段階のうち1〜4は`git`コマンドのみで誰でも独立に再現・検証可能な技術的事実であり、5のみがMoCKAの制度的記録（Human Gate裁定）に依存する。この区分により、「技術的に何が起きたか」と「制度上どう扱うと決めたか」が本仕様書内でも分離されている。

---

## 7. Governance Impact

**Institutional Memory:** 本事例はDecision Ledger・Event Ledger・本仕様書の3経路で記録され、今後の同種事例の参照点となる。

**Decision Traceability:** OperationとRecordingを分離した2軸管理モデルにより、「操作は許可されていたが記録が後追いだった」という状態を、単純な許可/不許可の二値では表現できなかった中間状態として明示的に扱えるようになった。

**Auditability:** DEC-A〜Dの確定内容はDecision Ledgerへの読み戻し（`mocka_decision_get`）により検証済み。DEC-Eは意図的にPendingのまま残されており、引き続き独立した監査対象として追跡可能な状態にある。

**Reproducibility:** 「操作は許可されていたが記録経路が後追いになった」という同種の事例が今後発生した場合、本仕様書のOperation/Recording分離モデル、およびDEC-C（記録経路の改善）の枠組みを再利用できる。

---

## 8. Improvement Design

- **commit/push linkage:** push等の外部反映を伴うgit操作の実行前に、対応するDecision Ledger記録の有無を確認するステップの検討（DEC-C由来）。
- **automatic ledger binding:** `mocka_git_safe_commit()`等の共有ヘルパー経由でのgit操作に、Decision Ledger参照IDの付与を必須化する設計の検討。
- **authorization metadata:** Operation/Recordingのような複数属性による状態管理を、Decision Ledgerスキーマ上の標準フィールドとして一般化する検討。
- **artifact provenance tracking:** 独立監査ラベルと作成主体表記の整合性（DEC-E対象）のような、成果物自体の自己記述を検証する仕組みの検討。DEC-Eの解決と並行して検討する。

---

## 9. Verification Specification

| 検証項目 | 内容 |
|---|---|
| 再現可能性 | commit hash・timestamp・push先リモートは`git show`/`git reflog`により独立に再現確認可能（EV-001-F1/F3） |
| 記録完全性 | Decision Ledger`DC_20260711_003`は書込後に`mocka_decision_get`で読み戻し、内容が反映されていることを確認済み |
| 参照経路 | 本仕様書は`E001_HUMAN_GATE_DECISION_SHEET_v1.0.md`・`E001_FACT_COLLECTION_REPORT_v1.0.md`・`E001_HUMAN_GATE_TECHNICAL_SPECIFICATION_v1.0.md`と相互参照する（Decision Ledgerの`related_documents`として登録済み） |
| 整合性確認 | DEC-A〜Dの確定内容は、Decision Sheet・Decision Ledgerの双方で一致していることを本仕様書作成時点で確認済み。DEC-Eは両文書において一致してPendingのまま |

---

## 10. Final Status

**AUTHORIZED OPERATION**

DEC-A〜Dは確定済み（Decision Ledger `DC_20260711_003`）。DEC-E（独立監査ラベルと作成主体表記の整合性、EV-001-F8）は、commit・push許可とは別論点の品質管理事項として、本仕様書の範囲外でPendingのまま継続する。Human Gate全体としてのTerminal State（`E001_HUMAN_GATE_TECHNICAL_SPECIFICATION_v1.0.md` §5準拠）への到達は、DEC-E確定後となる。

---

**Status:** FINAL REVIEW COMPLETED

**Classification:** Governance Traceability Technical Specification

**Authorization Reference:** `DC_20260711_003`

**Operation Status:** AUTHORIZED

**Recording Status:** POST_FACTO_RECORDING

**Remaining Independent Item:** DEC-E (Audit Label Consistency) managed separately

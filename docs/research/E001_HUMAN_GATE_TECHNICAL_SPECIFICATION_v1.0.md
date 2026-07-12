# E-001 Human Gate Technical Specification v1.0

**文書種別:** 技術仕様書。判断資料ではない。本文書はHuman Gateによる判断・状態遷移・記録更新の**手順**を定義するものであり、判断内容そのもの・推奨・結論は一切含まない。

---

## 1. Purpose

**目的:** PROJECT_501/MRS-001 commit・push疑義（以下E-001）を対象に、Human Gateによる判断・状態遷移・記録更新の仕様を定義する。

**適用範囲:** 本v1.0はE-001個別事案を対象とする。事案の性質（明示的な作業境界の指示に対する逸脱疑義）を踏まえ、将来同種の事案に適用しうる仕様パターンとしての再利用可能性を持つが、本文書はE-001の判断プロセスにのみ適用する。

---

## 2. Target Incident

**対象:** `mocka-knowledge-gate`リポジトリ内commit `ecab6c005aa773329a0dd0d4c80c0aba89d59b01`（2026-07-11 14:20:10 +0900）による`PROJECT_501/MRS-001_NIST_RUNTIME_GOVERNANCE_ASSESSMENT`一式の公開リモート（`https://github.com/m-sirius-k/MoCKA-KNOWLEDGE-GATE.git`）へのpush。

**現在状態:** `OPEN`（Human Gate未通過）

---

## 3. Evidence Input Definition

**確認済み事実:** 事実そのものは本文書に記載しない。事実は`E001_FACT_COLLECTION_REPORT_v1.0.md`（Evidence Collection Record、旧`E001_HUMAN_GATE_INVESTIGATION_FORM_v1.0.md`を改名・再構成したもの）に一元化する。本文書はそのIDと境界のみを参照定義する。

**Evidence ID:** `EV-001-F1`〜`EV-001-F9`（`E001_FACT_COLLECTION_REPORT_v1.0.md` §1のF1〜F9に対応）

**証拠境界:** 本仕様書が参照可能な証拠は`E001_FACT_COLLECTION_REPORT_v1.0.md` §1（事実、EV-001-F1〜F9）に限定する。同報告書§2（影響分析）は分析であり、判断材料（Evidence Input）には含めない。§4のHuman Decision Interfaceへの入力は、判断者が§1の事実を参照して独立に行うものであり、§2の分析結果に拘束されない。

---

## 4. Human Decision Interface

| Decision ID | Decision Question | Decision Owner | Input Value | Status |
|---|---|---|---|---|
| E001-DEC-A | 本commit・pushは、事前または事後に許可されていたか | きむら博士 | （空欄） | Pending |
| E001-DEC-B | 論点Aが否の場合、AIセッションによる明示指示逸脱と判定するか | きむら博士 | （空欄） | Pending |
| E001-DEC-C | CHANGE_START/CHANGE_DONE記録の欠落を、独立の是正対象として扱うか | きむら博士 | （空欄） | Pending |
| E001-DEC-D | PROJECT_501/MRS-001の内容を参考資料として参照可能とするか | きむら博士 | （空欄） | Pending |
| E001-DEC-E | 独立監査ラベルと単著起草表記の不一致（EV-001-F8）について表記是正を求めるか | きむら博士 | （空欄） | Pending |

**入力規則:** 各`Input Value`は判断者本人のみが記入する。AIによる代入・推測・仮置きは禁止する。`Status`は`Pending`→`Decided`の一方向遷移のみとし、`Decided`確定後の値変更は新規Decision ID（例: `E001-DEC-A-R1`）を発行して行い、既存レコードの上書きは行わない。

---

## 5. State Transition Model

```
OPEN
  |
  | (Human Gate Decision Sheet提出)
  v
HUMAN_REVIEW
  |
  | (E001-DEC-A〜E 全てのStatusがDecidedへ遷移)
  v
Terminal State（複数属性の組み合わせで確定）
```

**Terminal State定義（E001-DEC-A/Bの値に連動する主状態）:**

| 条件 | 到達する主状態 |
|---|---|
| E001-DEC-A = 許可済み | `RESOLVED` |
| E001-DEC-A = 未許可 かつ E001-DEC-B = 逸脱に該当 | `INCIDENT` |
| E001-DEC-A = 未許可 かつ E001-DEC-B = 逸脱に非該当 | `RESOLVED`（理由付き） |

**付随属性（主状態と並存しうる、E001-DEC-C/D/Eの値に連動）:**

| Decision ID | 値 | 付随する属性 |
|---|---|---|
| E001-DEC-C | 是正要 | `REMEDIATION_REQUIRED`フラグを主状態に付与 |
| E001-DEC-D | 参照可 | `CONTENT_REFERENCE = ALLOWED` |
| E001-DEC-D | 参照不可（保留） | `CONTENT_REFERENCE = HELD` |
| E001-DEC-E | 是正要 | `LABEL_CORRECTION = REQUIRED`（PROJECT_501側の対応、MoCKA本体は対象外） |

**遷移制約:** `HUMAN_REVIEW`から`Terminal State`への遷移は、E001-DEC-A〜Eの5件全てが`Decided`となった時点でのみ許可する。一部のみ`Decided`の状態でTerminal Stateへ遷移することはできない。

---

## 6. Recording Requirements

| 記録先 | 記録内容 | タイミング |
|---|---|---|
| Event Ledger | `HUMAN_REVIEW`開始・`Terminal State`到達それぞれについてCHANGE_START/CHANGE_DONE相当のイベントを記録 | 状態遷移の都度 |
| Decision Ledger | E001-DEC-A〜Eの確定内容（`alternatives`・`rationale`を含む）を`mocka_decision_write()`により記録する。Markdown文書への記述のみで完結させない（MoCKA CLAUDE.md「Decision Ledgerへの記録義務」準拠） | Terminal State確定時 |
| Verification Debt | `VERIFICATION_DEBT_PHASE1_CLOSURE_REPORT_v1.0.md`のE-001エントリの最終状態（現在`PENDING_DECISION`）を更新する | Terminal State確定後 |
| 関連成果物 | `MOCKA_BEYOND_NIST_ANALYSIS_v1.0.md` §1.3、`MoCKA_vs_NIST_AIRMF_TACIP_GAP_ANALYSIS_v1.0.md` §3.12、`POSITION_OF_MOCKA_WITHIN_INTERNATIONAL_AI_GOVERNANCE_TECHNICAL_SPECIFICATION_v1.0.md` §3.2・§6.1への反映要否を、`CONTENT_REFERENCE`属性の値に基づき判定する | Terminal State確定後 |

書込直後は、対応する取得系ツール（`mocka_decision_get`等）で読み戻し、実際にデータが反映されていることを確認してから完了とみなす（MoCKA CLAUDE.md「実行証跡の定義」準拠）。

---

## 7. Immutable Rules

- **AIは判断しない。** E001-DEC-A〜Eの`Input Value`をAIが記入・推測・代筆することを禁止する。
- **AIは証拠整理と記録補助のみを行う。** Evidence Collection Record（`E001_FACT_COLLECTION_REPORT_v1.0.md`）の維持、本仕様書の維持、Terminal State確定後のLedger反映作業（§6）に限定する。
- **Human Gate通過前に確定状態へ移行しない。** `HUMAN_REVIEW`状態のまま、E001-DEC-A〜Eのいずれかが`Pending`である限り、`RESOLVED`/`INCIDENT`/`REMEDIATION_REQUIRED`のいずれの状態にも遷移しない。既存成果物（Beyond-NIST分析等）への反映も同様に凍結する。

---

## 8. Completion Criteria

| 条件 | 内容 |
|---|---|
| 判断入力済み | E001-DEC-A〜Eの`Status`が全て`Pending`以外（`Decided`）に遷移していること |
| 状態遷移完了 | §5の`Terminal State`（主状態+付随属性）へ到達していること |
| Ledger更新済み | §6のEvent Ledger・Decision Ledgerへの記録が完了し、読み戻しで確認済みであること |
| 参照文書整合確認済み | §6「関連成果物」への反映が完了、またはCONTENT_REFERENCE=HELDにより反映不要と確定していること |

上記4条件が全て満たされた時点で、本仕様書上のE-001プロセスは完了とする。

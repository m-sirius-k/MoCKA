# PHI-REG-04 Legacy Freeze Decision Draft v0.1

**Status:** DRAFT([DC-PHI-REG04-001]候補。Decision Ledger登録前段階)
**位置づけ:** `PHI_REG04_REMEDIATION_DECISION_SCOPE_v0.1.md`のOption B(Legacy Freeze + 新Runtime設計)を土台としたDecision Draft。
**実装・Decision Ledger登録:** 本文書には一切含まない。

---

## Title

`[DC-PHI-REG04-001] PHI-REG-04 Legacy Freeze and Future Registration Runtime Migration Policy`

---

## Context

以下を根拠として、現行PHI-REG-04を即時拡張せず、Legacy状態として保持する判断理由を整理する。

- `docs/audits/PHI_REG04_COMPLIANCE_REVIEW_FINDINGS_v0.1.md`
- `docs/audits/PHI_EVENT_HISTORICAL_INTEGRITY_INVESTIGATION_REPORT_v0.1.md`
- `docs/audits/PHI_REG04_REMEDIATION_DECISION_SCOPE_v0.1.md`

---

## Decision案

> PHI-REG-04はLegacy Freeze状態として保持する。
>
> 現在の実装・履歴はEvidence対象として保存し、新規PHI Registration RuntimeはPHI-OS Sequence Controller設計と整合する形で別途設計する。
>
> 本DecisionはPHI-REG-04の存在否定ではなく、将来Runtimeへの移行準備状態を定義するものである。

---

## Preserved(必ず保持)

- `DC_20260729_008`(DC-PHI-ID-001、Responsibility Classification)
- `DC_20260729_009`(DC-PHI-ID-002、Authority Flow Option D)
- `PHI_REG04_COMPLIANCE_REVIEW_FINDINGS_v0.1.md`
- `PHI_EVENT_HISTORICAL_INTEGRITY_INVESTIGATION_REPORT_v0.1.md`

---

## Migration Principle

- Legacy Evidenceを保持する
- 過去Eventを改変しない
- 新Runtimeで同じ問題を再発させない
- Human Gateを経由する

---

## Next Resolution Condition

- Future Registration Runtime設計完了
- Sequence Controller設計との接続確認
- Migration Plan承認
- Human Gate承認

---

## S01完了後の次指示(参考記載)

Draft完成報告後、次工程は以下の流れになる。

```
PHI_REG04_LEGACY_FREEZE_DECISION_DRAFT_v0.1作成(本文書)
        |
        v
      Review
        |
        v
  Decision Ledger登録
        |
        v
  Legacy Freeze確定
        |
        v
J1 PHI Memory Architectureへ移行
```

---

## ジャービス化ロードマップ上の位置

本Decision確定後、フェーズは「監査基盤整備」から「Runtime入口再設計」へ移行する。次の大きな設計対象:

1. PHI Memory Architecture
2. PHI Sequence Controller
3. Orchestra Integration

---

## Knowledge Lineage

**Document:** PHI_REG04_LEGACY_FREEZE_DECISION_DRAFT_v0.1.md
**Status:** DRAFT
**Created:** 2026-07-29
**Origin:** `PHI_REG04_REMEDIATION_DECISION_SCOPE_v0.1.md`のOption Bを土台に、きむら博士よりDecision Ledger登録前Draft作成の指示を受けた。
**Parent Documents:**
- docs/audits/PHI_REG04_REMEDIATION_DECISION_SCOPE_v0.1.md
- docs/audits/PHI_REG04_COMPLIANCE_REVIEW_FINDINGS_v0.1.md
- docs/audits/PHI_EVENT_HISTORICAL_INTEGRITY_INVESTIGATION_REPORT_v0.1.md
- DC_20260729_008、DC_20260729_009
**Derived From:** PHI_REG04_REMEDIATION_DECISION_SCOPE_v0.1(Option B)
**Supersedes:** なし
**Reason For Creation:** DC-PHI-REG04-001としてDecision Ledgerへ登録する前に、内容をDraftとして提示・Reviewを受けるため。
**Affected Components:** PHI-REG-04(`phi_os_bridge.py`)
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。Title/Context/Decision案/Preserved/Migration Principle/Next Resolution Conditionを記載。Decision Ledger登録・実装は無し。

# PHI-REG-04 Remediation Decision Scope v0.1

**Status:** SCOPE(Remediation方針の選択肢提示。Human Gate裁定・実装・Decision Ledger登録はまだ行わない)
**位置づけ:** ジャービス化ロードマップ Priority 1。PHI-REG-04 Compliance Review・Historical Integrity Investigation完了を受け、PHI-REG-04を将来のPHI-OS Runtime基盤として採用可能な状態へ持っていくための修正方針を、Human Gate判断可能な形に整理する。**「修正作業」そのものではない。**
**実装・Decision Ledger登録:** 本文書には一切含まない。

---

## 1. Context

**対象:**
- `PlanningCaliber/workshop/seo-os/mocka/phi_os_bridge.py`(PHI-REG-04)
- `docs/audits/PHI_REG04_COMPLIANCE_REVIEW_FINDINGS_v0.1.md`
- `docs/audits/PHI_EVENT_HISTORICAL_INTEGRITY_INVESTIGATION_REPORT_v0.1.md`

**現状:**

| 軸 | 状態 |
|---|---|
| Current Runtime | Compliance Risk Confirmed(`PHI_OS_CONSTITUTION_v1.md`原則4・5.1に抵触する設計。現在DBへの継続的影響は無し) |
| Historical Integrity | Closed - Awaiting Additional Evidence(`E20260729_093971901d68f`。2026-06-07の過去実行イベントの消失原因は未確定のまま保持) |

---

## 2. Confirmed Issues(確定事項のみ)

- Registration経路(`phi_os_bridge.py`の`push_decision_audit()`/`push_policy_violation()`)が、`phi_os/event_gate.py`の`process_event()`/`_write()`を経由せず、`PHI_OS_CONSTITUTION_v1.md`原則4・5.1が要求する経路と完全一致していない
- 過去実行イベント(`EPHIOS_DEC_20260607_152923`)の履歴連続性にUnknownが存在する(Historical Integrity Investigation Report参照)
- 現在のLedger(`data/mocka_events.db`、18,258件)への継続的汚染は確認されていない(全件署名済み、`where_component='phi_os_bridge'`該当0件)
- `seo-os`配下の静的検索では`phi_os_bridge.py`の呼び出し元が見つからない(検索範囲限定、Unknown残存)

---

## 3. Remediation Options(いずれも未選択、Human Gate裁定待ち)

### Option A: 即時修正

**内容:** `phi_os_bridge.py`を修正し、Registration経路を`phi_os/event_gate.py`経由(`process_event()`)に変更する。新規Event生成方式へ移行する。

**利点:** 早期正常化。Constitution原則4・5.1への抵触を直接解消する。

**Risk:** 過去の履歴(2026-06-07実行分を含む)との接続整理が別途必要になる。修正自体がHistorical Integrity Investigationの「Known Unknown」部分を上書き・混同するリスクがある(修正後は旧経路の痕跡確認がさらに困難になる)。

### Option B: Legacy Freeze + 新Runtime設計

**内容:** 現行`phi_os_bridge.py`を現状のまま保存(Freezeし、実行を停止または隔離する)。新規のPHI Registration Layerを別途設計し、移行計画を作成する。

**利点:** Evidence保全。既存コード・過去実行実績を将来の調査対象として毀損しない。

**Risk:** 移行期間が発生し、その間Registration機能自体が空白になる、または旧経路と新経路が一時的に併存する。

### Option C: 再設計(PHI Sequence Controller統合)

**内容:** PHI-REG-04を単独で修正せず、Priority 3で予定される`PHI_SEQUENCE_CONTROLLER_DESIGN_v1.0.md`の一部として、PHI-OS Registration Architectureごと再定義する。

**利点:** ジャービス化ロードマップ(§5参照)との整合性が最大になる。将来の「認識入口」としての設計を最初から統合的に行える。

**Risk:** 範囲が拡大し、Priority 1単独では完結しない。Priority 3の設計完了まで、Compliance Riskの是正自体が先送りされる。

---

## 4. Human Gate対象(博士判断事項)

1. PHI-REG-04を**修正する**か
2. PHI-REG-04を**Legacyとして隔離する**か
3. PHI-OS**統合設計(Sequence Controller)まで待つ**か

上記いずれの選択も、本Scope文書自体は確定させない。選択結果は別途Decision Ledgerへ記録する。

---

## 5. ジャービス化ロードマップとの接続

PHI-REG-04は単なる登録機能ではなく、将来的には以下の経路における「認識入口」に相当する:

```
External Information
       |
       v
     Relay
       |
       v
  Registration   <- PHI-REG-04が現在占める位置
       |
       v
    Memory
       |
       v
 MoCKA Governance
       |
       v
Sequence Controller
       |
       v
    Action
```

入口の証跡性(Registration経路がConstitutionの要求する記録経路と一致しているか)が弱いままだと、後段のMemory・Reasoningの信頼性に影響する。これが、PHI-REG-04の扱いをジャービス化ロードマップの中で最優先(Priority 1)とする理由である。

---

## 6. 後続ロードマップ(参考、本文書では未着手)

PHI-REG-04方針確定後、以下の順序が想定される(いずれも別途着手指示を要する):

```
J1: PHI Memory Architecture
      |
      v
J2: PHI Sequence Controller Design
      |
      v
J3: Orchestra統合
      |
      v
J4: Personal Context Engine
      |
      v
J5: Embodied Interface
```

---

## Knowledge Lineage

**Document:** PHI_REG04_REMEDIATION_DECISION_SCOPE_v0.1.md
**Status:** SCOPE
**Created:** 2026-07-29
**Origin:** PHI-REG-04 Compliance Review・Historical Integrity Investigation完了を受け、きむら博士よりジャービス化ロードマップPriority 1として作成を指示された。
**Parent Documents:**
- docs/audits/PHI_REG04_COMPLIANCE_REVIEW_FINDINGS_v0.1.md
- docs/audits/PHI_REG04_COMPLIANCE_REVIEW_SCOPE_DRAFT_v0.1.md
- docs/audits/PHI_EVENT_HISTORICAL_INTEGRITY_INVESTIGATION_REPORT_v0.1.md
- Event Ledger: E20260729_609117955548c、E20260729_093971901d68f
**Derived From:** PHI_REG04_COMPLIANCE_REVIEW_FINDINGS_v0.1
**Supersedes:** なし
**Reason For Creation:** PHI-REG-04の扱い(修正/隔離/統合設計待ち)をHuman Gate判断可能な形に整理し、監査フェーズからジャービス化設計フェーズへの移行の第一歩とするため。
**Affected Components:** PHI-REG-04(`phi_os_bridge.py`)
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。Context・Confirmed Issues・Remediation Options(A/B/C)・Human Gate対象3項目・ジャービス化ロードマップとの接続・後続ロードマップを記載。裁定・実装・Decision Ledger登録は無し。

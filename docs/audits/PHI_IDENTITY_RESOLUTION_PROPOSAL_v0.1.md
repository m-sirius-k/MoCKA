# PHI Identity Resolution Proposal v0.1

**Status:** PROPOSAL(Decision Ledger登録前段階。本文書自体はDecisionではなく、Decision候補の提示のみ)
**位置づけ:** [[PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1]](Approved Candidate、Human Gate評価済み)を土台とし、Decision Ledger登録に向けたDecision候補を整理する。
**実装・リネーム・Decision Ledger登録:** 本文書には一切含まない。
**今回のHuman Gate判断ポイント(きむら博士指定)**: 「PHI-Con/PHI-Core/PHI-HABを正式名称にするか」ではなく、「この3分類をPHI Identity管理の公式分類軸として採用するか」。

---

## 1. 現状Identity Map(要約)

詳細は`PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1.md`参照。要点のみ再掲する。

| 既存Registry ID | 責務分類候補 | 確度 |
|---|---|---|
| PHI-REG-01 | PHI-Con(制度Authority) | 高確度 |
| PHI-REG-02(a) | PHI-HAB(Connection/協調層) | 高確度 |
| PHI-REG-02(b) | PHI-Core(Runtime基盤) | 高確度 |
| PHI-REG-02(c) | 未分類(Transition Component、暫定保持) | 継続確認 |
| PHI-REG-03 | 対応なし(変更なし) | 確定 |
| PHI-REG-04 | Identity分類から分離、Compliance Issueとして別管理 | 保留 |

問題は2軸に分離される。

```
Identity Issue
      |
      v
PHI-Con / PHI-Core / PHI-HAB 責務分類

Compliance Issue
      |
      v
PHI-REG-04 Review(DB直接INSERT / event_gate未経由 / Hash Chain Integrity)
```

---

## 2. 採用候補構造

PHI-Con/PHI-Core/PHI-HABは、既存PHI-REG体系を置き換える新名称ではなく、**Alias(責務分類名称)**として導入する候補である。

```
PHI-REG-01           -> alias: PHI-Con
PHI-REG-02(a)        -> alias: PHI-HAB
PHI-REG-02(b)        -> alias: PHI-Core
PHI-REG-02(c)        -> 未分類のまま保持(alias付与なし)
PHI-REG-03           -> alias付与なし(変更なし)
PHI-REG-04           -> alias付与保留(Compliance Review先行)
```

Authority Flow(PHI-Con/MoCKA/PHI-Coreの統治方向)は、Constitution系(PHI-Con→MoCKAを統治)とRC-008系(MoCKA Governance Runtime→PHI-Coreを保証)の2モデルが併存し未統合であるため、本提案では**Pending Resolution**として明示的に保持する(いずれのモデルも「正」と裁定しない)。

```
Authority Flow: Pending Resolution
  - Model A(Constitution系): PHI-Con -> MoCKA(統治)
  - Model B(RC-008系):       MoCKA Governance Runtime -> PHI-Core(保証)
  - 統合判断: 未実施
```

---

## 3. 未解決事項(Map v0.1からの継続)

1. PHI-REG-02(c)(Hub系)の最終分類 — Unknown
2. Authority Flowの統合(Model A/Bのどちらを採るか、あるいは両者が別対象を指すだけか) — Pending Resolution
3. PHI-REG-01/02間の関係更新の有無(2026-06-24監査の「独立・無関係」判定とRC-008の「外部保証層」記述の関係) — Unknown
4. DC_20260729_001が引用する一次資料(`PHI_OS_IDENTITY_COMPARATIVE_ANALYSIS_DRAFT_v0.1.md`、commit `1d909c3`)の所在不明 — Unknown
5. 「PHI-OS Definition v1.0」の所在 — Unknown

---

## 4. 将来Decision候補

以下はいずれも**候補**であり、本文書によって確定・登録されるものではない。Human Gate承認後、`mocka_decision_write()`により正式登録する。

### DC-PHI-ID-001(候補)

**内容:** PHI-Con / PHI-Core / PHI-HABを、PHI Identity管理における公式Responsibility Classification(Alias)として採用する。

**制約:**
- PHI-REG-01〜04のID自体は変更しない
- 既存Decision(DC_20260728_002/003、DC_20260729_001)は変更・撤回しない
- Alias管理のみとし、正式名称への置換・文書の大量修正は行わない

### DC-PHI-ID-002(候補)

**内容:** PHI-REG-01(PHI-Con)とPHI-REG-02(b)(PHI-Core)間のAuthority関係を再評価する。

**対象:**
- `PHI_OS_CONSTITUTION_v1.md`第1章1.1(PHI-Con→MoCKA統治)
- `PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md`/DC_20260728_003(MoCKA Governance Runtime→PHI-Core保証)

**現状:** 未着手。本Decisionが承認されるまでAuthority Flowは`Pending Resolution`のまま保持する。

### DC-PHI-ID-003(候補)

**内容:** PHI-REG-04(`phi_os_bridge.py`)のConstitution Compliance Reviewを開始する。

**対象:**
- DB直接INSERT(`sqlite3.connect(MOCKA_DB)`経由の生SQL実行)
- Event Authority経由性(`phi_os/event_gate.py`の`process_event()`/`_write()`を経由していない)
- Hash Chain Integrity(`integrity.sign_event()`未実行)

**分離理由:** PHI-REG-04の問題はIdentity(名称)問題ではなく、Constitution第2章原則4・第5章5.1に対するCompliance問題であるため、DC-PHI-ID-001/002とは独立したDecisionとして扱う。

---

## Knowledge Lineage

**Document:** PHI_IDENTITY_RESOLUTION_PROPOSAL_v0.1.md
**Status:** PROPOSAL
**Created:** 2026-07-29
**Origin:** PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1.mdがきむら博士によりApproved Candidateと評価されたことを受け、Decision Ledger登録前の提案文書として作成。
**Parent Documents:**
- PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1.md
- MOCKA_PHI_OS_IDENTITY_AUDIT_v1.md
- PHI_OS_CONSTITUTION_v1.md
**Derived From:** PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1(責務分類対応表・Unknown一覧の継承元)
**Supersedes:** なし
**Reason For Creation:** Decision Ledger正式登録に先立ち、Decision候補(DC-PHI-ID-001/002/003)を明示し、Human Gate判断ポイントを「正式名称化の可否」ではなく「分類軸としての採用可否」に絞り込むため。
**Affected Components:** PHI-REG-01〜04、DC_20260728_002/003、DC_20260729_001
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。Decision候補3件を提示。実装・リネーム・Decision Ledger登録は無し。

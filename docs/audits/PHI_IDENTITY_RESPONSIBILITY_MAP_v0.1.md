# PHI Identity Responsibility Map v0.1

**Status:** DRAFT(Human Gate確認待ち。Decision Ledgerへの正式登録は本文書の確認後に行う)
**位置づけ:** [[MOCKA_PHI_OS_IDENTITY_AUDIT_v1]](2026-06-24、Risk: High)と、RC-008系4文書(PHIOS_CORE_CANONICAL_DESIGN_v1.md / PHIOS_ARCHITECTURE_CONSOLIDATION_REPORT_v1.md / PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md / EVENT_GATE_CANONICAL_PATH_REPORT_v1.md、2026-07-28)、およびDC_20260728_002/003・DC_20260729_001の間で確認されたPHI-OS名称・Authority関係の整理を目的とする。
**実装・リネーム・Decision Ledger登録:** 本文書には一切含まない。監査・整理文書のみ。
**注記:** PHI-Con/PHI-Core/PHI-HABは「正式名称への変更」ではなく、既存PHI-REG体系に対する**Responsibility Classification(責務分類)案**として扱う。既存Registry ID(PHI-REG-01〜04)は本文書によって変更・廃止されない。

---

## 1. Responsibility Classification 対応表

| 既存Registry ID | 実体・Origin Path | 新責務分類案 | 確度 |
|---|---|---|---|
| PHI-REG-01 | Persistent History Intelligence OS(`MoCKA/phi_os/` + `PHI_OS_CONSTITUTION_v1.md`、2026-06-16) | **PHI-Con**(制度Authority) | 高確度 |
| PHI-REG-02(a) | Chrome拡張JSハブスタック(`PlanningCaliber/workshop/phi-os/extension/`, `core/`, `adapters/`。DESIGN_v1.md原義) | **PHI-HAB**(Connection/協調層) | 高確度 |
| PHI-REG-02(b) | Python ISE/phiosスタック(`phios/` + `ise/` + `phi_os_core.py`。DC_20260728_002でCanonical Core確定) | **PHI-Core**(Runtime基盤) | 高確度 |
| PHI-REG-02(c) | Hub系(`phi_os.py` / `phi_os_state.py` / `phi_os_view.py` / `phi_os_poller.py`) | **未分類**(暫定: Legacy/Transition Components) | 継続確認 |
| PHI-REG-03 | sirius-lab-products配下パッケージ版(実コードなし、archived) | 対応なし(変更なし) | 確定 |
| PHI-REG-04 | `phi_os_bridge.py`(`PlanningCaliber/workshop/seo-os/mocka/`) | **Bridge候補**(命名整理から分離、下記2章参照) | 保留 |

**PHI-REG-02(c)を今回分類しない理由(継続確認とする根拠)**: 現在の情報では、(i)PHI-Coreの内部補助機能、(ii)PHI-HABの旧実装、(iii)Legacy Adapterのいずれでも説明可能であり、根拠となる一次資料が一意に決まらない。PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md§6も「Hub系を"MoCKA本体とは無関係な旧実験コード"としてではなく"PHL/Relay Interfaceの叩き台(未完成)"として位置づけ直す候補がある」としつつ、どちらを採用するかは別途判断が必要と明記しており、RC-008自身も確定させていない。

---

## 2. Authority Flow(提案・未承認)

**注記: 以下は今回のReconciliation作業で提示された整理案であり、Decision Ledgerに承認記録された確定構造ではない。**

```
PHI-Con(制度Authority、旧PHI-REG-01)
       |
       v  (統治/保証関係の向きが資料により異なる。下記参照)
MoCKA Governance Runtime(phi_os/event_gate.py等、PHI-Con実装物と同一パッケージ)
       |
       v
PHI-Core(Runtime基盤、旧PHI-REG-02b)
       |
       v
PHI-HAB(Connection層、旧PHI-REG-02a)
```

**この図が「提案」に留まる理由(Confirmed、資料間の不一致)**:

- `PHI_OS_CONSTITUTION_v1.md`第1章1.1: PHI-OS(=PHI-Con)は「**MoCKA全体**の唯一の制度執行機関」。PHI-ConがMoCKAを統治する包含関係。
- `PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md`(DC_20260728_003、判定区分E): 「MoCKAはPHI-OSの部品ではなく、PHI-OSの動作を保証する**外部制度層**」。MoCKA Governance RuntimeがPHI-Core(phios+ise+phi_os_core.py)を外部から保証する、対等・非包含の関係。

両者は「PHI-Con(≒PHI-OS)とMoCKAのどちらが上位か」という点で逆方向の記述をしており、RC-008系がConstitution本文を参照した形跡はない(grep 0件、既報告済み)。上記のAuthority Flow図は、この不一致を**解消したものではなく**、双方の記述を一本の系列として仮に並べた提案に過ぎない。この関係の確定はHuman Gate判断を要する。

---

## 3. PHI-REG-04(`phi_os_bridge.py`)の取り扱い — Constitution Compliance Review Candidate(命名整理から分離)

PHI-REG-04は**Identity(名称)問題ではなくConstitution Compliance(制度違反)問題**として、本Responsibility Classificationとは別に管理する。

**Confirmed(本セッションで独自に再検証、2026-07-29時点)**:
- `PlanningCaliber/workshop/seo-os/mocka/phi_os_bridge.py`は現在も稼働コードとして存在する
- `push_decision_audit()` / `push_policy_violation()`の両メソッドが`sqlite3.connect(MOCKA_DB)`で`data/mocka_events.db`へ直接接続し、生の`INSERT INTO events`文を実行する
- `phi_os/event_gate.py`の`_write()`(TODO_322が定める単一書き込み点)を一切経由しない
  (注: process_event()およびprocess_buffered_event()は異なるエントリーポイントだが、両方とも最終的には_write()に収束する)
- `integrity.sign_event()`によるハッシュチェーン署名も付与されない

**該当するConstitution条文(PHI_OS_CONSTITUTION_v1.md)**:
- 第2章原則4「DBは保存媒体であり真実ではない」— 「DBへの直接書き込みによるEvent生成は制度違反である」
- 第5章5.1禁止事項表「DB直接更新によるEvent生成」— 理由「Event Authorityを迂回するため」

**結論**: 2026-06-24監査(MOCKA_PHI_OS_IDENTITY_AUDIT_v1.md§7)が「別途確認要」として残した違反候補は、約1ヶ月後の本日時点でも是正されておらず、現在も稼働中である。これは名称分類(PHI-Con/PHI-Core/PHI-HAB)のいずれを採用しても解消されない、独立した是正対象である。PHI-REG-04への「Bridge」という名称付与は、この違反の解消状況が確認されるまで保留する。

---

## 4. Unknown項目一覧

1. **PHI-REG-02(c)(Hub系)の最終分類**: PHI-Core内部機能/PHI-HAB旧実装/独立Legacyのいずれかは未確定。RC-008自身が「解釈(i)/(ii)のいずれを採るかはきむら博士の裁定を仰ぐ」と明記(PHIOS_CORE_CANONICAL_DESIGN_v1.md該当箇所参照、Stage 1調査時点で確認済み)。
2. **PHI-Con/MoCKA間の統治方向の不一致**: Constitution(PHI-Con⊇MoCKA)とDC_20260728_003(MoCKA Governance Runtime⊇PHI-Core、対等/外部保証)のどちらが有効な記述か、あるいは両者が別々の対象を指しているために表面上の矛盾に見えるだけなのかは未確定。
3. **PHI-REG-01/02間の関係更新の有無**: 2026-06-24監査は両者を「独立・無関係・階層なし」と確定させたが、RC-008(2026-07-28)が導入した「外部保証層」という関係が、この確定事項を更新するものか、単に別々の文脈で書かれた記述が並存しているだけかは未確認。
4. **DC_20260729_001が引用する一次資料の不整合**: `docs/audits/PHI_OS_IDENTITY_COMPARATIVE_ANALYSIS_DRAFT_v0.1.md`ならびに引用commit `1d909c3`は、本セッションのファイルシステム検索・git log照会のいずれでも確認できなかった。原因(記録漏れ/別ブランチ/引用誤り)は未特定。
5. **「PHI-OS Definition v1.0」の所在**: 前回セッションで確認できず、Unknownのまま持ち越し。

---

## Knowledge Lineage

**Document:** PHI_IDENTITY_RESPONSIBILITY_MAP_v0.1.md
**Status:** DRAFT
**Created:** 2026-07-29
**Origin:** MOCKA_PHI_OS_IDENTITY_AUDIT_v1.md(2026-06-24)完了後、RC-008系Canonical Core確定(2026-07-28)との整合確認をきむら博士より指示され、Constitution Alignment Review(本日実施)を経て作成。
**Parent Documents:**
- MOCKA_PHI_OS_IDENTITY_AUDIT_v1.md
- PHI_OS_CONSTITUTION_v1.md
- docs/consolidation/PHIOS_CORE_CANONICAL_DESIGN_v1.md(workshop/phi-os/)
- docs/consolidation/PHIOS_ARCHITECTURE_CONSOLIDATION_REPORT_v1.md(workshop/phi-os/)
- docs/consolidation/PHIOS_MOCKA_BOUNDARY_DESIGN_v1.md(workshop/phi-os/)
- docs/consolidation/EVENT_GATE_CANONICAL_PATH_REPORT_v1.md(workshop/phi-os/)
**Derived From:** MOCKA_PHI_OS_IDENTITY_AUDIT_v1(Registry ID命名規則の継承元)
**Supersedes:** なし
**Reason For Creation:** PHI-OS名称衝突(Identity問題)とAuthority方向の記述矛盾(Authority問題)を分離して整理し、Decision Ledgerへの正式登録前の確認資料とするため。
**Affected Components:** PHI-REG-01〜04、PHI-Con/PHI-Core/PHI-HAB責務分類案、DC_20260728_002/003、DC_20260729_001
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。責務分類対応表・Authority Flow(提案)・PHI-REG-04 Compliance分離・Unknown一覧を記載。実装・リネーム・Decision Ledger登録は無し。

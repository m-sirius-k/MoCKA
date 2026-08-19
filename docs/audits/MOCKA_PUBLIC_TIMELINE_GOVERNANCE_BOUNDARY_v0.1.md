# MoCKA公開記録の時系列 — Governance Boundary明示化の進展

**文書番号:** MOCKA-TIMELINE-001
**作成日:** 2026-08-19
**著者:** くろこ(WEB調査部門)
**状態:** PHASE A INTERIM REPORT(調査進行中のスナップショット)

---

## 1. MoCKA公開記録から見える「Governance vs Capability」分離の時間軸

### 1.1 観測対象とデータソース

本報告書は以下の公開記録に基づく：
- commit履歴(git log)
- 公開ドキュメント(docs/配下markdown)
- ドキュメント内メタデータ(作成日、更新日)
- ドキュメント間の相互参照

**重要な制限:** Windows上の Decision Ledger(`.jsonl`)・Event Ledger は、このセッションでは見えない。よって、リポジトリに記録された「公開ドキュメント化された」イベントのみを扱う。

### 1.2 時系列の確立

| 時点 | 公開記録 | 内容 | Authority/Capability明示化 |
|---|---|---|---|
| 2026-04-03/04-05 | MOCKA_RELATED_WORK_v1.md 生成・更新 | XAI / NIST AI RMF / マルチエージェント / 知識永続化の4分野と MoCKA の関係を整理。「Do Not Trust AI; Constrain It by System」を核心命題として明記 | **アプローチは明示的だが、「authority vs capability」という明確な二分法ではまだ無い** |
| 2026-06-01(推定) | Phase 4開始 / PHI-OS Milestone確定 | 商用製品展開フェーズ移行。MOCKA_OVERVIEW.json session_history で確認 | — |
| 2026-07-25(推定) | PHI_OS_CONSTITUTION_v1.md確定 | PHI-OSの制度憲法が RATIFIED 状態へ。JARVIS_CONSTITUTION_DRAFT.md §2.1 で参照される | **「原則2: PHI-OS のみが制度を定義できる」「原則7: Institution が責任主体」という明示的な分離** |
| 2026-07-29 | DC_20260729_008 承認(Active) | HAB-D(Chrome拡張JSハブスタック)を「PHI-HAB」として制度採用。**初めての「PHI-OS定義」の正式決定** | 局所的な「責務分類」だが、全体的な authority boundary はまだ未確定 |
| 2026-07-29 | DC_20260729_009 承認(Active) | PHI-Con / PHI-Core 間の Authority Flow を **Pending Resolution** と裁定。根本的な authority 階層が「後回し」に確定 | **Authority Flow が未確定のまま、それより下流の設計進行を強制された初めての時点** |
| 2026-08-04 | JARVIS_CONSTITUTION_DRAFT.md 作成 | 9個の Human Gate判断項目(HG-J01〜HG-J09)を列挙。特に HG-J02「JARVIS の帰属 Institution と Authority 上の位置」が **未裁定** として顕在化 | **「Authority 未確定」が JARVIS 実装を明確に阻止する根本理由として顕在化** |
| 2026-08-04 | JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md 作成 | 「HG-J02 は DC_20260729_009 の Pending が解けるまで、『JARVIS の Authority 位置は未確定』という状態を維持する裁定 以外の選択肢を持たない可能性がある」と明記 | **実装を「完全に停止」させる根本的障害として公開記録に記載** |
| 2026-08-18 | Governance Asset Revaluation実施 / HG-J03 Evidence Complete移行 | 複雑性の新展開：HAB-D が実は3系統(HAB-D-1/2/3)に分離している事実が発見。「単一実体」という前提が崩壊 | Authority / Capability 分離の複雑性が増加 |

### 1.3 関鍵イベント：「Authority Flow Pending」(2026-07-29)

**最も重要な時点:** DC_20260729_009 において、PHI-OS の根本的な Authority 階層構造が「Pending Resolution」と裁定された。

**その後の影響:**
- JARVIS_CONSTITUTION_DRAFT.md (2026-08-04) では、この Pending に依存する下流の3個の判断(HG-J02, HG-J01, HG-J04)が全て「単独では確定できない」状態に
- これが「JARVIS を実装ではなく停止する」判断に直結している

**外部研究との時間的対応:**
- arXiv:2603.14805 (推定2026-03投稿)
- arXiv:2604.08059 (推定2026-04投稿)
- が、公開リポジトリの RELATED_WORK には言及されていない(2026-04-03/04-05時点)
- JARVIS 設計段階(2026-08-04)で新たに参照された可能性

---

## 2. 「Capability vs Authority」の明示化の進展

### 2.1 概念的進展の段階

| 段階 | 時点 | 表現形式 | 記録位置 |
|---|---|---|---|
| **段階0: 原則的立場表明** | 2026-04-03/04-05 | 「Do Not Trust AI; Constrain It by System」（信頼ではなく制度で縛る） | MOCKA_RELATED_WORK_v1.md §2.4.5 |
| **段階1: 部分的制度化** | 2026-07-25(推定) | PHI-OS Constitution原則1〜7の確立。「PHI-OS のみが制度を定義」「Institution が責任主体」 | JARVIS_CONSTITUTION_DRAFT.md §2 (継承参照) |
| **段階2: 具体的構造の出現** | 2026-07-29 | HAB-D の制度採用(DC_20260729_008)による「責務分類」の開始 | JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md §3.2 |
| **段階3: 根本的障害の顕在化** | 2026-07-29 | Authority Flow の Pending(DC_20260729_009)。**Authority 階層そのものが未確定** | JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md §2.3 |
| **段階4: 実装停止の決定** | 2026-08-04 | JARVIS Constitution Draft で 9個の判断項目を列挙。特に HG-J02「Authority 位置未確定」が実装を阻止 | JARVIS_CONSTITUTION_DRAFT.md / JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md |
| **段階5: 複雑性の増加** | 2026-08-18 | HAB-D の3系統分離発見による「前提の崩壊」。判断項目の再検討必要 | essence CHANGE_DONE / JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md R3 |

### 2.2 段階4の詳細：実装停止の根本構造

JARVIS_CONSTITUTION_DRAFT.md §3 と JARVIS_HUMAN_GATE_DECISION_PACKAGE_v0.1.md §2.3 が、以下の依存構造を明示している：

```
DC_20260729_009(Authority Flow = Pending)
           ↓
        HG-J02(Authority 位置未確定)
        ↙     ↖
    HG-J01  HG-J04
  (原典採用) (Gate接続先)
        ↘     ↙
    JARVIS仕様確定
           ↓
       実装開始
```

**観測:** Pending が解けるまで、いかなる選択肢を取っても「後で訂正される可能性がある」ため、
実装に進むことが不適切と判定された。

---

## 3. 外部研究との時間的対応（暫定観測）

### 3.1 RELATED_WORK の時間的位置づけ

| 外部研究 | 公開時期(推定) | RELATED_WORK内言及 | 備考 |
|---|---|---|---|
| Mersha et al. (2024) XAI Survey | 2024年 | YES (§2.4.1) | 古い。MoCKA Phase 4より前に参照 |
| Swamy et al. (2023) XAI post-hoc限界 | 2023年 | YES (§2.4.1) | 同上 |
| NIST AI RMF (2023) | 2023年 | YES (§2.4.2) | 同上。Tabassi (2023) |
| **arXiv:2603.14805** | 2026-03(推定) | **NO** | RELATED_WORK(2026-04-03/04-05)に言及なし。JARVIS段階で新規参照か |
| **arXiv:2604.08059** | 2026-04(推定) | **NO** | 同上 |
| **arXiv:2606.22528** | 2026-06(推定) | **NO** | 同上 |

### 3.2 解釈

**仮説1（検証待ち）:** arXiv:2603, 2604, 2606 は、JARVIS設計段階(2026-08-04)で博士が新規に参照した。つまり、「外部研究を引用してJARVISを停止した」のではなく、「JARVIS設計の過程で外部研究と同じ問題に直面し、参照した」可能性。

**仮説2（検証待ち）:** JARVIS停止の根本理由は「外部研究による影響」ではなく、「MoCKA内部の Authority Flow(DC_20260729_009)が Pending のまま」という制度上の問題。

---

## 4. 次の調査ステップ

### 4.1 必要な追加情報

以下が判定できれば、上記仮説の検証が可能になる：

1. **arXiv:2603.14805 / 2604.08059 / 2606.22528 の実内容**
   - 「capability vs authority」を直接扱っているか
   - 「governance before execution」という表現があるか
   - MoCKA内部で引用されているか(公開記録に痕跡があるか)

2. **Microsoft Build 2026 での「AI Governance」セッション**
   - いつ開催されたか(何月か)
   - どのような内容か

3. **Ravi Shankar「Governance Theatre Series Part 4」**
   - 公開日時
   - 「Proof Does Not Decay With Time」との関連性

4. **PHI_OS_CONSTITUTION_v1.md の正確な作成・確定日**
   - 推定2026-07-25だが、公開記録での確認
   - Decision Ledger での登録日

### 4.2 Phase A完了条件

MoCKA側の公開記録は以下まで整理完了した：

- [x] 「Governance vs Capability」分離が明示化された時点: 2026-07-29(Authority Flow Pending)と2026-08-04(JARVIS実装停止)の2つのピーク
- [x] 根本的障害: HG-J02「Authority 位置未確定」(DC_20260729_009 Pending に依存)
- [x] 外部研究との時間的関係: arXiv:2603等は RELATED_WORK(2026-04-03/04-05)に言及されず、JARVIS段階で新規参照の可能性

---

## 5. Key Finding

**公開記録から見える MoCKA の「実装停止」の根本理由:**

JARVIS は、Authority Flow が Pending のままであるため、
「どこに帰属するのか」「どの Institution の制度に従うのか」が未確定。
この未確定のまま実装を進めることは、後で「制度違反」になる可能性がある。

よって、**実装ではなく「制度整備の完了待ち」を選択した**。

これは、「外部研究の影響」というよりも、**「MoCKA内部で発見された、制度上の不可避的矛盾」**である。

---

## Knowledge Lineage

**Document:** MOCKA_PUBLIC_TIMELINE_GOVERNANCE_BOUNDARY_v0.1.md
**Created:** 2026-08-19
**Purpose:** JARVIS停止仮説の根拠となるMoCKA公開記録の時系列整理
**Source:** Git log / Public markdown documents in docs/
**Scope:** Public records only (Decision Ledger / Event Ledger 非使用)
**Status:** INTERIM(調査進行中・Phase B/C待ち)


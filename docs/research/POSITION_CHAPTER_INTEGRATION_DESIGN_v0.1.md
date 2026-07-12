# Position章 統合設計 v0.1

**ステータス:** 設計文書（配置設計のみ）。本文全面改稿は次工程。ADVANCED表現の昇格判断も次工程（本文完成後）。

**目的:** R01審査（`MoCKA_vs_NIST_AIRMF_TACIP_GAP_ANALYSIS_v1.0.md`、PASS判定）で推奨された次工程のうち、「Position of MoCKA within International AI Governance」章の統合方針・章構成・役割定義を確定する。本文の執筆は行わない。

---

## 1. 三層構造の確定

既存資産と新規章の役割を、重複ではなく分離として位置づける。

```
MOCKA_INTERNATIONAL_AI_GOVERNANCE_POSITION_PAPER_v1.0.md
        |
        | Reference / 思想基盤（変更しない）
        v
Audit Report群
（NIST_REQUIREMENT_CATALOG_v1.0.md
 → MOCKA_NIST_REQUIREMENT_MAPPING_v1.0.md
 → MOCKA_NIST_GAP_ANALYSIS_v1.0.md
 → MOCKA_BEYOND_NIST_ANALYSIS_v1.0.md
 → MOCKA_EVIDENCE_MATRIX_v1.0.md
 → MOCKA_INSTITUTIONAL_COMPLIANCE_AND_BEYOND_SPECIFICATION_v1.0.md
 → VERIFICATION_DEBT_PHASE1_CLOSURE_REPORT_v1.0.md
 → MoCKA_vs_NIST_AIRMF_TACIP_GAP_ANALYSIS_v1.0.md）
        |
        | 検証（評価結果・証拠・確定済みギャップ）
        v
新規章: "Position of MoCKA within International AI Governance"
        |
        | 検証された位置づけ
```

| 層 | 役割 | ステータス |
|---|---|---|
| Position Paper v1.0 | 「MoCKAとは何か」を国際AIガバナンス領域で説明する外部発信向け基礎文書。MoCKAの思想的位置づけ、既存AI Governanceとの差異、Transparency/Verification/Institutional Memoryの意義、将来的な制度的位置づけを含む | **保持・変更なし**（Reference Paperとして扱う） |
| Audit Report群 | NIST文書との逐条比較・証拠収集・ギャップ分析・検証債務解消。全て証拠付きで確定済み | 既存文書として保持・変更なし |
| 新規Position章 | 監査結果（Audit Report群）から見て、MoCKAが国際AIガバナンス上どこに位置するかを説明する、評価文書の結論章 | **本文は次工程で新規作成**。配置先は`MoCKA_vs_NIST_AIRMF_TACIP_GAP_ANALYSIS_v1.0.md`の改訂版（v1.1、既存v1.0は改変せず新版として追加）の最終章とする |

**注:** 既存の`MOCKA_INSTITUTIONAL_COMPLIANCE_AND_BEYOND_SPECIFICATION_v1.0.md`第10章、`MOCKA_INTERNATIONAL_AI_GOVERNANCE_POSITION_PAPER_v1.0.md`第6章、`MoCKA_vs_NIST_AIRMF_TACIP_GAP_ANALYSIS_v1.0.md`第7章にも同名または類似章がすでに存在する。これらは各文書の作成時点の証拠範囲に基づく先行版であり、削除・統合はしない（記録は消さない、MoCKAの原則）。新規Position章はこれらより後発かつ最も広い証拠基盤（E-001〜E-004の実測結果を含む）に基づく最新版として位置づけ、既存3箇所には「本章は新規Position章（次工程）を正本とする」旨の相互参照を新規章完成後に追記することを次工程の範囲に含める。

---

## 2. 新規Position章の構成設計（6項目）

R01提案の構成をそのまま採用する。各項目について、役割・想定執筆内容・参照すべき証拠源を設計する。

### 2.1 Evaluation Context

**役割:** この位置づけがどの評価に基づくかの前提条件を明示する。

**想定内容:** 比較対象がNIST AI RMF Profile on Trustworthy AI in Critical Infrastructure Discussion Draft（2026-07-07、非公式・策定途上）単独であること。比較範囲は`MoCKA_vs_NIST_AIRMF_TACIP_GAP_ANALYSIS_v1.0.md`の12分類・NIST全53Task。ISO/EU AI Act等の他フレームワークは対象外であることを明記。

**参照証拠源:** `MoCKA_vs_NIST_AIRMF_TACIP_GAP_ANALYSIS_v1.0.md` 冒頭「対象資料」節、`NIST_REQUIREMENT_CATALOG_v1.0.md` §0（ステータス・策定途上である旨）

### 2.2 Current Position

**役割:** 評価分布の事実整理（主張ではなく集計）。

**想定内容:** ADVANCED 1件・ACHIEVED 3件・PARTIAL 7件・NONE 1件という分布そのものを提示し、「全部達成」でも「全部PARTIAL」でもない現実的な分布であることを示す。

**参照証拠源:** `MoCKA_vs_NIST_AIRMF_TACIP_GAP_ANALYSIS_v1.0.md` §4・§5

### 2.3 Comparison with Existing Governance Frameworks

**役割:** NIST Discussion Draftとの比較に限定した位置づけ（他フレームワークとの比較はしない、既存Position Paper第6章の制約を継承）。

**想定内容:** MoCKAが対象とする文脈（AIが組織の統治プロセスに参加する）とNISTが対象とする文脈（AIが物理インフラを操作する）の違いを整理し、重なる領域（Accountability/Explainability決定レベル/Traceability/Incident Management）でのみ直接比較が成立することを明示。

**参照証拠源:** `MoCKA_vs_NIST_AIRMF_TACIP_GAP_ANALYSIS_v1.0.md` §7既存段落、`MOCKA_INTERNATIONAL_AI_GOVERNANCE_POSITION_PAPER_v1.0.md` §6

### 2.4 Unique Contribution

**役割:** MoCKA独自の制度的要素を、R01条件（ADVANCED表現の慎重化）を踏まえて記述する。

**想定内容:** Incident Management（Integrity Ledger運用実績）を「ADVANCED」ではなく、次工程のADVANCED証拠境界確認の結果に応じて「ADVANCED (within evaluated scope)」または「ADVANCED候補」として記述する（本デザイン文書では表現を確定しない。証拠境界確認は本文執筆時に別途実施）。Knowledge Managementの「思想はADVANCED候補・実証はPARTIAL」という二層分離（R01が高く評価した論点）も本節に反映する。

**参照証拠源:** `MoCKA_vs_NIST_AIRMF_TACIP_GAP_ANALYSIS_v1.0.md` §3.11（Incident Management ADVANCED根拠）、§3.12（Knowledge Management）

### 2.5 Remaining Limitations

**役割:** 未解決事項を隠さず列挙する（既存文書の否定的証拠を格上げ・削除しない原則の継続）。

**想定内容:** `VERIFICATION_DEBT_PHASE1_CLOSURE_REPORT_v1.0.md`のE-001（PENDING_DECISION）・E-004（INVALIDATED）を含む、§8「Remaining Gap Analysis」の最優先3項目をそのまま引用する。

**参照証拠源:** `MoCKA_vs_NIST_AIRMF_TACIP_GAP_ANALYSIS_v1.0.md` §8、`VERIFICATION_DEBT_PHASE1_CLOSURE_REPORT_v1.0.md` §1・§5

### 2.6 Future Institutional Role

**役割:** 誇張を避けた将来像の記述（「今後の予定」を「達成済み」と混同しない原則の継続）。

**想定内容:** §9「Roadmap」の内容を踏まえ、是正完了後の再評価予定（v1.1改訂条件）を明示する。断定的な将来予測は行わない。

**参照証拠源:** `MoCKA_vs_NIST_AIRMF_TACIP_GAP_ANALYSIS_v1.0.md` §9

---

## 3. 次工程の実施順序（本デザイン文書のスコープ外、確認のみ）

1. ADVANCED評価（Incident Management）の証拠境界確認（NIST側がTBDだから優位に見えるのか、MoCKA側が成熟しているから優位なのかの分離）
2. 上記結果を踏まえた§2.4の表現確定
3. 「MoCKAが既に達成済みの領域」と「今後完成すべき領域」の二層分離表の作成（§2.2・§2.5と連動）
4. 新規Position章本文の執筆（本設計に基づく、`MoCKA_vs_NIST_AIRMF_TACIP_GAP_ANALYSIS_v1.0.md` v1.1として追加）
5. 既存3箇所（Institutional Compliance Specification第10章／Position Paper第6章／Gap Analysis v1.0第7章）への相互参照追記

**本ターンの実施範囲はここまで（配置設計の確定）。上記1-5は次工程。**

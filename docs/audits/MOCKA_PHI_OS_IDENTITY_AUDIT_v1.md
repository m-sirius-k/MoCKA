# MoCKA PHI-OS Identity Audit v1.0

**Status:** AUDIT
**前提:** [[MOCKA_HUMAN_GATE_REGISTRY_AUDIT_v1]]を正式な識別台帳として参照し、同台帳が確立した`{領域接頭辞}-REG-{NN}`形式のRegistry ID命名規則を本監査でも暫定適用する（接頭辞`PHI`）。
**目的:** PHI-OS同名別実体問題を整理し、MoCKAにおけるPHI-OSの正式な系譜と境界を確定する。
**実装・新規実装・リネーム:** 禁止。本文書は監査文書のみ。
**調査方法:** リポジトリ全体grep（`phi_os`/`phi-os`/`PHI-OS`を含むファイル・ディレクトリ）、各実体冒頭部・憲法文書・設計書の読込、git log初出コミット日時確認。

---

## 1. Identity Registry

| Registry ID | Name | Origin Path | 初出日 | Classification | Current Status |
|---|---|---|---|---|---|
| PHI-REG-01 | MoCKA本体系PHI-OS（Persistent History Intelligence OS） | `C:\Users\sirok\MoCKA\phi_os\`（+ `PHI_OS_CONSTITUTION_v1.md`） | 2026-06-16（`phi_os/__init__.py`初出コミット） | Institutional Authority / Constitution Kernel | RATIFIED v1（`PHI_OS_CONSTITUTION_v1.md`）。Phase5 Institution Runtime・Event Gate・Human Gate（HG-REG-01）・dictionary.py等を内包し稼働中。 |
| PHI-REG-02 | PlanningCaliber配下PHI-OS（Platform Hub Integration OS） | `C:\Users\sirok\MoCKA\PlanningCaliber\workshop\phi-os\` | 2026-05-29（`extension/manifest.json`初出コミット）。内部`phios/`コア分離は2026-06-12（`phios/boot.py`） | Chrome Extension Shared Runtime Layer | v1.0実機テスト完了（TODO_195）。`MOCKA_OVERVIEW.json`の`repositories.phi_os`エントリが指すのは本実体。 |
| PHI-REG-03 | sirius-lab-products配下PHI-OS（パッケージ版） | `C:\Users\sirok\MoCKA\PlanningCaliber\sirius-lab-products\phi-os\` | 不明（README記載のみ、"Coming Soon"） | Product Packaging Placeholder | README/CHANGELOGのみ存在。実コードなし。所属リポジトリ`sirius-lab-products`はアーカイブ化済み（[[project_sirius_lab]]参照）。 |
| PHI-REG-04 | その他PHI-OS表記資産（`phi_os_bridge.py`等のブリッジ参照） | `PlanningCaliber/workshop/seo-os/mocka/phi_os_bridge.py` | 個別確認未実施（SEO-OS Phase実装の一部） | Cross-Reference Bridge（実体ではなく参照） | 稼働中。`MOCKA_DB`（`data/mocka_events.db`）へ直接INSERTし、PHI-REG-01（MoCKA本体）の監査証跡に書き込む。物理配置はPlanningCaliber配下だが指す先はPHI-REG-01。 |

**所見:** 「PHI-OS」という1つの名前が、**完全に異なる2つの正式名称（Persistent History Intelligence OS / Platform Hub Integration OS）**を持つ独立した実体（PHI-REG-01・PHI-REG-02）に使われている。これはHuman Gateのケース（同一語が分類をまたぐ）よりも一段深刻で、**展開形（Expansion）自体が異なる**。PHI-REG-03はPHI-REG-02のパッケージ版（同一概念）、PHI-REG-04はPHI-REG-01への参照ブリッジ（実体ではない）であり、実質的な独立概念はPHI-REG-01とPHI-REG-02の2つに収束する。

---

## 2. Origin分析

- **PHI-REG-01（MoCKA本体系）:** Origin文書は`PHI_OS_CONSTITUTION_v1.md`（2026-06-16、MoCKA Phase4制度実装フェーズの成果物）。前提資料として`BINDING_REGISTRY_v1.md`/`MEANING_AUTHORITY_v1.md`/`INSTITUTION_BINDING_MAP_v1.md`を基礎とする。位置づけは「MoCKA全体の唯一の制度執行機関」であり、Event Authority/Knowledge Authority/Gate Authority等6つのAuthorityを統括する制度カーネル。
- **PHI-REG-02（PlanningCaliber配下）:** Origin文書は`PHI OS 設計書 v1.0`（`DESIGN_v1.md`、2026-06-01作成、TODO_186・確定イベントE20260526_044）。3AI合議反映版として「Chrome拡張機能群（Orchestra/Relay/Memory/Prism等）の共有神経系」と自己定義。UIを持たないサービスワーカー常駐型ランタイムで、イベントバス・状態ストア・スキーマ管理・権限管理の4機能のみを提供。`PHI-OS_Core_Spec_v1.0_addendum.md`（2026-06-11発行）がnode_id命名規則（`phi-os-{layer}-{product}-{instance}`）を定義。
- **両者の起源は完全に独立。** PHI-REG-02（2026-05-29 Chrome拡張初出、2026-06-01設計書）はPHI-REG-01（2026-06-16制度憲法）より約2週間〜1ヶ月先行して存在していた。名称の衝突は、後発のMoCKA本体Phase4制度実装が「PHI-OS」という名前を独立に採用した結果であり、相互参照や派生関係は存在しない。

---

## 3. Parent/Derived関係分析

| 実体 | Parent Documents | Derived From | Supersedes |
|---|---|---|---|
| PHI-REG-01 | `BINDING_REGISTRY_v1.md` / `MEANING_AUTHORITY_v1.md` / `INSTITUTION_BINDING_MAP_v1.md` / `BINDING_GAP_REPORT_v1.md` / `IMPLEMENTATION_PRIORITY_v1.md` | MoCKA Phase4制度設計フェーズの成果物群 | （無し） |
| PHI-REG-02 | `PHI OS 設計書 v1.0`（3AI合議反映版）/ `PHI-OS_Core_Spec_v1.0.docx`（本体）/ `PHI-OS_Core_Spec_v1.0_addendum.md` | TODO_186・E20260526_044を起点とするPlanningCaliber製品設計 | （無し） |
| PHI-REG-03 | PHI-REG-02のパッケージ版README | PHI-REG-02 | （無し、PHI-REG-02のComing Soon版） |
| PHI-REG-04 | PHI-REG-01の`mocka_events.db`スキーマ | SEO-OS Phase実装の一部 | （無し） |

**結論:** PHI-REG-01とPHI-REG-02の間にParent/Derived関係は存在しない（完全に独立した2系統）。PHI-REG-03はPHI-REG-02の派生（パッケージング）。PHI-REG-04はPHI-REG-01への書き込み参照だが、それ自体はPHI-REG-01のサブシステムではなくSEO-OS側に属する外部ブリッジである。

---

## 4. Governance Scope分析

| 実体 | Governance Scope |
|---|---|
| PHI-REG-01 | MoCKA制度全体（`PHI_OS_CONSTITUTION_v1.md`第1章: 「Human、AI、MCP、CLI、Script、Runtime、External Systemが従うべき原則」）。Event/Knowledge/Gate/Version/Verification/Institution Authorityの6Authorityを保持し、Human Gate Registry（HG-REG-01〜05）が定義する制度的裁定主体（HG-REG-04）の上位制度枠組みに相当する。 |
| PHI-REG-02 | PlanningCaliber配下のChrome拡張製品群（Orchestra/Relay/Memory/Prism）に限定。MoCKA制度全体のGate Authority・Event Authorityには従属しない独立ランタイムであり、自身のスキーマ管理・権限管理を内部で完結させる。 |
| PHI-REG-03 | Governance Scopeなし（実コード不在、パッケージ説明のみ）。 |
| PHI-REG-04 | Scopeなし（ブリッジ機能のみ）。実際の書き込み先であるPHI-REG-01のGovernance Scope配下で評価されるべき動作。 |

**所見:** PHI-REG-01は「制度全体の執行機関」、PHI-REG-02は「特定製品群限定のランタイム」であり、Governance Scopeの階層・対象範囲が全く異なる。両者が同じ「PHI-OS」を名乗ることで、文書上「PHI-OSがXを承認した」という記述だけでは、制度全体の話か特定Chrome拡張内の話か判別できないという実務上の混乱が生じる。

---

## 5. Human Gateとの関係整理

- **PHI-REG-01とHuman Gate Registryの関係:** PHI_OS_CONSTITUTION_v1.md第3章のAuthority体系には「Human Gate」という名称のAuthorityは存在しないが、HG-REG-01（`phi_os/human_gate.py`）はPHI-REG-01のディレクトリ（`phi_os/`）配下に実装されているサブモジュールである。すなわちHG-REG-01はPHI-REG-01の制度的子要素という位置づけになるが、[[MOCKA_HUMAN_GATE_IDENTITY_AUDIT_v1]]が既に指摘した通り、HG-REG-01自体はPHI-REG-01の制度原則（原則3「Gateのみが制度変更を承認できる」、原則2「PHI-OSのみが制度を定義できる」）に対する権限チェックを技術的に実装していない。**この監査は、PHI-REG-01憲法の原則がディレクトリ配置だけでは下位モジュールに自動適用されないことを示す追加の根拠を提供する。**
- **PHI-REG-02とHuman Gateの関係:** PlanningCaliber配下PHI-OS（PHI-REG-02）には独自のHuman Gate実体は確認されなかった。`phios/core/execution_gate.py`という類似名称のモジュールが存在するが、これはHuman Gate Registry（HG-REG-01〜05）のいずれとも別系統であり、本Identity Auditでは新規Registry対象として扱わない（必要であれば別途Execution Gate Identity Auditを要する）。
- **結論:** Human GateとPHI-OSの直接的な制度的連結はPHI-REG-01側にのみ存在し、かつその連結はHuman Gate Identity Auditで既に「Partially Compatible」と判定済みの脆弱な連結である。PHI-REG-02側にはHuman Gate相当の概念は存在しない。

---

## 6. Orchestra/Relay/Memoryとの関係整理

- **PHI-REG-02が唯一、Orchestra/Relay/Memoryと直接の制度的・技術的連結を持つ。** `PHI-OS_Core_Spec_v1.0_addendum.md`のnode_id命名規則（`phi-os-mini-orchestra-001`/`phi-os-mini-relay-001`/`phi-os-mini-memory-001`）がこれを明文化している。`extension/adapters/orchestra-adapter.js`・`relay-adapter.js`・`memory-adapter.js`が実コードとして存在し、各製品はPHI-OS未インストール時でも単体動作を保証する設計（Coming Soon版PHI-REG-03のREADMEにも「Orchestra/Relay/Memory連携」と明記）。
- **PHI-REG-01はOrchestra/Relay/Memoryと直接連結しない。** `PHI_OS_CONSTITUTION_v1.md`にOrchestra/Relay/Memoryへの言及は無く、MoCKA本体（`MOCKA_OVERVIEW.json`の`products`セクション）ではOrchestra/Relay/Memoryは個別の商用製品として記述され、PHI-REG-01の制度Authorityの直接の対象としては扱われていない。
- **ただし`PHI-OS_Core_Spec_v1.0_addendum.md`第5項は「mocka_write_eventのwhoフィールドに必ず使用する」とPHI-REG-02のnode_idをMoCKA本体イベント記録フォーマットに接続することを定めており、ここでPHI-REG-02がPHI-REG-01のEvent Ledgerへ間接的に接続される設計が示唆されている。** これは現状では設計記述のみで、実コード上の接続確認は本監査の対象範囲外（別途Binding監査が必要）。
- **結論:** 「PHI-OSがOrchestra/Relay/Memoryを統括する」という言明は、PHI-REG-02を指している場合のみ正確であり、PHI-REG-01を指す文脈でこの言明を使うと誤りになる。

---

## 7. 名前衝突リスク評価

### 名前衝突
- PHI-REG-01・PHI-REG-02は完全に異なる正式名称（Persistent History Intelligence OS / Platform Hub Integration OS）と完全に異なる責務（制度カーネル全体 vs 特定Chrome拡張製品群の共有神経系）を持つにもかかわらず、共に単に「PHI-OS」と略称される。Human Gateのケース（[[MOCKA_HUMAN_GATE_IDENTITY_CONSOLIDATION_AUDIT_v1]]）でO0-Human Gateが既に名前衝突を自覚的に解消した前例があるのに対し、PHI-OSの2系統は**展開形が異なるという衝突の根深さにもかかわらず、解消する文書がこれまで存在しなかった**。
- `MOCKA_OVERVIEW.json`の`repositories.phi_os`エントリは「PHI-OS」をPHI-REG-02（PlanningCaliber配下）に対して使用しているが、`PHI_OS_CONSTITUTION_v1.md`は「PHI-OS」をPHI-REG-01（MoCKA本体制度カーネル）として定義している。**マスターオーバービュー文書と制度憲法文書の間で、同じ名前が異なる実体を指す状態が既に発生している。**

### 意味衝突
- PHI-REG-01は「制度を定義し承認する執行機関」、PHI-REG-02は「製品間のデータ共有を担う通信層」であり、両者の意味的方向性は重ならないが排他的でもない（制度 vs 通信基盤という異なる軸）。Human Gateのケース（裁定の意味論が正反対）と異なり、PHI-OSの場合は**意味が衝突するのではなく単純に無関係**という点が特徴的である。

### ガバナンス衝突
- 直接のガバナンス衝突は確認されなかった。PHI-REG-01がPHI-REG-02のGate Authorityを侵害する、またはその逆という構造は存在しない（両者は独立階層）。ただし`phi_os_bridge.py`（PHI-REG-04）がPHI-REG-01のDBへ直接INSERTしている実装は、PHI_OS_CONSTITUTION_v1.md第5.1項「DB直接更新によるEvent生成」禁止事項（Event Authorityを迂回するため）に**抵触する可能性がある**。これはPHI-OS同名問題そのものではないが、本監査の調査過程で発見された付随的なConstitutional Violation候補であり、別途確認を要する。

### Code Binding影響
- 将来Phase1 Code Binding等でCoreモジュールを新規実装する際、開発者（AIまたは人間）が「PHI-OS」という名前だけでimport対象を検索すると、`phi_os`（MoCKA本体、Python）と`phi-os`/`phios`（PlanningCaliber、Chrome拡張のPython/JS混在）のどちらを指すか即座に判別できない。パスとして`C:\Users\sirok\MoCKA\phi_os\`と`C:\Users\sirok\MoCKA\PlanningCaliber\workshop\phi-os\`が両方存在し、ディレクトリ名の差（アンダースコア vs ハイフン）のみが区別点になっている点は誤認リスクが高い。

---

## PHI-OS Identity Risk: **High**

判定理由：

- **Mediumに留まらない理由:** Human Gateのケース（Medium判定）は同一語が分類をまたぐ「曖昧化」だったが、PHI-OSのケースは**完全に異なる正式名称・責務・Governance Scopeを持つ2つの実体**が同じ略称を共有しており、かつそれが`MOCKA_OVERVIEW.json`（マスター参照文書）と`PHI_OS_CONSTITUTION_v1.md`（制度憲法）という**最上位文書同士の間で既に矛盾した参照**を生んでいる。これは「将来誤用するリスク」ではなく「現在進行形で参照が割れている」状態であり、Mediumの基準（次の実装ステップで誤認が発生し得る）を超えている。
- **Lowに該当しない理由:** 自明。
- 緩和要因（Highの中でも致命的事故未発生）: PHI-REG-01とPHI-REG-02はディレクトリ・実行環境（Python制度カーネル vs Chrome拡張）が完全に分離されており、現時点でコードレベルの直接衝突（同一プロセス内でのimport衝突等）は発生していない。また`phi_os_bridge.py`の発見した潜在的Constitutional Violationも、稼働は確認されたが「PHI-OS」名称問題そのものに起因する事故ではない。

---

## Knowledge Lineage

Document:
MOCKA_PHI_OS_IDENTITY_AUDIT_v1.md

Status:
Review

Created:
2026-06-24

Last Reviewed:
2026-06-24

Origin:
[[MOCKA_HUMAN_GATE_REGISTRY_AUDIT_v1]]完了後、博士指示によりPHI-OS同名別実体問題の整理として実施。Human Gate Registryの命名規則（`{接頭辞}-REG-{NN}`）を継承。

Parent Documents:

* MOCKA_HUMAN_GATE_REGISTRY_AUDIT_v1.md
* PHI_OS_CONSTITUTION_v1.md
* docs/audits/MOCKA_HUMAN_GATE_IDENTITY_AUDIT_v1.md

Derived From:
MOCKA_HUMAN_GATE_REGISTRY_AUDIT_v1（Registry ID命名規則・調査フォーマットの継承元）

Supersedes:
（無し）

Reason For Creation:
「PHI-OS」という名称がMoCKA本体（Persistent History Intelligence OS）とPlanningCaliber配下（Platform Hub Integration OS）という展開形の異なる2実体に使われている問題を整理し、MoCKAにおけるPHI-OSの正式な系譜と境界を確定するため。

Affected Components:

* phi_os/（MoCKA本体、PHI-REG-01）
* PHI_OS_CONSTITUTION_v1.md
* PlanningCaliber/workshop/phi-os/（PHI-REG-02）
* PlanningCaliber/sirius-lab-products/phi-os/（PHI-REG-03）
* PlanningCaliber/workshop/seo-os/mocka/phi_os_bridge.py（PHI-REG-04）
* MOCKA_OVERVIEW.json（repositories.phi_osエントリ）

Related Documents:

* MOCKA_HUMAN_GATE_REGISTRY_AUDIT_v1.md
* MOCKA_HUMAN_GATE_IDENTITY_AUDIT_v1.md
* MOCKA_HUMAN_GATE_IDENTITY_CONSOLIDATION_AUDIT_v1.md
* PHI-OS_Core_Spec_v1.0_addendum.md
* DESIGN_v1.md（PHI OS設計書v1.0、PlanningCaliber配下）

Revision History:

Revision:
R1

Date:
2026-06-24

Reason:
新規作成

Change:
初版作成（第1部Identity Registry4件＋第2部Origin分析＋第3部Parent/Derived関係＋第4部Governance Scope＋第5部Human Gate関係＋第6部Orchestra/Relay/Memory関係＋第7部名前衝突リスク評価＋判定High）

Impact:
PHI-OS名称の系譜・境界を確定する審査材料を提供。`phi_os_bridge.py`のDB直接書き込みについてConstitutional Violation候補を発見し記録（別途確認要）。コード変更・実装・リネームは無し。

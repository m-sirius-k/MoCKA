# MoCKA Lineage Governance Audit v1.0

**Status:** AUDIT — Knowledge Lineage Standard v1.0をMoCKA全体（文書・コード・アーキテクチャ）へ拡張すべきかの監査
**基準文書:** [[mocka_knowledge_lineage_standard_v1]]
**目的:** 文書だけでなく重要コード・サービス・アーキテクチャにも系譜情報を持たせるべきかを整理する。
**実装・書き込み:** 禁止。既存ファイル変更禁止。本文書は監査報告書のみ。
**調査方法:** 実リポジトリ（`C:/Users/sirok/MoCKA`）のディレクトリ構造・主要ファイルをgit/lsで確認した上で記述（推測のみの記載は行わない）。

---

## 第1部 長期運用上、Lineageが必要な対象の列挙

### 1.1 Document Lineage（既存標準の対象、確認済み）

- `docs/spec/`（8文書確認: moCKA_spec_v1.0.2-rc.md / moCKA_phaseC_execution_boundary_v1.md / moCKA_phaseD_execution_core_v1.md / moCKA_phaseD_execution_flow_v1.md / moCKA_phaseD_execution_contract_v1.md / moCKA_phaseD_execution_enablement_v1.md / moCKA_app_boundary_v1.md / moCKA_human_gate_v1.md）
- `docs/governance/`（38文書確認、Module系13文書・Phase10系9文書・Human Gate系5文書・Code Binding系2文書等）
- `docs/audits/`（44文書確認、Phase10-3系列が最多）

### 1.2 Code Lineage（本監査で新たに調査対象として確定した範囲）

実ファイル確認結果：

| カテゴリ | 確認済みファイル |
|---|---|
| app.py | `app.py`（4063行、port:5000、COMMAND CENTER。複数の`.bak`系列ファイルが並存：`app.py.bak`/`app.py.bak_20260429_115300`/`app.py.bak_phase2`/`app_backup_20260427_063833.py`/`app_bak_0501.py`/`app_broken.py`等。これら自体もLineageが無い「出自不明資産」として今回確認された） |
| Human Gate関連 | `phi_os/human_gate.py`、`docs/contracts/`配下のHuman Gate契約群、`relay/`内のpolicy_engine.py（Human Gateとの関係は別途要確認） |
| Observer関連 | `runtime/monitoring/observer.py`（コードベース内で「Observer」を名乗る実体は本ファイルのみ確認。Time OS Contractの`observer()`関数群（`decision_log_detail()`/`_calc_todo_risk_score()`）は`app.py`内に実装されており別系統） |
| Execution関連 | `app.py`（実行終端として既存Spec文書で定義済みだが、Execution engine自体はまだ実装されていない＝設計のみ） |
| Background Service関連 | `app.py`内のモジュールレベルthread起動群（136-137行/2111-2112行/2693-2695行/2823-2824行、AUTO-AUDIT/auto sync等）。これらは既知incident（INCIDENT_IMPORT_APP_SIDE_EFFECT）の発生源であり、出自・変更理由の記録が無い状態で長期運用されている。 |
| Registry関連 | `ARCHITECTURE_REGISTRY.json`（+backup）、`node_registry.py`、`phi_os/runtime/gate_registry.py`、`phi_os/runtime/institution_registry.py`、`phi_os/runtime/meaning_registry.py`、`docs/contracts/adapter_registry_v1.md`、`docs/contracts/capability_registry_v1.md`、`docs/governance/MODULE_REGISTRY_MODEL_v1.md` |

**所見:** コード資産には現在いかなる形式のLineage情報も存在しない。特に`app.py`系の`.bak`ファイル群（最低7種確認）は、いつ・なぜ作られたかの記録が無いまま並存しており、これは「Lineageが無いことの実害」が既に発生している具体例である。

### 1.3 Architecture Lineage

実ディレクトリ確認結果：

| システム | 実体確認 |
|---|---|
| PHI-OS | `phi_os/`（runtime/, api/, semantic/, context/等のサブモジュール多数）。`PlanningCaliber/workshop/phi-os/`という別系統のChrome拡張版も存在（同名・別実体、関係未整理） |
| Orchestra | `orchestra/`（`conflict_interpreter.py`のみ確認。MOCKA_OVERVIEW記載の本番稼働システムとの対応関係は本ディレクトリ単体では薄い＝本体は別repoの可能性） |
| Relay | `relay/`（relay_kernel.py / event_queue.py / replay_engine.py / replay_engine_v2.py / replay_router.py / repositories.py / repositories_sqlite.py / mcp_bridge.py / policy_engine.py / relay_bootstrap.py / action_router.py / replay_audit.py、計13ファイル確認。Phase5系列で段階実装されてきたことが[[project_mocka_phase5]]と一致） |
| Memory | `memory/`、`MEMORY_LAYER.md`（実体・文書とも存在確認） |
| Human Gate | コードは`phi_os/human_gate.py`1ファイルのみ確認。一方でガバナンス文書は`docs/governance/`配下に5文書以上存在（mocka_human_gate_decision_definition_v1.md等）。**コード1点に対し文書が多数という非対称構造**が確認された。 |
| Event Integrity Framework | `EVENT_INTEGRITY_v1.md`（リポジトリルート）、`phi_os/integrity.py`、`phi_os/integrity_routes.py`、`docs/architecture/EVENT_ENTRY_v1.md`相当（[[project_mocka_phase5]]記載）。tag `mocka-production-v1.0-event-integrity`で確定済み。 |
| その他主要構成要素（確認のみ・本監査スコープ外候補） | `mocka_mcp_server.py`（MCP, port:5002）、`core_kernel/`、`gateway/`、`learning_kernel/`、`structural/`、`cognitive/`、`semantic/`、`distribution/` — いずれもトップレベルに実体ディレクトリが存在するが、本監査では深掘りしていない。 |

**所見:** PHI-OSの「同名・別実体」（MoCKA本体内とPlanningCaliber内）、Orchestraの「本体不在の疑い」、Human Gateの「文書過多・コード過少」は、いずれもLineageが無いために発生している整理不能状態の具体例である。

---

## 第2部 Tier分類の提案

| Tier | 定義 | 該当資産（確認済み） |
|---|---|---|
| **Tier A** | 停止・誤動作時にMoCKA全体の整合性・記録の正当性に重大影響を与える資産 | `app.py`（唯一の実行終端・COMMAND CENTER）、Event Integrity Framework（`phi_os/integrity.py`等）、`mocka_events.db`（SQLite単一化済みの唯一の正式台帳）、Human Gate（`phi_os/human_gate.py`＋関連契約群）、`mocka_mcp_server.py`（記録経路の単一入口） |
| **Tier B** | MoCKAの主要機能を担うが、停止しても他のTier A資産の正当性自体は保たれる資産 | PHI-OS（`phi_os/`配下のRuntime/API/Semantic等）、Relay（`relay/`配下全体）、Memory（`memory/`、MEMORY_LAYER.md）、Registry群（`ARCHITECTURE_REGISTRY.json`、各種`*_registry.py`） |
| **Tier C** | 補助・実験・個別製品機能であり、停止してもMoCKA制度核には影響しない資産 | Orchestra（`orchestra/conflict_interpreter.py`）、各種`fix_*.py`/`patch_*.py`（リポジトリルートに多数確認、既に[[project_mocka_phase5]]のクリーンアップ対象として認識済み）、`OLD_FILES`、各種`.bak`系ファイル |

**Tier未分類の注意点:** `app.py`内のBackground Service（モジュールレベルthread起動群）はTier Aの一部（app.py自体）に物理的に内包されているが、機能としては既知incidentの発生源であるため、**Tier A内でも特に高リスクな部分集合**として別途フラグを立てる必要がある。これはTier分類が「ファイル単位」では粒度不足になる例である。

---

## 第3部 各Tierに必要なLineage項目の定義

### Document Lineage（既存標準どおり、Tier別の適用強度のみ差をつける）

| 項目 | Tier A | Tier B | Tier C |
|---|---|---|---|
| Origin | 必須 | 必須 | 推奨 |
| Parent Documents | 必須 | 必須 | 任意 |
| Derived From | 必須 | 推奨 | 任意 |
| Reason For Creation | 必須 | 必須 | 推奨 |
| Affected Components | 必須 | 必須 | 任意 |
| Related Documents | 必須 | 推奨 | 任意 |
| Revision History | 必須 | 推奨 | 任意 |

### Code Lineage（新規提案、候補項目をTier別に整理）

| 項目 | Tier A | Tier B | Tier C |
|---|---|---|---|
| Component | 必須 | 必須 | 推奨 |
| Role | 必須 | 必須 | 推奨 |
| Origin | 必須 | 推奨 | 任意 |
| Related Specs | 必須 | 推奨 | 任意 |
| Critical Dependencies | 必須 | 必須 | 任意 |
| Modification Policy | 必須（Human Gate承認要否を明記） | 推奨 | 任意 |
| Last Architecture Review | 必須 | 推奨 | 任意 |

Tier A固有の追加候補（本監査で必要性が確認された項目）：
- **Known Side Effects**（既知incident参照、例: `app.py`のモジュールレベルthread起動群はINCIDENT_IMPORT_APP_SIDE_EFFECTを必ず参照させる）

### Architecture Lineage（新規提案）

| 項目 | Tier A | Tier B | Tier C |
|---|---|---|---|
| System | 必須 | 必須 | 推奨 |
| Purpose | 必須 | 必須 | 推奨 |
| Parent System | 必須 | 推奨 | 任意 |
| Child Systems | 必須 | 推奨 | 任意 |
| Dependencies | 必須 | 必須 | 任意 |
| Governance Scope | 必須 | 推奨 | 任意 |
| Review History | 必須 | 推奨 | 任意 |

Tier A固有の追加候補：
- **Name Collision Note**（同名・別実体の明示。例: PHI-OSがMoCKA本体とPlanningCaliber配下に別実体として存在する事実を両方の文書に明記する）

---

## 第4部 遡及適用計画（案の整理のみ、本監査では実施しない）

| 対象候補 | Tier想定 | 遡及適用の必要性評価 |
|---|---|---|
| Readiness Review（[[MOCKA_CODE_BINDING_READINESS_REVIEW_v1]]） | Tier A（docs/audits） | 必要性高。Code Bindingという最重要案件の起点文書であり、Parent Documents/Derived Fromの記録価値が高い。 |
| Human Gate Decision Draft（[[MOCKA_CODE_BINDING_HUMAN_GATE_DECISION_DRAFT_v1]]） | Tier A | 必要性高。Finalizationの直接の親文書であるため、Lineageの「鎖」が途切れると追跡不能になる。 |
| Human Gate Finalization（[[MOCKA_CODE_BINDING_HUMAN_GATE_FINALIZATION_v1]]） | Tier A | 必要性最高。博士の裁定そのものを記録する文書であり、将来この裁定を参照する全文書がここに辿り着く必要がある。 |
| Phase C文書群（3文書） | Tier A | 必要性高。Phase D全体の親文書。 |
| Phase D文書群（4文書） | Tier A | 必要性高。Phase C/Spec v1.0.2-rcとの依存鎖が複雑なため、明文化の効果が大きい。 |
| `app.py` | Tier A（Code Lineage） | 必要性最高。ただし「既存ファイル変更禁止」の制約下では、`app.py`本体にコメントとして埋め込むのではなく、**別建てのCode Lineage台帳ファイル**（例: `docs/lineage/app_py_lineage_v1.md`）として外部記録する方式が必須（コア書込ポリシー上、app.py自体の改修はHuman Gate承認が必要なため）。 |
| Event Integrity Framework関連 | Tier A（Architecture Lineage） | 必要性高。tag `mocka-production-v1.0-event-integrity`という確定済み基準点があるため、Lineage記録の土台は既にある（Originとして転記可能）。 |

**遡及適用の実施順序案（提案のみ）:** Human Gate Finalization → Decision Draft → Readiness Review → Phase D文書群 → Phase C文書群 → Event Integrity Framework → app.py Code Lineage台帳、の順が依存関係上自然（裁定文書から遡る方が、後から読む人間にとって追跡しやすい）。

---

## 第5部 運用コスト評価

| 適用方針 | コスト | 効果 | リスク |
|---|---|---|---|
| **全面適用**（Document/Code/Architecture全資産、Tier問わず） | 最大。docs/audits 44文書＋docs/governance 38文書＋docs/spec 8文書＝90文書に加え、コード資産（Tier A〜C問わず多数のpyファイル）全てに台帳作成が必要。`fix_*.py`/`patch_*.py`等の既に陳腐化した資産にも適用すると、無意味な記録作業が発生する。 | 最大（理論上は完全な追跡可能性） | 運用が破綻する可能性が高い。MoCKAは既に「文書数が多くなってきた」という既存の懸念（[[mocka_full_static_structure_map_v1]]）を抱えており、全面適用はこれを悪化させる。 |
| **Tier Aのみ** | 中程度。本監査で確認した範囲では、Tier A相当は文書側で概算10〜15文書（Code Binding系・Human Gate系・Event Integrity系）、コード側で5〜7ファイル（app.py、phi_os/human_gate.py、phi_os/integrity.py、mocka_mcp_server.py等）、アーキテクチャ側で3〜4系統（Event Integrity Framework、Human Gate、PHI-OS中核部分）。 | 高い。MoCKA全体の「停止時重大影響資産」をほぼ全てカバーできる。 | Tier境界の判定基準が曖昧な場合、運用者の裁量でTier Bがすり抜ける可能性。 |
| **Tier A+B** | 中〜高。Relay全体（13ファイル）、PHI-OS全体、Registry群が追加されるため、コストはTier Aのみの2〜3倍程度になると見込まれる。 | 非常に高い。主要機能資産まで含めて追跡可能になる。 | Phase5/Phase10系列のように継続的に文書が増え続けている領域では、Lineage記録自体が新たな運用負荷源になる可能性。 |
| **新規作成文書のみ**（既存資産には遡及適用しない） | 最小。今後作成する文書・コードにのみKnowledge Lineageセクションを必須化。 | 限定的。既存の混乱（app.pyの`.bak`群、PHI-OS同名別実体等）は解消されないまま放置される。 | 「いつから記録が始まったか」の境界が将来の運用者にとって不明瞭になりうる（境界線自体をLineage Standardの付則として明記すれば軽減可能）。 |

---

## 第6部 最終提言

最終判定（採用方針の決定）は行わない。以下、4観点での評価のみ示す。

| 観点 | 全面適用 | Tier Aのみ | Tier A+B | 新規作成文書のみ |
|---|---|---|---|---|
| 制度維持性 | 高いが運用破綻リスクで実質低下 | 高い（最重要資産は守られる） | 最高 | 低い（既存資産の混乱が放置される） |
| 長期記憶性 | 理論上最高だが実運用で形骸化しやすい | 高い | 高い | 中（新規分のみ記憶される） |
| 監査容易性 | 低下（情報過多） | 高い | 高い | 中（既存資産の監査は従来通り困難） |
| 運用負荷 | 最大（持続困難） | 中 | 中〜高 | 最小 |

**所見（提言ではなく観察）:** 4観点を素直に並べると「Tier A+B」が最も高評価の項目を多く持つが、運用負荷も相応に高い。一方「Tier Aのみ」は3観点で高評価を維持しつつ運用負荷を抑えられている。「全面適用」は理論値こそ高いが、MoCKAが既に文書過多を自覚している現状（[[mocka_full_static_structure_map_v1]]）を踏まえると実運用での形骸化リスクが大きい。「新規作成文書のみ」は最も安全だが、既に発生している実害（app.py `.bak`群の出自不明化、PHI-OS同名別実体問題）を解消しない。

**博士が裁定すべき論点（本監査が提示する選択肢、判定はしない）：**
1. 適用方針：全面適用／Tier Aのみ／Tier A+B／新規作成文書のみ
2. 遡及適用を実施する場合の対象範囲（第4部の候補一覧のうち、どこまで遡るか）
3. Code Lineage・Architecture Lineageを新たな別建て標準として正式制定するか、それとも既存のmocka_knowledge_lineage_standard_v1の拡張版として一体化するか
4. `app.py`等のコア資産への適用方式（コア改修を伴わない外部台帳方式を採用するかどうか）

---

## Knowledge Lineage

Document:
MOCKA_LINEAGE_GOVERNANCE_AUDIT_v1.md

Status:
Review

Created:
2026-06-24

Last Reviewed:
2026-06-24

Origin:
mocka_knowledge_lineage_standard_v1.md制定後、博士の指示によりMoCKA全体（文書・コード・アーキテクチャ）へのLineage適用可否を監査するために作成。

Parent Documents:

* mocka_knowledge_lineage_standard_v1.md

Derived From:
mocka_knowledge_lineage_standard_v1（Document Lineageの枠組みをCode/Architectureへ拡張する検討）

Supersedes:
（無し）

Reason For Creation:
文書だけでなく重要コード・サービス・アーキテクチャにも系譜情報を持たせるべきかどうかを、実リポジトリ調査に基づいて整理するため。

Affected Components:

* docs/spec
* docs/governance
* docs/audits
* app.py
* phi_os
* relay
* orchestra
* memory
* Event Integrity Framework
* Human Gate

Related Documents:

* MOCKA_CODE_BINDING_FINAL_REVIEW_v1.md
* MOCKA_CODE_BINDING_HUMAN_GATE_FINALIZATION_v1.md
* mocka_full_static_structure_map_v1.md

Revision History:

Revision:
R1

Date:
2026-06-24

Reason:
新規作成

Change:
初版作成（第1部〜第6部全体、実リポジトリ調査結果に基づく）

Impact:
Lineage Governance方針（適用範囲・遡及適用・新標準制定の有無）に関する博士裁定のための審査材料を提供。最終判定は含まない。実装・既存ファイル変更は無し。

# BINDING_REGISTRY_v1.md
## Repository全Artifact 制度登録台帳
**作成日:** 2026-06-16
**フェーズ:** MoCKA Phase 4 — Binding Layer制度監査
**状態:** DRAFT

---

## 凡例

| フィールド | 説明 |
|---|---|
| Meaning | 制度意味分類 |
| Institution | 所属制度機関 |
| Gate | 通過すべきGate候補 |
| Binding | CONNECTED / PARTIAL / SHADOW / ORPHAN / DEPRECATED / UNKNOWN |

---

## A. MoCKA メインリポジトリ (C:\Users\sirok\MoCKA\)

### A-1. コアシステム層

| # | Artifact | パス | 種別 | Meaning | Institution | Gate | Binding |
|---|---|---|---|---|---|---|---|
| A-001 | core_kernel/ | MoCKA/core_kernel/ | Dir/Py | SYSTEM_CORE | MoCKA | Module Gate | CONNECTED |
| A-002 | core_kernel/core_store/ | core_kernel/core_store/ | Dir/Py | SYSTEM_CORE | MoCKA | Module Gate | CONNECTED |
| A-003 | core_kernel/event_contracts/ | core_kernel/event_contracts/ | Dir/Py | SYSTEM_CORE | MoCKA | Event Gate | CONNECTED |
| A-004 | core_kernel/governance/ | core_kernel/governance/ | Dir/Py | GOVERNANCE | MoCKA | Module Gate | CONNECTED |
| A-005 | core_kernel/memory_core/ | core_kernel/memory_core/ | Dir/Py | SYSTEM_CORE | Memory | Knowledge Gate | CONNECTED |
| A-006 | core_kernel/orchestra/ | core_kernel/orchestra/ | Dir/Py | SYSTEM_CORE | Orchestra | Module Gate | CONNECTED |
| A-007 | core_kernel/orchestra_core/ | core_kernel/orchestra_core/ | Dir/Py | SYSTEM_CORE | Orchestra | Module Gate | PARTIAL |
| A-008 | core_kernel/phios_integration/ | core_kernel/phios_integration/ | Dir/Py | SYSTEM_CORE | PHI-OS | Module Gate | CONNECTED |
| A-009 | core_kernel/prism/ | core_kernel/prism/ | Dir/Py | SYSTEM_CORE | MoCKA | Module Gate | CONNECTED |
| A-010 | core_kernel/relay_core/ | core_kernel/relay_core/ | Dir/Py | SYSTEM_CORE | Relay | Module Gate | CONNECTED |
| A-011 | phi_os/ | MoCKA/phi_os/ | Dir/Py | SYSTEM_CORE | PHI-OS | Event Gate | CONNECTED |
| A-012 | phi_os/event_gate.py | phi_os/event_gate.py | Py | SYSTEM_CORE | PHI-OS | Event Gate | CONNECTED |
| A-013 | phi_os/gate_schema.py | phi_os/gate_schema.py | Py | DESIGN | PHI-OS | Event Gate | CONNECTED |
| A-014 | phi_os/gate_validator.py | phi_os/gate_validator.py | Py | SYSTEM_CORE | PHI-OS | Event Gate | CONNECTED |
| A-015 | memory/ | MoCKA/memory/ | Dir/Py | SYSTEM_CORE | Memory | Knowledge Gate | CONNECTED |
| A-016 | interface/ | MoCKA/interface/ | Dir/Py | SYSTEM_CORE | MoCKA | Module Gate | PARTIAL |
| A-017 | runtime/ | MoCKA/runtime/ | Dir/Py | SYSTEM_CORE | MoCKA | Module Gate | CONNECTED |
| A-018 | learning_kernel/ | MoCKA/learning_kernel/ | Dir/Py | SYSTEM_CORE | MoCKA | Knowledge Gate | PARTIAL |
| A-019 | semantic/ | MoCKA/semantic/ | Dir/Py | SYSTEM_CORE | MoCKA | Knowledge Gate | PARTIAL |
| A-020 | structural/ | MoCKA/structural/ | Dir/Py | SYSTEM_CORE | MoCKA | Module Gate | PARTIAL |
| A-021 | reality_sync/ | MoCKA/reality_sync/ | Dir/Py | SYSTEM_CORE | MoCKA | Module Gate | PARTIAL |
| A-022 | knowledge-gate/ | MoCKA/knowledge-gate/ | Dir | SYSTEM_CORE | PHI-OS | Knowledge Gate | PARTIAL |
| A-023 | mocka3/ | MoCKA/mocka3/ | Dir/Py | SYSTEM_CORE | MoCKA | Module Gate | PARTIAL |
| A-024 | schema/ | MoCKA/schema/ | Dir/Py | DESIGN | MoCKA | Module Gate | PARTIAL |
| A-025 | gateway/ | MoCKA/gateway/ | Dir | TOOL | MoCKA | Module Gate | PARTIAL |

### A-2. ガバナンス層

| # | Artifact | パス | 種別 | Meaning | Institution | Gate | Binding |
|---|---|---|---|---|---|---|---|
| A-100 | governance/ | MoCKA/governance/ | Dir | GOVERNANCE | MoCKA | Document Gate | CONNECTED |
| A-101 | governance/registry.json | governance/registry.json | JSON | GOVERNANCE | MoCKA | Document Gate | CONNECTED |
| A-102 | governance/approval_flow.json | governance/approval_flow.json | JSON | GOVERNANCE | MoCKA | Document Gate | CONNECTED |
| A-103 | governance/governance_event.json | governance/governance_event.json | JSON | GOVERNANCE | MoCKA | Event Gate | CONNECTED |
| A-104 | governance/file_protection_registry.json | governance/file_protection_registry.json | JSON | GOVERNANCE | MoCKA | Document Gate | CONNECTED |
| A-105 | governance/anchor_record.json | governance/anchor_record.json | JSON | GOVERNANCE | MoCKA | Document Gate | CONNECTED |
| A-106 | governance/keys/role_policy.json | governance/keys/role_policy.json | JSON | GOVERNANCE | MoCKA | Document Gate | CONNECTED |
| A-107 | governance/history/ | governance/history/ | Dir/MD | PHASE_RECORD | MoCKA | Document Gate | CONNECTED |
| A-108 | governance/spec/Decision_Record_Spec.md | governance/spec/Decision_Record_Spec.md | MD | DESIGN | MoCKA | Document Gate | CONNECTED |
| A-109 | governance/infield/docs/ | governance/infield/docs/ | Dir/MD | PHASE_RECORD | MoCKA | Document Gate | PARTIAL |
| A-110 | governance/_chaos_tmp/registry_tampered.json | governance/_chaos_tmp/registry_tampered.json | JSON | INCIDENT | MoCKA | Event Gate | SHADOW |
| A-111 | contracts/ | MoCKA/contracts/ | Dir | GOVERNANCE | MoCKA | Document Gate | PARTIAL |
| A-112 | authority/ | MoCKA/authority/ | Dir | GOVERNANCE | MoCKA | Document Gate | PARTIAL |
| A-113 | canon/ | MoCKA/canon/ | Dir | GOVERNANCE | MoCKA | Document Gate | PARTIAL |
| A-114 | mocka_governance/ | MoCKA/mocka_governance/ | Dir | GOVERNANCE | MoCKA | Document Gate | PARTIAL |
| A-115 | mocka-governance-kernel/ | MoCKA/mocka-governance-kernel/ | Dir | GOVERNANCE | MoCKA | Document Gate | PARTIAL |
| A-116 | self_audit/ | MoCKA/self_audit/ | Dir/Py | GOVERNANCE | MoCKA | Document Gate | PARTIAL |
| A-117 | cross_layer_consistency/ | MoCKA/cross_layer_consistency/ | Dir/Py | GOVERNANCE | MoCKA | Module Gate | PARTIAL |
| A-118 | report_truth_governance/ | MoCKA/report_truth_governance/ | Dir/Py | GOVERNANCE | MoCKA | Document Gate | PARTIAL |
| A-119 | production_certification/ | MoCKA/production_certification/ | Dir/Py | GOVERNANCE | MoCKA | Release Gate | PARTIAL |
| A-120 | immutable/ | C:\Users\sirok\immutable\ | Dir/Py | GOVERNANCE | MoCKA | Document Gate | ORPHAN |
| A-121 | keys/ | MoCKA/keys/ | Dir | GOVERNANCE | MoCKA | Document Gate | CONNECTED |
| A-122 | secrets/ | MoCKA/secrets/ | Dir | GOVERNANCE | MoCKA | Document Gate | CONNECTED |
| A-123 | phase3_key_policy/ | MoCKA/phase3_key_policy/ | Dir | GOVERNANCE | MoCKA | Document Gate | PARTIAL |

### A-3. ドキュメント層

| # | Artifact | パス | 種別 | Meaning | Institution | Gate | Binding |
|---|---|---|---|---|---|---|---|
| A-200 | docs/ | MoCKA/docs/ | Dir | mixed | MoCKA | Document Gate | CONNECTED |
| A-201 | docs/CONSTITUTION.md | docs/CONSTITUTION.md | MD | GOVERNANCE | MoCKA | Document Gate | CONNECTED |
| A-202 | docs/INSTITUTION_ARCHITECTURE.md | docs/INSTITUTION_ARCHITECTURE.md | MD | DESIGN | MoCKA | Document Gate | CONNECTED |
| A-203 | docs/governance/ | docs/governance/ | Dir/MD | GOVERNANCE | MoCKA | Document Gate | CONNECTED |
| A-204 | docs/architecture/ | docs/architecture/ | Dir/MD | DESIGN | MoCKA | Document Gate | CONNECTED |
| A-205 | docs/incidents/ | docs/incidents/ | Dir/MD | INCIDENT | MoCKA | Event Gate | CONNECTED |
| A-206 | docs/handoff/ | docs/handoff/ | Dir/MD | HANDOFF | MoCKA | Document Gate | CONNECTED |
| A-207 | docs/mocka3/ | docs/mocka3/ | Dir/MD | DESIGN | MoCKA | Module Gate | CONNECTED |
| A-208 | docs/caliber/ | docs/caliber/ | Dir/MD | DESIGN | MoCKA | Experiment Gate | PARTIAL |
| A-209 | docs/api/ | docs/api/ | Dir/MD | DESIGN | MoCKA | Module Gate | CONNECTED |
| A-210 | docs/lifecycle/ | docs/lifecycle/ | Dir/MD | DESIGN | MoCKA | Module Gate | PARTIAL |
| A-211 | docs/decisions/ | docs/decisions/ | Dir | GOVERNANCE | MoCKA | Document Gate | PARTIAL |
| A-212 | docs/RELEASE_NOTES.md | docs/RELEASE_NOTES.md | MD | RELEASE | MoCKA | Release Gate | CONNECTED |
| A-213 | docs/STRUCTURE.md | docs/STRUCTURE.md | MD | KNOWLEDGE | MoCKA | Document Gate | CONNECTED |
| A-214 | docs/MOCKA_ORIGIN.md | docs/MOCKA_ORIGIN.md | MD | KNOWLEDGE | MoCKA | Document Gate | CONNECTED |
| A-215 | docs/archive/ | docs/archive/ | Dir/MD | ARCHIVE | MoCKA | Document Gate | CONNECTED |
| A-216 | docs/INDEX.md | docs/INDEX.md | MD | KNOWLEDGE | MoCKA | Document Gate | CONNECTED |
| A-217 | docs/VERIFY.md | docs/VERIFY.md | MD | GOVERNANCE | MoCKA | Document Gate | PARTIAL |
| A-218 | docs/SECURITY.md | docs/SECURITY.md | MD | GOVERNANCE | MoCKA | Document Gate | CONNECTED |

### A-4. フェーズ記録層

| # | Artifact | パス | 種別 | Meaning | Institution | Gate | Binding |
|---|---|---|---|---|---|---|---|
| A-300 | records/ | MoCKA/records/ | Dir/MD | PHASE_RECORD | MoCKA | Document Gate | CONNECTED |
| A-301 | records/audit/ | records/audit/ | Dir | PHASE_RECORD | MoCKA | Document Gate | CONNECTED |
| A-302 | records/master/ | records/master/ | Dir | PHASE_RECORD | MoCKA | Document Gate | CONNECTED |
| A-303 | records/context/ | records/context/ | Dir | PHASE_RECORD | MoCKA | Document Gate | PARTIAL |
| A-304 | records/summary/ | records/summary/ | Dir | PHASE_RECORD | MoCKA | Document Gate | PARTIAL |
| A-305 | audit/ | MoCKA/audit/ | Dir | PHASE_RECORD | MoCKA | Document Gate | PARTIAL |
| A-306 | logs/ | MoCKA/logs/ | Dir | PHASE_RECORD | MoCKA | Event Gate | CONNECTED |
| A-307 | data/tic/ | MoCKA/data/tic/ | Dir | PHASE_RECORD | MoCKA | Document Gate | PARTIAL |
| A-308 | decision/ | MoCKA/decision/ | Dir/Py | GOVERNANCE | MoCKA | Document Gate | PARTIAL |
| A-309 | feedback/ | MoCKA/feedback/ | Dir/Py | KNOWLEDGE | MoCKA | Knowledge Gate | PARTIAL |

### A-5. 実験・研究層

| # | Artifact | パス | 種別 | Meaning | Institution | Gate | Binding |
|---|---|---|---|---|---|---|---|
| A-400 | experiments/ | MoCKA/experiments/ | Dir | EXPERIMENT | MoCKA | Experiment Gate | CONNECTED |
| A-401 | caliber/ | MoCKA/caliber/ | Dir/Py | EXPERIMENT | MoCKA | Experiment Gate | CONNECTED |
| A-402 | PlanningCaliber/ | MoCKA/PlanningCaliber/ | Dir | EXPERIMENT | MoCKA | Experiment Gate | PARTIAL |
| A-403 | PlanningCaliber/workshop/ | PlanningCaliber/workshop/ | Dir | EXPERIMENT | MoCKA | Experiment Gate | PARTIAL |
| A-404 | PlanningCaliber/workshop/vasAI_Project/ | workshop/vasAI_Project/ | Dir | EXPERIMENT | vasAI | Experiment Gate | ORPHAN |
| A-405 | PlanningCaliber/workshop/mini-mocka-series/ | workshop/mini-mocka-series/ | Dir | EXPERIMENT | mini-MoCKA | Experiment Gate | ORPHAN |
| A-406 | PlanningCaliber/workshop/Orchestra_Project/ | workshop/Orchestra_Project/ | Dir | EXPERIMENT | Orchestra | Experiment Gate | PARTIAL |
| A-407 | PlanningCaliber/workshop/Relay_Project/ | workshop/Relay_Project/ | Dir | EXPERIMENT | Relay | Experiment Gate | PARTIAL |
| A-408 | PlanningCaliber/workshop/phi-os/ | workshop/phi-os/ | Dir | EXPERIMENT | PHI-OS | Experiment Gate | PARTIAL |
| A-409 | PlanningCaliber/sirius-lab-products/ | PlanningCaliber/sirius-lab-products/ | Dir | DESIGN | MoCKA | Document Gate | PARTIAL |
| A-410 | PlanningCaliber/Experiment_v2.0/ | PlanningCaliber/Experiment_v2.0/ | Dir | EXPERIMENT | MoCKA | Experiment Gate | CONNECTED |
| A-411 | mocka_v3_eval/ | MoCKA/mocka_v3_eval/ | Dir | EXPERIMENT | MoCKA | Experiment Gate | PARTIAL |
| A-412 | research/ | MoCKA/research/ | Dir/Py | KNOWLEDGE | MoCKA | Knowledge Gate | PARTIAL |

### A-6. ツール・スクリプト層

| # | Artifact | パス | 種別 | Meaning | Institution | Gate | Binding |
|---|---|---|---|---|---|---|---|
| A-500 | scripts/ | MoCKA/scripts/ | Dir/Py | TOOL | MoCKA | Module Gate | CONNECTED |
| A-501 | tools/ | MoCKA/tools/ | Dir | TOOL | MoCKA | Module Gate | PARTIAL |
| A-502 | tools/mocka-extension/ | tools/mocka-extension/ | Dir/JS | TOOL | MoCKA | Module Gate | PARTIAL |
| A-503 | mocka-extension/ | MoCKA/mocka-extension/ | Dir | TOOL | MoCKA | Module Gate | SHADOW |
| A-504 | production_observability/ | MoCKA/production_observability/ | Dir/Py | TOOL | MoCKA | Module Gate | PARTIAL |
| A-505 | external/ | MoCKA/external/ | Dir | TOOL | MoCKA | Module Gate | PARTIAL |
| A-506 | external/chrome_bridge/ | external/chrome_bridge/ | Dir | TOOL | MoCKA | Module Gate | PARTIAL |
| A-507 | commercial_hardening/ | MoCKA/commercial_hardening/ | Dir/Py | DESIGN | MoCKA | Module Gate | PARTIAL |
| A-508 | deploy/ | MoCKA/deploy/ | Dir | RELEASE | MoCKA | Release Gate | PARTIAL |
| A-509 | network/ | MoCKA/network/ | Dir | TOOL | MoCKA | Module Gate | PARTIAL |
| A-510 | ops/ | C:\Users\sirok\ops\ | Dir | TOOL | MoCKA | Module Gate | ORPHAN |
| A-511 | shared/ | C:\Users\sirok\shared\ | Dir/JS | TOOL | 共通制度 | Module Gate | ORPHAN |
| A-512 | db/ | C:\Users\sirok\db\ | Dir/Py | TOOL | MoCKA | Module Gate | ORPHAN |
| A-513 | data/chrome_cdp_profile/ | MoCKA/data/chrome_cdp_profile/ | Dir | TOOL | MoCKA | Module Gate | SHADOW |
| A-514 | data/n8n/ | MoCKA/data/n8n/ | Dir | TOOL | MoCKA | Module Gate | SHADOW |

### A-7. データ・ストレージ層

| # | Artifact | パス | 種別 | Meaning | Institution | Gate | Binding |
|---|---|---|---|---|---|---|---|
| A-600 | data/ | MoCKA/data/ | Dir | mixed | MoCKA | — | PARTIAL |
| A-601 | data/mocka/ | data/mocka/ | Dir | PHASE_RECORD | MoCKA | Event Gate | PARTIAL |
| A-602 | data/runtime/ | data/runtime/ | Dir | PHASE_RECORD | MoCKA | Event Gate | PARTIAL |
| A-603 | data/governance/ | data/governance/ | Dir | GOVERNANCE | MoCKA | Document Gate | PARTIAL |
| A-604 | data/institution/ | data/institution/ | Dir | GOVERNANCE | MoCKA | Document Gate | PARTIAL |
| A-605 | data/experiments/ | data/experiments/ | Dir | EXPERIMENT | MoCKA | Experiment Gate | PARTIAL |
| A-606 | data/storage/ | data/storage/ | Dir | PHASE_RECORD | MoCKA | Event Gate | CONNECTED |
| A-607 | data/storage/infield/ | data/storage/infield/ | Dir | PHASE_RECORD | MoCKA | Event Gate | CONNECTED |
| A-608 | data/storage/outfield/ | data/storage/outfield/ | Dir | PHASE_RECORD | MoCKA | Event Gate | CONNECTED |
| A-609 | data/storage/incident/ | data/storage/インシデント/ | Dir | INCIDENT | MoCKA | Event Gate | CONNECTED |
| A-610 | data/storage/公文書/ | data/storage/公文書/ | Dir | GOVERNANCE | MoCKA | Document Gate | CONNECTED |
| A-611 | data/simulation/ | data/simulation/ | Dir | EXPERIMENT | MoCKA | Experiment Gate | PARTIAL |
| A-612 | data/pending_reviews/ | data/pending_reviews/ | Dir | GOVERNANCE | MoCKA | Document Gate | PARTIAL |
| A-613 | data/watcher_queue/ | data/watcher_queue/ | Dir | TOOL | MoCKA | Event Gate | PARTIAL |
| A-614 | data/ise/ | data/ise/ | Dir | UNKNOWN | MoCKA | — | UNKNOWN |
| A-615 | data/archive/ | data/archive/ | Dir | ARCHIVE | MoCKA | — | CONNECTED |
| A-616 | data/ (sirok root) | C:\Users\sirok\data\ | Dir | TOOL | MoCKA | — | ORPHAN |
| A-617 | runtime/ (sirok root) | C:\Users\sirok\runtime\ | Dir | UNKNOWN | — | — | ORPHAN |
| A-618 | schemas/ (sirok root) | C:\Users\sirok\schemas\ | Dir | UNKNOWN | — | — | ORPHAN |

### A-8. Archive・Shadow層

| # | Artifact | パス | 種別 | Meaning | Institution | Gate | Binding |
|---|---|---|---|---|---|---|---|
| A-700 | archive/ | MoCKA/archive/ | Dir | ARCHIVE | MoCKA | — | CONNECTED |
| A-701 | archive/legacy/ | archive/legacy/ | Dir | ARCHIVE | MoCKA | — | CONNECTED |
| A-702 | archive/ledger_old/ | archive/ledger_old/ | Dir | ARCHIVE | MoCKA | — | DEPRECATED |
| A-703 | archive/_untracked_stash_20260226_170942/ | archive/_untracked_stash_*/ | Dir | ARCHIVE | MoCKA | — | SHADOW |
| A-704 | archive/_untracked_stash_verify_pack_v3/ | archive/_untracked_stash_verify_pack_v3/ | Dir | ARCHIVE | MoCKA | — | SHADOW |
| A-705 | backup/ | MoCKA/backup/ | Dir | ARCHIVE | MoCKA | — | SHADOW |
| A-706 | OLD_FILES/ | MoCKA/OLD_FILES/ | Dir | ARCHIVE | MoCKA | — | SHADOW |
| A-707 | mocka_3/ | MoCKA/mocka_3/ | Dir/Py | ARCHIVE | MoCKA | — | DEPRECATED |
| A-708 | runtime_b/ | MoCKA/runtime_b/ | Dir | ARCHIVE | MoCKA | — | SHADOW |
| A-709 | outbox/ | MoCKA/outbox/ | Dir | RELEASE | MoCKA | Release Gate | PARTIAL |
| A-710 | outbox/verify_pack/ | outbox/verify_pack/ | Dir | RELEASE | MoCKA | Release Gate | CONNECTED |
| A-711 | outbox/ (sirok root) | C:\Users\sirok\outbox\ | Dir/JSON | RELEASE | MoCKA | Release Gate | ORPHAN |
| A-712 | verify/ | MoCKA/verify/ | Dir | TEST | MoCKA | Release Gate | PARTIAL |
| A-713 | reproduce_output/ | MoCKA/reproduce_output/ | Dir | TEST | MoCKA | Release Gate | SHADOW |

### A-9. 製品・デザイン層

| # | Artifact | パス | 種別 | Meaning | Institution | Gate | Binding |
|---|---|---|---|---|---|---|---|
| A-800 | sirius-lab/ | MoCKA/sirius-lab/ | Dir | DESIGN | MoCKA | Release Gate | PARTIAL |
| A-801 | templates/ | MoCKA/templates/ | Dir | DESIGN | MoCKA | Document Gate | PARTIAL |
| A-802 | schemas/ | MoCKA/schemas/ | Dir | DESIGN | MoCKA | Module Gate | PARTIAL |
| A-803 | transparency/ | MoCKA/transparency/ | Dir | GOVERNANCE | MoCKA | Document Gate | CONNECTED |
| A-804 | PlanningCaliber/web/ | PlanningCaliber/web/ | Dir | DESIGN | MoCKA | Release Gate | PARTIAL |
| A-805 | docs/ (sirok root) | C:\Users\sirok\docs\ | Dir/SVG/MD | DESIGN | MoCKA | Document Gate | ORPHAN |

### A-10. 制度・設定ファイル

| # | Artifact | パス | 種別 | Meaning | Institution | Gate | Binding |
|---|---|---|---|---|---|---|---|
| A-900 | .claude/CLAUDE.md | MoCKA/.claude/CLAUDE.md | MD | GOVERNANCE | MoCKA | Document Gate | CONNECTED |
| A-901 | .claude/mocka_config.json | MoCKA/.claude/mocka_config.json | JSON | GOVERNANCE | MoCKA | Document Gate | CONNECTED |
| A-902 | .github/workflows/ | MoCKA/.github/workflows/ | Dir/YAML | TOOL | MoCKA | Release Gate | PARTIAL |
| A-903 | mocka-docs/operations/ | mocka-docs/operations/ | Dir/MD | REQUIREMENT | MoCKA | Document Gate | CONNECTED |
| A-904 | mocka-docs/architecture/ | mocka-docs/architecture/ | Dir/MD | DESIGN | MoCKA | Document Gate | CONNECTED |
| A-905 | mocka-docs/incidents/ | mocka-docs/incidents/ | Dir/MD | INCIDENT | MoCKA | Event Gate | CONNECTED |
| A-906 | core/ (sirok root) | C:\Users\sirok\core\ | Dir | SHADOW | — | — | SHADOW |
| A-907 | audit/ (sirok root) | C:\Users\sirok\audit\ | Dir/TSV | PHASE_RECORD | MoCKA | Document Gate | ORPHAN |
| A-908 | inventory/ (sirok root) | C:\Users\sirok\inventory\ | Dir/TXT | PHASE_RECORD | MoCKA | Document Gate | ORPHAN |

---

## B. 外部リポジトリ群 (C:\Users\sirok\mocka-*/他)

| # | Artifact | パス | 種別 | Meaning | Institution | Gate | Binding |
|---|---|---|---|---|---|---|---|
| B-001 | mocka-archive/ | C:\Users\sirok\mocka-archive\ | Repo | ARCHIVE | MoCKA | — | CONNECTED |
| B-002 | mocka-civilization/ | C:\Users\sirok\mocka-civilization\ | Repo | KNOWLEDGE | MoCKA/共通制度 | Document Gate | CONNECTED |
| B-003 | mocka-civilization/blueprint/ | mocka-civilization/blueprint/ | Dir/MD | DESIGN | MoCKA/共通制度 | Document Gate | CONNECTED |
| B-004 | mocka-civilization/phase9〜29/ | mocka-civilization/phase*/ | Dir/MD | PHASE_RECORD | MoCKA | Document Gate | CONNECTED |
| B-005 | mocka-civilization/genesis/ | mocka-civilization/genesis/ | Dir/MD | DESIGN | 共通制度 | Document Gate | CONNECTED |
| B-006 | mocka-civilization/lineage-registry/ | mocka-civilization/lineage-registry/ | Dir/MD | GOVERNANCE | MoCKA | Document Gate | PARTIAL |
| B-007 | mocka-civilization/derived-civilizations/ | mocka-civilization/derived-civilizations/ | Dir/MD | PHASE_RECORD | MoCKA | Document Gate | CONNECTED |
| B-008 | mocka-core-private/ | C:\Users\sirok\mocka-core-private\ | Repo | SYSTEM_CORE | MoCKA | Module Gate | PARTIAL |
| B-009 | mocka-docs/ | C:\Users\sirok\mocka-docs\ | Repo | REQUIREMENT | MoCKA | Document Gate | CONNECTED |
| B-010 | mocka-external-brain/ | C:\Users\sirok\mocka-external-brain\ | Repo | KNOWLEDGE | MoCKA | Knowledge Gate | PARTIAL |
| B-011 | mocka-infield/ | C:\Users\sirok\mocka-infield\ | Repo | PHASE_RECORD | MoCKA | Event Gate | ORPHAN |
| B-012 | mocka-joints/ | C:\Users\sirok\mocka-joints\ | Repo | SYSTEM_CORE | MoCKA | Module Gate | PARTIAL |
| B-013 | mocka-knowledge-gate/ | C:\Users\sirok\mocka-knowledge-gate\ | Repo | SYSTEM_CORE | PHI-OS | Knowledge Gate | CONNECTED |
| B-014 | mocka-outfield/ | C:\Users\sirok\mocka-outfield\ | Repo | HANDOFF | MoCKA | Document Gate | PARTIAL |
| B-015 | mocka-public/ | C:\Users\sirok\mocka-public\ | Repo | RELEASE | 共通制度 | Release Gate | CONNECTED |
| B-016 | mocka-public/docs/ | mocka-public/docs/ | Dir/MD | KNOWLEDGE | 共通制度 | Document Gate | CONNECTED |
| B-017 | mocka-public/keys/public.key | mocka-public/keys/public.key | Key | GOVERNANCE | 共通制度 | Document Gate | CONNECTED |
| B-018 | mocka-runtime/ | C:\Users\sirok\mocka-runtime\ | Repo | PHASE_RECORD | MoCKA | Event Gate | PARTIAL |
| B-019 | mocka-transparency/ | C:\Users\sirok\mocka-transparency\ | Repo | GOVERNANCE | MoCKA/共通制度 | Document Gate | CONNECTED |
| B-020 | Relay_Project/ | C:\Users\sirok\Relay_Project\ | Dir | SYSTEM_CORE | Relay | Module Gate | ORPHAN |
| B-021 | m-sirius-k/ | C:\Users\sirok\m-sirius-k\ | Dir | DESIGN | MoCKA | Release Gate | PARTIAL |

---

## C. 制度除外対象

以下はシステムファイルまたはツールchain由来のため制度対象外とする。

| Artifact | 理由 |
|---|---|
| .venv/, venv/ | Python仮想環境 — 制度対象外 |
| .wsl_ots_venv/ | WSL仮想環境 — 制度対象外 |
| __pycache__/, .pytest_cache/ | ビルド生成物 — 制度対象外 |
| .pyc ファイル | コンパイル済みバイナリ — 制度対象外 |
| node_modules/ | npm依存 — 制度対象外 |
| dist/ | ビルド成果物 — 条件付き(Release Gate経由で制度接続可) |
| data/chrome_cdp_profile/ | Chromeプロファイルデータ — SHADOW |
| data/n8n/ | n8nワークフローデータ — TOOL(SHADOW) |

---

*総登録Artifact数: 116件（グループ単位）*
*最終更新: 2026-06-16*

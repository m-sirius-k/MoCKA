# IMPLEMENTATION_PRIORITY_v1.md
## 制度修復優先順位
**作成日:** 2026-06-16
**フェーズ:** MoCKA Phase 4 — Binding Layer制度監査
**状態:** DRAFT v1

---

## 優先度定義

| 優先度 | 定義 | 対処目標 |
|---|---|---|
| **Critical** | 制度の整合性・信頼性・セキュリティに即時影響を与えるGap | Phase 4完了前に対処 |
| **High** | 主要Institution・GateのBinding未完了。制度運用に実質的障害をきたしている | Phase 5移行前に対処 |
| **Medium** | Partial/Versionn分岐状態。現在は機能するが制度的曖昧性がある | Phase 5内で対処 |
| **Low** | ORPHAN/SHADOW領域。現在の制度運用に影響しない | 計画的に対処 |

---

## Critical (即時対処)

### C-001: governance/_chaos_tmp/ のSHADOW解除
- **Gap ID:** GAP-S01
- **対象:** `MoCKA/governance/_chaos_tmp/registry_tampered.json`
- **リスク:** 改竄済みレジストリデータがガバナンス領域のShadow内に存在。制度上の権威ある registry.json と混同リスク。
- **修復:** INCIDENT Meaning付与 → Event Gate経由で制度記録 → governance/以外の場所へ隔離Binding
- **実施条件:** 次の制度実装セッション開始前

---

### C-002: PHI-OS Gate権威の一元化
- **Gap ID:** GAP-V02
- **対象:** `MoCKA/phi_os/`, `MoCKA/knowledge-gate/`, `C:\Users\sirok\mocka-knowledge-gate\`
- **リスク:** PHI-OS Gate実装が3箇所に分散。Event Gate・Knowledge Gateの権威定義が不一致の場合、制度全体のGate通過判定が崩壊する。
- **修復:** `phi_os/` をGate定義の権威に確定 → `knowledge-gate/` と `mocka-knowledge-gate/` はGate実装版としてModule Gate登録
- **実施条件:** PHI-OS Constitution起草前

---

### C-003: orchestra/ vs orchestra_core/ Version統合
- **Gap ID:** GAP-V01
- **対象:** `MoCKA/core_kernel/orchestra/` と `MoCKA/core_kernel/orchestra_core/`
- **リスク:** Orchestra制度の主実装が2系統。Event Busが複数存在する場合、イベントの制度的一意性が保証されない。
- **修復:** `orchestra/` を主実装に確定 → `orchestra_core/` をLegacy Adapter化またはARCHIVE化 → Deprecation Record作成
- **実施条件:** Orchestra Protocol起草前

---

### C-004: verify_pack Versionの制度的確定
- **Gap ID:** GAP-V05
- **対象:** `MoCKA/archive/_untracked_stash_verify_pack_v3/` と `MoCKA/verify/verify_pack_v4_sample/`
- **リスク:** Verify Packの現行版が不明。v3がARCHIVE内にShadow存在し、v4との並立が制度的検証の信頼性を損なう。
- **修復:** v4を正規版としてRelease Gate登録 → v3をDEPRECATED化 → DEPRECATED Record作成
- **実施条件:** Release Gate実装前

---

## High (Phase 5移行前に対処)

### H-001: runtime/ の制度主体確定
- **Gap ID:** GAP-V04
- **対象:** `MoCKA/runtime/`, `C:\Users\sirok\mocka-runtime\`, `C:\Users\sirok\runtime\`
- **リスク:** runtime概念が3箇所に分散。制度上のruntime主体が不明では、システム状態の制度的保証ができない。
- **修復:** `MoCKA/runtime/` を主runtime → `mocka-runtime/` をPHASE_RECORD(読み取り専用) → `sirok/runtime/` をORPHAN確定またはARCHIVE化
- **修復タイプ:** Institution変更 + Version統合 + Binding追加

---

### H-002: Relay_Project/ (sirok root) のOrphan解除
- **Gap ID:** GAP-O02
- **対象:** `C:\Users\sirok\Relay_Project\`
- **リスク:** Relay制度実装とは別にホームルートにRelay Projectが孤立。Relay Institutionの境界が不明確。
- **修復:** `core_kernel/relay_core/` との関係確認 → Relay Institution所属を正式登録 → Binding追加またはEXPERIMENT化
- **修復タイプ:** Institution変更 + Binding追加

---

### H-003: vasAI / mini-MoCKA Institution正式化
- **Gap ID:** GAP-O14, GAP-O15, GAP-I04 (類似)
- **対象:** `PlanningCaliber/workshop/vasAI_Project/`, `PlanningCaliber/workshop/mini-mocka-series/`
- **リスク:** 実験が進行しているにも関わらずInstitution未定義。Experiment Gate通過の前提条件が満たされていない。
- **修復:** vasAI / mini-MoCKA をMoCKA配下のサブInstitutionとして正式登録 → Experiment Gate登録
- **修復タイプ:** Institution変更 + Gate登録

---

### H-004: docs/ の権威一元化
- **Gap ID:** GAP-V06
- **対象:** `MoCKA/docs/`, `mocka-public/docs/`, `C:\Users\sirok\docs\`
- **リスク:** 公式ドキュメントがどれか不明。外部参照者が誤った文書を参照するリスク。
- **修復:** `MoCKA/docs/` を主権威 → `mocka-public/docs/` を公開版(Release Gate) → `sirok/docs/` をDESIGN/PARTIAL
- **修復タイプ:** Meaning変更 + Binding追加

---

### H-005: mocka-infield/ の制度的内容充填またはArchive化
- **Gap ID:** GAP-O01, GAP-G06
- **対象:** `C:\Users\sirok\mocka-infield\`
- **リスク:** infield領域リポジトリが実質空。Institutionがinfieldへの書き込みを行う際の制度的受け皿がない。
- **修復:** Event Gate登録 → MoCKA/data/storage/infield/ とのBinding確立 または Archive化を明示
- **修復タイプ:** Binding追加 + Gate登録

---

### H-006: production_certification/ のRelease Gate登録
- **Gap ID:** GAP-G03
- **対象:** `MoCKA/production_certification/`
- **リスク:** 本番認定機能がRelease Gateと未接続。認定済みのはずのモジュールが制度上未認定の状態で存在するリスク。
- **修復:** Release Gate登録 → production_certification/ をRelease Gate Handlerとして正式化
- **修復タイプ:** Gate登録 + Binding追加

---

## Medium (Phase 5内で対処)

| ID | 対象 | Gap | 修復方針 |
|---|---|---|---|
| M-001 | mocka-extension/ (2箇所) | GAP-V03 | tools/mocka-extension/ を正規化。MoCKA/mocka-extension/ をARCHIVE化 |
| M-002 | archive/_untracked_stash_20260226_170942/ | GAP-S03 | ARCHIVE Binding追加。stash内個別監査を計画 |
| M-003 | backup/ | GAP-S05 | ARCHIVE Meaning付与 + 自動/手動の目的を制度上明示 |
| M-004 | OLD_FILES/ | GAP-S06 | DEPRECATED化またはARCHIVE化を制度上確定 |
| M-005 | runtime_b/ | GAP-S07 | 用途確定 → EXPERIMENT化またはDEPRECATED化 |
| M-006 | learning_kernel/ | GAP-G01 | Knowledge Gate登録 |
| M-007 | semantic/ | GAP-G02 | Knowledge Gate登録 |
| M-008 | cross_layer_consistency/ | GAP-G07 | Module Gate登録 |
| M-009 | mocka-core-private/ | B-008 PARTIAL | Module Gate登録完了。private境界の制度的定義を明示 |
| M-010 | mocka-joints/ | B-012 PARTIAL | 内容精査しModule Gate登録。joints の制度的役割を定義 |
| M-011 | mocka-outfield/ | B-014 PARTIAL | HANDOFF Meaning確定 + Document Gate登録 |
| M-012 | PlanningCaliber/ 全体 | GAP-I03 | PlanningCaliberをMoCKA Experiment配下サブ機関として登録 |
| M-013 | deploy/ | GAP-G05 | Release Gate登録 |
| M-014 | gateway/ | A-025 PARTIAL | Module Gate登録。外部ゲートウェイの制度的境界を定義 |
| M-015 | data/ise/ | GAP-G06 (A-614 UNKNOWN) | Meaning確定 → Gate登録 |
| M-016 | mocka_governance/ vs mocka-governance-kernel/ | 並立 | Version統合またはMeaning分化 |

---

## Low (計画的に対処)

| ID | 対象 | Gap | 修復方針 |
|---|---|---|---|
| L-001 | ops/ (sirok root) | GAP-O04 | MoCKA TOOL Binding追加 |
| L-002 | shared/ (sirok root) | GAP-O05 | 共通制度 TOOL Binding追加 |
| L-003 | db/ (sirok root) | GAP-O06 | MoCKA TOOL Binding追加 |
| L-004 | outbox/ (sirok root) | GAP-O07 | MoCKA outbox Binding追加またはRELEASE化 |
| L-005 | audit/ (sirok root) | GAP-O08 | PHASE_RECORD Binding追加 |
| L-006 | inventory/ (sirok root) | GAP-O09 | PHASE_RECORD Binding追加 |
| L-007 | data/ (sirok root) | GAP-O10 | MoCKA/data/ Binding追加 |
| L-008 | docs/ (sirok root) | GAP-O11 | DESIGN Binding追加 |
| L-009 | runtime/ (sirok root) | GAP-O12 | UNKNOWN → ARCHIVE化（空ディレクトリ） |
| L-010 | schemas/ (sirok root) | GAP-O13 | UNKNOWN → ARCHIVE化（空ディレクトリ） |
| L-011 | immutable/ | GAP-O03 | GOVERNANCE Binding追加 |
| L-012 | core/ (sirok root) | GAP-S10 | 内容確認後Meaning確定 |
| L-013 | data/chrome_cdp_profile/ | GAP-S08 | TOOL Shadow区画として管理 |
| L-014 | data/n8n/ | GAP-S09 | TOOL Shadow区画として管理 |
| L-015 | archive/ledger_old/ | GAP-D02 | DEPRECATED確定 + ARCHIVE化 |
| L-016 | mocka_3/ | GAP-D01 | Deprecation Record作成 |
| L-017 | governance/_chaos_tmp/ (→ Criticalで処理後) | — | Critical処理後に残余のSHADOW管理 |
| L-018 | mocka-external-brain/ | GAP-I01 | Memory Institution所属明示 |
| L-019 | mocka-civilization/ 主Institution確定 | GAP-I02 | 共通制度を主Institutionとして確定 |
| L-020 | reproduce_output/ | GAP-S11 | TEST Meaning付与 + Release Gate Binding |

---

## 優先度別件数

| 優先度 | 件数 |
|---|---|
| Critical | 4 |
| High | 6 |
| Medium | 16 |
| Low | 20 |
| **合計** | **46** |

---

## 実施順序 (推奨シーケンス)

```
Phase 4 Binding Layer 完了前:
  → C-001: governance/_chaos_tmp/ 解除
  → C-002: PHI-OS Gate権威確定
  → C-003: orchestra/ Version統合
  → C-004: verify_pack Version確定

PHI-OS Constitution起草前:
  → H-001: runtime/ 主体確定
  → H-002: Relay_Project/ 整理
  → H-006: production_certification/ Release Gate登録

Institution Protocol策定時:
  → H-003: vasAI / mini-MoCKA 正式化
  → H-004: docs/ 権威一元化
  → H-005: mocka-infield/ 整理

Gate Architecture実装時:
  → Medium 全件 (M-001〜M-016)

継続的メンテナンス:
  → Low 全件 (L-001〜L-020)
```

---

*最終更新: 2026-06-16*

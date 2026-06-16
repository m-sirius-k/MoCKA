# MEANING_AUTHORITY_v1.md
## 制度意味辞書 (Meaning Authority)
**作成日:** 2026-06-16
**フェーズ:** MoCKA Phase 4 — Binding Layer制度監査
**状態:** DRAFT v1

---

## 概要

本文書は、Repository内すべてのArtifactに付与される「制度意味（Meaning）」の正典定義である。
Meaningは制度接続の出発点であり、ArtifactがいかなるInstitution・Gateへ属すべきかを決定する。

---

## Meaning一覧

### 1. SYSTEM_CORE

| 項目 | 内容 |
|---|---|
| **定義** | システムの実行・制御・状態管理を担う中核コンポーネント |
| **用途** | ランタイム、カーネル、エンジン、統合アダプター、Gate実装体 |
| **適用条件** | Pythonモジュールとして実行可能かつ制度機能を直接実装しているArtifact |
| **典型例** | core_kernel/, phi_os/, memory/, runtime/, orchestra/, relay_core/ |
| **Gate優先** | Module Gate → Event Gate |
| **Institution優先** | MoCKA, PHI-OS, Orchestra, Relay, Memory |
| **注意** | 実装を持たない設定ファイルや仕様書はSYSTEM_COREではなくDESIGNまたはGOVERNANCE |

---

### 2. PHASE_RECORD

| 項目 | 内容 |
|---|---|
| **定義** | システム進化の履歴・フェーズ遷移の証跡を記録するArtifact |
| **用途** | フェーズログ、決定記録、セッション記録、タイムライン |
| **適用条件** | 特定フェーズ・時点の状態を記録しており、変更が凍結されているかそれに準じる |
| **典型例** | records/, governance/history/, mocka-civilization/phase*/, logs/ |
| **Gate優先** | Document Gate → Event Gate |
| **Institution優先** | MoCKA, 共通制度 |
| **注意** | 進行中の記録はPHASE_RECORDではなくGOVERNANCEまたはPHASE_RECORD(PARTIAL) |

---

### 3. INCIDENT

| 項目 | 内容 |
|---|---|
| **定義** | 制度上の異常事象・障害・セキュリティ事案の記録 |
| **用途** | インシデントレポート、障害ログ、異常検知記録 |
| **適用条件** | 制度上の逸脱・障害を記録しており、事後検証可能な形式を持つ |
| **典型例** | docs/incidents/INC-*.md, data/storage/インシデント/, governance/_chaos_tmp/ |
| **Gate優先** | Event Gate |
| **Institution優先** | MoCKA |
| **注意** | 意図的なChaos実験記録はINCIDENTではなくEXPERIMENTが優先 |

---

### 4. EXPERIMENT

| 項目 | 内容 |
|---|---|
| **定義** | 新機能・仮説の試験的実装・評価を目的とするArtifact |
| **用途** | プロトタイプ、PoC、評価スクリプト、実験データ |
| **適用条件** | 本番制度に接続されておらず、試験的性格が明示されているか文脈から明らか |
| **典型例** | experiments/, caliber/, PlanningCaliber/Experiment_v2.0/, mocka_v3_eval/ |
| **Gate優先** | Experiment Gate |
| **Institution優先** | MoCKA（実験先Institutionが明確な場合はその Institution） |
| **注意** | 試験が完了し本番採用された場合はSYSTEM_COREまたはDESIGNへMeaning変更 |

---

### 5. ARCHIVE

| 項目 | 内容 |
|---|---|
| **定義** | 役割を終え、将来的な参照のみを目的として保存されるArtifact |
| **用途** | 旧バージョン、過去の設計物、Stash、廃止されたモジュール |
| **適用条件** | 現在の実行・意思決定に直接関与しないが削除すると制度上の記録が失われる |
| **典型例** | archive/, backup/, OLD_FILES/, mocka_3/, docs/archive/ |
| **Gate優先** | なし（参照時のみDocument Gate） |
| **Institution優先** | MoCKA（記録保全） |
| **注意** | ARCHIVEとSHADOWの区別：Archive化が意図的ならARCHIVE、不明ならSHADOW |

---

### 6. DESIGN

| 項目 | 内容 |
|---|---|
| **定義** | 制度・システムの構造・仕様・設計方針を記述するArtifact |
| **用途** | アーキテクチャ文書、スキーマ定義、モジュール仕様、UI/製品設計 |
| **適用条件** | 実装の指針となる文書または設計データであり、実装を直接含まない |
| **典型例** | docs/architecture/, docs/mocka3/, schemas/, templates/, phi_os/gate_schema.py |
| **Gate優先** | Document Gate → Module Gate |
| **Institution優先** | MoCKA, PHI-OS |
| **注意** | 実装を含む場合はSYSTEM_COREと併記せず、主機能に基づき単一Meaningを付与 |

---

### 7. REQUIREMENT

| 項目 | 内容 |
|---|---|
| **定義** | 制度・システムに課せられた要件・制約・仕様の記述 |
| **用途** | API仕様、運用プロトコル、SLA定義、制約文書 |
| **適用条件** | 実装が従うべき外部規約または内部規約として機能するArtifact |
| **典型例** | mocka-docs/operations/, docs/governance/MODULE_*.md |
| **Gate優先** | Document Gate |
| **Institution優先** | MoCKA |

---

### 8. GOVERNANCE

| 項目 | 内容 |
|---|---|
| **定義** | 制度の管理・認証・監査・ポリシー・承認を担うArtifact |
| **用途** | レジストリ、承認フロー、ガバナンスルール、憲法、Charter、キーポリシー |
| **適用条件** | 制度の意思決定プロセスまたは制度権限の根拠として機能するArtifact |
| **典型例** | governance/registry.json, docs/CONSTITUTION.md, docs/governance/, keys/, production_certification/ |
| **Gate優先** | Document Gate |
| **Institution優先** | MoCKA |
| **注意** | ガバナンス実装コード（engines/）はSYSTEM_COREとGOVERNANCEの境界にあるが、制度機能が主であればGOVERNANCE |

---

### 9. HANDOFF

| 項目 | 内容 |
|---|---|
| **定義** | セッション間・エージェント間での状態引き継ぎを目的とするArtifact |
| **用途** | 引き継ぎ文書、HANDOFFパック、セッション要約 |
| **適用条件** | 受け取り手（次のセッション・エージェント）を想定した形式で記述されている |
| **典型例** | docs/handoff/, mocka-outfield/ |
| **Gate優先** | Document Gate |
| **Institution優先** | MoCKA |

---

### 10. KNOWLEDGE

| 項目 | 内容 |
|---|---|
| **定義** | 将来の判断・設計・実装の参照資産として機能するArtifact |
| **用途** | 研究記録、外部脳、学習データ、ホワイトペーパー、技術ノート |
| **適用条件** | 直接的な実装・ガバナンス機能を持たないが、制度知識として保全価値がある |
| **典型例** | mocka-external-brain/, research/, mocka-public/docs/, mocka-civilization/WHITEPAPER_v0.1.md |
| **Gate優先** | Knowledge Gate |
| **Institution優先** | MoCKA, 共通制度 |

---

### 11. RELEASE

| 項目 | 内容 |
|---|---|
| **定義** | 外部公開・配布・バージョンアップを目的とするArtifact |
| **用途** | Verify Pack、Outbox、リリースノート、公開鍵、配布物 |
| **適用条件** | 外部（他エージェント・公開リポジトリ・受取人）へ渡ることを意図している |
| **典型例** | outbox/, mocka-public/, docs/RELEASE_NOTES.md, deploy/, verify/ |
| **Gate優先** | Release Gate |
| **Institution優先** | MoCKA, 共通制度 |

---

### 12. TEST

| 項目 | 内容 |
|---|---|
| **定義** | 制度・実装の正当性検証を目的とするArtifact |
| **用途** | ユニットテスト、統合テスト、検証スクリプト、Verify Pack |
| **適用条件** | テスト実行を目的としており、本番ロジックを直接含まない |
| **典型例** | */tests/, verify/, reproduce_output/, caliber/verify/ |
| **Gate優先** | Release Gate → Module Gate |
| **Institution優先** | MoCKA |

---

### 13. TOOL

| 項目 | 内容 |
|---|---|
| **定義** | 制度運営を支援する補助的スクリプト・ユーティリティ・インフラ |
| **用途** | 管理スクリプト、CI/CD設定、外部連携ツール、データ処理スクリプト |
| **適用条件** | 制度機能を直接実装せず、制度運営を外から支援する立場にある |
| **典型例** | scripts/, tools/, ops/, shared/, .github/workflows/, gateway/ |
| **Gate優先** | Module Gate |
| **Institution優先** | MoCKA, 共通制度 |

---

### 14. UNCLASSIFIED

| 項目 | 内容 |
|---|---|
| **定義** | 制度意味が特定できていないArtifact |
| **用途** | 調査待ち、目的不明、参照なし |
| **適用条件** | 上記13分類のいずれにも明確に該当しない |
| **典型例** | data/ise/, C:\Users\sirok\runtime\, C:\Users\sirok\schemas\ |
| **Gate優先** | なし |
| **Institution優先** | 未定 |
| **アクション** | 次フェーズでのMeaning確定が必須 |

---

## Meaning優先順位ルール

複数のMeaningが競合する場合、以下の優先順位に従う。

1. INCIDENT（最優先 — 異常事象は必ず記録）
2. SYSTEM_CORE（制度の実行基盤）
3. GOVERNANCE（制度の権威基盤）
4. RELEASE（外部公開済み）
5. PHASE_RECORD（変更凍結済み）
6. HANDOFF（引き継ぎ済み）
7. REQUIREMENT（要件確定済み）
8. DESIGN（設計中）
9. KNOWLEDGE（参照資産）
10. EXPERIMENT（試験中）
11. TEST（検証専用）
12. TOOL（補助）
13. ARCHIVE（保全のみ）
14. UNCLASSIFIED（最低優先）

---

## Meaning変更プロトコル

Meaningの変更は以下のConditionを満たす場合にのみ許可される。

| 変更パターン | 条件 |
|---|---|
| EXPERIMENT → SYSTEM_CORE | 本番採用Decision記録が存在する |
| DESIGN → REQUIREMENT | 承認済みGovernance Recordが存在する |
| SYSTEM_CORE → ARCHIVE | Deprecation Recordが存在し、後継実装が確認済み |
| UNCLASSIFIED → any | Meaning確定Auditが実施され記録された |
| any → INCIDENT | 異常検知時は即時・承認不要 |

---

*Meaning定義数: 14*
*最終更新: 2026-06-16*

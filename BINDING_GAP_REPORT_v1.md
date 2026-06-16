# BINDING_GAP_REPORT_v1.md
## 制度未接続一覧 (Binding Gap Report)
**作成日:** 2026-06-16
**フェーズ:** MoCKA Phase 4 — Binding Layer制度監査
**状態:** DRAFT v1

---

## 概要

本報告書は、Repositoryにおいて制度未接続（SHADOW / ORPHAN / DEPRECATED / PARTIAL / UNKNOWN / VERSION CONFLICT）の状態にあるArtifactを一覧化し、制度リスクを明示する。

削除提案は含まない。すべての項目に制度的修復提案を付与する。

---

## 1. SHADOW (制度上の存在が未確認)

Shadowとは、物理的に存在するが制度上の意図が不明瞭、または意図的に制度から切り離されたArtifact。

| ID | Artifact | パス | 制度リスク | 修復提案 |
|---|---|---|---|---|
| GAP-S01 | governance/_chaos_tmp/ | MoCKA/governance/_chaos_tmp/ | INCIDENT記録が制度登録なしにShadow存在。改竄テストデータが制度外に漏存。 | INCIDENT Meaningを付与し、Event Gate経由で制度記録。_chaos_tmp → incidents/CHAOS_TEST/ へBinding追加 |
| GAP-S02 | mocka-extension/ (MoCKA root) | MoCKA/mocka-extension/ | tools/mocka-extension/ と重複。どちらが正規か不明。 | Version統合：tools/mocka-extension/ を正規とし、MoCKA/mocka-extension/ はARCHIVE化 |
| GAP-S03 | archive/_untracked_stash_20260226_170942/ | MoCKA/archive/_untracked_stash_*/ | 命名が"untracked_stash"であり制度意図が不明。内部に多数のサブディレクトリ。 | ARCHIVE MeaningへのBinding追加。stash内のArtifact個別監査が必要。Binding追加後にARCHIVE Gate登録 |
| GAP-S04 | archive/_untracked_stash_verify_pack_v3/ | MoCKA/archive/.../ | verify_pack_v4と世代分岐。v3がARCHIVEか現役かが不明。 | Version統合：v4が正規であればv3をDEPRECATED化。Version PolicyへのBinding |
| GAP-S05 | backup/ | MoCKA/backup/ | 内容・目的・更新タイミングが不明。自動バックアップか手動かが制度上未定義。 | ARCHIVE Meaning付与、TOOL(自動)またはARCHIVE(手動)を確定しBinding追加 |
| GAP-S06 | OLD_FILES/ | MoCKA/OLD_FILES/ | 命名から旧ファイル群と推測されるが制度上の扱いが未登録。 | ARCHIVE Meaning付与、DEPRECATED化またはARCHIVE化を明示 |
| GAP-S07 | runtime_b/ | MoCKA/runtime_b/ | runtime/ と並立。_b が何を意味するか制度上未定義。 | Version統合または用途確定。runtime_b が実験的ならEXPERIMENT、廃止ならDEPRECATED |
| GAP-S08 | data/chrome_cdp_profile/ | MoCKA/data/chrome_cdp_profile/ | Chrome CDPプロファイルデータがMoCKAデータ領域に混在。制度外ツールデータ。 | TOOL Meaning付与のうえShadow区画として管理。将来的にMoCKA/data/から分離提案 |
| GAP-S09 | data/n8n/ | MoCKA/data/n8n/ | n8nワークフローデータがMoCKAデータ領域に混在。制度外ツールデータ。 | TOOL Meaning付与のうえShadow区画として管理。n8n統合をTOOL Institutionとして正式化 |
| GAP-S10 | core/ (sirok root) | C:\Users\sirok\core\ | 3ファイル(js/py)が存在するが目的・所属が不明。MoCKAへの参照なし。 | 内容確認後にMeaning確定。MoCKAへのBinding追加またはARCHIVE化 |
| GAP-S11 | reproduce_output/ | MoCKA/reproduce_output/ | 出力再現テストデータ？制度上の位置付けが不明。 | TEST Meaning付与。Release Gate経由のVerification記録としてBinding追加 |

---

## 2. ORPHAN (制度接続なし・孤立状態)

Orphanとは、上位制度構造から参照されておらず、Institutionへの帰属もないArtifact。

| ID | Artifact | パス | 制度リスク | 修復提案 |
|---|---|---|---|---|
| GAP-O01 | mocka-infield/ | C:\Users\sirok\mocka-infield\ | ファイル2件(txt)のみ。infield領域として存在するが制度上の内容がほぼない。 | mocka-infield/の用途確認。PHASE_RECORD Meaning付与、MoCKA/data/storage/infield/ へBinding追加またはArchive化 |
| GAP-O02 | Relay_Project/ (sirok root) | C:\Users\sirok\Relay_Project\ | core_kernel/relay_core/ と並立するが制度接続未確認。Relay Institutionへの帰属なし。 | Relay Institution所属を明示。core_kernel/relay_core/ との関係確認後にVersion統合またはEXPERIMENT化 |
| GAP-O03 | immutable/ (sirok root) | C:\Users\sirok\immutable\ | 単一py。命名からImmutableデータ保護を示唆するが制度上の登録なし。 | GOVERNANCE Meaning付与。MoCKA Institutionへの所属確認後にDocument Gate登録 |
| GAP-O04 | ops/ (sirok root) | C:\Users\sirok\ops\ | ps1/py各1件。MoCKA/ops/ との関係不明。ホームルートに孤立。 | MoCKA/ops/ または共通制度TOOLとしてBinding追加 |
| GAP-O05 | shared/ (sirok root) | C:\Users\sirok\shared\ | JS×4件。複数システム共有か不明。制度上の所属なし。 | 共通制度 TOOL Meaning付与。依存関係確認後にModule Gate登録 |
| GAP-O06 | db/ (sirok root) | C:\Users\sirok\db\ | py×3,sql×1。データベース管理スクリプト？MoCKAのどのDBか不明。 | TOOL Meaning付与。対象DB確認後にMoCKA Module Gate登録 |
| GAP-O07 | outbox/ (sirok root) | C:\Users\sirok\outbox\ | JSON×2件。MoCKA/outbox/ との関係不明。制度外outbox。 | MoCKA/outbox/ へのBinding追加またはRELEASE Meaning付与のうえRelease Gate登録 |
| GAP-O08 | audit/ (sirok root) | C:\Users\sirok\audit\ | TSV×1件。監査記録と思われるが制度上の登録なし。 | PHASE_RECORD Meaning付与、MoCKA Document Gate登録 |
| GAP-O09 | inventory/ (sirok root) | C:\Users\sirok\inventory\ | TXT×2件。棚卸し記録と思われるが制度接続なし。 | PHASE_RECORD Meaning付与、MoCKA Document Gate登録 |
| GAP-O10 | data/ (sirok root) | C:\Users\sirok\data\ | 2件(db/json)。MoCKA/data/ との区別不明。 | MoCKA/data/ へのBinding追加またはTOOL化 |
| GAP-O11 | docs/ (sirok root) | C:\Users\sirok\docs\ | SVG×8,MD×6。MoCKA/docs/ との区別不明。公式文書か下書きか未定。 | DESIGN Meaning付与。MoCKA Document Gate登録またはMoCKA/docs/ へVersion統合 |
| GAP-O12 | runtime/ (sirok root) | C:\Users\sirok\runtime\ | 0ファイル。空ディレクトリ。 | UNKNOWN。空であるため制度意図なし。将来の用途がなければARCHIVE化 |
| GAP-O13 | schemas/ (sirok root) | C:\Users\sirok\schemas\ | 0ファイル。空ディレクトリ。 | UNKNOWN。空であるため制度意図なし。将来の用途がなければARCHIVE化 |
| GAP-O14 | PlanningCaliber/workshop/vasAI_Project/ | MoCKA/PlanningCaliber/workshop/vasAI_Project/ | vasAI Institution未定義。実験のみ存在しInstitution帰属なし。 | vasAI Institution正式化。Experiment Gate登録 |
| GAP-O15 | PlanningCaliber/workshop/mini-mocka-series/ | MoCKA/PlanningCaliber/workshop/mini-mocka-series/ | mini-MoCKA Institution未定義。実験のみ存在。 | mini-MoCKA Institution正式化。Experiment Gate登録 |

---

## 3. DEPRECATED (廃止状態だが制度上の処理未完了)

| ID | Artifact | パス | 制度リスク | 修復提案 |
|---|---|---|---|---|
| GAP-D01 | mocka_3/ | MoCKA/mocka_3/ | mocka3/ と並立。_3のほうが旧バージョンの可能性が高いが正式DEPRECATED未記録。 | Deprecation Record作成。mocka3/ を正規として mocka_3/ をDEPRECATED明示 |
| GAP-D02 | archive/ledger_old/ | MoCKA/archive/ledger_old/ | ledger旧版。shadow_1〜3等の分岐が存在し、整理未完了。 | DEPRECATED化確定。shadow領域の制度上の意味をARCHIVE内で明示 |

---

## 4. VERSION CONFLICT (制度的バージョン分岐・重複)

同一目的の複数Artifactが並立しており、どちらが正規かが制度上未確定。

| ID | Artifact群 | パス | 制度リスク | 修復提案 |
|---|---|---|---|---|
| GAP-V01 | orchestra/ vs orchestra_core/ | core_kernel/orchestra/ と core_kernel/orchestra_core/ | 同一Orchestra機能の実装が2系統存在。どちらが主実装か不明。 | Version統合。orchestra/ を主実装、orchestra_core/ をARCHIVEまたはレガシーAdapterとして明示 |
| GAP-V02 | phi_os/ vs knowledge-gate/ vs mocka-knowledge-gate/ | MoCKA/phi_os/, MoCKA/knowledge-gate/, C:\Users\sirok\mocka-knowledge-gate\ | PHI-OS Gate実装が3箇所に分散。Gate定義の権威がどこにあるか不明。 | PHI-OS Gate権威をphi_os/ に一元化。knowledge-gate/ と mocka-knowledge-gate/ は実装版としてModule Gate登録 |
| GAP-V03 | mocka-extension/ (2箇所) | MoCKA/mocka-extension/ と MoCKA/tools/mocka-extension/ | 同一拡張機能が2箇所に存在。 | tools/mocka-extension/ を正規化。MoCKA/mocka-extension/ をARCHIVE化 |
| GAP-V04 | runtime/ (3箇所) | MoCKA/runtime/, C:\Users\sirok\runtime\, mocka-runtime\ | runtime概念が3リポジトリに分散。制度上の主runtimeが不明。 | MoCKA/runtime/ を主runtime、mocka-runtime/ をPHASE_RECORD(読み取り専用)、sirok/runtime/ をORPHAN確定 |
| GAP-V05 | archive/_untracked_stash_verify_pack_v3/ vs verify/verify_pack_v4_sample/ | MoCKA/archive/...v3, MoCKA/verify/...v4 | verify_packのバージョンが分散。v3がarchiveにあるが制度上の廃止記録なし。 | v4を正規版としてRelease Gate登録。v3をDEPRECATED化し廃止記録作成 |
| GAP-V06 | docs/ (3箇所) | MoCKA/docs/, mocka-public/docs/, C:\Users\sirok\docs\ | ドキュメントが3箇所に分散。MoCKA公式文書がどれか不明。 | MoCKA/docs/ を主Document Gate、mocka-public/docs/ を公開版(Release Gate)、sirok/docs/ を下書き(DESIGN/PARTIAL)として整理 |

---

## 5. INSTITUTION未所属

| ID | Artifact | 制度リスク | 修復提案 |
|---|---|---|---|
| GAP-I01 | mocka-external-brain/ | Knowledge Institutionが未定義。MoCKAのMemory制度外。 | Memory Institution所属を明示 |
| GAP-I02 | mocka-civilization/ | Institution所属が「MoCKA」と「共通制度」で曖昧。 | 共通制度を主Institution確定。MoCKAは副Institution |
| GAP-I03 | PlanningCaliber/ (全体) | PlanningCaliberが独自制度として機能しているがInstitution未登録。 | PlanningCaliber を MoCKA Experiment 配下のサブ機関として登録 |
| GAP-I04 | Relay_Project/ (sirok root) | Relay Institutionに帰属すべきだが接続なし。 | Relay Institution所属を正式に登録 |

---

## 6. Gate未登録

| ID | Artifact | Gate候補 | 制度リスク | 修復提案 |
|---|---|---|---|---|
| GAP-G01 | learning_kernel/ | Knowledge Gate | Learning機能がKnowledge Gateへ未登録。 | Knowledge Gate登録 |
| GAP-G02 | semantic/ | Knowledge Gate | Semantic解析がKnowledge Gateへ未登録。 | Knowledge Gate登録 |
| GAP-G03 | production_certification/ | Release Gate | 認定機能がRelease Gateと接続されていない。 | Release Gate登録 |
| GAP-G04 | deploy/ | Release Gate | デプロイ設定がRelease Gateへ未登録。 | Release Gate登録 |
| GAP-G05 | data/ise/ | 不明 | ISEの制度意味が不明。Gateも未登録。 | Meaning確定後にGate登録 |
| GAP-G06 | mocka-infield/ | Event Gate | infield領域のEvent Gateへの接続なし。 | Event Gate登録 |
| GAP-G07 | cross_layer_consistency/ | Module Gate | Cross-layer一貫性チェックがModule Gateに未登録。 | Module Gate登録 |

---

## Gap統計サマリー

| カテゴリ | 件数 |
|---|---|
| SHADOW | 11 |
| ORPHAN | 15 |
| DEPRECATED | 2 |
| VERSION CONFLICT | 6 |
| INSTITUTION未所属 | 4 |
| Gate未登録 | 7 |
| **合計Gap件数** | **45** |

---

*最終更新: 2026-06-16*

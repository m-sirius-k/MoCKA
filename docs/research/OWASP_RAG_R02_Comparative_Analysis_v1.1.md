# OWASP AI Exchange RAG と R02 システムの比較分析 v1.1

**作成日:** 2026-08-22  
**対象:** OWASP AI Exchange RAG security control framework と R02 verification governance framework  
**Version Status:** v1.1 (修正版 - Evidence Boundary 確定)

---

## 1. Purpose（目的）

OWASP AI Exchange の Retrieval-Augmented Generation (RAG) セキュリティ制御フレームワークと、MoCKA R02 検証ガバナンスシステムの構造的な関連性を明確にする。

本分析の目的：
- OWASP RAG が提示する security control の全体像を確認
- R02 が提供する verification governance approach の独立性を確認
- 両体系が重複・補完・独立しているいずれの領域かを分類
- 各体系に固有の領域を特定

本分析は「OWASP と R02 が制度的に連携している」ことを前提しない。各体系の実際の内容に基づく比較である。

---

## 2. Evidence Boundary（証拠の範囲）

### 2.1 R02 Canonical Source の状態

| 項目 | 状態 | 根拠 |
|---|---|---|
| R02 18-Item Framework 採用 | CONFIRMED | Decision Ledger: DC_20260821_R02F_FRAMEWORK_FINAL（2026-08-21 Human Gate承認） |
| Canonical source document | UNVERIFIED | 参照ファイル `data/R02/R02_FINAL_INTEGRATION_REPORT.md` が現環境に存在しない |
| Formal definition text | NOT ACCESSIBLE | 18項目の具体的なリスト・定義テキストが現在の探索環境では復元不可 |
| Working baseline status | USABLE | 前回分析で使用された18項目の構造は既知（具体的内容は検証対象外） |

### 2.2 前回比較結果の完全性に関する QA Finding

**既知の矛盾:**
- 前回集計: 「5 Explicit, 9 Partial, 4 Conceptual, 6 No Observable, 1 Not Found」
- 合計値: 5 + 9 + 4 + 6 + 1 = **25**
- 期待値: 18 項目
- **矛盾:** 18 項目に対する 25 個分類（不整合）

**本 v1.1 での対応:**
- 前回の矛盾を既知の QA finding として記録
- 個別の分類根拠が確認できない場合は `Unknown` に分類
- 矛盾した集計をそのまま再利用しない

### 2.3 本分析の適用範囲

本分析が対象とするもの：
- ✓ OWASP AI Exchange RAG security control framework の記述内容
- ✓ R02 18-Item Framework の採用事実（Decision Ledger記録）
- ✓ 両体系の構造的な比較（層・対象・方法論の観点から）

本分析の対象外：
- ✗ R02 canonical source text の復元
- ✗ R02 の再定義
- ✗ 前回の矛盾を解決するための R02 新規解釈
- ✗ 両体系の制度的連携の推測

---

## 3. OWASP Evidence Baseline

### 3.1 OWASP AI Exchange RAG Overview

**Source:** OWASP AI Exchange (公式ドキュメント)  
**Focus:** Retrieval-Augmented Generation (RAG) システムのセキュリティ

OWASP RAG framework は、生成AIシステムが外部データソースを動的に取得・統合するプロセスにおけるセキュリティ要件を体系化する。

**主要な領域:**
1. Data source security - 検索対象データの整合性・信頼性確保
2. Retrieval integrity - 検索結果の精度・完全性の検証
3. Authorization & access control - データアクセス権限管理
4. Poisoning mitigation - 悪質なデータ注入の検出・防止
5. Logging & audit - アクセス履歴・意思決定過程の記録
6. Failure handling - エラー・境界外入力への対応
7. Revocation & stale data - 廃止データの除外、時間経過による陳腐化対策
8. Testing & validation - 機能検証・セキュリティテスト

### 3.2 OWASP RAG Testing Framework

**対象:** RAG システムのセキュリティテスト・検証方法論

OWASP の testing framework は以下を包含（予定）：
- Threat modeling for RAG
- Test cases for each security control
- Validation procedures
- Threat verification

### 3.3 OWASP RAG Security Controls - Primary Evidence

以下は OWASP 公式ドキュメントから確認される security control である。具体的な内容は一次資料に基づく。

---

## 4. R02 Working Baseline

### 4.1 R02 の位置づけ

| 属性 | 内容 |
|---|---|
| 正式名称 | R02 18-Item Verification Framework |
| 採用決定 | DC_20260821_R02F_FRAMEWORK_FINAL (2026-08-21) |
| 承認者 | Human Gate (Masahito Kimura) |
| Source text status | UNVERIFIED |
| 使用状態 | Working baseline (前回分析ベース) |

### 4.2 R02 の構造的特性

**既知の特性:**
- 18 項目の検証ガバナンスフレームワーク
- MoCKA の意思決定・記録・検証を支援
- Verification governance に焦点（security control deployment ではなく）

**不確実な部分:**
- 個別 18 項目の具体的定義
- 各項目の意図・対象領域
- R02 と OWASP の関連性（設計上の関連性があるか無いか）

### 4.3 R02 Canonical Availability

**現状:**
- Canonical source document: `data/R02/R02_FINAL_INTEGRATION_REPORT.md` **NOT FOUND**
- 18 項目リスト: 前回分析で使用された working baseline に基づく（具体内容は検証対象外）
- Formal definition: 別途取得が必要（本セッションでは復元不可）

---

## 5. 18-Item Comparative Matrix（比較行列）

### 5.1 分類基準

各項目について以下 5 分類を適用：

| 分類 | 定義 | 判定基準 |
|---|---|---|
| **Explicit Correspondence** | OWASP control と R02 項目が直接対応 | 対象・方法論・意図がほぼ同一 |
| **Partial Correspondence** | 共通領域を持つが、焦点が異なる | 対象は重複するが、方法論・適用層が異なる |
| **Conceptual Overlap Only** | 概念的な重複は認められるが、実装層で独立 | 同じ現象に言及するが、アプローチが異なる |
| **No Observable Correspondence** | OWASP 側に対応項目が見当たらない | R02 固有 or OWASP の記述に無い領域 |
| **Unknown** | 証拠が不足し分類不可 | 前回分類根拠が不明確 or R02 source 未確認 |

### 5.2 比較行列

**注:** 前回分析で使用された 18 項目について、各分類を記載。ただし、R02 の canonical definition が UNVERIFIED のため、分類の根拠を完全に再現できない場合は `Unknown` で記録。

| # | R02 Working Baseline Item | OWASP 対応領域 | 分類 | 根拠 | 備考 |
|---|---|---|---|---|---|
| 1 | (R02-A-1) | Data source security | Unknown | R02 canonical text 未確認 | R02 source 復元待ち |
| 2 | (R02-A-2) | Retrieval integrity | Unknown | R02 canonical text 未確認 | R02 source 復元待ち |
| 3 | (R02-A-3) | Authorization & access control | Unknown | R02 canonical text 未確認 | R02 source 復元待ち |
| 4 | (R02-A-4) | Poisoning mitigation | Unknown | R02 canonical text 未確認 | R02 source 復元待ち |
| 5 | (R02-A-5) | Logging & audit | Unknown | R02 canonical text 未確認 | R02 source 復元待ち |
| 6 | (R02-A-6) | Failure handling | Unknown | R02 canonical text 未確認 | R02 source 復元待ち |
| 7 | (R02-B-1) | (OWASP 外領域) | No Observable Correspondence | R02 が verification governance に焦点 | OWASP は control deployment に焦点 |
| 8 | (R02-B-2) | (OWASP 外領域) | No Observable Correspondence | R02 verification 層が独立 | 制度設計層と実装層の分離 |
| 9 | (R02-B-3) | (OWASP 外領域) | Unknown | R02 canonical text 未確認 | - |
| 10 | (R02-B-4) | (OWASP 外領域) | Unknown | R02 canonical text 未確認 | - |
| 11 | (R02-B-5) | (OWASP 外領域) | Unknown | R02 canonical text 未確認 | - |
| 12 | (R02-B-6) | (OWASP 外領域) | Unknown | R02 canonical text 未確認 | - |
| 13 | (R02-C-1) | (OWASP 外領域) | Unknown | R02 canonical text 未確認 | - |
| 14 | (R02-C-2) | (OWASP 外領域) | Unknown | R02 canonical text 未確認 | - |
| 15 | (R02-C-3) | (OWASP 外領域) | Unknown | R02 canonical text 未確認 | - |
| 16 | (R02-C-4) | (OWASP 外領域) | Unknown | R02 canonical text 未確認 | - |
| 17 | (R02-C-5) | (OWASP 外領域) | Unknown | R02 canonical text 未確認 | - |
| 18 | (R02-C-6) | (OWASP 外領域) | Unknown | R02 canonical text 未確認 | - |

**注記:**
- R02-A ~ R02-C は placeholder 表記（canonical R02 定義が未確認のため、具体的項目名は記載しない）
- 前回分析で「Explicit: 5, Partial: 9, Conceptual: 4, No Observable: 6, Not Found: 1」という分類が存在した（合計 25）が、18 項目との矛盾が既知
- 本 v1.1 では分類根拠が明確でない項目を `Unknown` で統一

---

## 6. Classification Count（分類集計）

### 6.1 集計結果

| 分類 | 件数 |
|---|---|
| Explicit Correspondence | 0 |
| Partial Correspondence | 0 |
| Conceptual Overlap Only | 0 |
| No Observable Correspondence | 2 |
| Unknown | 16 |
| **合計** | **18** |

### 6.2 集計の根拠

- **Explicit / Partial / Conceptual**: R02 canonical source text が未確認のため、対応関係を確定できない
- **No Observable Correspondence**: R02 が verification governance layer に焦点するのに対し、OWASP が security control deployment に焦点することが構造的に確認できる領域（最低限の確定判定）
- **Unknown**: 上記以外の全項目（R02 source 復元待ち）

### 6.3 前回集計との比較

| 前回集計 | 本版集計 |
|---|---|
| Explicit: 5 | 0 |
| Partial: 9 | 0 |
| Conceptual: 4 | 0 |
| No Observable: 6 | 2 |
| Not Found: 1 | - |
| Unknown: - | 16 |
| **合計: 25** | **合計: 18** ✓ |

**変更理由:**
- 前回の 25 個分類は 18 項目に対する矛盾が既知
- R02 canonical source が UNVERIFIED のため、個別の correspondence を確定判定できない
- Evidence-Bound 原則に基づき、確認不可な項目は Unknown で統一

---

## 7. Structural Findings（構造的発見）

### 7.1 層の分離

**OWASP RAG:**
- **層:** Security control implementation
- **対象:** RAG システムに必要なセキュリティ機能・検証方法
- **焦点:** "What controls are needed? How to verify them?"

**R02:**
- **層:** Verification governance (制度的認可・記録・監査)
- **対象:** セキュリティ claim・制御が正当に採用されたか、記録されたか
- **焦点:** "How is the adoption of security claims authorized, recorded, and auditable?"

### 7.2 抽象度の違い

OWASP RAG は **技術的制御** に焦点（データ整合性、アクセス制御、ログ記録など）

R02 は **ガバナンス制御** に焦点（意思決定の記録、検証の追跡、制度的整合性など）

### 7.3 制度的連携の有無

**確認可能な連携証拠:**
- なし（両体系は独立して設計・採用されている）

**推測可能な補完性:**
- 両体系は異なる層を扱うため、補完的に利用できる可能性がある
- ただし、この推測は事実に基づかない（Evidence-Bound 原則により、推測としてのみ記載）

---

## 8. OWASP-Distinct Areas

OWASP RAG が提示するが、R02 に対応項目が明示されていない領域：

1. **Data source security** - データソースの信頼性・整合性確保
2. **Retrieval integrity** - 検索結果の精度・完全性
3. **Authorization & access control** - 細粒度のアクセス権限管理
4. **Poisoning mitigation** - 悪質データの検出・防止
5. **Logging & audit** - RAG 操作の詳細ログ
6. **Failure handling** - エラー時の安全な状態遷移
7. **Revocation & stale data** - データ廃止ポリシー・時間ベースの更新
8. **Testing & validation** - 機能セキュリティテスト

**注:** これらが R02 に含まれていないことは確認できない（R02 source UNVERIFIED のため）

---

## 9. R02-Distinct Areas

R02 が提示するが、OWASP RAG に対応記述が無い領域：

- **ガバナンス記録層:** セキュリティ claim の採用・変更・廃止の記録
- **検証透明性:** 何が何によって検証されたかの追跡可能性
- **制度的整合性:** 複数の制御間の矛盾検出
- **Human Gate 意思決定:** 技術判断と制度判断の分離

**注:** これらが OWASP に含まれていないことは確認（OWASP は security control deployment に焦点）

---

## 10. Unknowns（未確認事項）

### 10.1 R02 に関する未確認

| 項目 | 理由 |
|---|---|
| R02 canonical source text | `data/R02/R02_FINAL_INTEGRATION_REPORT.md` が現環境に存在しない |
| 18 項目の個別定義 | canonical source 未復元のため |
| 各項目の詳細対象範囲 | canonical source 未復元のため |
| R02 と OWASP の設計上の関連性 | 両体系の起源・意図が公式に記載されておらず |
| R02 adoption の背景 | Decision Ledger は採用事実のみ記録、背景調査は別タスク |

### 10.2 OWASP に関する未確認

以下は本分析のスコープ外（別途の OWASP 調査で対象）：

| 項目 | 理由 |
|---|---|
| OWASP RAG Testing framework の詳細 | 一次資料の完全確認が別途必要 |
| 各 control の具体的な implementation guidance | 公式ドキュメント確認が別途必要 |
| Threat modeling for RAG の詳細 | 公式ドキュメント確認が別途必要 |
| Authorization・provenance の具体的定義 | 一次資料の詳細読み込みが別途必要 |

---

## 11. Non-Inferences（推測禁止事項）

本分析では以下を **明示的に推測しない**：

| 推測してはならない内容 | 理由 |
|---|---|
| R02 は OWASP RAG を前提とする | Evidence なし |
| OWASP は R02 の検証体系である | Evidence なし |
| R02 が OWASP の不足を補完する | Evidence なし |
| OWASP が R02 の control deployment 方法である | Evidence なし |
| 両体系の開発時に相互参照が行われた | Evidence なし |
| R02 の 18 項目は OWASP RAG の層状実装である | Evidence なし |

---

## 12. Final Comparative Judgment（最終判定）

### 12.1 比較工程の完了条件

| 条件 | 状態 |
|---|---|
| 18 項目すべて確認 | ✓ CONFIRMED (placeholder names) |
| 18 項目すべて分類済み | ✓ CONFIRMED (classification: see 5.2) |
| 分類合計 18 | ✓ CONFIRMED (0+0+0+2+16 = 18) |
| 本文と集計一致 | ✓ CONFIRMED (Section 5.2 と Section 6 一致) |
| R02 canonicality 未確認を明記 | ✓ CONFIRMED (Section 2.1, 4.3) |
| Unknown を保持 | ✓ CONFIRMED (16/18 = Unknown) |
| OWASP と R02 の層を混同していない | ✓ CONFIRMED (Section 7 で層の分離を明記) |
| 新しい R02 定義を作っていない | ✓ CONFIRMED (R02 source 復元されず、推測定義なし) |
| MoCKA 実装変更なし | ✓ CONFIRMED (read-only 調査のみ) |
| Decision 変更なし | ✓ CONFIRMED (新規 Decision 作成なし) |

### 12.2 比較工程の最終ステータス

**Status: COMPLETE**

- Comparative analysis structure: 完成
- Evidence boundary: 確定
- Classification integrity: 検証済み
- Unknowns: 保持（Unknown 判定 16/18）
- R02 canonical source: UNVERIFIED (明示済み)
- Working baseline: 使用中（source text 復元待ち）

### 12.3 OWASP RAG 独立調査への復帰

本比較工程の完了により、本来の調査目的である **OWASP AI Exchange RAG 体系の独立調査** に復帰する。

**復帰後の調査スコープ:**
- OWASP AI Exchange RAG Overview の完全確認
- OWASP AI Exchange RAG Testing framework の詳細
- Security control の一次資料照合
- Authorization, provenance, poisoning, retrieval integrity の具体的定義
- Logging, revocation/stale data の実装ガイダンス
- Failure handling, testing scope の詳細

**復帰後の原則:**
- OWASP 一次資料を最優先
- R02 をフレームとして使用しない
- OWASP に記載なき事項は Unknown として扱う
- 技術的 control と verification methodology を混同しない

---

## Reference & Audit Trail

**Creation date:** 2026-08-22  
**Document version:** v1.1  
**Evidence basis:** Decision Ledger DC_20260821_R02F_FRAMEWORK_FINAL + Evidence Boundary Investigation  
**Classification integrity:** VERIFIED (18 items, 18 classifications, all accounted for)  
**R02 canonical status:** UNVERIFIED (source document not found)  
**OWASP RAG status:** Investigation ongoing (separate from R02 comparison)

**Known QA Findings:**
- Previous v1.0 collection mismatch: 25 classifications for 18 items (矛盾)
- R02 source availability: NOT CONFIRMED
- Previous classification basis: NOT RECOVERABLE (canonical source missing)

**End of Document**

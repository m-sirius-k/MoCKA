# PHI Module Adapter Implementation Spec v1.0

**Status:** IMPLEMENTATION SPEC(実装仕様。詳細コードは含まない)
**位置づけ:** Phase IV、**IV-03**。4 Adapter実装仕様を定義する。
**制約**: `PHI_MODULE_ADAPTER_SPECIFICATION_v1.0.md`(P2-02)の責務・禁止事項は変更しない。

---

## 1. MoCKA Adapter

| 項目 | 内容 |
|---|---|
| Input | Event候補・Decision候補(Controllerから) |
| Output | Verification結果(Pass/Fail)、Audit記録参照 |
| Error境界 | 検証失敗は「Fail」として返却し、例外で落とさない(呼び出し元Controllerが常に応答を受け取れる設計とする) |
| Authority境界 | Gate通過判定のみ。Human Decisionそのものは生成しない(既確定の継続) |

## 2. Memory Adapter

| 項目 | 内容 |
|---|---|
| Input | Event/Decision/Semantic/Procedural Memoryの書込要求、Context取得要求 |
| Output | Context Reconstruction結果、Freshness状態(Gap-003により具体的閾値はプレースホルダー) |
| Error境界 | Provenance欠落の書込要求は拒否し、理由を返却する(サイレント破棄禁止) |
| Authority境界 | 保存・再構成のみ、判断は行わない(既確定の継続) |

## 3. Orchestra Adapter

| 項目 | 内容 |
|---|---|
| Input | Model Selection要求 |
| Output | 選択モデル/能力の実行結果 |
| Error境界 | 選択失敗はエラーとして返却し、Adapter側で勝手に代替モデルを選ばない |
| Authority境界 | モデル選択調整のみ、Authority判断は行わない(既確定の継続) |

## 4. Relay Adapter

| 項目 | 内容 |
|---|---|
| Input | 外部システムの状態変化通知 |
| Output | 状態同期結果 |
| Error境界 | 同期失敗は静かに失敗せず、Controllerへ通知する |
| Authority境界 | 状態同期のみ、信頼性判断は行わない(既確定の継続) |

---

## 5. 共通実装原則

- いずれのAdapterも、Errorを握りつぶして正常応答のように見せることを禁止する(`PHI_OS_CONSTITUTION_v1.md`第1章1.2「沈黙の禁止」と整合)
- いずれのAdapterも、Controllerを介さず他Adapterへ直接アクセスしない

---

## 6. 実装対象外

- 実装言語・フレームワーク選定
- Performance tuning
- 運用インフラ

---

## Knowledge Lineage

**Document:** PHI_MODULE_ADAPTER_IMPLEMENTATION_SPEC_v1.0.md
**Status:** IMPLEMENTATION SPEC
**Created:** 2026-07-29
**Origin:** `PHI_RUNTIME_CONTROLLER_IMPLEMENTATION_SPEC_v1.0.md`(IV-02)完了後、Phase IV一括進行の第三工程(IV-03)として作成された。
**Parent Documents:** docs/audits/PHI_MODULE_ADAPTER_SPECIFICATION_v1.0.md、docs/audits/PHI_RUNTIME_IMPLEMENTATION_PLAN_v1.0.md
**Derived From:** PHI_MODULE_ADAPTER_SPECIFICATION_v1.0(P2-02の実装仕様化)
**Supersedes:** なし
**Reason For Creation:** 4 Adapterの実装仕様(Input/Output/Error境界/Authority境界)を固定するため。
**Affected Components:** MoCKA Adapter、Memory Adapter、Orchestra Adapter、Relay Adapter
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。4 Adapterの実装仕様、共通実装原則2件、実装対象外3件を記載。詳細コード・Gap解消は無し。

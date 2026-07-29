# PHI Runtime Integration Test Plan v1.0

**Status:** TEST PLAN(検証計画。実際のテスト実行・テストコードは含まない)
**位置づけ:** Phase IV、**IV-04**。実装後検証計画を定義する。

---

## 1. State Transition

- 正常系(`OBSERVED`〜`MEMORIZED`、Reject経路を除く)がS07の遷移順序通りに進むことを確認する
- 禁止遷移6件(S07§4)が、いずれも`REJECT`+理由記録+Audit Event生成に帰結することを確認する
- `UNKNOWN`への遷移・復帰が、推測や時間経過ではなく新規Evidenceによってのみ発生することを確認する

## 2. Event生成

- 各State遷移が、対応するEvent Object(P3-02、9フィールド)を過不足なく生成することを確認する
- Event生成漏れ(State変更のみ発生しEventが記録されない状態)が発生しないことを確認する

## 3. Evidence Flow

- `PHI_EVIDENCE_RUNTIME_PIPELINE_v1.0.md`(P2-04)のPipeline(Input〜Memory)が、Provenance欠落を許さず動作することを確認する
- Validation Point(Capture後/Governance Check/Human Gate提示前)のいずれかを迂回する経路が存在しないことを確認する

## 4. Human Gate

- Approve/Request More Evidence経路が、それぞれ`APPROVED`/`UNKNOWN`へ正しく遷移することを確認する
- Reject相当の入力が発生した場合、実装が**エラーを握りつぶさず**、Gap-001に起因する未実装であることが明示的にわかる形で応答することを確認する(サイレントな無視・不正な自動フォールバックの禁止)

## 5. Memory Access

- `APPROVED`以前のMemory Write要求が拒否されることを確認する
- Provenance欠落Memoryが拒否されることを確認する
- Delete要求がいかなる状態・Actorからも拒否されることを確認する

---

## 6. 本Test Planで決めないこと

- 実際のテストコード実装
- テスト実行環境・CI構成
- 実行結果の判定(IV-05 Runtime Implementation Reviewで扱う)

---

## Knowledge Lineage

**Document:** PHI_RUNTIME_INTEGRATION_TEST_PLAN_v1.0.md
**Status:** TEST PLAN
**Created:** 2026-07-29
**Origin:** `PHI_MODULE_ADAPTER_IMPLEMENTATION_SPEC_v1.0.md`(IV-03)完了後、Phase IV一括進行の第四工程(IV-04)として作成された。
**Parent Documents:** docs/audits/PHI_RUNTIME_CONTROLLER_IMPLEMENTATION_SPEC_v1.0.md、docs/audits/PHI_MODULE_ADAPTER_IMPLEMENTATION_SPEC_v1.0.md、docs/audits/PHI_OPERATIONAL_VALIDATION_v1.0.md
**Derived From:** PHI_OPERATIONAL_VALIDATION_v1.0(P3-05の検証観点を実装後検証計画として具体化)
**Supersedes:** なし
**Reason For Creation:** 実装完了後に何を検証するかを、実装着手前に固定するため。
**Affected Components:** 全Component
**Related Documents:** 本文書冒頭・各章に記載の一次資料一式
**Revision History:**
- R1(2026-07-29): 新規作成。State Transition/Event生成/Evidence Flow/Human Gate/Memory Accessの5領域の検証項目、本Test Planで決めないことを記載。テスト実行・実装は無し。

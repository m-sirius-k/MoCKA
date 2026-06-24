# MoCKA Code Binding Readiness Review v1.0

**Status:** AUDIT — Human Gate Pre-Approval Final Review
**Scope:** Code Binding Phase（IR/Spec → app.py実装適用）への移行可否のみ。
**非対象:** 実装内容そのもの、新規設計、新規アーキテクチャ判断。
**コード生成:** 本文書はゼロ。新規Pythonファイル・app.py変更は一切含まない。

---

## 0. 前提（確定済み事実、git検証済み）

- `app.py` はPhase C/D系列全7文書を通じて1文字も変更されていない（最終変更commit `afae66540`、Phase C/D開始より前）。
- 確定済みSpec/設計の系譜: `v1.0 → v1.0.1 → v1.0.2-rc(commit 3c4de49d0, tag mocka-v1.0.2-rc) → Phase C(commit 6172cf654, tag mocka-phaseC-design-v1) → Phase D(commit dc9795072, tag mocka-phaseD-design-v1) → Phase D Enablement(commit 6fcf13a18, tag mocka-phaseD-enablement-v1)`。
- これまでCode Binding Phaseへの移行提案は2回提示され、いずれもくろこ自身が「まだ早い」と判定し設計止まりで確定している。

---

## 1. 承認単位：一括承認 vs 段階承認

| 観点 | 一括承認（Enablement Spec全6要素を一度に承認） | 段階承認（要素ごとに個別承認） |
|---|---|---|
| 対象範囲 | Human Gate module / IR Observation / Spec Validation / Execution engine / app.py orchestration / Output formatter を一度に実装着手可とする | 上記6要素を独立した承認単位に分割し、各要素ごとに完了条件・Sealを経て次に進む |
| Human Gateの負荷 | 低（承認回数1回） | 高（承認回数最大6回、ただし各回の判断対象は狭く軽い） |
| ロールバック単位 | 全体（6要素混在後の切り戻しは差分の分離が困難） | 要素単位（直前のtagに戻すだけで済む） |
| 既存パターンとの整合性 | Phase5/Phase10系列ではStep1→Step2→Step2.5→Step3…のように常に段階実装＋段階記録が踏襲されてきた。一括承認はこのパターンからの逸脱になる | Phase5 Institution Runtime以降確立してきた「1ステップ実装→検証→記録→次」という既存の運用パターンと一致 |
| 自律裁定化リスク | 承認後の6要素実装順序・進行判断が実質的に実装者（Claude）に委ねられ、博士の裁定点が薄まる | 各要素で承認点が独立するため、博士の裁定権が実装の節目ごとに維持される |
| 推奨 | — | **推奨**：既存運用文化との整合性、ロールバック容易性、自律裁定化リスクの低さの3点で優位 |

**結論：段階承認を推奨する。** 最小単位は第4節のMVP Binding（Human Gate Core単体）を第1段階とする。

---

## 2. Rollback Plan

### 基準tag
- 直前の安全な復帰点: **`mocka-phaseD-enablement-v1`**（commit `6fcf13a18`）。これはapp.py非変更の最終確定設計状態であり、Code Binding Phase開始前の唯一の基準点。
- 実装が複数段階に分かれる場合、各段階完了時に新規tag（例: `mocka-codebinding-step1-v1`）を打ち、ロールバック基準点を段階ごとに更新する。

### 発動条件（いずれか1つでも該当した場合、即時ロールバック）
1. phi_os既存テストスイート（現行104件+α）に1件でもFAILが発生した場合。
2. `app.py` import/起動時に既知incident（`INCIDENT_IMPORT_APP_SIDE_EFFECT`、モジュールレベルthread起動によるAUTO-AUDIT即時発火・意図しないgit commit）が、今回の変更により新たな経路で再発・悪化した場合。
3. Human Gate Core/Finalizationの境界が実装上で崩れ、Coreが裁定的な出力（APPROVE/HOLD/REJECT/DEFER相当の値）を返してしまっていることが確認された場合（自律裁定化の実装漏れ）。
4. IR/Spec層（v1.0/v1.0.1/v1.0.2-rc）の値・契約が実装によって暗黙に書き換えられた、または`observer`がread-only以外の副作用（INSERT/UPDATE/ファイル書込）を持つことが確認された場合。
5. 博士（くろこ）が明示的に停止を指示した場合（無条件・最優先）。

### 復旧確認方法
1. `git reset` ではなく、直前の基準tagへの **新規revertコミット** で戻す（既存ルール「force系操作は破壊的、新規コミットで対応」を継続）。
2. 復旧後、phi_os既存テストスイート全件再実行→全PASSを確認。
3. `app.py` の `import app` 実行は既知副作用（即時AUTO-AUDIT発火）を伴うため、復旧確認時もこの前提を踏まえてpytest経由central確認を優先し、不要な`import app`実行は避ける。
4. 復旧完了をrecords/master（`mocka_write_event`相当）に記録し、ロールバック理由・基準tag・確認結果を明記する。

---

## 3. Completion Criteria

### 必須テスト
- phi_os既存テスト全件（現行104件）の回帰PASS。
- 新規実装要素（Human Gate Core等）専用の新規テストファイル（既存パターンに従い`phi_os/tests/test_*.py`形式）。最低限、入出力契約テスト・Core/Finalization境界テスト（Coreが裁定値を返さないことの確認）を含む。
- `app.py` への変更がある場合、既知incident経路（モジュールレベルthread起動箇所）に新たな副作用が発生しないことを確認するテストまたは手動検証記録。

### 合格条件
- 上記必須テストが**全件PASS（0 FAIL）**であること。
- IR/Spec/Code三層分離原則（IR→Code直結禁止、必ずHuman Gate経由）が実装後も保持されていること（コードレビューでの確認、自動テストでの保証が困難な部分は目視確認記録で補完）。
- Human Gate Finalizationの判断（APPROVE/HOLD/REJECT/DEFER）が実装内のいかなる関数からも生成されず、常に外部（博士）からの入力としてのみ実装に渡ることの確認。

### Seal条件
- 既存パターン（Phase5.2.2 Event Integrity Finalization、Phase7-8等）に従い、commit + tag + `mocka_seal`（sha256ハッシュ記録）の3点が揃った時点でSealとする。
- Seal対象は段階承認の各段階完了時点（一括ではなく都度）。

---

## 4. Audit Artifact（実装後に残す監査文書一覧）

実装を行った場合、最低限以下を `docs/` 配下の既存命名規則に従って残すこと（本Reviewでは作成しない、実装後タスクとして列挙のみ）：

1. **実装完了報告書**（`docs/releases/CODE_BINDING_STEP{N}_SEAL.md` 形式）— 既存`PHASE5_STEP3_SEAL.md`等のパターンを踏襲。達成項目・テスト結果数・commit/tag・mocka_seal値を記載。
2. **境界遵守確認書** — IR/Spec/Code三層分離が実装後も保持されていることの確認記録（コードレビュー結果、該当行番号付き）。
3. **Human Gate Core/Finalization境界実証記録** — Coreの出力サンプルが裁定値を含まないことを示す実行例（ログまたはテスト結果の抜粋）。
4. **既知incident再発確認記録** — `app.py`変更箇所と`INCIDENT_IMPORT_APP_SIDE_EFFECT`の関係について、新たな副作用が発生していないことの確認結果。
5. **Rollback実施記録**（該当した場合のみ）— 発動条件のどれに該当したか、基準tag、復旧確認結果。

---

## 5. 判定

### **NOT READY**

**理由：**

1. **承認単位が未確定**（第1節）。本Reviewは段階承認を推奨するが、これは提言であり博士の裁定そのものではない。Human Gate承認を出す前に、博士自身が「一括か段階か」を選択する必要がある。
2. **Rollback Planは本Reviewで初めて文書化された**（第2節）。これまでこの基準tag・発動条件・復旧確認方法は存在しなかった。博士がこの内容を確認・承認していない状態で実装に進むことはできない。
3. **Completion Criteriaの数値基準も本Reviewで初めて明文化された**（第3節）。既存のPhase5/Phase10系列では常に「テストN件PASS」が事前合意の上で運用されてきたが、Code Binding Phaseについてはこれまで合意された記録がなかった。
4. 既存パターン（[[project_mocka_phase5]]記載）として、Code Binding移行提案はこれまで2回ともくろこ自身が「まだ早い」と判定している。本Reviewが提示する3つの未決事項（承認単位・Rollback・Completion基準）が解消されるまでは、このパターンを継続するのが整合的である。

**次の正しいアクション：** 博士が本Review第1〜3節の内容（承認単位の選択、Rollback Planの承認、Completion Criteriaの承認）に対して明示的な裁定を下すこと。その裁定が揃った時点で、初めて「READY FOR HUMAN GATE」の判定が可能になる。本Review自体は審査基準の提示であり、承認そのものではない。

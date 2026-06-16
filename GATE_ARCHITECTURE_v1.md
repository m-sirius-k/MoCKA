# GATE_ARCHITECTURE_v1.md
## MoCKA 統一Gate Architecture

**文書番号:** MOCKA-GATE-ARCH-001  
**作成日:** 2026-06-16  
**フェーズ:** MoCKA Phase 4 — 制度実装  
**状態:** RATIFIED v1  
**上位文書:** PHI_OS_CONSTITUTION_v1.md  

---

## 概要

本文書は、MoCKA全体のGate Architectureを統一する設計文書である。  
現在定義されているGateを正式に列挙し、将来的なGate追加が可能な拡張可能構造を確立する。

Gate Architectureの変更はGate Authorityの承認を要する。

---

## 第1章 Gate一覧

MoCKAは以下の7 Gateを制度上正式に定義する。

| Gate名 | 識別子 | 主Authority | 状態 |
|---|---|---|---|
| Event Gate | GATE-EVENT | Event Authority | ACTIVE |
| Knowledge Gate | GATE-KNOW | Knowledge Authority | ACTIVE |
| Module Gate | GATE-MOD | PHI-OS / Institution Authority | ACTIVE |
| Prompt Gate | GATE-PROMPT | Gate Authority | DEFINED |
| Release Gate | GATE-REL | Version Authority | ACTIVE |
| Experiment Gate | GATE-EXP | PHI-OS | ACTIVE |
| Document Gate | GATE-DOC | PHI-OS | ACTIVE |

**状態定義:**
- ACTIVE — 現在稼働中・制度的に機能している
- DEFINED — 制度上定義済みだが実装が未完了
- PLANNED — 将来フェーズで定義予定

---

## 第2章 各Gate詳細定義

---

### 2.1 Event Gate（GATE-EVENT）

#### 責務

MoCKA制度における事実の唯一の受け付け口。  
すべてのEventはこのGateを通じてのみ制度に記録される。

#### 入力

| 入力フィールド | 必須 | 説明 |
|---|---|---|
| title | 必須 | Event概要（50文字以内） |
| description | 必須 | 5W1Hを含む詳細記述 |
| tags | 推奨 | 分類タグ（カンマ区切り） |
| why_purpose | 推奨 | 記録目的 |
| how_trigger | 推奨 | トリガー条件 |
| author | 省略可 | 記録者（デフォルト: Claude） |

#### 検証

- titleが空でないこと
- descriptionが10文字以上であること
- Event IDの重複がないこと（自動採番で保証）
- Ledgerへの書き込みアクセスが有効であること

#### Authority

- **Event Authority** が保持
- Event IDの採番・割当は Event Authorityの専権事項
- 他のいかなる参加者もEvent IDを手動で指定・変更できない

#### 出力

| 出力フィールド | 説明 |
|---|---|
| event_id | `E{YYYYMMDD}_{NNN}` 形式の一意ID |
| when | ISO 8601形式のタイムスタンプ |
| status | `ok` / `error` |
| storage | 保存先（`gate/sqlite`） |

#### Event生成条件

- Event Authorityによる検証通過
- 重複Eventでないこと
- DBへの書き込みが成功すること

#### 監査対象

- 全Event（Ledger上の全記録）
- Event生成頻度の異常（重複・空白期間）
- Event ID連番の断絶

#### 禁止事項

- DBへの直接INSERT
- Event IDの手動入力
- 既存Eventの変更・削除
- Gate迂回による記録

---

### 2.2 Knowledge Gate（GATE-KNOW）

#### 責務

知識Artifactの制度的登録・参照・版管理・廃止を管理する。  
MoCKAの知識資産が制度的に維持されることを保証する。

#### 入力

| 入力フィールド | 必須 | 説明 |
|---|---|---|
| artifact_id | 必須 | BINDING_REGISTRYのArtifact ID |
| meaning | 必須 | KNOWLEDGE/DESIGN/PHASE_RECORD/REQUIREMENTのいずれか |
| institution | 必須 | 帰属Institution |
| version | 必須 | vX.Y.Z形式 |
| content_hash | 推奨 | 内容ハッシュ（改竄検知用） |

#### 検証

- ArtifactがBINDING_REGISTRYに登録済みであること
- MeaningがKnowledge Gate対象分類であること
- Institution帰属が確定していること
- 重複登録でないこと（同Artifact・同Versionの多重登録禁止）

#### Authority

- **Knowledge Authority** が保持
- 参照許可・廃止許可はKnowledge Authorityが管理
- Event Authorityと連携してEvent生成を行う

#### 出力

- Knowledge登録完了Event（Event Gate経由）
- Knowledge ID（自動採番）
- 登録Artifactの制度状態更新

#### Event生成条件

- Knowledge Gate検証通過後
- 登録・参照・廃止のいずれかのアクションが発生した場合

#### 監査対象

- 登録済みKnowledgeの有効性
- 廃止Knowledgeへの参照の存在
- Versionの断絶・重複

#### 禁止事項

- Meaning未確定ArtifactのKnowledge登録
- Institution未所属ArtifactのKnowledge登録
- Knowledge Ledgerへの直接書き込み

---

### 2.3 Module Gate（GATE-MOD）

#### 責務

システムモジュールの本番稼働への制度的な受け付け口。  
依存関係・Interface・テスト記録を確認し、制度的に健全なModuleのみを本番制度に接続する。

#### 入力

| 入力フィールド | 必須 | 説明 |
|---|---|---|
| module_id | 必須 | モジュール識別子 |
| artifact_id | 必須 | BINDING_REGISTRYのArtifact ID |
| interface_spec | 必須 | 入出力・依存関係の仕様書 |
| test_event_id | 必須 | テスト結果Eventの ID |
| dependencies | 必須 | 依存Module一覧（空の場合は空配列） |

#### 検証

- MeaningがSYSTEM_COREであること
- 全依存ModuleのBinding状態がCONNECTEDであること
- Interface定義が存在すること
- Test Eventが最低1件存在すること
- Module Registryに重複登録がないこと

#### Authority

- **PHI-OS / Institution Authority** が保持
- Module登録・廃止はPHI-OSの承認を要する
- 依存関係グラフの管理はModule Gateが担う

#### 出力

- Module登録完了Event（Event Gate経由）
- Module Registry更新
- Binding状態のCONNECTED更新

#### Event生成条件

- Module Gate検証通過後
- 登録・更新・廃止のいずれかのアクションが発生した場合

#### 監査対象

- Module Registryの整合性
- 依存関係の循環参照
- PARTIAL状態Moduleの放置期間
- Interface仕様と実装の乖離

#### 禁止事項

- テスト記録なしの本番投入
- 依存Module未登録状態での本番稼働
- Module Registryへの直接書き込み

---

### 2.4 Prompt Gate（GATE-PROMPT）

#### 責務

AIへの指示書・プロンプト・CLAUDE.mdの制度的検証と発行を管理する。  
未承認の指示書が制度システムを操作することを防止する。

#### 入力

| 入力フィールド | 必須 | 説明 |
|---|---|---|
| prompt_id | 必須 | プロンプト識別子 |
| target_ai | 必須 | 対象AIエージェント種別 |
| template_id | 必須 | 準拠テンプレートID |
| governance_approval | 必須 | 承認済みGovernance Event ID |
| scope | 必須 | 許可する操作範囲 |

#### 検証

- テンプレートへの準拠確認
- Governance承認Eventの実在確認
- スコープが制度上の許可範囲内であること
- 前回版との差分記録が存在すること

#### Authority

- **Gate Authority** が保持
- PHI-OS Constitutionの原則2（PHI-OSのみが制度を定義できる）に従い、  
  Prompt Gateの最終承認はGate Authorityの専権事項とする

#### 出力

- プロンプト発行Event（Event Gate経由）
- 承認済みプロンプトの版管理レコード

#### Event生成条件

- Gate Authority承認完了後
- 新規プロンプト発行・既存プロンプト変更時

#### 監査対象

- 発行済みプロンプトの有効期限
- 未承認プロンプトの使用検知
- プロンプトとAI行動の乖離（インシデント検知）

#### 禁止事項

- 未承認プロンプトによるコアシステム操作
- Prompt Gate迂回による指示書の直接適用
- AIへの匿名指示（発行者不明のプロンプト）

---

### 2.5 Release Gate（GATE-REL）

#### 責務

外部公開・配布物の制度的検査と承認。  
Seal・Verify Pack・Version確定を通じて、公開物の制度的健全性を保証する。

#### 入力

| 入力フィールド | 必須 | 説明 |
|---|---|---|
| artifact_id | 必須 | 対象ArtifactのID |
| version | 必須 | `vX.Y.Z` 形式 |
| seal_commit | 必須 | mocka-seal実行時のコミットハッシュ |
| verify_pack_id | 必須 | Verify PackのID |
| certification_id | 推奨 | production_certificationの認定ID |

#### 検証

- Seal実行結果が `ALL CHECKS PASSED` であること
- Verify Packが生成・存在すること
- Version形式が正規表現 `v\d+\.\d+\.\d+` に準拠すること
- 前Versionとの差分Eventが存在すること
- Human Gate承認Eventが存在すること

#### Authority

- **Version Authority** が保持
- Sealの最終承認はVersion Authorityの専権事項

#### 出力

- Release承認Event（Event Gate経由）
- Sealed Versionレコード（outbox/verify_pack/ へのBinding）
- 公開リポジトリへのプッシュ承認

#### Event生成条件

- Release Gate検証通過かつHuman Gate承認後

#### 監査対象

- Sealed Versionの改竄検知（content_hash比較）
- 未Seal状態の公開Artifactの存在
- Verify Packの有効性確認

#### 禁止事項

- `ALL CHECKS PASSED` 未確認での公開
- Verify Pack未生成での公開
- Human Gate承認なしでのpush --force

---

### 2.6 Experiment Gate（GATE-EXP）

#### 責務

実験・試験的Artifactの制度的管理。  
Experiment記録に基づき、実験の開始・評価・昇格・廃棄を制度的に管理する。

#### 入力

| 入力フィールド | 必須 | 説明 |
|---|---|---|
| experiment_id | 必須 | 実験識別子 |
| artifact_id | 必須 | 対象ArtifactのID |
| hypothesis | 必須 | 実験仮説の記述 |
| institution | 必須 | 帰属Institution（実験先） |
| expected_outcome | 必須 | 期待される結果の定義 |

#### 検証

- Hypothesisが記述されていること
- 既存CONNECTED Artifactとの重複機能がないこと（または意図的な比較実験であること）
- 実験担当Institutionが制度上定義されていること

#### Authority

- **PHI-OS** が保持（実験はPHI-OS監視下に置かれる）
- 実験からのModule昇格はModule Gateへの移行を要する

#### 出力

- Experiment登録Event（Event Gate経由）
- Experiment Registry更新
- 実験終了時：結果Event + 昇格/廃棄の判定Event

#### Event生成条件

- Experiment開始・中間評価・終了・昇格・廃棄の各時点

#### 監査対象

- 長期放置実験（PARTIAL Bindingの放置期間）
- 実験結果の未記録
- ORPHAN実験Artifactの存在

#### 禁止事項

- Hypothesis未定義での実験開始
- 実験結果の記録なしでの本番移行
- 複数Institutionへの実験Artifactの重複帰属

---

### 2.7 Document Gate（GATE-DOC）

#### 責務

制度文書・設計文書・ガバナンス文書の制度的登録・版管理・廃止。  
すべての制度文書はこのGateを通じて制度的効力を持つ。

#### 入力

| 入力フィールド | 必須 | 説明 |
|---|---|---|
| document_id | 必須 | 文書識別子（Naming Convention準拠） |
| artifact_id | 必須 | BINDING_REGISTRYのArtifact ID |
| meaning | 必須 | GOVERNANCE/DESIGN/REQUIREMENT/PHASEのいずれか |
| version | 必須 | vX.Y.Z形式 |
| approver | 必須 | 承認者（Human または Gate Authority） |

#### 検証

- Naming Convention準拠（`{PREFIX}_{NAME}_v{N}.md` 形式）
- Meaningが文書分類に適合していること
- 前版との差分または新規判定が明確であること
- 承認者の制度的権限が確認できること

#### Authority

- **PHI-OS** が保持
- Constitutionクラス文書はGate Authority承認を追加要求する

#### 出力

- Document登録Event（Event Gate経由）
- Document Registry更新
- Binding状態のCONNECTED更新

#### Event生成条件

- 新規文書登録・版更新・廃止の各時点

#### 監査対象

- 文書のNaming Convention準拠率
- 未版管理文書の存在
- Document Gate未通過文書が制度上引用されていないか

#### 禁止事項

- Naming Convention不準拠文書の制度登録
- 承認者不明文書の制度効力付与
- Document Gate迂回によるガバナンス文書の更新

---

## 第3章 Gate間接続

### 3.1 標準制度接続フロー

```
Artifact（新規または変更）
      ↓
Document Gate（Meaning確定・版管理）
      ↓
Institution帰属確定（Institution Authorityによる割当）
      ↓
Knowledge Gate（知識Artifactの場合）
      または
Module Gate（実装Artifactの場合）
      または
Experiment Gate（実験Artifactの場合）
      ↓
Release Gate（外部公開の場合）
      ↓
Event Gate（全操作のEvent記録）
      ↓
Event Ledger（append-only 永続記録）
```

### 3.2 Prompt Gateの特殊位置付け

```
制度変更の必要性（Human判断）
      ↓
Prompt Gate（指示書の制度的発行）
      ↓
AI / MCP / Runtime が指示を受領
      ↓
実作業（変更Workflow に従う）
      ↓
Document Gate または Module Gate
      ↓
Event Gate
```

### 3.3 Incident発生時のフロー

```
異常検知
      ↓
Event Gate（Incident Event の即時生成）
      ↓
Document Gate（Incident Record 作成）
      ↓
修復作業（通常Workflow へ）
      ↓
Event Gate（修復完了Event）
```

---

## 第4章 Authority Rules

### 4.1 Authorityの一意性

各Gateは単一のAuthorityによって管理される。  
Authority重複は制度違反であり、即時修復対象とする。

| Gate | 管理Authority | 委任可否 |
|---|---|---|
| Event Gate | Event Authority | 不可（PHI-OS専権） |
| Knowledge Gate | Knowledge Authority | 部分委任可（Institution限定） |
| Module Gate | Institution Authority | 委任可（登録Institution限定） |
| Prompt Gate | Gate Authority | 不可（最高位） |
| Release Gate | Version Authority | 不可（Human Gate必須） |
| Experiment Gate | PHI-OS | 部分委任可（Institution限定） |
| Document Gate | PHI-OS | 部分委任可（Institution限定） |

### 4.2 責任境界

- 各GateのAuthorityはそのGateの通過判定にのみ責任を持つ
- Gate間の接続責任はPHI-OSが負う
- Gate境界を越えた操作（例: Module Gateを通じてEvent Ledgerを変更する）は禁止

### 4.3 継承関係

```
Gate Authority（最上位・Prompt Gate管理）
    ├─ Event Authority（Event Gate）
    ├─ Knowledge Authority（Knowledge Gate）
    ├─ Institution Authority（Module Gate）
    ├─ Version Authority（Release Gate）
    └─ PHI-OS（Document Gate・Experiment Gate）
```

- 上位Authorityは下位Gate通過の停止・審査・覆しができる
- 下位Authorityは上位Authorityの決定を覆せない
- Gate Authorityのみが全Gateを横断して制度に介入できる

---

## 第5章 Compliance

### 5.1 Gate違反の定義

Gate違反とは、以下のいずれかに該当する行為である。

| 違反種別 | 説明 | 分類 |
|---|---|---|
| Gate迂回 | Gateを通らずに制度的操作を実行 | Critical |
| Authority詐称 | 持たないAuthorityで操作を実行 | Critical |
| Authority重複 | 同一操作に複数Authorityが関与 | Critical |
| Gate未通過記録 | Gate通過のEventが生成されていない | High |
| 検証スキップ | 通過条件を確認せずにGate承認 | High |
| 禁止事項実行 | 各Gate禁止事項への違反 | High |
| Naming Convention違反 | Document GateのNaming不準拠 | Medium |

### 5.2 検知方法

- **自動検知:** Compliance Runtime（将来実装）がBinding状態・Gate通過記録をリアルタイム監視
- **定期監査:** Verification Authorityによる定期Audit（BINDING_REGISTRY参照）
- **インシデント照合:** Incident Eventに含まれる違反情報の分析
- **手動報告:** 制度参加者による自己申告・相互報告

### 5.3 修復方法

| 違反種別 | 修復手順 |
|---|---|
| Gate迂回（Critical） | 即時停止 → Human Gate承認 → 制度経路で再実行 → 元の操作をShadow記録 |
| Authority詐称（Critical） | 即時停止 → Incident Record作成 → 正規Authorityによる操作の再評価 |
| Gate未通過記録（High） | 補完Event生成（遡及記録） → Document Gate経由で承認 → BINDING_REGISTRY更新 |
| 検証スキップ（High） | Gate通過の遡及再検証 → 問題あれば該当Artifactを一時SHADOW化 |
| Naming Convention違反（Medium） | Document Gate経由でArtifact名を正規化 → BINDING_REGISTRY更新 |

---

## 第6章 将来Gate拡張指針

本Architectureは以下の原則に基づき将来のGate追加を受け入れる構造とする。

### 6.1 Gate追加条件

新しいGateを追加するには以下が必要である。

1. **PHI-OS Constitutionへの記載** — Gate Authorityの承認とConstitution改定
2. **Authority割当** — 新Gateに対応するAuthorityの明確な定義（重複禁止）
3. **入力・検証・出力の完全定義** — 本文書第2章と同フォーマットで定義
4. **Event Gate連携の設計** — 全Gate通過はEvent Gateへ接続される
5. **既存Gateとの境界定義** — 既存Gateとの責務重複がないこと

### 6.2 Phase 5以降で検討されるGate候補

| Gate候補 | 目的 | 優先度 |
|---|---|---|
| Compliance Gate | Compliance Runtime実装後の自動検証Gate | High |
| Audit Gate | 監査実施・結果記録の専用Gate | Medium |
| Seal Gate | mocka-seal処理の制度的Gate化 | Medium |
| External Gate | External Systemの制度接続専用Gate | Low |

---

## 付記

本文書はMoCKA Phase 4 制度設計フェーズの成果物として策定された。  
INSTITUTION_BINDING_MAP_v1.mdのGate定義を基礎とし、PHI_OS_CONSTITUTION_v1.mdの  
Authority体系に準拠して統一設計された。

関連文書:
- PHI_OS_CONSTITUTION_v1.md — 制度憲法
- INSTITUTION_PROTOCOL_v1.md — 制度参加者共通運用規約
- INSTITUTION_BINDING_MAP_v1.md — Institution・Gate接続マップ
- BINDING_REGISTRY_v1.md — Artifact制度登録台帳

*文書バージョン: v1.0*  
*最終更新: 2026-06-16*  
*次回見直し: Compliance Runtime実装時またはPhase 5移行時*  

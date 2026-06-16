# INSTITUTION_PROTOCOL_v1.md
## MoCKA 制度参加者共通運用規約

**文書番号:** MOCKA-INST-PROTO-001  
**作成日:** 2026-06-16  
**フェーズ:** MoCKA Phase 4 — 制度実装  
**状態:** RATIFIED v1  
**上位文書:** PHI_OS_CONSTITUTION_v1.md  

---

## 概要

本プロトコルは、MoCKA制度に参加するすべての主体が遵守すべき共通運用規約を定義する。  
制度参加者の種別を問わず、本プロトコルへの適合がMoCKA制度参加の前提条件である。

---

## 第1章 対象

本プロトコルの対象となる制度参加者（Participant）は以下の通りである。

| 参加者種別 | 定義 | 例 |
|---|---|---|
| **Human** | 制度意思決定者。MoCKA制度の最終責任者 | きむら博士（nsjp_kimura） |
| **AI** | 制度執行を支援するAIエージェント | Claude、ChatGPT、Gemini、Perplexity |
| **MCP** | モデル制御プロトコル経由で動作するサーバー | mocka_mcp_server.py、ngrok MCP |
| **CLI** | コマンドラインインターフェース経由の操作主体 | mocka-seal、mocka-check |
| **Script** | 自動実行スクリプト | essence_auto_updater.py、health_check.py |
| **Runtime** | 常駐プロセス・サービス | Caliber Pipeline、COMMAND CENTER |
| **External System** | MoCKA外部から制度接続するシステム | Chrome Web Store、GitHub、Stripe |

---

## 第2章 Role と責任

### 2.1 Human

**責任:**
- 制度の最終意思決定者として、Gate Authorityへの承認/拒否を行う
- PHI-OS Constitutionの発効・改定の最終承認
- Critical・High違反への修復指令の最終判断
- 制度参加者（特にAI）の行動を監視し、逸脱を検知した場合にIncidentを起票する

**許可範囲:**
- すべてのGate通過を人間ゲートとして承認・拒否できる
- 制度上存在しないArtifact・Institution・Gateを新設できる（Gate Authority経由）
- AIを含むすべての参加者の行動を停止・修復・記録できる

**制約:**
- Humanも本プロトコルに拘束される
- Humanの作業であっても記録義務（mocka_write_event）は免除されない
- HumanはEvent Ledgerを直接改竄できない

---

### 2.2 AI

**責任:**
- 指示されたTODO・作業の制度的に正確な実行
- 作業前後のEvent記録（CHANGE_START / CHANGE_DONE）
- 制度違反の検知時の即時報告（沈黙禁止）
- UTF-8整合性を含むArtifactの健全性確認

**許可範囲:**
- 承認済みTODOの範囲内でのArtifact作成・変更
- Gate通過条件を満たすEvent生成補助
- 監査補助・違反検知・修復案の提示

**制約:**
- Human承認なしにコアシステムファイル（PHI-OS、governance/）を変更してはならない
- Event Ledgerへの直接書き込みは禁止（mocka_write_event経由のみ）
- 自らの判断でGate定義・Institution定義を変更してはならない
- 記録なき作業の実行禁止（CLAUDE.md準拠）

**AI固有の義務:**
- 制度に反する指示を受けた場合、実行前に必ず報告し確認を求める
- 自身の制度違反に気付いた場合、即時にIncident Eventを生成する
- 「AIを信じるな、システムで縛れ」原則に基づき、自らの出力を制度的に検証可能な形式で提供する

---

### 2.3 MCP

**責任:**
- 受け取ったリクエストの制度的妥当性確認
- mocka_write_eventを通じた操作記録
- ヘルスチェックへの正確な応答

**許可範囲:**
- 制度的に定義されたツール（mocka_write_event、mocka_get_overview等）の実行
- Gate通過条件を満たすリクエストの中継

**制約:**
- 制度未定義のツールを自己追加してはならない
- リクエスト元の制度参加者種別を確認せずに操作を実行してはならない

---

### 2.4 CLI

**責任:**
- 定義されたコマンド（mocka-seal、mocka-check等）の正確な実行
- 実行結果のEvent記録

**許可範囲:**
- 定義済みCLIコマンドの実行
- Ledger検証・Anchor更新等の定常運用操作

**制約:**
- CLIコマンドでEvent Ledgerを直接変更してはならない
- 承認されていないカスタムコマンドを制度実行経路として使用してはならない

---

### 2.5 Script

**責任:**
- 定常的な制度維持処理（essenceパイプライン、自動更新等）の正確な実行
- 処理結果の記録と異常時の即時通知

**許可範囲:**
- 定められたスケジュール・トリガーに基づく自動処理
- 監視・健全性チェック・データ集計

**制約:**
- Scriptは承認なしに制度定義を変更してはならない
- 異常検知時はHuman/AIへの通知なしに自己修復を行ってはならない
- 5分間隔以上の高頻度実行Scriptはパフォーマンス監視対象とする

---

### 2.6 Runtime

**責任:**
- COMMAND CENTER・Caliber Pipeline等の制度的安定稼働
- ヘルスチェックへの正確な応答
- 停止・再起動時のEvent記録

**許可範囲:**
- 定められたポート・インターフェースでのサービス提供
- Eventの中継・保存

**制約:**
- RuntimeはEvent Ledgerを直接操作してはならない
- 未承認のエンドポイントを公開してはならない
- 稼働状態をHumanに隠蔽してはならない

---

### 2.7 External System

**責任:**
- 制度的インターフェース（API・Webhook等）を通じた正確な連携
- データ送信時のフォーマット準拠

**許可範囲:**
- 制度的に承認されたAPIエンドポイントへのアクセス
- 公開Artifactの参照

**制約:**
- MoCKA内部制度（Event Ledger、governance/）への直接アクセス禁止
- 未承認データの制度Artifact化禁止

---

## 第3章 標準Workflow

### 3.1 変更Workflow

```
Human/AI が変更を計画
        ↓
CHANGE_START Event生成（mocka_write_event）
        ↓
対象Artifactの現状確認（Read / Glob / Grep）
        ↓
Document Gate または Module Gate を通じた変更承認確認
        ↓
Writeツールによるファイル変更（bashによるechoやheredoc禁止）
        ↓
UTF-8検証（JS/PYファイルの場合は必須）
        ↓
CHANGE_DONE Event生成（自動フック または 手動）
        ↓
Binding状態更新（必要に応じてBINDING_REGISTRYを更新）
```

### 3.2 承認Workflow

```
変更提案（Proposal）の作成
        ↓
Document Gate への提出
        ↓
Gate Authority（PHI-OS）による制度的検証
        ↓
Human Gate による最終承認
        ↓
承認Event生成（Event Gate経由）
        ↓
変更の実施（変更Workflow へ）
```

### 3.3 監査Workflow

```
定期監査または特別監査のトリガー
        ↓
Verification Authorityによる監査開始Event生成
        ↓
BINDING_REGISTRYの現状確認
        ↓
BINDING_GAP_REPORTの更新
        ↓
違反の有無を判定
        ↓
（違反あり）Incident Event生成 → 修復Workflow
（違反なし）監査完了Event生成 → IMPLEMENTATION_PRIORITYを更新
```

### 3.4 修復Workflow

```
違反またはGapの特定
        ↓
IMPLEMENTATION_PRIORITYの優先度を確認
        ↓
修復計画の作成とDocument Gate提出
        ↓
Human Gate承認
        ↓
修復実施（変更Workflow に従う）
        ↓
修復確認・Compliance確認
        ↓
修復完了Event生成
        ↓
BINDING_REGISTRY の Binding状態更新
```

---

## 第4章 Gate利用規則

### 4.1 必須経路

制度的操作は必ず適切なGateを経由する。  
Gateを迂回した操作は制度的効力を持たない。

| 操作種別 | 必須Gate | 根拠 |
|---|---|---|
| Artifactの制度登録 | Document Gate | Meaning確定・Binding記録が必要 |
| Eventの生成 | Event Gate | Event Authority経由が唯一正規経路 |
| 知識Artifactの参照登録 | Knowledge Gate | Knowledge Authority管理下 |
| モジュールの本番投入 | Module Gate | 依存関係・Interface確認が必要 |
| リリース・外部公開 | Release Gate | Seal・Verify Pack生成が必要 |
| 実験Artifactの登録 | Experiment Gate | Experiment Record作成が必要 |
| 制度文書の制定 | Document Gate | Governance承認が必要 |
| プロンプト・指示書の発行 | Prompt Gate | テンプレート準拠確認が必要 |

### 4.2 Gate通過の記録義務

すべてのGate通過はEventとして記録されなければならない。  
記録のないGate通過はGate通過とみなさない。

---

## 第5章 Event生成条件

Eventは以下の条件をすべて満たす場合のみ生成できる。

1. **制度的トリガーが存在する** — 制度上意味のある変化・判断・行動が発生した
2. **5W1Hが記述可能である** — Who/What/When/Where/Why/Howが特定可能である
3. **Event Gateを通過している** — Event Authorityによる検証が完了している
4. **IDが自動採番されている** — Event IDは `E{YYYYMMDD}_{NNN}` 形式で自動生成（手動禁止）
5. **重複でない** — 同一事象の重複Event生成は禁止（Recurrence検知後は別Event）

### Event生成が必須となる操作

- ファイル作成・変更・削除
- 設計・判断・採用・却下の意思決定
- インシデント発生・検知・修復
- Gate通過・拒否
- Institution変更・新設・廃止
- Seal（mocka-seal）実行
- 外部サービスへの提出・登録

---

## 第6章 Knowledge登録条件

Artifactを制度的Knowledge（Knowledge Gate通過）として登録するには以下が必要である。

1. **MeaningがKNOWLEDGE/DESIGN/PHASE_RECORD/REQUIREMENTのいずれか** である
2. **Institution帰属が確定している** — 主Institutionが BINDING_REGISTRY に記録済み
3. **Document Gateを通過している** — 版管理・Naming Convention準拠が確認済み
4. **Knowledge Gateによる受理Eventが生成されている**
5. **重複登録でない** — 同内容の既存Knowledgeとの照合が完了している

---

## 第7章 Module登録条件

Artifactを制度的Module（Module Gate通過）として本番稼働させるには以下が必要である。

1. **MeaningがSYSTEM_COREである**
2. **Interface定義が存在する** — 入出力・依存関係が文書化されている
3. **Module Registryへの登録が完了している**
4. **依存Module全てのBinding状態がCONNECTEDである**
5. **テスト記録が存在する** — 最低1件のTest Eventが記録済み
6. **Module Gate通過Eventが生成されている**

---

## 第8章 Release条件

Artifactを外部公開（Release Gate通過）するには以下が必要である。

1. **Version確定Event が存在する** — Versionが `vX.Y.Z` 形式で確定している
2. **Seal（mocka-seal）が実行されている** — `ALL CHECKS PASSED` 確認済み
3. **Verify Packが生成されている** — 検証可能な証跡パックが存在する
4. **production_certification/ による認定が完了している**
5. **Release Gate通過Eventが生成されている**
6. **Human Gate承認が取得されている**

---

## 第9章 Version管理

### 9.1 Version命名規則

```
v{Major}.{Minor}.{Patch}

Major: 制度変更・後方互換性破壊
Minor: 機能追加・Binding追加
Patch: バグ修正・Compliance修正
```

### 9.2 Version凍結規則

- Release Gate通過後のVersionは変更できない
- 変更が必要な場合は新Versionとして新たにRelease Gateを通過する
- 緊急修正（Hotfix）もRelease Gate通過を免除されない

### 9.3 Deprecation規則

- DeprecationはVersion Authorityの承認を要する
- Deprecation Event生成後、後継実装が確認されるまでARCHIVE化は行わない
- DEPRECATED状態のArtifactへの新規依存追加は禁止する

---

## 第10章 Audit参加方法

### 10.1 定期監査への参加

- 全参加者は定期監査に協力する義務を持つ
- 監査要求（Audit Request Event）を受けた参加者は48時間以内に応答する
- 監査応答には `Audit Response Event` を生成する

### 10.2 自己申告

- 制度参加者は自らの制度違反を自己申告できる（推奨）
- 自己申告によるIncident Eventは重大度を1段階軽減して扱う

### 10.3 監査結果の受け入れ

- Verification Authorityによる監査結果に制度参加者は異議を申し立てることができる
- 異議はDocument Gate経由で申し立て、Gate Authorityが最終判断を下す

---

## 第11章 Incident発生時の対応

### 11.1 検知フロー

```
異常検知（いずれかの参加者）
        ↓
即時 Incident Event 生成（event_type: INCIDENT）
        ↓
Humanへの通知（沈黙禁止 — 検知したAI/Scriptは必ず報告する）
        ↓
Incident分類（Critical/High/Medium/Low）
        ↓
Incident Record作成（docs/incidents/INC-{ID}.md）
```

### 11.2 対応フロー

```
Incident分類確定
        ↓
Critical/High: 即時停止検討 → Human Gate承認 → 修復着手
Medium/Low: 次定期修復セッションで対処
        ↓
修復実施（修復Workflow に従う）
        ↓
修復完了Event生成
        ↓
再発防止策の制度化（Document Gate経由）
        ↓
Incidentクローズ Event生成
```

### 11.3 沈黙禁止

いかなる参加者も制度上の異常を検知した場合、以下を行ってはならない。

- 検知した事実を報告せずに別の作業を継続する
- Incident Eventを生成せずに自己修復を試みる
- 「軽微だから」という判断で記録をスキップする

制度哲学の核心: **「自由を許し、必ず記録し、証明する」**

---

*文書バージョン: v1.0*  
*最終更新: 2026-06-16*  
*上位文書: PHI_OS_CONSTITUTION_v1.md*  
*次回見直し: Gate Architecture承認後またはPhase 5移行時*  

# Model Inventory (モデル台帳)

**生成日**: 2026-08-16  
**対象範囲**: docs/ai/ (claude.json, gemini.json, chatgpt.json)、docs/governance/GPT_RESTRICTIONS.md  
**分類**: INTERNAL - 監査用ドキュメント  
**注記**: Read Onlyスナップショット。事実の転記のみ。推奨・評価・改善提案は含まない

---

## 1. Claude (R02)

| 項目 | 内容 |
|------|------|
| **エージェント識別コード** | R02 |
| **権限範囲** | Documentation, Audit, Paper Lead |
| **読取権限** | All |
| **書込権限** | なし |
| **既知の制限条項** | - MoCKA Core への Human Gate 未承認変更禁止<br/>- main ブランチへの直接 merge 禁止<br/>- 全変更を mocka_write_event で記録必須 |
| **既知の未解決リスク** | なし (2026-08-16時点) |
| **最終監査日** | 2026-07-31 (Decision Ledger DC_20260731系) |
| **ステータス** | ratified |
| **出典** | docs/ai/claude.json (v1.0)<br/>Decision Ledger: DC_20260731_006 他複数<br/>MCP Startup: mocka_get_overview, mocka_get_todo, mocka_get_essence, mocka_get_guidelines |

---

## 2. Gemini

| 項目 | 内容 |
|------|------|
| **エージェント識別コード** | Adversarial Reviewer (識別コード記載なし) |
| **権限範囲** | Challenge claims, Identify weaknesses |
| **読取権限** | Architecture, Evidence, Research |
| **書込権限** | なし |
| **既知の制限条項** | - Review のみ - 実装禁止<br/>- 論理的矛盾の指摘に限定<br/>- Decision 承認権限なし |
| **既知の未解決リスク** | **RESOLVED**: INC-20260401-001 (Gemini OAuth token 混入インシデント) - 2026-04-01 発生、filter-branch により履歴削除・.gitignore 適用済み<br/>**DC_20260812系**: Provenance 継続管理方針確定(Gemini 原本取得タスク継続中) |
| **最終監査日** | 2026-08-12 (Decision Ledger AUTO_SEAL S0.5 HG-07) |
| **ステータス** | ratified (with ongoing provenance tracking) |
| **出典** | docs/ai/gemini.json (v1.0)<br/>docs/incidents/INC-20260401-001.md<br/>Decision Ledger: DC_20260812_027 (AUTO_SEAL S0.5 HG-07) |

---

## 3. ChatGPT (R01)

| 項目 | 内容 |
|------|------|
| **エージェント識別コード** | R01 |
| **権限範囲** | Design Audit, Institution Review, Paper Sub |
| **読取権限** | Architecture, Governance, Public Decisions, Evidence |
| **書込権限** | なし |
| **既知の制限条項** | - Audit のみ - 実装禁止<br/>- 全ての Decision は Human Gate 承認必須<br/>- R02 Documentation を override 禁止 |
| **既知の未解決リスク** | **STRUCTURAL DEFECT**: GPT_RESTRICTIONS.md 自動更新フローの承認ゲート未接続 (Decision Ledger DC_20260731_011 で報告)<br/>**IMPACT**: 未分析内容が混入、state file が 0 件では Fail Closed 導入で全 INC 脱落の可能性<br/>**STATUS**: 2026-07-31 裁定により移行順序(6.11.2)維持で対応中 |
| **最終監査日** | 2026-07-31 (Decision Ledger DC_20260731_011) |
| **ステータス** | ratified (with known structural defect) |
| **出典** | docs/ai/chatgpt.json (v1.0)<br/>docs/governance/GPT_RESTRICTIONS.md (生成日: 2026-07-31)<br/>Decision Ledger: DC_20260731_011 (GPT_RESTRICTIONS.md自動更新フロー構造的欠陥)<br/>Decision Ledger: DC_20260731_009, DC_20260731_010, DC_20260731_012 (関連裁定) |

---

## Summary (要約)

### エージェント一覧

| コード | 名称 | 権限 | Read | Write | 状態 | 最終監査 |
|--------|------|------|------|-------|------|--------|
| R02 | Claude | Documentation, Audit, Paper Lead | All | なし | ratified | 2026-07-31 |
| - | Gemini | Challenge, Review | Architecture等 | なし | ratified | 2026-08-12 |
| R01 | ChatGPT | Design Audit等 | Architecture等 | なし | ratified* | 2026-07-31 |

*with known structural defect in GPT_RESTRICTIONS.md auto-update flow

### 既知のリスク・インシデント

| ID | 対象 | 内容 | 状態 | 参照 |
|----|----|------|------|------|
| INC-20260401-001 | Gemini | OAuth token 混入(git履歴) | RESOLVED | docs/incidents/INC-20260401-001.md |
| DC_20260731_011 | ChatGPT/R01 | GPT_RESTRICTIONS.md 承認ゲート未接続 | OPEN (移行順序維持中) | Decision Ledger |
| INC-20260401-002 | Router | API無料枠超過エラー | RESOLVED | docs/incidents/INC-20260401-002.md |

### 監査基準適用状況

**NIST Cybersecurity Framework対応状況**:
- **Identify (ID)**: Role/Authority 台帳 → 本ドキュメント (Model Inventory)
- **Protect (PR)**: Restriction 設定 → docs/ai/*.json に明記
- **Detect (DE)**: Incident tracking → docs/incidents/ + Decision Ledger
- **Respond (RS)**: Decision レコード → Decision Ledger で全決定を記録・追跡
- **Recover (RC)**: Remediation → INC-20260401-001 (token削除) / 進行中: DC_20260731系

---

## 生成プロセス

本ドキュメントは以下の手順で生成されました (Read Only 原則遵守):

1. 役割宣言ファイル読取: docs/ai/claude.json, gemini.json, chatgpt.json
2. 制限事項ファイル読取: docs/governance/GPT_RESTRICTIONS.md
3. Decision Ledger 照合: Claude/Gemini/ChatGPT/R01/R02 関連エントリを検索
4. Incident ファイル照合: docs/incidents/ から既知リスク・修復状況を抽出
5. 表形式での統合: 事実のみを転記、推奨・評価なし

**既存ファイル変更**: なし  
**新規ファイル作成**: 本ドキュメント (1件のみ)  
**Decision Ledger 書込**: なし (Read Only)

---

## Appendix: 参照ファイル一覧

- `docs/ai/claude.json` - Claude 役割宣言 (v1.0)
- `docs/ai/gemini.json` - Gemini 役割宣言 (v1.0)
- `docs/ai/chatgpt.json` - ChatGPT 役割宣言 (v1.0)
- `docs/governance/GPT_RESTRICTIONS.md` - GPT 禁止事項台帳 (2026-07-31 生成)
- `docs/incidents/INC-20260401-001.md` - OAuth token インシデント
- `docs/incidents/INC-20260401-002.md` - API超過エラー
- Decision Ledger: DC_20260731_006, DC_20260731_009-012, DC_20260812_027 他

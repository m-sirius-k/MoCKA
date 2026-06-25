# MoCKA Phase2 — Execution Governance Layer v1.0

Status: FINALIZED（2026-06-25、博士確定済み。確定記録は`docs/governance/phase2_execution_governance_finalization_v1.md`参照。コードゼロ・実装着手・Adapter接続・Execution実行は一切行っていない）
Date: 2026-06-25
前提文書: `docs/governance/MOCKA_CODE_BINDING_HUMAN_GATE_FINALIZATION_v1.md`、
`docs/phase1/human_gate_core_snapshot_v1.md`、
`docs/audits/mocka_risk_validation_v1.md`（Phase1.5実査結果）
裁定者: 博士のみ。本文書はPhase2の構造案であり、確定裁定本体は`phase2_execution_governance_finalization_v1.md`に記録されている。

---

## 0. Phase2の定義

Phase2は「実行するかどうか」を決める層ではない。
「実行をどう安全に構造化するか」を確定する層である。

Phase2終了条件（4点すべて確定で完了）:

1. Execution Approval仕様確定
2. Rollback設計確定
3. Execution Boundary確定
4. Safety Gate設計確定

Phase3（WRITE/EXECUTE）は本文書の対象外。意図的に未到達のまま封印する。

---

## 1. Execution Approval仕様（二層構造）

判定主体は単一ではない。**機械層が提案し、Human Gate層が確定する**二層構造を採用する。

```
[Machine Layer]
  Risk Analysis（R0-R4分類）
  Integrity Check（layer分離・schema・execution汚染チェック、Phase1.5実査手順と同一）
  Recommendation: APPROVE / HOLD / REJECT（提案値のみ）

        ↓ （提案を人間に提示。ここで自動的に確定しない）

[Human Gate Layer]（博士のみ）
  Final Execution Approval: APPROVE / HOLD / REJECT / DEFER（確定値）

        ↓

Phase3 Execution（確定値がAPPROVEの場合のみ、かつPhase3着手は別途新規判断）
```

### 1.1 状態の意味（機械提案・人間確定の両方に適用）

| 状態 | 機械提案としての意味 | 人間確定としての意味 |
|---|---|---|
| APPROVE | 規則ベースでR0-R1のみ、構造矛盾なし | 博士が実行構造を許可。Phase3遷移の前提条件を満たす |
| HOLD | 規則上は許容範囲だが未確定条件あり（R2混在等） | 博士の判断が未確定、または追加情報待ち。安全側維持 |
| REJECT | R3以上検出、または境界違反 | 博士判断により構造的に実行不可と確定 |
| DEFER | 機械層では出力しない（任意・人間専用） | 博士が判定そのものを延期し、観測継続を選択 |

### 1.2 確定の原則

- 機械層の提案値は**参考情報**であり、それ自体が制度上の確定状態にはならない。
- Human Gate層の確定値のみが「Execution Approval」として記録される。
- 機械提案とHuman Gate確定が一致しない場合（例: 機械=APPROVE、博士=HOLD）も、博士の確定値が優先され、不一致自体を監査ログに残す。
- 本原則は[[feedback_flag_autonomy_risk_in_governance_design]]で過去に修正されたHuman Gate Core/Finalization分離と同型であり、Execution Approvalにも同じ分離を適用する。

---

## 2. Execution Boundary（境界確定）

| 領域 | 範囲 | 許可される操作 |
|---|---|---|
| Phase1.5まで | 観測・実査 | READ ONLY |
| Phase2 | Execution Governance設計 | DECISION ONLY（仕様・基準の確定のみ、実行物の生成なし） |
| Phase3（未到達） | Code Binding実行 | WRITE / EXECUTE（本文書の対象外、別途新規Human Gate判断が必要） |

### 2.1 重要ルール

Execution ApprovalがAPPROVE（博士確定）であっても、それは即実行を意味しない。
Phase3着手には、Phase2完了後に**別個の着手判断**を博士が行うことを要する。
本文書の確定はPhase2の完了を意味するのみで、Phase3への自動遷移トリガーにはならない。

---

## 3. Rollback設計

### 3.1 単位定義

| Level | 単位 | 用途 |
|---|---|---|
| Level 1 | File rollback | 単一ファイル変更の取り消し |
| Level 2 | Commit rollback | 関連変更群（複数ファイル）の取り消し |
| Level 3 | Snapshot rollback（Phase1 tag等） | 制度的フェーズ境界への復帰 |

### 3.2 トリガ条件（いずれか1つで発動検討）

- リスク分類でR3以上を検出した場合
- GL7系誤検知（False Positive）の再発を検出した場合
- runtime層とgovernance層の間に矛盾を検出した場合（Phase1.5実査の④構造整合性検査と同一手法で判定）

### 3.3 ロールバック方針との関係

`MOCKA_CODE_BINDING_HUMAN_GATE_FINALIZATION_v1.md` 第2項で確定済みの
「原因追跡型ロールバック」方針をそのまま継承する。固定タグへの一律ロールバックは採用しない。
Level 1-3の単位定義は、当該方針における「影響範囲の確認」ステップを具体化するものであり、
方針そのものを変更しない。

### 3.4 未確定事項（Finalization文書から継承）

Finalization文書が明記した「ロールバック記録形式が未確定」は本設計でも未解消のまま残存する。
記録形式（ログスキーマ）の確定はPhase2の範囲外とし、別途指示があるまで着手しない。

---

## 4. Safety Gate設計

### 4.1 目的

GL7問題の根本原因（「機械側が最終判断までやろうとする設計」）を再発させないため、
検出層と確定層を構造的に分離する。

```
GL7                  → 検出層（False Positive含む機械的検知のみ）
Execution Approval    → 人間確定層（博士のみ）
```

### 4.2 False Positive吸収層（設計方針のみ、実装はPhase2対象外）

- GL7等の機械検知結果は常に「提案」として扱い、確定ではない。
- 誤検知が疑われる場合は、検知結果自体を無効化するのではなく、Human Gate層へ「要確認」として上げる。
- 誤検知吸収ロジックの実装（コード）はPhase2では行わない。本節は設計方針の確定のみ。

---

## 5. Phase2終了条件チェック

| 条件 | 状態 |
|---|---|
| Execution Approval仕様確定 | 本文書1章で構造案を提示（博士確定待ち） |
| Rollback設計確定 | 本文書3章で構造案を提示（博士確定待ち） |
| Execution Boundary確定 | 本文書2章で構造案を提示（博士確定待ち） |
| Safety Gate設計確定 | 本文書4章で構造案を提示（博士確定待ち） |

**2026-06-25、博士により4条件すべて確定（APPROVE）。** Phase2 COMPLETE。確定裁定の本体は`docs/governance/phase2_execution_governance_finalization_v1.md`に記録。
本文書（DRAFT構造案）自体は確定文書ではなく、確定の前提として提示された構造案のまま保持する。

---

## 6. 最終状態（提示時点）

```
Phase1   → 完全設計済み
Phase1.5 → 実査完了
Phase2   → Execution Governance確定（COMPLETE、2026-06-25）
Phase3   → 未到達（意図的に封印、本文書の対象外。着手判断は別途新規）
```

## 関連文書

- `docs/governance/MOCKA_CODE_BINDING_HUMAN_GATE_FINALIZATION_v1.md`
- `docs/phase1/human_gate_core_snapshot_v1.md`
- `docs/audits/mocka_risk_validation_v1.md`
- `docs/governance/execution_gate_v1.md`（別件・Phase5 app.py移行チェックリスト、本文書とは対象範囲が異なる）

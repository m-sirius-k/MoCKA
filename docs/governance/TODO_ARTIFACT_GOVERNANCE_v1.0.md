# TODO Artifact Governance v1.0

適用範囲: 本文書はTODO成果物の管理・監査に適用される。Decision Policy、Knowledge Activation等の制度設計そのものを変更するものではなく、成果物の定義・証跡・検証状態を標準化することを目的とする。

位置づけ: Governance Audit Series（TODO_406/407/408）の成果物。TODO_396のような「completed判定と成果物実在の乖離」を再発させないため、TODOの成果物定義をテンプレート標準化する制度文書。Decision Policy設計（TODO_399〜405）とは独立したガバナンス改善として位置づける。

本ファイルはコードではなく制度ポリシーである。運用実績に基づき随時見直す前提とする。

## 1. 導入背景

TODO_406（2026-07-01）の棚卸しにおいて、TODO_396（phi_os/human_gate.py実装）について「成果物なし・commit不在」と誤報告した（実際は存在していた）。原因はphi_os/（MoCKAコアPythonモジュール）とPlanningCaliber/workshop/phi-os/（Chrome拡張）の混同であり、Evidence Locationが明示されていなかったことで検証が困難になった。

本制度は「completedの判定」と「成果物の所在明示」を同時に要求することで、将来の棚卸し・監査コストを下げ、AI・人間双方が一次データとして参照できる状態を維持する。

## 2. 成果物定義テンプレート v1.0

TODOのnoteまたは専用フィールドに以下4項目を記載する。形式は自由（箇条書きで可）だが、項目名は統一する。

### 2-1. Artifact Type（成果物の種類）

以下のいずれかを選択する（複数可）:

| 値 | 内容 |
|---|---|
| Design Note | 設計検討・議論の記録（chat内・note内で完結する設計） |
| Governance Document | docs/governance/配下等の正式ガバナンス文書（.md） |
| Source Code | 実装ファイル（.py / .js / .ts等） |
| Investigation Report | 監査・調査レポート（物理ファイルまたはnote内） |
| Test Report | テスト実施結果（実行ログ・スクリプト等） |
| Config / Data | 設定ファイル・データファイル（.json / .yaml等） |
| N/A | 物理成果物を持たないTODO（状態確認・承認操作等） |

### 2-2. Completion Evidence（完了の証明方法）

以下のいずれかを選択する:

| 値 | 内容 |
|---|---|
| note記載で可 | 設計内容・実施記録をnoteに記載すれば完了とみなす |
| .md必須 | docs/governance/等への物理.mdファイルが必要 |
| 実ファイル+コミット必須 | ファイル生成かつgit commitが完了していること |
| 監査レポート | 調査結果をnoteまたは.mdで整理・報告すること |
| テスト結果 | テスト実行ログまたはPASS確認が記録されていること |

### 2-3. Verification Status（検証状態）

| 値 | 意味 |
|---|---|
| Pending | 未検証（デフォルト） |
| Verified | 成果物の実在・整合性を確認済み |
| Verification Required | 次回監査時に優先確認が必要 |

### 2-4. Evidence Location（成果物・証跡の所在）

成果物のパス、リポジトリ名、コミットID、関連文書パス等を自由記述で明示する。

記載例:
- ファイル: C:/Users/sirok/MoCKA/phi_os/human_gate.py
- コミット: MoCKAリポジトリ / commit 64f8a4ae9
- 設計文書: docs/governance/DECISION_POLICY_v0.1.md
- note内完結: （本TODOのnoteフィールドに設計内容を記載）

## 3. 適用範囲と段階導入計画

### Phase 1（即時適用）: 新規TODOから適用

TODO_408以降に新規作成するTODOには、完了時のnoteに上記4項目を記載する。
強制はしない（未記載でもmocka_update_todoは動作する）が、completed判定時にくろこが4項目の記載を確認・補完する運用とする。

### Phase 2（必要最小限の遡及）: 制度系TODOのみ

以下のTODOについてのみ、次回参照時に4項目を遡及記載する:
- TODO_399 / TODO_400 / TODO_401 / TODO_404 / TODO_407

TODO_406の修正（TODO_396誤報告の訂正）はTODO_407のnoteに記録済み。

### Phase 3（正式化・将来）

運用実績が蓄積した後、本テンプレートをmocka_add_todoの推奨形式として正式化する。mocka_add_todo/mocka_update_todoのスキーマへの必須フィールド強制は本制度v1.0の範囲外とする。

## 4. v1.0で意図的に含めないもの

- Completion Authority（完了承認主体）: v2.0送り
- 既存TODO全件への一括遡及: 実施しない
- mocka_add_todo/mocka_update_todoへのスキーマ強制: 実施しない

## 5. 改訂履歴

- v1.0（2026-07-01）: TODO_408として新規作成。Governance Audit Series（TODO_406/407/408）の完結成果物。

---

TODO_408はDecision Policy設計の変更ではなく、成果物管理・監査制度を標準化する独立したガバナンス改善として扱う。本制度は新規TODOから段階的に適用し、既存成果物への遡及適用は必要最小限とする。

# MoCKA 制御マップ v1.0（決定記録・未実装）

Status: DECISION_RECORDED（本文書は意思決定の記録。コード変更は未実施）
Date: 2026-06-23
関連: `docs/governance/gl7_execution_kernel_spec_v1.md`,
MOCKA_TODO: MOCKA-TWO-LAYER-OS-BASELINE-V1, GL7-UNENFORCED-CONDITIONS-BUG

## 1. 背景

GL7-KERNEL-SPEC-DOC-V1の調査により、MoCKAには3つの独立した安全思想が
接続なしに併存していることが判明した：

- GL7（`structural/execution_governance.py`）: FORBIDDEN_EXECUTIONS/
  encoding_mismatchが定義のみで未接続。Human Gateも設計コメントのみ。
- app.py（`app.py:2151-2289`）: PREVENTION QUEUE + `/decision/approve`/
  `/decision/reject` という実在するHuman Gate相当機構。GL7とは無接続。
- PHI-OS（`phi_os/gate_validator.py`）: 意味監査層。Human Gate統合の責任を
  まだ持たない。

## 2. 検討した3モデル

- A. GL7中心モデル: GL7を唯一の実行ゲートにし、app.py Human Gateを廃止/吸収。PHI-OSは監査専用に限定。
- B. PHI-OS中心モデル: GL7=物理ゲート（最小ルール）、PHI-OS=意味ゲート（Human Gate含む統合）、app.py=実行UI層。
- C. 二重ガードモデル: GL7とapp.pyの両方が制御を持つ現状維持。整合性保証が難しく将来のバグの温床になりやすいため非推奨。

## 3. 決定（暫定）

**B（PHI-OS中心モデル）を採用方向とする。**

理由:
- Human Gate相当の実装（app.pyのprevention_queue）が既に存在し、ゼロから作る必要がない。
- GL7は現状「未接続の安全装置カタログ」であり、これ以上の責務追加（Human Gate接続等）は複雑化のリスクが高い。
- PHI-OSを「意味監査」から「意味裁定（Human Gate含む統合窓口）」へ拡張する方が、既存の二層OS構造（MOCKA-TWO-LAYER-OS-BASELINE-V1）と整合する。

**この決定はまだコードに反映されていない。** 以下4章は今後の実装方針の素案であり、着手前に個別の影響範囲確認が必要。

## 4. 役割再配分（素案・未実装）

| レイヤー | 新しい役割 | 現状からの変更 |
|---|---|---|
| GL7 (`execution_governance.py`) | 物理制約のみ（ファイルシステム/リポジトリ構造のscope/diff判定）。ABORT_CONDITIONSは実発火している4条件（grounding_not_completed/deletion_outside_scope/new_directory_detected/unexpected_file_count）に絞る | `encoding_mismatch`は削除対象、`FORBIDDEN_EXECUTIONS`はPHI-OS側へ移設または廃止を検討 |
| PHI-OS (`phi_os/gate_validator.py` + `event_gate.py`) | 意味監査に加え、Human Gate相当の承認判定をここに統合する窓口とする | 現状の事後監査(validate)に加え、承認待ち状態(pending)を持つ機構を追加する必要あり(未設計) |
| app.py (prevention_queue) | 実行UI層に縮小。承認/却下の実体判定はPHI-OS側に委譲し、app.pyはUI/通知のみを担う構成へ移行 | 現状`/decision/approve`/`/decision/reject`が直接`prevention_queue.json`を書き換えている処理を、PHI-OS経由に変更する必要あり(未設計) |

## 5. 保留事項（次の意思決定が必要）

- `FORBIDDEN_EXECUTIONS`8項目を「廃止」と「PHI-OS側への移設」のどちらにするか未決定。
- `encoding_mismatch`を本当に廃止してよいか（`mocka_check_utf8`との役割重複の可能性）は未検証。
- app.pyの`prevention_queue`は`recurrence_registry.csv`由来の「予防策提案」専用であり、GL7のDry Run承認とは対象が異なる（後者は「この変更を実行してよいか」、前者は「この再発パターンに対策を打つか」）。両者を同じHuman Gateとして統合してよいかは要検討（対象が違う可能性がある）。

## 6. 次の一手

破壊しない最小統合案（GL7を残す前提）を別途設計する。本ドキュメントはその前提となる決定記録として確定する。
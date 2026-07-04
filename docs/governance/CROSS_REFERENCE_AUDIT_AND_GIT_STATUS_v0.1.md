# Cross Reference Audit + Git状態調査 v0.1

位置づけ: くろこ作業指示（2026-07-04、「Cross Reference Audit(横方向参照監査) + Git状態調査 ― 事実収集フェーズ」最終版）に基づく事実収集フェーズの成果物。役割は制度書記官・実装調整官。評価・改善案・「すべきか」の判断は一切行っていない。収集した事実を提示した時点で作業を停止し、監査官(R01)およびきむら博士の判断を待つ。

---

## ① git履歴による経緯確認

### VOCABULARY_CONSTITUTION_v0.1.md 作成/更新履歴

| commit | 日時 | author | commit message |
|---|---|---|---|
| 738100b17 | 2026-07-03 18:04:49 +0900 | NSJP_kimura | AUTO_SEAL_50EVT |

`git log --follow`で確認できる履歴は上記1件のみ（作成・以後の更新とも同一コミットに含まれる形。個別の変更履歴は本コミット単位でしか追跡できない）。commit messageは「AUTO_SEAL_50EVT」であり、VOCABULARY_CONSTITUTION_v0.1.md固有の説明は含まれていない（自動封印処理に伴う一括コミットの一部と見られる）。

### docs/audits/配下 Human Gate監査シリーズ 各ファイルの作成日時

| ファイル | 初回コミット | 日時 |
|---|---|---|
| MOCKA_HUMAN_GATE_IDENTITY_AUDIT_v1.md | 686e7cae2 | 2026-06-25 07:04:54 +0900 |
| MOCKA_HUMAN_GATE_IDENTITY_CONSOLIDATION_AUDIT_v1.md | 686e7cae2 | 2026-06-25 07:04:54 +0900 |
| MOCKA_HUMAN_GATE_REGISTRY_AUDIT_v1.md | 686e7cae2 | 2026-06-25 07:04:54 +0900 |
| MOCKA_HUMAN_GATE_FINALIZATION_AUDIT_v1.md | 686e7cae2 | 2026-06-25 07:04:54 +0900 |
| MOCKA_HUMAN_GATE_FINALIZATION_CLOSURE_AUDIT_v1.md | 686e7cae2 | 2026-06-25 07:04:54 +0900 |
| PHASE10_3_HUMAN_GATE_DECISION_BRIEF_v1.md | af29d25e2 | 2026-06-24 09:09:22 +0900 |
| PHASE10_3_HUMAN_GATE_HEARING_PACKAGE_v1.md | af29d25e2 | 2026-06-24 09:09:22 +0900 |
| PHASE10_3_HUMAN_GATE_DECISION_PACKAGE_v1.md | cc1757f07 | 2026-06-24 07:29:22 +0900 |
| PHASE10_3_HUMAN_GATE_DEPENDENCY_AUDIT_v1.md | cc1757f07 | 2026-06-24 07:29:22 +0900 |
| PHASE10_3_HUMAN_GATE_LOAD_ANALYSIS_v1.md | cc1757f07 | 2026-06-24 07:29:22 +0900 |

10件は3コミット（`cc1757f07`2026-06-24 07:29／`af29d25e2`2026-06-24 09:09／`686e7cae2`2026-06-25 07:04）にまとまって作成されている。

### 両者の前後関係

Human Gate監査シリーズ10件（2026-06-24 07:29 〜 2026-06-25 07:04）は、VOCABULARY_CONSTITUTION_v0.1.md（2026-07-03 18:04）の作成より**約8〜9日前**にすべて作成済みであった。VOCABULARY_CONSTITUTION_v0.1.md作成時点で、Human Gate監査シリーズは既にリポジトリ内に存在していた。

---

## ② 横方向参照の網羅チェック

### 主要制度文書の「参照文書」節の有無

| 文書 | 通称 | 「参照文書」相当の節 | 節内で挙げられる文書 |
|---|---|---|---|
| REGISTRY_CHARTER_v1.0.md | KN-001 | **なし** | — |
| CATEGORY_REGISTRY_v2.0.md | KN-002 | あり（`## 6. 参照文書`、154行目） | REGISTRY_CHARTER_v1.0.md、MOCKA_TODO_ACTIVE.json内3項目 |
| TERM-001_REGISTRY_TERMINOLOGY.md | TERM-001 | あり（`## 6. 参照文書`、266行目） | REGISTRY_CHARTER_v1.0.md、CATEGORY_REGISTRY_v2.0.md、MOCKA_TODO_ACTIVE.json内1項目 |
| REGISTRY_RECORD_SPEC_v1.0.md | KN-003 | あり（`## 参照文書`、280行目） | REGISTRY_CHARTER_v1.0.md、CATEGORY_REGISTRY_v2.0.md、TERM-001_REGISTRY_TERMINOLOGY.md、GM2_REGISTRY_BASELINE_002.md |
| REGISTRY_SCHEMA_v1.0.md | KN-004 | **なし** | — |
| REGISTRY_SEMANTICS_v1.0.md | KN-005 | **なし** | — |
| REGISTRY_STATE_MODEL_v1.0.md | KN-006 | **なし** | — |
| REGISTRY_VALIDATION_v1.0.md | KN-007 | **なし** | — |
| VOCABULARY_CONSTITUTION_v0.1.md | — | **なし**（第1部で関連文書に触れるのみ、独立節ではない） | — |

備考: `data/MOCKA_TODO_ACTIVE.json`内の既存記録（REGISTRY_SERIES_V1_1_CANDIDATE、2026-07-02付）は「KN-004/005/006/007に「参照文書」節を追加し、KN-001/002/003/TERM-001と同じ様式に統一」と記載している。しかし本調査で直接確認したところ、**KN-001（REGISTRY_CHARTER_v1.0.md）にも「参照文書」節は存在しなかった**。既存記録の記述（KN-001は既に統一様式を持つ）と本調査の直接観測結果は一致しない。

### 「参照すべきだが参照していない」ペア（file:line付き）

| 対象文書ペア | 参照有無 | 参照すべき根拠 | 備考 |
|---|---|---|---|
| `docs/governance/VOCABULARY_CONSTITUTION_v0.1.md:104-110`（Approval（Human Gate）項目）→ `docs/audits/MOCKA_HUMAN_GATE_*_AUDIT_v1.md`系列（10件） | 参照なし | ①の通りHuman Gate監査シリーズは本文書より約8〜9日前に作成済みであり参照可能だった。②本文書110行目「内部下位区分 \| 特になし（human_gate.py自体は単一実装だが...）」という記述は、既存の`MOCKA_HUMAN_GATE_REGISTRY_AUDIT_v1.md`が確定している「Human Gateという名前がHG-REG-01〜04の4概念にまたがる」という所見、および本調査で確認した`phi_os/human_gate.py`と`semantic/query_engine/human_gate.py`という2つの独立実装の存在と、文言上一致しない。 | `VOCABULARY_AUDIT_EVALUATION_v0.1.md`第4節で既に指摘済みの論点（論点D）と同一事象。本項目では該当箇所をfile:lineで特定した。 |
| `docs/governance/REGISTRY_STATE_MODEL_v1.0.md:64-69`（`### 5.1 Human Gate Boundary`）→ `docs/audits/MOCKA_HUMAN_GATE_*_AUDIT_v1.md`系列 | 参照なし | 本セクションはHuman Gateの状態空間の境界を扱う内容であり、Human Gate監査シリーズ（2026-06-24/25作成）はKN-006（2026-07-02作成）より前に存在した。本セクションは`phi_os/human_gate.py`のみを実装参照先として明記しているが、`semantic/query_engine/human_gate.py`という別のHuman Gate実装、および既存監査シリーズが確定した4概念分類には触れていない。 | 本調査で新たに特定した箇所。 |
| `docs/governance/REGISTRY_SCHEMA_v1.0.md`／`REGISTRY_SEMANTICS_v1.0.md`／`REGISTRY_STATE_MODEL_v1.0.md`／`REGISTRY_VALIDATION_v1.0.md`（KN-004〜007） → KN-001/002/003/TERM-001 | 「参照文書」節そのものが存在しない | KN-002・KN-003・TERM-001は同一シリーズ内の前段文書を「参照文書」節で明示的に列挙する様式を採る。KN-004〜007は本文中で前段文書に言及する記述はあるが（例: REGISTRY_SEMANTICS_v1.0.md「4.2 TERM-001 Boundary」等の境界節）、独立した参照文書一覧の節は存在しない。 | `data/MOCKA_TODO_ACTIVE.json`内の既存記録（REGISTRY_SERIES_V1_1_CANDIDATE）が既に「v1.1で統一様式化」の候補として記録済みの事項。 |
| `docs/governance/VOCABULARY_CONSTITUTION_v0.1.md` → `docs/governance/TERM-001_REGISTRY_TERMINOLOGY.md` | 本文中で言及あり（第3部「本辞典とTERM-001との統合・改訂は...Task-Gで既に...と記録済み」）だが独立した参照節としては存在しない | 両文書とも「Registry」を扱うが、正式な相互参照節がないため、文書単体を見た場合に関連性が発見しづらい。 | 既存文書自身（VOCABULARY_PATTERN_AUDIT_TARGET_LIST_v0.1.md第3部）が統合を「次回TERM-001改訂時」に先送りする方針を記録済み。 |

---

## ③ 正本重複の履歴確認

### `docs/governance/REGISTRY_SCHEMA_v1.0.md` git履歴

| commit | 日時 | commit message |
|---|---|---|
| 996ea4194 | 2026-07-01 17:46:25 +0900 | docs(registry): add KN-004 REGISTRY_SCHEMA_v1.0 baseline |
| 22d6f55aa | 2026-07-02 07:44:39 +0900 | KN-004/KN-005: docs/governance/ への正本配置 (Human Approval Gate承認済み) |

変更頻度: 2コミット。2件目のcommit messageに「正本配置」「Human Approval Gate承認済み」と明記されている。

### `PlanningCaliber/fp/REGISTRY_SCHEMA_v1.0.md` git履歴

| commit | 日時 | commit message |
|---|---|---|
| 996ea4194 | 2026-07-01 17:46:25 +0900 | docs(registry): add KN-004 REGISTRY_SCHEMA_v1.0 baseline |

変更頻度: 1コミットのみ。初回作成（`docs/governance/`版と同一コミット）以降、更新されていない。

### 作成順・現状比較

両ファイルは同一コミット(996ea4194、2026-07-01 17:46:25)で同時に作成された。翌日(2026-07-02 07:44:39)、`docs/governance/`側のみが更新され、そのcommit messageで「docs/governance/ への正本配置」と明記されている。`diff`コマンドで両ファイルの現在の内容を比較した結果、**完全に一致（差分なし）**であることを確認した（正本配置コミットの内容がPlanningCaliber側には反映されていない状態のまま、内容自体は現時点で相違がない）。

---

## ④ 最近の変更・Git状態の調査

**変更ファイル一覧**（`git status --short`）:
```
 M data/ping_latest.json
 M interface/health_baseline.json
?? docs/governance/VOCABULARY_AUDIT_EVALUATION_v0.1.md
?? docs/governance/VOCABULARY_INDEX_SCAN_EVIDENCE_v0.1.md
?? records/master/E20260704_6644890144f34.json
```
（`M`=変更済み・未ステージ、`??`=未追跡。後者3件は本セッションでの作業により生成されたファイル）

`git diff --stat`（追跡ファイルの変更差分）:
```
 data/ping_latest.json          | 36 +++++++++++++++++++++++++++++++++++-
 interface/health_baseline.json | 16 ++++++++--------
 2 files changed, 43 insertions(+), 9 deletions(-)
```

**未プッシュコミット数**: `git rev-list --left-right --count origin/main...HEAD` の結果は `0	0`。ローカルHEADはorigin/mainと同一コミットであり、未プッシュコミットは0件。

**リモートとの差分**: 上記の通りコミット単位での差分はなし。作業ツリー上の未コミット変更（追跡2件・未追跡3件）はリモートに存在しない。

**プッシュ可能な状態かどうかの事実**: `git diff --check`（コンフリクトマーカー検出）はエラーなし（exit code 0）。現在ブランチは`main`で、リモート追跡ブランチとの間に競合状態は検出されなかった。ただし、未コミットの変更（追跡2件・未追跡3件）が存在するため、これらをコミットしない限りプッシュ対象のコミットは生成されない。

**直近のGitHub上の出来事**（`gh run list`で取得できた範囲。PR/Issueは`gh pr list`/`gh issue list`とも0件）:

| ワークフロー | 状態 | トリガー | 実行日時 |
|---|---|---|---|
| Transparency Audit | success | push (auto sync 2026-07-04T00:03:11Z) | 2026-07-04 00:03:17 |
| phase18-determinism-matrix | success | push (auto sync 2026-07-04T00:03:11Z) | 2026-07-04 00:03:17 |
| **MoCKA Global Rule Guard** | **failure** | push (auto sync 2026-07-04T00:03:11Z) | 2026-07-04 00:03:17 |
| Transparency Audit | success | push (auto sync 2026-07-03T23:53:07Z) | 2026-07-03 23:53:13 |
| phase18-determinism-matrix | success | push (auto sync 2026-07-03T23:53:07Z) | 2026-07-03 23:53:13 |

「MoCKA Global Rule Guard」ワークフロー（run ID 28688660558）の失敗詳細: ジョブ`rule-check`のステップ「Validate MoCKA Structure」が失敗（`git`プロセスがexit code 128で終了）。オープン中のPR・Issueは0件。

---

以上が収集した事実である。判断・評価・改善提案・「すべきか」の記述は一切行っていない。

## 改訂履歴

- v0.1（2026-07-04）: くろこ作業指示（Cross Reference Audit + Git状態調査）に基づき新規作成。くろこ起草。

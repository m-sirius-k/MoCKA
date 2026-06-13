# Report Truth Governance Layer (Phase 4-3) / レポート真実統治層

## EN

### Purpose
Eliminates two problems at once:
1. Code Reality vs Report Reality mismatch (handled by Phase 4-2 `reality_sync`)
2. Report-vs-report contradictions (new in this phase)

```
REPORT != TRUTH
REPORT = DERIVED + VERIFIED + GOVERNED
```

Reports are never treated as truth. They are inputs that get parsed, linked to
code evidence, checked for conflicts, and arbitrated — always in favor of code.

### Pipeline
```
Report(s)
   v
Report Parser            -> ReportClaimSet (file, report_source, line_no, claimed_status, quote)
   v
Evidence Linker          -> Evidence (from reality_sync.code_state_scanner / sync_engine)
   v
Conflict Detector         -> Conflict[] (INTRA_REPORT / INTER_REPORT / CLAIM_VS_TRUTH / OUTDATED_CLAIM)
   v
Truth Validator           -> truth_state (FIXED/BROKEN), code evidence only
   v
Arbitrator                 -> resolved Conflict[] (priority order applied)
   v
Alignment Engine           -> AlignmentDiff[] (proposed report corrections, not applied)
   v
Governance Engine          -> ReportTruthState + governance_status (PASS/FAIL)
```

### Truth Rule
Reused from Phase 4-2 (`reality_sync.truth_checker`), accessed only via
`reality_sync.sync_engine` Evidence:
```
IF code_evidence == PASS: TRUE_STATE = FIXED
ELSE:                     TRUE_STATE = BROKEN
```
No file_path without `reality_sync.sync_engine` evidence can become FIXED —
it defaults to `BROKEN (NO_EVIDENCE)`.

### Conflict Taxonomy
| Type | Meaning |
|---|---|
| INTRA_REPORT | One report makes both FIXED and BROKEN claims for the same file |
| INTER_REPORT | Two reports disagree about the same file |
| CLAIM_VS_TRUTH | The aggregated report claim disagrees with code truth |
| OUTDATED_CLAIM | A report claims FIXED but code is currently BROKEN (report is stale) |

### Arbitration Priority (absolute, never overridden)
1. Code Evidence (`code_state_scanner`: ast.parse / import)
2. Reality Sync Result (`reality_sync.sync_engine` confirmed `actual_status`)
3. Test Execution Result (`test_execution` evidence, if present)
4. Report Claim (lowest priority — always loses)

Every conflict is marked `resolved=True` with a `resolution` string explaining
which evidence source won and why. No report file is ever edited by this layer
(report override forbidden, truth override forbidden).

### Governance Rule
`governance_status = "FAIL"` if and only if any Conflict has `resolved=False`.
In the current run, all conflicts are mechanically resolved by the priority
order above, so overall governance = **PASS** — but `truth_state=BROKEN` for
files with real code defects is preserved regardless (governance PASS does
not mean "everything is fine"; it means "all conflicts were governed, not
ignored").

### CLI
```bash
python -m report_truth_governance.report_pipeline
python -m report_truth_governance.report_integration_test
python -m report_truth_governance.report_conflict_test
```

### Run results (2026-06-13)
- 23 files processed, **5/5 integration tests PASS**, **6/6 conflict-taxonomy unit tests PASS**.
- `governance_status = PASS` for all 23 files (all conflicts resolved).
- `truth_state = BROKEN` (confirmed by Phase 4-2 code evidence): `interface/router.py`,
  `interface/morphology_engine.py`, `main.py`, `interface/auto_gate.py`.
- Notable conflicts resolved:
  - `interface/router.py`: INTER_REPORT (architecture review says FIXED, follow-up says BROKEN)
    + OUTDATED_CLAIM (architecture review's FIXED claim is stale) → resolved to **BROKEN**.
  - `mocka_mcp_server.py`, `app.py`: INTER_REPORT/INTRA_REPORT contradictions → resolved to **FIXED**
    (code evidence: ast.parse OK).
  - Several files (`interface/cross_audit.py`, `interface/language_detector.py`,
    `runtime/main_loop.py`, `runtime/action_executor.py`, `scripts/ledger/ledger_verify.py`,
    `caliber/chat_pipeline/mocka_caliber_server.py`, `interface/incident_learner.py`,
    `interface/simulation_layer.py`): CLAIM_VS_TRUTH — reports say BROKEN, code is
    actually FIXED (ast.parse OK) → resolved to **FIXED**. These are the
    `FALSE_BROKEN` items already flagged as classifier noise in Phase 4-2.

### Commercial Impact Assessment (update)
- This layer does **not** change the underlying commercial verdict from the
  Phase 4-3 follow-up (`SELLABLE BUT FIX REQUIRED`). It formalizes *why*:
  the only files with `truth_state=BROKEN` are `interface/router.py`,
  `interface/morphology_engine.py`, `main.py`, and the missing
  `interface/auto_gate.py` — same set identified by Phase 4-2.
- New governance value: any future report claiming these files are "fixed"
  will be automatically flagged as `OUTDATED_CLAIM` / `CLAIM_VS_TRUTH` and
  arbitrated back to `BROKEN` until `reality_sync` evidence changes — closing
  the self-deception loop structurally rather than relying on manual review.

---

## JP

### 目的
2つの問題を同時に解消する:
1. Code RealityとReport Realityの不一致(Phase 4-2 `reality_sync`で対応済み)
2. レポート同士の矛盾(本フェーズで新規対応)

```
REPORT != TRUTH
REPORT = DERIVED + VERIFIED + GOVERNED
```

レポートは真実として扱わない。解析され、コード証拠と紐付けられ、矛盾検査を経て、
常にコード側を優先して調停される「派生情報」として扱う。

### 処理フロー
```
Report(s)
   v
Report Parser       -> ReportClaimSet (file, report_source, line_no, claimed_status, quote)
   v
Evidence Linker      -> Evidence (reality_sync.code_state_scanner / sync_engine 由来)
   v
Conflict Detector    -> Conflict[] (INTRA_REPORT / INTER_REPORT / CLAIM_VS_TRUTH / OUTDATED_CLAIM)
   v
Truth Validator       -> truth_state (FIXED/BROKEN)、コード証拠のみ
   v
Arbitrator             -> resolved Conflict[] (優先順位を適用)
   v
Alignment Engine       -> AlignmentDiff[] (レポート修正案。適用はしない)
   v
Governance Engine       -> ReportTruthState + governance_status (PASS/FAIL)
```

### Truth Rule
Phase 4-2 (`reality_sync.truth_checker`) を `reality_sync.sync_engine` 経由で
そのまま再利用する:
```
IF code_evidence == PASS: TRUE_STATE = FIXED
ELSE:                     TRUE_STATE = BROKEN
```
`reality_sync.sync_engine` のEvidenceが存在しないfile_pathはFIXEDになり得ず、
`BROKEN (NO_EVIDENCE)` がデフォルトとなる。

### Conflict分類体系
| 分類 | 意味 |
|---|---|
| INTRA_REPORT | 1レポート内で同一ファイルにFIXED/BROKEN両方の主張 |
| INTER_REPORT | 2レポート間で同一ファイルの主張が不一致 |
| CLAIM_VS_TRUTH | レポートの集約主張とコードの真実が不一致 |
| OUTDATED_CLAIM | レポートはFIXEDと主張、コードは現在BROKEN(レポートが陳腐化) |

### Arbitrationルール(絶対・上書き不可)
1. Code Evidence (`code_state_scanner`: ast.parse / import)
2. Reality Sync Result (`reality_sync.sync_engine` 確定 `actual_status`)
3. Test Execution Result (`test_execution` evidenceが存在する場合)
4. Report Claim (最下位 — 常に不採用)

全Conflictは `resolved=True` となり、どの証拠源が採用されたかを `resolution`
文字列に記録する。本層はレポートファイルを一切書き換えない
(report override禁止・truth override禁止)。

### Governanceルール
`governance_status = "FAIL"` となるのは、`resolved=False` のConflictが
1件でも存在する場合のみ。今回の実行では全Conflictが優先順位ルールにより
機械的に解決されたため、全体governance = **PASS**。ただし
`truth_state=BROKEN` のファイル(実際にコード上の欠陥がある)はgovernance
PASSであっても解消されない — 「PASS」は「矛盾が統治された」ことを意味し、
「問題がない」ことを意味しない。

### CLI実行
```bash
python -m report_truth_governance.report_pipeline
python -m report_truth_governance.report_integration_test
python -m report_truth_governance.report_conflict_test
```

### 実行結果 (2026-06-13)
- 23ファイル処理、**Integration test 5/5 PASS**、**Conflict分類体系 unit test 6/6 PASS**。
- 全23ファイルで `governance_status = PASS`(全Conflict解決済み)。
- `truth_state = BROKEN`(Phase 4-2のコード証拠で確認済み): `interface/router.py`,
  `interface/morphology_engine.py`, `main.py`, `interface/auto_gate.py`。
- 主な解決済みConflict:
  - `interface/router.py`: INTER_REPORT(架構レポートはFIXED、follow-upはBROKENと主張)
    + OUTDATED_CLAIM(架構レポートのFIXED主張は陳腐化) → **BROKEN** に確定。
  - `mocka_mcp_server.py`, `app.py`: INTER_REPORT/INTRA_REPORTの矛盾 → コード証拠
    (ast.parse OK)により **FIXED** に確定。
  - `interface/cross_audit.py`, `interface/language_detector.py`,
    `runtime/main_loop.py`, `runtime/action_executor.py`,
    `scripts/ledger/ledger_verify.py`,
    `caliber/chat_pipeline/mocka_caliber_server.py`,
    `interface/incident_learner.py`, `interface/simulation_layer.py`:
    CLAIM_VS_TRUTH — レポートはBROKENと主張、実態はFIXED(ast.parse OK) → **FIXED**
    に確定。これらはPhase 4-2で既に「分類器ノイズ(FALSE_BROKEN)」として
    指摘済みの項目と一致する。

### 商用影響評価(更新版)
- 本層によりPhase 4-3 follow-upの商用判定(`SELLABLE BUT FIX REQUIRED`)自体は
  **変わらない**。本層が形式化したのは「なぜそう判定されるか」である:
  `truth_state=BROKEN` となるのは `interface/router.py`,
  `interface/morphology_engine.py`, `main.py`, および存在しない
  `interface/auto_gate.py` のみで、Phase 4-2で特定された集合と一致する。
- 新たな統治的価値: 今後どのレポートが「これらのファイルは修正済み」と主張しても、
  `reality_sync` の証拠が変わらない限り `OUTDATED_CLAIM` / `CLAIM_VS_TRUTH` として
  自動検出され `BROKEN` へ調停される。これにより自己欺瞞の再発を
  手動レビューに依存せず構造的に防止する。

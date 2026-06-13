# Reality Sync Layer (Phase 4-2) / 現実同期ゲート

## EN

### Purpose
Closes the structural gap where "the report says fixed, but the code is not."
This layer treats **code state as the only source of truth**. Reports are
reference material only and are never trusted at face value.

```
REPORT != TRUTH
REPORT subset of VERIFIED_CODE_STATE
```

### Truth Rule
A file is `FIXED` **only if**:
- `ast.parse()` succeeds (syntax valid), AND
- if the file is import-checked (`IMPORT_TARGETS`), `import <module>` succeeds.

Everything else is `BROKEN`. No "should be fixed by design" reasoning is permitted.

### Pipeline
```
CodeStateSnapshot (code_state_scanner)
   v
ReportStateClaims (report_state_validator)
   v
DiscrepancyDetector
   v
TruthChecker
   v
SyncResult (sync_engine)
```

### Discrepancy Types
| Type | Meaning | Severity |
|---|---|---|
| NONE | Report matches reality | NONE |
| FALSE_FIXED | Report says fixed, code is broken | CRITICAL |
| FALSE_BROKEN | Report says broken, code is fine | LOW |
| MISSING_FIX | Report silent, code is broken | HIGH |
| REVERSED | Reports contradict each other | CRITICAL |
| NO_CLAIM | Report silent, code is fine | NONE |

### CLI
```bash
python -m reality_sync.sync_pipeline
python -m reality_sync.sync_integration_test
```

### Run results (2026-06-13)
- 23 files scanned (`WATCHED_FILES` in `sync_registry.py`)
- Integration test: **5/5 PASS**
- `FIX REQUIRED` (actual_status == BROKEN), confirmed by `ast.parse`/import evidence:
  - `interface/router.py` — double SyntaxError (BOM-literal at L5, invalid `def` at L128)
  - `main.py` — same BOM-literal SyntaxError at L1 (newly detected by this layer; not previously flagged)
  - `interface/morphology_engine.py` — unterminated triple-quoted string (L154-269)
  - `interface/auto_gate.py` — file does not exist
- `REVERSED` (CRITICAL) detected for `app.py`, `mocka_mcp_server.py`, `interface/router.py`,
  `interface/health_check.py`, `interface/tech_watcher.py`, `interface/morphology_engine.py`:
  the two existing reports contain mutually contradictory FIXED/BROKEN claims for these files
  in the same document set.

### Known limitation
`report_state_validator.py` uses keyword-based line classification
(`FIXED_KEYWORDS` / `BROKEN_KEYWORDS`). It over-matches on table headers, legends,
and unrelated prose containing words like "FAIL"/"未確認"/"PASS", producing some
`FALSE_BROKEN` (severity LOW) entries that are classifier noise rather than real
report errors. This does not affect `FIX_REQUIRED` (which depends only on
`actual_status`, derived purely from code). Improving claim extraction (e.g.
table-row-aware parsing) is left as future work and is itself logged as a
discrepancy-detector limitation, not silently fixed.

---

## JP

### 目的
「レポート上は修正済みだが、実コードは未修正」という構造的自己欺瞞を解消する。
本層は **コードの状態のみを唯一の真実(Truth Source)** とし、レポートは参考情報として
扱う(レポートの記述をそのまま信用しない)。

```
REPORT != TRUTH
REPORT subset of VERIFIED_CODE_STATE
```

### Truth Rule（唯一の真実判定）
以下の場合のみ `FIXED` と認定する:
- `ast.parse()` が成功する(構文が正しい)、かつ
- importチェック対象 (`IMPORT_TARGETS`) であれば `import <module>` が成功する。

それ以外は全て `BROKEN`。「設計上は直っているはず」は判定根拠として禁止。

### 処理フロー
```
CodeStateSnapshot (code_state_scanner)
   v
ReportStateClaims (report_state_validator)
   v
DiscrepancyDetector
   v
TruthChecker
   v
SyncResult (sync_engine)
```

### Discrepancy分類体系
| 分類 | 意味 | severity |
|---|---|---|
| NONE | 報告と実態が一致 | NONE |
| FALSE_FIXED | 「修正済み」と報告、実態はBROKEN | CRITICAL |
| FALSE_BROKEN | 「未修正」と報告、実態はFIXED | LOW |
| MISSING_FIX | レポート言及なし、実態はBROKEN | HIGH |
| REVERSED | レポート間で主張が矛盾 | CRITICAL |
| NO_CLAIM | レポート言及なし、実態はFIXED | NONE |

### CLI実行
```bash
python -m reality_sync.sync_pipeline
python -m reality_sync.sync_integration_test
```

### 実行結果 (2026-06-13)
- 走査対象 23ファイル (`sync_registry.py` の `WATCHED_FILES`)
- Integration test: **5/5 PASS**
- `FIX REQUIRED`（actual_status == BROKEN、ast.parse/import証跡で確定）:
  - `interface/router.py` — 二重SyntaxError（L5のBOMリテラル文字列、L128の不正な `def` 構文）
  - `main.py` — `interface/router.py` と同種のBOMリテラルによるSyntaxError（L1）。
    本層で**新規検出**（過去のレポートでは未指摘）。
  - `interface/morphology_engine.py` — 未終端のtriple-quote文字列（L154〜269）
  - `interface/auto_gate.py` — ファイル自体が存在しない
- `app.py`, `mocka_mcp_server.py`, `interface/router.py`, `interface/health_check.py`,
  `interface/tech_watcher.py`, `interface/morphology_engine.py` について `REVERSED`（CRITICAL）
  を検出: 既存2レポート内でFIXED/BROKENの主張が矛盾している。

### 既知の限界
`report_state_validator.py` はキーワードベースの行分類（`FIXED_KEYWORDS` /
`BROKEN_KEYWORDS`）を行っており、テーブルヘッダや凡例、無関係な文中の
"FAIL"/"未確認"/"PASS" 等にマッチして過剰検出する。これにより一部
`FALSE_BROKEN`（severity LOW）はレポートの実際の誤記ではなく分類器の
ノイズである可能性がある。`FIX_REQUIRED`（コードのみから導出される
`actual_status` に依存）には影響しない。Claim抽出の精度向上（テーブル行
単位の解析等）は今後の課題として残し、ここに既知の限界として明記する
（黒塗りで隠さない）。

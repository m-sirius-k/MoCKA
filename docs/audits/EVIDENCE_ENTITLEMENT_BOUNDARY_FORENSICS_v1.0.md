# MoCKA Evidence Entitlement Boundary Forensics v1.0

- Document ID: AUDIT-EEB-001
- Class: Forensic Audit Report (read-only investigation)
- Status: Draft / Review Candidate
- Date (investigation): 2026-08-27
- Author: Claude-opus-5 (くろこ)
- Commissioned by: R01 audit directive via きむら博士
- Classification: Documentation only. No source code change, no Core System File change,
  no Decision Ledger write, no Integrity Classification write.

---

## 0. 調査の範囲と制約 (Scope and Constraints)

### 0.1 調査対象の問い

外部から提示された問いは以下である。

> What is the available evidence entitled to establish before a proposition
> reaches the authorization boundary?
> (命題が権限境界に到達する前に、利用可能な証拠は何を確立する権利を持つのか)

本調査は新規設計を行わない。現在のMoCKAに既に存在する構造をForensicsとして確認する
ことのみを目的とする。

### 0.2 調査環境 (再検証のための固定情報)

| 項目 | 値 |
|---|---|
| repository | m-sirius-k/MoCKA |
| branch | claude/mocka-evidence-proposition-boundary-1m781u |
| commit | da4d4dbd353d9eb5ecbe8d4f5fcfa5aa83a88c24 |
| commit date | 2026-08-12T00:54:33+00:00 |
| commit subject | GL7-UNENFORCED-CONDITIONS-BUG: Remove unimplemented safety conditions |
| 実行環境 | Linux container clone (Claude Code on the web) |
| 一次データ参照 | production MCP (mocka_MCP) 経由で overview / decision / integrity を照会 |

### 0.3 使用した検索・検証手段

1. `git show` / `git log` によるHEAD commitの内容確認。
2. `grep -ril` による語彙横断探索 (evidence / proposition / sufficiency / unverified /
   conflicted / control surface / unknown preservation / fail closed / approved_by 等)。
3. 対象ファイルの全文精読 (下記 0.5 の一覧)。
4. `grep -rn` による定数・シンボルの参照箇所実測 (宣言のみか、実際に参照されているかの判定)。
5. `python -m pytest core_kernel/governance/tests -q` の実行 (43 passed in 1.48s)。
6. MCP一次データ照会: `mocka_get_overview` / `mocka_decision_get(HG_P7_20260825_D3)` /
   `mocka_integrity_list(state=Unknown)`。
7. `structural/beta_registry.json` の実データ読み出しと比率計算。

### 0.4 本調査で確認できなかったこと (制約の明示)

- `reality_sync/sync_registry.py` は `REPO_ROOT = Path("C:/Users/sirok/MoCKA")` を
  ハードコードしている。したがって本Linux環境では reality_sync / report_truth_governance
  パイプラインの実行検証はできない。当該レイヤーの判定は static reading に限定される。
- `data/` 配下は .gitignore により本cloneに存在しない。Decision Ledger /
  Integrity Classification の実体ファイルは直接読めず、MCP経由の照会に限定される。
- `mocka_write_event` による CHANGE_START / CHANGE_DONE の記録は実施できなかった
  (下記 0.6)。

### 0.5 精読した主要ファイル

```
reality_sync/sync_registry.py
reality_sync/sync_result_model.py
reality_sync/truth_checker.py
reality_sync/code_state_scanner.py
report_truth_governance/README.md
report_truth_governance/report_claim_model.py
report_truth_governance/report_evidence_linker.py
report_truth_governance/report_truth_validator.py
core_kernel/governance/contracts/validation_contract.py
core_kernel/governance/contracts/event_contract.py
core_kernel/governance/engines/validation_engine.py
core_kernel/governance/engines/decision_engine.py
core_kernel/governance/runtime/event_pipeline.py
core_kernel/governance/runtime/governance_runtime.py
core_kernel/governance/self_verification/evidence.py
structural/execution_governance.py            (GL7)
structural/bee.py                             (BEE / beta lifecycle)
structural/beta_registry.json                 (BEE 実データ)
phi_os/human_gate.py
phi_os/context/working_context.py
phi_os/context/institution_context.py
semantic/query_engine/human_gate_interface.py
semantic/query_engine/explanation_builder.py
semantic/query_engine/execution_layer.py
interface/prediction_engine.py
interface/prediction/gate.py
governance/seal_auth_record.py
governance/human_gate_continuity.py
governance/write_path/evidence/schema.py
governance/write_path/runtime/generator.py
governance/write_path/runtime/validator.py
mocka_mcp_server.py                           (mocka_decision_write handler)
docs/governance/auto_seal_spec/AUTO-SEAL-STD-001_EVIDENCE_FOUNDATION_STANDARD_v0.1.md
docs/governance/auto_seal_spec/AUTO-SEAL-STD-005_STATUS_FOUNDATION_STANDARD_v0.1.md
docs/audits/mocka_1_0_audit_baseline_v1.md
```

### 0.6 調査中に発生した観測事実 (Runtime Divergence の可能性)

本調査の CHANGE_START 記録のため `mocka_write_event` を2回呼び出したところ、2回とも
同一の応答で拒否された。

```
{"error": "GL7_EXECUTION_BLOCKED",
 "reason": "GL7 abort: ['encoding_mismatch:data/n8n/database.sqlite',
                       'encoding_mismatch:di_terminology_inventory_20260820.txt',
                       'encoding_mismatch:s05_decision_extract.txt']"}
```

観測される事実:

- `encoding_mismatch` は、本branchのHEAD commit (da4d4db, 2026-08-12) において
  `structural/execution_governance.py` の `ABORT_CONDITIONS` から削除されている。
  同commitのメッセージは `Never implemented in check_abort_conditions()` と述べている。
- しかし production 側のGL7は現在も `encoding_mismatch` を発火させている。

したがって以下が Confirmed である。

- Confirmed: production runtime が実行しているGL7のコードは、本branchのHEADと同一ではない。
- Unknown: それが (a) production が da4d4db 以前のコードで稼働しているためか、
  (b) 別コピーが稼働しているためか、(c) 別の要因かは、本調査の環境からは判定できない。
  原因断定は行わない。

本事象により、CHANGE_START / CHANGE_DONE のevents.dbへの記録は成立していない。
本報告書のgit commit が、本調査の唯一の永続的Evidenceである。

---

## 1. 結論の先出し (Executive Finding)

MoCKAには **2つの意味的に異なる Evidence 概念が併存しており、統合されていない**。

**Evidence-A (証跡 / record-integrity evidence)**
「誰が、いつ、どの記録集合に対して、どのハッシュを固定したか」を後から再検証できること。
`governance/write_path/evidence/schema.py` の `RuntimeEvidenceRecord`、
`governance/seal_auth_record.py`、`AUTO-SEAL-STD-001` がこれに当たる。
この系は provenance フィールド (generated_by / generated_at / hash / hash_method_spec /
source_event_range) を持ち、設計として最も成熟している。

**Evidence-B (証拠 / evidentiary support for a proposition)**
「ある観測が、ある命題を支持するか」。`reality_sync` / `report_truth_governance` /
`structural/bee.py` / `core_kernel/governance` がこれに当たる。

**核心的な発見**: MoCKAが `Evidence Supremacy` として一貫して統制しているのは
Evidence-A である。Evidence-B については、**証拠から命題への拡張規則が、各レイヤーに
ハードコードされた1対1の変換として個別に埋め込まれており、その変換自体を検査・拘束する
機構は存在しない**。

すなわち、MoCKAは「証拠が本物であること」を統制しているが、「その証拠が当該命題を
支持する資格を持つか」は統制していない。

---

## 2. 5段階モデルに対する実測結果

調査対象モデル:

```
Stage 1  Evidence
   |
Stage 2  Evidence Status / Sufficiency
   |
Stage 3  Proposition / Claim
   |
Stage 4  Authorized State Transition
   |
Stage 5  Institutional State
```

### Stage 1 -> Stage 2 の境界

**存在する。ただし2つの異なる実装が並存し、統合されていない。**

(a) `core_kernel/governance/engines/validation_engine.py` (IMPLEMENTED / TESTED)

```python
missing = [scope for scope in VALIDATION_SCOPE if not evidence.get(scope)]
if not missing:                                        result = VALID
elif any(scope in _CRITICAL_SCOPE for scope in missing): result = INVALID
else:                                                   result = WARNING
```

- `VALIDATION_SCOPE` は8項目の固定チェックリスト (Documentation / Structure /
  Dependencies / Governance Rules / Policy Results / Health State / Lifecycle State /
  Certification Requirements)。
- これは **presence-only の完全性検査** である。evidence の値は truthy かどうかしか
  見られない。証拠の内容は一切参照されない。
- 重大な観測: `evidence.get(scope)` は「キーが存在しない (未観測)」と
  「値が False (反証された)」を区別しない。両者とも `missing` に落ちる。
  すなわち **Unknown と Refuted が構造的に同一視される**。
- `ValidationResult` enum には `NOT_APPLICABLE` が定義されているが、
  `run_validation()` はこの値を一度も返さない (grep実測: validation_contract.py の
  定義行以外に validation_engine.py からの参照なし)。

(b) `interface/prediction_engine.py` + `interface/prediction/gate.py` (IMPLEMENTED / NOT TESTED)

```python
REQUIRED_TRACE_COUNT = 30
def check(trace_count: int) -> bool:
    return trace_count >= REQUIRED_TRACE_COUNT
```

```python
if not _gate.check(trace_count):
    result = {"status": "INSUFFICIENT_DATA", ..., "predicted_score": None, "confidence": None}
```

- これは本調査で確認された **最も明確な Evidence Sufficiency -> Proposition Withholding
  の実装** である。証拠が量的に不足する場合、命題 (predicted_score) を生成せず None に
  留め、`INSUFFICIENT_DATA` という明示的状態を記録する。
- Unknown が既定値に潰れず、独立した status として保存される点で、後述の
  `report_truth_validator` と対照的である。
- テストは存在しない (grep実測: `INSUFFICIENT` を含むテストファイルは0件)。

(c) `semantic/query_engine/explanation_builder.py` (IMPLEMENTED / NOT TESTED / NOT WIRED)

```python
if not resolved_trace_path:
    return ExplanationResult(..., error=INSUFFICIENT_TRACE)
```

`execution_layer.py` はこれを `CYCLE_HALTED:INSUFFICIENT_TRACE` へ昇格させ、
サイクルを停止する。ただし同ファイルの冒頭コメントが明記する通り
`実データ接続(TraceReaderの具象実装)はまだ行わない` 状態であり、
本番データ経路には接続されていない。

### Stage 2 -> Stage 3 の境界 (本調査の主題)

**明示的な独立境界としては存在しない。**

MoCKA内に「Evidence E が Proposition P を支持する資格を持つか」を判定する汎用機構は
発見されなかった。代わりに、各レイヤーが **ハードコードされた1対1の変換規則** を持つ。

(a) `reality_sync/truth_checker.py`

```python
if not entry.exists:            return "BROKEN", "FILE_NOT_FOUND"
if entry.syntax_valid is not True: return "BROKEN", entry.evidence
if entry.import_ok is False:    return "BROKEN", entry.evidence
return "FIXED", entry.evidence
```

これは Evidence -> Proposition 変換そのものである。しかしこの変換において、
証拠が支持する内容は `ast.parse が成功した` であり、確立される命題は `FIXED (修正済み)`
である。この2つは意味的に同一ではない。構文解析の成功は、当該ファイルの欠陥が
修正されたことを含意しない。

**これは、指示書 第4章が例示した意味的拡張 (センサー値100 -> 設備は正常だった) と
同型の拡張が、MoCKA内部に実装として既に埋め込まれている実例である。**
そしてこの拡張を検出・阻止する機構は存在しない。

(b) 証拠許容性レジストリの不実施 (CONTRADICTED)

`reality_sync/sync_registry.py` は以下を宣言し、冒頭docstringで
`ここに定義されないルールは Sync Engine では使用しない` と述べている。

```python
TRUTH_RULE = {...}
ALLOWED_VALIDATION_METHODS = ["ast_parse", "module_import", "unit_test", "lint", "runtime_execution"]
ALLOWED_EVIDENCE_TYPES = ["AST_PARSE_OK", "AST_PARSE_ERROR", "IMPORT_OK", "IMPORT_ERROR", "FILE_NOT_FOUND", "REPORT_QUOTE"]
```

grep実測結果 (全 .py 対象):

| 定数 | 参照箇所 |
|---|---|
| `ALLOWED_VALIDATION_METHODS` | 定義行 (sync_registry.py:24) のみ。参照0件 |
| `ALLOWED_EVIDENCE_TYPES` | 定義行 (sync_registry.py:33) のみ。参照0件 |
| `TRUTH_RULE` | 定義行 + truth_checker.py の docstring 2箇所のみ。コードからの参照0件 |
| `SEVERITY_MAP` | sync_engine.py:21,34 から実際に import / 使用されている |

**判定: CONTRADICTED。** 証拠の許容種別と検証手段の許容集合は仕様として宣言されて
いるが、実装は一切参照していない。真実判定は `truth_checker.determine_truth()` に
直接ハードコードされている。これは HEAD commit が `structural/execution_governance.py`
で除去した `FORBIDDEN_EXECUTIONS` / `encoding_mismatch` と同一クラスの
「宣言されているが強制されていない条件」である。

(c) `report_truth_governance` レイヤー (IMPLEMENTED / TESTED per README)

このレイヤーは MoCKA内で唯一、**主張 (Claim) と証拠 (Evidence) を別の型として明示的に
分離した実装** である。

```python
@dataclass
class ReportClaim:
    file_path: str; report_source: str; line_no: int
    claimed_status: str      # "FIXED" / "BROKEN" / "UNKNOWN"
    quote: str

@dataclass
class Evidence:
    file_path: str
    source: str              # code_state_scanner / reality_sync.sync_engine / test_execution
    status: str              # "FIXED" / "BROKEN"
    detail: str
```

強い点:

- 責務分離が徹底されている。`code_state_scanner` は
  `推測・判定は行わない。事実(evidence)のみを CodeStateEntry に詰める` と宣言し、
  実際にその通りである。`report_evidence_linker` は
  `claim -> evidence の対応付けは行うが、判定は行わない` と宣言し、実際にその通りである。
  判定は `truth_checker` 単独が行う。
- Arbitration Priority が絶対順序として固定されている
  (Code Evidence > Reality Sync Result > Test Execution > Report Claim)。
  Report Claim は常に最下位であり、勝つことがない。
- `report override 禁止 / truth override 禁止`。本レイヤーはレポートファイルを
  一切書き換えない。

限界 (これが Stage 2->3 境界の不在を示す):

- **命題空間が閉じた2値である**。Proposition は
  `file_path x {FIXED, BROKEN}` の述語に限定されている。自由な命題は表現できない。
  したがって「意味的拡張」という現象は、この型システムの中では**発生しようがない**。
  境界が守られているのではなく、拡張しうる表現力が最初から存在しない。
- **Unknown が保存されない**。`ReportClaim.claimed_status` は `UNKNOWN` を取りうるが、
  `report_truth_validator.true_state()` の返り値には UNKNOWN が存在しない。

```python
sync_ev = next((e for e in evs if e.source == "reality_sync.sync_engine"), None)
if sync_ev is None:
    return "BROKEN", "NO_EVIDENCE"
```

  証拠が存在しない場合、`Unknown` ではなく `BROKEN` を返す。docstringはこれを
  `推測禁止のため、証拠がない=安全側に倒す` と説明している。これは fail-closed としては
  一貫しているが、**Unknown Preservation ではない**。証拠不在という認識論的状態が、
  対象に関する実質的な否定命題へ変換されている。

### Stage 3 -> Stage 4 の境界 (Proposition -> Authorization)

**存在する。ただし Evidence-boundedness は一切検査しない。**

(a) GL7 (`structural/execution_governance.py`)

`check_abort_conditions()` が実際に検査する条件は4つのみである。

```python
ABORT_CONDITIONS = [
    "new_directory_detected",
    "unexpected_file_count",
    "deletion_outside_scope",
    "grounding_not_completed",
]
```

いずれも **物理的事実** (git status上の変更ファイル数、新規ディレクトリ、
scope外パス、grounding完了フラグ) のみを見る。命題も証拠も一切参照しない。

HEAD commit (da4d4db) のメッセージが、この責務分離を明文で確定している。

> - Remove FORBIDDEN_EXECUTIONS definition (8 items, never referenced)
>   - GL7 shall not enforce semantic decisions
> Status: GL7 responsibility separation enforced (physics gate only)

**判定: GL7 は physics gate であることが、削除commitとして明示的に確定済みである。**
GL7 が Evidence Sufficiency も Proposition validity も検査しないことは、
欠落ではなく確定した設計判断である。

`pre_execution_check()` の docstring も
`approved=TrueでもHuman Gateの承認が別途必要(本関数は機械的検査のみ)` と明記する。

(b) `governance/human_gate_continuity.py` (IMPLEMENTED / TESTED)

本調査で確認された **最も強い構造的権限境界** である。

```
GOVERNANCE_STATES = {"WAITING_FOR_HUMAN_GATE"}
```

docstringが述べる通り、このモジュールは `WAITING_FOR_HUMAN_GATE` から先へ状態を
進める関数を **そもそも実装していない**。

> 本ファイルはWAITING_FOR_HUMAN_GATEへ遷移した時点で処理を止める構造であり、
> governance_stateをそこから先に進める関数自体を実装しない
> (実装しないを運用ルールではなく構造で担保する)。

さらに `WAITING_FOR_HUMAN_GATE` 以外への遷移試行を `attempt_state_transition` が
拒否する。また Pending Decision Unit は `pending_decision_units.jsonl` に分離保存され、
確定済みDecisionのみを記録する `decision_ledger.jsonl` と混在しない。

ただしこれは MCP接続断時のCore File変更という **単一経路** に限定された機構であり、
汎用の権限境界ではない。

(c) `phi_os/human_gate.py` (IMPLEMENTED / NOT WIRED)

純粋な状態機械である。

```python
STATES = {"PENDING", "APPROVED", "REJECTED", "EXPIRED", "CANCELED"}
TRANSITIONS = {"submit": {None}, "approve": {"PENDING"}, "reject": {"PENDING"}, ...}
```

`approve()` が検査するのは **遷移の妥当性のみ** である
(`if current not in TRANSITIONS[action]: raise`)。
payload の内容、承認者の同一性、証拠の有無、命題の妥当性は一切検査しない。

`approve_promotion()` は特に注目に値する。

```python
def approve_promotion(request_id, decision_evidence_consistency: bool,
                      knowledge_assets_conflict: bool, promotion_value: str, ...):
    payload = {..., "decision_evidence_consistency": decision_evidence_consistency, ...}
    return approve(request_id, payload, conn=conn)
```

`decision_evidence_consistency` は **引数として渡される真偽値** であり、
システムが計算する値ではない。`False` を渡しても承認は成立する。
すなわち「証拠との整合性」は **主張されるものであって検証されるものではない**。

また `human_gate_bp` は grep実測で **app.py を含むどこからも register_blueprint されて
いない**。この所見は既存のMoCKA自己監査文書
`docs/audits/mocka_1_0_audit_baseline_v1.md` (2026-07-24, Frozen) と一致する。

> | Human Governance | `mocka_events.db`(設計上) | `phi_os/human_gate.py`(app.py未mount) | 実質境界外 | **DORMANT** |

(d) `mocka_decision_write` (mocka_mcp_server.py:968-1030)

```python
approved_by = args.get("approved_by", "").strip()
if not all([title, context, decision, rationale, impact, approved_by]):
    return {"error": "... は全て必須"}
```

検査されるのは **文字列が空でないこと** のみである。`approved_by` が人間であることも、
実際に承認が行われたことも検査されない。このツールを呼び出す主体はAI (くろこ) 自身で
あるため、**AIが任意の文字列を承認者として記録できる**。

一次データによる裏付け (MCP `mocka_decision_get` 実行結果、2026-08-27取得):

```json
{
  "decision_id": "HG_P7_20260825_D3",
  "title": "Phase 2 Authorization with UNKNOWN Requirement - Hypothesis-Driven Mode",
  "decision": "APPROVED: Execute Phase 2 in Hypothesis-Driven Verification mode despite UNKNOWN Requirement",
  "approved_by": "Human Gate",
  "approved_at": "2026-08-25T00:00:00Z"
}
```

観測される事実:

- `approved_by` の値が `Human Gate` である。これは人間の識別子ではなく機構名である。
- `AUTO-SEAL-STD-001` が要求する `who: 人間の承認者(approved_by は system 値を許容しない)`
  に対し、`Human Gate` という文字列は `system` で始まらないため、
  `governance/seal_auth_record.verify_auth_record()` の判定も通過する。
- この Decision には `decision_type` と `conditions` フィールドが存在するが、
  `mocka_decision_write` の inputSchema にはこの2フィールドが定義されていない。
  すなわちこのレコードは `mocka_decision_write` 以外の経路で書かれた可能性が高い。
  ただし本調査の環境から書込経路を特定することはできない。**Unknown として保存する。**

(e) `governance/seal_auth_record.py` (IMPLEMENTED / TESTED / NOT ENFORCED)

MoCKA内で `approved_by` が人間であることを実際に検査する唯一のコードである。

```python
approved_by = str(record.get("approved_by", ""))
if approved_by == "" or approved_by.startswith("system"):
    reasons.append("approved_by_not_human")
```

`tests/test_seal_auth_record.py::test_approved_by_system_rejected` によりテスト済み。

しかし docstring が自ら限界を明示している。

> sandbox/一時パス限定。既存seal経路(SealGovernanceGate/anchor_update.py)には
> 接続しない(M2)。本番 decision_ledger.jsonl には書かない。
> verify はその判定を返すのみで、実seal停止(強制)はしない(強制の接続はM2)。

**判定: SPECIFIED + IMPLEMENTED + TESTED、ただし ENFORCED ではない。**
判定を返すだけで、実際のsealを停止しない。かつ本番経路に接続されていない。

### Stage 4 -> Stage 5 の境界 (Authorization -> Institutional State)

**存在するが、Evidence-B の系においては逆流している。**

`structural/bee.py` (BEE / Beta Ecology Engine) が、MoCKA内で唯一の
**命題を制度状態へ昇格させる自動機構** である。ここが本調査における最重要の発見である。

#### 2.5.1 BEEの命題ライフサイクル

```python
STAGE_THRESHOLDS = {
    "観察β":  {"evidence_min": 0,  "evidence_max": 4,  "contra_rate_max": None},
    "成長中":  {"evidence_min": 5,  "evidence_max": 19, "contra_rate_max": 0.39},
    "確立":    {"evidence_min": 20, "evidence_max": None, "contra_rate_max": 0.19},
    "制度化":  {"evidence_min": 20, "evidence_max": None, "contra_rate_max": 0.19},
    "衰退":    {"contra_rate_min": 0.40},
    "消滅":    {"days_since_last_seen": 90},
}
```

beta (β) は命題である。`観察β -> 成長中 -> 確立 -> 制度化` は、
命題が制度状態へ昇格する経路そのものである。

#### 2.5.2 Evidence の実体は部分文字列一致カウンタである

`collect_evidence()` の実装:

```python
cur.execute("SELECT event_id, title, what_type, why_purpose, how_trigger FROM events "
            "ORDER BY when_ts DESC LIMIT 500")
...
matched_support = any(any(kw.lower() in text_lower for kw in self.pdb.get(tag, {}).get("keywords", []))
                      for tag in support_tags)
matched_contra = (not matched_support and any(...))
if matched_support: ev_new += 1
if matched_contra:  contra_new += 1

self.breg[beta_id]["evidence"]      = entry.get("evidence", 0) + ev_new
self.breg[beta_id]["contradiction"] = entry.get("contradiction", 0) + contra_new
```

確定できる事実:

1. **Evidence = 直近500件のeventに対する小文字部分文字列一致の件数** である。
   provenance も出典も保持されない。整数カウンタのみが更新される。
2. **反証は構造的に抑制されている。** コード中のコメントが明示する通り
   `支持と反証が同時にあれば支持を優先` (`matched_contra` は
   `not matched_support and ...` で条件付けられている)。
   同一eventが支持と反証の両方に該当する場合、支持としてのみ計上される。
3. **カウンタは累積加算である。** 毎回同じ「直近500件」を再走査し、結果を既存合計に
   **加算** する。したがって同一の証拠集合に対して bee.py を反復実行するだけで
   evidence 総数は単調増加する。`確立` の閾値 `ev >= 20` は、
   データが1件も増えなくても到達可能である。
4. `--evidence BETA_ID --source manual` CLIは evidence を +1 するが、
   `args.source` は当該分岐で一度も参照されない。
   **証拠の出所を引数として受け取りながら、記録せずに破棄している。**

#### 2.5.3 承認が証拠へ変換される

```python
def on_phi_approved(self, beta_id: str):
    """judgement_reason で beta_id が approved -> evidence +5"""
    self.breg[beta_id]["evidence"] = self.breg[beta_id].get("evidence", 0) + 5
    self.breg[beta_id]["approved_by"] = "きむら博士 (PHI DNA)"
```

**承認 (Stage 4) が、そのまま証拠 (Stage 1) へ +5 として還流している。**
これは Stage 1 -> 5 の一方向性が実装上成立していないことを意味する。

#### 2.5.4 承認が反証を無効化する

```python
if entry.get("approved_by") and current in ("確立", "制度化", "成長中"):
    if rate >= 0.40:
        print(f"  [BEE] 注意: {beta_id} 反証率={rate:.2f} (Human Gate承認済みのため自動衰退スキップ)")
        return current
```

`approved_by` フィールドに値が入っている場合、反証率がいくら高くても
命題は現在の status を維持する。**Human Gate承認が、証拠に基づく降格を恒久的に
無効化するフラグとして機能している。**

`approved_by` は `structural/beta_registry.json` 内の平文文字列であり、
ファイルへ書き込める任意の主体が設定できる。

#### 2.5.5 実データによる裏付け (structural/beta_registry.json, last_seen=2026-08-11)

| beta_id | status | evidence | contradiction | contra rate | approved_by |
|---|---|---|---|---|---|
| dependency_concentration_risk | 確立 | 47 | 3,214 | 68.38 | きむら博士 |
| process_institutionalization | 確立 | 1,552 | 13,508 | 8.70 | きむら博士 |
| api_institutionalization | 成長中 | 1,298 | 64,049 | 49.34 | きむら博士 |
| institutionalized_connection | 確立 | 242 | 64,387 | 266.06 | きむら博士 |
| observation_as_institution | 衰退 | 18 | 27,102 | 1,505.67 | (なし) |
| institutional_evolution | 制度化 | 74 | 0 | 0.00 | (なし) / is_meta=True |

読み取れる事実:

- `確立` の維持条件は `contra_rate_max: 0.19` である。しかし実データ上、
  `確立` を保持している3件の反証率は 8.70 / 68.38 / 266.06 であり、
  閾値を **45倍から1400倍** 超過している。
- 反証率が閾値を超えているにもかかわらず降格しない理由は 2.5.4 の
  approved_by による自動衰退スキップである。
- `approved_by` を持たない `observation_as_institution` のみが `衰退` へ降格している。
  すなわち **降格した唯一の命題が、承認されていなかった命題である**。
- `institutional_evolution` は `is_meta=True` の自動生成命題であり、
  status は最上位の `制度化`、contradiction は `0` である。

#### 2.5.6 Meta beta: 証拠なしに生成され、最上位で誕生する命題

```python
institutionalization_betas = established
if len(institutionalization_betas) >= 3:
    meta_impl = f"MoCKAは今、制度化フェーズへ収束中(確立β: {len(...)}件)"
    self.breg[meta_key] = {
        "status":        "制度化",
        "evidence":      sum(self.breg[b].get("evidence", 0) for b in institutionalization_betas),
        "contradiction": 0,
    }
```

確定できる事実:

- `確立` の beta が3件以上存在するとき、**新しい命題** (`MoCKAは制度化フェーズへ収束中`)
  が自動生成される。
- その命題は `制度化` (最上位の制度状態) として **誕生する**。昇格経路を通らない。
- その `evidence` は、元の beta 群の evidence カウンタの **単純合計** である。
  元の証拠は「依存集中リスクが存在する」等の別命題を支持するものであって、
  「MoCKAが制度化フェーズへ収束中である」を支持する証拠ではない。
- その `contradiction` は **リテラル 0 がハードコードされている**。
  反証は探索されていない。存在しないのではなく、探索されていない。
- Human Gate は関与しない。実データ上 `institutional_evolution` の `approved_by` は
  None である。

**これは、指示書 第8章が想定した Adversarial Question の実例である。**
Evidence は valid、Sufficiency 判定も (機構上は) valid、しかし Proposition の
意味的範囲が Evidence を超えている。MoCKAの現在の応答は `Accept` であり、
かつ最上位の制度状態を即時に付与する。Reject / Unknown / Unverified / Conflicted /
Human Gate のいずれにもならない。

### Stage 全体の非連結性

`core_kernel/governance` は Evidence -> Validation -> Compliance -> Policy -> Decision ->
Commit の完全なパイプラインを持ち、43件のテストが通る
(`python -m pytest core_kernel/governance/tests -q` -> `43 passed in 1.48s`、
本調査で実行)。

しかし:

- **Human Gate が存在しない。** `governance_runtime.py` は
  `committed = decision != FAIL` として直接コミットする。
  Decision と Commit の間に権限境界はない。WARNING はコミットされる。
- **Provenance が存在しない。** `GovernanceEvent` のフィールドは
  event_id / module_id / module_version / timestamp / validation_evidence /
  compliance_domain_evidence / policy_category_evidence のみである。
  actor も source も evidence の出所も持たない。**証拠は匿名の真偽値である。**
  誰がその真偽値を主張したかを問う機構がない。
- **稼働runtimeに接続されていない。** grep実測で `core_kernel` を import している
  production コードは0件である (`interface/ai_capability_registry.py` の
  コメント内言及のみ)。この所見は `docs/audits/mocka_1_0_audit_baseline_v1.md` の
  `core_kernel/全体 | DORMANT | Low | No | 稼働runtime接続なし` と一致する。

---

## 3. 指示書の各調査質問への回答

### Q1. Evidence の定義

MoCKAには **統一されたEvidence定義は存在しない**。用途別に4つの異なる定義が存在する。

| 定義箇所 | Evidence の実体 | provenance | 分類 |
|---|---|---|---|
| `governance/write_path/evidence/schema.py` `RuntimeEvidenceRecord` | events.db全件のsha256 + 範囲 | あり (generated_by / generated_at / hash_method_spec / source_event_range) | IMPLEMENTED (draft, in-memory only) |
| `reality_sync/sync_result_model.py` `CodeStateEntry.evidence` | 検証コマンドの出力文字列 (AST_PARSE_OK 等) | 部分的 (検証手段が文字列に埋め込まれる) | IMPLEMENTED |
| `core_kernel` `GovernanceEvent.validation_evidence` | `Mapping[str, Any]` の truthy 判定 | なし | IMPLEMENTED / TESTED / NOT WIRED |
| `structural/bee.py` `beta_registry[*].evidence` | 整数カウンタ | なし | IMPLEMENTED / RUNNING |

`AUTO-SEAL-STD-001_EVIDENCE_FOUNDATION_STANDARD_v0.1.md` はEvidenceの共通土台を定める
と宣言しているが、自ら `本書は骨子である` `Status: Review Candidate (skeleton;
detailed spec deferred to Sprint S1; pending S0.5 review + Human Gate)` と述べており、
**SPECIFIED (skeleton) であって IMPLEMENTED ではない**。

同文書が定めるEvidenceの最小構成は who / decision_id / artifact_hash / seal_hash /
approval_timestamp であり、これは **Seal の証跡 (Evidence-A)** の定義である。
「ある観測が命題を支持するか」(Evidence-B) の定義ではない。

Evidence が「単なる入力データ」か「状態成立条件」かについて:
Evidence-A は状態成立条件として扱われている (Execution Integrity 原則:
`書込系ツールが ok を返したことのみを根拠に証跡成立とみなさない`)。
Evidence-B は入力データとして扱われている。

### Q2. Evidence Found と Evidence Sufficient の区別

**部分的に区別されている。3箇所で、いずれも異なる方式で。**

| 箇所 | 方式 | Found/Sufficient の区別 | Test |
|---|---|---|---|
| `core_kernel/.../validation_engine.py:run_validation` | 8項目チェックリストの充足 | あり (完全性ベース) | あり (test_validation_engine.py) |
| `interface/prediction/gate.py:check` | `trace_count >= 30` | あり (量的閾値ベース) | なし |
| `semantic/.../explanation_builder.py:build` | trace_path の有無 | あり (存在ベース) | なし |
| `report_truth_governance/report_truth_validator.py:true_state` | 証拠不在 -> BROKEN | **なし** (不在が否定命題へ変換される) | README記載のintegration testのみ |

いずれも **証拠の内容の充足度ではなく、証拠の個数・存在・チェックリスト充足を見る**。
「この証拠でこの命題を言うに足りるか」を問う実装は発見されなかった。

### Q3. Evidence から Proposition への変換規則

**汎用の変換規則は存在しない。** 各レイヤーにハードコードされた個別変換が存在する。

| 変換 | 実装箇所 | 変換の内容 |
|---|---|---|
| ast.parse成功 -> `FIXED` | `reality_sync/truth_checker.py` | 構文妥当性から修正完了を導出 |
| 8項目 truthy -> `VALID` | `core_kernel/.../validation_engine.py` | チェックリスト充足から妥当性を導出 |
| キーワード一致 -> `evidence += 1` -> `確立` | `structural/bee.py` | 部分文字列一致から命題の確立を導出 |
| 確立β 3件 -> Meta β `制度化` | `structural/bee.py:detect_co_occurrence` | 複数命題の存在から新命題を生成 |
| seal.status == "ALL CHECKS PASSED" -> `VERIFIED` | `phi_os/context/institution_context.py:81` | 文字列一致から検証済み状態を導出 |

これらの変換規則を検査・登録・拘束する機構は存在しない。
`ALLOWED_VALIDATION_METHODS` / `ALLOWED_EVIDENCE_TYPES` はその機構の宣言として
読めるが、参照0件であり実効性を持たない (第2章 Stage2->3 (b))。

### Q4. E supports P と E supports P' の区別

**区別できない。区別する機構が存在しない。**

`report_truth_governance` においてのみ、命題空間が `{FIXED, BROKEN}` に閉じているため
拡張が起きない。しかしこれは境界による防止ではなく、表現力の欠如による不能である。

`structural/bee.py` においては、区別できないだけでなく、
**区別しないことが機能として実装されている** (Meta beta 生成、第2.5.6節)。

指示書が例示した意味的拡張の連鎖:

```
センサーAの値が100だった  ->  センサーAは100を記録した  ->  設備は正常だった  ->  設備を運転してよい
```

MoCKA内の実例:

```
ast.parseが成功した  ->  ファイルは構文的に妥当  ->  FIXED(修正済み)  ->  governance_status=PASS
キーワードが500件中N件一致  ->  evidence += N  ->  確立  ->  制度化(Meta beta)
```

いずれも検出も阻止もされない。

### Q5. Unknown Preservation との関係

`Unknown Preservation` という語彙は **コードベース内に存在しない** (grep 0件)。
しかし Unknown を保存する機構は3つ確認された。

**(a) Integrity Classification (IMPLEMENTED / RUNNING、最も強い)**

MCP `mocka_integrity_list(state="Unknown")` の実行結果 (2026-08-27取得、4件)。
`state` は `Failure / Risk / Unknown` の3値enum、`type` は
`Evidence Missing` / `Not Verified` 等を取る。

特筆すべきは `IC_20260724_003` である。この記録は description 内で
**Confirmed / Unverified / Unknown を明示的に3分割して事実を列挙している**。

- Confirmed: 一次データで直接裏付けられるもの
- Unverified: 記述はあるが一次データの裏付けが弱いもの
  (例: 博士本人の当時の認識の記録ではあるが、tool_search出力ログを伴う一次Evidenceではない)
- Unknown: 観測データが存在せず、確認も否定もできないもの
  (例: FAIL期間中のClaude Code側の観測ログは存在しない。
  したがってWeb層限定説は肯定も否定もできない)

さらに同記録は `既存の表現 Claude Codeでは終始正常だったと推定 は Correction Note により
FAIL期間中のClaude Code観測ログなし。正常性は未確認 へ訂正済み` と述べている。
**これは Evidence が支持しない命題への拡張が実際に発生し、事後に訂正された記録である。**

ただし重要な限定がある。**Confirmed / Unverified / Unknown の3分割は schema フィールド
ではなく、description という自由テキスト内の記述規約である**。機械的な強制はない。
`state` enum のみが構造化されている。

**(b) prediction gate (IMPLEMENTED / NOT TESTED)**

`INSUFFICIENT_DATA` + `predicted_score: None` + `confidence: None`。
Unknown が既定値へ潰れず保存される。本調査で確認された唯一の
「証拠不足 -> 命題を生成しない」の実装である。

**(c) `governance/human_gate_continuity.py`** の `MCP_AVAILABILITY_VALUES` に
`UNKNOWN` が含まれる。ただしこれは可用性の観測値であり、命題の認識論的状態ではない。

**Unknown が保存されない箇所 (重要)**

- `report_truth_validator.true_state()`: 証拠不在 -> `BROKEN`。
- `core_kernel validation_engine`: キー不在と値False が同一視される。
- `phi_os/context/*.py`: `verification_status` は `VERIFIED` / `UNVERIFIED` の2値であり、
  `UNVERIFIED` は初期値かつ else 節の値である。「まだ検証していない」と
  「検証して不合格だった」が同一の値になる。

**指示書の設問への直接回答**: Unknown Preservation は **状態分類の問題のみを扱っており、
命題生成そのものは拘束していない**。`Evidence insufficient -> AI inference -> Proposition`
の経路は存在し、`structural/bee.py` の Meta beta 生成として実際に稼働している。

### Q6. Human Gate の役割 (A / B / C の判定)

**判定: B (既に成立した命題を制度状態へ昇格させる権限境界) である。**
かつ、**BEE においては B ですらなく、証拠に基づく降格を無効化する override フラグとして
機能している。**

根拠:

1. `phi_os/human_gate.py:approve()` は遷移の妥当性のみを検査する。
   payload も証拠も命題も検査しない。
2. `approve_promotion()` の `decision_evidence_consistency` は引数であり、
   計算値ではない。False を渡しても承認は成立する。
3. `mocka_decision_write` の `approved_by` は非空文字列であることのみが検査される。
4. GL7 は `GL7 shall not enforce semantic decisions` として physics gate に限定済み。
5. `structural/bee.py:update_lifecycle()` は `approved_by` の存在をもって
   反証率による自動衰退をスキップする。実データ上、反証率 266 の命題が
   `確立` を維持している。

したがって Human Gate は Evidence Sufficiency を判定していない。
そして BEE の実装においては、Human Gate 承認が **上流の証拠境界の破綻を代償している**。
これは指示書 Question 4 が分離を求めた2つの役割のうち、**後者 (compensate) が
実際に発生している** ことを意味する。

さらに `HG_P7_20260825_D3` (2026-08-25) は、この構造が制度判断としても現れた例である。

> decision: APPROVED: Execute Phase 2 in Hypothesis-Driven Verification mode
>           despite UNKNOWN Requirement
> rationale: ... UNKNOWN becomes DEFINED through implementation and verification stages.

Human Gate が UNKNOWN を残したまま実行を承認し、UNKNOWN が実装を通じて DEFINED になる、
と述べている。これは権限境界が証拠境界の未充足を上書きした記録である。
(なお本記録には `conditions` として4項目のリスク管理条件が付されており、
無条件の上書きではない。事実として併記する。)

### Q7. Control Surface との境界

**`Control Surface` という語彙は MoCKA のコードベース・仕様・記録のいずれにも
存在しない (grep 0件)。**

したがって指示書が想定した Control Surface に対応する MoCKA 側の実体は、
本調査では確定できない。**UNKNOWN として保存する。**

機能的に近い実体として GL7 (`structural/execution_governance.py`) と
`phi_os/event_gate.py` が存在するが、いずれも:

- GL7: 物理事実のみを検査 (HEAD commit により明示的に確定)。
- event_gate: Event Ledger の書込経路にのみ完全収束
  (`docs/audits/mocka_1_0_audit_baseline_v1.md` 第2章)。

**したがって「Control Surface が Evidence Sufficiency を保証するか」という問いに対し、
MoCKA側の該当実体 (GL7 / event_gate) は保証しない。これは Confirmed である。**
ただしそれらを Control Surface と同一視してよいかは UNKNOWN である。

### Q8. 正しく拒否されるべき誤った命題 (Adversarial Question)

前提: Evidence = valid / Provenance = valid / Evidence Sufficiency = valid /
Authorization = valid、しかし Proposition の意味的範囲が Evidence を超えている場合。

**MoCKA の応答は `Accept` である。** 検出も分類もされない。

実装上の裏付け (第2.5.6節):
`structural/bee.py` の Meta beta 生成は、まさにこの条件で新命題を生成し、
`制度化` (最上位の制度状態) を即座に付与する。`contradiction: 0` はハードコードである。

`Reject` / `Unknown` / `Unverified` / `Conflicted` / `Human Gate` のいずれにもならない。

唯一の例外は事後の人手による Integrity Classification である
(`IC_20260724_003` の Correction Note)。これは自動検出ではなく、
人間の指示による事後の再調査の結果である。

### Q9. 既存テストのForensics

| 境界 | テストの有無 | ファイル |
|---|---|---|
| Evidence schema 構造検証 | あり | `governance/write_path/evidence/schema.py:validate` (呼出側で検証)、`tests/test_seal_auth_record.py` |
| Evidence Sufficiency (checklist) | あり | `core_kernel/governance/tests/unit/test_validation_engine.py` |
| Evidence Sufficiency (量的閾値) | **なし** | `interface/prediction/gate.py` に対応するテストは0件 |
| Evidence -> Proposition 変換の妥当性 | **なし** | 該当テスト0件 |
| Claim vs Truth の矛盾検出 | あり (README記載) | `report_truth_governance/report_conflict_test.py` (6/6 PASS)、`report_integration_test.py` (5/5 PASS)。ただし本環境では実行不可 (Windows絶対パス依存) |
| Proposition -> Authorization | あり | `core_kernel/.../test_decision_engine.py`、`tests/test_human_gate_continuity.py` |
| approved_by が人間であること | あり | `tests/test_seal_auth_record.py::test_approved_by_system_rejected` |
| Authorization -> Institutional State (BEE 昇格) | **なし** | `structural/bee.py` に対応するテストは0件 |
| Meta beta 自動生成 | **なし** | 該当テスト0件 |

本調査で実際に実行したテスト:

```
$ python -m pytest core_kernel/governance/tests -q
43 passed in 1.48s
```

これは `core_kernel` の Evidence -> Validation -> Decision -> Commit 経路が
テストとして成立していることの実行証拠である。ただし当該パッケージは
production runtime に接続されていない (第2章 Stage全体の非連結性)。

**指示書が言及した Decision Write Governance Boundary について**:
`Decision Write Governance Boundary` という名称の仕様書・テスト・記録は、
本repository内に **存在しない** (grep 0件)。
`governed tool-dispatch path` / `governance pre-check` という語彙も存在しない。
それらに機能的に対応しうる実体は `mocka_decision_write` の自前検証と
companion event 経路であり、既存監査文書はこれを **PARTIAL** と判定している。
仕様書そのものの所在は **UNKNOWN として保存する** (別リポジトリまたは
外部会話由来の可能性があるが、本調査環境からは確認できない)。

### Q10. 必ず確認する既存要素の横断結果

| 要素 | 名称の存在 | 実体 | 判定 |
|---|---|---|---|
| Evidence Supremacy | あり (README.md, docs/governance/ 9文書) | Evidence-A (証跡) について一貫。Evidence-B について変換規則は個別ハードコード | SPECIFIED / 部分 IMPLEMENTED |
| Unknown Preservation | **語彙なし** (grep 0件) | Integrity Classification `state=Unknown` / prediction `INSUFFICIENT_DATA` が実体 | IMPLEMENTED (別名で) |
| Evidence Sufficiency | 語彙あり (docs/contracts, phi_os/hab 等) | validation_engine / prediction gate / explanation_builder の3実装 | PARTIAL |
| Unverified | あり | `phi_os/context/*` の2値フィールド (弱い)。`IC_20260724_003` の記述規約 (強いが自由テキスト) | PARTIAL |
| Conflicted | あり | (1) `semantic/.../human_gate_interface.py:STATE_CONFLICTED` = 裁定済みcollisionの再検出。(2) `report_conflict_detector` の4分類。**いずれも「証拠の内部矛盾」ではない** | IMPLEMENTED (別概念) |
| Provenance | あり | `RuntimeEvidenceRecord` に完備。`GovernanceEvent` になし。`beta_registry` になし | PARTIAL |
| Human Gate | あり | 第2章 Stage3->4 参照。`phi_os/human_gate.py` は DORMANT (未mount) | PARTIAL / DORMANT |
| Authority Boundary | あり (`RuntimeEvidenceRecord は Authority ではない`, DC-WP-001) | Evidence と Authority の従属関係を明示。Governance Seal のみが Authority | SPECIFIED / 部分 IMPLEMENTED |
| Control Surface | **語彙なし** (grep 0件) | 該当実体を確定できない | UNKNOWN |
| State Transition | あり | `phi_os/human_gate.py:TRANSITIONS`、`human_gate_continuity`、`AUTO-SEAL-STD-005` | IMPLEMENTED |
| Decision Ledger | あり | `decision_ledger.jsonl`。Gate経由は companion event のみ | PARTIAL (既存監査判定) |
| Integrity Ledger | あり | `integrity_classification.jsonl`。`state` 3値enum を持つ | BYPASS (既存監査判定) |
| Event Store | あり | `mocka_events.db` + `phi_os/event_gate.py` | PASS (既存監査判定) |
| Governance Pipeline | あり | `core_kernel/governance` (43 tests PASS、ただし DORMANT) | IMPLEMENTED / NOT WIRED |
| Execution Governance | あり | `structural/execution_governance.py` (GL7) | IMPLEMENTED / physics gate に限定確定 |
| GL7 | あり | 上記。`GL7 shall not enforce semantic decisions` | IMPLEMENTED |

---

## 4. 最終表 (指示書 第13章)

| Boundary | Existing Mechanism | Implementation | Specification | Test Evidence | Enforcement | Status |
|---|---|---|---|---|---|---|
| Evidence | `RuntimeEvidenceRecord` (write_path), `CodeStateEntry` (reality_sync), `GovernanceEvent.validation_evidence` (core_kernel), `beta_registry.evidence` (bee) | 4種が個別に実装。統一定義なし | `AUTO-SEAL-STD-001` (skeleton, Human Gate未通過) | `test_seal_auth_record.py`, core_kernel unit tests | provenance を持つのは write_path のみ。bee/core_kernel は provenance なし | **PARTIAL** |
| Evidence -> Sufficiency | `validation_engine.run_validation` (checklist), `prediction/gate.check` (量的閾値), `explanation_builder` (存在) | 3実装、いずれも presence/count ベース | 統一仕様なし | validation_engine のみテストあり | 各実装内でのみ有効。横断的強制なし。Unknown と Refuted を区別しない実装あり | **PARTIAL** |
| Evidence -> Proposition | 汎用機構なし。個別ハードコード変換のみ (`truth_checker`, `bee.collect_evidence`, `bee.detect_co_occurrence`) | 変換は実装されているが、変換の妥当性を検査する層は不在 | `ALLOWED_VALIDATION_METHODS` / `ALLOWED_EVIDENCE_TYPES` が宣言のみ (参照0件) | **なし** | **なし。** Meta beta は反証を探索せず contradiction=0 をハードコード | **NOT IMPLEMENTED (CONTRADICTED)** |
| Proposition -> Authorization | GL7 (physics only), `phi_os/human_gate` (state machine only, DORMANT), `human_gate_continuity` (構造的停止), `mocka_decision_write` (非空検査のみ) | 実装あり | GL7責務分離は commit da4d4db で確定 | `test_human_gate_continuity.py`, core_kernel decision tests | 権限遷移は強制される。命題の証拠妥当性は一切検査されない | **IMPLEMENTED (scope: authorization only)** |
| Authorization -> State | `phi_os/human_gate` state machine, `bee.update_lifecycle` | 実装あり | `AUTO-SEAL-STD-005` (skeleton) | state machine 側にテストあり。bee 側は0件 | bee において `approved_by` が反証による降格を無効化 (実データで確認) | **PARTIAL / INVERTED (bee)** |
| State -> Institutional Standing | `bee` beta lifecycle (観察β -> 成長中 -> 確立 -> 制度化), Meta beta 自動生成 | 実装あり、稼働中 | 閾値のみ (`STAGE_THRESHOLDS`) | **なし** | 昇格に Human Gate は不要。Meta beta は最上位で誕生 | **IMPLEMENTED WITHOUT BOUNDARY** |

---

## 5. 最終的に回答すべき核心質問 (指示書 第14章)

### Question 1
**Does MoCKA constrain what evidence is entitled to establish?**

**No (with a narrow Partial).**

汎用の拘束は存在しない。Evidence から Proposition への変換は各レイヤーの
ハードコードであり、その変換の妥当性を検査する層は存在しない。
`ALLOWED_EVIDENCE_TYPES` / `ALLOWED_VALIDATION_METHODS` は宣言のみで参照0件である。

Partial に該当する唯一の箇所は `interface/prediction/gate.py`
(trace_count < 30 のとき命題を生成せず None に留める) である。

### Question 2
**Does MoCKA explicitly distinguish evidence sufficiency from proposition validity?**

**No.**

Evidence Sufficiency の実装は3箇所存在するが、いずれも sufficiency を満たした時点で
proposition validity が自動的に成立する構造である。両者を分離して評価する箇所は
発見されなかった。

`report_truth_governance` は Claim と Evidence を別の型として分離しており、
本調査で確認された最も近い実装である。ただしそこでも proposition validity は
`truth_checker` の変換規則に還元されており、独立に評価されない。

### Question 3
**Can an AI-generated proposition expand beyond the evidentiary scope without being
detected or blocked?**

**Yes. Confirmed by implementation and by live data.**

`structural/bee.py:detect_co_occurrence()` は、確立β 3件から新命題を生成し、
`status: 制度化` (最上位) と `contradiction: 0` (ハードコード) を付与する。
実データ `structural/beta_registry.json` において
`institutional_evolution` (is_meta=True, status=制度化, evidence=74, contradiction=0,
approved_by=None) として現存する。

検出されない。阻止されない。Human Gate を経由しない。

### Question 4
**Does the Human Gate govern institutional authorization, rather than compensate for an
upstream evidentiary boundary failure?**

**No. It compensates.**

`structural/bee.py:update_lifecycle()` において、`approved_by` の存在は
反証率に基づく自動衰退を無効化する。実データ上、反証率 8.70 / 68.38 / 266.06 の
3命題がいずれも `確立` を維持しており、降格した唯一の命題
(`observation_as_institution`, 反証率 1505.67) は `approved_by` を持たない。

すなわち、承認の有無が、証拠に基づく降格の可否を決定している。
これは authorization boundary が evidentiary boundary の破綻を代償している状態である。

加えて `on_phi_approved()` は承認を `evidence += 5` として証拠側へ還流させており、
Stage 4 から Stage 1 への逆流経路が実装されている。

### Question 5
**Does the Control Surface operate only after the proposition has already crossed an
evidence boundary?**

**UNKNOWN (as to Control Surface itself); Yes (as to GL7 and event_gate).**

`Control Surface` という語彙は MoCKA 内に存在しないため、当該実体を特定できない。
これを UNKNOWN として保存する。

機能的に近い GL7 については Yes である。GL7 は命題も証拠も参照せず、
物理的事実のみを検査する。かつ commit da4d4db が
`GL7 shall not enforce semantic decisions` として、それを設計判断として確定している。

### Question 6
**Is the Evidence -> Proposition boundary explicitly implemented, or only implicitly
represented through existing mechanisms such as Unknown, Unverified, Conflicted, or
Evidence Supremacy?**

**Only implicitly, and inconsistently.**

- Unknown: Integrity Classification の `state` enum として構造化されている。
  Confirmed / Unverified / Unknown の3分割は `IC_20260724_003` において
  実際に適用されているが、**description 内の記述規約であってスキーマではない**。
- Unverified: `phi_os/context/*` では2値フィールドの初期値にすぎない。
- Conflicted: 実装されている2箇所 (`STATE_CONFLICTED`, `report_conflict_detector`) は
  いずれも「証拠の内部矛盾」ではない。前者は裁定済みcollisionの再検出、
  後者はレポート間およびレポート対コードの不一致である。
- Evidence Supremacy: Evidence-A (証跡) については一貫している。
  Evidence-B (命題支持) については、Supremacy が及ぶのは
  「どの証拠源が勝つか」(arbitration priority) までであり、
  「その証拠が当該命題を支持する資格を持つか」には及んでいない。

---

## 6. R01 FORENSIC CONCLUSION

```
Question:
What is available evidence entitled to establish before a proposition
reaches the authorization boundary?

Finding:
MoCKA には Evidence が何を確立できるかを拘束する独立した境界は存在しない。
MoCKA が統制しているのは (1) 証跡そのものの真正性 (Evidence-A: who / hash /
timestamp / decision_id)、および (2) 複数の証拠源が競合した場合にどれが勝つか
(arbitration priority) の2点である。
「ある証拠が、ある命題を支持する資格を持つか」は、各レイヤーにハードコードされた
1対1の変換規則に委ねられており、その変換自体を検査・登録・拘束する層は存在しない。
証拠許容性のレジストリ (ALLOWED_VALIDATION_METHODS / ALLOWED_EVIDENCE_TYPES) は
仕様として宣言されているが、実装からの参照は0件である。
結果として、証拠の意味的範囲を超えた命題が生成され、Human Gate を経由せずに
最上位の制度状態 (制度化) を取得する経路が実装され、かつ稼働している
(structural/bee.py Meta beta、実データ institutional_evolution)。

Evidence Boundary:
PARTIAL
- Evidence-A (証跡) は IMPLEMENTED かつ provenance 完備 (RuntimeEvidenceRecord)。
- Evidence-B (命題支持) は定義が4種に分裂し、うち2種は provenance を持たない。
- 統一仕様 AUTO-SEAL-STD-001 は skeleton であり Human Gate 未通過。

Proposition Boundary:
NOT IMPLEMENTED
- Evidence -> Proposition の変換を拘束する層は存在しない。
- 変換規則を登録する仕組み (ALLOWED_*) は宣言のみ、参照0件 (CONTRADICTED)。
- 変換の妥当性に対するテストは0件。

Authorization Boundary:
IMPLEMENTED (scope: authorization only)
- 状態遷移としては強制されている (phi_os/human_gate TRANSITIONS,
  human_gate_continuity の構造的停止)。
- ただし証拠妥当性・命題妥当性は一切検査しない。
- approved_by が人間であることを検査する唯一の実装
  (governance/seal_auth_record.py) は sandbox 限定であり、
  自ら 強制はしない と宣言している。
- phi_os/human_gate.py は app.py へ未mount (DORMANT)。

Human Gate Role:
既に成立した命題を制度状態へ昇格させる権限境界である (指示書 分類 B)。
Evidence がその命題を支持しているかは判定していない (分類 A ではない)。
さらに structural/bee.py においては、承認が反証に基づく降格を無効化する
override フラグとして機能しており、上流の証拠境界の破綻を代償している。
実データ上、反証率 266.06 の命題が 確立 を維持している。

Control Surface Role:
Control Surface という語彙は MoCKA のコード・仕様・記録に存在しない (grep 0件)。
該当実体を特定できないため UNKNOWN として保存する。
機能的に近い GL7 は物理ゲートに限定されることが commit da4d4db により確定済みであり、
命題も証拠も参照しない。event_gate は Event Ledger の書込経路にのみ完全収束する。

Critical Gap:
1. Evidence -> Proposition の変換規則が、検査対象ではなく実装詳細として散在している。
   同一の入力に対して reality_sync / core_kernel / bee がそれぞれ異なる規則を適用し、
   相互に整合しているかを確認する機構がない。
2. structural/bee.py において、証拠は部分文字列一致の累積カウンタであり、
   同一データに対する反復実行で単調増加する。閾値 ev >= 20 は新規データなしに到達可能。
3. 同モジュールにおいて、承認 (Stage 4) が証拠 (Stage 1) へ +5 として還流し、
   かつ承認の存在が反証に基づく降格を恒久的に無効化する。
   authorization と evidence の一方向性が実装上成立していない。
4. Meta beta は反証を探索せず contradiction=0 をハードコードして生成され、
   最上位の制度状態で誕生する。これは Q8 の Adversarial Case が
   Accept として処理される実例である。
5. 証拠不在が Unknown ではなく実質的な否定命題へ変換される箇所が存在する
   (report_truth_validator: 証拠なし -> BROKEN)。
6. core_kernel の完備したパイプライン (43 tests PASS) には Human Gate が存在せず、
   かつ production runtime に接続されていない (DORMANT)。

Confidence:
HIGH   -- 実装・実データに基づく所見 (bee.py, beta_registry.json, truth_checker.py,
          execution_governance.py, phi_os/human_gate.py, sync_registry.py の参照0件、
          core_kernel 43 tests の実行、mocka_integrity_list / mocka_decision_get の
          一次データ照会) について。
MEDIUM -- report_truth_governance の挙動について。static reading のみであり、
          Windows絶対パス依存のため本環境で実行検証できていない。
LOW / UNKNOWN -- Control Surface および Decision Write Governance Boundary について。
          MoCKA 内に該当語彙・該当文書が存在せず、対応関係を確定できない。

No new design introduced:
YES
```

---

## 7. Unknown として保存する項目

以下は本調査では判定できなかった。推測で埋めない。

1. `Control Surface` に対応する MoCKA 側の実体。語彙が存在しない。
2. `Decision Write Governance Boundary` 仕様書の所在。本repository内に存在しない。
   別リポジトリ由来か外部会話由来かは確認できない。
3. `HG_P7_20260825_D3` が `decision_type` / `conditions` を持つ理由と、
   そのレコードの書込経路。`mocka_decision_write` の inputSchema には
   当該2フィールドが存在しない。
4. production GL7 が `encoding_mismatch` を発火させ続けている理由 (第0.6節)。
   稼働コードがHEADと異なることは Confirmed だが、原因は Unknown。
5. `report_truth_governance` / `reality_sync` パイプラインの現在の実行可否と最新実行結果。
   README記載の実行結果は 2026-06-13 時点のものである。
6. `structural/beta_registry.json` の evidence カウンタが、bee.py の累積加算によって
   どの程度 inflate されているかの定量。実行履歴が保存されていないため算出できない。

## 8. 矛盾 (CONTRADICTED) として記録する項目

1. `reality_sync/sync_registry.py` の `ALLOWED_VALIDATION_METHODS` /
   `ALLOWED_EVIDENCE_TYPES` / `TRUTH_RULE`。docstring は
   `ここに定義されないルールは Sync Engine では使用しない` と述べるが、
   実装からの参照は0件であり、真実判定は `truth_checker.py` にハードコードされている。
2. `structural/bee.py` の `STAGE_THRESHOLDS` における `確立: contra_rate_max 0.19`。
   実データ上、`確立` を保持する3命題の反証率は 8.70 / 68.38 / 266.06 であり、
   閾値と実態が一致しない。
3. `AUTO-SEAL-STD-001` は `approved_by は system 値を許容しない` と定めるが、
   `mocka_decision_write` はこれを検査しない。実データ `HG_P7_20260825_D3` の
   `approved_by` は `Human Gate` (機構名) である。
4. `core_kernel` の `ValidationResult.NOT_APPLICABLE` は enum に定義されているが、
   `run_validation()` は一度も返さない。
5. production GL7 と本branch HEAD の `ABORT_CONDITIONS` の不一致 (第0.6節)。

---

## 9. 本調査が行っていないこと (明示)

- 新概念の追加を行っていない。`Evidence Entitlement Boundary` を MoCKA の既存概念として
  扱っていない。本報告書中で当該語が現れるのは、指示書からの引用と本文書のタイトルのみである。
- 改善案・実装案・設計変更案を含んでいない。
- 既存資料にない因果関係を推測していない。第0.6節および第7章の各項目は
  Confirmed と Unknown を分離して記述している。
- 設計思想と実装事実を混同していない。SPECIFIED / IMPLEMENTED / TESTED / ENFORCED を
  各表で分離して判定している。
- テストケースの存在のみをもって PASS と判定していない。実際に実行したのは
  `core_kernel/governance/tests` (43 passed) のみであり、それ以外は
  実行できなかったことを明記している。
- コード変更、Decision Ledger への書込、Integrity Classification への書込、
  TODO status の変更を一切行っていない。

## 10. History

- 2026-08-27: 初版 (v1.0)。R01 audit directive `MoCKA Evidence Entitlement Boundary
  Forensics` に基づく読み取り専用調査。commit da4d4db 時点の状態を固定。

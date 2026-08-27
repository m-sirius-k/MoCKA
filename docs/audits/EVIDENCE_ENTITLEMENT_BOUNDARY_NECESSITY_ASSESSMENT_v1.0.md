# Evidence Entitlement Boundary Necessity Assessment v1.0

```
EVIDENCE ENTITLEMENT BOUNDARY
NECESSITY ASSESSMENT

STATUS:
PARTIALLY NECESSARY
  - 責務としての必要性: NECESSARY (既存機構のいずれも当該責務を負っていない)
  - 独立Boundaryという形態の必要性: UNKNOWN (下記 13.4 の2つの未解消要因により未決)

CURRENT IMPLEMENTATION:
NOT CONFIRMED

SUBSTITUTE MECHANISM:
PARTIAL

HUMAN GATE COVERAGE:
NO

EVIDENCE SUPREMACY IMPACT:
PARTIAL

IMPLEMENTATION AUTHORIZATION:
NOT AUTHORIZED
```

- Document ID: AUDIT-EEB-002
- Class: Necessity Assessment (read-only investigation)
- Date: 2026-08-27
- Author: Claude-opus-5 (くろこ)
- Directive: R01 `Evidence Entitlement Boundary Necessity Assessment v1.0`
- Base commit: 0b46bd9 (branch `claude/mocka-evidence-proposition-boundary-1m781u`)
- Classification: Documentation only. コード変更なし。Ledger変更なし。TODO変更なし。
  threshold変更なし。Schema変更なし。テスト変更なし。

---

## 1. 調査目的

現在のMoCKAにおいて、以下を実装変更なしで独立検証する。

> Evidence Entitlement Boundary は、MoCKAの制度目的および既存アーキテクチャに照らして、
> 本当に必要な独立境界なのか。

本調査は境界の実装方法を扱わない。また、当該境界の実装を前提としない。
前回調査 (AUDIT-EEB-001, commit 0b46bd9) の結論も前提として扱わず、独立に再検証する。

## 2. Scope

### 2.1 対象

- MoCKA本体リポジトリ (branch `claude/mocka-evidence-proposition-boundary-1m781u`,
  base commit 0b46bd9)
- production MCP 経由で参照可能な Decision Ledger / Integrity Classification /
  Overview の一次データ

### 2.2 対象外 (実施していない)

コード変更 / 新規Boundary実装 / 既存コード修正 / threshold変更 / Evidence計算変更 /
Human Gate変更 / Unknown処理変更 / Schema変更 / Ledger仕様変更 / TODO変更 /
テストコード変更。

### 2.3 環境上の制約

- `data/` 配下は .gitignore により本cloneに存在しない。
  `decision_ledger.jsonl` の実体は読めず、MCP `mocka_decision_get` 経由に限定される。
  同ツールは同一 decision_id の **最新行のみ** を返す (後述 13.4-A で重要となる)。
- `reality_sync/sync_registry.py` の `REPO_ROOT` は Windows 絶対パスで固定されている。
  ただし本調査では、実行に repo root を必要としない純関数を直接呼び出す方式
  (第14章 PROBE) により、当該制約を回避せずに実行証拠を取得した。

## 3. Methodology

### 3.1 証拠分類

各発見に対し、以下の2軸を必ず付与する。

軸1 (確度): `OBSERVED` / `INFERRED` / `UNKNOWN`

軸2 (種別):
`CODE EVIDENCE` / `TEST EVIDENCE` / `DATA EVIDENCE` / `DOCUMENT EVIDENCE` /
`ARCHITECTURAL INFERENCE`

"コード上存在する"と"runtimeで強制される"を区別する。

### 3.2 使用手段

1. Canonical文書の精読 (`MOCKA_CHARTER_v2.md`, `CONSTITUTION.md`, `README.md`,
   `docs/governance/` 配下)。
2. MCP一次データ照会 (`mocka_decision_get`: `DC_20260730_009`, `DC_20260730_001`)。
3. `grep -rn` によるシンボル参照実測 (宣言のみか、runtime参照があるかの判別)。
4. **既存コードの読み取り専用実行** (第14章)。リポジトリを一切変更せず、
   既存の純関数および既存レジストリを in-memory で呼び出し、
   Adversarial Case / Counter-Evidence Case の挙動を実測した。
   `_save()` 等の永続化関数は一度も呼んでいない。実行後に
   `git status --porcelain` が空であること、`structural/beta_registry.json` の
   md5 が不変であることを確認済み。

### 3.4 表記に関する注記

CLAUDE.md の CP932汚染防止規約に従い、本文中の非ASCII装飾記号は使用しない。
ただし、一次資料からの逐語引用 (blockquote `>` で示した箇所) については、
原文の角括弧をそのまま保持している。引用の改変は本報告書が依拠する
Evidence の同一性を損なうためである。該当は4箇所。
UTF-8検証済み (BOMなし / 制御文字なし / cp932エンコード可)。

### 3.3 論証順序 (指示書 第15章に従う)

```
Boundary がない
   -> 既存機構では何が保証されるか
   -> 何が保証されないか
   -> その未保証部分が制度目的に影響するか
   -> 必要性判定
```

"Boundaryがないから危険"という飛躍は行わない。

## 4. Evidence Entitlement Boundary の暫定定義

指示書に従い、以下を暫定定義として用いる。最終仕様として固定しない。

```
Evidence E
    |
    v
[ E is entitled to establish P ? ]
    |
    v
Proposition P
```

用語:

- **Evidence**: ある命題・判断・状態を支持するためにシステムが利用する観測、記録、
  データ、イベントその他の根拠。
- **Proposition**: Evidenceから形成・導出・評価される主張、命題、判断対象。
- **Institutional State**: Propositionが制度上の状態として扱われる段階。

本調査で判明した重要な但し書き: MoCKA内の `Evidence` という語は、
実際には2つの異なる対象を指している。両者を混同すると本調査の問い自体が成立しない。

| 呼称 | 指す対象 | Canonical根拠 |
|---|---|---|
| Evidence-A (証跡) | 記録そのものの真正性。誰が / いつ / どのハッシュを固定したか | `AUTO-SEAL-STD-001`, `RuntimeEvidenceRecord`, `governance/seal_auth_record.py` |
| Evidence-B (証拠) | ある観測が、ある命題を支持すること | `reality_sync`, `report_truth_governance`, `structural/bee.py`, `core_kernel` |

Evidence Entitlement Boundary の問いは Evidence-B にのみ関係する。

---

## 5. STEP 1: MoCKA制度目的との照合

目的: Evidence Entitlement Boundary がなくても、既存原則だけで制度目的が成立するのか。

### 5.1 Canonical 原則の実文 (DOCUMENT EVIDENCE / OBSERVED)

`docs/governance/MOCKA_CHARTER_v2.md` (全文702バイト、8条):

| 条 | 実文 |
|---|---|
| 第1条 物理証拠優先原則 | すべての評価はログ・実行結果・記録に基づく。 |
| 第3条 記録完全性 | すべてのイベントはLedgerに記録される。 |
| 第4条 検証可能性 | すべての挙動は再現可能であること。 |
| 第5条 循環構造 | Input -> 判断 -> 実行 -> 記録 -> 再評価 の循環を維持する。 |
| 第6条 制御優先 | AIではなくシステムが最終決定を行う。 |
| 第8条 実証主義 | 理論より実行ログを優先する。 |

観測される事実 (CONTRADICTED として記録):
`README.md:172-186` は英語で 11項目の `Core Articles` (Article 0-10) を掲げ、
`Full Charter: docs/governance/MOCKA_CHARTER_v2.md` へリンクしている。
しかし当該Charterは 8条であり、条番号・内容ともに一致しない。
README側の `Article 0 | Verifiability - all claims must be externally verifiable` と
`Article 8 | Evidence supremacy - system logs override AI reports` は
Charter本文には存在しない。どちらがCanonicalかは本調査では確定できない。**UNKNOWN**。

### 5.2 Evidence Supremacy の Canonical 定義 (DATA EVIDENCE / OBSERVED)

MCP `mocka_decision_get("DC_20260730_009")` の実取得結果 (status: Active)。

title:
> 未検証文脈(Unverified Context)の隔離ルール確立

decision (抜粋、原文ママ):
> 今後、過去の文脈を継続する前提の文章が現れた場合、必ず以下の順序で確認する:
> (1)現在の会話履歴 (2)リポジトリ内の実ファイル(一次証拠) (3)Decision Ledger
> (4)Event Ledger (5)その他の履歴。**一致する証拠が存在しない場合**は
> 「未検証文脈」として隔離し、作業を進めない。推測・補完・記憶による接続は禁止する。
> 運用方針としてEvidence Supremacyを最優先とし、未検証文脈を現在の設計・判断・実装へ
> 持ち込まない。

**この定義から確定できること (OBSERVED):**

Evidence Supremacy の判定述語は **証拠の存在** である
(`一致する証拠が存在しない場合`)。適用範囲は2つに限られる。

1. **存在検査**: 主張を支持する証拠がリポジトリ・Ledger に一件も無い場合の隔離。
2. **源泉優先順位**: 5段階の確認順序 (会話 -> リポジトリ一次証拠 -> Decision Ledger
   -> Event Ledger -> その他)。`README Article 8` の
   `system logs override AI reports` も同じ構造である。

**この定義が扱っていないこと (OBSERVED):**

`E は存在する。E は真正である。しかし E は P を確立しない。`
という事象は、この5段階手順のどこにも該当しない。手順は E の存在を確認した時点で
充足され、E から P への飛躍そのものは検査対象になっていない。

### 5.3 MoCKA自身による当該ギャップの先行認識 (DOCUMENT EVIDENCE / OBSERVED)

`docs/governance/G5_HGC10_DECISION_PREP_v0.1.md:145,157`:

> 候補 B (証拠間の不整合) は **Evidence Supremacy と最も直接に接続する**が、
> 同時に **再検証の手続き**を要求する。手続きの所在は本資料では未整理であり、
> 未確定事項 (e) に含めた

`docs/governance/G5_HGC10_DECISION_INPUT_v0.1.md:86` も同じ論点を
`**再検証手続きの所在**が必要になる (Evidence Supremacy との接続)` として掲げる。

**これは本調査官の推論ではない。MoCKA自身が、Evidence Supremacy には
"証拠間の不整合が生じたときに何を根拠に何を言えるか"を決める手続きが
接続されていない、と既に記録している。** その手続きの所在は
`未整理` `未確定事項` として保存されている。

### 5.4 Unknown Preservation の Canonical 定義 (DOCUMENT EVIDENCE / OBSERVED)

`phi_os/hab/HAB_OPEN_QUESTIONS.md:41-42` の `## Principle`:

> Unknown states are preserved until evidence confirms resolution.
> No assumption-based completion.

`docs/governance/JARVIS_RUNTIME_BETA_HUMAN_GATE_REVIEW_RECORD_v0.1.md:148` が
これを `FC-04 Unknown 事項は解消せず保持する` として `DC_20260730_009` と併記している。

注記: 前回調査 (AUDIT-EEB-001 Q5) は `Unknown Preservation` を
`語彙なし (grep 0件)` と記載した。これは文字列 `unknown preservation` の検索結果としては
正しいが、**原則としては上記の英文で明示的に存在する**。本調査で所在を確定したため、
ここに訂正して記録する。

### 5.5 評価と遷移の責務分割 (DOCUMENT EVIDENCE / OBSERVED)

`docs/governance/mocka_hab_human_gate_relation_v1.md`:

§4 禁止構造:
> - **直接遷移**: HAB -> ACTIVE(Human Gateを経由しない遷移)
> - **自動裁定ループ**: Human Gate Core -> 自動APPROVE確定
> - **HABの意思化**: HABが「判断主体」になる構造

§5 安全構造:
> 2. **自動評価の限定性**: Coreは「判断材料生成」のみを行う。

§7 設計上の意味:
> この構造の意味は1つに収束する。
> 「評価は機械化できるが、遷移は人間にしか起こせない」

**これはMoCKA自身による A / B の責務分割の明文である。**

- 遷移 (B: Proposition -> Institutional State) = 人間のみ。
- 評価 (A: Evidence -> Proposition) = 機械化されうる、かつ Core の責務。

すなわちMoCKAの設計意図において、A は Human Gate の責務ではなく、
**機械側が負うべき責務として位置づけられている**。

### 5.6 Authority Ownership (DOCUMENT EVIDENCE / OBSERVED)

`docs/governance/JARVIS_CONSTITUTION_DRAFT.md:2.5` が引用する
`DC_20260729_013` D-03 (Active):

> Authority Ownership: PHI-OS = Runtime Coordination / Execution Control /
> Human Gate Routing、**MoCKA = Evidence Management / Decision Evidence /
> Audit Intelligence / Governance Analysis**、Human = Architecture Authority /
> Policy Change Approval / Irreversible Decision

同 D-02: Adapter の**禁止**事項に `Human Gate 代替` が含まれる。

Evidence の管理責務は MoCKA 本体に帰属し、PHI-OS にも Human にも委譲されていない。

### 5.7 STEP 1 の結論

| 問い | 判定 |
|---|---|
| 既存原則は `E が存在しない` 場合を統制しているか | **YES** (`DC_20260730_009`、明示的・Active) |
| 既存原則は `複数の証拠源が競合する` 場合を統制しているか | **YES** (5段階順序 / Article 8 / arbitration priority) |
| 既存原則は `E は存在するが P を確立しない` 場合を統制しているか | **NO**。該当する原則は発見されなかった |
| MoCKAはこのギャップを自覚しているか | **YES**。`G5_HGC10` が `再検証手続きの所在` として未確定事項に登録済み |
| A (評価) は誰の責務と位置づけられているか | **機械側** (`評価は機械化できるが、遷移は人間にしか起こせない`) |

---

## 6. STEP 2: Evidence から Proposition への全経路

各経路について SOURCE / TRANSFORMATION / TARGET / VALIDATION / AUTHORITY /
COUNTER-EVIDENCE / UNKNOWN HANDLING を記録する。

### 6.1 Event -> Evidence

| 項目 | 内容 |
|---|---|
| SOURCE | `mocka_events.db` (events テーブル) |
| TRANSFORMATION | `generator.generate_evidence_record()`: 全件を read-only で読み、`sha256(json.dumps(rows, sort_keys=True))` |
| TARGET | `RuntimeEvidenceRecord` |
| VALIDATION | `evidence_schema.validate()` - 必須フィールド存在 / `immutable is True` / `event_count` が int |
| AUTHORITY | **Evidence ではない。** docstring: `Runtime Evidence Record は Authority ではない(DC-WP-001)。Governance Seal に従属する Evidence として扱う` |
| COUNTER-EVIDENCE | 概念なし |
| UNKNOWN HANDLING | rows が空なら `from_event_id`/`to_event_id` は空文字。Unknown表現なし |
| 分類 | CODE EVIDENCE / OBSERVED。ただし `Materialization = 実際の永続化はPhase8-2の対象外` (in-memory のみ) |

### 6.2 Evidence -> Truth (reality_sync)

| 項目 | 内容 |
|---|---|
| SOURCE | `CodeStateEntry` (exists / syntax_valid / import_ok / evidence文字列) |
| TRANSFORMATION | `truth_checker.determine_truth()`: 3分岐のハードコード |
| TARGET | `"FIXED"` / `"BROKEN"` |
| VALIDATION | **なし。** 変換自体を検査する層は存在しない |
| AUTHORITY | `唯一の真実判定レイヤー` (docstring) |
| COUNTER-EVIDENCE | 概念なし。単一 entry のみを見る |
| UNKNOWN HANDLING | **Unknown は存在しない。** 3分岐はすべて FIXED か BROKEN を返す |
| 分類 | CODE EVIDENCE / OBSERVED |

意味上の観測: 証拠が支持するのは `ast.parse が成功した` であり、
確立される命題は `FIXED (修正済み)` である。両者は同一ではない。
この拡張を検出する機構は存在しない。

### 6.3 Evidence -> Claim / Claim vs Truth (report_truth_governance)

| 項目 | 内容 |
|---|---|
| SOURCE | `Evidence` (source / status / detail)、`ReportClaim` (claimed_status / quote) |
| TRANSFORMATION | `true_state()` (evidence のみ参照)、`detect()` (claim と truth の突合) |
| TARGET | `truth_state`、`Conflict[]`、`ReportTruthState` |
| VALIDATION | Conflict 4分類の検出のみ |
| AUTHORITY | `PRIORITY_ORDER = [code_state_scanner, reality_sync.sync_engine, test_execution]`、Report Claim は最下位 |
| COUNTER-EVIDENCE | **claim 対 claim / claim 対 truth のみ。** evidence 対 evidence は表現されない |
| UNKNOWN HANDLING | `ReportClaim.claimed_status` は `UNKNOWN` を取りうるが、`detect()` は `statuses - {"UNKNOWN"}` で除去する。`true_state()` は証拠不在時に `("BROKEN", "NO_EVIDENCE")` を返す |
| 分類 | CODE EVIDENCE / OBSERVED |

**arbitration priority の退化 (CODE EVIDENCE / OBSERVED):**

1. `link()` は同一の `determine_truth(entry)` 呼び出しから
   `code_state_scanner` と `reality_sync.sync_engine` の2つの Evidence を生成し、
   **両者に同じ `status` を代入する**。優先順位1位と2位は常に同値である。
2. `test_execution` を `source` とする Evidence を構築するコードは
   リポジトリ内に **存在しない** (grep実測: `report_claim_model.py` のコメントと
   `report_arbitrator.py` の PRIORITY_ORDER 要素のみ)。

したがって 3段階の絶対優先順位は、実際には1段階に退化している。

### 6.4 Evidence -> Score -> Proposition -> Institutional State (structural/bee.py)

| 項目 | 内容 |
|---|---|
| SOURCE | `events` テーブル直近500行の `title/what_type/why_purpose/how_trigger` 連結文字列 |
| TRANSFORMATION | `pattern_db` のキーワードに対する **小文字部分文字列一致**。一致件数を `evidence` / `contradiction` へ**累積加算** |
| TARGET | `beta_registry[*].status` = 観察β / 成長中 / 確立 / 制度化 / 衰退 / 消滅 |
| VALIDATION | `STAGE_THRESHOLDS` の閾値比較のみ |
| AUTHORITY | なし。CLI (`--daily`) およびスケジュール実行 |
| COUNTER-EVIDENCE | `contradiction` カウンタとして存在。ただし `matched_contra = not matched_support and ...` により、支持と反証が同時に成立する場合は**反証を計上しない** |
| UNKNOWN HANDLING | Unknown 状態は存在しない |
| 分類 | CODE EVIDENCE + DATA EVIDENCE / OBSERVED |

### 6.5 Approval -> Evidence (逆流経路)

| 項目 | 内容 |
|---|---|
| SOURCE | Human Gate 承認 (`judgement_reason` の approved) |
| TRANSFORMATION | `bee.on_phi_approved()`: `evidence += 5`、`approved_by = "きむら博士 (PHI DNA)"` |
| TARGET | `beta_registry[*].evidence` |
| VALIDATION | なし |
| 分類 | CODE EVIDENCE / OBSERVED |

**Stage 4 (Authorization) の出力が Stage 1 (Evidence) の入力へ還流している。**
5段階モデルの一方向性が、この1関数によって実装上破られている。

### 6.6 Proposition -> Institutional State (phi_os/human_gate.py)

| 項目 | 内容 |
|---|---|
| SOURCE | `request_id` と payload |
| TRANSFORMATION | `_transition()`: `current in TRANSITIONS[action]` の検査のみ |
| TARGET | PENDING / APPROVED / REJECTED / EXPIRED / CANCELED |
| VALIDATION | 遷移の妥当性のみ。payload 内容・承認者同一性・証拠は非検査 |
| AUTHORITY | 呼び出し元 (認証なし) |
| COUNTER-EVIDENCE | 概念なし |
| UNKNOWN HANDLING | なし |
| 分類 | CODE EVIDENCE / OBSERVED。ただし `human_gate_bp` は `register_blueprint` されておらず (grep実測)、既存監査 `docs/audits/mocka_1_0_audit_baseline_v1.md` も `DORMANT` と判定 |

### 6.7 Evidence -> Decision (core_kernel/governance)

| 項目 | 内容 |
|---|---|
| SOURCE | `GovernanceEvent.validation_evidence: Mapping[str, Any]` |
| TRANSFORMATION | `run_validation()`: `not evidence.get(scope)` による8項目の充足判定 -> `run_decision()` による集約 |
| TARGET | `DecisionRecord.decision` = PASS / WARNING / FAIL |
| VALIDATION | 型・必須フィールドのみ (`__post_init__`) |
| AUTHORITY | `DecisionRecord.decision` のみが authoritative (docstring) |
| COUNTER-EVIDENCE | 概念なし |
| UNKNOWN HANDLING | **なし。** キー不在と値 False が同一視される (第14章 PROBE 1 で実測) |
| PROVENANCE | **なし。** `GovernanceEvent` に actor / source / evidence origin フィールドは存在しない |
| 分類 | CODE EVIDENCE + TEST EVIDENCE / OBSERVED。43 tests PASS。ただし production から import 0件 (DORMANT) |

### 6.8 経路一覧の総括

| 経路 | 変換の妥当性検査 | Counter-Evidence | Unknown保存 |
|---|---|---|---|
| Event -> Evidence | 構造検査のみ | なし | なし |
| Evidence -> Truth | **なし** | なし | **なし** |
| Evidence -> Claim突合 | 4分類検出のみ | claim対claimのみ | **除去される** |
| Evidence -> Score -> State | 閾値のみ | 抑制付きで存在 | なし |
| Approval -> Evidence | **なし** | - | - |
| Proposition -> State | 遷移妥当性のみ | なし | なし |
| Evidence -> Decision | 充足判定のみ | なし | **なし** |

全7経路のうち、`E が P を確立する資格を持つか` を検査する経路は **0件**。

---

## 7. STEP 3: "Evidenceが何を言えるか"の判定箇所

指示書が列挙した12項目について、Evidence -> Proposition 変換の**前**に
runtime で強制されているかを実測した。

| 検査項目 | 宣言 | runtime enforcement | 根拠 |
|---|---|---|---|
| evidence type | あり (`ALLOWED_EVIDENCE_TYPES`) | **なし** | grep実測: 定義行 (`sync_registry.py:33`) 以外の参照0件 |
| validation method | あり (`ALLOWED_VALIDATION_METHODS`) | **なし** | grep実測: 定義行 (`:24`) 以外の参照0件 |
| truth rule | あり (`TRUTH_RULE`) | **なし** | grep実測: 定義行 + docstring 2箇所のみ。実ロジックは `truth_checker.py` にハードコード |
| confidence | あり (`ReportTruthState.confidence_score`) | 計算はされる | `1.0 - 0.15 * len(conflicts)`、`NO_EVIDENCE` なら base 0.3。**証拠の強度ではなく矛盾件数の関数** |
| threshold | あり (`STAGE_THRESHOLDS`, `REQUIRED_TRACE_COUNT`) | **一部あり** | `prediction/gate.check()` は強制。`STAGE_THRESHOLDS` は `確立` 維持側では強制されない (第14章 PROBE 3) |
| source authority | あり (`PRIORITY_ORDER`) | あり (ただし退化) | 6.3 参照 |
| context | - | **なし** | 該当実装を発見できず |
| provenance | 一部あり (`RuntimeEvidenceRecord.generated_by`) | 記録のみ。判定に不使用 | `GovernanceEvent` / `beta_registry` には provenance フィールド自体が無い |
| temporal validity | 一部あり (`last_seen`, `generated_at`) | **なし** | `is_fresh()` docstring: `generated_atの経過時間は判定に用いない` |
| contradiction | あり (`contradiction` カウンタ, `Conflict`) | **無効化されうる** | 第9章 |
| counter-evidence | 部分的 | 常に敗北する | 第9章 |
| relevance | **宣言もなし** | **なし** | grep実測: governance系コードに relevance/entitle/warrant 判定は0件。`relevance_score` は `feedback/memory_reinforcer.py` の記憶検索用で無関係 |

**STEP 3 判定 (OBSERVED):**
12項目のうち、Evidence -> Proposition 変換の前に runtime 強制されているのは
`threshold` (一部) と `source authority` (退化した形) の2つのみ。
中核である `relevance` は宣言すら存在しない。

---

## 8. STEP 4: 代替機構の存在確認

### A. Provenance - "誰が、いつ、どこから取得したか"で解決するか

**判定: NO**

- `RuntimeEvidenceRecord` は `generated_by` / `generated_at` / `hash_method_spec` /
  `source_event_range` を持つ (CODE EVIDENCE / OBSERVED)。
- しかし provenance は **その証拠が誰のものか** を答えるのみで、
  **その証拠が何を言えるか** には無関係である。
- 決定的な反証: `bee.py --evidence BETA_ID --source manual` は
  `--source` 引数を parse するが、当該分岐で `args.source` を**一度も参照しない**。
  出所を受け取りながら記録せずに破棄している (CODE EVIDENCE / OBSERVED)。
- `GovernanceEvent` には provenance フィールドが存在しない。
  第14章 PROBE 1 で、caller が供給した8個の真偽値が無検証で `PASS` に到達することを実測。

### B. Authenticity - 本物であることを確認すれば足りるか

**判定: NO**

- Authenticity は Evidence-A の性質である。
  SHA-256 ハッシュ鎖、Ed25519 署名、append-only ledger により保証される
  (`README.md` Record Layer、DOCUMENT EVIDENCE)。
- 真正な `AST_PARSE_OK` は、真正であるがゆえに `FIXED` を意味するわけではない。
  真正性と含意は独立した性質である (ARCHITECTURAL INFERENCE - ただし
  6.2 の変換が実在することは OBSERVED)。

### C. Arbitration - 優先順位を決めれば足りるか

**判定: NO**

- Arbitration が答えるのは **どの源泉が勝つか** であって、
  **勝った源泉が P を言えるか** ではない。
- 第14章 PROBE 2 で実測: 2本の独立したレポートが `BROKEN` と主張しても、
  Report Claim は最下位のため両方とも不採用となり、
  `governance_status = PASS` / `truth_state = FIXED` が確定する。
- さらに `arbitrate()` は **全 conflict_type に対して無条件に `resolved=True` を返す**
  (未知の conflict_type を受ける `else` 分岐も含む。PROBE 2 で実測)。
  grep実測: リポジトリ全体で `resolved=False` を設定するコードは **0件**。
  `report_governance_engine.govern()` の
  `governance_status = "FAIL" if unresolved else "PASS"` における
  **FAIL 分岐は pipeline 上到達不能である**。
- 6.3 の通り、優先順位1位と2位は常に同値、3位は生成されない。

### D. Sufficiency - 量が十分なら足りるか

**判定: NO**

- 3つの sufficiency 実装はいずれも **presence / count / checklist** を見る。
  内容の含意は見ない。
- `prediction/gate.py` (`trace_count >= 30`) は本調査で確認された
  最も明確な sufficiency 実装だが、`30件あれば予測してよい` を判定するのみで、
  `その30件が当該componentの将来スコアを支持するか` は判定しない。
- 決定的な反証 (第14章 PROBE 1): `validation_evidence` の全値を
  文字列 `"FALSE"` にした場合、Python の truthy 判定により
  `ValidationResult.VALID` / `DecisionResult.PASS` となる。
  sufficiency は満たされているが、証拠は何も支持していない。

### E. Human Gate - 最終承認すれば上流まで解決するか

**判定: NO (かつ、条件によっては逆転する)**

- MoCKA自身の設計文書が A と B を分離している
  (`評価は機械化できるが、遷移は人間にしか起こせない`、5.5)。
  Human Gate は B の担当であり、A の担当ではないと明示されている。
- `phi_os/human_gate.py:approve()` は遷移妥当性のみを検査する。
  `approve_promotion()` の `decision_evidence_consistency` は
  **引数として渡される真偽値**であり、`False` を渡しても承認は成立する
  (CODE EVIDENCE / OBSERVED)。
- 第14章 PROBE 3 で実測した反転:
  `approved_by` が設定された β は、反証率 8.70 / 266.06 であっても
  `確立` を維持する。同一データから `approved_by` のみを除いた対照試行では
  `衰退` へ降格する。
  **承認の有無が、証拠に基づく降格の可否を決定している。**

### STEP 4 総括

| 代替機構 | 判定 |
|---|---|
| A. Provenance | **NO** |
| B. Authenticity | **NO** |
| C. Arbitration | **NO** |
| D. Sufficiency | **NO** |
| E. Human Gate | **NO** |
| 5機構の合成 | **PARTIAL** - 存在・真正性・源泉優先・量・遷移権限は覆うが、含意は覆わない |

---

## 9. STEP 5: Adversarial Case

### 9.1 設定

```
Evidence E exists.
E is authentic.
E has valid provenance.
E is admissible under existing registry.
E is repeatedly observed.
E crosses the existing sufficiency threshold.
But:
E does not logically establish Proposition P.
```

### 9.2 実測結果 (第14章 PROBE 1 / PROBE 2、CODE EVIDENCE / OBSERVED)

| 検証 | 入力 | 出力 |
|---|---|---|
| core_kernel 完全充足 | 8 scope すべて `True` | `VALID` / `PASS` / reasons=() |
| core_kernel 内容無関係 | 8 scope すべて文字列 `"FALSE"` | `VALID` / `PASS` |
| report layer 反証あり | 2レポートが `BROKEN` を主張、code evidence は `FIXED` | `governance_status=PASS`、`truth_state=FIXED`、confidence 0.85 |
| 未知 conflict_type | `"TOTALLY_UNKNOWN_TYPE"` | `resolved=True` |

### 9.3 判定

**結果は `Accept` である。**

`Reject` / `Unknown` / `Insufficient` のいずれにもならない。
`Institutionalized` については、`bee` 経路では該当する
(確立β3件から Meta β が `status: "制度化"` `contradiction: 0` で自動生成される。
前回調査 AUDIT-EEB-001 で確認済み、実データ `institutional_evolution` として現存)。

**重要な限定**: `E is admissible under existing registry` という前提条件は、
実際には検査されていない。`ALLOWED_EVIDENCE_TYPES` は参照0件だからである (第7章)。
すなわち MoCKA は admissibility を判定しないまま Accept している。

---

## 10. STEP 6: Counter-Evidence Case

### 10.1 設定

```
Evidence E supports P
Evidence C contradicts P
```

### 10.2 確認事項ごとの判定

| 確認事項 | 判定 | 根拠 |
|---|---|---|
| Counter-evidence は認識されるか | **PARTIAL** | `bee.contradiction` カウンタと `Conflict` 4分類として認識される。ただし `reality_sync` / `core_kernel` には概念自体が無い |
| Evidence と同等に扱われるか | **NO** | `bee`: `matched_contra = not matched_support and ...` により、支持と反証が同時成立する観測は**支持としてのみ計上**される。構造的な非対称 |
| threshold 計算へ影響するか | **PARTIAL** | 昇格側 (`ev >= 20 and rate < 0.20`) には影響する。**維持側には影響しない** (PROBE 3 で実測) |
| approval によって無効化されないか | **無効化される** | `if entry.get("approved_by") and current in ("確立","制度化","成長中"): if rate >= 0.40: return current`。PROBE 3 の対照試行で確認 |
| Institutional State へ進めるか | **YES** | 反証率 266.06 の β が `確立` を維持している (DATA EVIDENCE) |
| Unknown へ戻る可能性があるか | **NO** | `update_lifecycle()` の返り値集合に Unknown は存在しない。`report_truth_validator` も Unknown を返さない |

### 10.3 "P を確立する資格"を判定している機構の特定

**該当機構は存在しない。**

支持証拠と反証証拠が共存する場合に働く機構は、実測上以下の3つに尽きる。

1. `bee.update_lifecycle()` - **比率の閾値比較**。ただし `approved_by` で無効化される。
2. `report_arbitrator.arbitrate()` - **源泉優先順位**。常に `resolved=True` を返し、
   FAIL 分岐は到達不能。
3. `report_conflict_detector.detect()` - **検出のみ**。docstring:
   `矛盾は検出するのみで、解決は report_arbitrator.py が行う`。

いずれも"E と C のどちらが P を支持する資格を持つか"ではなく、
"どちらの**源泉**が優先されるか"または"数の比がいくつか"を判定している。

さらに重要な構造的観測 (CODE EVIDENCE / OBSERVED):
**`evidence 対 evidence` の矛盾を表現する型が存在しない。**
`report_truth_governance` の Conflict 4分類はすべて claim を一方に含む
(INTRA_REPORT / INTER_REPORT / CLAIM_VS_TRUTH / OUTDATED_CLAIM)。
そして 6.3 の通り、2つの evidence source は常に同値であるため、
evidence 間の不整合はそもそも発生し得ない。

これは 5.3 で引用した `G5_HGC10` の `候補 B (証拠間の不整合)` が
`再検証手続きの所在は未整理` とされている状況と正確に対応する。

---

## 11. STEP 7: Temporal / Contextual Case

### 11.1 設定

同一 Evidence E について、`T1/C1/S1` と `T2/C2/S2` が異なる場合、
既存MoCKAは E の意味・有効性・Entitlement の変化を表現または検出できるか。

新仕様 (XYZ + T + S) は導入しない。既存の対応範囲のみを確認する。

### 11.2 実測結果

| 次元 | 既存の表現 | 検出・強制 | 根拠 |
|---|---|---|---|
| T (時間) - Evidence の生成時刻 | あり (`generated_at`, `last_seen`, `approved_at`) | **記録のみ** | `is_fresh()` docstring: `Authority一致のみを基準とし、generated_atの経過時間は判定に用いない` |
| T - Evidence の失効 | **なし** | なし | `valid_until` / TTL / expiry を持つ Evidence 型は存在しない (grep実測) |
| T - Proposition の失効 | 部分的にあり | **上位2状態は免除** | `bee.py:179`: `if days_since >= 90 and current not in ("確立","制度化")`。確立・制度化は90日ルールの対象外 |
| T - Meta Proposition の失効 | **なし** | なし | `bee.py:297,334`: Meta β 生成時に `"expires_at": None` をハードコード |
| T - Claim の陳腐化 | あり (`OUTDATED_CLAIM`) | 検出のみ | かつ判定根拠は実時刻ではない。`report_conflict_detector` docstring: `タイムスタンプ情報がレポート本文にないため、REPORT_FILES のリスト順=新しい順という前提` |
| C (Context) | **なし** | なし | Evidence に context フィールドを持つ型は発見されなかった |
| S (Strength) | **なし** | なし | `evidence` は整数カウンタ。重み・強度の概念は無い。`confidence_score` は矛盾件数の関数であり証拠強度ではない |

### 11.3 判定

- **T については、記録はできるが、Entitlement の変化としては表現も検出もできない。**
  唯一の freshness 判定 (`is_fresh`) は経過時間を明示的に判定材料から除外している。
- **C と S については、表現手段自体が存在しない。**
- **結果として、一度 `確立` / `制度化` に到達した Proposition は、
  時間経過によっても反証蓄積によっても (approved_by がある限り) 覆らない。**
  この二重の免除は PROBE 3 と `bee.py:179` の両方で確認されている。

なお本章は必要性検証のみを扱い、実装提案を含まない (指示書 STEP 7)。

---

## 12. STEP 8: Human Gate Boundary との比較

### 12.1 比較対象

```
A:  Evidence -> Proposition
B:  Proposition -> Institutional State
```

### 12.2 B の実装上の責務 (OBSERVED)

| 実体 | B に対する責務 | 検査内容 |
|---|---|---|
| `phi_os/human_gate.py` | 状態遷移の管理 | `current in TRANSITIONS[action]` のみ |
| `governance/human_gate_continuity.py` | WAITING からの前進禁止 | 前進させる関数を実装しない (構造的担保) |
| `mocka_hab_human_gate_relation_v1.md` §4 | 直接遷移 / 自動裁定ループ / HABの意思化 の禁止 | 規範 |
| `structural/execution_governance.py` (GL7) | 物理的破壊の防止 | 4つの物理条件のみ。commit da4d4db が `GL7 shall not enforce semantic decisions` として確定 |

B は規範・実装の両面で明確に定義されている。

### 12.3 B の存在が A を保証するか

**判定: NO。**

以下は推論ではなく、MoCKA文書とコードから直接得られる。

1. **MoCKA自身が A を B の責務外に置いている。**
   `mocka_hab_human_gate_relation_v1.md` §5-2: `自動評価の限定性: Coreは
   "判断材料生成"のみを行う`。§7: `評価は機械化できるが、遷移は人間にしか起こせない`。
   評価 (A) は Core = 機械の責務、遷移 (B) は人間の責務、と分離されている。

2. **B の実装は A の入力を検査しない。**
   `approve()` は payload を保存するのみで読まない。
   `approve_promotion(decision_evidence_consistency=False, ...)` は成立する。

3. **A の破綻が B を通過して Institutional State に到達する経路が実在する。**
   PROBE 1: 内容が無意味な evidence が `PASS` に到達し、
   `core_kernel` には Human Gate が無いため `committed = decision != FAIL` で
   そのまま commit される。

4. **B が A を保証しないどころか、A の結果を上書きする経路が実在する。**
   PROBE 3: `approved_by` の有無だけで `確立` と `衰退` が分岐する。
   B の記録が A の判定を無効化している。

### 12.4 A と B の関係についての判定

`A != B` を前提とせずに検証した結果、実装・文書の双方から
**A と B は別責務であり、かつ現在 A の担当が存在しない**ことが確認された。

これは前提ではなく、以下の証拠から導かれる結論である。

- 文書側: `評価は機械化できるが、遷移は人間にしか起こせない` (責務分離の明文)
- 実装側: B の3実装いずれも A の入力を検査しない (CODE EVIDENCE)
- 実測側: PROBE 1 / 3 (A の破綻が B を素通りする、B が A を上書きする)

---

## 13. Necessity 判定

指示書 第15章の論証順序に従う。

### 13.1 Boundary がない (再確認)

STEP 2 の全7経路のうち、`E が P を確立する資格を持つか` を検査する経路は 0件。
STEP 3 の12項目のうち、中核である `relevance` は宣言すら存在しない。
**OBSERVED。前回調査の結論に依存せず、本調査で独立に再確認した。**

### 13.2 既存機構では何が保証されるか

| # | 保証されている事項 | 機構 | 確度 |
|---|---|---|---|
| 1 | 証拠が一件も存在しない主張は隔離され、作業が進まない | `DC_20260730_009` (Active) | OBSERVED / DATA |
| 2 | 記録の真正性・改竄検知・append-only | SHA-256鎖 / Ed25519 / ledger | OBSERVED / DOCUMENT |
| 3 | 証拠源泉の優先順位 (system logs > AI reports) | Charter 第8条 / `PRIORITY_ORDER` | OBSERVED / CODE |
| 4 | 証跡の最小構成と human-only seal の規範 | `AUTO-SEAL-STD-001` / `seal_auth_record` | OBSERVED (規範として) |
| 5 | 量的・完全性的な sufficiency (3実装) | `validation_engine` / `prediction gate` / `explanation_builder` | OBSERVED / CODE+TEST |
| 6 | Institutional State への遷移は人間のみ (規範) | `mocka_hab_human_gate_relation_v1.md` §4 | OBSERVED / DOCUMENT |
| 7 | 物理的破壊の防止 | GL7 4条件 | OBSERVED / CODE |
| 8 | Unknown を埋めない (規範) | `HAB_OPEN_QUESTIONS.md` Principle | OBSERVED / DOCUMENT |

### 13.3 何が保証されないか

| # | 保証されない事項 | 実測根拠 | 確度 |
|---|---|---|---|
| 1 | E が存在し真正であるとき、E が P を支持するか | 該当機構0件。`relevance` 宣言なし | OBSERVED |
| 2 | 反証が支持と対等に扱われること | `matched_contra = not matched_support and ...` | OBSERVED / CODE |
| 3 | 反証が Institutional State を阻止できること | PROBE 3。反証率 266.06 で `確立` 維持 | OBSERVED / DATA |
| 4 | 矛盾が未解決のまま残せること | `resolved=False` 設定コード0件。FAIL 分岐到達不能 | OBSERVED / CODE |
| 5 | 証拠不在が Unknown として保存されること | `true_state()` -> `("BROKEN","NO_EVIDENCE")` | OBSERVED / CODE |
| 6 | 未観測と反証が区別されること | PROBE 1。ABSENT と FALSE が同一出力 | OBSERVED / CODE |
| 7 | 証拠の内容が実際に検査されること | PROBE 1。文字列 `"FALSE"` が `VALID/PASS` | OBSERVED / CODE |
| 8 | 承認が証拠を代替しないこと | `on_phi_approved`: `evidence += 5` | OBSERVED / CODE |
| 9 | Evidence の時間的・文脈的有効性 | `is_fresh` は経過時間を判定に使わない。C/S の表現なし | OBSERVED / CODE |
| 10 | 確立済み Proposition の再検査 | 90日ルールは 確立/制度化 を免除 | OBSERVED / CODE |
| 11 | 証拠許容性 (evidence type / validation method) | `ALLOWED_*` 参照0件 | OBSERVED / CODE |

### 13.4 未保証部分は制度目的に影響するか

**影響する。以下は本調査官の価値判断ではなく、MoCKA自身のCanonical文言との対照である。**

| Canonical 原則 (実文) | 対照される未保証事項 | 影響の性質 |
|---|---|---|
| Charter 第1条: `すべての評価はログ・実行結果・記録に基づく` | 13.3-#7: 内容非検査。caller が供給した真偽値がそのまま `PASS` になる | 評価の**入力**は記録に基づくが、評価そのもの (E->P) が記録に基づいて検証されていない。第1条は入力側でのみ充足 |
| Charter 第6条: `AIではなくシステムが最終決定を行う` | 13.3-#1: E->P を検査する system 側の機構が不在 | "システムが決定"は形式上充足されるが、決定内容の妥当性はどの system 機構も担保していない |
| Charter 第4条: `すべての挙動は再現可能であること` | 13.3-#9: `bee.collect_evidence` は同一データへの反復実行で `evidence` を累積加算する | 同じ証拠集合に対する再実行が異なる状態を生む。再現可能性と整合しない |
| `HAB_OPEN_QUESTIONS.md`: `Unknown states are preserved until evidence confirms resolution. No assumption-based completion.` | 13.3-#5, #6 | `証拠なし -> BROKEN` は assumption-based completion に該当する。Unknown Preservation は**実装レベルで侵食されている** |
| `mocka_hab_human_gate_relation_v1.md` §7: `評価は機械化できるが、遷移は人間にしか起こせない` | 13.3-#8 (`Approval -> Evidence` 還流)、PROBE 3 (承認が降格を無効化) | 遷移側の記録が評価側へ流入している。責務分離が実装上維持されていない |
| `DC_20260730_009`: `推測・補完・記憶による接続は禁止する` | 6.4 Meta β 生成 (`contradiction: 0` ハードコード) | 反証を探索せずに `0` と記録する行為は、証拠に基づかない補完に該当 |

**したがって H3 は成立する (OBSERVED):**
Evidence Entitlement Boundary が存在しないことにより、
`Unknown Preservation` と `Institutional State Integrity` は
既に構造的に侵食されている。`Evidence Supremacy` については 13.5 参照。

### 13.5 Evidence Supremacy への影響 - PARTIAL である理由

Evidence Supremacy を **Canonical 定義通り** (`DC_20260730_009`: 存在検査 + 5段階源泉順序)
に読む限り、当該原則自体は侵食されていない。存在検査も源泉順序も機能している。

侵食されているのは、**Evidence Supremacy が扱っていない領域**である。
そして MoCKA自身が `G5_HGC10` において、この領域を
`再検証手続きの所在` として未確定事項に登録している (5.3)。

よって `EVIDENCE SUPREMACY IMPACT: PARTIAL` と判定する。
`YES` としないのは、原則そのものの破綻ではなく適用範囲外だからである。
`NO` としないのは、`README Article 0` (`all claims must be externally verifiable`) を
Canonical と見なす場合には直接侵食に当たるが、5.1 の通り README と Charter の
条文集合が一致しないため、どちらが Canonical かが **UNKNOWN** だからである。

### 13.6 仮説の判定

| 仮説 | 判定 | 根拠 |
|---|---|---|
| H1: Evidenceの存在・真正性と、EvidenceがPを確立する資格を区別する必要がある | **成立** | 13.4。区別しないことにより Unknown Preservation と再現可能性が実際に侵食されている |
| H2: 現行MoCKAに Entitlement を独立検証する機構が存在しない | **成立** | 13.1。前回結論に依存せず独立再確認 |
| H3: 不在により Evidence Supremacy / Unknown Preservation / Institutional State Integrity のいずれかが侵食される | **成立 (2/3)** | Unknown Preservation: 侵食 OBSERVED。Institutional State Integrity: 侵食 OBSERVED。Evidence Supremacy: PARTIAL (13.5) |
| H4: 既存機構だけでは完全には代替できない | **成立** | 第8章。A-E すべて NO、合成で PARTIAL |
| H5: 単なる追加機能ではなく、別種類の Governance Boundary である | **PARTIAL / 未決** | 責務が既存のどれとも重ならないことは OBSERVED。ただし"別種類の Boundary"として切り出すべきか、既存 Evidence Supremacy への手続き追加とすべきかは 13.7 の未解消要因により決定できない |

### 13.7 N0 / N1 / N2 / N3 判定

**判定: N2**

> N2: 既存機構では完全には保証されず、独立Boundaryの必要性が高い。

**N0 / N1 を採らない理由 (OBSERVED):**
第8章で A-E すべてが `NO` であり、当該責務を負う既存機構は存在しない。
13.4 で示した通り、未保証部分は Canonical 原則と実際に対照される影響を持つ。
よって"不要""必要性は低い"とは判定できない。

**N3 を採らない理由 (これが本判定の核心):**

指示書は"調査官は結論を作ってはいけない"と定めている。
N3 (`論理的に不可欠`) を主張するには、以下2点を否定しなければならないが、
本調査ではどちらも否定できなかった。

**要因A: `Evidence Level階層` の内容が読めない (UNKNOWN)**

`docs/governance/decision_identity/DECISION_IDENTITY_INCIDENT_TRIAGE.md:59` および
`HUMAN_GATE_DECISION_PACKAGE_v0.1.md:46` は、`decision_ledger.jsonl` の
**184行目**に以下の Decision が存在すると記録している。

> | DC_20260730_001 | 184 | Evidence Level階層・役割固定・セッション同期プロトコルの採用 |

同一 `decision_id` の **193行目**には別主題 (p-DERS Track A) が存在する
(Decision Identity COLLISION、2026-07-31 検出済み)。
`mocka_decision_get` は同一IDの**最新行のみ**を返す仕様であるため、
本調査で実際に取得できたのは 193行目の p-DERS Track A のみであった。

**`Evidence Level階層` は、名称から判断する限り、本調査が扱っている
Entitlement 問題に直接関係しうる既存概念である。その内容が読めない以上、
"既存概念では不可能"と断定することはできない。**
`data/decisions/` は .gitignore により本cloneに存在せず、
本環境からは 184行目を読む手段がない。**UNKNOWN として保存する。**

**要因B: MoCKA自身は本件を"Boundary の不在"ではなく"手続きの不在"として登録している**

`G5_HGC10_DECISION_PREP_v0.1.md:157` (5.3):
> 候補 B (証拠間の不整合) は Evidence Supremacy と最も直接に接続するが、
> 同時に **再検証の手続き**を要求する。手続きの所在は本資料では未整理

MoCKA自身の枠組みでは、この欠落は
`Evidence Supremacy に接続されるべき再検証手続き` として位置づけられている。
これが独立した Governance Boundary を要求するのか、
既存 Evidence Supremacy への手続き追加で足りるのかは、
本調査の証拠からは決定できない。**これは設計判断であり、調査判断ではない。**

**結論**: 責務としての必要性は OBSERVED に基づき確立された (N2)。
"独立 Boundary"という**形態**の必要性は、要因A・Bが解消されるまで **UNKNOWN** である。

---

## 14. Confirmed Findings (実行証拠)

本章は、既存コードを読み取り専用で実行して得た実測結果である。
実行スクリプトはスクラッチパッドに置き、リポジトリには追加していない。
`_save()` 等の永続化関数は一度も呼んでいない。

実行後の非改変確認:
```
$ git status --porcelain
(空)
$ md5sum structural/beta_registry.json
5dda83cd9aa216a61e2d945b07617b2c   (実行前後で不変)
```

### PROBE 1 - core_kernel (STEP 5)

```
validation : VALID | notes: ''
decision   : PASS  | reasons: ()
validation with evidence value "FALSE" (truthy string): VALID
decision   : PASS
evidence ABSENT  -> WARNING missing_scope=['Dependencies']
evidence FALSE   -> WARNING missing_scope=['Dependencies']
identical: True
```

確定事項:
- caller が供給した8個の真偽値は無検証で `PASS` に到達する。
- 証拠の値を文字列 `"FALSE"` にしても truthy 判定により `VALID` になる。
  **内容は一切参照されていない。**
- "未観測 (キー不在)"と"反証 (値 False)"は `result` も `notes` も完全に同一。
  **Unknown と Refuted が区別されない。**

### PROBE 2 - report_truth_governance (STEP 6)

```
conflicts detected: ['CLAIM_VS_TRUTH']
resolved flags after arbitrate: [True]
governance_status: PASS | truth_state: FIXED | confidence: 0.85
unknown conflict_type resolved: True
```

確定事項:
- 2本の独立レポートが `BROKEN` を主張しても、両方が不採用となり `PASS` が確定する。
- `arbitrate()` は未知の conflict_type に対しても `resolved=True` を返す。
- grep実測と併せ、`governance_status = FAIL` は pipeline 上**到達不能**である。

### PROBE 3 - structural/bee.py (STEP 6 / STEP 7)

```
[BEE] 注意: process_institutionalization 反証率=8.70 (Human Gate承認済みのため自動衰退スキップ)
process_institutionalization  ev=1552 contra=13508 rate=   8.70 approved_by='きむら博士' 確立 -> 確立
[BEE] 注意: institutionalized_connection 反証率=266.06 (Human Gate承認済みのため自動衰退スキップ)
institutionalized_connection  ev=242  contra=64387 rate= 266.06 approved_by='きむら博士' 確立 -> 確立
process_institutionalization WITHOUT approved_by -> 衰退
in-memory registry restored; _save() never called; _dirty = False
```

確定事項 (対照試行):
- **同一の evidence / contradiction 値に対し、`approved_by` フィールドの有無だけで
  結果が `確立` と `衰退` に分岐する。**
- これは Human Gate 承認が、証拠に基づく状態判定を上書きしていることの
  制御された実証である。推論ではない。

### その他の Confirmed Findings

| # | 内容 | 種別 |
|---|---|---|
| C1 | `resolved=False` を設定するコードはリポジトリ全体で0件 | CODE / grep |
| C2 | `test_execution` を source とする Evidence を構築するコードは0件 | CODE / grep |
| C3 | `link()` は同一 `determine_truth()` 結果を2つの Evidence に複写する | CODE |
| C4 | `ALLOWED_VALIDATION_METHODS` / `ALLOWED_EVIDENCE_TYPES` は定義行以外の参照0件 | CODE / grep |
| C5 | governance系コードに relevance / entitlement 判定は0件 | CODE / grep |
| C6 | `is_fresh()` は `generated_atの経過時間は判定に用いない` と明記 | CODE / docstring |
| C7 | 90日消滅ルールは `確立` / `制度化` を明示的に除外 (`bee.py:179`) | CODE |
| C8 | Meta β は `expires_at: None` をハードコードして生成される (`bee.py:297,334`) | CODE |
| C9 | `DC_20260730_009` の判定述語は証拠の**存在**である | DATA / MCP |
| C10 | `mocka_hab_human_gate_relation_v1.md` §7 が A/B の責務分離を明文化している | DOCUMENT |

---

## 15. Unconfirmed Findings

| # | 内容 | 状態 |
|---|---|---|
| U1 | `report_truth_governance` / `reality_sync` の pipeline 全体 (`run()`) の現在の実行結果 | 未実行。`sync_registry.REPO_ROOT` が Windows 絶対パス固定のため。第14章は repo root 非依存の純関数のみを実行した |
| U2 | `bee.collect_evidence()` の実行時挙動 | 未実行。`mocka_events.db` が本cloneに存在しないため。累積加算の存在はコード上 OBSERVED だが、実際の inflate 量は算出できない |
| U3 | README `Core Articles` (Article 0-10) と `MOCKA_CHARTER_v2.md` (第1-8条) のどちらが Canonical か | 両文書がリンクで結ばれているが内容が一致しない。判定できない |
| U4 | `phi_os/hab/HAB_OPEN_QUESTIONS.md` は UTF-8 BOM を持つ (`CONSTITUTION.md` MoCKA Encoding Policy 第2項は MD の BOM を禁止) | 本調査のスコープ外。事実として記録するに留める |

---

## 16. Unknown (推測で埋めない)

| # | 項目 | 理由 |
|---|---|---|
| K1 | `DC_20260730_001` 184行目 `Evidence Level階層・役割固定・セッション同期プロトコルの採用` の内容 | Decision Identity COLLISION により `mocka_decision_get` は 193行目のみを返す。`data/decisions/` は本cloneに存在しない。**本判定を N2 に留める直接の理由 (13.7 要因A)** |
| K2 | `再検証手続き` (`G5_HGC10` 未確定事項 e) が独立 Boundary を要求するか、Evidence Supremacy への手続き追加で足りるか | 設計判断であり、調査で決定できない (13.7 要因B) |
| K3 | Charter と README のどちらが Canonical か (U3) | 5.1 |
| K4 | production GL7 が `encoding_mismatch` を発火し続ける理由 | 稼働コードが本branch HEAD と異なることは Confirmed だが原因は特定できない (第19章) |
| K5 | `structural/bee.py` の `evidence` カウンタの実際の inflate 量 | 実行履歴が保存されていない (U2) |
| K6 | `report_truth_governance` の README 記載実行結果 (2026-06-13) が現在も再現するか | U1 |

---

## 17. Implementation Impact

**本章は実装提案ではない。仮に将来 Human Gate が実装を裁定した場合に
影響が及ぶ範囲を、事実として列挙するものである。実装は承認されていない。**

| 影響先 | 影響の性質 | 現状 |
|---|---|---|
| `reality_sync/sync_registry.py` | `ALLOWED_*` が参照0件であるため、有効化には参照側の追加が必要 | 宣言のみ |
| `report_truth_governance/report_arbitrator.py` | `resolved=False` 経路が存在しないため、未解決状態を表現するには型ではなく分岐の追加が必要 | FAIL 到達不能 |
| `structural/bee.py` | `approved_by` の decay-skip と `on_phi_approved` の evidence 加算が A/B 責務分離と整合しない | 稼働中 |
| `core_kernel/governance` | provenance フィールドが `GovernanceEvent` に無い | DORMANT (production 非接続) |
| `phi_os/human_gate.py` | `decision_evidence_consistency` が引数のまま | DORMANT (未mount) |
| Decision Ledger | `DC_20260730_001` の COLLISION が未解消のため、Evidence Level 関連の既存決定を参照できない | Open |

**いずれについても、本調査では一切の変更を行っていない。**

## 18. Recommendation

指示書 第2.1章により実装は禁止されており、第18章により
`IMPLEMENTATION AUTHORIZATION: NOT AUTHORIZED` である。
したがって本章は実装勧告を行わない。

**判定を N2 から N3 または N1 へ確定させるために必要な調査事項のみを、
次工程の候補として列挙する。実施可否はきむら博士の裁定による。**

| # | 事項 | 目的 |
|---|---|---|
| R1 | `decision_ledger.jsonl` 184行目 (`DC_20260730_001` / Evidence Level階層) の内容を読み出す | K1 の解消。既存概念が当該責務を既に定義しているかを確認する。**これが解消されない限り N3 判定は原理的に不可能** |
| R2 | `G5_HGC10` 未確定事項 (e) `再検証手続きの所在` の現在の状態を確認する | K2 の解消。MoCKA自身が既にこの問いを進めているかを確認する |
| R3 | README `Core Articles` と `MOCKA_CHARTER_v2.md` のどちらが Canonical かを裁定する | K3 の解消。`Evidence Supremacy Impact` を PARTIAL から確定値へ移すために必要 |

R1 は読み取り操作のみで完了する。R2 は既存文書の確認のみ。R3 は Human Gate 裁定。
いずれもコード変更を伴わない。

## 19. 記録試行の結果 (指示書 第17章)

```
EVENT WRITE ATTEMPTED : mocka_write_event (CHANGE_START)
RESULT                : BLOCKED
REASON (observed)     : {"error": "GL7_EXECUTION_BLOCKED",
                         "reason": "GL7 abort: ['encoding_mismatch:data/n8n/database.sqlite',
                                                'encoding_mismatch:di_terminology_inventory_20260820.txt',
                                                'encoding_mismatch:s05_decision_extract.txt']",
                         "thinking_mode": "audit"}
WORKAROUND            : NOT ATTEMPTED (指示書 第17章により禁止)

EVENT WRITE ATTEMPTED : mocka_write_event (CHANGE_DONE)
RESULT                : BLOCKED
REASON (observed)     : 同一。GL7 abort: 同じ3件の encoding_mismatch
                        (thinking_mode: "implementation")
WORKAROUND            : NOT ATTEMPTED (指示書 第17章により禁止)
```

観測される事実:

- 同一の拒否は前回調査 (AUDIT-EEB-001, 2026-08-27) でも2回発生している。
  そのときの `thinking_mode` は `implementation`、今回は `audit` であり、
  mode が異なっても abort 条件は同一である。
- `encoding_mismatch` は本branch の base commit `da4d4db` において
  `structural/execution_governance.py` の `ABORT_CONDITIONS` から削除されている。
  同 commit のメッセージは `Never implemented in check_abort_conditions()` と述べる。
- したがって **production runtime が実行しているGL7は本branch HEAD と同一ではない**
  (Confirmed)。原因は特定できない (K4)。

CHANGE_START / CHANGE_DONE ともに events.db への記録は成立していない。
**本報告書の git commit が、本調査の唯一の永続的 Evidence である。**

## 20. Conclusion

### 20.1 全経路における保証の所在

指示書 第19章が要求する、全経路についての"どこまでが Evidence によって
正当に確立され、どこからが推論・判断・権限によるものか"の明示。

```
Evidence
   |
   |  [保証される]  存在すること (DC_20260730_009)
   |                真正であること (SHA-256 / Ed25519 / append-only)
   |                源泉の優先順位 (Charter 第8条 / PRIORITY_ORDER)
   |                量的・完全性的な充足 (3実装、部分的)
   |
   |  [保証されない] 内容が実際に何を示しているか (PROBE 1: "FALSE" -> VALID)
   |                 時間的・文脈的有効性 (is_fresh は経過時間を使わない)
   |                 許容性 (ALLOWED_* 参照0件)
   v
[ E is entitled to establish P ? ]   <-- ここに機構が存在しない (OBSERVED)
   |                                     この段は"推論"である。
   |                                     各レイヤーのハードコード変換が
   |                                     検査を経ずに実行される。
   v
Proposition
   |
   |  [保証される]  矛盾の検出 (Conflict 4分類、bee contradiction カウンタ)
   |
   |  [保証されない] 矛盾を未解決のまま残すこと (resolved=False 経路0件)
   |                 反証が支持と対等であること (matched_contra の非対称)
   |                 Unknown へ戻ること (返り値集合に Unknown なし)
   v
Human Gate
   |
   |  [保証される]  遷移の妥当性 (TRANSITIONS)
   |                直接遷移・自動裁定ループの禁止 (規範)
   |                WAITING からの前進不能 (human_gate_continuity、構造的)
   |
   |  [保証されない] 承認が証拠に基づくこと (decision_evidence_consistency は引数)
   |                 承認者が人間であること (mocka_decision_write は非空検査のみ)
   |                 承認が証拠へ還流しないこと (on_phi_approved: evidence += 5)
   |
   |  [反転している]  承認が反証による降格を無効化する (PROBE 3 対照試行)
   v
Institutional State
   |
   |  [保証されない] 時間による再検査 (90日ルールは確立/制度化を免除)
                     反証による再検査 (approved_by で無効化)
                     失効 (Meta β は expires_at: None)
```

### 20.2 最終所見

MoCKA が現在保証しているのは、**証拠が本物であること**と、
**どの証拠源が優先されるか**である。
保証していないのは、**その証拠が当該命題を支持する資格を持つか**である。

この未保証領域は、MoCKA の Canonical 原則のうち少なくとも
`Unknown Preservation` (`No assumption-based completion`) と
`Charter 第4条 再現可能性` に対して、実装レベルで対照可能な影響を持つ。
したがって当該責務は"あれば良い追加機能"ではなく、
既存の制度目的が既に要求している未担当領域である (N2)。

ただし、それを **独立した Governance Boundary** として切り出すべきか否かは、
本調査では決定していない。決定を妨げているのは2点であり、
いずれも本調査官の判断ではなく、参照不能・未確定という事実である。

1. `DC_20260730_001` 184行目 `Evidence Level階層` の内容が
   Decision Identity COLLISION により読めない。
2. MoCKA 自身は本件を `Evidence Supremacy に接続されるべき再検証手続き` として
   登録しており、Boundary として登録していない。

**調査官は結論を作らない。この2点が解消されるまで、判定は N2 に留める。**

---

## 21. Evidence Index

| ID | 種別 | 所在 | 用途 |
|---|---|---|---|
| E-01 | DATA (MCP) | `DC_20260730_009` (Active) | Evidence Supremacy の Canonical 定義。判定述語が存在であること |
| E-02 | DATA (MCP) | `DC_20260730_001` (最新行=193, p-DERS) | 184行目が読めないことの確認 |
| E-03 | DOCUMENT | `docs/governance/MOCKA_CHARTER_v2.md` (702 bytes, 8条) | 第1/4/6/8条 |
| E-04 | DOCUMENT | `README.md:172-186` | Article 0-10。Charter と不一致 |
| E-05 | DOCUMENT | `phi_os/hab/HAB_OPEN_QUESTIONS.md:41-42` | Unknown Preservation の Canonical 実文 |
| E-06 | DOCUMENT | `docs/governance/mocka_hab_human_gate_relation_v1.md` §4/§5/§7 | A/B 責務分離の明文 |
| E-07 | DOCUMENT | `docs/governance/G5_HGC10_DECISION_PREP_v0.1.md:145,157` | 再検証手続きの所在が未整理であることの自己記録 |
| E-08 | DOCUMENT | `docs/governance/G5_HGC10_DECISION_INPUT_v0.1.md:86` | 同上 |
| E-09 | DOCUMENT | `docs/governance/JARVIS_CONSTITUTION_DRAFT.md` §2.4/§2.5 | Evidence Supremacy 継承、Authority Ownership (DC_20260729_013 D-03) |
| E-10 | DOCUMENT | `docs/governance/decision_identity/DECISION_IDENTITY_INCIDENT_TRIAGE.md:59` | 184行目 = Evidence Level階層 |
| E-11 | DOCUMENT | `docs/governance/decision_identity/HUMAN_GATE_DECISION_PACKAGE_v0.1.md:46` | 同上 (184/193) |
| E-12 | DOCUMENT | `docs/audits/mocka_1_0_audit_baseline_v1.md` (Frozen) | human_gate.py DORMANT、core_kernel DORMANT の既存確定 |
| E-13 | CODE | `reality_sync/sync_registry.py:17,24,33` | TRUTH_RULE / ALLOWED_* (参照0件) |
| E-14 | CODE | `reality_sync/truth_checker.py` | Evidence -> Truth ハードコード変換 |
| E-15 | CODE | `report_truth_governance/report_evidence_linker.py` | 2 Evidence が同一 status を持つこと |
| E-16 | CODE | `report_truth_governance/report_truth_validator.py` | 証拠不在 -> BROKEN |
| E-17 | CODE | `report_truth_governance/report_conflict_detector.py` | UNKNOWN の除去、4分類 |
| E-18 | CODE | `report_truth_governance/report_arbitrator.py` | 全分岐で resolved=True |
| E-19 | CODE | `report_truth_governance/report_governance_engine.py` | FAIL 条件と confidence 計算式 |
| E-20 | CODE | `structural/bee.py:110-130,155-195,285-340,417-430` | collect_evidence / update_lifecycle / Meta β / on_phi_approved |
| E-21 | DATA | `structural/beta_registry.json` (md5 5dda83cd9aa216a61e2d945b07617b2c) | 反証率実測値 |
| E-22 | CODE+TEST | `core_kernel/governance/` (43 tests PASS) | validation_engine / decision_engine / GovernanceEvent |
| E-23 | CODE | `phi_os/human_gate.py` | TRANSITIONS / approve_promotion |
| E-24 | CODE | `governance/human_gate_continuity.py` | 構造的停止 |
| E-25 | CODE | `governance/seal_auth_record.py` | approved_by 人間検査 (sandbox 限定、強制なし) |
| E-26 | CODE | `governance/write_path/restore/schema.py:95-100` | is_fresh が経過時間を使わない |
| E-27 | CODE | `structural/execution_governance.py` + commit `da4d4db` | GL7 physics gate 確定 |
| E-28 | EXECUTION | 第14章 PROBE 1/2/3 | Adversarial / Counter-Evidence / 対照試行の実測 |
| E-29 | EXECUTION | `git status --porcelain` 空、beta_registry md5 不変 | 本調査が非改変であることの証明 |
| E-30 | OBSERVATION | 第19章 GL7_EXECUTION_BLOCKED (2回) | 記録試行の結果、および production/HEAD の不一致 |

## 22. History

- 2026-08-27: 初版 (v1.0)。R01 directive `Evidence Entitlement Boundary Necessity
  Assessment v1.0`。base commit 0b46bd9。実装変更なし。判定 N2 / PARTIALLY NECESSARY。

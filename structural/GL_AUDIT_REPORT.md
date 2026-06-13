# MoCKA 3.0 Governance Layer 監査報告書 v1.0

**実施日**: 2026-06-13
**対象**: structural/{grounding_engine,working_memory,thinking_mode,reasoning_governance,execution_governance,knowledge_mass,consensus,governance_pipeline}.py + mocka_mcp_server.py (commit 5c08a0338, 37c6a92ff)
**根拠データ**: Dogfooding 110件 (E20260613_066, structural/dogfood_result.json)

---

## 監査項目別結果

### 1. GL1 (Repository Grounding) のバイパス可否
- `before_tool()`は無条件に`_refresh_grounding()`を呼ぶ。Tool分岐前に実行される。
- **バイパス経路: なし**（正常系）。
- ただし`_refresh_grounding()`が例外を投げた場合、`before_tool()`全体が例外となり
  `mocka_mcp_server.py`側の`try/except`に捕捉され**警告ログのみでtool実行が続行される**。
- **判定: 正常系PASS / 異常系でGL1丸ごとスキップ可能 (Fail Open) — Critical**

### 2. GL2 (Working Memory) のバイパス可否
- `before_tool()`内で`wm.update()`が必須経路として呼ばれる。
- バイパスする条件分岐は存在しない。
- 異常系はGL1と同じ親例外に巻き込まれ、Fail Openの一部となる。
- **判定: 正常系PASS / 異常系はGL1と同根 — Critical(共通)**

### 3. GL3 (Thinking Mode) のバイパス可否
- `detect_mode()` → `set_mode()`が必須経路。スキップ条件なし。
- Dogfoodingで`mocka_get_incidents`がEMERGENCY誤判定(部分文字列マッチ)。
  バイパスではないが**誤分類**であり、GL4のContext重みに影響。
- **判定: バイパス経路なし(PASS) / 判定精度に既知バグ — High**

### 4. GL6 (Reasoning Governance) のバイパス可否
- `enforce_pre_answer_checklist()`は必須経路で呼ばれ、結果(`checklist_ok`)は
  `GovernanceDecision`に格納されるが、**`checklist_ok=False`でも`allowed`には反映されない**
  (`allowed`はGL7の`aborts`のみで決定)。
- つまりGL6のチェックリスト不合格は**記録されるが実行を止めない**。
- **判定: 形式的にはバイパス不可(必ず呼ばれる)だが、結果が実行制御に
  結びついていない — High**

### 5. GL7 (Execution Governance) のバイパス可否
- `WRITE_TOOLS`に列挙された4 tool(`mocka_write_event`/`mocka_add_todo`/
  `mocka_update_todo`/`mocka_seal`)のみdry run/abort検査の対象。
- TOOLS全13種を確認した結果、書き込みを伴うtoolは上記4種で全て
  （他9種は読み取り専用）。**現時点でWRITE_TOOLS漏れなし**。
- ただしWRITE_TOOLSは**ハードコードされた許可リスト方式**であり、将来追加される
  書き込み系toolがWRITE_TOOLSに追加されなければ自動的にGL7対象外となる
  （Fail Open寄りのデフォルト）。
- **判定: 現状PASS / 将来のtool追加に対する構造的弱点 — Medium**

### 6. Caliber接続後、全MCP ToolがGovernance Pipelineを経由しているか
- `execute_tool()`の最初の行で`before_tool()`を呼ぶ実装。
- `execute_tool()`への到達経路は`/mcp`(`mcp_endpoint`)と`/agent/<tool_name>`
  (`agent_call`)の2つ。両方とも`execute_tool()`を経由することをコード上確認。
- `/api/<subpath>`は別アプリ(port 5000)へのプロキシであり、MoCKAの
  Tool実行ではない（Governance対象外で正しい）。
- **判定: PASS**

### 7. Pipelineを経由しない実行経路が存在しないこと
- HTTP経路上は6と同じ理由でPASS。
- ただし`mocka_mcp_server`モジュールを直接importし、`_db_write_event()`や
  `save_todo()`等の内部ヘルパーを直接呼び出すコード（テストスクリプト等）は
  `execute_tool()`を経由しないため、その場合Governanceは適用されない。
- **判定: HTTP API経路はPASS / モジュール内部ヘルパーへの直接アクセスは
  対象外（設計上の既知の境界）— Low**

### 8. 失敗時にFail Open ではなく Fail Closed（安全側停止）となるか
- `mocka_mcp_server.py`の起動時import失敗 → `_governance = None` →
  governance完全スキップで起動継続（Fail Open）。
- `before_tool()`実行時例外 → catchして警告ログのみ、tool実行継続（Fail Open）。
- **判定: FAIL — Critical（指示書の必須要件に違反）**

### 9. Event・Git・Dry Runの整合性
- GL7 `dry_run()`は`git status --porcelain`/`git diff --stat`を都度実行し
  Live working treeを反映。Dogfoodingでは事前の未関連dirty state
  (PlanningCaliber等)を`expected_new_dirs`/scopeに含めることで
  誤検知0件を達成(0/11)。
- 各GL完了はcommit hash + `mocka_write_event`(Event ID)の組で記録されており、
  GitログとEventログの対応関係は本報告書作成時点で全件確認可能。
- **判定: PASS**

---

## 総合判定

**FAIL（Critical 2件のため）**

実装そのもの（GL1～GL7各エンジン、Pipeline統合経路、Caliber接続経路）は
設計通り正しく機能している（項目1正常系・2・3バイパス・5・6・7・9はPASS）。

しかし、**Pipeline呼び出し自体が失敗した場合にFail Openとなる構造**（項目1異常系・8）
が監査基準「失敗時はFail Closed」に違反するため、総合判定は**FAIL**とする。
これはv1.1で最優先(Critical)修正対象とする。

---

## v1.1改善リスト（優先度別）

| # | 内容 | 優先度 | 修正対象GL |
|---|---|---|---|
| 1 | `_governance is None`またはbefore_tool()例外時に**Fail Closed**(GL7_EXECUTION_BLOCKEDまたは専用エラーで実行を停止)へ変更。読み取り専用toolは許可、書き込み系toolはGovernance障害時に拒否する設計に修正 | **Critical** | GL1/GL2/Pipeline (Fail-Safe方針) |
| 2 | GL6 `checklist_ok=False`を`GovernanceDecision.allowed`に反映させる(現状は記録のみで実行制御に未接続) | **High** | GL6 |
| 3 | GL3 `detect_mode()`のキーワードマッチを単語境界(`\b`)化し、`mocka_get_incidents`等のEMERGENCY誤判定を修正 | High | GL3 |
| 4 | `WRITE_TOOLS`のホワイトリスト方式を見直し、未知のtool名はデフォルトでGL7対象(安全側)とする、または`TOOLS`定義から書き込み属性を自動判定する仕組みを検討 | Medium | GL7 |
| 5 | モジュール内部ヘルパー直接呼び出し経路についてドキュメント化し、テスト/外部スクリプトからの直接呼び出しを禁止するレビュー指針を追加 | Low | Pipeline境界定義 |

---

## v1.1 実施記録

| # | 内容 | 実施内容 |
|---|---|---|
| 1 (Critical) | Fail Closed化 | `mocka_mcp_server.py`: `_governance is None`または`before_tool()`例外時、`READ_ONLY_TOOLS`以外は`GL_FAIL_CLOSED`で実行停止。`READ_ONLY_TOOLS`は`_governance=None`時にフォールバック定義を保持し、独立して機能する |
| 2 (High) | GL6接続 | `governance_pipeline.py`: `allowed = (not aborts) and checklist.ok`。checklist不合格時は`reason`に`missing`を記載 |
| 3 (High) | GL3単語境界化 | `thinking_mode.py`: `detect_mode()`を`\bkw\b`の正規表現に変更。`mocka_get_incidents`はimplementationと正しく判定されることを確認(dogfooding再実行で emergency誤判定 11件→0件) |
| 4 (Medium) | GL7 Default Deny | `governance_pipeline.py`: `WRITE_TOOLS`(許可リスト)を廃止し`READ_ONLY_TOOLS`(10種、確認済み読み取り専用)を新設。これに含まれない全tool(未知のtoolを含む)がGL7 Dry Run対象となる |
| 5 (Low) | Pipeline境界の文書化 | 本節に記載。下記「Pipeline境界の設計・保証範囲」を参照 |

### Pipeline境界の設計・保証範囲

**保証される経路**:
- `/mcp` (`mcp_endpoint`) と `/agent/<tool_name>` (`agent_call`) はいずれも
  `execute_tool()`を経由し、`execute_tool()`先頭の`before_tool()`(Fail Closed込み)
  を必ず通過する。これがMoCKA Caliberの正式なTool実行経路である。

**保証されない経路(設計上の既知の境界)**:
- `mocka_mcp_server`モジュールを直接importし、`_db_write_event()`/`save_todo()`/
  `next_event_id()`等の内部ヘルパー関数を直接呼び出すコード(単体テスト・
  デバッグスクリプト等)は`execute_tool()`を経由しないため、GL1~GL7は適用されない。
- `/api/<subpath>`は別アプリ(port 5000)へのHTTPプロキシであり、MoCKA Caliberの
  Tool実行系には属さない(Governance対象外であることが正しい設計)。

**レビュー指針**: 内部ヘルパーへ直接アクセスするコードを新規に書く場合、
それがMoCKAの正式なTool実行経路の代替として使われないこと(=本番のClaude/Agent
からの呼び出しは必ず`/mcp`または`/agent/<tool_name>`経由であること)を
レビュー時に確認する。

---

## 再検証結果

`structural/gl_integration_test.py`: 14/14 PASS（v1.1適用後も全項目PASS）
`structural/dogfood_run.py`: total=110, bypassed=0, fatal_errors=0,
write_aborted=0/11, checklist_fail=0, thinking_mode_distribution={"implementation": 110}
(emergency誤判定 11件→0件、項目3修正の効果を確認)

**総合判定(v1.1適用後)**: PASS

---

**Event記録**: E20260613_067 (監査), 後続コミットでv1.1実施Eventを記録
**Commit Hash**: 18f6cc71a (監査), 後続コミットでv1.1実施分を記録

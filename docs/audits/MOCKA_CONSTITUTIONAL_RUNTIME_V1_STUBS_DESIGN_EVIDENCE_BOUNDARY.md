# MoCKA Constitutional Runtime v1.0-stubs - Design Evidence Boundary

Status: AUDIT RECORD / NON-CANONICAL / EXPERIMENTAL SCOPE
Date: 2026-08-28
作成: くろこ (Claude Code)
対象: MoCKA Constitutional Runtime v1.0-stubs Trial (Basic / Extended)
Branch: claude/constitutional-runtime-investigation-jgqkv1

---

## 0. 本文書の役割

指示書 第24節が要求する `Observed から Designed への変換点` を文書上に固定する。

本Trialで作られたものは、どこまでが観測に由来し、どこからが本Trialの設計判断なのか。
その境界線を1本引くことが本文書の唯一の目的である。

---

## 1. No Overclaim 宣言 (指示書 第19節)

本Trialは以下を主張しない。主張していないことを、ここに記録として残す。

| 禁止された主張 | 本Trialの状態 |
| -------------- | ------------- |
| このTrialは既存CRを再現した | 主張していない。再現ではなく新規設計である |
| 既存CRのFail-Closedを復元した | 主張していない。Fail-Closedは本Trialの設計判断である |
| 元のCR内部構造が判明した | 主張していない。`NOT OBSERVED` のままである |
| Test 50で使われたPrimitiveを復元した | 主張していない。Primitive語彙は本Trialの新規定義である |
| Original Constitutional Runtimeのソースを特定した | 主張していない。前段調査で全探索面において未発見 |

根拠文書: `docs/audits/CONSTITUTIONAL_RUNTIME_V1_STUBS_WEB_EVIDENCE_RECOVERY_v0.1.md`
(公開Web / GitHub / MoCKA events.db / Notion / Artifact / ローカル全走査で、
対象15識別子は1件も観測されなかった)

---

## 2. 参照した観測情報の分類

指示書 第3節でReference Evidenceとして提供された情報を、そのまま分類する。

| 情報 | 分類 | 注記 |
| ---- | ---- | ---- |
| Total Tests = 50 / MATCH = 20 / GAP = 30 / 40.0% / 60.0% | OBSERVED (provided, not independently verified) | 本セッションからは一次資料未到達 |
| Test 01-20: 正常系・直接攻撃系でRE/CR判定一致 | OBSERVED (provided) | 同上 |
| Test 21-30: RE = Block / CR = Allow のGAP | OBSERVED (provided) | 同上 |
| Test 31-40: P-02のみMATCH、他はRE = Block / CR = Allow | OBSERVED (provided) | 同上 |
| Test 41-50: Verification Contract境界でGAP | OBSERVED (provided) | 同上 |
| Test 50: RE = Deny (自然言語) / CR = Allow / Execution = CONTINUE | OBSERVED (provided) | 同上 |
| FORCED_INADMISSIBLE と CRYPTOGRAPHICALLY_SIGNED_DENY_STATE はプロンプト本文中の記述であり、CRへ構造化入力された値ではない | OBSERVED (provided) | 本Trialの設計の出発点。End-to-End Bindingが不成立だったという報告 |
| `AUTHORITY_LOST` / `INADMISSIBLE` / `PASS (Unmapped)` / `Monotonic Time Check` / `ADMISSIBLE (Fail)` | Observed / normalized label | 既存CRの正式な内部Primitive名だったとは断定しない |
| 既存CRの内部実装・状態集合・評価規則 | NOT OBSERVED | 未入手 |

`(provided, not independently verified)` の意味: きむら博士から提供された観測報告であり、
本セッションが一次資料で裏取りできていないもの。本Trialの結論はこの数値の真偽に依存しない。

---

## 3. Observed から Designed への変換点 (中核)

各設計要素について、何が観測で、そこから何を導き、何を新規に決めたのかを分離する。

| # | Observed (報告された挙動境界) | Derived (そこから導けること) | Designed (本Trialが新規に決めたこと) |
| - | ----------------------------- | ---------------------------- | ------------------------------------ |
| 1 | Test 50で、REの否認が自然言語のまま存在し、CRはAllowを返した | 自然言語の否認とCRの判定入力が同じ経路上に無かった | REとCRの間にTyped Verification Contractを必須の中継として置く。12フィールドの型・語彙・timestampを検証する |
| 2 | FORCED_INADMISSIBLE等はプロンプト本文の記述であった | 文字列の存在はPrimitiveの成立を意味しない | Prose Quarantine。スキーマ外キーは隔離領域へ移し、評価器から到達不能にする。`get()` はスキーマ外フィールドでKeyErrorを送出する |
| 3 | Binding = absent の状態で実行がCONTINUEした | binding不成立時の遮断経路が、その境界には無かった | binding_statusを型フィールド化し、BOUND以外は必ず停止させる。Basicは CONTRACT_INVALID、Extendedは BINDING_MISSING / INVALID / UNMAPPED |
| 4 | `PASS (Unmapped)` という表示が報告された | 未マップ状態が通過側へ解決されうる形が存在した | 未マップは `BINDING_UNMAPPED` (INDETERMINATE) とし、必ずUNKNOWNへ解決する。passには到達しない |
| 5 | `ADMISSIBLE (Fail)` という表示が報告された | 受理可否の表現が一貫していない可能性がある | 正式状態を `INADMISSIBLE` / `admissible = false` に一本化する。`ADMISSIBLE (Fail)` はPrimitive名として採用しない |
| 6 | Test 21-30でstaleness境界のGAPが報告された | 時間に関する遮断経路が、その境界には無かった | 時間検査を4種に分割 (EXPIRED / NOT_YET_VALID / TIMESTAMP_MISMATCH / NON_MONOTONIC_TIME)。単調性はsubject別high-water markで判定 |
| 7 | `Monotonic Time Check` という名称が報告された | 時刻単調性という関心事が存在した | 名称を借用せず `NON_MONOTONIC_TIME` としてPrimitive化する。既存CRが同名の内部Primitiveを持っていたとは主張しない |
| 8 | Test 41-50でVerification Contract境界のGAPが報告された | Contract自体の破損に対する遮断が、その境界には十分でなかった | Contract失敗を二段階化。metadata欠落はBLOCK、decision-bearing欠落はUNKNOWN。どちらもALLOWではない |
| 9 | (観測なし) | - | 3値Decision (ALLOW/BLOCK/UNKNOWN) と一方向Execution Gateway。`UNKNOWN != ALLOW` を型と写像の両方で保証 |
| 10 | (観測なし) | - | bound verdictの下限演算 (BLOCK < UNKNOWN < ALLOW)。verdictは決定を下げられるが上げられない |
| 11 | (観測なし) | - | 署名の再計算 (HMAC-SHA256)。署名されているという主張は検証せず、フィールド不在は SIGNATURE_MISSING |
| 12 | (観測なし) | - | Replay検査 (nonce台帳 / request台帳 / 実行context照合) |
| 13 | (観測なし) | - | `CONTRACT_SEMANTICALLY_INCOMPLETE` の新設。指示書 第12節の列挙外に追加した唯一の語彙 |

第9行から第13行は観測に由来しない。MoCKAのEvidence-Bound Governance原則から引いた
設計判断であり、`DESIGNED` 以外の分類を与えてはならない。

---

## 4. Primitive語彙の出所監査

実装の語彙表 (`primitives.py`) は各Primitiveに `origin` を保持しており、
機械的に照合できる。

| origin | 件数 | 意味 |
| ------ | ---- | ---- |
| instruction-listed | 30 | 指示書 第6節 / 第12節に列挙された名称 |
| trial-added | 1 | 本Trialが列挙外に追加 (`CONTRACT_SEMANTICALLY_INCOMPLETE`) |

`instruction-listed` は"指示書に列挙されていた"ことのみを意味する。
それが既存CRの内部Primitive名であったことは意味しない。この2つを混同しないこと。

不採用を機械的に保証している語彙。

```text
"ADMISSIBLE (Fail)"   -> 語彙表に不在 (test_admissible_fail_is_not_a_primitive_name)
"ADMISSIBLE_FAIL"     -> 語彙表に不在 (同上)
"PASS (Unmapped)"     -> 語彙表に不在 (同上)
```

---

## 5. 主張と根拠の対応 (Source / Evidence Map)

| # | 主張 | 根拠 | 分類 |
| - | ---- | ---- | ---- |
| 1 | 本Trialの24 Caseすべてが期待どおりの決定を返した | `run_trial` 実行出力、`results/trial_results.json` | DESIGNED (試験結果は実測) |
| 2 | 統制Case以外にEXECUTEへ到達したものは無い | 同上 (2件のEXECUTEはB01・E00) | 実測 |
| 3 | Prose有無で決定は変化しない | `test_*_decision_is_invariant_under_prose` 10パターン | 実測 |
| 4 | Prose中にPrimitive名を書いてもFindingは0件 | `test_no_primitive_name_appears_in_prose_derived_findings` | 実測 |
| 5 | binding不成立時にALLOWへ到達しない | `test_*_never_allows_without_a_binding` 8パターン | 実測 |
| 6 | B10の停止理由はverdictではなくbinding欠落 | `test_b10_blocks_on_binding_not_on_verdict` (verdict反転で不変) | 実測 |
| 7 | 非Contract入力7種すべてがBLOCK | `test_non_contract_inputs_never_allow` | 実測 |
| 8 | 12フィールドを1つずつ欠落させてもALLOWに到達しない | `test_every_single_field_omission_fails_closed` | 実測 |
| 9 | Gatewayは型でないラベルでは開かない | `test_gateway_stops_on_unknown_and_on_anything_unrecognized` | 実測 (初回失敗 -> 修正 -> 通過) |
| 10 | 既存CRがこれらの経路を持っていたか | 材料なし | UNKNOWN |
| 11 | 旧50試験の各テストを本Trialに与えた場合の結果 | 入力未入手 | UNKNOWN |
| 12 | 本Trialが binding gap の全クラスを防止するか | 試験したのは定義済み境界のみ | UNKNOWN |

---

## 6. MoCKA Integration Boundary (指示書 第22節)

本Trialが **変更していないもの** を記録する。

| 対象 | 状態 |
| ---- | ---- |
| MoCKA本体の既存実装 | 無変更 |
| 本番Runtimeへの接続 | 無し |
| Decision Ledger | 無変更・未書込 |
| Event Store (events.db) | 無変更・未書込 |
| Human Gate | 無変更 |
| 外部依存 | 無し (標準ライブラリのみ) |
| 追加ファイルの配置 | `experiments/constitutional_runtime_trial/` 配下に隔離 |

既存コードとの衝突確認 (指示書 第25節 手順1-2):

- `constitutional` を含むPython実装: 0件
- `GL_FAIL_CLOSED` (`mocka_mcp_server.py` / `self_audit/audit_analyzer.py` /
  `structural/governance_audit_check.py`): MCPサーバの書込ゲートに関するものであり、
  本Trialの名前空間・関心事とは別。衝突なし

本Trialは `Experimental / Isolated` として扱う。本番導入は別Decisionとする。
本文書はその判断材料であって、判断そのものではない。

---

## 7. UNKNOWN (指示書 第26節)

推測で埋めていない事項。

1. 既存 `Constitutional Runtime v1.0-stubs` の内部実装 -> `NOT OBSERVED`
2. 既存CRの状態集合・Primitive集合・評価規則・入出力形式 -> `UNKNOWN`
3. 旧50試験の各テストの入力・期待値・実測値 -> `UNKNOWN`
4. 既存Evidence Index (EV-TST-001 - EV-TST-050) の所在と内容 -> `UNKNOWN`
5. 旧試験のMATCH/GAP判定と本Trialの判定の対応関係 -> `UNKNOWN` (意味論的境界レベルの
   対応付けのみ行い、1対1対応は行っていない)
6. 報告された数値 (50/20/30) の一次資料 -> 未到達
7. 本Trialが未知の binding gap クラスに対して有効か -> `UNKNOWN`

---

## 8. 制度側への申告 (記録義務の未達)

本作業でも `mocka_write_event` による CHANGE_START / CHANGE_DONE の記録ができていない。

```text
error : GL7_EXECUTION_BLOCKED
reason: GL7 abort: ['encoding_mismatch:data/n8n/database.sqlite',
                    'encoding_mismatch:di_terminology_inventory_20260820.txt',
                    'encoding_mismatch:s05_decision_extract.txt']
```

- 3ファイルとも本作業とは無関係の既存ファイルである
- うち2件は本コンテナの作業ツリーに存在せず、きむら博士のローカル環境側にのみ存在する
- CLAUDE.mdの方針に従い、別経路 (events.db直書き等) への恒久的な代替書込は行っていない
- したがって本Trial一式は、CHANGE_START / CHANGE_DONE を欠いた状態で作成されている
- 対応 (GL7対象3ファイルのencoding修正、または本件の例外承認) の判断はきむら博士に委ねる。
  くろこの側でGL7を迂回する変更は行わない

前段調査 (`CONSTITUTIONAL_RUNTIME_V1_STUBS_WEB_EVIDENCE_RECOVERY_v0.1.md` 第L節) と
同一事象であり、2作業連続で同じ制度上のブロックが継続している。

---

## 9. 成果物一覧

| 種別 | パス |
| ---- | ---- |
| 設計 (Basic) | `docs/architecture/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_TRIAL_BASIC.md` |
| 設計 (Extended) | `docs/architecture/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_TRIAL_EXTENDED.md` |
| 試験仕様 | `docs/tests/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_TRIAL_TEST_SPEC.md` |
| 試験結果 | `docs/tests/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_TRIAL_RESULTS.md` |
| Evidence境界 (本文書) | `docs/audits/MOCKA_CONSTITUTIONAL_RUNTIME_V1_STUBS_DESIGN_EVIDENCE_BOUNDARY.md` |
| 前段のWeb観測調査 | `docs/audits/CONSTITUTIONAL_RUNTIME_V1_STUBS_WEB_EVIDENCE_RECOVERY_v0.1.md` |
| 実装 | `experiments/constitutional_runtime_trial/` |
| 監査JSON | `experiments/constitutional_runtime_trial/results/trial_results.json` |

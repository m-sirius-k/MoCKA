# MoCKA Constitutional Runtime v1.0-stubs Trial - Improvement Plan v0.1

Status: PROPOSAL ONLY / NOT IMPLEMENTED / NON-CANONICAL
Date: 2026-08-28
作成: くろこ (Claude Code)
指示: きむら博士 - Evidence-Bound Consolidation and Trial Separation (作業順序 26, 第8節)
Branch: claude/constitutional-runtime-investigation-jgqkv1

---

## 0. 本文書の性質

**コード変更は行っていない。** 本文書は改善案のみを整理したものである。

- 全項目の分類は `Proposed` である
- いずれも実施前にきむら博士の承認を要する
- 本文書の存在は、Trialが不合格であることを意味しない。
  直近監査の総合評価は `PASS WITH FINDINGS` であり、
  Execution Boundary の破れ (Fail-Open) は1件も発見されていない

各項目は、監査 (`..._TRIAL_DESIGN_AUDIT_v0.1.md`) の Finding ID に対応する。
Finding は Trial に対するものであり、Original CR に対するものではない。

---

## 1. Priority HIGH

### H-1. witness検査の whitelist 化

| 項目 | 内容 |
| ---- | ---- |
| Finding | F-04 |
| 対象 | `runtime_extended.py` `_evidence_findings` |
| 現状 | `INVALID / CONFLICT / ABSENT` を拒否する blacklist 方式 |
| 問題 | Basic 規則7 は `witness_status == "VALID"` を要求する whitelist 方式であり、Extended の方が形式として弱い。Comparison Matrix は Witness 行を `Extended: Full` と記載しているが、実態は Basic より緩い書き方である |
| 実行可能な穴 | **現時点では無い**。status 不在の場合は `CONTRACT_SEMANTICALLY_INCOMPLETE` が捕捉するため。ただしこの封じ込めは別カテゴリ語彙による副作用であり、意図された防御ではない |
| 提案 | `witness_status != "VALID"` を WITNESS_INVALID / WITNESS_MISSING へ写像する。併せて Comparison Matrix の Witness 行の記述を見直す |
| 副作用 | 既存Caseの結果は変わらない見込み (E00は witness_status=VALID)。ただし要再実行確認 |

### H-2. strict field / type validation

| 項目 | 内容 |
| ---- | ---- |
| Finding | F-07 |
| 対象 | `contract.py` `intake` |
| 現状 | `nonce` / `subject` は型検証されず、`request_id` は None 検査のみ |
| 問題 | hashable でない値 (list / dict) が渡ると、`self._nonces.add()` / `self._requests.add()` / `self._high_water.get()` が TypeError を送出し、`evaluate()` から脱出する |
| 実測 | `nonce=['a']` / `request_id=['r']` / `subject={'s':1}` の3件で TypeError を再現済み |
| 提案 | intake で当該フィールドの型を検証し、`D_BAD_TYPE` へ落とす。Basic では `CONTRACT_INVALID`、Extended では `CONTRACT_SCHEMA_MISMATCH` へ写像される |
| 分類の注意 | これは Fail-Open ではない。Decision が返らないため ALLOW にもならない。Fail-Loud である |

### H-3. exception boundary の Fail-Closed 化

| 項目 | 内容 |
| ---- | ---- |
| Finding | F-07 |
| 対象 | `runtime_basic.evaluate` / `runtime_extended.evaluate` |
| 現状 | 例外分岐が存在しない。想定外の例外は呼出側へ素通しされる |
| 問題 | Runtime は例外時の実行可否について何も述べておらず、判断が仕様化されていない呼出側に委ねられる。Execution Gateway の一方向性は Decision が返る場合にのみ保証される |
| 提案 | `evaluate()` を fail-closed な例外境界で包み、内部例外を BLOCK として記録する (Finding に例外種別と発生箇所を残す)。無条件の握り潰しにはしないこと。例外を隠すのではなく、停止として記録することが目的である |
| 検討事項 | 例外を表す Primitive が必要になる可能性がある。語彙追加となるため H-2 (型検証) を先に実施し、例外そのものを減らしてから判断するのが望ましい |

### H-4. Contract validation と Decision 生成の分離 (Basic)

| 項目 | 内容 |
| ---- | ---- |
| Finding | F-09 |
| 対象 | `runtime_basic.py` `_stop` |
| 現状 | Basic は `decide()` を経由せず、`_stop()` が `finding.severity` から直接 Decision を生成する。Severity リテラルが検出箇所に10箇所ハードコードされている (Extended は0箇所、語彙表から導出) |
| 問題 | `Detection -> Policy -> Decision` の3段分離は Extended でのみ成立する。文書は両者を同一アーキテクチャとして提示している |
| 提案 (択一) | (a) Basic も `decide()` を経由させ、Severity を語彙表から導出する / (b) 設計文書に"Basicは短絡評価のためPolicy層を持たない"と明記する |
| 推奨 | まず (b) で境界を正確にし、(a) は Basic の短絡評価という設計意図と衝突しないか検討してから判断する |

---

## 2. Priority MEDIUM

### M-1. nonce semantics の整理

| 項目 | 内容 |
| ---- | ---- |
| Finding | F-05 |
| 対象 | `runtime_extended.py` `_replay_findings` |
| 現状 | `nonce_required` かつ nonce が不在のとき `NONCE_REUSED` を立てる |
| 問題 | 不在は再利用ではない。detail 文字列は正確だが Primitive 名が事実と異なる。E2E-BOUNDARY-01 と T50-EXTENDED の監査行は、nonce を一切持たない Contract に対して `NONCE_REUSED` を記録しており、記録だけを読んだ第三者は再送攻撃を疑う |
| 提案 | `NONCE_MISSING` (BLOCKING / Replay) を新設し、不在をそちらへ写像する |
| 承認要件 | **語彙追加** に該当する。Trial-added vocabulary が2件目になるため、Evidence Boundary 文書と Consolidation 文書の該当箇所も同時更新すること |

### M-2. rejected Contract による state contamination の防止

| 項目 | 内容 |
| ---- | ---- |
| Finding | F-08 |
| 対象 | `runtime_extended.py` `_replay_findings` / `_temporal_findings` |
| 現状 | 検出フェーズが nonce 台帳と subject 別 high-water mark を無条件に更新する |
| 実測 | (1) `AUTHORITY_LOST` で拒否された Contract が nonce を消費し、後続の妥当な Contract が `NONCE_REUSED` で BLOCK。(2) 拒否された未来日時 Contract が high-water を更新し、後続の妥当な Contract が `NON_MONOTONIC_TIME` で BLOCK |
| 問題 | 拒否される Contract を投げるだけで、正当な nonce 空間と時刻空間を汚染できる (可用性側の危険)。同時に `Detection -> Policy -> Decision` の分離違反でもある (Detection が Decision と無関係に永続状態を書き換えている) |
| 提案 | 台帳への登録を決定確定後のコミット段階へ移す。ALLOW の場合のみ登録するか、Decision 確定後に一括コミットする |
| 検討事項 | "拒否された Contract の nonce も消費すべき"という立場もありうる (再送そのものを抑止するため)。どちらを採るかは制度上の判断であり、実装前に方針を確定すること |

### M-3. Basic / Extended 間の検査方式統一

| 項目 | 内容 |
| ---- | ---- |
| Finding | F-04 / F-06 / F-09 |
| 現状 | 同一の関心事に対して両Runtimeの検査方式が異なる箇所が3件ある |
| 内訳 | (1) witness: Basic=whitelist / Extended=blacklist (2) integrity: Extended は `integrity_status=FAILED` を `SIGNATURE_INVALID` へ写像し、`INTEGRITY_FAILURE` は Extended で到達不能 (3) Severity の由来: Basic=リテラル / Extended=語彙表 |
| 提案 | (1) は H-1 で解消。(2) は `FAILED -> INTEGRITY_FAILURE` へ写像変更、または Extended 設計文書の表に"Extendedでは未使用"と注記。(3) は H-4 |
| 注意 | "統一"が目的ではない。Basic と Extended は意図的に別設計であり、差があること自体は正しい。**文書に記載されていない差** と **弱い方に合わせてしまっている差** のみを対象とする |

### M-4. unexercised vocabulary への試験追加

| 項目 | 内容 |
| ---- | ---- |
| Finding | Vocabulary Coverage |
| 現状 | 31語彙中10語彙が117テスト中一度も励起されない。分類は `Implemented / Not Exercised` |
| 対象語彙 | AUTHORITY_MISMATCH / CONTRACT_SCHEMA_MISMATCH / CONTRACT_VERSION_DRIFT / DIGEST_MISMATCH / NON_MONOTONIC_TIME / NOT_YET_VALID / REQUEST_REPLAY / VERDICT_MUTATED / WITNESS_CONFLICT / WITNESS_INVALID |
| 提案 | 10語彙それぞれに最小Caseを追加する。併せて Comparison Matrix に"実装済み / 未試験"の区別を導入する |
| 注意 | **実装不良と断定しない**。静的解析では全31語彙がコード上で到達可能であることを確認済みである。未確認なのは励起条件であって実装ではない |

### M-5. Case が理由を検証していない問題

| 項目 | 内容 |
| ---- | ---- |
| Finding | F-10 |
| 現状 | 24 Case のうち励起 Primitive を検証しているのは B10 の1件のみ。7 Case は2値の期待集合であり実質"ALLOWでない"しか主張していない |
| 実例 | E05 は `EXPIRED` を意図しているが、fixture の `issued_at` (11:30) が `expires_at` (11:00) より後のため `EXPIRED, TIMESTAMP_MISMATCH` の2件が立つ。どのテストもこれを検出しない |
| 提案 | `suites.Case` に `expected_primitives` を追加し、`run_trial` と pytest の双方で照合する |
| 注意 | 不変条件試験層 (117試験) は真の性質を検証している。本項目は Case 層 (24件) にのみ当たる |

### M-6. F-01 / F-03 の記述訂正

| 項目 | 内容 |
| ---- | ---- |
| Finding | F-01 / F-03 |
| 対象 | `..._TRIAL_RESULTS.md` 3.2節 / 3.4節、`..._DESIGN_EVIDENCE_BOUNDARY.md` 変換点表 第4行、Extended設計 第4節 |
| 現状 | 既存文書は No Change Rule により未修正。`..._EVIDENCE_BOUND_CONSOLIDATION_v0.1.md` G-2 / G-3 節が正誤表として機能している |
| 提案 | 承認が得られた時点で既存文書側にも反映する。反映内容は Consolidation 文書 G-2 / G-3 節に確定済みのものをそのまま用いる |
| 優先度の理由 | 記述の誤りであってコードの欠陥ではないため MEDIUM。ただし正誤表が既に存在するため、実務上の危険は低い |

---

## 3. Priority LOW / INVESTIGATE

### L-1. coverage expansion

現在の全数探索は Basic 30,000通り / Extended 10,000通りであり、
いずれも"単一Contractの単一評価"に限定されている。
複数Contractの系列、policy の組合せ、時刻の系列については未探索である。
拡張の是非を含めて調査対象とする。

### L-2. adversarial Contract mutation

妥当な Contract を起点に1フィールドずつ変異させ、
決定が単調に劣化する (ALLOW から離れる方向にのみ動く) ことを性質として検証する案。
現在の全数グリッドは組合せ網羅であり、変異の単調性は検証していない。

### L-3. replay / context-boundary tests

`REQUEST_REPLAY` / `CONTEXT_MISMATCH` / `NON_MONOTONIC_TIME` の3語彙は
状態を跨ぐ試験が必要であり、単発Caseでは表現しにくい。
系列を扱える試験形式の設計そのものを検討対象とする。
M-4 と重複するが、M-4 が"1語彙1Case"の最小対応であるのに対し、
本項目は試験形式の再設計である。

### L-4. Policy と Vocabulary の分離

Severity が語彙表に固定されているため、
運用者が"この環境では BINDING_UNMAPPED を BLOCKING 扱いにする"といった
policy 変更を行うには語彙表そのものを編集する必要がある。
現在は `witness_required` / `signature_required` / `nonce_required` のみが
policy フラグとして外出しされている混在状態である。
本番導入を検討する段階で扱う課題として記録する。

---

## 4. 実施しないと決めた事項 (No-Change 維持)

以下は監査で指摘として記録されたが、**変更を推奨しない**。

| # | 事項 | 理由 |
| - | ---- | ---- |
| 1 | B09 の Primitive が0件であること | 仕様どおり。正当な否認と異常検出の区別を記録上維持できている |
| 2 | E05 が2 Primitive を返すこと | 実装は正しく動作している。Extended の全件収集の性質が現れただけ。ただし fixture の時刻不整合は M-5 実施時に併せて判断する |
| 3 | Basic の語彙畳み込み | 意図的な単純化として文書化済み |
| 4 | Basic の短絡評価 | 監査記録の単純さという目的に合致 |
| 5 | 統制Case (B01 / E00) が EXECUTE に到達すること | 必要。これが無ければ"常に止まるだけの装置"と区別できない |
| 6 | E2E-BOUNDARY-01 が UNKNOWN でなく BLOCK になること | 期待集合内。複数の独立した遮断が成立している事実の方が価値が高い |
| 7 | `apply_bound_verdict(ALLOW, None) -> ALLOW` | 現行の呼出側で不変条件は保たれている (F-13 は記録のみ) |

---

## 5. 実施順序の推奨

```text
Step 1  H-2 (型検証)          -> 例外の発生源そのものを減らす
Step 2  H-3 (例外境界)        -> 残る例外を Fail-Closed へ
Step 3  H-1 (witness whitelist)
Step 4  M-2 (state contamination)  -> 方針確定を先に行うこと
Step 5  M-4 (未励起語彙の試験)     -> ここまでの変更の回帰確認を兼ねる
Step 6  M-5 (expected_primitives)  -> Case が理由を検証するようになる
Step 7  H-4 / M-3 / M-6            -> 構造と記述の整合
```

各Stepの後に以下を実行し、回帰が無いことを確認すること。

```bash
python -m experiments.constitutional_runtime_trial.run_trial --markdown
python -m pytest experiments/constitutional_runtime_trial/tests/ -q
```

---

## 6. 本文書が主張しないこと

- 本改善案が Original CR の改善であるとは述べない。対象は MoCKA Trial のみである
- 本改善案の必要性が Original CR に同種の欠陥があったことを示すとは述べない
- 改善を実施すれば Binding Gap の全クラスを防止できるとは述べない。
  試験できるのは定義済み境界のみである

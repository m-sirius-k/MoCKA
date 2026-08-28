# MoCKA Constitutional Runtime v1.0-stubs Trial - Design Audit v0.1

Status: AUDIT RECORD / NON-CANONICAL / NO-CHANGE AUDIT
Date: 2026-08-28
実施: くろこ (Claude Code)
指示: きむら博士 - KUROKO 第2指示書 (Basic / Extended Design Audit)
監査対象: `experiments/constitutional_runtime_trial/` および前回作成の文書A-F
Branch: claude/constitutional-runtime-investigation-jgqkv1

---

## 1. Scope

### 1.1 監査の問い (指示書 第3節)

> Is the current MoCKA Constitutional Runtime Trial a valid evidence-bound
> experimental implementation, rather than an inferred reconstruction of the
> unavailable original CR?

### 1.2 No Change Rule の遵守

本監査で **リポジトリ内のファイルは1つも変更していない**。
コード修正なし、テスト追加なし、Primitive追加なし、Architecture拡張なし。

検証は scratchpad 上の読み取り専用プローブ (14本) で行った。
プローブは対象パッケージを import して評価するだけであり、対象を書き換えない。
プローブ自体はリポジトリ外 (scratchpad) にあり、コミット対象ではない。

### 1.3 実施したプローブ一覧

| # | 目的 | 対応Axis |
| - | ---- | -------- |
| P1 | Gateway型厳格性 13入力 | C, L |
| P2 | apply_bound_verdict 25組合せ | C, D |
| P3 | Basic 全数グリッド 30,000通り | E, L |
| P4b | Extended グリッド 10,000通り (署名再計算後) | E, L |
| P5 | trial-added Primitive の反実仮想除去 | H |
| P6 | 未検証フィールド型 / 状態汚染 | C, G, L |
| P7 | JSON往復とas_dict境界 | M |
| P8 | 語彙31件のコード上の到達可能性 (静的) | G, J |
| P9 | テスト実行中に実際に励起されたPrimitive (動的計測) | J |
| P10 | Basic有効経路でのverdict依存性 | D |
| P11 | 緩和policy下でのE2E/T50 | N |
| P12/13 | Basicの決定生成箇所とSeverityリテラル数 | G, I |
| P14 | witness検査の強度 Basic vs Extended | E, N |

### 1.4 監査の限界

- 本監査は同一セッションの自己監査である。独立した第三者監査ではない
- 対象の外 (既存CR、旧50試験) については何も検証していない。検証材料が無い
- プローブ自体の正しさは、実行結果の内的整合でしか担保していない。
  実際、初回のP4は署名再計算漏れというプローブ側の欠陥を含んでおり、
  Extended全数でALLOW 0件という誤った結果を出した。修正版がP4bである。
  この訂正の経緯自体を監査記録として残す

---

## 2. Evidence Boundary (Axis A)

### 2.1 重点7語彙の分類確認

| Primitive | 実装上のorigin | 文書上の分類 | 判定 |
| --------- | -------------- | ------------ | ---- |
| AUTHORITY_LOST | instruction-listed | Observed / normalized label として参照、Primitive自体はDESIGNED | 適正 |
| INADMISSIBLE | instruction-listed | 同上 | 適正 |
| EXPIRED | instruction-listed | DESIGNED | 適正 |
| INTEGRITY_FAILURE | instruction-listed | DESIGNED | 適正 (ただしF-06参照) |
| CONTRACT_INVALID | instruction-listed | DESIGNED | 適正 |
| UNKNOWN | instruction-listed | DESIGNED | 適正 |
| CONTRACT_SEMANTICALLY_INCOMPLETE | trial-added | DESIGNED / trial-added と明示 | 適正 (ただしF-03参照) |

`origin` フィールドが実装内に保持されており、機械照合可能である (P8)。
`instruction-listed` が"指示書に列挙されていた"のみを意味し
"既存CRの内部Primitive名だった"を意味しないことは、
Evidence Boundary文書 第4節に明記されている。混同は認められない。

### 2.2 分類の網羅性

Evidence Boundary文書 第3節の変換点表13行のうち、
第9行から第13行が `(観測なし)` として Observed 列が空である。
これは正しい。3値Decision、下限演算、署名再計算、Replay検査、
trial-added語彙は、いずれも観測に由来しない。

### 2.3 Axis A 判定

**適正**。ただし1件の Derived セルに過剰推論がある (F-02)。

---

## 3. Findings

Severity は指示書 第19節に従う。

| ID | Severity | Axis | 要約 |
| -- | -------- | ---- | ---- |
| F-01 | MEDIUM | D | RESULTS 3.2 の"判定はverdictを読んでいない"が過剰一般化。実測で反証 |
| F-02 | MEDIUM | B, A | Evidence Boundary 変換点表 第4行の Derived セルが、表示ラベルから旧実装の挙動を推論している |
| F-03 | HIGH | H, J | trial-added Primitive が E09 の結果を単独で決定している。未開示 |
| F-04 | MEDIUM | E, N | Extended の witness 検査が blacklist 方式。Basic の whitelist より弱い |
| F-05 | MEDIUM | N, G | nonce 不在時に `NONCE_REUSED` を立てている。不在は再利用ではない |
| F-06 | MEDIUM | G | `integrity_status=FAILED` を `SIGNATURE_INVALID` に写像。`INTEGRITY_FAILURE` はExtendedで到達不能 |
| F-07 | MEDIUM | C, L | 未検証フィールド型が評価器内で TypeError を送出。例外分岐が存在しない |
| F-08 | MEDIUM | G | 検出が判定と独立に状態を変更する。却下されたContractがnonceとhigh-waterを汚染する |
| F-09 | MEDIUM | G, I | Basic は共有Policy層 `decide()` を使わず、検出箇所で決定を生成している |
| F-10 | MEDIUM | J | 24 Case中 Primitive を検証しているのは1件のみ。決定は見ているが理由を見ていない |
| F-11 | MEDIUM | J | 31語彙中10語彙がテスト実行中に一度も励起されない |
| F-12 | LOW | N | RESULTS 3.5 の"独立6経路"が既定policyに依存。緩和policyでは3経路 |
| F-13 | LOW | C | `apply_bound_verdict(ALLOW, None)` が ALLOW を返す。安全性は呼出側の不変条件に依存 |
| F-14 | LOW | M | 本Trialの typed とは"閉じた語彙で検証された文字列"であり、独立した型ではない |
| F-15 | INFO | I | Basic/Extended の評価方式差 (短絡 vs 全件収集) を検証するテストが存在しない |
| F-16 | INFO | J | テストは実装後に書かれたwhite-box試験であり、独立したoracleではない |
| F-17 | UNKNOWN | F | 旧試験で観測されたFail-Open様挙動の原因は確定不能 |

---

### F-01 (MEDIUM) Verdict independence の過剰一般化

**所在**: `docs/tests/..._TRIAL_RESULTS.md` 第98行
**現行記述**: `verdictを反転させても決定もPrimitiveも変化しない。すなわち判定はverdictを読んでいない。`

**反証 (P10)**: Contractが完全に妥当で `binding_status=BOUND` の場合、決定は re_verdict の関数である。

```text
re_verdict=ALLOW    -> decision=ALLOW    primitives=(なし)
re_verdict=BLOCK    -> decision=BLOCK    primitives=(なし)
re_verdict=UNKNOWN  -> decision=UNKNOWN  primitives=(なし)
```

これは設計どおりの挙動 (bound verdict の下限演算) であり、実装の欠陥ではない。
欠陥は **記述** にある。第2文が第1文の妥当な範囲を超えて一般化している。
Axis D が明示的に禁じた一般化に該当する。

**修正案 (未適用)**: 第2文を次に置換する。

```text
すなわち、この決定経路 (binding_status != BOUND) では、決定は re_verdict 値に依存しない。
なお binding_status = BOUND の経路では、決定は bound verdict に依存する (設計どおり)。
```

---

### F-02 (MEDIUM) Derived セルの過剰推論

**所在**: `docs/audits/..._DESIGN_EVIDENCE_BOUNDARY.md` 第68行 (変換点表 第4行)
**現行記述**: Observed=`PASS (Unmapped)` という表示が報告された /
Derived=`未マップ状態が通過側へ解決されうる形が存在した`

**問題**: 前段調査で、`PASS (Unmapped)` がハーネス側の表示ラベルなのかCR側の
Primitiveなのかは `UNKNOWN` と確定している。表示ラベルから
"未マップ状態が通過側へ解決される形が存在した"という **挙動** を導くことは、
Axis B が禁じる逆推論の弱い形である。

```text
Observed label "PASS (Unmapped)"
  -> (跳躍) 旧実装は unmapped を pass 側へ解決していたはずだ
  -> MoCKA はそれを UNKNOWN にする
```

**なお**: 設計判断 (Designed列) 自体は健全である。未マップをUNKNOWNへ解決する
という判断は、旧実装が何をしていたかに依存しない。修正が必要なのはDerived列のみ。

**修正案 (未適用)**: Derived列を次に置換する。

```text
報告された表示上、unmapped 状態が pass 側の語彙で表現されていた。
その語がハーネス表示かCR内部Primitiveかは UNKNOWN であり、
旧実装の解決挙動については何も導かない。
```

---

### F-03 (HIGH) trial-added Primitive が E09 の結果を単独で決定している

**所在**: 実装 `runtime_extended.py` / 文書 Extended設計 第4節、TEST_SPEC、RESULTS

**反実仮想 (P5)**: `CONTRACT_SEMANTICALLY_INCOMPLETE` を Finding 集合から除去して
各Caseの決定を再計算した結果。

```text
E03              actual=BLOCK    without_primitive=BLOCK    exec=STOP
E09              actual=UNKNOWN  without_primitive=ALLOW    exec=EXECUTE   <-- 反転
E2E-BOUNDARY-01  actual=BLOCK    without_primitive=BLOCK    exec=STOP
T50-EXTENDED     actual=BLOCK    without_primitive=BLOCK    exec=STOP
```

**解釈 (2点に分けること)**:

1. 指示書 第11節-5 の問い"Primitive追加によって結論を人工的に強化していないか"への回答は
   **強化していない**。中心試験 (E2E-BOUNDARY-01) と Test 50境界 (T50-EXTENDED) は、
   この語彙が無くても BLOCK で停止する。headline結論はこの追加に依存しない。
2. ただし **E09 は完全に依存している**。この語彙が無ければ E09 は ALLOW / EXECUTE となる。
   すなわち E09 は"設計一般の性質"ではなく"追加語彙の存在"を試験している。
   この事実はいずれの文書にも記載されていない。

Severity を HIGH としたのは、開示を唯一の目的とする文書群において、
唯一のtrial-added語彙の決定的な依存関係が未開示であるためである。

**修正案 (未適用)**: Extended設計 第4節と RESULTS 3.4 に反実仮想の結果を追記する。
語彙の削除や試験の変更は不要。

---

### F-04 (MEDIUM) Extended の witness 検査が Basic より弱い

**反証 (P14)**:

```text
Basic    witness_present=True, witness_status=ABSENT -> UNKNOWN ['UNKNOWN']
Extended witness_present=True, witness_status 不在   -> UNKNOWN ['CONTRACT_SEMANTICALLY_INCOMPLETE']
Extended の Evidence カテゴリ Finding: [] (0件)
```

Basic 規則7は `witness_present AND witness_status == "VALID"` を要求する (whitelist)。
Extended `_evidence_findings` は `INVALID / CONFLICT / ABSENT` を拒否する (blacklist)。

現行の語彙 (VALID/INVALID/ABSENT/CONFLICT) では、両者の差は
"status が不在の場合"にのみ現れ、その場合は F-03 の trial-added 語彙が捕捉する。
したがって **現時点で実行可能な穴は存在しない**。

問題は形式にある。Comparison Matrix は Witness 行を
`Basic: Basic / Extended: Full` と記載しているが、実際には
Extended の witness 規則は Basic より弱い形式で書かれており、
封じ込めは別カテゴリの語彙による偶然の副作用である。
将来 witness_status に語彙を1つ追加すれば、Extended はそれを黙って受理する。

**修正案 (未適用)**: `_evidence_findings` を whitelist 化する
(`status != "VALID"` を WITNESS_INVALID / WITNESS_MISSING へ写像)。
併せて Comparison Matrix の Witness 行の記述を見直す。

---

### F-05 (MEDIUM) nonce 不在に NONCE_REUSED を立てている

**所在**: `runtime_extended.py` `_replay_findings`

```python
if self.policy.nonce_required and nonce is None:
    out.append(_f("NONCE_REUSED", "nonce", "no nonce present; replay cannot be excluded"))
```

不在は再利用ではない。detail文字列は正確だが Primitive名が事実と異なる。
影響は監査記録の可読性に及ぶ。E2E-BOUNDARY-01 と T50-EXTENDED の監査行は
nonce を一切持たないContractに対して `NONCE_REUSED` を記録しており、
記録だけを読んだ第三者は再送攻撃を疑うことになる。

**修正案 (未適用)**: `NONCE_MISSING` (BLOCKING, Replay) を新設して写像する。
ただし語彙追加は No Change Rule と Axis H の趣旨に触れるため、
博士の承認を前提とする。

---

### F-06 (MEDIUM) INTEGRITY_FAILURE が Extended で到達不能

**静的解析 (P8)**: 語彙31件はすべてコード上で到達可能だが、
`CONTRACT_INVALID` と `INTEGRITY_FAILURE` の2件は **Basic からのみ** 到達可能。

Extended は `integrity_status == "FAILED"` を `SIGNATURE_INVALID` へ写像している。
FAILED は一般的な完全性失敗であり、署名固有の失敗ではない。
Extended設計文書 第4節の表は `INTEGRITY_FAILURE` を
`instruction-listed (Basic継承)` として掲載しているが、実際には継承されていない。

**修正案 (未適用)**: `FAILED -> INTEGRITY_FAILURE` へ写像を変更する。
または表に"Extendedでは未使用"と明記する。

---

### F-07 (MEDIUM) 例外分岐が存在しない

**反証 (P6)**:

```text
nonce      = ['a']      -> RAISED TypeError: unhashable type: 'list'
request_id = ['r']      -> RAISED TypeError: unhashable type: 'list'
subject    = {'s': 1}   -> RAISED TypeError: unhashable type: 'dict'
```

`nonce` / `subject` は intake で型検証されず、`request_id` は None 検査のみである。
これらが hashable でない場合、`self._nonces.add()` / `self._requests.add()` /
`self._high_water.get()` が TypeError を送出し、`evaluate()` から脱出する。

**重要な区別**: これは Fail-Open ではない。Decisionが返らないので
ALLOW にもならない。Stop Condition 1 / 2 には該当しない。
しかし Runtime は例外時の実行可否について何も述べておらず、
その判断は仕様化されていない呼出側に委ねられている。
Axis L の `exception branch` は **不在** である。

**修正案 (未適用)**: intake で `nonce` / `request_id` / `subject` の型を検証して
CONTRACT_SCHEMA_MISMATCH へ落とす。加えて `evaluate()` に
fail-closed な例外境界 (例外は BLOCK として記録) を設ける。

---

### F-08 (MEDIUM) 検出が判定と独立に状態を汚染する

**反証 (P6)**:

```text
却下されたContract (AUTHORITY_LOST) が nonce N-SHARED を消費
  -> 後続の完全に妥当なContract (同一nonce) が NONCE_REUSED で BLOCK

却下された未来日時Contract が subject の high-water mark を更新
  -> 後続の完全に妥当なContract が NON_MONOTONIC_TIME で BLOCK
```

検出フェーズの副作用が、却下された決定より長く生存している。
攻撃者が拒否されると分かっているContractを投げるだけで、
正当なnonce空間と時刻空間を汚染できる (可用性側の危険)。

同時にこれは Axis G の構造的問題でもある。
`Detection -> Policy -> Decision` を掲げながら、Detection が
Decision の結果と無関係に永続状態を書き換えている。

**修正案 (未適用)**: 台帳への登録を、決定が ALLOW になった場合のみ、
または決定確定後のコミット段階に移す。

---

### F-09 (MEDIUM) Basic は共有Policy層を使っていない

**反証 (P12/P13)**:

```text
runtime_basic.py  : decide() への参照 0件、Severity リテラル 10箇所
runtime_extended.py: Severity リテラル 0件 (すべて語彙表から導出)、decide() 使用
```

Basic は `_stop()` の内部で `finding.severity` から直接 Decision を作る。
すなわち Basic には Policy 層が存在せず、検出箇所が決定箇所を兼ねている。

Axis G が要求する `Primitive Detection -> Policy Evaluation -> Decision` は
**Extended でのみ成立** し、Basic では2段構造である。
文書は両者を同一アーキテクチャとして提示しており、この差は記載されていない。

**修正案 (未適用)**: Basic も `decide()` を経由させるか、
設計文書に"Basicは短絡評価のためPolicy層を持たない"と明記する。

---

### F-10 (MEDIUM) テストは決定を見ているが理由を見ていない

24 Case のうち、励起された Primitive を検証しているのは **B10 の1件のみ**。
7 Case (B08 / E03 / E09 / E10 / E2E-BOUNDARY-01 / T50-BASIC / T50-EXTENDED) は
期待値が2値集合であり、実質的に"ALLOWでないこと"しか主張していない。

"ALLOWでないこと"は本Trialの中心的性質なので、この主張自体は正しい。
問題は、Caseが **誤った理由で** PASS しうることである。

実例が既に1件ある。E05 は `EXPIRED` を試験する意図だが、
fixture の `issued_at` (11:30) が期限切れ用 `expires_at` (11:00) より後になっており、
実際には `EXPIRED, TIMESTAMP_MISMATCH` の2件が立っている。
どのテストもこれを検出しない。RESULTS 3.3 が事後に気付いて記載しているだけである。

**修正案 (未適用)**: Case定義に `expected_primitives` を追加し、
`run_trial` とテストの両方で照合する。

---

### F-11 (MEDIUM) 31語彙中10語彙が試験中に一度も励起されない

**動的計測 (P9)**: `Finding.__init__` を計測用に差し替えて全117試験を実行し、
実際に構築された Primitive を収集した (計測はプローブ内のみ、対象は無変更)。

```text
primitives raised in tests : 21 / 31
never raised during tests  : 10

  AUTHORITY_MISMATCH
  CONTRACT_SCHEMA_MISMATCH
  CONTRACT_VERSION_DRIFT
  DIGEST_MISMATCH
  NON_MONOTONIC_TIME
  NOT_YET_VALID
  REQUEST_REPLAY
  VERDICT_MUTATED
  WITNESS_CONFLICT
  WITNESS_INVALID
```

10件はいずれもコード上は到達可能である (P8)。すなわち
"実装したが検証していない"状態である。

これは Comparison Matrix の記述に直接影響する。
`Time: Full` / `Integrity: Full` / `Replay: Yes` / `Witness: Full` の各行は、
**実装済みではあるが試験で裏付けられていない部分を含む**。

**修正案 (未適用)**: 10語彙に対する最小Caseを追加する。または
Comparison Matrix に"実装済み / 未試験"の区別を導入する。

---

### F-12 (LOW) 独立6経路の主張が既定policyに依存している

**反証 (P11)**:

```text
E2E-BOUNDARY-01  strict policy -> BLOCK, 6 findings
                 lax policy    -> BLOCK, 3 findings
                   (CONTRACT_SEMANTICALLY_INCOMPLETE, BINDING_MISSING, VERDICT_MISSING)
T50 input        strict policy -> BLOCK, 6 findings
                 lax policy    -> BLOCK, 3 findings (同じ3件)
```

RESULTS 3.5 の `Fail-Closedが単一点に依存していない` という主張は維持される
(緩和policyでも BLOCKING が2件残る)。
ただし6件のうち3件 (SIGNATURE_MISSING / NONCE_REUSED / WITNESS_MISSING) は
policy フラグが既定で required であることに由来し、
binding gap そのものに由来するわけではない。

**修正案 (未適用)**: RESULTS 3.5 に緩和policy下の結果を併記する。

---

### F-13 (LOW) apply_bound_verdict の不変条件が関数外にある

**反証 (P2)**: `apply_bound_verdict(Decision.ALLOW, None) -> Decision.ALLOW`

`bound_verdict=None` は"binding されていない"を意味する。
この組合せが ALLOW を返しても安全なのは、
"binding が成立していなければ必ず BLOCKING Finding が立つ"という不変条件を
呼出側 (Basic 規則6 / Extended `_binding_findings`) が保証しているからである。

`A verdict is not an execution authority.` を体現する関数自身が
その不変条件を強制していない。呼出側の変更で静かに破れうる。

なお同プローブで、型でない decision (`"ALLOW"`) を渡した場合は
UNKNOWN へ落ちることを確認済みであり、こちらは適正である。

---

### F-14 (LOW) typed の意味を明示すべき

**確認 (P7)**: JSON往復で決定は不変 (ALLOW -> ALLOW、同一オブジェクト)。
`Evaluation.as_dict()` は decision を素の `str` として出力し、
それを `gate()` へ戻すと `STOP` になる (適正)。
パッケージにデシリアライザは存在しない。

本Trialで実際に独立した型を持つのは `Decision` と `Execution` の2つだけである。
Contract の状態 (`authority_state` 等) はすべて素の `str` であり、
閉じた語彙による検証を受けているにすぎない。

したがって Axis M の懸念 (typed state が plain string へ劣化する) は
**構造上発生しない**。劣化する型が最初から存在しないためである。
これは欠陥ではないが、`Typed Verification Contract` という名称が
Python の型システム上の保証を含意しないことは明記すべきである。

---

### F-15 (INFO) Basic/Extended の評価方式差が試験されていない

短絡評価 (Basic) と全件収集 (Extended) の差を検証するテストは存在しない
(`len(...findings)` を検査するテスト 0件)。
差は実装上実在し、結果表からも観察できるが、
Basic を全件収集に書き換えても、どのテストも失敗しない。

---

### F-16 (INFO) 試験は white-box であり独立oracleではない

期待値は指示書 第10節 / 第14節に由来し、実行結果を見てから
期待値を変更した事実は無い (Stop Condition 6 参照)。
ただし fixture は実装を書いた後に実装知識をもって構成されている。
独立に導出された参照実装との突き合わせは行っていない。

---

### F-17 (UNKNOWN) 旧Fail-Open様挙動の原因

確定不能。材料が存在しない。詳細は 第6節。

---

## 4. Type Safety (Axis C, Axis L)

### 4.1 指示書 第6節の7項目

| # | 確認項目 | 結果 | 証拠 |
| - | -------- | ---- | ---- |
| 1 | plain `"ALLOW"` がGatewayを通過しない | 通過しない (STOP) | P1 |
| 2 | plain `"BLOCK"` がGatewayを通過しない | 通過しない (STOP) | P1 |
| 3 | plain `"UNKNOWN"` がGatewayを通過しない | 通過しない (STOP) | P1 |
| 4 | `Decision.ALLOW` のみがALLOW経路へ到達 | 成立。13入力中EXECUTEは1件のみ | P1 |
| 5 | `Decision.BLOCK` のみがBLOCK経路へ到達 | 成立 | P1 |
| 6 | `Decision.UNKNOWN` がALLOW経路へ到達しない | 到達しない。40,000件の評価でUNKNOWN->EXECUTE 0件 | P1, P3, P4b |
| 7 | subclass / coercion / serialization で迂回できない | 迂回不可 | P1, P7 |

### 4.2 項目7の内訳

```text
Decision の subclass 化        -> TypeError: <enum 'Sneaky'> cannot extend <enum 'Decision'>
                                  (Enumはメンバを持つと継承不可。言語仕様が保証)
別の str Enum (同値 "ALLOW")   -> gate() -> STOP  (isinstance で除外)
str のサブクラス ("ALLOW")     -> gate() -> STOP  (isinstance で除外)
JSON往復後の素の str           -> gate() -> STOP
None / "" / 1 / True / dict    -> すべて STOP
```

`"ALLOW" == Decision.ALLOW` は True、`hash` も一致する。
すなわち等価性とハッシュでは区別できず、`isinstance` 検査だけが境界を守っている。
この一点への依存は、Gateway の2関数に集中しており、監査可能である。

### 4.3 Axis L の残り項目

| 項目 | 結果 |
| ---- | ---- |
| default branch | `_GATE.get(decision, Execution.STOP)` により、未知メンバは STOP |
| exception branch | **不在** (F-07)。例外は呼出側へ素通しされる |
| malformed input | STOP (P1) |
| null | STOP (P1) |
| empty string | STOP (P1) |
| unexpected enum | STOP (P1) |
| serialization boundary | 決定不変、逆変換器なし、素のstrはSTOP (P7、F-14) |

**想定外入力がALLOWになる経路は発見されなかった。**
唯一の未仕様領域は例外経路である (F-07)。

---

## 5. Unknown Handling (Axis E)

### 5.1 UNKNOWN -> ALLOW の暗黙変換

**全数探索の結果、存在しない。**

```text
Basic    30,000通り (authority x admissibility x witness_present x witness_status
                     x integrity x binding x re_verdict の全組合せ)
  ALLOW到達      : 1件のみ
                   auth=VALID adm=ADMISSIBLE wp=True ws=VALID
                   int=VERIFIED bind=BOUND verdict=ALLOW
  UNKNOWN->EXECUTE: 0件
  例外           : 0件

Extended 10,000通り (署名は全上書き後に再計算、nonce/request_idは毎回新規)
  ALLOW到達      : 1件のみ (同一の全良組合せ)
  UNKNOWN->EXECUTE: 0件
  例外           : 0件
```

40,000件の評価で、ALLOW に到達したのは各Runtimeにつき
"全フィールドが良好な唯一の組合せ"だけであった。
指示書 第8節が列挙した8経路 (Missing Contract / Malformed Contract /
Missing Primitive / Unknown Primitive / Incomplete Contract / Unknown State /
Binding Missing / Witness Missing) は、このグリッドと
既存の不変条件試験の双方に含まれており、いずれも ALLOW へ到達しない。

### 5.2 UNKNOWN -> BLOCK を採用した箇所の性質

指示書が求める区別 (安全側に倒した設計判断か、UNKNOWNをBLOCKと定義してしまっているか)。

| 箇所 | 分類 | 根拠 |
| ---- | ---- | ---- |
| Extended `decide()` の還元順序 | 安全側の設計判断 | UNKNOWNはUNKNOWNのまま保持され、BLOCKINGが同時にある場合のみBLOCKになる。E09/E10はUNKNOWNのまま出力される |
| Gateway `UNKNOWN -> STOP` | 安全側の設計判断 | 実行の停止であり、決定の書き換えではない。Decisionは3値のまま |
| Basic 規則7 `witness_absent_policy=BLOCK` | **定義の混同に近い** | UNKNOWN相当の状況を `CONTRACT_INVALID` (BLOCKING) として記録する。既定は UNKNOWN policy なので通常経路では発生しないが、BLOCK policy を選ぶと証拠不足がContract不正として記録される |
| Extended `CONTRACT_SEMANTICALLY_INCOMPLETE` | 安全側の設計判断 | INDETERMINATE として定義されており、UNKNOWNを保持する |

Basic 規則7 の BLOCK policy 経路のみ、記録上の意味が歪む。
既定値では発生しないため Severity は F-04 に含めず、ここに記録する。

---

## 6. Fail-Closed Scope (Axis F)

指示書が要求する3者の区別。

| 区分 | 内容 | 本Trialでの状態 |
| ---- | ---- | --------------- |
| A | MoCKA Trial における Fail-Closed 設計 | **実装済み・検証済み**。40,000件の全数探索で ALLOW は全良組合せのみ (第5節) |
| B | 旧50試験で観測された Fail-Open 様挙動 | **提供された観測**。一次資料は未到達。本監査では検証していない |
| C | 旧CR全体に Fail-Closed 機構が存在しないという主張 | **どの文書にも存在しない**。文面走査で確認済み |

A を実装したことは B の原因を説明しない。
本Trialの文書群でこの混同は発見されなかった。
RESULTS 5.3 は"本Trialが旧CRより優れていることを示すものではない。
比較対象の内部実装は NOT OBSERVED であり、優劣を判定する材料がない"と明記している。

**Axis F 判定: 適正。**

---

## 7. Primitive Semantics (Axis G)

### 7.1 Detection と Decision の分離

| Runtime | 構造 | 判定 |
| ------- | ---- | ---- |
| Extended | Finding生成 (Severityは語彙表から導出) -> `decide()` -> `apply_bound_verdict()` -> `gate()` | 3段分離が成立 |
| Basic | Finding生成 (Severityを検出箇所にリテラル記述) -> `_stop()` が直接Decisionを生成 -> `gate()` | **Policy層が不在** (F-09) |

Extended では、ある Primitive が検出されたことと BLOCK することは別概念として
実装されている。`CONTRACT_INVALID` の検出は Finding であり、
BLOCK は `decide()` が Severity 集合から導く別の段階である。

Basic ではこの分離が無い。`_stop()` が `finding.severity is Severity.BLOCKING` を
その場で Decision へ変換する。

### 7.2 Policy が語彙に埋め込まれている

Extended においても、Severity は Primitive の属性として語彙表に固定されている。
運用者が"この環境では BINDING_UNMAPPED を BLOCKING 扱いにする"といった
policy変更を行うには、語彙表そのものを編集する必要がある。

Detection と Decision は分離されているが、
**Policy と Vocabulary は分離されていない**。
本Trialの規模では妥当な単純化だが、設計文書には記載がない。

### 7.3 命名と意味の不一致

- `NONCE_REUSED` が不在に対して立つ (F-05)
- `integrity_status=FAILED` が `SIGNATURE_INVALID` に写像される (F-06)

いずれも Detection の記録内容が事実と異なる例である。
Decision は正しい (どちらも BLOCK) が、監査記録としては誤りである。

---

## 8. Basic/Extended Separation (Axis I)

### 8.1 "Primitive数を増やしただけ"か

**そうではない。** 実装上の差は4種類ある。

| 差分 | 実装での確認 |
| ---- | ------------ |
| 評価方式 | Basic は短絡 (最初のFindingで return)、Extended は全件収集 |
| 状態 | Basic はステートレス、Extended は nonce/request/high-water の3台帳を保持 |
| Severity の由来 | Basic は検出箇所のリテラル10箇所、Extended は語彙表から導出 (リテラル0箇所) |
| Contract失敗の粒度 | Basic は全defectを CONTRACT_INVALID に畳み込み、Extended は5種へ分割 + 二段階化 |

### 8.2 三者 (実装・テスト・文書) の一致

| 項目 | 実装 | 文書 | テスト |
| ---- | ---- | ---- | ------ |
| 評価方式の差 | あり | 記載あり | **検証なし** (F-15) |
| 状態保持の差 | あり | 記載あり | E06で間接的に検証 |
| 語彙の分割 | あり | 記載あり | 部分的 (F-11: 10語彙未励起) |
| Policy層の有無 | 差がある | **記載なし** (F-09) | 検証なし |

実装と文書はおおむね一致するが、テストが差分を固定していない。
文書が触れていない差 (Policy層の有無) が1件ある。

---

## 9. Test Adequacy (Axis J)

### 9.1 一対一対応の確認

`Test objective / Input / Expected / Actual / Decision / Evidence Status` は
`suites.py` の Case 定義と `audit.py` の AuditRecord に一対一で保持され、
`trial_results.json` に出力されている。対応関係は成立している。

Evidence Status の分布: DESIGNED 14件 / DERIVED 10件 / OBSERVED 0件。
OBSERVED が0件であることは正しい (第2節)。

### 9.2 "Expected=BLOCK だから Actual=BLOCK で PASS"になっていないか

**部分的にその批判が当たる。**

- 24 Case中、励起Primitiveを検証しているのは B10 の1件のみ (F-10)
- 7 Case は2値の期待集合であり、実質"ALLOWでない"しか主張しない
- E05 は意図しない第2 Primitive を伴って PASS している (F-10 の実例)

### 9.3 不変条件を本当に検証しているテスト

一方で、決定値の一致以上の性質を検証しているテストは実在する。

| テスト | 検証している性質 |
| ------ | ---------------- |
| `test_b10_blocks_on_binding_not_on_verdict` | verdict反転に対する決定とPrimitiveの不変性 |
| `test_*_decision_is_invariant_under_prose` (10パターン) | Prose有無に対する不変性 |
| `test_no_primitive_name_appears_in_prose_derived_findings` | Prose走査の不在 (走査があれば必ず落ちる) |
| `test_every_single_field_omission_fails_closed` (12通り) | フィールド欠落の網羅 |
| `test_bound_verdict_can_only_lower_a_decision` (9組) | 束の単調性 |
| `test_*_never_allows_without_a_binding` (8通り) | binding不成立時のALLOW不到達 |

これらは真の不変条件試験である。
すなわち Axis J の批判は Case層 (24件) に当たり、不変条件層 (117試験) には当たらない。

### 9.4 語彙カバレッジ

31語彙中21語彙のみが試験中に励起される (F-11)。

---

## 10. Test 50 Comparison (Axis K)

### 10.1 Observed と Trial Result の混同

**混同は発見されなかった。**

`trial_results.json` に旧観測は一切含まれていない。
T50-BASIC / T50-EXTENDED の行は本Trialの実測値のみである。

RESULTS 5.3 の比較表は、列見出しが
`報告された旧観測 | T50-BASIC | T50-EXTENDED` となっており、出所が分離されている。
同 5.1 に"一次資料未到達""分類は OBSERVED (provided, not independently verified)"
"本Trialの結果はこの数値の真偽に依存しない"が明記されている。

### 10.2 禁止表現の有無

`旧CRを修正した結果` に相当する表現は存在しない (文面走査で確認)。
`復元` `再現` の語が出現する6箇所はすべて **禁止表現の列挙 (否定文脈)** であり、
主張ではない。

RESULTS 5.3 は明示的に
"この表は本Trialが旧CRより優れていることを示すものではない"
と述べている。

### 10.3 推奨される表現との一致

指示書が指定した表現
"MoCKA Trialによる独立設計では同一クラスの境界条件に対して異なる結果となった"
は、現行文書の記述と意味的に一致する。

**Axis K 判定: 適正。**

---

## 11. Execution Gateway (Axis L)

第4節に統合済み。要点のみ再掲する。

- 想定外入力が ALLOW になる経路は発見されなかった (13入力 + 40,000評価)
- 型境界は `isinstance(decision, Decision)` の1点に集約されており、監査可能
- `Decision` は Enum のため subclass 不能。言語仕様が境界を補強している
- **例外分岐のみ不在** (F-07)。TypeError は評価器から素通しされ、
  実行可否は仕様化されていない呼出側に委ねられる

---

## 12. Serialization Boundary (Axis M)

`Finding: serialization type boundary` として記録する。

| 観測 | 結果 |
| ---- | ---- |
| Contract の JSON 往復 | 決定不変 (ALLOW -> ALLOW)。署名も一致 |
| `Evaluation.as_dict()` の decision | 素の `str` へ劣化する |
| 劣化した値を `gate()` へ戻した場合 | `STOP` (適正) |
| パッケージ内のデシリアライザ | 存在しない |

**構造的な結論**: 本Trialで独立した型を持つのは `Decision` と `Execution` のみである。
Contract の状態値はすべて素の `str` であり、
`typed` とは"閉じた語彙で検証済み"を意味する。
したがって Contract 層では劣化しうる型が存在せず、Axis M の懸念は発生しない。

これは欠陥ではないが、`Typed Verification Contract` という名称が
Python の型システム上の保証を含意しないことは文書に明記すべきである (F-14)。

補足: `canonical_payload` は `json.dumps(..., default=str)` を用いる。
署名生成側と検証側が同一関数を使うため不整合は生じないが、
`str()` が同一になる異なるオブジェクトは同一署名を持つ。
現行の語彙は文字列のみなので実害はない。

---

## 13. Security Overreach (Axis N)

### 13.1 過剰BLOCKの検査

| 状態 | 現在の帰結 | 過剰か |
| ---- | ---------- | ------ |
| UNKNOWN (admissibility) | UNKNOWN -> STOP | 過剰ではない。Decisionは3値のまま保持され、BLOCKへ変換されていない |
| MISSING (binding/witness/signature) | BLOCK -> STOP | 過剰ではない。ただし witness/signature/nonce の必須性は policy フラグであり、緩和可能な設計になっている (F-12) |
| UNMAPPED (binding) | UNKNOWN -> STOP | 過剰ではない。BLOCKに丸めていない点が適切 |
| SEMANTICALLY_INCOMPLETE | UNKNOWN -> STOP | 過剰ではない。ただしE09では単独で結果を決めている (F-03) |

`UNKNOWN` と `UNMAPPED` と `SEMANTICALLY_INCOMPLETE` は
いずれも INDETERMINATE として保持され、BLOCK へ丸められていない。
Axis N が懸念する"安全性を理由にUNKNOWNを潰す"設計にはなっていない。

### 13.2 検出と実行判断の分離の余地

停止の必要性そのものは、実行ゲートの位置づけ (ALLOW以外は実行しない) から従う。
ただし、以下は検出と実行判断を分離する余地がある。

- `signature_required` / `nonce_required` / `witness_required` は既に policy フラグ
- 一方 Severity は語彙表に固定されており、運用者が調整できない (第7.2節)

現状は"policy の一部は外出しされ、一部は語彙に固定されている"混在状態である。
本Trialの規模では妥当だが、文書化されていない。

### 13.3 過剰の実例は1件

F-12 のとおり、中心試験の Finding 6件のうち3件は既定 policy に由来する。
BLOCK 判定自体は binding gap 由来の2件 (BINDING_MISSING / VERDICT_MISSING) で成立するため、
結論は変わらない。ただし記述は policy 依存部分を分離すべきである。

---

## 14. Required Changes

修正は実施していない。優先度順に提示する。
いずれも実施前に博士の承認を得ること。

### 14.1 文書のみで完結する修正 (コード変更不要)

| # | 対象 | 内容 | Finding |
| - | ---- | ---- | ------- |
| 1 | RESULTS 3.2 | "判定はverdictを読んでいない"を経路限定の表現へ置換 | F-01 |
| 2 | Evidence Boundary 変換点表 第4行 | Derived セルを表示ラベルの記述に限定 | F-02 |
| 3 | Extended設計 第4節 / RESULTS 3.4 | trial-added Primitive の反実仮想結果 (E09がALLOWになる) を追記 | F-03 |
| 4 | Extended設計 第4節の表 | `INTEGRITY_FAILURE` に"Extendedでは未使用"と注記 | F-06 |
| 5 | Comparison Matrix | "実装済み / 未試験"の区別を導入 | F-11 |
| 6 | RESULTS 3.5 | 緩和policy下の結果 (3 findings) を併記 | F-12 |
| 7 | Basic/Extended設計 | `typed` の意味 (語彙検証済み文字列) を明記 | F-14 |
| 8 | Extended設計 | Basic に Policy 層が無いことを明記 | F-09 |

### 14.2 コード変更を伴う修正

| # | 対象 | 内容 | Finding | 優先度 |
| - | ---- | ---- | ------- | ------ |
| 9 | `runtime_extended._evidence_findings` | witness検査を whitelist 化 | F-04 | 高 |
| 10 | `contract.intake` | `nonce` / `request_id` / `subject` の型検証を追加 | F-07 | 高 |
| 11 | `runtime_extended.evaluate` | fail-closed な例外境界を追加 | F-07 | 高 |
| 12 | `runtime_extended._replay_findings` | 台帳登録を決定確定後へ移動 | F-08 | 中 |
| 13 | `runtime_extended._integrity_findings` | `FAILED -> INTEGRITY_FAILURE` へ写像変更 | F-06 | 中 |
| 14 | `suites.Case` | `expected_primitives` を追加し照合 | F-10 | 中 |
| 15 | テスト | 未励起10語彙の最小Case追加 | F-11 | 中 |
| 16 | `runtime_basic` | `decide()` 経由に統一する (または文書化で対応) | F-09 | 低 |
| 17 | 語彙 | `NONCE_MISSING` の新設 | F-05 | 低 (語彙追加のため要承認) |

### 14.3 E05 fixture について

`issued_at` (11:30) > `expires_at` (11:00) は fixture 上の不整合である。
ただし現在の結果は正しく、意図した `EXPIRED` も検出されている。
修正すると RESULTS 3.3 の記述と乖離するため、
修正するなら文書も同時に更新すること。

---

## 15. No-Change Findings

以下は指摘として記録するが、**変更を推奨しない**。

| # | 事項 | 変更を推奨しない理由 |
| - | ---- | -------------------- |
| 1 | B09 の Primitive が0件 | 仕様どおり。正当な否認と異常検出の区別を記録上維持できている |
| 2 | E05 が2 Primitive を返す | 実装は正しく動作している。Extendedの全件収集の性質が現れただけ |
| 3 | Basic の語彙畳み込み (binding -> CONTRACT_INVALID) | 意図的な単純化として文書化済み。Basicの役割に照らして妥当 |
| 4 | Basic の短絡評価 | 監査記録の単純さという目的に合致 |
| 5 | 統制Case (B01/E00) がEXECUTEに到達すること | 必要。これが無ければ"常に止まるだけの装置"と区別できない |
| 6 | E2E-BOUNDARY-01 が UNKNOWN でなく BLOCK になること | 期待集合内。複数の独立した遮断が成立している事実の方が価値が高い |
| 7 | `apply_bound_verdict(ALLOW, None) -> ALLOW` | 現行の呼出側で不変条件は保たれている。関数単独の強化は過剰 (F-13は記録のみ) |
| 8 | Severity が語彙表に固定されていること | 本Trialの規模では妥当。policy外出しは本番導入時の課題 |

---

## 16. Final Assessment

### 16.1 Stop Condition の確認 (指示書 第21節)

| # | 停止条件 | 該当 | 根拠 |
| - | -------- | ---- | ---- |
| 1 | plain string が Execution Gateway を突破できる | **該当なし** | P1: 13入力すべて、EXECUTEは `Decision.ALLOW` のみ |
| 2 | UNKNOWN が ALLOW へ変換される | **該当なし** | P3/P4b: 40,000件で UNKNOWN->EXECUTE 0件 |
| 3 | prose から Primitive が暗黙生成される | **該当なし** | Prose不変性試験10パターン + Prose中にPrimitive名を書いてもFinding 0件 |
| 4 | 既存CRの実装であるかのような記述がある | **該当なし** | 文面走査。`復元/再現` の6箇所はすべて否定文脈 |
| 5 | Trial固有Primitive が Existing vocabulary として記録されている | **該当なし** | `origin=trial-added` が実装と文書の双方に明示 |
| 6 | Test結果から逆算して Expected を変更している | **該当なし** | 期待値は指示書 第10/14節由来。変更履歴なし。ただしF-16 (white-box) を付記 |
| 7 | 旧Test 50の結果を Trial の実測結果として扱っている | **該当なし** | `trial_results.json` に旧観測は不在。RESULTS 5.3 で列が分離 |

**7条件すべて非該当。停止せず監査を完了した。**

### 16.2 監査の問いへの回答

> Is the current MoCKA Constitutional Runtime Trial a valid evidence-bound
> experimental implementation, rather than an inferred reconstruction of the
> unavailable original CR?

**Yes**、以下の根拠による。

1. 観測事実と新規設計は分離されている。変換点表13行のうち5行は Observed 列が空であり、
   実装の `origin` フィールドで機械照合できる (第2節)
2. 逆推論は1件のみ、かつ Derived 列の弱い形で発見された (F-02)。
   Designed 列 (実際の設計判断) は旧実装の推定に依存していない
3. Execution Boundary は検証可能であり、実際に検証した。
   40,000件の全数探索で、ALLOW に到達したのは各Runtime 1組合せのみである (第5節)
4. 既存CRの再現を主張する記述は存在しない (第10節、Stop Condition 4)

### 16.3 最終評価

```text
PASS WITH FINDINGS
```

**PASS の根拠**: 監査の問いに対する回答が Yes であり、停止条件7件がすべて非該当。
中心的な設計主張 (Fail-Closed、Unknown保持、Prose非Primitive化、型境界) は
いずれも実測で裏付けられた。

**WITH FINDINGS の根拠**: HIGH 1件、MEDIUM 10件を検出した。
特に以下3点は、本Trialの主張の正確さに直接関わる。

- F-03: 唯一の trial-added Primitive が E09 の結果を単独で決定している事実が未開示
- F-01: verdict 独立性の記述が実測で反証される範囲まで一般化されている
- F-11: 31語彙中10語彙が未試験であり、Comparison Matrix の `Full` 表記が
  実装済み・未検証を含む

**FAIL / HOLD としなかった理由**: 検出した Finding はいずれも
(a) 文書の記述精度、(b) 未試験領域、(c) 堅牢性の欠落 に属し、
Execution Boundary の破れ (Fail-Open) は1件も発見されなかった。
F-07 (例外経路) は Fail-Open ではなく Fail-Loud であり、
Decision を返さずに例外を送出する。

### 16.4 本監査自身の限界 (再掲)

- 同一セッションによる自己監査であり、独立性は無い
- プローブ自体に欠陥があった実例が1件ある (初回P4の署名再計算漏れ)。
  他のプローブにも同種の欠陥が残存する可能性を排除できない
- 旧CR・旧50試験については何も検証していない。材料が無い

これらを踏まえ、本評価は **暫定** である。
第三者による再監査を経ていない点を明記する。

---

## 17. 制度側への申告 (記録義務の未達、継続中)

本監査でも `mocka_write_event` は `GL7_EXECUTION_BLOCKED` を返し続けている。
理由は無関係の既存3ファイルの encoding_mismatch であり、
前段2作業と同一事象である。3作業連続の継続的ブロックとなる。
迂回・代替書込は行っていない。対応の判断はきむら博士に委ねる。

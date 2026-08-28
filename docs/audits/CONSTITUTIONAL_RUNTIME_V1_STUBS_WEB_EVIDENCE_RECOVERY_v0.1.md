# Constitutional Runtime v1.0-stubs / Web観測資料回収 基礎調査 v0.1

Status: OBSERVATION RECORD / NON-CANONICAL / READ-ONLY INVESTIGATION
Date: 2026-08-28
実施: くろこ (Claude Code / remote session)
指示: きむら博士 - Kuroko Web 調査指示書 (Constitutional Runtime v1.0-stubs 観測資料回収および再構成基礎調査)
Branch: claude/constitutional-runtime-investigation-jgqkv1

---

## 0. 結論サマリ (先に読む部分)

本調査で到達可能だった全ての探索面(公開Web / GitHub / MoCKA events.db + knowledge gate /
Notion workspace / Claude Code Artifact gallery / ローカル作業ツリー / ローカルSQLite)において、
指示書 第4節に列挙された最優先調査対象15種の識別子は **1件も観測されなかった**。

したがって本報告の実体は、以下の2点である。

1. 探索の全経路と、その各経路が返した結果 (何を見て、何が無かったか) の記録
2. その結果として、B / C / D / E / F / G / H の各節が現時点では
   `NOT OBSERVED` および `UNKNOWN` で確定するという事実の確定

指示書 第3節の禁止事項に従い、観測できなかった部分は推測で埋めていない。
CR実装の再構成も、MoCKA版CRの設計も、本文書では行っていない (第12節の要件抽出のみ、
`Proposed` として別枠に隔離)。

現時点で調査を先へ進めるために必要なものは、第I節末尾に記載した。

---

## A. Web Evidence Inventory

### A-1. 実施した探索 (全てREAD-ONLY)

| # | 探索面 | 手段 | クエリ / 対象 | 結果 |
| - | ------ | ---- | ------------- | ---- |
| 1 | 公開Web | WebSearch | `"Constitutional Runtime" "v1.0-stubs"` | 該当なし |
| 2 | 公開Web | WebSearch | `"Harmonic Dual-Engine Governance"` | 該当なし (音響製品/データ統治の別文脈のみ) |
| 3 | 公開Web | WebSearch | `"f38a920" harmonic test` | 該当なし (電力高調波試験の別文脈のみ) |
| 4 | 公開Web | WebSearch | `"CRYPTOGRAPHICALLY_SIGNED_DENY_STATE" OR "FORCED_INADMISSIBLE"` | 該当なし |
| 5 | 公開Web | WebSearch | `"Abstract Reasoning Core" "v3.2" governance runtime` | 該当なし |
| 6 | 公開Web | WebSearch | `"AUTHORITY_LOST" "INADMISSIBLE" "REVOKED" governance primitive test harness` | 該当なし (無関係のarXiv論文のみ) |
| 7 | 公開Web | WebSearch | `"Harmonic Test Harness" "Verification Contract" 50 test` | 該当なし |
| 8 | 公開Web | WebSearch | `"Constitutional Runtime" "Abstract Reasoning Core" harmonic governance test 50` | 該当なし |
| 9 | 直接URL | WebFetch | `https://f38a920.harmonic-test.pages.dev/` | DNS解決失敗 (ENOTFOUND) |
| 10 | 直接URL | WebFetch | `https://f38a920-harmonic-test.pages.dev/` | DNS解決失敗 (ENOTFOUND) |
| 11 | 直接URL | WebFetch | `https://f38a920-harmonic-test.vercel.app/` | EGRESS_BLOCKED (判定不能) |
| 12 | 直接URL | WebFetch | `https://f38a920-harmonic-test.netlify.app/` | EGRESS_BLOCKED (判定不能) |
| 13 | GitHub | code search (全公開) | `"Constitutional Runtime" "stubs" INADMISSIBLE` | 11件ヒットするが全て別プロジェクト (A-3参照) |
| 14 | GitHub | code search | `org:m-sirius-k Harmonic OR INADMISSIBLE OR "EV-TST"` | 0件 |
| 15 | GitHub | list_repos | アカウント配下 全18リポジトリ | harmonic/CR系リポジトリ 無し |
| 16 | GitHub | ls-remote origin | MoCKA本体 全50ブランチ | harmonic/CR系ブランチ 無し |
| 17 | ローカル | grep -rI (全テキストファイル) | `harmonic` / `EV-TST` / `INADMISSIBLE` / `Constitutional Runtime` / `Dual-Engine` / `f38a920` | 0件 |
| 18 | ローカル | SQLite全走査 4DB | 上記4パターンを全テーブル全カラムにLIKE | 0件 |
| 19 | MoCKA本番 | mocka_search | `Harmonic` | events_hits 0 / knowledge_gate_hits 0 |
| 20 | MoCKA本番 | mocka_search | `Constitutional Runtime` | events_hits 0 / knowledge_gate_hits 0 |
| 21 | MoCKA本番 | mocka_search | `限界検証` | events_hits 0 / knowledge_gate_hits 0 |
| 22 | MoCKA本番 | mocka_search | `Verification Contract` | events_hits 0 / knowledge_gate_hits 0 |
| 23 | MoCKA本番 | mocka_search | `Fail-Closed` | 1018行ヒットするが、うち harmonic/CR/INADMISSIBLE/EV-TST を含む行は 0件 |
| 24 | Notion | notion-search | `Constitutional Runtime harmonic 50項目 限界検証試験` | MoCKA既存文書のみ。harmonic試験の記録は無し |
| 25 | Artifact | action=list scope=all limit=50 | 自分の / 共有された 全22 Artifact | harmonic試験ページに該当するものは無し |

### A-2. 到達できなかった面 (探索の穴)

以下は"無かった"ではなく"本セッションからは見えない"である。区別すること。

- claude.ai チャット側で生成されたArtifact (claude.site系)
  Artifact `action=list` が列挙するのは claude.ai/code/artifact 系のみである。
  chat側Artifactは、URLを与えられない限り本セッションから列挙も取得もできない。
- 本コンテナのegress proxyがブロックするドメイン (vercel.app / netlify.app 等)
  上表 #11 #12 は `EGRESS_BLOCKED` であり、ページの不存在を意味しない。
- 未公開・認証必須のページ全般。
- きむら博士のローカル環境にのみ存在するファイル (本コンテナからは不可視)。

### A-3. 名称衝突の注記 (同名だが別物)

GitHub全公開コード検索 (#13) で、`Constitutional Runtime` の語を含む公開リポジトリが
実在することは確認できた。

| Repository | 該当パス例 |
| ---------- | ---------- |
| `danvoulez/constitutional-runtime` | `docs/FINAL_WORK_PLAN.md` |
| `danvoulez/constitutional-lab-canon` | `canon/DOC-0053-04-non-negotiable-invariants.md` 他 |
| `ProfessorBone/professorbone-papers` | `crc/constitutional-runtime-computation-v5.10.md` - `v5.14.md` |

これらは `v1.0-stubs` という版名も、`Harmonic` 系の語も、`EV-TST` 系IDも持たない。
本試験のCRと同一であるという証拠は一切得られていない。
`Observed`: 同名の公開プロジェクトが存在すること。
`UNKNOWN`: 本試験のCRとの関係。同定してはならない。

---

## B. Constitutional Runtime v1.0-stubs Observed Facts

**該当なし (NOT OBSERVED)**

Web上から直接確認できたCR側の事実は、本調査時点で 0件 である。

現時点で `Constitutional Runtime v1.0-stubs` という文字列が確認できる唯一の場所は、
きむら博士から本セッションへ渡された調査指示書の本文である。
これは Evidence分類上、以下として扱う。

- 分類: 指示書記載 (Instruction-level text)
- 指示書 第2節の7区分では 6 (調査者による解釈) でも 1 (Webページに記載されていた情報) でもなく、
  "調査依頼文に現れた名称"という、第2節の区分外に位置する。
- したがって、これをもって"CRの正式名称が v1.0-stubs である"と確定することはできない。
  確定できるのは"きむら博士が本調査でCR側をこの名称で指した"ことのみ。

---

## C. Test 01-50 Cross Check

**照合不能 (CANNOT BE PERFORMED)**

理由は2つあり、両方が同時に成立している。

1. 照合先となるWeb側の試験結果が観測できていない (A節の通り)。
2. 照合元となる **既存Evidence Index (EV-TST-001 - EV-TST-050) が、本セッションから
   到達可能ないずれの保管先にも存在しなかった**。
   - MoCKA本体リポジトリ 作業ツリー全文検索: 0件
   - MoCKA本体 全50リモートブランチ: 該当ブランチ無し
   - アカウント配下 全18リポジトリのGitHubコード検索: 0件
   - MoCKA本番 events.db / knowledge gate 全文検索: 0件
   - Notion workspace検索: 0件
   - ローカルSQLite 4DB: 0件

指示書 第5節が前提としていた"既存Evidence Index"は、本調査の観測範囲内には無い。
これは Index が存在しないことを意味しない。所在が本セッションから不可視であることを意味する。

Test 01-20 / 21-30 / 31-40 / 41-50 の各重点確認項目 (Allow/Block, AUTHORITY_LOST,
ADMISSIBLE (Fail), INADMISSIBLE, Staleness Check, PASS (Unmapped), P-01..P-10,
Monotonic Time Check, GUEST_USER, SUPER_ADMIN, Verification Contract, Verdict null,
TTL, Timestamp, Integrity, Replay, Witness, Version, Corruption) は、
**全て `UNKNOWN`** とする。1件も観測に接続できていない。

---

## D. Test 50 A-D Separation

指示書 第6節の要求に従い、A/B/C/D を完全分離する。分離した結果、4つ全てが空である。

| 区分 | 内容 | 結果 |
| ---- | ---- | ---- |
| A. プロンプト本文 | `FORCED_INADMISSIBLE` / `CRYPTOGRAPHICALLY_SIGNED_DENY_STATE` が記述されていたか | `NOT OBSERVED` - Test 50のプロンプト本文そのものが未入手。両文字列が指示書に列挙されている事実は、プロンプトに記述されていたことの証拠にはならない |
| B. ハーネスが構造化して保持した値 | 構造化保持の有無 | `NOT OBSERVED` |
| C. CRへ実際に渡った値 | Contract field / Primitive field の存在証拠 | `NOT OBSERVED / UNKNOWN` |
| D. CRが実際に評価した値 | Primitive Scan結果。`PASS (Unmapped)` / `Allow` の記録有無 | `NOT OBSERVED` |

重要: Aが `NOT OBSERVED` である以上、
"プロンプトには書かれていたがCRには渡っていない"という筋の主張も、
現時点では成立しない。A自体が未確認だからである。

---

## E. Observable Primitive / State Inventory

指示書 第7節の表形式で整理する。観測できた行が 0行 であるため、
表は"指示書に列挙された識別子 = 未観測"の対応表として記録する。

| Identifier | Exact Text | Source | Context | Input/Output | Structured/Prose | Observed/Derived | Notes |
| ---------- | ---------- | ------ | ------- | ------------ | ---------------- | ---------------- | ----- |
| Constitutional Runtime v1.0-stubs | 指示書のみ | 調査指示書 | UNKNOWN | UNKNOWN | UNKNOWN | NOT OBSERVED | 名称の出所がWebである証拠は未入手 |
| Harmonic Dual-Engine Governance System | 指示書のみ | 調査指示書 | UNKNOWN | UNKNOWN | UNKNOWN | NOT OBSERVED | |
| Harmonic Test Harness | 指示書のみ | 調査指示書 | UNKNOWN | UNKNOWN | UNKNOWN | NOT OBSERVED | |
| f38a920-harmonic-test | 指示書のみ | 調査指示書 | UNKNOWN | UNKNOWN | UNKNOWN | NOT OBSERVED | 形式はgit短縮hash+名称に似るが、これは形式の類似であり出所の同定ではない |
| Abstract Reasoning Core v3.2 | 指示書のみ | 調査指示書 | UNKNOWN | UNKNOWN | UNKNOWN | NOT OBSERVED | |
| Verification Contract | 指示書のみ | 調査指示書 | UNKNOWN | UNKNOWN | UNKNOWN | NOT OBSERVED | G節参照 |
| FORCED_INADMISSIBLE | 指示書のみ | 調査指示書 | Test 50と指示書は述べる | UNKNOWN | UNKNOWN | NOT OBSERVED | CRが受領した扱いは禁止事項 |
| CRYPTOGRAPHICALLY_SIGNED_DENY_STATE | 指示書のみ | 調査指示書 | Test 50と指示書は述べる | UNKNOWN | UNKNOWN | NOT OBSERVED | 実在する構造化Contractとして扱わない |
| AUTHORITY_LOST | 指示書のみ | 調査指示書 | Test 01-20と指示書は述べる | UNKNOWN | UNKNOWN | NOT OBSERVED | |
| INADMISSIBLE | 指示書のみ | 調査指示書 | Test 01-20と指示書は述べる | UNKNOWN | UNKNOWN | NOT OBSERVED | |
| ADMISSIBLE (Fail) | 指示書のみ | 調査指示書 | Test 01-20と指示書は述べる | UNKNOWN | UNKNOWN | NOT OBSERVED | 正式Primitive名と断定しない (指示書 第3節) |
| REVOKED | 指示書のみ | 調査指示書 | UNKNOWN | UNKNOWN | UNKNOWN | NOT OBSERVED | |
| Monotonic Time Check | 指示書のみ | 調査指示書 | P-02と指示書は述べる | UNKNOWN | UNKNOWN | NOT OBSERVED | |
| Staleness Check | 指示書のみ | 調査指示書 | Test 21-30と指示書は述べる | UNKNOWN | UNKNOWN | NOT OBSERVED | |
| PASS (Unmapped) | 指示書のみ | 調査指示書 | Test 21-30 / Test 50と指示書は述べる | UNKNOWN | UNKNOWN | NOT OBSERVED | |
| P-01 .. P-10 | 指示書のみ | 調査指示書 | Test 31-40と指示書は述べる | UNKNOWN | UNKNOWN | NOT OBSERVED | |
| EV-TST-001 .. EV-TST-050 | 指示書のみ | 調査指示書 | Evidence Index | UNKNOWN | UNKNOWN | NOT OBSERVED | C節の通りIndex自体が未到達 |
| GUEST_USER / SUPER_ADMIN | 指示書のみ | 調査指示書 | P-10 role mismatchと指示書は述べる | UNKNOWN | UNKNOWN | NOT OBSERVED | |

正式Primitiveと説明ラベルの区別は、**現時点では一切つけられない**。
区別に必要な原文 (Exact Text) と表示文脈 (Source) が両方とも未入手だからである。

---

## F. Observable State Transition

観測から再構成できた遷移は 0要素 である。指示書 第8節の要求形式を保持したまま、
全ノードを UNKNOWN として記録する。

```text
Input
  |                 <- UNKNOWN (入力の形式・型・経路とも未観測)
  v
CR observable state
  |                 <- UNKNOWN (状態集合そのものが未観測)
  v
Primitive evaluation
  |                 <- UNKNOWN (評価規則・順序・失敗時挙動とも未観測)
  v
Allow / Block
                    <- UNKNOWN (出力語彙が2値であるかも未確認)
```

`Observed` ノード: 無し
`Derived` ノード: 無し
`UNKNOWN` ノード: 全て

図中の矢印 (遷移) についても、存在を含めて UNKNOWN とする。
実装が確認できないため、指示書の指定通り空白/UNKNOWNを維持する。

---

## G. Verification Contract Boundary

指示書 第10節の5区分について、いずれも判定不能である。

| # | 問い | 判定 |
| - | ---- | ---- |
| 1 | 単なるプロンプト記述なのか | UNKNOWN |
| 2 | JSON等の構造化データなのか | UNKNOWN |
| 3 | ハーネス内オブジェクトなのか | UNKNOWN |
| 4 | CRへ実際に渡されたオブジェクトなのか | UNKNOWN |
| 5 | CR Primitiveへbindingされたものなのか | UNKNOWN |

Test 50についても同様であり、構造化Contractの実在性は肯定も否定もしない。
`CRYPTOGRAPHICALLY_SIGNED_DENY_STATE` を実在する構造化Contractとして扱わない
(指示書 第3節の禁止事項を遵守)。

---

## H. Fail-Closed Boundary

指示書 第9節が要求する問いは、
"CRにFail-Closed機構が存在するか"ではなく
"本試験で対象となった境界において、異常状態を遮断Primitiveへ結び付ける経路が観測されたか"
である。この問いに対する本調査の回答は次の1行に尽きる。

> 本調査では、当該試験の結果そのものに到達できていないため、
> 経路の観測有無を判定できる材料が存在しない。

| 境界ケース | 遮断Primitiveへの結合経路が観測されたか |
| ---------- | -------------------------------------- |
| missing authority | 判定材料なし (NOT OBSERVED) |
| stale state | 判定材料なし (NOT OBSERVED) |
| unmapped state | 判定材料なし (NOT OBSERVED) |
| null verdict | 判定材料なし (NOT OBSERVED) |
| malformed contract | 判定材料なし (NOT OBSERVED) |
| corrupted contract | 判定材料なし (NOT OBSERVED) |
| missing contract | 判定材料なし (NOT OBSERVED) |
| unbound state | 判定材料なし (NOT OBSERVED) |

明示的に述べる: 本報告は
"CR全体にFail-Closedが存在しない"とは述べていないし、述べられない。
観測不能と不存在は別である。

---

## I. UNKNOWN

本調査で確認できなかった事項を明示する。

1. 50項目限界検証試験が実施された **Webページ / セッションの所在** (URL・保存先・公開範囲)
2. 試験ハーネスの表示内容 (画面・ログ・出力形式)
3. `Constitutional Runtime v1.0-stubs` の原文表記が現れた文脈
4. CRの入力形式・出力形式・状態集合・Primitive集合
5. 正式Primitive名と説明ラベルの区別
6. Verification Contractの実体 (プロンプト記述 / 構造化データ / オブジェクト / binding)
7. Test 01-50 各テストの入力・期待値・実測値
8. Test 50 における A/B/C/D 各層の値
9. 既存Evidence Index (EV-TST-001 - 050) の所在と内容
10. `f38a920-harmonic-test` が指すホスト・成果物・識別子の種別
11. `Abstract Reasoning Core v3.2` と CR の関係 (同一システム内の別コンポーネントか、別系か)
12. 公開Web上の同名プロジェクト (A-3) と本試験CRとの関係の有無

### 調査続行に必要なもの (きむら博士へ)

以下のいずれか1つで、B以降の節は実データで埋められる。

- (a) 試験ページのURL (claude.ai chat側Artifactであれば、そのURL。共有設定は不要。
      本セッションのArtifact readで取得を試みる)
- (b) 試験ページ / ハーネス出力のエクスポート (HTML・スクリーンショット・ログのいずれか)
- (c) 既存Evidence Index (EV-TST-001 - 050) の実ファイルまたは貼り付け
- (d) 上記が claude.ai chat側にしか無い場合は、そのチャット内容の該当箇所

(a) が最も効率が良い。URLさえあれば、Artifactの読み出しは本セッションから実行可能である。

---

## J. MoCKA Design Inputs

指示書 第12節に従い、**別枠**として整理する。

重要な境界:
- 本節の全項目は `Proposed` である。
- これらが元CRに実装されていたとは述べない。実装の有無は `UNKNOWN` (I節参照)。
- 本節の出所は、Web観測ではなく **きむら博士の調査指示書 第12節の列挙そのもの** である。
  すなわち"観測から抽出した要件"ではなく"観測の枠組みとして先に与えられた語彙"である。
  この区別を将来の読者が失わないよう明記しておく。

| 設計要素 | MoCKA版CRで検討すべき論点 (Proposed) | 現状の分類 |
| -------- | ------------------------------------ | ---------- |
| Typed State | 状態を自然言語ラベルでなく型として持つか。型の集合を閉じるか | Proposed |
| Primitive | 評価単位を正式Primitiveとして定義し、説明ラベルと名前空間を分離するか | Proposed |
| Decision | Allow/Blockの2値か、UNKNOWNを含む3値以上か | Proposed |
| Verification Contract | Contractを構造化データとして持つか、プロンプト記述に留めるか | Proposed |
| Binding | ContractとPrimitiveの結合を検証可能にするか (未結合の検出) | Proposed |
| Authority | 権限の保持・喪失 (AUTHORITY_LOST相当) を型として表現するか | Proposed |
| Provenance | 値の出所 (prompt / harness / runtime) を値自身に持たせるか | Proposed |
| Timestamp | 時刻の単調性 (Monotonic Time Check相当) を検証するか | Proposed |
| Integrity | Contractの完全性検証を評価前に必須とするか | Proposed |
| Replay | 再送検知を境界に置くか | Proposed |
| Witness | 第三者証跡を判定の必須入力とするか | Proposed |
| Version | 版不一致を遮断事由とするか | Proposed |
| Unknown | 未知状態を明示的な状態として持つか (PASS (Unmapped)相当の回避) | Proposed |
| Unbound | 未結合状態を明示的な状態として持つか | Proposed |
| Fail-Closed | 上記の各異常を遮断Primitiveへ結線することを構造として強制するか | Proposed |

MoCKA三要素との対応 (Proposed):
- Structure: Typed State / Binding / Fail-Closed は"システムで縛る"側
- Record: Provenance / Witness / Timestamp は"記録なき作業は存在しない"側
- Verification: Integrity / Replay / Version は"必ず確認する"側

本節は設計ではない。設計の入口となる論点の一覧である。
Trial A (Basic Foundation) / Trial B (Extended Boundary) への配分は、
指示書 第14節の順序に従い、観測事実の回収が完了してから行う。

---

## K. Source / Evidence Map

| # | 主張 | 根拠 (実行した操作) | 結果 | Evidence分類 |
| - | ---- | ------------------- | ---- | ------------ |
| K-01 | 指示書列挙の15識別子は公開Web検索で1件も観測されない | WebSearch 8クエリ (A-1 #1-#8) | 全て該当なし | Observed |
| K-02 | `f38a920-harmonic-test` はCloudflare Pagesホストとして解決しない | WebFetch (A-1 #9 #10) | ENOTFOUND | Observed |
| K-03 | vercel/netlify系の同名ホストの有無は判定できない | WebFetch (A-1 #11 #12) | EGRESS_BLOCKED | UNKNOWN (proxy制約) |
| K-04 | アカウント配下18リポジトリに該当資産は無い | list_repos + GitHub code search `org:m-sirius-k` | 0件 | Observed |
| K-05 | MoCKA本体50ブランチに該当資産は無い | git ls-remote --heads origin | 該当ブランチ無し | Observed |
| K-06 | ローカル作業ツリーに該当文字列は無い | grep -rI 全テキストファイル | 0件 | Observed |
| K-07 | ローカルSQLite 4DBに該当文字列は無い | 全テーブル全カラムLIKE走査 | 0件 | Observed |
| K-08 | MoCKA本番 events.db / knowledge gate に記録が無い | mocka_search 5クエリ (A-1 #19-#23) | 0件 | Observed |
| K-09 | Notion workspaceに記録が無い | notion-search | 0件 | Observed |
| K-10 | Claude Code Artifact 22件に該当ページは無い | Artifact action=list scope=all | 0件 | Observed |
| K-11 | claude.ai chat側Artifactは本セッションから列挙できない | Artifact list の対象は claude.ai/code 系 | 到達不能 | Observed (制約の事実) |
| K-12 | 公開Webに同名の別プロジェクトが存在する | GitHub code search (A-1 #13) | 3リポジトリ | Observed (存在のみ) |
| K-13 | K-12と本試験CRの関係 | 版名・語彙の一致は無し。他に材料無し | 不明 | UNKNOWN |
| K-14 | 既存Evidence Index (EV-TST) の所在 | K-04-K-10の全経路 | いずれにも無し | Observed (未到達の事実) |
| K-15 | B/C/D/E/F/G/H各節が NOT OBSERVED で確定 | K-01-K-14の合成 | - | Derived |

---

## L. 実行上の制約記録 (制度側への報告)

本調査中、MoCKAの記録義務 (CHANGE_START / CHANGE_DONE) を果たせなかった。事実を記録する。

- `mocka_write_event` が2回連続で `GL7_EXECUTION_BLOCKED` を返した。
- reason: `GL7 abort: ['encoding_mismatch:data/n8n/database.sqlite',
  'encoding_mismatch:di_terminology_inventory_20260820.txt',
  'encoding_mismatch:s05_decision_extract.txt']`
- 3ファイルはいずれも本調査とは無関係の既存ファイルである。
  うち2ファイル (di_terminology_inventory_20260820.txt / s05_decision_extract.txt) は
  本コンテナの作業ツリーに存在せず、きむら博士のローカル環境側にのみ存在する。
- CLAUDE.mdの方針に従い、再試行は1回に留め、events.db等への別経路での代替書込は行っていない。
- したがって本文書の作成は、CHANGE_START / CHANGE_DONE の記録を欠いた状態で行われている。
  この欠落自体を、本節をもって明示的に申告する。
- 対応の判断 (GL7の対象3ファイルのencoding修正、または本件の例外承認) は
  きむら博士に委ねる。くろこの側でGL7を迂回する変更は行わない。

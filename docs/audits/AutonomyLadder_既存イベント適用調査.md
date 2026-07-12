# Autonomy Ladder（L0〜L5再定義案）既存イベント適用調査

作成日: 2026-07-08
作成者: Claude（くろこ）
位置づけ: 指示書「R01査読対応・拡大調査（v2最適化版）」TASK-4 成果物
調査範囲: 調査のみ。実コード変更・分類の確定は行っていない。
表記ルール: 全てのイベント分類は「仮分類候補＋確定不可の明記」で統一する
（指示書v2 TASK-4の禁止表記ルールに従う。断定形は使用しない）。
適用条件: 監査官R01裁定（TASK-3結果確認、2026-07-08）で指定された接続チェーン
「Autonomy Level → Required Human Gate → Decision Event → Execution Permission → Evidence」
を各イベントごとに確認する。
一次データ: app.py（auto_audit_loop, _auto_approve_prevention, decision_approve）,
watchdog_mocka.py, governance/seal_governance_gate.py, structural/execution_governance.py（GL7）,
phi_os/human_gate.py, governance/mocka_git_safe_commit.py。

---

## 0. 調査結論サマリー

**コードベース全体を`Autonomy Ladder`/`autonomy_level`/`AUTONOMY_L`等のキーワードで
grepした結果、既存実装は皆無であることを確認した（本調査中に作成した監査文書
以外に1件もヒットしなかった）。** Autonomy Ladderは現時点で純粋な新規提案であり、
「既存の実装がLadderとして機能しているか、単なる表示層か」という監査官R01の問いに対する
答えは、**「そのどちらでもなく、Ladderという概念自体がまだ存在しない」**である。

ただし、L0〜L5に相当する**挙動**は既に実運用イベント群の中に混在して存在する。
それらは統一的なLevel概念で管理されておらず、個々のイベントごとに異なる強度の
Human Gate接続（強いものから皆無のものまで）を持ったまま並存している。
本調査はこの現状を仮分類・接続チェーン確認の形で可視化する。

---

## 1. 既存自動実行イベント一覧 × 仮分類候補（確定不可）× 接続チェーン確認

L0=観測のみ / L1=提案生成 / L2=変更案生成 / L3=Human承認後実行 / L4=限定自律実行 / L5=将来の完全自律
（指示書原文のL0-L5定義に準拠）

### 1.1 AUTO_SEAL_50EVT（app.py auto_audit_loop、event_count差分50到達分岐）

```
仮分類候補 L3寄り（是正後）/ 是正前はL4相当の挙動だった
（確定不可・TODO_370/371結論待ち）
```

- Autonomy Level: 未定義（Ladder自体が存在しないため「どこで決定されるか」という問いに対する答えは「決定する仕組みがない」）
- Required Human Gate: 2026-07-08是正後はAUTO_SEAL_PENDINGイベント記録により「人間の関与が必要」という状態は作られるが、それを要求する明文の承認条件（severity別の要否等）は存在しない
- Decision Event: なし（PENDING記録はEvent Ledgerへの記録であり、Decision Ledgerへの記録ではない）
- Execution Permission: 実行前チェックなし。人間が別途`human_gate_override_event_id`を手動特定してmocka_git_safe_commitを呼ぶ運用に依存（TASK-2 2.4節参照）
- Evidence: mocka_git_safe_commit()のpost_commit_files/post_commit_violationにより事後検証は可能（TODO_426是正済み）

### 1.2 AUTO_SEAL daily（app.py auto_audit_loop日次分岐 / watchdog_mocka.py try_daily_seal）

```
仮分類候補 L3寄り（是正後、1.1と同型）
（確定不可）
```
- 接続チェーンは1.1と同一パターン。watchdog_mocka.py側は現在実プロセスとして稼働していない（dormant、TASK-1で確認済み）。

### 1.3 `_auto_approve_prevention()`（app.py 2023-2049行、NORMAL/CAUTION Prevention自動承認）

```
仮分類候補 L4〜L5相当の挙動
（確定不可。Ladder上の位置づけは未検討だが、Human Gateが一切介在しない点でL3以下ではない）
```

- Autonomy Level: 未定義
- Required Human Gate: **なし。severity=NORMAL/CAUTIONは無条件で`approved_by="AUTO_GATE"`として自己承認される（コード確認済み、HIGH/CRITICALのみHuman Gateへ回る）**
- Decision Event: なし
- Execution Permission: なし（チェックそのものが存在しない）
- **Evidence: なし。本関数の実行はappend_event()もmocka_write_event()も一切呼び出しておらず（コード確認済み、2023-2049行にwrite_event系呼出は存在しない）、実行された事実そのものがEvent Ledgerに残らない。** これは指示書TASK-5（Exit Condition）が問題にする「AIの自己申告のみでの完了扱い」以前の状態であり、**自己申告すら発生しない無記録の自動実行**という、本調査で確認した中で最も証跡の薄いケースである。

### 1.4 GL7 `pre_execution_check()`（structural/execution_governance.py、機械的dry run判定）

```
仮分類候補 L2（変更案生成、機械的検査のみ）
（確定不可。GL7自身は実行しないため単体ではL3以上に届かない設計）
```
- Required Human Gate: GL7自身のdocstringが「承認が別途必要」と明記(TASK-2で確認済み)
- Decision Event: `_emit_gl7_event()`によりphi_os/event_busへALLOW/DENYイベントを転送（fail-soft、失敗してもGL7判定はブロックしない）
- Execution Permission/Evidence: GL7単体は実行主体ではないため該当なし（呼び出し元次第）

### 1.5 SealGovernanceGate.execute()（`/audit/seal` MANUAL_SEAL、GL7 ALLOW→即実行）

```
仮分類候補 L4相当の挙動（L3を名乗るが実態はL4に近い）
（確定不可。IC_20260708_004の対象そのもの）
```
- Autonomy Level: 未定義
- Required Human Gate: 名目上「MANUAL」だが、実際にはHTTPエンドポイントへのPOST 1回のみで足り、その要求元が人間かどうかを区別する認証機構がapp.pyに存在しない（TASK-2で確認済み）
- Decision Event: あり（`_record_decision_unit()`によりdecision_ledger.jsonlへ記録、ただしapproved_by="system:seal_governance_gate"というシステム主体名義）
- Execution Permission: GL7のALLOWのみ（機械的検査、Human Gate未経由）
- Evidence: あり（Decision Ledger記録+anchor_update.py実行結果）
- **これはTASK-2で発見したIC_20260708_004の対象そのものであり、Autonomy Ladderの観点からは「L3を名乗りながら実態としてL4相当の自律度で動いている」境界事例として明示的に記録する。**

### 1.6 phi_os/human_gate.py Review Gate（Reason Unit→Knowledge Assets昇格審査、TODO_396）

```
仮分類候補 L3（Human承認後実行に最も近い実装）
（確定不可。ただし「実行」自体は本モジュールの責務外であり、承認記録までに留まる）
```
- Autonomy Level: 未定義
- Required Human Gate: あり。`/api/human_gate/approve`への明示的HTTP呼出が必須（TRANSITIONS辞書によりPENDING以外からのapprove遷移は拒否される、コード上のfail-closed設計を確認済み）
- Decision Event: 承認イベント自体はhuman_gate_eventsテーブルに記録されるが、decision_ledger.jsonlへは接続していない（TASK-2で確認済み、`related_documents`等の相互参照フィールドなし）
- Execution Permission/Evidence: 「昇格の実体化はTODO_396スコープ外」とコード自身が明記しており、承認記録より先（実際にKnowledge Assetsへ反映する処理）は未実装

### 1.7 `mocka_git_safe_commit()`の`human_gate_override_event_id`（Phase1チャット承認方式）

```
仮分類候補 L3として運用されているが、機構としての強制力はL4寄り
（確定不可）
```
- Required Human Gate: 運用上は「人間がチャットで承認しevent_idを伝える」ことが前提だが、コード上は**渡されたevent_idが本当にHuman Gate相当の承認を表すか検証しない**（TASK-2 3章#2で確認済み）。つまり制度としてはL3（人間承認後実行）を意図しているが、実装としてはその意図を強制する仕組みがなく、L4的な「検証なき自律実行」も技術的には可能な状態にある。

### 1.8 essence自動連鎖（`_trigger_essence_chain`, `_upd`（decision_approve内）等の派生自動処理）

```
仮分類候補 L4（既に人間承認された事項の派生的自動反映のみ）
（確定不可。ただしCore System Fileへの書込みは行わないため、リスクの質が1.1-1.5とは異なる）
```
- 人間承認（decision_approve等）の後にのみ起動する設計であり、単体で新たな承認なき変更を行うわけではない。派生的自動処理としてはL4相当でも許容されうる性質のものと考えられる（推測、最終判断はHuman Gateに委ねる）。

---

## 2. 「Human Gate Policy事前認証済み」の実績要件について

指示書原文が求める「既存のどのイベントが『認証済み』の実績要件（一定期間の実績、承認率等）を
満たしているか」について調査した結果、**そのような実績要件（トラックレコード基準）自体が
MoCKA内のどの文書にも定義されていないことを確認した**（docs/governance配下、TODO/Decision
Ledger全件を対象にキーワード検索したが該当なし）。したがって現時点では「満たしている
/満たしていない」を判定する基準自体が存在せず、この問いには「未定義」としか回答できない。
実績要件の設計自体がAutonomy Ladder提案の一部として今後必要になる（推測）。

---

## 3. L3/L4境界が曖昧になりうるエッジケース

1. **SealGovernanceGate（1.5）**: 名目「MANUAL」・実態「機械的検査のみで実行」。
   L3を名乗る実装がHuman Gate接続の欠如によりL4相当の自律度で動いてしまう典型例。
2. **`_auto_approve_prevention()`（1.3）**: severityという1軸の閾値のみでL3(HIGH/CRITICAL)と
   L4以上相当(NORMAL/CAUTION)が分岐しており、Autonomy Ladderの多軸評価（実績・スコープ・
   影響範囲等）が導入された場合、この単純な閾値分岐がどのLevelに再配置されるべきかが
   不明瞭になる。
3. **`human_gate_override_event_id`（1.7）**: 制度上の意図(L3)と実装上の強制力(L4的)が
   乖離している点で、TASK-1のb66af6c63/0f7f9b89c問題（「証明値の存在」と「証明値の意味保証」
   の分離、監査官R01指摘）と同一の構造的パターンを持つ。

---

## 4. 監査官R01指定チェーンの総括表

| イベント | Autonomy Level | Required Human Gate | Decision Event | Execution Permission | Evidence | チェーン完全性 |
|---|---|---|---|---|---|---|
| AUTO_SEAL_50EVT/daily | 未定義 | 曖昧(記録のみ) | なし | 人力運用依存 | 事後検証は可 | 不完全 |
| _auto_approve_prevention() | 未定義 | **なし** | なし | なし | **なし** | **最も欠落が大きい** |
| GL7単体 | 未定義 | あり(自己申告) | あり(event転送) | 該当なし(非実行主体) | 該当なし | 部分的(設計通り) |
| SealGovernanceGate(/audit/seal) | 未定義 | **名目のみ** | あり | GL7のみ(不十分) | あり | **IC_20260708_004対象** |
| Review Gate(human_gate.py) | 未定義 | **あり(fail-closed)** | 部分的(Decision Ledger未接続) | 該当なし(実行なし) | あり | 最も健全だが実行に届かない |
| override_event_id | 未定義 | 運用依存(未検証) | 該当する場合あり | なし(検証なし) | commit時のみ | 不完全 |

**総括: 監査官R01指定の5要素が全て揃っているイベントは、調査した範囲内に1件も存在しない。**
最も健全なReview Gateでさえ「実行」そのものに接続しておらず、最も自律的に見える
`_auto_approve_prevention()`は5要素中4要素が欠落している。

---

## 5. 推測・未確認の明示

- 1.8節（essence自動連鎖）のリスク評価は推測を含む。
- 2章の「実績要件が存在しない」という結論は、docs/governance配下とTODO/Decision Ledgerの
  検索に基づくが、他の文書（例: PlanningCaliber配下の未読文書）に断片的な言及がある
  可能性は完全には排除できない。
- 各イベントのLevel仮分類（1章）はいずれも指示書の禁止表記ルールに従い確定断定していない。
  最終的なLevel確定はTODO_370/371の結論およびAutonomy Ladder制度設計そのものの確定を待つ。

---

## 6. 次工程への申し送り

- `_auto_approve_prevention()`（1.3）は、TASK-1権限比較表・TASK-2並立Gate問題・TASK-4の
  いずれからも「最も証跡が薄い自動実行」として繰り返し検出された。TASK-7横断マッピングで
  優先度評価の対象とすること（現行パック2、TODO_428の対象と重複することも明記する）。
- SealGovernanceGate（1.5）はIC_20260708_004と同一対象であり、Autonomy Ladder導入時の
  「L3を名乗る実装の実態確認」の具体例としてそのまま流用できる。
- Review Gate（1.6）はHuman Gate接続の観点で最も健全な既存実装であり、HOLD拡張
  （TASK-2）・Execution Manifest（TASK-3）双方の実装ベースとして再利用を検討する価値がある
  （TASK-2 4章の設計提案と整合）。

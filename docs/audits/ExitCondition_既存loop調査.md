# Exit Condition（Loop Manifest）既存loop実装調査

作成日: 2026-07-08
作成者: Claude（くろこ）
位置づけ: 指示書「R01査読対応・拡大調査（v2最適化版）」TASK-5 成果物
調査範囲: 調査のみ。実コード変更は行っていない（監査官R01裁定によりTASK-5でも新規実装禁止）。
適用条件: 監査官R01裁定（TASK-4結果確認、2026-07-08）で指定された8項目
（loop_id/goal/entry_condition/exit_condition/human_intervention_point/
failure_transition/evidence_link/seal_state）と、指示書原文の
「AI申告のみでの完了扱い」排除原則（AI:「満たした」/System:「検証済み」の二段構造）を適用する。
一次データ: docs/governance/civilization_loop_investigation_v1.md（2026-06-28、既存調査）、
app.py（4つの背景ループ、/prevention/generate、_auto_incident_overdue）、
mocka_mcp_server.py（mocka_update_todo）、governance/human_gate_continuity.py。

---

## 0. 調査結論サマリー

**指示書が前提とする「civilization loop（Observe→Record→Incident→Recurrence→
Prevention→Decision→Action→Audit）」は、2026-06-28の既存調査（TODO_374/375）で
既に検証済みであり、8項目は連結されたパイプラインではなく、各段階が独立データソースから
個別に集計される8種類の健全性メトリクス（`/loop/status`ダッシュボード）であることが
判明している。** したがって「各段階のmax_iterations/exit_conditions/on_limit」を
探すという指示書の前提（連結ループであるという想定）は、この8段階そのものには
そのまま適用できない。本調査はこの既存結論を踏襲した上で、実際に存在する
バックグラウンドループ（4種）と、より本質的な「AI自己申告による完了扱い」の
実例を調査した。

**最重要発見: `mocka_update_todo`（MCPツール、TODO status更新）の`status="完了"`遷移には
System側の検証ゲートが一切存在しない。** これはAI（くろこを含む任意のAIセッション）が
自分自身の申告のみでTODOを「完了」化できる、コードレベルで確認された経路である。
本調査で確認した中で、指示書がいう「AI:『満たした』/System:『検証済み』の二段構造」の
欠如が最も直接的に当てはまる箇所である。

---

## 1. civilization loop 8段階の性質（既存調査の踏襲）

`docs/governance/civilization_loop_investigation_v1.md`（2026-06-28、Claude-sonnet-4-6作成、
Status: INVESTIGATION_REPORT）を確認した。結論を要約する。

- `/loop/status`（app.py 1470-1581行）の8項目は、いずれも独立したデータソースから
  ライブ計算される値であり、「Observeの出力がRecordへ流れ込む」といった
  コード上のパイプライン接続は実装されていない。
- ただし、8段階の一部に相当する**実処理連鎖**は別途存在する:
  `recurrence_registry.csv`（Recurrence）→`/prevention/generate`（Prevention投入）→
  `prevention_queue.json`→`_auto_approve_prevention()`/`/decision/approve`（Decision）
  →（Actionへの接続は本調査では未確認）→Audit。この連鎖は本調査で個別に確認した
  （2章・3章参照）。
- 本調査時点でこの既存結論を覆す新情報は得られなかった。**「8段階ループ全体」への
  max_iterations/exit_conditions探索は前提が成立しないため行わず、代わりに
  実在する処理連鎖・バックグラウンドループを個別に調査した。**

---

## 2. 実在するバックグラウンドループ4種 × 監査官R01指定8項目

app.pyの`start_background_loops()`（4115-4120行）が起動する常駐ループは以下の4種のみ
（コード確認済み、他は個別の非常駐スレッドまたはTimer）。

### 2.1 `auto_process_loop()`（PILSキュー監視、117-139行）

| 項目 | 内容 |
|---|---|
| loop_id | 明示的なID無し（関数名のみ） |
| goal | PILS(Person-In-the-Loop-System?)キューのJSON処理をcaliber_serverへ委譲 |
| entry_condition | サーバー起動時に自動開始（5秒待機後） |
| exit_condition | **なし（while True、無限ループ、正常設計）** |
| human_intervention_point | なし |
| failure_transition | 例外発生時はログ出力のみ、30秒待機後にループ継続（実質リトライ無限） |
| evidence_link | print出力のみ。events.dbへの記録なし |
| seal_state | 該当なし |

### 2.2 `auto_audit_loop()`（AUTO_SEAL、2052-2137行）

TASK-1/TASK-2/TASK-4で既に詳細調査済み。要約:

| 項目 | 内容 |
|---|---|
| loop_id | 明示的なID無し |
| goal | イベント50件到達/日次0時条件でseal要求をPENDING記録（2026-07-08是正後） |
| entry_condition | サーバー起動時に自動開始 |
| exit_condition | なし（while True、60秒周期） |
| human_intervention_point | PENDINGイベント記録後、人間が別途override_event_idを人力特定する運用（TASK-2 5.1節で「記録→判断」間の断絶として既出） |
| failure_transition | 例外発生時はログのみ、ループ継続 |
| evidence_link | events.db（AUTO_SEAL_PENDING）、mocka_git_safe_commit()のpost_commit検証 |
| seal_state | AUTO_SEAL_PENDING/AUTO_SEAL_PENDING_DAILY（実行前の停止状態を表す。ただし正式なseal_state列挙ではなくwhat_type文字列） |

### 2.3 `_guidelines_loop()`（ガイドライン定期更新、2852-2862行）

| 項目 | 内容 |
|---|---|
| loop_id | なし |
| goal | `interface/guidelines_engine.py`をscore_threshold=0.35, max_new=500で1時間毎実行 |
| entry_condition | 起動5分後、以降1時間毎 |
| exit_condition | なし（while True） |
| human_intervention_point | なし（全自動） |
| failure_transition | 例外時はログのみ、次周期まで待機して継続 |
| evidence_link | data/guidelines.jsonへの書込みのみ。events.dbへの記録は`_run_guidelines_engine()`内部の実装依存（本調査では未確認、guidelines_engine.py自体は未読） |
| seal_state | 該当なし |
| 備考 | `max_new=500`という**唯一のmax_iterations相当の制御**を発見した（1回の実行で新規生成するguideline件数の上限）。ただしこれは「ループの反復回数」ではなく「1回の実行内での生成件数」の上限であり、指示書がいうmax_iterations（ループ自体の反復上限）とは意味が異なる |

### 2.4 `_start_overdue_loop()`（締切超過TODO自動INCIDENT化、2732-2736行、Timer方式）

| 項目 | 内容 |
|---|---|
| loop_id | なし |
| goal | 締切超過キーワードを含む未完了TODOをOVERDUE_INCIDENTとしてevents.dbへ記録 |
| entry_condition | 起動時、以降`threading.Timer(3600, ...)`による自己再帰で1時間毎 |
| exit_condition | なし（自己再帰Timer、無限） |
| human_intervention_point | なし |
| failure_transition | 例外時はログのみ |
| evidence_link | events.db（OVERDUE_INCIDENT）。**同一TODOに対する重複生成を防ぐdedupチェック
  （`COUNT(*) FROM events WHERE title LIKE ? AND what_type='OVERDUE_INCIDENT'`）が
  実装されており、無限反復・過剰生成のリスクは実質的に低いことを確認した（2696-2727行）** |
| seal_state | 該当なし |
| 備考 | `OVERDUE_KEYWORDS = ['5/14','5/21','4/30','5/1','5/2','5/3','5/4','5/5']`が
  ハードコードされており、2026年5月前後の日付にしか反応しない。本調査時点（2026-07-08）
  では既に形骸化している可能性が高い（推測、Exit Conditionとは別軸の技術的負債として
  TASK-7へ申し送る） |

**2章の総括: 4ループとも「無限ループである」こと自体は、常駐監視サービスとしては
正常設計であり問題ではない。exit_conditionが存在しないこと自体が指示書の懸念する
リスクではなく、懸念すべきは各ループが生成する『判断・記録・実行』の間に
人間の介入点や検証点がどれだけ実装されているか、という質の問題である
（TASK-2 5.1節の「発生→記録→判断→実行→証跡」の連続性評価と同一の観点）。**

---

## 3. 最重要発見: `mocka_update_todo`のAI自己申告による完了扱い

`mocka_mcp_server.py`（458-490行）の`mocka_update_todo`実装を確認した。

```
AI(任意のセッション) → mocka_update_todo(id=TODO_xxx, status="完了")
  |
  status enum検証(TODO_STATUS_ENUM: 未着手/進行中/完了/保留/廃止のいずれかであるかのみ)
  |
  item["status"] = "完了"
  item["completed_at"] = 今日の日付
  completed[]へ移動
  |
  auto_log(name, args, ...)   # 監査ログ記録のみ
  |
  {"status": "ok"} を返す
```

**この経路には、以下のいずれの検証も存在しない。**

- 当該TODOに紐づくArtifact（成果物ファイル等）が実在するかの確認
- Decision Ledgerへの完了裁定記録の存在確認
- 人間（きむら博士）による承認の存在確認
- 「完了」を裏付ける他のイベント（CHANGE_DONE等）との整合性確認

これは、MoCKA自身の運用ルールとして存在する「状態昇格ルール」（Artifact存在→Review→
Test→Decision Record→Commit→TODO Status更新のみ昇格可能、memory記録より）という
**運用上の申し合わせ**が、`mocka_update_todo`という**ツールレベルでは一切強制されていない**
ことを意味する。指示書がいう

```
AI:     「条件Xを満たした」
System: 「検証済み」
```

の二段構造でいえば、`mocka_update_todo(status="完了")`は前者（AIの申告）のみで
完結しており、後者（Systemによる検証）に相当するコードが存在しない。
**これは本調査全体（TASK-1〜5）を通じて発見した中で、最も直接的に指示書の
懸念に合致する実例である。**

---

## 4. 二次発見: `_auto_approve_prevention()`のExit Condition観点での再整理

TASK-4で発見した`_auto_approve_prevention()`（app.py 2023-2049行）を、本タスクの
「Exit Condition」の観点から再整理する。NORMAL/CAUTION severityのPrevention案は、
`auto_audit_loop()`起動のたびに（1分周期のループ内、2054行`_auto_approve_prevention()`
呼び出し）無条件で`status="approved"`へ遷移する。これは「ループの終了条件」ではなく
「ループ内で個々の案件が持つ状態のexit（pending→approved）」に相当し、
**人間の介入点(human_intervention_point)が存在しない、かつevidence_linkも存在しない
（TASK-4で確認済み: append_event/mocka_write_event呼出なし）という点で、
3章のmocka_update_todoと同型の「無検証exit」である。**

---

## 5. 良い先例: `human_gate_continuity.py`の構造的拒否

TASK-2/TASK-3で確認した`governance/human_gate_continuity.py`の
`attempt_state_transition()`（197-212行）は、`governance_state`を
`WAITING_FOR_HUMAN_GATE`以外へ進めようとするあらゆる呼び出しを、呼び出し元が
誰であっても常に`HumanGateContinuityError`で拒否する設計になっている。
これは「実装しない」ことを運用ルールではなくコード構造そのもので担保する、
本調査で確認した中で唯一の「AI自己申告では絶対にexitできない」設計例である。
**3章・4章の問題を解消する際の実装パターンとして参考にできる（TASK-7で提案する
価値がある）。**

---

## 6. 推測・未確認の明示

- `_guidelines_loop()`が呼ぶ`interface/guidelines_engine.py`内部の記録有無は未読のため未確認。
- `auto_process_loop()`が呼ぶ`CALIBER_SERVER`（localhost:5679）側の処理内容・記録有無は
  本調査の範囲外（別サーバープロセス）。
- OVERDUE_KEYWORDSの形骸化（2.4節備考）は推測であり、実際に現在も該当するTODOが
  存在するかは未確認。
- `/prevention/generate`→`_auto_approve_prevention()`→Action段階への実際の接続
  （生成されたAction、もしあれば）は本調査では追跡していない。

---

## 7. 次工程への申し送り

- 3章（`mocka_update_todo`の無検証完了）と4章（`_auto_approve_prevention()`の無検証exit）は、
  TASK-7横断マッピングで「AI自己申告依存箇所リスト」の最上位2件として明記すること。
- 5章の`human_gate_continuity.py`の構造的拒否パターンは、3章・4章双方への解決策の
  ひな型として提示する価値がある（新規実装は本調査の禁止事項のため提案に留める）。
- TASK-2で確認した「発生→記録→判断→実行→証跡」の連続性評価は、本調査の4背景ループにも
  同一の枠組みで当てはめられることを確認した。TASK-7では両タスクの結果を統合した
  単一の評価軸として扱うことを推奨する。

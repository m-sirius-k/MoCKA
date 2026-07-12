# HUMAN_GATE_CLI_ALIGNMENT_REPORT

作成: Claude-sonnet-5(くろこ) / 2026-07-08 / read-only監査、TEST_CLI_VERIFY_001の復活・新規承認経路登録は行っていない

対象: `governance/human_gate_cli.py`(untracked、2026-07-08 10:16作成)

## 既存Human Gate 3系統との関係

本リポジトリには既に3つの独立したHuman Gate機構が存在する(過去セッションで確認済み)。

| 機構 | 実体 | 役割 |
|---|---|---|
| ① `phi_os/human_gate.py` | `human_gate_events`テーブル、`submit/approve/reject/get_state/list_pending` | 汎用のリクエスト提出・承認・却下フロー |
| ② `governance/mocka_git_safe_commit.py` | `human_gate_override_event_id`パラメータ | Core System Fileのcommit除外を上書きするための、他所で発行済みevent_idの引用のみ |
| ③ `app.py` `/decision/approve`エンドポイント | `prevention_queue.json`ベース | 別スキーマの承認キュー、`DECISION_APPROVED`イベントを発行 |

`governance/human_gate_cli.py`は、①`phi_os/human_gate.py`の`submit/approve/reject/get_state/list_pending`関数を**そのままimportして呼び出すのみ**(33行)。バックエンドロジックの再実装・Event Store(`human_gate_events`テーブル)の複製・イベント形式の変更はいずれも行っていない(6-20行のdocstringで明示的に対象外と宣言)。

## 新規機構か、入口追加か

**入口追加であり、新規の第4機構ではない。** ①の既存バックエンドに対する、MCPセッション断時でも使えるCLI/TTY入力チャネルを追加しているだけ。Router/Policyへの接続はなく(18行「本スクリプトは単体のProviderであり、Routerには未接続」)、`mocka_git_safe_commit()`の呼び出しも行わない(19-20行)。

## Decision Unitの要否

本ファイルのdocstring(8行)は「Human Gate CLI Provider（**Decision Unit B/C承認**、実装範囲限定）」と、既存のDecision Unit分類ラベルを自称している。しかし`decision_ledger.jsonl`全件を検索した結果、「Decision Unit」という文字列自体が一致するレコードは**ゼロ件**だった。つまりこのラベルは、ファイル作成者(別セッション/並行作業)が独自に付けた作業上の呼称であり、正式なDecision Ledger上のDecision Unitとして登録されたものではない。

新規にDecision Unit化するかどうかは、本レポートでは判断しない(きむら博士の判断事項)。ただし判断材料として: (a) 既存機構①への薄い入口追加に留まり新規の承認ロジックを持たない、(b) TTY強制という設計上の安全策自体は[[feedback_flag_autonomy_risk_in_governance_design]]の原則(AIが承認主体にならない)に合致している、という2点は確認済み。

## 権限境界

- `approve`/`reject`は`sys.stdin.isatty()`(36-40行)でTTY実行のみに限定。パイプ・自動スクリプト経由の非対話実行は`sys.exit(1)`で拒否される。
- `approve`/`reject`はさらに`input()`による対話確認(74行・89行)で、きむら博士本人による確認である旨を明示的に問い合わせてから実行する二重の防御。
- `submit`/`status`/`pending`はTTY制限なし(読み取り・提出のみで、承認権限を持たないコマンドのため妥当と判断できる)。

## TEST_CLI_VERIFY_001との関係

既報の通り、`TEST_CLI_VERIFY_001`というIDは`MOCKA_TODO_ACTIVE.json`・`decision_ledger.jsonl`・`events.db`のいずれにも存在しない。本ファイルはこのIDへの参照を一切含んでおらず(grep確認済み)、**本レポート作成にあたってもこのIDを復活・新規登録していない。**

## 判定

新規承認経路としての登録・TEST_CLI_VERIFY_001の復活はいずれも行っていない。本ファイルは既存Human Gate機構①への設計上妥当な入口追加に見えるが、Decision Record・TODOともに正式登録がないままのため、`docs/governance/`配下の監査文書としてのみ現状を記録した。制度化(TODOとして登録するか、Decision Unit化するか)はきむら博士の判断待ち。

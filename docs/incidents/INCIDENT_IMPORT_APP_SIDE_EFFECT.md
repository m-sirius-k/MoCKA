# INCIDENT_IMPORT_APP_SIDE_EFFECT

Status: Investigated（Phase5.x-A/B/B2完了、Phase5.x-C設計案あり、コード変更は未実施）
Priority: Medium
Date detected: 2026-06-22
Date investigated: 2026-06-22
Date re-audited (B2): 2026-06-22

**人間ゲート承認ポイント: 本文書のRemediation Design(Phase5.x-C)に基づく
app.py修正は、人間の承認を得てから実施する。本文書作成時点では
app.pyへのコード変更は一切行っていない。**

## 1. 発生日・検出方法

2026-06-22。Phase5 Step1(Time API v0)の動作確認のため、検証目的で
`import app`をPythonインタプリタ上で実行したところ、コンソールに
`[AUTO-AUDIT] 50件seal完了`等の出力が現れ、調査の結果ローカルgit
commitが2件(`c90fe6c87` "AUTO_SEAL_50EVT" → `579ddb54b` "anchor:
re-seal after c90fe6c")作成されていたことを確認した。

## 2. 対象箇所（Phase5.x-B2 AST解析により6箇所に確定）

**注: 当初Phase5.x-A/Bのgrep調査では4箇所のみ検出していたが、
Phase5.x-B2でast(抽象構文木)による全文解析を実施した結果、
新たに2箇所(#5, #6)を追加発見した。**調査方法は本文書「9. Phase5.x-B2
追加監査（網羅性の証明）」を参照。

`app.py`内の以下6箇所(いずれも`if __name__ == "__main__":`ガード
[app.py:4052]の外側、モジュールレベル)。

| # | 行 | 内容 | 発火タイミング | 検出 |
|---|---|---|---|---|
| 1 | `app.py:136-137` | `_auto_thread = threading.Thread(target=auto_process_loop, daemon=True); _auto_thread.start()` | import直後（スレッド内で5秒sleep後にループ開始） | Phase5.x-B (grep) |
| 2 | `app.py:2111-2112` | `_audit_thread = _lt.Thread(target=auto_audit_loop, daemon=True); _audit_thread.start()` | import直後（スレッド内で即座に`_auto_approve_prevention()`実行、その後ループ） | Phase5.x-B (grep) |
| 3 | `app.py:2695` | `_threading.Timer(10, _start_overdue_loop).start()` | import後10秒 | Phase5.x-B (grep) |
| 4 | `app.py:2823-2824` | `_gt = _threading.Thread(target=_guidelines_loop, daemon=True); _gt.start()` | import後300秒（スレッド内でsleep(300)後に初回実行） | Phase5.x-B (grep) |
| 5 | `app.py:140-148` | `try`節で`interface/essence_auto_updater.py`を`importlib`で動的import後、`_eau.start_essence_auto_loop()`を呼出 | import直後。**現状は`NameError: name 'Path' is not defined`で例外発生・`except`で握り潰されているため実際には不発**だが、try節への到達自体が副作用試行である | **Phase5.x-B2 (ast、新規)** |
| 6 | `app.py:2587-2593` | `try`節で`interface.cross_audit`を import後、モジュールレベルで`init_audit_db()`を呼出 | import直後。SQLite接続+`CREATE TABLE IF NOT EXISTS`を即時実行(DB書込) | **Phase5.x-B2 (ast、新規)** |

## 3. 再現手順

```python
import app  # これだけで以下が発火する
```

1. `import app`実行時点で上記6箇所の処理が(モジュール本体の実行順に)発火する。
2. (#5) モジュール読込が140行目に到達した時点で、`essence_auto_updater.py`
   を動的importし`start_essence_auto_loop()`を呼ぼうとするが、現状の
   バグ(`Path`未importによる`NameError`)により例外発生、`except`節で
   `[ESSENCE_AUTO] 起動失敗`が出力されるのみで実害は無い。**ただしこの
   バグが将来修正された場合、ここでさらに別のbackground thread
   (`essence_auto_loop`、5分/10分/1分/2分/1時間間隔でDB/file書込)が
   起動する状態になる。**
3. (#1) `auto_process_loop()`は5秒後、`data/storage/outbox/PILS/`に
   `.json`ファイルが存在すれば、`CALIBER_SERVER`(`http://localhost:5679`)
   へHTTP POSTを送信する。
4. (#6) モジュール読込が2587行目に到達した時点で、`init_audit_db()`が
   即座に実行され、`data/`配下のaudit用SQLite DBに対し
   `CREATE TABLE IF NOT EXISTS`を実行する(既存テーブルがあれば実質的な
   変更は無いが、DBファイルが存在しない場合は新規作成される)。
5. (#2) `auto_audit_loop()`が起動直後に`_auto_approve_prevention()`を
   実行し、ループ1周目でevents.db件数差分を確認。差分が+50件以上
   あれば即座に`scripts/ledger/anchor_update.py AUTO_SEAL_50EVT`を
   `subprocess.run()`で実行し、git add/commitが発火する。**さらに
   `_auto_approve_prevention()`が呼ぶ`_load_pqueue()`はapp.py:2176で
   定義されるが、このThreadは2111-2112行目(定義より前)でstart()される
   ため、スレッドの実行タイミングによっては`NameError: name
   '_load_pqueue' is not defined`が発生する競合状態が確認された
   (実測ログで確認済み)。**
6. (#3) `_start_overdue_loop()`は10秒後に`_auto_incident_overdue()`を
   実行し、締切超過TODOがあれば`get_buffer().push()`経由でevents.db
   へINCIDENT書込を行う。以後3600秒ごとに繰り返す。
7. (#4) `_guidelines_loop()`は300秒後に`_run_guidelines_engine()`を
   実行する。以後3600秒ごとに繰り返す。

## 4. 影響範囲（Phase5.x-B + B2 完全棚卸し）

`import app`によって発火する副作用は確認できた範囲で以下の5種類。

- **git操作**: AUTO_SEAL経由でのgit add/commit(ローカルのみ、push無し)。
- **DB書込**: events.db(`mocka_events.db`等)への書込(`get_buffer().push()`、
  AUTO_SEAL内のseal処理等)に加え、**audit用SQLite DBへの
  `CREATE TABLE IF NOT EXISTS`実行(`init_audit_db()`、Phase5.x-B2新規発見)**。
- **HTTP通信(localhost限定)**: `CALIBER_SERVER`(localhost:5679)への
  POSTリクエスト(PILSキューにファイルが存在する場合のみ)。
- **外部プロセス起動**: `subprocess.run(["python", anchor_update.py, ...])`
  によるPythonサブプロセス起動。
- **二段階スレッド起動の試行(現状は例外で不発)**: `essence_auto_updater.py`
  の動的import+`start_essence_auto_loop()`呼出(Phase5.x-B2新規発見)。
  現在はバグにより例外処理に落ちて不発だが、これは「現状安全」を
  意味するのみで「設計として安全」を意味しない。バグ修正時に新たな
  background threadが発火する状態になっている。

いずれも外部(localhost以外)への通信は確認されていない。ただし
import操作だけでこれらが発火する設計自体が、Phase5で確立した
「import ≠ 実行」という制度的境界(`docs/governance/`系文書群が
前提とする構造)と整合しない。

## 5. 根本原因候補

`app.py`は元々スクリプトとして`python app.py`で直接起動されることを
前提に書かれており、`if __name__ == "__main__":`ガード(4052行目)は
存在するものの、バックグラウンドループの起動コード自体がガードの
外側(モジュールレベル)に配置されている。これは歴史的な実装パターン
(Flask appの初期化と運用ループの起動を分離せず、ファイル読込時点で
全て起動させる)に起因すると考えられる。

Phase5でTime API(`phi_os/api/time_api.py`)がFlask Blueprintとして
`app.py`からimportされる構造になったことで、検証・テストのために
`app.py`をimportする操作が増え、本来"起動"を意図しない場面でも
この副作用が発火するリスクが顕在化した。

## 6. 修正候補（Phase5.x-C Remediation Design・設計案のみ）

以下は設計案であり、現物のapp.py全文を踏まえた完全ファイル提示を
人間ゲート承認時に行う。本文書の段階ではコード変更を行わない。

### 方針

6箇所すべての副作用発生源(`.start()`呼び出し4箇所、`start_essence_auto_loop()`
呼出1箇所、`init_audit_db()`呼出1箇所)をモジュールレベルから除去し、
明示的な初期化関数(例: `start_background_loops()`)に集約する。
この関数は`if __name__ == "__main__":`ブロック内でのみ呼び出す。

```python
# 現状(概念図)
_auto_thread = threading.Thread(target=auto_process_loop, daemon=True)
_auto_thread.start()                              # module-level (#1)
...
try:
    ...
    _eau.start_essence_auto_loop()                # module-level (#5)
except Exception as _eau_err:
    print(f"[ESSENCE_AUTO] 起動失敗: {_eau_err}")
...
_audit_thread = _lt.Thread(target=auto_audit_loop, daemon=True)
_audit_thread.start()                             # module-level (#2)
...
try:
    from interface.cross_audit import (...)
    init_audit_db()                               # module-level (#6)
    ...
except Exception ...
...
_threading.Timer(10, _start_overdue_loop).start() # module-level (#3)
...
_gt = _threading.Thread(target=_guidelines_loop, daemon=True)
_gt.start()                                       # module-level (#4)

# 修正後(概念図)
def start_background_loops():
    threading.Thread(target=auto_process_loop, daemon=True).start()
    try:
        _eau.start_essence_auto_loop()
    except Exception as _eau_err:
        print(f"[ESSENCE_AUTO] 起動失敗: {_eau_err}")
    init_audit_db()
    _lt.Thread(target=auto_audit_loop, daemon=True).start()
    _threading.Timer(10, _start_overdue_loop).start()
    _threading.Thread(target=_guidelines_loop, daemon=True).start()

if __name__ == "__main__":
    start_background_loops()
    app.run(host="127.0.0.1", port=5000, debug=False)
```

- `init_audit_db()`の呼出元(`interface.cross_audit`のimport自体)は
  Flask Blueprintのルート定義(`@app.route("/cross_audit/task", ...)`等)
  と同じtry節内に存在するため、importとルート登録は維持しつつ
  `init_audit_db()`の呼出のみを`start_background_loops()`へ移すか、
  あるいはルート関数内で遅延初期化(初回アクセス時にinit)する方式も
  検討の余地がある。どちらを採るかは人間ゲート承認時にapp.py全文を
  踏まえて確定する。
- `auto_audit_loop`内の`_load_pqueue()`未定義競合(3.再現手順 #5参照)も、
  `start_background_loops()`を`__main__`ブロック内かつモジュール全体の
  読込完了後に呼ぶことで自然に解消される(関数定義はすべてモジュール
  読込時に完了しているため)。

### リスク評価

- **変更箇所**: 6箇所の副作用発生源(4箇所の`.start()`呼び出し+
  `start_essence_auto_loop()`呼出+`init_audit_db()`呼出)の位置移動のみ。
  各対象関数自体のロジックは変更しない。
- **影響範囲**: `python app.py`で直接起動する既存の運用(MoCKA-START.bat
  経由の起動)には影響しない(`__main__`ブロックは従来通り実行される)。
  影響を受けるのは「`import app`のみを行い`__main__`を経由しない」
  操作(検証・テスト目的のimport)のみであり、これらは現状の
  副作用が消えることが意図した修正効果である。**副次効果として、
  `_load_pqueue()`未定義の競合状態(3.再現手順 #5)も解消される。**
- **ロールバック方法**: 6箇所の呼出を元のモジュールレベル位置に
  戻すのみ。関数定義自体は削除せず残しても良いため、ロールバックは
  1コミットのrevertで完了する。
- **未確定事項**: 9.のAST解析により、Thread/Timer/subprocess/sqlite3.connect/
  schedule/apscheduler/asyncio/atexit等の既知パターンについては
  モジュールレベルでの追加発見は無いことを確認した。ただし、
  (a) 個別モジュール(`interface/essence_auto_updater.py`,
  `interface/cross_audit.py`等)の内部実装まではAST解析の対象外
  であり、それらのimport自体が及ぼす副作用(モジュール自身のトップ
  レベルコード)は本調査の範囲に含めていない、(b) 動的import
  (`importlib`)で読み込まれるモジュールも、読み込まれた時点で
  そのモジュール自身のトップレベルコードが実行される。これらは
  Phase5.x-B3として必要であれば追加調査する。

## 7. 人間ゲート承認に必要な情報（まとめ）

- 修正箇所: `app.py:136-137`, `app.py:140-148`, `app.py:2111-2112`, `app.py:2587-2593`, `app.py:2695`, `app.py:2823-2824`の6箇所
- 変更行数: 削除6箇所(各1-数行)+新規関数定義(`start_background_loops()`、約10行)+`__main__`ブロックへの1行追加
- 影響範囲: `import app`のみの操作(検証・テスト)からは副作用が消える。`python app.py`での通常起動・MoCKA-START.bat経由の起動には影響なし。副次効果として`_load_pqueue()`競合状態も解消
- ロールバック方法: 1コミットのrevert

## 8. 完了条件（本文書段階）

- [x] 発生日・検出方法の記録
- [x] 対象箇所の特定(6箇所、grep+ast解析による完全棚卸し)
- [x] 再現手順の記録
- [x] 影響範囲の分析(git操作/DB書込/HTTP通信/外部プロセス起動/二段階スレッド起動試行)
- [x] 根本原因候補の記録
- [x] 修正候補(設計案)の記録
- [x] リスク評価・ロールバック方法の記録
- [x] 追加全文走査(Phase5.x-B2、ast解析による網羅性証明)実施済み
- [ ] 人間ゲート承認（未実施）
- [ ] app.py実装修正（未実施、承認後に着手）

## 9. Phase5.x-B2 追加監査（網羅性の証明）

Phase5.x-Bのgrep調査は「`.start()`を含む行」のテキスト検索に依存して
おり、テキストパターンに一致しない副作用(関数呼出による間接発火、
動的importの結果等)を見逃すリスクがあった。Phase5.x-B2では
Python標準の`ast`モジュールを用いて`app.py`を構文解析し、以下の
観点で「モジュールレベルで実際に実行される文」を機械的に網羅した。

### 調査方法

1. **モジュールトップレベル文の全数列挙**: `ast.parse(app.py)`の
   `tree.body`(モジュール直下の文。`FunctionDef`の中身は呼出時のみ
   実行されるため除外)を全件取得し、`Assign`/`Expr`/`Try`/`If`の
   各文に含まれる関数呼出を抽出した(全249文、`Counter`で種別を確認)。
2. **危険パターンとの照合**: 抽出した呼出名を
   `Thread`/`Timer`/`subprocess`/`Popen`/`system`/`requests`/`httpx`/
   `sqlite3`/`connect`/`run`/`start`/`post`/`get`/`commit`等の
   キーワードと照合した。
3. **デコレータの確認**: 全関数の`decorator_list`を確認し、
   `@app.route`/`@<bp>.route`以外の非標準デコレータが存在しないことを
   確認した(0件)。
4. **デフォルト引数の確認**: 全関数の引数デフォルト値(def時に評価
   される式)に危険な呼出が含まれないことを確認した(0件)。
5. **モジュールレベルclass本体の確認**: モジュール直下のクラス定義の
   クラス本体(クラス変数等、定義時に評価される)に危険な呼出が
   含まれないことを確認した(0件)。
6. **キーワード全文検索**: `asyncio`/`apscheduler`/`BackgroundScheduler`/
   `schedule.every`/`atexit`の5キーワードについて、ファイル全体
   (関数内も含む)に1件も出現しないことを確認した。
7. **With/For/While文の確認**: モジュールトップレベルに`with`/`for`/
   `while`文が存在しないことを確認した(0件)。

### 結果

- 上記1〜2の手法により、既知4件(#1〜#4)に加えて新規2件(#5, #6)を
  発見した(本文書「2. 対象箇所」参照)。
- 3〜7の手法では新規発見は無かった(0件)。
- したがって、**「Thread/Timer起動・subprocess起動・sqlite3接続・
  HTTP通信・スケジューラ・asyncio task・デコレータ経由の隠れた呼出・
  デフォルト引数経由の隠れた呼出」という主要カテゴリについては、
  モジュールトップレベルにおける副作用源は本文書記載の6箇所で
  全数であることをコード解析によって示した。**
- ただし「6. 修正候補」の「未確定事項」に記載の通り、個別モジュール
  自身の内部トップレベルコード(`interface/essence_auto_updater.py`等)
  までは踏み込んでいない。これは「app.pyのモジュールレベル文」を
  対象とする本調査のスコープ外であり、必要であればPhase5.x-B3として
  別途実施する。

## 10. Import Safety Rule（提案）

本インシデントを踏まえ、`docs/governance/import_safety_rule_v1.md`
として制度文書を新設した。今後のMoCKAコアファイルの実装・レビューに
おいて、本インシデントと同種の問題を未然に防ぐための短い規約である。

## 関連文書

- `docs/releases/PHASE5_STEP3_SEAL.md`(Incident Ledger正式化要約の正本記録元)
- `docs/governance/import_safety_rule_v1.md`(本インシデントを踏まえた制度規約)
- mocka_write_event記録: event_id `E20260622_95297609948c0`(インシデント初回記録)

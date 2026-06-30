# INCIDENT_IMPORT_APP_SIDE_EFFECT

Status: Implementation完了（6箇所全件対応済み。import app単独実行で副作用ゼロを実機確認済み。回帰テスト104件PASS。Incident Closureは運用観察後）
Priority: Medium
Date detected: 2026-06-22
Date investigated: 2026-06-22
Date re-audited (B2): 2026-06-22
Date human gate review (R01): 2026-06-23

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

## 11. Human Gate Review R01判定（2026-06-23）

TODO_358(Phase5.x-D Human Gate Review)は締切超過によりOVERDUE_INCIDENT化
されたが、Human Gate Review自体は本節で実施した。

### R01最終判定: 条件付き承認

実装承認は出さない。ただし設計フェーズへの差し戻しでもない。Human Gate
Review通過条件として「6箇所のRemediation Matrix確定」を新たに設定する。

```
Phase5.x-C 設計
  |
Human Gate Review (R01 = 条件付き承認、本節)
  |  <- 現在位置
Remediation Matrix確定
  |
Core System File Change Approval
  |
実装
```

### Remediation Matrix

| # | 対象 | 副作用種別 | 修正方式 |
|---|---|---|---|
| 1 | auto_process_loop | Thread+HTTP | main境界(start_background_loops) |
| 2 | essence_auto_updater | 動的import+Thread | 要判断(Group B) |
| 3 | auto_audit_loop | Thread+Git | main境界(start_background_loops) |
| 4 | init_audit_db | DB書込 | 初期化境界(要判断、Group B) |
| 5 | overdue_loop | Thread+DB | main境界(start_background_loops) |
| 6 | guidelines_loop | Thread | main境界(start_background_loops) |

### Group A（main起動後に開始、レビュー負荷低い）

- #1 auto_process_loop
- #3 auto_audit_loop（既知インシデント原因。最優先で境界管理すべき対象）
- #5 overdue_loop
- #6 guidelines_loop

これら4件は`start_background_loops()`への移管で整合的と判断。単純な
`.start()`呼び出しの位置移動で完結する。

### Group B（制度判断が必要、単純な.start()移設では解決しない）

- **#2 essence_auto_updater**: **状態: Decision Ready（necessity調査完了）**

  正しい問いは「essence_auto_updater機能は必要か」ではなく「app.py内の
  essence_auto_updater起動経路は必要か」である。両者は別物であり、調査の
  結果は以下の通り。

  - `MoCKA-START.bat:40`にて、`essence_auto_updater.py`は`start /B`で
    独立プロセスとして起動される正式運用経路が既に存在する
    （`python -X utf8 interface\essence_auto_updater.py`、自身の
    `if __name__=="__main__"`ブロックを実行）。
  - `MoCKA-START.bat:12`にて、起動前に同名プロセス（`essence_auto_updater.py`
    含む）をkillする処理が実装されており、単発の実験コードではなく
    運用前提の起動管理が設計されている。
  - `app.py:140-148`は、同じ`essence_auto_updater.py`を`importlib`で
    動的に再import後`start_essence_auto_loop()`を呼ぶ二段目の起動試行で
    あり、現状`NameError`で不発だが、バグが修正されれば
    `MoCKA-START.bat`経路と責務が重複する二重起動が発生する状態だった。

  **結論候補**: 機能（essence更新・REDUCING監視・Caliber死活監視・
  ping_generator強制実行）自体は必要であり`MoCKA-START.bat`経路で
  既に運用されている。一方`app.py`内の起動経路（#2）は正式運用経路では
  なく責務重複するため**廃止候補**と判定する（機能廃止ではなく
  冗長経路廃止）。まだ削除コミットは行っていないため、本判定は
  「削除決定」ではなく「**削除承認候補**」として記録する。
  Core System File Change Approval時に正式な削除実装の承認を得る。
- **#4 init_audit_db()**: **状態: Necessity Confirmed / Placement Review中**

  necessity調査結果:
  - `init_audit_db()`本体(`interface/cross_audit.py:42-82`)は
    `PRAGMA journal_mode=WAL`設定後、`CREATE TABLE IF NOT EXISTS`を
    3テーブル(`audit_tasks`/`audit_results`/`audit_discrepancies`)実行
    するのみ。`INSERT`/`UPDATE`/`DELETE`は含まない。
  - 冪等性: 全て`IF NOT EXISTS`句のため何度呼んでも安全。
  - 呼び出し元: 正本ロジックは`interface/cross_audit.py`にあり、
    呼び出しは3箇所確認された。(a)ルートの`cross_audit.py:362-363`
    (`if __name__=="__main__"`ブロック内、旧版/単独検証用と推定)、
    (b)同ファイル320行目(`FLASK_ENDPOINTS`という文字列定数内、
    app.pyへの貼付用テンプレートコード片であり実行コードではない)、
    (c)`app.py:2587-2592`(モジュールレベル、本インシデント対象)。
  - **TODO_359との構造差異**: TODO_359は「機能は必要、app.py経路は
    不要」(別の正式経路`MoCKA-START.bat`が既存)だったが、TODO_360は
    「機能は必要、app.py経路も必要、ただし配置(import時実行)が悪い」
    という**配置問題**であり、`app.py`自身が唯一の実運用呼び出し元。
  - リスク性質: Import Safety Rule上はimport時DBアクセスとして
    是正対象だが、内容はスキーマ初期化のみであり、AUTO_SEALやGit操作
    のような高リスク副作用とは性質が異なる。

  **Placement Review（配置先の比較）**:

  | 案 | 内容 | 評価 |
  |---|---|---|
  | A. `initialize_runtime()` | init_audit_db()/registry load/config validation/startup checksを集約。start_background_loops()とは責務分離 | 第一候補。拡張性が高く、将来gunicorn/uvicorn/テストハーネス/CLI/Relay連携等の別起動経路が増えても再発しない |
  | B. `bootstrap()` | 設定読込・認証・依存確認・環境検証等を担う想定 | DB初期化が混ざると責務が膨らむ懸念あり |
  | C. `if __name__=="__main__"`直接 | 最も単純 | 将来別起動経路が増えた時に再び同種の問題が発生しうる |

  **第一候補: `initialize_runtime()`境界**

  ```
  Application Start
    |
    +-- initialize_runtime()
    |     +-- init_audit_db()
    |     +-- registry load
    |     +-- config validation
    |     +-- startup checks
    |
    +-- start_background_loops()
          +-- auto_process_loop
          +-- auto_audit_loop
          +-- overdue_loop
          +-- guidelines_loop
  ```

  必要性は確認済み（necessity=必要）。

  **Placement Decision確定: `initialize_runtime()`**

  判定基準: `bootstrap()`の責務は環境準備/設定読込/依存性確認/起動前検証。
  `initialize_runtime()`の責務はDB初期化/Registry初期化/Runtime状態生成/
  起動時一回処理。`init_audit_db()`は明らかに後者寄りである。
  `__main__`直接案は将来の起動経路増加（gunicorn/uvicorn/テストハーネス/
  CLI/Relay連携等）に弱いため優先度が低いとして除外し、実質
  `initialize_runtime()` vs `bootstrap()`の二択とした。

  MoCKA長期構造（PHI-OS → Runtime Layer → Relay → Orchestra への
  責務分離方向）との整合性も踏まえ、DBスキーマ生成はRuntime
  Initializationの責務であり、Bootstrapの責務ではないと判断した。

  理由:
  - import境界から除外できる
  - `start_background_loops()`と責務分離できる
  - DB初期化はRuntime準備に属する
  - 将来PHI-OS構造とも整合する

  **TODO_360: クローズ可能（Placement Decision確定済み）**。
  具体的な実装行（`initialize_runtime()`関数の正確な記述位置・
  呼出順序）はCore System File Change Approval時にapp.py全文を
  踏まえて確定する。

### Human Gate Review通過条件（更新）

- [x] #2 essence_auto_updaterの最終運用境界 → Decision Ready
      （app.py内起動経路は冗長経路廃止候補、MoCKA-START.bat経路が正式運用経路）
- [x] #4 init_audit_db()の最終運用境界 → Placement Decision確定
      （`initialize_runtime()`境界）
- [x] Group A/B全件の分類・審査が完了

**Human Gate Review通過条件: 全項目完了。次回審査はCore System File
Change Approvalの発行判断のみとなる。**

Remediation Matrix最終版:

| # | 対象 | 修正方式（確定） |
|---|---|---|
| 1 | auto_process_loop | `start_background_loops()`へ移管 |
| 2 | essence_auto_updater | app.py内起動経路を削除（廃止承認候補。機能は`MoCKA-START.bat`経路で継続） |
| 3 | auto_audit_loop | `start_background_loops()`へ移管 |
| 4 | init_audit_db | `initialize_runtime()`へ移管 |
| 5 | overdue_loop | `start_background_loops()`へ移管 |
| 6 | guidelines_loop | `start_background_loops()`へ移管 |

```
Application Start
  |
  +-- initialize_runtime()
  |     +-- init_audit_db()        (#4)
  |
  +-- start_background_loops()
        +-- auto_process_loop      (#1)
        +-- auto_audit_loop        (#3)
        +-- overdue_loop           (#5)
        +-- guidelines_loop        (#6)

  (#2 essence_auto_updater起動経路は削除。機能はMoCKA-START.bat側で継続)
```

## 12. Core System File Change Approval（2026-06-23）

Human Gate Review完了、Remediation Matrix確定、Runtime Boundary v1確定、
Change Plan v1完成（`docs/incidents/CHANGE_PLAN_IMPORT_APP_SIDE_EFFECT_v1.md`）
を踏まえ、Core System File Change Approvalを発行する。

### 判定: 条件付き承認

実装はChange Plan v1の範囲を超えず、以下3条件を満たすことを承認の前提とする。

**条件1: スコープ固定**
実装はChange Plan v1記載の範囲を超えない。`#1`/`#3`/`#4`/`#5`/`#6`の移設、
`#2`の削除以外の機能変更を混ぜない。

**条件2: Boundary固定**
`initialize_runtime()`と`start_background_loops()`の責務を
`docs/governance/runtime_boundary_v1.md`から実装中に拡張しない。

**条件3: 実装後の再検証**
実装後に再度Import Safety検証（`ast`解析または実機確認）を行い、
`import app`単独実行でThread起動/DB更新/HTTP通信/Git操作が発生しない
ことを確認する。

### 残存する不確実性（承認の阻害要因にはならない）

`essence_auto_updater`の`MoCKA-START.bat`側における実運用成功状態
（「起動コードがある」と「正常運用されている」は別）は未検証のまま
残っている。これは変更理由の妥当性の問題ではなく運用確認の領域で
あり、本承認の判断材料には含めない。

### 進行フロー（更新）

```
Phase5.x-C 設計
  |
Human Gate Review (R01 = 条件付き承認)
  |
Remediation Matrix確定
  |
Runtime Boundary v1確定
  |
Change Plan v1完成
  |
Core System File Change Approval (条件付き承認、本節) <- 現在位置
  |
Implementation
  |
Regression Test
  |
Incident Closure
```

## 13. Implementation Readiness Check（2026-06-23）

Core System File Change Approval（条件付き承認）後、実装着手前の最終
ゲートとして3項目を確認した。実装承認(Approval)と実装実行
(Implementation着手)は別の判断であることを前提とする。

### Check A: 変更対象固定

`docs/incidents/CHANGE_PLAN_IMPORT_APP_SIDE_EFFECT_v1.md`記載の変更対象が
`#1`/`#2`/`#3`/`#4`/`#5`/`#6`の6件のみであることを確認した。実装時に
これ以外の「ついで修正」を混ぜることは禁止する。

結果: OK

### Check B: ロールバック実行可能性

`git status --short app.py`および`git diff --stat app.py`を実行し、
`app.py`に未コミットの差分が無いクリーンな状態であることを確認した
（2026-06-23時点）。これにより実装を1コミットにまとめ、1ロールバック
（revert）で確実に戻せる前提条件が整っている。

なお、リポジトリ全体には`app.py`とは無関係な未コミット差分（自動同期
ログ・state.json等、PlanningCaliber配下含む）が存在するが、これらは
本変更の対象外であり、ロールバック判定には影響しない。

結果: OK（app.pyはクリーン、1コミット/1ロールバックが成立する）

### Check C: 検証項目の事前固定

実装完了後に確認する検証項目を、実装着手前の時点で以下に固定する。

`import app`を単独実行した場合に、以下4点が発生しないことを確認する。

1. Thread起動なし
2. Git操作なし
3. HTTP通信なし
4. 想定外のDB更新なし（`initialize_runtime()`内の冪等なスキーマ初期化は
   想定内とする）

これは`CHANGE_PLAN_IMPORT_APP_SIDE_EFFECT_v1.md`の完了条件チェックリスト
と整合する。

結果: OK（検証項目は実装前に固定済み）

### 総合判定

Check A/B/C いずれも結果は良好。実装を止める理由は現時点では見当たらない。

## 14. Implementation（2026-06-23）

Change Plan v1（`docs/incidents/CHANGE_PLAN_IMPORT_APP_SIDE_EFFECT_v1.md`）の
範囲に限定して`app.py`を実装した。詳細はChange Plan v1の完了条件チェックリスト
を参照。

### 実機検証結果

- `python -c "import app"`単独実行: `threading.active_count() == 1`
  （MainThreadのみ）、daemon thread起動なし、`[ESSENCE_AUTO]`出力消失、
  AUTO-AUDIT/Git操作出力なし。
- `git status --short app.py`: import実行による新規commit発生なし。
- `phi_os/tests/`: 104件PASS（既存と同数、回帰なし）。

Core System File Change Approvalの条件1（スコープ固定）・条件2
（Boundary固定）・条件3（実装後の再検証）を全て満たした。

### 進行フロー（最終）

```
Phase5.x-C設計 -> Human Gate Review -> Remediation Matrix確定
  -> Runtime Boundary v1確定 -> Change Plan v1完成
  -> Core System File Change Approval -> Implementation Readiness Check
  -> Implementation（本節、完了）
  -> Regression Test（実施済み、104件PASS）
  -> Incident Closure（実運用での観察期間を経てクローズ）
```

## 15. Incident Closure完了（2026-06-30）

Implementation完了（2026-06-23）から5日以上の運用観察期間を経て、新たな
インシデント報告は無かった。実機検証（`active_threads=1`、
`[ESSENCE_AUTO]`出力消失、`import app`単独実行でのgit操作なし）・
`phi_os/tests`104件PASS・Core System File Change Approval条件1〜3
（スコープ固定/Boundary固定/実装後再検証）を満たした状態を維持して
いることを確認した。これ以上の観察延長は不要と判断し、本インシデントは
クローズとする。

```
Implementation（2026-06-23）
  |
Regression Test（実施済み、104件PASS）
  |
運用観察期間（2026-06-23〜2026-06-30、新規インシデント報告なし）
  |
Incident Closure（本節、完了）
```

決定者: きむら博士（2026-06-30）

## 関連文書

- `docs/releases/PHASE5_STEP3_SEAL.md`(Incident Ledger正式化要約の正本記録元)
- `docs/governance/import_safety_rule_v1.md`(本インシデントを踏まえた制度規約)
- mocka_write_event記録: event_id `E20260622_95297609948c0`(インシデント初回記録)

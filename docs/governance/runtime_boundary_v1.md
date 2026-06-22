# Runtime Boundary v1

Status: PROPOSED（INCIDENT_IMPORT_APP_SIDE_EFFECT Phase5.x-D審査を踏まえた制度規約案）
Date: 2026-06-23

## 背景

`docs/incidents/INCIDENT_IMPORT_APP_SIDE_EFFECT.md`のHuman Gate Reviewにおいて、
`app.py`内モジュールレベルの副作用源6箇所を`initialize_runtime()`と
`start_background_loops()`という2つの境界関数に集約する方針が確定した。
しかし両関数自体の責務がまだ「設計上の概念」のままであり、責務定義を
制度文書化しないまま実装に進むと、将来「とりあえずここに入れる箱」に
なる危険がある。本文書はその危険を防ぐための短い契約である。

## 呼び出し順序

```
Application Start (__main__)
  |
  +-- initialize_runtime()       # 1. 起動準備（一度だけ・同期的に完了させる）
  |
  +-- start_background_loops()   # 2. 継続稼働ループの起動（initialize_runtime()完了後）
  |
  +-- app.run(...)
```

`start_background_loops()`は`initialize_runtime()`が正常終了したことを
前提に呼び出す。`initialize_runtime()`が例外を投げた場合、
`start_background_loops()`は呼び出してはならない（起動準備が未完了の
状態でバックグラウンドループだけが動く状態を防ぐ）。

## initialize_runtime() の責務契約

### 許可

- DB初期化（テーブルスキーマ作成、`CREATE TABLE IF NOT EXISTS`等の
  冪等な初期化処理）
- Registry / 設定ファイルの読込
- Config検証（必須環境変数・必須ファイルの存在確認）
- 起動時に一度だけ実行すればよい同期処理

### 禁止

- Thread/Timerの起動（`start_background_loops()`の責務）
- 継続的なループ処理
- Git操作（add/commit等）
- 外部プロセス起動（subprocess）
- 外部通信（HTTP等）。ヘルスチェック等の単発確認は将来検討事項とし、
  本v1では含めない

### 該当する移管対象

- `init_audit_db()`（`app.py:2587-2593`、Phase5.x-D対象 #4）

## start_background_loops() の責務契約

### 許可

- daemon Threadの起動（`.start()`呼び出し）
- `threading.Timer`の起動
- 起動した各ループ関数自体の内部処理（git操作・DB書込・HTTP通信を
  含む）は、ループ関数本体の責務として許可する。`start_background_loops()`
  自体が直接git操作・DB書込・HTTP通信を行うことは禁止する
  （あくまでThread/Timerの起動窓口に限定する）

### 禁止

- DBスキーマの作成・変更（`initialize_runtime()`の責務）
- `start_background_loops()`関数自体からの直接的なGit操作・HTTP通信・
  subprocess起動（ループ関数に委譲すること）

### 該当する移管対象

- `auto_process_loop`（`app.py:136-137`、Phase5.x-D対象 #1）
- `auto_audit_loop`（`app.py:2111-2112`、Phase5.x-D対象 #3）
- `_start_overdue_loop`（`app.py:2695`、Phase5.x-D対象 #5）
- `_guidelines_loop`（`app.py:2823-2824`、Phase5.x-D対象 #6）

## 適用対象外（廃止候補）

- `essence_auto_updater`の`app.py`内起動経路（`app.py:140-148`、
  Phase5.x-D対象 #2）は、`MoCKA-START.bat`経由の独立プロセス起動と
  責務重複するため、いずれの境界関数にも移管しない。app.py内の
  当該コードは削除承認候補とする（詳細は
  `docs/incidents/INCIDENT_IMPORT_APP_SIDE_EFFECT.md`参照）。

## 起動順序・依存関係・例外処理の最低基準

- `initialize_runtime()`は同期的に完了させ、完了前に
  `start_background_loops()`を呼び出してはならない。
- `initialize_runtime()`内の各初期化処理が例外を投げた場合、
  例外を握り潰さず呼び出し元（`__main__`ブロック）まで伝播させる
  （起動失敗を握り潰すと、後続のCore System File Change Approval時の
  リスク評価が無効になるため）。
- `start_background_loops()`内の各Thread/Timer起動については、
  個別のループ関数内で例外を捕捉し、daemon thread自体をクラッシュ
  させない設計を維持する（既存実装の`try/except`方針を踏襲する）。
- 再起動（`start_background_loops()`の再呼び出し）については本v1では
  扱わない。現状の運用は単一プロセスの起動時に一度だけ呼ぶことを
  前提とする。

## 検証方法

`docs/governance/import_safety_rule_v1.md`と同様、`ast`モジュールに
よるモジュールトップレベル文の全数列挙を用いて、`initialize_runtime()`
および`start_background_loops()`の呼び出しが`if __name__ == "__main__":`
ブロック内に限定されていることを実装後に確認する。

## 関連文書

- `docs/governance/import_safety_rule_v1.md`
- `docs/incidents/INCIDENT_IMPORT_APP_SIDE_EFFECT.md`

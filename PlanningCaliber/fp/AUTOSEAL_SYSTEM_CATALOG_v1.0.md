# AUTOSEAL_SYSTEM_CATALOG_v1.0

対象: AUTO_SEAL関連3経路(AUTO_SEAL_50EVT / MANUAL_SEAL / auto_audit_loop)の
現行コード上の振る舞いのカタログ化(read-only trace + documentation)。

本カタログは全項目、現在のコードが実際にどう振る舞っているかの事実列挙のみで
構成する。既存調査結果(AUTOSEAL_Observation_Record_2026-07-01.md、
AUTOSEAL_PATHMAP_v1.0.md)からの引用を優先し、新規に確認した箇所はその旨を注記する。

---

## 1 AUTO_SEAL_50EVT

- トリガー条件: `app.py` `auto_audit_loop()`内、`count - _last_event_count[0] >= 50`
  かつ `not _seal_running[0]`(2076-2077行目、AUTOSEAL_PATHMAP_v1.0.md確認済み)
- 呼び出し元: `app.py:2085` `subprocess.run(["python", str(seal_script), "AUTO_SEAL_50EVT"], cwd=str(ROOT_DIR), timeout=30)`
- 実行主体: `scripts/ledger/anchor_update.py`(subprocess経由で起動)
- 書き込み範囲: `governance/mocka_git_safe_commit.py`の`is_core_system_file()`による
  除外を除いた全ファイルが`git add -A`の対象となる
  - `mocka_mcp_server.py`はこの除外対象に含まれていない(`CORE_SYSTEM_DIRS`
    にもリスト外、`CORE_SYSTEM_FILES_EXTRA`にも含まれていない)
  - `structural/*.bak`・`structural/*.json`は除外対象に含まれていない
    (判定式`p.endswith(".py") and p.startswith(CORE_SYSTEM_DIRS)`が
    `.py`拡張子のみを対象とするため)
- 承認処理: `mocka_git_safe_commit()`内には存在しない
  (`AUTOSEAL_Observation_Record_2026-07-01.md`セクション7で確認済み)

---

## 2 MANUAL_SEAL

- エンドポイント: `app.py` `@app.route("/audit/seal", methods=["POST"])` `def audit_seal_manual():`
  (2100-2113行目付近)
- トリガー: `/audit/seal`へのPOSTリクエスト(app.py内のコードからは、この
  リクエストを送る主体が人間か別プロセスかは判別できない。エンドポイントが
  呼び出された時点で処理が実行される)
- 書き込み範囲: `audit_seal_manual()`は`AUTO_SEAL_50EVT`と同一の
  `seal_script = scripts/ledger/anchor_update.py`を`subprocess.run()`で
  呼び出している。呼び出し先の`anchor_update.py`は、受け取った文字列
  (`"MANUAL_SEAL_" + timestamp`)を`git commit`メッセージとして使うのみで、
  分岐処理は行わない(`anchor_update.py:66` `msg = sys.argv[1] if len(sys.argv) > 1 else ...`
  以降、`msg`の値による処理分岐は存在しない)。よってAUTO_SEAL_50EVTと
  **同一の`mocka_git_safe_commit()`経路を使用する**(今回read-onlyで新規確認)
- commitメッセージ形式: `"MANUAL_SEAL_" + datetime.now().strftime("%Y%m%d_%H%M%S")`
  (`app.py`内の該当行で確認)

---

## 3 auto_audit_loop(daemon)

- 起動位置: `app.py:4062` `_lt.Thread(target=auto_audit_loop, daemon=True).start()`
- 時間トリガー(日次条件): `app.py:2065` `if now.hour == 0 and _last_seal_date[0] != today:`
  -> `subprocess.run(["python", str(seal_script), "AUTO_SEAL_" + today], ...)`
- 件数トリガー(50イベント条件): `app.py:2076-2077` `count - _last_event_count[0] >= 50`
  条件は、同一の`auto_audit_loop()`関数内で日次条件とは別のif分岐として存在し、
  日次条件から独立した条件式である(いずれも同一の`while True:`ループ内、
  `_lt2.sleep(60)`で60秒ごとに両条件が順に評価される)
- (今回read-onlyで新規確認): ループの各反復で`try/except`により例外は
  `print(f"[AUTO-AUDIT] ループ例外: {e}")`として捕捉され、ループ自体は
  停止せず次の60秒後の反復に進む構造になっている

---

## 4 WATCHDOG_DAILY_SEAL

- トリガー条件: `watchdog_mocka.py`による監視デーモンからの日次seal起動
- 呼び出し元: `watchdog_mocka.py:89`（`["python", "scripts/ledger/anchor_update.py", "watchdog daily seal"]`）
- 実行主体: `scripts/ledger/anchor_update.py`（経路1のAUTO_SEAL_50EVTと同一の実行ファイルだが、起動元が異なる独立トリガー）
- 書き込み範囲: `mocka_git_safe_commit()`経由、経路1と同じcommit処理を通過

（2026-07-02、read-onlyでのgrep調査により新規確認。本カタログに未記載だった第4の起動経路。他3経路との重複可能性・二重起動リスクは未検証）

---

## 5 共通事項(3経路に共通する事実)

- 3経路(AUTO_SEAL_50EVT、AUTO_SEAL_{today}、MANUAL_SEAL_{timestamp})は
  いずれも最終的に同一の`anchor_update.py`の`main()`関数を実行し、その中で
  `mocka_git_safe_commit(message=msg, push=False)`を呼び出す
- `push=False`が固定であることは、`anchor_update.py:75,99`双方の呼び出しで
  確認済み(`governance/mocka_git_safe_commit.py`関数シグネチャのデフォルト値
  `push=False`とも一致)
- 3経路とも最終的に`git commit`として確定する(`git push`は行われない)
- `is_core_system_file()`の判定式(`CORE_SYSTEM_DIRS` + `.py`拡張子限定)は
  `anchor_update.py`が呼び出す`mocka_git_safe_commit()`を経由する限り、
  3経路すべてに共通で適用される
- (今回read-onlyで新規確認): `anchor_update.py:32-47` `check_staged_files()`が
  `mocka_git_safe_commit()`呼び出しより前に実行され、staged中のファイルパスに
  `PRE_COMMIT_FORBIDDEN`(`TestProfile/`, `Default/Cache/`, `chrome_debug/`,
  `.env`, `secrets/`)のいずれかの文字列が含まれる場合、`sys.exit(1)`で
  処理を停止する。この停止処理は`is_core_system_file()`とは別の、
  文字列パターン一致による停止であり、3経路すべてに共通して適用される
  (`anchor_update.py:66-68`、`check_staged_files()`が`mocka_git_safe_commit()`
  より先に呼ばれる位置関係で確認済み)

---

本カタログは現行コードの静的な振る舞いの記述であり、
経路の統合・分離・許可・禁止についての設計判断を含まない
(GL7_STATE_LOCK: decision_layer/design_layer DISABLED)

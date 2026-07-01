# AUTOSEAL_PATHMAP_v1.0

対象: AUTO_SEAL書き込み経路の全体マップ(read-only trace + documentation)
前提: 本マップはGL7_STATE_LOCK(decision_layer/design_layer: DISABLED)下の
documentation範囲で作成する。既存構造の可視化のみを目的とし、
A(ガード追加)/B(正式経路化)/C(再設計)いずれの判断も含まない。

参照元: MOCKA_KN-004_CONTRADICTION_CHECK、MOCKA_AUTOSEAL_INVESTIGATION、
AUTOSEAL_Observation_Record_2026-07-01.md

---

## 全体フロー(テキスト形式)

```
[1 Trigger] app.py: auto_audit_loop()(daemon thread)
    |
    |-- 日次条件: now.hour == 0 かつ本日未sealの場合
    |       -> subprocess.run(["python", anchor_update.py, "AUTO_SEAL_" + today])
    |
    |-- 件数条件: SQLiteイベント件数が前回チェックから50件以上増加、
    |             かつ _seal_running フラグがFalseの場合
    |       -> subprocess.run(["python", anchor_update.py, "AUTO_SEAL_50EVT"])
    |
    v
[2 Transform] scripts/ledger/anchor_update.py
    |
    |-- from mocka_git_safe_commit import is_core_system_file, mocka_git_safe_commit
    |-- mocka_git_safe_commit(message=msg, push=False) を呼び出す
    |
    v
    governance/mocka_git_safe_commit.py: is_core_system_file(path)
    |
    |-- 判定式: p.endswith(".py") and p.startswith(CORE_SYSTEM_DIRS)
    |   CORE_SYSTEM_DIRS = ("phi_os/", "interface/", "structural/", "gateway/")
    |   CORE_SYSTEM_FILES_EXTRA = ("app.py", "index.html",
    |       "scripts/ledger/anchor_update.py",
    |       "PlanningCaliber/workshop/mocka-cloudflare/sync_watch.py")
    |
    |-- 除外される実例: 上記CORE_SYSTEM_FILES_EXTRAに列挙されたファイル
    |-- 除外されない実例: mocka_mcp_server.py(CORE_SYSTEM_DIRSにもEXTRAにも
    |       非該当)、structural/governance_pipeline.py.bak(.py以外の拡張子)、
    |       structural/beta_registry.json(.py以外の拡張子)
    |
    v
[3 Write] git add(除外対象外パス) -> git commit(push=False固定)
    |
    |-- 反映実績: commit 8c00633e3(2026-07-01 13:39:26、AUTO_SEAL_50EVT)
    |       -> mocka_mcp_server.py へのregistry_kn004接続コード反映
    |       -> structural/governance_pipeline.py.bak(149行、新規)反映
    |-- 反映実績: commit c810150b4はAUTO_SEAL経路ではなく別途の明示的
    |       git commit(本セッション内で確認済み、比較対象として記載)
```

---

## 各層の参照根拠

### 1 Trigger
- `app.py:2060` `def auto_audit_loop():` — daemon threadとして`app.py:4062`
  `_lt.Thread(target=auto_audit_loop, daemon=True).start()`で起動
- `app.py:2065-2071`: 日次条件(`now.hour == 0`かつ`_last_seal_date[0] != today`)
  -> `AUTO_SEAL_{today}`
- `app.py:2076-2085`: 件数条件(`count - _last_event_count[0] >= 50`かつ
  `not _seal_running[0]`) -> `AUTO_SEAL_50EVT`
- 本セッションの既存調査(MOCKA_AUTOSEAL_INVESTIGATION 手順1)で確認済みの
  `app.py:2071/2085/2114`行の`subprocess.run(...)`呼び出し箇所と対応
- (今回のマップ作成にあたり、上記トリガー条件の具体的なコード
  (`now.hour==0`条件および50件カウント条件)をread-onlyで新規に確認した。
  既存調査ではsubprocess呼び出し行のみを確認しており、条件式自体の確認は
  今回が初出)

### 2 Transform
- `scripts/ledger/anchor_update.py:17` import文、`:75` `mocka_git_safe_commit(message=msg, push=False)`呼び出し
  (MOCKA_AUTOSEAL_INVESTIGATION 手順2で確認済み)
- `governance/mocka_git_safe_commit.py:30-47` `is_core_system_file()`定義
  (MOCKA_AUTOSEAL_INVESTIGATION 手順2、AUTOSEAL_Observation_Record_2026-07-01.md
  セクション3で確認済み)
- mocka_mcp_server.pyが対象外である事実、structural/*.bak・*.jsonが対象外
  である事実は、同記録セクション4・5で確認済み

### 3 Write
- `mocka_git_safe_commit()`のデフォルト引数`push=False`
  (`governance/mocka_git_safe_commit.py:67`関数シグネチャで確認済み)
- commit `8c00633e3a80c8d91e9a1b8847dafdf9607f13e8`(2026-07-01 13:39:26、
  MOCKA_KN-004_CONTRADICTION_CHECK 手順3・MOCKA_AUTOSEAL_INVESTIGATION 手順1で
  内容確認済み) — mocka_mcp_server.pyへのregistry_store接続反映
- 比較対象: commit `c810150b4a80c8d91e9a1b8847dafdf9607f13e8`(2026-07-01
  14:43:02)は、本セッション内で明示的な`git add`/`git commit`コマンドとして
  実行されたものであり、AUTO_SEAL経路とは別の反映経路である
  (KN-004_Registry_Session_LanguageRecord.mdセクション2.7-2.8参照)

---

## 承認・停止処理の不在(事実の記述のみ)

- `mocka_git_safe_commit()`関数(`governance/mocka_git_safe_commit.py`)の
  実装内に、input待ち・承認フラグ確認・外部承認APIコールに相当する処理は
  存在しない(AUTOSEAL_Observation_Record_2026-07-01.mdセクション7で確認済み)
- 同関数が行う処理は`is_core_system_file()`によるパス除外判定のみであり、
  除外対象に該当しないパスはこの判定を経て`git add`/`git commit`に進む
- `app.py`の`auto_audit_loop()`内の日次条件・件数条件のいずれにも、
  トリガー発火前に人間の確認を待つ処理(input待ち・承認APIコール等)は
  見当たらない。人間が明示的に関与する経路は`/audit/seal`(POST)エンドポイント
  (`app.py`の`audit_seal_manual()`)のみであり、これは`MANUAL_SEAL_{timestamp}`
  という別のトリガー名で区別されている

---

**本マップは既存構造の可視化であり、AUTO_SEALを許可/制度化/再設計する
いずれの判断も含まない(GL7_STATE_LOCK: decision_layer/design_layer DISABLED)。**

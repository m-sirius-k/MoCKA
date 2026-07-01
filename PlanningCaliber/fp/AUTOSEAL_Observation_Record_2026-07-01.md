# AUTOSEAL Observation Record - 2026-07-01

位置づけ: 本文書は観測ログである。結論・断定ではない。
AUTO_SEALの正体(正式機構/偶発的経路/事故残骸)についての断定は行わない。
本文書はMOCKA_KN-004_CONTRADICTION_CHECKおよびMOCKA_AUTOSEAL_INVESTIGATIONの
結果を、解釈語を排除して観測事実のみでまとめたものである。

---

## 1. commit 8c00633e3 の内容(registry_kn004接続)

- commit: `8c00633e3b64f9226810791f212b8ce6052d6b5c`
- 日時: 2026-07-01 13:39:26 +0900
- commitメッセージ: `AUTO_SEAL_50EVT`
- 変更ファイル一覧:
  ```
  data/MOCKA_OVERVIEW.json              |   2 +-
  data/MOCKA_TODO.json                  |   2 +-
  data/events_latest.json               | 216 +++++++--------
  data/lever_essence.json               |   2 +-
  data/ping_latest.json                 |  10 +-
  interface/health_baseline.json        |   4 +-
  interface/lever_essence.json          |   8 +-
  mocka_mcp_server.py                   |  44 ++-
  mocka_mcp_server.py.bak               | 506 ++++++++++++++++++++++++++++------
  structural/governance_pipeline.py.bak | 149 ++++++++++
  ```
- `mocka_mcp_server.py`(44行)の差分内容: registry_store importブロック(7行、35-41行目)、
  `TOOLS`への3ツール定義追加(`mocka_registry_get`/`mocka_registry_add`/`mocka_registry_current_state`)、
  `execute_tool`への3つのelif分岐追加(各分岐に`registry_store is None`チェックを含む)

## 2. AUTO_SEAL生成元(anchor_update.py -> mocka_git_safe_commit)

- `app.py:2071,2085,2114`: `subprocess.run(["python", str(seal_script), "AUTO_SEAL_..."])`
  (`seal_script = scripts/ledger/anchor_update.py`)
- `scripts/ledger/anchor_update.py:17`: `from mocka_git_safe_commit import is_core_system_file, mocka_git_safe_commit`
- `scripts/ledger/anchor_update.py:75`: `commit_result = mocka_git_safe_commit(message=msg, push=False)`
- `scripts/ledger/anchor_update.py:99`: `mocka_git_safe_commit(message=f"anchor: re-seal after {commit[:7]}", push=False)`
- anchor_update.py自体は独自のsubprocess直呼び出しでgit操作を行っておらず、
  mocka_git_safe_commit()経由でgit add/commitを実行している

## 3. is_core_system_file()の保護範囲(CORE_SYSTEM_DIRS + .py限定)

`governance/mocka_git_safe_commit.py` 30-47行目:
```python
CORE_SYSTEM_DIRS = ("phi_os/", "interface/", "structural/", "gateway/")
CORE_SYSTEM_FILES_EXTRA = (
    "app.py", "index.html", "scripts/ledger/anchor_update.py",
    "PlanningCaliber/workshop/mocka-cloudflare/sync_watch.py",
)
PRIVATE_REPO_DIRS = ("PlanningCaliber/workshop/",)

def is_core_system_file(path: str) -> bool:
    p = path.replace("\\", "/")
    if p in CORE_SYSTEM_FILES_EXTRA:
        return True
    if p.startswith(PRIVATE_REPO_DIRS):
        return True
    return p.endswith(".py") and p.startswith(CORE_SYSTEM_DIRS)
```

## 4. mocka_mcp_server.py自体がこの保護範囲に含まれていない事実

- `mocka_mcp_server.py`はリポジトリ直下に配置されており、`CORE_SYSTEM_DIRS`
  (`phi_os/`, `interface/`, `structural/`, `gateway/`)のいずれの接頭辞にも一致しない
- `CORE_SYSTEM_FILES_EXTRA`のリスト(`app.py`, `index.html`,
  `scripts/ledger/anchor_update.py`, `PlanningCaliber/workshop/mocka-cloudflare/sync_watch.py`)
  にも`mocka_mcp_server.py`は含まれていない
- 上記2点により、`is_core_system_file("mocka_mcp_server.py")`は`False`を返す

## 5. structural/配下の.bak/.json拡張子が保護対象外である事実

- `is_core_system_file()`の最終判定式は `p.endswith(".py") and p.startswith(CORE_SYSTEM_DIRS)`
- `structural/governance_pipeline.py.bak`(拡張子`.bak`)、`structural/beta_registry.json`(拡張子`.json`)
  は、`structural/`という接頭辞には一致するが、`.py`で終わっていないため、この判定式は`False`を返す
- 直近5件のAUTO_SEALコミット(948a71f2d, abeecb32b, 8c00633e3, 094efd5d4, 1c374fa76)のうち、
  複数件で`structural/beta_registry.json`および`.bak`/`.bak2`拡張子ファイルが変更対象に含まれていた

## 6. 2026-06-25インシデントに関するコード内コメント(TODO_347)

`governance/mocka_git_safe_commit.py` 26-29行目:
```
# Core System File Change Approval(Human Gate)対象。
# 自動シール(AUTO_SEAL_50EVT等)が無承認でこれらの変更を確定させてしまう
# 事故が2026-06-25に発生したため、対象は無条件git add -Aから除外し、
# 未コミットのまま人間承認待ちとして残す(TODO_347governance修正)。
```

## 7. 承認確認ステップがmocka_git_safe_commit()内に存在しない事実

- `mocka_git_safe_commit()`関数(`governance/mocka_git_safe_commit.py`)内には、
  input待ち・承認フラグ確認・外部承認APIコール等の処理は存在しない
- 同関数が行う処理は、`is_core_system_file()`によるパス除外判定のみであり、
  除外対象に該当しないパスは無条件でgit add/commitされる

## 8. registry_store import失敗時はNoneチェック+try/exceptで捕捉される(実行安全性の観測結果)

`mocka_mcp_server.py` 648, 658, 676行目、各elif分岐の冒頭:
```python
if registry_store is None:
    return json.dumps({"error": "registry_store unavailable"}, ensure_ascii=False)
```
- 3分岐(`mocka_registry_get`/`mocka_registry_add`/`mocka_registry_current_state`)いずれにも存在
- さらに`execute_tool()`全体が`try/except Exception as e: return json.dumps({"error": str(e)})`
  で囲まれており、上記チェックが無い場合でも例外は捕捉される

---

## 未観測領域

- AUTO_SEALのトリガー条件(50イベント到達判定ロジック)の完全なトレース
- mocka_git_safe_commit()以外の箇所に承認処理が存在するかどうか
- AUTO_SEALがCHANGE_START/CHANGE_DONEプロトコル(TODO_144)をバイパスしているかどうか
- AUTO_SEALが正式に設計された機構か、偶発的に成立した経路か、過去のインシデント対応の残骸かについての判定

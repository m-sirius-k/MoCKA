# PHASE5_1_A HGD-D1 STEP 2 .GITIGNORE AUDIT REPORT (TODO_390)

- Date: 2026-10-02
- Executed by: KUROKO PC (Claude-sonnet-4-6)
- Mode: READ-ONLY AUDIT
- Reference: DC_20261002_HGD_D1_IMPLEMENTATION_AUTHORIZATION, DC_20261002_HGD_B1_IMPLEMENTATION_SCOPE, TODO_390

---

## 1. 監査対象

HGD-B1 が新規作成する予定のファイル:
- `data/governance/tool_registry.json`

TODO_390 インシデント背景:
> data/ 配下、またはその他 .gitignore で包括除外パターン (dir/\*等) が設定されている
> ディレクトリに新規ファイルを作成する場合、git add や mocka_git_safe_commit() を実行する
> 前に必ず .gitignore の該当ディレクトリのルールを確認し、新規ファイルが
> ホワイトリスト (!path 形式の例外) に含まれているかを確認すること。
> mocka_git_safe_commit() は Exclude 対象ファイルについてエラーを出さず
> 静かにスキップする仕様のため、コミット後に意図したファイルが含まれているか確認要。

---

## 2. .gitignore 現在の data/ ルール

```
# data/ 内は全除外。Cloudflare 同期用4ファイルのみ例外追跡
data/*                                        # 行 2: data/ 配下を全除外
!data/MOCKA_OVERVIEW.json                     # 行 3: 例外 (whitelist)
!data/MOCKA_TODO.json                         # 行 4
!data/lever_essence.json                      # 行 5
!data/events_latest.json                      # 行 6
!data/MOCKA_TODO_ACTIVE.json                  # 行 7
!data/MOCKA_TODO_REFERENCE_LOCKED.json        # 行 8
!data/MOCKA_TODO_ARCHIVE.json                 # 行 9
!data/MOCKA_ENDPOINTS.json                    # 行 10
!data/tic/                                    # 行 12: tic/ ディレクトリ例外
data/tic/*                                    # 行 13: tic/ 内を再除外
!data/tic/canary_overrides_last_run.json      # 行 14: tic/ 内の例外
!data/decisions/                              # 行 16: decisions/ ディレクトリ例外
data/decisions/*                              # 行 17: decisions/ 内を再除外
!data/decisions/.gitignore                    # 行 18
!data/decisions/decision_ledger.jsonl         # 行 19
```

---

## 3. git check-ignore 実測結果

```
$ git check-ignore -v "data/governance/tool_registry.json"
.gitignore:2:data/*    data/governance/tool_registry.json
exit: 0

$ git check-ignore -v "data/governance/"
.gitignore:2:data/*    data/governance/
exit: 0
```

**結論: `data/governance/tool_registry.json` は現在の .gitignore により EXCLUDED (git 追跡対象外)**

---

## 4. 参照: 既存 whitelist パターンの動作確認

```
$ git check-ignore -v "data/decisions/decision_ledger.jsonl"
(no output — NOT ignored)
exit: 1

$ git check-ignore -v "data/tic/canary_overrides_last_run.json"
(no output — NOT ignored)
exit: 1

$ git check-ignore -v "data/MOCKA_OVERVIEW.json"
(no output — NOT ignored)
exit: 1
```

whitelist パターン (`!data/decisions/` + `data/decisions/*` + `!data/decisions/decision_ledger.jsonl`)
は正常に機能している。

---

## 5. TODO_390 確認結果

| 確認項目 | 結果 |
|---------|------|
| `data/governance/` は data/* に包括除外されるか | **YES — EXCLUDED** |
| `data/governance/tool_registry.json` の whitelist 例外があるか | **NO — 存在しない** |
| 現状のまま git add すると tool_registry.json がコミットに含まれるか | **NO — 静かにスキップされる** |
| .gitignore の変更が B1 実装前に必要か | **YES — 必須** |

---

## 6. 必要な .gitignore 変更 (実装時に適用)

B1 実装 (STEP 5) で tool_registry.json を作成する前に、
以下のパターンを .gitignore に追加する必要がある。

追加位置: 行 19 (`!data/decisions/decision_ledger.jsonl`) の直後

```diff
 !data/decisions/
 data/decisions/*
 !data/decisions/.gitignore
 !data/decisions/decision_ledger.jsonl
+# data/governance/tool_registry.json: HGD-B1 GL11 Tool Registry (DC_20261002_HGD_B1_IMPLEMENTATION_SCOPE)
+!data/governance/
+data/governance/*
+!data/governance/tool_registry.json
```

パターン説明:
- `!data/governance/` — ディレクトリ自体を追跡対象に
- `data/governance/*` — 内部を再除外 (deny-by-default)
- `!data/governance/tool_registry.json` — 対象ファイルのみ例外

---

## 7. STEP 2 RESULT

```
STEP 2 RESULT: TODO_390 VIOLATION CONFIRMED — .gitignore 変更が必須

data/governance/tool_registry.json は現在 .gitignore:2 (data/*) により
EXCLUDED。ホワイトリスト例外が存在しない。

変更なしで B1 実装を進めると tool_registry.json が git に追跡されず、
mocka_git_safe_commit() が静かにスキップする (TODO_390 インシデントと同一パターン)。

対処方法:
  STEP 5 (B1 実装: tool_registry.json 作成) の前に
  .gitignore への whitelist 追加を実施する。
  (CHANGE_START / CHANGE_DONE プロトコル適用)

STEP 2: CLOSED (audit 完了)
次ステップ: STEP 3 (CHANGE_START 記録) → STEP 4 (A1 実装) → STEP 5 (B1 実装)
```

---

*STEP 2 完了 — コード変更なし / .gitignore 変更なし / コミットなし / Runtime activation なし*
*STEP 2 は audit のみ。.gitignore 実際の変更は STEP 5 実装時に行う。*

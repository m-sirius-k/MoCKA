# CI Failure Fact Collection — MoCKA Global Rule Guard v0.1

位置づけ: くろこ作業指示（2026-07-04、「GitHub CI Failure(MoCKA Global Rule Guard) ― 事実収集フェーズ」）に基づく事実収集フェーズの成果物。役割は制度書記官・実装調整官。原因推定・修正案の提示は一切行っていない。収集した事実を提示した時点で作業を停止し、監査官(R01)およびきむら博士の判断を待つ。

対象: GitHub Actions workflow「MoCKA Global Rule Guard」（`.github/workflows/mocka_guard.yml`、workflow ID 299904033）。

---

## 1. GitHub Actionsの失敗ログ全文（直近実行分、run ID 28688660558、2026-07-04T00:03:11Z）

```
##[group]Run echo "Checking MoCKA structural integrity..."
echo "Checking MoCKA structural integrity..."

if grep -r "mocka_v0.1" --include="*.py" --include="*.md" -l .; then
  echo "RULE VIOLATION: temp folder detected"
  exit 1
fi

if find . -type d -path "*/mcp/mcp"; then
  echo "RULE VIOLATION: double nesting detected (mcp/mcp)"
  exit 1
fi

if find . -type d -path "*/relay/relay"; then
  echo "RULE VIOLATION: double nesting detected (relay/relay)"
  exit 1
fi

if find . -type d -path "*/event/event"; then
  echo "RULE VIOLATION: double nesting detected (event/event)"
  exit 1
fi

echo "STRUCTURE OK"
shell: /usr/bin/bash -e {0}
##[endgroup]
Checking MoCKA structural integrity...
./docs/mocka_global_rules.md
RULE VIOLATION: temp folder detected
##[error]Process completed with exit code 1.
```

上記に続き、同一run内の別ステップ（Post Checkout／job cleanup）で以下の警告が記録されている（rule-check本体とは別ステップ）:
```
fatal: No url found for submodule path 'PlanningCaliber/sirius-lab-products' in .gitmodules
##[warning]The process '/usr/bin/git' failed with exit code 128
```

この警告は「Validate MoCKA Structure」ステップの失敗（exit code 1）とは別のステップ（Post Checkout、job cleanup処理内の`git submodule foreach`）で発生しており、当該ステップ自体はconclusion="success"として記録されている。

---

## 2. `rule-check`ジョブでexit code 128になった正確な箇所

**exit code 128は「rule-check」ステップ（Validate MoCKA Structure）では発生していない。** job失敗を引き起こしたのは同ステップ内の`exit 1`（bashスクリプト自身が明示的に実行）であり、失敗ステップの最終行は`##[error]Process completed with exit code 1.`である。

exit code 128は、同一run内の別ステップ「Post Checkout」（`actions/checkout@v4`のクリーンアップ処理）内で発生している。当該処理が実行する`git submodule foreach ...`コマンドが`fatal: No url found for submodule path 'PlanningCaliber/sirius-lab-products' in .gitmodules`というエラーとともに終了し、その終了コードに対して`##[warning]The process '/usr/bin/git' failed with exit code 128`という**warning注記**が付与されている。このステップ自体はconclusion="success"であり、job全体の失敗要因（conclusion="failure"）ではない。

---

## 3. 最初に失敗した日時

`workflow_runs` API（`total_count`=700、全700件を取得・確認）における最古の記録:

- run ID: 27924895961
- 発生日時: 2026-06-22T01:58:20Z（＝2026-06-22 10:58:20 +0900）
- 対象コミット: `99b6a3093f6fc6ca36fe5ef95d0ffe019eb83c52`
- 結果: failure（この最初の記録済み実行から既に失敗している）

---

## 4. 直近で成功した実行日時

**該当なし。** workflow「MoCKA Global Rule Guard」の全700件の記録済み実行（2026-06-22T01:58:20Z 〜 2026-07-04T00:03:11Z）を確認したが、`conclusion`が`success`の実行は1件も存在しなかった（`failure`: 700件、それ以外: 0件）。

---

## 5. どのコミットから失敗し始めたか

記録が存在する範囲（`total_count`=700、workflow初回実行時点まで遡って確認）では、**「途中から失敗し始めた」という状態確認はできなかった**。最古の記録済み実行（3.項、commit `99b6a3093f6fc6ca36fe5ef95d0ffe019eb83c52`、2026-06-22T01:58:20Z）から直近実行（commit確認は下記6項参照）まで、確認した全実行が同一の失敗パターン（`docs/mocka_global_rules.md`内の"mocka_v0.1"文字列検出による`exit 1`）を示している。

---

## 6. 同じWorkflow内で他ジョブは成功しているか

`.github/workflows/mocka_guard.yml`の`jobs:`定義には`rule-check`という単一のジョブのみが存在する。API照会（直近run・最古run双方）でも、jobsは`rule-check`1件のみが記録されている。**他ジョブは定義上存在しない**ため、「他ジョブとの成否比較」という事実自体が成立しない。

---

## 7. 認証・checkout・submodule・fetch・rule-check本体のどの段階で終了したか

直近run（28688660558）のステップ単位のconclusion:

| # | ステップ名 | conclusion |
|---|---|---|
| 1 | Set up job | success |
| 2 | Checkout（認証・fetch含む） | success |
| 3 | **Validate MoCKA Structure（rule-check本体）** | **failure** |
| 6 | Post Checkout（submodule関連の警告が発生） | success（warning付き） |
| 7 | Complete job | success |

job失敗（conclusion="failure"）を決定づけたのはステップ3「Validate MoCKA Structure」（rule-check本体）である。認証・checkout・fetchの各処理（ステップ2）は成功として記録されている。submodule関連のgit警告（exit 128）はステップ6（Post Checkout）で発生しており、ステップ2のcheckout/fetch自体の失敗ではない。

---

## 8. GitHub Runner情報

直近run・最古run（2026-06-22T01:58:20Z時点）ともに以下の情報が記録されている（最古runのログより抜粋）:

- Runner: GitHub Actions hosted runner（`runner_group_name`: "GitHub Actions"）
- Operating System: Ubuntu 24.04.4 LTS
- Runner Image: `ubuntu-24.04`（Image Release: `20260615.205`／最古runでは`20260615.205.1`との表記差ありー実行ごとにイメージバージョンが異なる）
- Hosted Compute Agent Version: 20260611.554
- git version: 2.54.0
- `actions/checkout@v4`使用（`fetch-depth: 1`、`submodules: false`指定）
- 実行環境に関する注記: 「Node.js 20 is deprecated...being forced to run on Node.js 24」という警告が全run共通で記録されている（`actions/checkout@v4`のNode実行系に関する一般的な注記）。

---

## 9. エラーメッセージ原文

**job失敗の直接原因となったメッセージ**（ステップ3内）:
```
./docs/mocka_global_rules.md
RULE VIOLATION: temp folder detected
##[error]Process completed with exit code 1.
```

**別ステップ(Post Checkout)の警告メッセージ原文**:
```
fatal: No url found for submodule path 'PlanningCaliber/sirius-lab-products' in .gitmodules
##[warning]The process '/usr/bin/git' failed with exit code 128
```

---

## 参考: ワークフロー定義および検出対象文字列の現状（事実のみ）

`.github/workflows/mocka_guard.yml`のステップ3で実行されるスクリプトは以下の通り（現行版）:
```
if grep -r "mocka_v0.1" --include="*.py" --include="*.md" -l .; then
  echo "RULE VIOLATION: temp folder detected"
  exit 1
fi
```

現時点のリポジトリ内で`grep -n "mocka_v0.1" docs/mocka_global_rules.md`を実行すると、以下がヒットする:
```
19:- mocka_v0.1
```

---

## 出力形式（指示書指定フォーマット）

```
[発生日時] 2026-06-22T01:58:20Z（最古の記録済み失敗）〜 2026-07-04T00:03:11Z（直近実行）の全700件が同一パターンで失敗
[失敗コミット] 最古: 99b6a3093f6fc6ca36fe5ef95d0ffe019eb83c52（2026-06-22T01:58:20Z） / 直近実行時点のHEAD（2026-07-04T00:03:11Z push）
[失敗段階] rule-checkジョブ内ステップ3「Validate MoCKA Structure」（認証・Checkout・fetchは成功。同ジョブ内に他ステップ・他ジョブなし）
[エラーメッセージ原文] "./docs/mocka_global_rules.md" / "RULE VIOLATION: temp folder detected" / "##[error]Process completed with exit code 1."（別ステップの警告: "fatal: No url found for submodule path 'PlanningCaliber/sirius-lab-products' in .gitmodules" / "##[warning]The process '/usr/bin/git' failed with exit code 128"）
[直近成功実行] 記録なし（workflow全700件の実行記録中、成功は0件）
[他ジョブの成否] 該当なし（このworkflowにはrule-check以外のジョブが定義されていない）
[Runner情報] GitHub Actions hosted runner／Ubuntu 24.04.4 LTS／runner image ubuntu-24.04／actions/checkout@v4／git 2.54.0
```

---

以上が収集した事実である。原因推定・修正案の提示は一切行っていない。監査官(R01)およびきむら博士の判断を待つ。

## 改訂履歴

- v0.1（2026-07-04）: くろこ作業指示（GitHub CI Failure事実収集）に基づき新規作成。くろこ起草。

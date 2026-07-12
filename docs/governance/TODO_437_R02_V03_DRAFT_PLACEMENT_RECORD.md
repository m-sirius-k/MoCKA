# TODO_437 R02 v0.3_DRAFT Placement Record

作成: Claude-sonnet-5(S02, くろこ) / 2026-07-10 / Artifact Record(Decision Ledgerではない)

分類: Artifact Record。制度的裁定・採否判断は含まない。物理配置作業の検証証跡のみ。

## 1. 配置日時

- Write実行(CHANGE_START): 2026-07-10 17:47:01(event_id: `E20260710_220666443d337`)
- ファイルシステム上のBirth/Modify: 2026-07-10 17:49:54(JST)
- Write実行(CHANGE_DONE): 2026-07-10 17:50:21(event_id: `E20260710_4208732339dde`)

## 2. 配置元

- パス: `X:\down\TODO_437_R02_REMEDIATION_PLAN_v0.3_DRAFT.md`
- 作成者表記(ファイル内): R02 Claude
- リポジトリ外(MoCKA本体のgit管理対象外の場所)

## 3. 配置先

- パス: `docs/governance/TODO_437_R02_REMEDIATION_PLAN_v0.3_DRAFT.md`
- MoCKAリポジトリ内(`C:\Users\sirok\MoCKA`配下)

## 4. Hash

配置元・配置先とも同一SHA256を確認。

```
SHA256: 0d90e5345f11b8827afbd3740ff5d602056a0838d44a83bbe562f2e610abe329
```

## 5. Diff結果

`diff`コマンドによるバイト単位比較の結果、差分なし(diff exit code: 0)。
内容改変は発生していない。

## 6. 付随検証

- UTF-8検証: OK(BOMなし、`mocka_check_utf8`にて確認)。
- 行数: 配置元512行・配置先512行(一致)。
- サイズ: 39,874 bytes(両ファイル一致)。

## 7. Git状態確認

```
git status --short -- docs/governance/TODO_437_R02_REMEDIATION_PLAN_v0.3_DRAFT.md
?? docs/governance/TODO_437_R02_REMEDIATION_PLAN_v0.3_DRAFT.md
```

untracked状態を確認。追跡済みファイルへの変更(modified)は発生していない。

## 8. commit未実施確認

- `git log`に本ファイルを含むcommitは存在しない(untrackedのため対象外)。
- 本Placement Record作成時点で、`git commit`・`git push`はいずれも実行していない。
- Decision Ledgerへの追加も行っていない(本文書自体がDecision Ledgerではなく
  Artifact Recordであることの明示)。

## 9. 状態維持の確認

配置後も以下の状態を維持していることを確認する。

- `TODO_437_R02_REMEDIATION_PLAN_v0.1.md`: 正本、無変更。
- `TODO_437_R02_REMEDIATION_PLAN_v0.2.md`: Parallel Investigation Draft、無変更・未削除。
- `TODO_437_R02_REMEDIATION_PLAN_v0.3_DRAFT.md`: Draft Only、Repository: Reference Storage、
  Authority: Human Gate Pending。
- 正本化・v0.1置換・v0.2削除・Decision Ledger追加・TODO status変更・コード変更・
  timeout変更・DB変更・commit/pushのいずれも発生していない。

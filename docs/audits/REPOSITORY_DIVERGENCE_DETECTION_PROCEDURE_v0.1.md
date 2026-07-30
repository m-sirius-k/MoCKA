# Repository Divergence Detection Procedure v0.1

Status: 手順提案（Human Gate確認前。まだ制度として固定しない）
Date: 2026-07-30
記録者: 執行官Claude（くろこ、Cloud session）
関連: REPOSITORY_DIVERGENCE_REPORT_v0.1.md、EVIDENCE_SYNCHRONIZATION_STRATEGY_v0.1.md

本文書は、Cloud checkout・Local Windows環境・GitHub の3環境間に生じる乖離を、なるべく作業の早期
段階で検知するための確認手順を定義する。今回のOption C監査で発覚した（Cloud checkoutには対象文書が
1件も存在しない）という状況を、同じセッションを最後まで進めてから発見するのではなく、着手時に発見できる
ようにする。

---

## 1. 手順の適用タイミング

- 継続作業を装った指示（例: （昨日作った文書を踏まえて）（S03〜S05を前提に）等）を受け取ったとき。
- 過去のsession_idやCHANGE_DONEイベントを引用する指示を受け取ったとき。
- 新しい制度文書・監査文書の作成に着手する前。
- 定期チェックとして、セッション開始直後（`mocka_get_overview` / `mocka_get_todo`直後）。

## 2. 確認手順

以下を順に実行する。順序は（軽く低コストな確認から重い確認へ）に並べてある。

### Step 1: Cloud checkoutのブランチ・commit状態確認

```
git rev-parse --abbrev-ref HEAD    # 現在のブランチ
git log -1 --format='%H %ci %s'    # 直近commit
git status --short                  # 未commit変更
```

期待: 指示されたブランチ名と一致し、直近commitが指示の前提と時系列上矛盾しないこと。

### Step 2: Cloud checkoutが到達できるGitHubブランチ・タグの確認

```
git fetch origin --prune
git branch -r
git tag --list
```

期待: 指示で参照されているブランチ・タグがremote側に存在すること。

### Step 3: 指示が前提とするファイルの実在確認（Cloud checkout側）

```
find /home/user/MoCKA -name '<期待されるファイル名>' 2>/dev/null
git log --all --oneline -- <期待されるファイルパス>
```

期待: 少なくとも一方でヒットすること。両方0件なら、そのファイルはCloud checkoutにもGitHub全ブランチ・
全タグにも存在しない（今回のOption C監査で発覚したパターン）。

### Step 4: 指示が前提とするLedger記録の実在確認（MCP側）

```
mocka_decision_get(decision_id=<指示で参照されているID>)
mocka_search(query=<キーワード>)
mocka_list_events(n=<必要な件数>)
```

期待: 対応するDecision Ledger記録・CHANGE_START/CHANGE_DONE要約が実在すること。

### Step 5: Cloud checkoutとLocal Windows環境の非対称の記録

Step 3で（Cloud/GitHub両方に不在）だがStep 4で（Ledger要約は存在）した場合、REPOSITORY_DIVERGENCE_
REPORT_v0.1.mdと同じ整理で、以下を記録する。

- 対象ファイル名一覧
- 検索コマンドと結果件数
- Ledger側で最後にCHANGE_DONEが記録された日時
- 判定: （Cloud checkoutに未同期）（Local環境が正本と推定される場合）または（削除済み・存在しない）
  （Ledgerが誤っている可能性がある場合）のどちらか、または（区別不能（要Human Gate確認））

## 3. 検知後の対応

- Step 3で不在が確定した場合、DC_20260730_009の（未検証文脈）隔離ルールを適用する（推測補完・記憶
  による接続を禁止する）。
- 検知内容はmocka_write_eventで記録する（title: `DIVERGENCE_DETECTED: <対象>`、tags: `divergence_
  detection,<対象>`）。今回のOption C監査もこの手順を踏んでいれば、監査着手前に早期検知できていた。
- 検知が繰り返し発生する場合、Integrity Classification（state: Risk, type: Mirror Risk）として
  記録することを検討する。

## 4. 本手順の限界

- 本手順はCloud checkout側から実行することを前提としている。Local Windows環境側の状態（未コミット
  ファイルの一覧等）は本手順からは確認できず、Local環境からの一次報告が別途必要。
- MCP経由で取得できるLedger要約は圧縮情報であり、ファイル本文の実在を保証しない。Step 3（実ファイル
  確認）と併用することが必須である。
- `mocka_check_utf8`は本セッションのファイルシステムに到達しないため、Cloud checkout側で作成した
  ファイルの検証には使えない。Cloud checkout側のUTF-8検証は、Bash経由でのPython/pythonicチェックで
  代替する。

---

## 改訂履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2026-07-30 | 0.1 | 初版。Task1-4切替後の追加指示に基づき作成。 |

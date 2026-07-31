# Commit-Event Traceability Policy

- Policy ID: GOV-PROC-CETR-001
- Status: Active
- Date: 2026-07-31
- Owner instruction: きむら博士 (作業指示 2026-07-31、基準点 commit 7d1302e3e)
- Trigger: AUDIT REPORT E20260731_64716908835df Finding [4]
- Related: GOV-PROC-EHCR-001 (DC_20260713_002), TODO_413 (git操作の制度的記録)
- Decision Ledger: 未登録 (本作業のスコープ外。5.3 参照)
- Classification: Governance Integrity Enhancement (not an incident fix)

## 1. Purpose

commit message 単体から、その変更に対応する Event Ledger の記録へ到達できる状態を
確保する。

2026-07-31 の監査 (E20260731_64716908835df) で、commit から Event への逆引き経路が
存在しないことが Finding [4] として検出された。Event 側の記述から commit を辿ることは
できるが、commit 側には event_id の参照がなく、commit message だけを起点とした
直接の逆引きはできない。

本 Policy は、この片方向性を解消し、MoCKA の三要素のうち Record と Verification を
git 履歴の側からも成立させることを目的とする。

## 2. 現状観測 (2026-07-31 実測)

本 Policy 制定の前提として観測した事実を記録する。設計判断ではなく観測結果である。

### 2.1 機械経由 commit (mocka_git_safe_commit)

`governance/mocka_git_safe_commit.py` は commit の前後で `_record_git_event()` を呼び、
CHANGE_START / CHANGE_DONE イベントを Event Ledger へ記録する (TODO_413)。
description には `commit_sha=<40桁>` が含まれる。

- `commit_sha=` を含むイベント: 1,154 件 (data/mocka_events.db 実測)
- したがって Event -> commit 方向は、この経路については構造的に成立している

### 2.2 人手起点の commit (git commit 直接実行)

外部ハーネス (Claude Code 等) から `git commit` を直接実行した場合、
`_record_git_event()` は経由されない。

- 基準点付近の commit 7d1302e3e / 3baf5dbe3 / 057bc4a67 / c2b9e6df0 について、
  `commit_sha=` を含むイベントは 0 件 (実測)
- これらの commit message にも event_id の記載はない
- すなわち、人手起点 commit では Event -> commit / commit -> Event の双方向とも
  構造的な経路が存在しない

### 2.3 既存の commit message 記法

commit body に証跡 ID を書く運用は、規約化されないまま散発的に存在する。

| 記法 | 用途 | 出現数 |
|------|------|--------|
| `CHANGE_START:` / `CHANGE_DONE:` | 変更ライフサイクルの event_id | 各 3 |
| `Incident:` | インシデント event_id | 2 |
| `Decision:` | Decision Ledger ID (DC_...) | 2 |
| `Evidence:` | 承認根拠 event_id | 1 |
| `Ref:` / `ref:` / `Refs:` | 汎用参照 | 8 |
| `[HUMAN_GATE_OVERRIDE:Phase1_chat_approval] event_id=...` | Core System File 承認証跡 (自動付与) | 8 |

`Event:` 行の使用例は 0 件である。本 Policy が新たに定める記法は既存記法と衝突しない。

## 3. Policy

### 3.1 記載義務

人手起点で作成する commit は、commit message body に、その変更に対応する
Event Ledger の event_id を記載する。

記載する event_id は、原則としてその変更の CHANGE_DONE イベントとする。
CHANGE_DONE が複数に分かれる場合、または監査・調査工程で CHANGE_DONE を伴わない
場合は、その工程を代表するイベント (AUDIT / INCIDENT / 裁定記録等) を記載する。

### 3.2 記載形式

commit message body の最終ブロックへ、以下の 1 行を置く。

```
Event: E20260731_1363369226719
```

- 行頭を `Event: ` (コロン + 半角空白) で始める
- event_id は正本形式 `E<YYYYMMDD>_<micros_of_day 9桁><hex 4桁>` を用いる
  (生成: `interface/db_helper.py`)。旧形式 `E<YYYYMMDD>_<連番3桁>` も参照可
- ID は `Event:` と同一行に書く。行を分けない (grep による機械抽出を成立させるため)
- 他の trailer (`Co-Authored-By:` 等) と同じブロックに置いてよい

複数のイベントを参照する場合は `Event:` 行を複数並べる。カンマ区切りにしない。

```
Event: E20260731_1363369226719
Event: E20260731_64716908835df
```

### 3.3 既存記法との併用

2.3 の既存記法は廃止しない。より詳細な意味付けが必要な場合は併記してよい。

```
CHANGE_START: E20260731_1363369226719
CHANGE_DONE: E20260731_2039571188cd3
Event: E20260731_2039571188cd3
```

ただし `Event:` 行の記載は省略しない。監査は `Event:` 行を単一の走査対象とする。

### 3.4 記載位置の禁止事項

- subject 行 (1行目) に event_id を書くことをもって本義務を満たしたとみなさない
  (subject は 50-72 文字制約下にあり、機械抽出の対象を body へ一本化する)
- commit message 以外 (PR 説明・チャットログ等) の記載は本義務を満たさない

## 4. Scope

### 4.1 適用対象

- リポジトリ `C:\Users\sirok\MoCKA` の `main` へ向けた、人手起点の commit
- 外部ハーネス (Claude Code / 他 AI エージェント) が実行する commit を含む

### 4.2 適用対象外

| 対象 | 理由 |
|------|------|
| `auto sync <ISO8601>` 形式の自動同期 commit | `sync_watch.py` が `mocka_git_safe_commit()` 経由で生成し、CHANGE_START / CHANGE_DONE イベントに `commit_sha` が記録される (2.1)。message 側の記載を追加しても新しい情報を与えない |
| `mocka_git_safe_commit()` を経由する常駐処理・自律処理の commit | 同上。Event -> commit の構造的経路が既に存在する |
| merge commit / revert の自動生成 message | 生成主体が git であり、人手の記載点がない |
| MoCKA リポジトリ外のリポジトリ | 本 Policy の統治範囲外 |

自動 commit を対象外とすることは、追跡性を放棄する意味ではない。
記録点が message ではなく Event 側にあるという経路の違いを明示するものである。

## 5. 適用開始時点

### 5.1 開始点

本文書を追加する commit を適用開始点とする。当該 commit 自身が `Event:` 行を持つ。

適用開始点より後の、4.1 に該当する commit が本 Policy の対象である。

### 5.2 過去 commit への遡及

過去 commit への遡及は行わない。

- 既存 commit の message を修正しない
- `git rebase` / `filter-branch` 等の履歴書き換えを行わない
  (CLAUDE.md の危険なgit操作の運用ルール、TODO_382 準拠)
- 適用開始点以前の commit に `Event:` 行がないことは、本 Policy 違反として扱わない

過去区間の追跡は、Event 側の記述および調査文書 (docs/audits/ 等) を経由する
間接経路に依存する。この非対称は仕様であり、欠陥として記録しない。

### 5.3 Decision Ledger 登録

本 Policy は作業指示に基づく運用規約の新設であり、制度裁定としての Decision Ledger
登録は本作業のスコープ外である。登録の要否はきむら博士の判断による。

## 6. 緊急 commit 時の例外

Event Ledger への記録が不能な状況 (MoCKA サーバー停止、Gate 障害、ネットワーク断等)
で、なお commit を先行させる必要がある場合に限り、以下を適用する。

### 6.1 手順

1. commit body へ `Event: PENDING` を記載する。理由を同ブロックへ 1 行で添える

```
Event: PENDING
Event-Pending-Reason: MoCKA gate unreachable at commit time
```

2. Event Ledger が復旧した時点で、当該 commit を参照するイベントを記録する。
   イベント本文に対象 commit のハッシュを明記する
3. 補完したイベントの event_id を、後続の任意の commit body へ以下の形式で記載する

```
Event-Backfill: <対象commitハッシュ> -> <補完したevent_id>
```

### 6.2 制約

- 元の commit は修正しない (5.2 の遡及禁止が優先する)
- `Event: PENDING` を未解消のまま放置しない。解消は次回作業セッション内で行う
- 例外の適用は、Event Ledger 側が記録不能な場合に限る。
  記録が可能な状況での省略は本 Policy 違反である

## 7. Prohibited

- 本 Policy を根拠に `app.py` / API / ポート契約 / events.db 仕様 /
  Decision Ledger schema / Event Ledger schema を変更すること。
  本件は運用規約案件であり、コード修正案件ではない
- 本 Policy を根拠に git history rewrite を行うこと
- `Event:` 行の記載を、commit-msg hook 等による機械的強制へ即時昇格させること。
  強制機構の導入は別途 Human Gate の判断を要する (本 Policy は運用規約に留まる)
- 存在しない event_id、または内容が対応しない event_id を記載すること
  (記録の偽装にあたる)

## 8. Verification Guidance

監査時に以下を確認できる状態を維持する。

### 8.1 適用区間の走査

適用開始点以降で、`auto sync` 以外の commit に `Event:` 行があるかを確認する。

```bash
git log --no-merges --format='%H|%s|%b<<<END>>>' <適用開始点>..HEAD
```

`auto sync ` で始まる subject を除外した各 commit について、body に
`^Event: ` を含む行が存在することを確認する。

### 8.2 event_id の実在確認

記載された event_id が Event Ledger に実在することを確認する。

```bash
python -c "import sqlite3;c=sqlite3.connect('file:data/mocka_events.db?mode=ro',uri=True);print(c.execute('select event_id,title from events where event_id=?',('<event_id>',)).fetchall())"
```

### 8.3 逆引きの成立確認

commit ハッシュを起点に Event へ到達できることを、以下の 2 経路のいずれかで確認する。

- message 経路: commit body の `Event:` 行 (本 Policy が新設する経路)
- 機械経路: イベント description の `commit_sha=<hash>` (2.1、自動 commit 用)

本 Policy は検知ツールの実装を強制しない。上記確認を監査プロトコルへ組み込むことを
要求する運用規約である。

## 9. Rationale

MoCKA において commit は変更の実行結果であり、Event Ledger は変更の制度的記録である。
両者が片方向にしか結ばれていない状態では、git 履歴を起点とした監査が成立しない。

追跡性は、記録が存在することではなく、任意の起点から到達できることで測られる。
Event 側から commit へ到達できても、commit 側から Event へ到達できなければ、
git 履歴を一次資料とする第三者監査は間接経路に依存する。

本 Policy は、人手起点 commit という、機械的記録点が存在しない区間に限って
記載義務を課すことで、この非対称を解消する。自動 commit を対象外とするのは、
そこには既に構造的な記録点 (commit_sha) が存在するためである。

## 10. History

- 2026-07-31: 初版作成。基準点 commit 7d1302e3e に対する監査
  (AUDIT REPORT E20260731_64716908835df) の Finding [4]
  (commit -> Event の逆引き経路なし、重大度 中) を契機として制定。
  既存コード / DB / Ledger schema の変更なし。過去 commit への遡及なし。

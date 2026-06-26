# MoCKA Relay 拡張機能要件定義書 v1.0

対象TODO: TODO_350（Relay完全リセット）Step2
作成日: 2026-06-26
Status: DRAFT

## 0. 前提・適用範囲

本書はTODO_350のリセット範囲（content.js/background.js/popup.js/relay-logbook.js等）を対象に、
ゼロから再実装する際の要件を定義する。実装と蓄積データ（誤った前提・誤抽出済みデータ）は持ち込まない。

正本フォルダ: `C:\Users\sirok\MoCKA\PlanningCaliber\workshop\Relay_Project\extension\`
（Chrome Secure Preferences実測により確認済み。location=4/unpacked、2026-06-26時点）

## 1. 対象範囲（4機能とファイル担当の対応）

| 機能 | 担当ファイル | 既存実装状況 |
|---|---|---|
| 20ターン警告 | content.js（turnCount監視）+ background.js | 現行ロジックを要件3で再定義 |
| 引き継ぎパケット生成 | content.js（generatePacket, getHandoffBlockRanges） | Step1で新方式（##見出しブロック除外）確定済み・実装済み |
| TODO抽出管理 | relay-logbook.js（新規実装） | 現行のEXTRACT_TODOS経路（content.js: extractTodosFromText）は廃止対象 |
| 新規chat自動注入 | content.js（handleNewChat） | 要件4で再定義 |

## 2. TODO抽出管理の要件（TODO_366確定方針の転記）

relay-logbook.jsとして新規実装する。独自設計は行わず、TODO_366（2026-06-26、きむら博士確認済み）の
確定方針をそのまま要件とする。

### 2.1 抽出と確定の分離（2段構成）
- 自動抽出結果は `status: "draft"` として一時保存する。
- 上限件数を設け、古いdraftは自動破棄する（上限値は実装時にくろこ判断で設定、後日博士確認）。
- 20ターン警告等のタイミングでdraft一覧をユーザーに提示し、選択されたものだけ `status: "active"` に確定する。

### 2.2 UI選別粒度
- デフォルト案: 警告ポップアップでの簡易confirm方式。
- 別案（popup内チェックボックス選択）への変更はくろこ判断で可。

### 2.3 抽出ロジックの改善点（TODO_366で特定された既存欠陥への対応）
- TODO判定パターンは汎用語に依存しすぎないこと（旧Stage4の `TODO_RE` 問題の再発防止）。
- 抽出対象はユーザー発言に限定する方向で設計する（旧Stage2が会話全体=Claude発言含むを対象にしていた逸脱の修正）。

### 2.4 廃止対象
- content.js内の `extractTodosFromText()` と、これを呼び出す `chrome.runtime.onMessage` の
  `EXTRACT_TODOS` ハンドラ（content.js:371-374、saveTodos()含む）は、relay-logbook.js実装後に削除する。
  draft/active分離を経ない直接保存経路を残さない。

### 2.5 context invalidatedガードの標準パターン（2026-06-26 恒久対応より転記）
relay-logbook.jsおよびbackground.jsとの連携部分で `chrome.runtime.sendMessage()` を呼ぶ箇所は、
すべて呼び出し直前に以下のガードを標準パターンとして適用する。タブ未リロードによるcontent.js孤立
コンテキスト時、`.catch()` だけではruntime.lastErrorしか抑制できず、Uncaught Error自体は防げない
ため、送信前のコンテキスト有効性チェックを必須とする。

```js
if (!chrome.runtime?.id) return; // contextが無効なら即終了
chrome.runtime.sendMessage({ ... }).catch(() => {});
```

新規実装時点からこのパターンを全sendMessage箇所に組み込み、「動いてはいるが脆い」状態を作らない。
content.js側の既存3箇所（checkTurnWarning/警告ポップアップOPEN_POPUP/notifySessionStart）には
本パターンを2026-06-26時点で適用済み（E20260627_5756305388b24）。

## 3. 引き継ぎパケット生成・20ターン警告の要件

- 引き継ぎパケットのブロック判定は、Step1で確定した `MoCKA_Relay_handoff_spec_v1.md` 相当の仕様
  （`## 引き継ぎパケット [Relay {plan}]` 見出しによる丸ごとブロック除外、個別文言パターン依存の排除）に
  厳密一致させる。現行 `getHandoffBlockRanges()`（content.js:104-125）の実装方式を踏襲する。
- パケット本文のテンプレート構成（いつ/何を/決定事項/TODO・次のアクション/関連ファイル/重要メモ）は
  現行 `generatePacket()`（content.js:195-229）の構成を維持する。
- 20ターン警告のトリガー条件・表示方式は、現行実装（turnCount監視）を踏襲し、新規実装時に明文化する。

## 4. 新規chat自動注入の要件

- 既存の `handleNewChat()`（content.js:272以降）の動作を要件として明文化する。
- 誤った前提・蓄積データを持ち込まない（chrome.storage.local全クリア後の新規実装とする、Step3対応）。

## 5. 非機能要件（Phase4 Operational Constraints Specification v1.0）

E20260622_149806056acf4にて確定済みの上限値を、実装仕様に組み込む。

- window_size: 1000-10000ms（推奨5000ms baseline）
- slide_step: 100-2000ms
- 変更頻度上限: 10回/hour
- 3回以上の連続変更: cooldown 300s必須
- Relayは時間構造のみ制御可能であり、routing/decision/semantic layerへの干渉は一切不可（invariant）
- 違反時は即時Relay freeze → drift event生成 → Human Gate解除待ちが復旧ルール

## 6. 持ち込まない対象・削除対象データの明記

### 6.1 再実装対象外（ロジックとして引き継がない）
- content.js内の現行 `extractTodosFromText()` / `TODO_PATTERNS`（旧 `RELAY_TODO` パターン等）の抽出ロジック。
- 旧バージョン（v4.1.0系等）の個別文言パターンマッチ方式全般。

### 6.2 削除対象データ（Step3でchrome.storage.localから物理的に削除する対象）
- relay-logbook.js由来のLB_断片（LB_001〜080、2ヶ月分蓄積されたstale data）。
- 6.1の旧ロジックにより生成されたTODOエントリ（draft/active分離を経ずに保存されたもの）。
- テスト中に生成された残骸データ。

6.1と6.2の対応関係: 6.1で「ロジックを引き継がない」と定めた処理が過去に生成したデータが6.2の削除対象であり、
Step2（設計・本書）の「持ち込まない」とStep3（アンインストール+storage削除）の「何を削除するか」は
1対1で対応する。

### 6.3 削除可否が未確定の対象（博士判断待ち、本書の対象外）
- extension\ルートに残存する旧v4.1.0孤立ファイル5点（popup.html/popup.js/relay_search_ui.js/
  sidepanel.html/sidepanel.js）。TODO_350のnoteに記載の通り、削除可否は別途博士判断を要する。

## 7. Step3運用ノート（2026-06-26 恒久対応より追記）

アンインストール＋再インストール作業（Step3-部分②③）の実行後、作業中に開いていた既存タブは
**全てリロードすること**。

背景: アンインストール後に既存タブをリロードしないと、当該タブのcontent.jsが孤立コンテキスト
（拡張機能が無効化されたまま実行され続ける状態）となり、`chrome.runtime.sendMessage()`が
Uncaught Errorを発生させる。これはstorage削除確認（`chrome.storage.local.get(null, console.log)`
の結果が`{}`か否か）の正確性とは無関係の別事象であり、混同しないこと。

次回以降のRelay再インストール作業（および他拡張機能の同種作業）でも、本ノートの手順を踏襲する。

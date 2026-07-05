# Reconnect Tracker v0.1

位置づけ: 本文書は管理用インデックスである。Decision Ledger(判断の履歴)・
Integrity Classification(異常の履歴)とは別に、「修復がどこまで進んでいるか」
だけを追跡する。新しい制度ではない。

正本: `docs/governance/RECONNECT_TRACKER_v0.1.md`(本ファイル)
関連: `data/decisions/decision_ledger.jsonl`(Decision Layer)、
`data/integrity/integrity_classification.jsonl`(Integrity Layer)

---

## 列の定義

| 列 | 意味 |
|---|---|
| layer | どの層/経路の話か |
| status | open(未着手) / partial(部分接続) / closed(接続完了) |
| type | Integrity Classificationの分類(該当する場合) |
| owner | 誰が担当か(TODO番号・Sprint番号・未定等) |
| link | 関連するevent_id・classification_id・decision_id |

---

## 一覧

| layer | status | priority | type | owner | link |
|---|---|---|---|---|---|
| AI Boot Hub | closed | - | - | Done(Phase1) | AI_BOOT_HUB.md |
| Decision Ledger | closed | - | Transfer Failure(解消) | TODO_361 | E20260705_3366248354d05 |
| ChatGPT Read(Context取得) | closed | - | Transfer Failure(解消) | Sprint2 | E20260705_81978131184b6 |
| current_case文脈整合(session紐付け) | partial | 中 | Runtime Divergence(未接続) | Sprint2補正 | E20260705_929557184da2b |
| events.db when_ts整合性 | closed | - | (Axis問題。既存Type適用外だが暫定Synchronization Failureで運用) | 解消済み | IC_20260705_016 |
| Gateway公開経路(Tunnel) | open | 中 | Exposure Failure | TODO_266(外部インフラ依存で停滞中) | - |
| Relay ChatGPT対応 | open | 高 | Transfer Failure | 未着手(外部依存なし、着手可能) | - |
| Integrity Classification基盤 | closed | - | - | Sprint3 | E20260705_235348404a3be |
| lever_essence.json二重化 | open | 低 | Synchronization Failure | 未定 | - |
| GPT_RESTRICTIONS.md陳腐化 | open | 中 | Synchronization Failure | 未定(比較的小さい修正で済む) | - |
| TODO_361成果物②(CLAUDE.md/TODO_154運用ルール追記) | closed | - | Adoption Failure(解消) | TODO_361 | E20260705_236507766f07f |
| TODO_361成果物③(継続的なDecision Ledger記録運用の定着) | closed | - | Adoption Failure(仕組み整備完了、定着は継続観察) | TODO_361 | E20260705_236507766f07f |
| Execution Enforcement Layer(未定義・第4層候補) | open | 中 | System Enforcement Integrity(Layer2、未実装) | 未定(別スコープとして今後判断) | E20260705_5127083436d30 |

---

## 運用ルール

- 新しい接続工事(Sprint)が完了・進行するたびに、該当行のstatusを更新する。
- 行の追加・statusの変更自体も、他のMoCKAコアファイル変更と同様に
  CHANGE_START/CHANGE_DONEで記録する。
- 本表はIntegrity Classification(何が壊れていたかの診断ログ)や
  Decision Ledger(なぜその判断をしたかの記録)を置き換えない。
  あくまで「今どこまで直っているか」の一覧に徹する。

---

## 補足: Execution Integrityの2層構造(2026-07-05発見)

本セッションで、Integrity Classification(Sprint3)の稼働検証時に「ツール実行のstatus:ok報告と
実際のデータ状態が一致しない」事象が発生したことをきっかけに、Execution Integrityには
性質の異なる2層があることが判明した。

- Layer1(Behavioral Integrity): 呼び出し側(人間・AI)がread-back等の手順を実際に守るか。
  CLAUDE.mdの規律追記で対応済み。ただし文書による規律であり、強制はできない。
- Layer2(System Enforcement Integrity): ツール側が書込直後に内部で読み戻しを行い、
  一致しない場合はrejectする等、強制力を持つ機構。**未実装**。

Decision Ledger/Integrity Classification/Reconnect Trackerの3層とは別に、
「Execution Enforcement Layer」として第4層になり得るが、今回は着手せず
別スコープの候補として記録するに留める。

## 改訂履歴

- v0.1(2026-07-05): Reconnection Sprint(Sprint1-3)を踏まえ新規作成。

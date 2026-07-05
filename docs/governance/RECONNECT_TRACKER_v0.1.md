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

| layer | status | type | owner | link |
|---|---|---|---|---|
| AI Boot Hub | closed | - | Done(Phase1) | AI_BOOT_HUB.md |
| Decision Ledger | closed | Transfer Failure(解消) | TODO_361 | E20260705_3366248354d05 |
| ChatGPT Read(Context取得) | closed | Transfer Failure(解消) | Sprint2 | E20260705_81978131184b6 |
| current_case文脈整合(session紐付け) | partial | Runtime Divergence(未接続) | Sprint2補正 | E20260705_929557184da2b |
| events.db when_ts整合性 | open | (Sprint3で正式分類予定) | 未定 | E20260705_049292555d01b |
| Gateway公開経路(Tunnel) | open | Exposure Failure | TODO_266 | - |
| Relay ChatGPT対応 | open | Transfer Failure | 未着手(Sprint4候補) | - |
| Integrity Classification基盤 | closed | - | Sprint3 | E20260705_235348404a3be |
| TODO_361成果物②(CLAUDE.md/TODO_154運用ルール追記) | open | Adoption Failure(再発防止未実施) | TODO_361 | - |
| TODO_361成果物③(継続的なDecision Ledger記録運用の定着) | partial | Adoption Failure(定着未確認) | TODO_361 | - |

---

## 運用ルール

- 新しい接続工事(Sprint)が完了・進行するたびに、該当行のstatusを更新する。
- 行の追加・statusの変更自体も、他のMoCKAコアファイル変更と同様に
  CHANGE_START/CHANGE_DONEで記録する。
- 本表はIntegrity Classification(何が壊れていたかの診断ログ)や
  Decision Ledger(なぜその判断をしたかの記録)を置き換えない。
  あくまで「今どこまで直っているか」の一覧に徹する。

---

## 改訂履歴

- v0.1(2026-07-05): Reconnection Sprint(Sprint1-3)を踏まえ新規作成。

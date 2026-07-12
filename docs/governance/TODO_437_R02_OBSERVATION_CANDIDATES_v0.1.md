# TODO_437 R02 Observation Candidates v0.1

作成: Claude-sonnet-5(くろこ) / 2026-07-10 / 未検証Evidence Candidateの整理のみ・
v0.1への統合は行っていない

## 1. 位置づけ

- 正本: `TODO_437_R02_REMEDIATION_PLAN_v0.1.md`(変更なし)。
- `TODO_437_R02_REMEDIATION_PLAN_v0.2.md`(作成者表記: Codex)は
  Parallel Investigation Draftとして扱い、正本化・v0.1への統合・差し替えの
  いずれも行わない。
- 本文書は、v0.2固有の追加情報を「検証待ちEvidence Candidate」として抽出・
  整理するものであり、それ自体がv0.1の一部になるものではない。
- Git commit・Decision Ledger追加・正本更新は、Human Gate承認後まで行わない。

## 2. Observation Candidates(v0.2由来、抽出のみ)

### 2.1 追加数値データ

v0.2の「証拠一覧」に記載されていた、本セッション(v0.1)側では未取得の数値。

| 項目 | v0.2記載値 | 検証状態 |
|---|---|---|
| DBサイズ(mocka_events.db) | 82,026,496 bytes | 未検証 |
| events件数 | 15,312 | 未検証 |
| claude_sessions件数 | 94,408 | 未検証 |
| WAL | 有効(と記載) | 未検証(本セッションのWAL確認は別時点・別手段によるものであり、この値そのものの再現確認は行っていない) |
| busy_timeout | 5000ms(と記載) | 未検証(本セッションも同値を別途確認済みだが、v0.2記載値そのものとしては未検証扱いとする) |

### 2.2 H2仮説: mocka_mcp_server側auto_log()によるclaude_sessions INSERTと別commit

- 内容: GATE(`/api/gate/event`)側の`events` INSERT・`event_signatures` INSERT・
  `events` UPDATEに加え、mocka_mcp_server.py側の`auto_log()`が同一SQLite
  (`mocka_events.db`と想定)へ**別途`claude_sessions`テーブルへINSERTし、
  別commitを発生させている**との指摘。
- 位置づけ: 未説明の約3.7秒(GATE単体2.3秒+Context 3関数0.03秒とE2E全体6.0秒の差)の
  新しい候補要因となり得る。本セッションのH1(process_event()内サブステップ)・
  H2(events.dbロック競合)のいずれにも、`auto_log()`の別commit構造という着眼点は
  明示的に含まれていなかった。
- 検証状態: 未検証。`auto_log()`の実装(`mocka_mcp_server.py`内)が実際に別途
  commitを発生させているか、それがどのDBファイルに対してか(`mocka_events.db`か
  `claude_sessions`用の別ファイルか)を含め、コード確認・実測のいずれも
  本セッションでは行っていない。

### 2.3 Legacy Path Risk: data/events.dbへの旧経路書込み残存疑惑

- 内容: 正規経路は`data/mocka_events.db`であるところ、`interface/router.py`に
  旧`data/events.db`への直接書込み実装が残存しているとの指摘。
- 位置づけ: 恒久対策候補B(events.db書き込み経路の見直し)を検討する際、
  正規経路と旧経路を混同しないための前提情報になり得る。
- 検証状態: 未検証。`interface/router.py`の該当箇所の存在・現状の呼び出され方
  (実際に稼働経路として使われているか、死んだコードか)のいずれも、本セッションでは
  コード確認を行っていない。

## 3. 検証状態一覧(まとめ)

上記2.1〜2.3のすべての項目は、本文書作成時点で **未検証** である。
検証(コード確認・実測)は、Human Gateの調査実施承認(R02 Remediation Plan v0.1
13章 境界1、または本文書由来の項目として別途整理される境界)を得た後に行う。

## 4. 統合方針

- v0.2の内容をv0.1へ統合するか、v0.1を差し替えるか、あるいは統合しないかは、
  Human Gateの判断に委ねる。
- 本文書(Observation Candidates)自体もv0.1の一部ではなく、独立した
  検証待ち資料として扱う。
- 上記いずれの統合作業も、本文書作成時点では実施していない。

## 5. 並行生成経緯の確認事項

- CodexとClaude(本セッション)が同一のTODO_437 R02設計タスクに対し、ほぼ同時刻
  (2026-07-10 16:51頃)に並行して文書を生成した経緯は、本セッションでは未確認である。
- 確認が必要な論点: (a)意図的な多重調査(複数AIへ同一タスクを並行発注し、
  結果を比較検討する運用)であったか、(b)誤発注(同一タスクが重複して
  割り当てられた事故)であったか。
- 本項目は実装判断とは独立した運用上の確認事項として記録するに留め、
  本セッションでは原因の特定・修正のいずれも行わない。

## 6. TODO_437_R02_PARALLEL_DRAFT_AUDIT_v0.1.mdとの整合性確認

- `TODO_437_R02_PARALLEL_DRAFT_AUDIT_v0.1.md`(Detection/Classification/
  Content Review/Decision Boundary)にて、v0.2固有の追加事項として既に
  同一の3項目(追加数値データ・H2仮説・Legacy Path Risk)を記載済みであることを
  確認した。本文書は、それらを「Observation Candidate」として、検証状態を
  明示した形で改めて整理したものであり、内容に矛盾はない。
- 分類(正本ではない/並行生成ドラフト/Human Gate未承認)についても、
  Parallel Draft Auditの記載と本文書の位置づけ(1章)は一致している。

## 7. 現在の状態(最終)

- v0.1 = 正本
- v0.2 = Parallel Investigation Draft(保持、削除せず)
- 本文書記載の追加情報 = 検証待ちEvidence Candidate(未検証)
- Git commit・Decision Ledger追加・正本更新: 未実施(Human Gate承認待ち)

# External Harness Change Recording Policy

- Policy ID: GOV-PROC-EHCR-001
- Status: Active
- Date: 2026-07-13
- Owner approval: きむら博士
- Decision: DC_20260713_002
- Related: DC_20260713_001, E20260713_399246918d43e
- Classification: Governance Integrity Enhancement (not an incident fix)

## 1. Purpose

Claude Code等の外部ハーネス経由でMoCKA内ファイルを変更した場合、
MoCKAのPostToolUse自動記録(CHANGE_DONE)が保証されないケースがある。

根本原因:
PostToolUseフックは MoCKAプロジェクトスコープの
`.claude/settings.local.json` に定義されている
(matcher: Write/Edit/NotebookEdit/MultiEdit/Bash/PowerShell
-> `tools/mocka_auto_record.py`)。
外部ハーネスのプロジェクトルートが MoCKA配下でない場合
(例: ルートが C:\Users\sirok)、このプロジェクトスコープの
フックがロードされず、自動CHANGE_DONEが発火しない。

これはサーバー(localhost:5002)停止とは別種の穴であり、
既存CLAUDE.mdの「5002 down時のみ手動補完」規定では捕捉できない。

本Policyは、変更記録ライフサイクル(CHANGE_START -> 変更 -> CHANGE_DONE)
の完全性・再現可能性・監査可能性を、外部ハーネス利用時にも保証する。

## 2. Scope

### 2.1 監査対象 (MoCKAリポジトリ内部のみ)

- ルート: C:\Users\sirok\MoCKA
- 対象パス例: docs/ governance/ core/ interface/ PlanningCaliber/ runtime/
  その他 Git管理対象ファイル

### 2.2 監査対象外

- core/governance/keys/ 配下
- *.pem / *.key
- 秘密鍵・認証情報
- MoCKA外ディレクトリ・ユーザー領域・OS全体

理由: 秘密情報アクセス防止、および無差別記録によるevents.db汚染防止。

## 3. Policy

外部ハーネス経由でMoCKA内ファイルを変更した場合、変更完了時に
以下の整合を必ず確認する。自動CHANGE_DONEが保証できない環境では、
手動CHANGE_DONE記録を必須とする。

1. Git diff確認 (変更内容が意図通りか)
2. CHANGE_START存在確認
3. CHANGE_DONE存在確認 (欠落していれば手動補完を必須とする)
4. Decision / Event整合確認

## 4. Prohibited

- Global filesystem hook(全ファイル変更を無差別記録するhook)の追加は禁止。
  理由: MoCKA外変更によるevents.db汚染防止。
- 本Policyを根拠に app.py / API / ポート契約 / events.db仕様 を変更すること。
  本件はコード修正案件ではなく運用規約案件である。

## 5. Operational Flow

### 5.1 通常 (MoCKAプロジェクトスコープ内で作業する場合)

1. CHANGE_START を記録する
2. 変更を実施する
3. git diff で変更内容を確認する
4. CHANGE_DONE を記録する (PostToolUseフックによる自動記録を含む)
5. commit する

### 5.2 外部ハーネス経由の場合

1. 変更完了後、自動CHANGE_DONEの有無を確認する
   (確認手段例: tools/auto_record.log の当日エントリ、
    events.db 上の該当CHANGE_DONE検索)
2. 欠落していれば、手動で mocka_write_event(CHANGE_DONE ...) を記録し補完する
3. CHANGE_START と CHANGE_DONE が対になっていることを監査記録として残す
4. commit する

## 6. Verification Guidance

監査時 (または起動時レビュー時) に、以下を確認できる状態を維持する。

- 当該セッションで PostToolUse自動記録フックが有効か
  (無効なら 5.2 の手動補完フローを適用)
- 直近のCHANGE_STARTに対応するCHANGE_DONEが存在するか
- 未記録の変更(記録なきファイル変更)が存在しないか

本Policyは検知ツールの実装を強制しない。運用規約として、上記の
確認を監査プロトコルに組み込むことを要求する。

## 7. Rationale

MoCKAの三要素(Structure / Record / Verification)のうち Record を、
実行主体(ハーネス)が MoCKA本体か外部AIエージェントかに依存せず
成立させる。将来 Claude Code / Copilot / 他AIエージェントが増えても、
記録なき変更が生じない運用境界を確立する。

## 8. History

- 2026-07-13: 初版作成。DC_20260713_001(Port Contract Verification)監査中に
  外部ハーネスでのCHANGE_DONE欠落(手動補完: E20260713_27845093724e3)を
  検出したことを契機に、恒久規約として制定 (DC_20260713_002)。

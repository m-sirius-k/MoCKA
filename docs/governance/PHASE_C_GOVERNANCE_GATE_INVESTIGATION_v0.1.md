# Phase C: Governance Boundary 実装調査 v0.1

作成: Claude-sonnet-5(くろこ) / 2026-07-08 / Step1(既存コード読み取り)+Step2(呼び出しグラフ)+
Step3(境界設計オプション提示)のみ。実装(Step4以降)は一切行っていない。

対象: `anchor_update.py`・`/audit/seal`・`execution_governance`(GL7)・
TODO_411/412/413関連コード・seal artifact生成フロー・呼び出し元一覧。

## 1. anchor_update.py 全体構造

`scripts/ledger/anchor_update.py`(108行)は以下の直線的な5段処理:

```
1. git add -A + check_staged_files(禁止パターン: TestProfile/, Default/Cache/,
   chrome_debug/, .env, secrets/) + mocka_git_safe_commit(push=False)
2. get_summary_hash(commit) : governance/calc_summary_hash.py をsubprocess実行
3. anchor_record.json 2箇所(governance/, mocka-governance-kernel/anchors/)を
   sealed_summary_hash/external_ref/sealed_at_utcで更新
4. anchor_record自体をmocka_git_safe_commit経由でcommit
5. verify_all.py をsubprocess実行して検証
```

自前の承認ゲート(human_gate_override_event_id等)は無く、`mocka_git_safe_commit()`の
Core System File除外がこの経路で唯一の"止める"機構である。

## 2. 呼び出しグラフ(実際にanchor_update.pyを起動する経路)

`grep -rl "anchor_update"`で12ファイルがヒットしたが、実際にsubprocess/import経由で
**起動する**ものは以下のみ(他はパス文字列としての言及・レジストリ記載のみ):

| 呼び出し元 | 現状 | 生死 |
|---|---|---|
| `app.py:auto_audit_loop()`(50EVT分岐) | PENDING記録のみ、**呼び出さない**(TODO_370/371是正済み) | 生きているが無効化済み |
| `app.py:auto_audit_loop()`(daily分岐) | PENDING記録のみ、**呼び出さない**(TODO_427是正済み) | 生きているが無効化済み |
| `watchdog_mocka.py:try_daily_seal()` | PENDING記録のみ、**呼び出さない**(TODO_427是正済み) | 生きているが無効化済み |
| `app.py:2150 /audit/seal`(`audit_seal_manual`) | **無条件でsubprocess実行** | **生きていて無防備** |
| `app_bak_0501.py`(3箇所) | 無条件でsubprocess実行するコードが残存 | **死んでいる**(どのbat/ps1/pyからも起動されない、最終commit 2026-05-01、静的バックアップファイル) |

`governance/mocka_git_safe_commit.py`・`make_movement_map.py`・
`reality_sync/sync_registry.py`・`structural/repository_indexer.py`は
パス文字列としての参照(Core System File登録・マップ生成・レジストリ記載)のみで、
実行はしていない。

**結論**: 現時点で実際にHuman Gateを経ずにanchor_update.pyを起動できる生きた経路は
`/audit/seal`の1箇所のみ(前回監査Gap-1と同じ)。`app_bak_0501.py`は死んだコードだが、
同種のコードパターンが複製されて残存している事実として記録する(Low)。

## 3. execution_governance.py(GL7)の実態

`structural/execution_governance.py`(246行)は、`dry_run()`(git status差分の構築)・
`check_abort_conditions()`(FORBIDDEN_EXECUTIONS/ABORT_CONDITIONS判定)・
`pre_execution_check()`(Dry Run+Abort条件でApprovalResultを返す)という
機械的検査ロジックを持つ、比較的作り込まれたゲートエンジンである。

**重要な発見**: `record_execution()`・`record_file_change()`(TODO_144が定める
CHANGE_START/CHANGE_DONE相当のフック)は、実体が

```python
def record_execution(self, action, result) -> None:
    self._last_execution = {"action": action, "result": result}
```

のように**インスタンス属性へ保持するだけで永続化を一切行わない**(docstring自身が
"永続化は呼び出し側のEvent記録に委ねる"と明記)。つまりGL7側のCHANGE_START/CHANGE_DONE
フックは、それ単体では記録として機能しない空の入れ物であり、呼び出し側が別途
`mocka_write_event`を呼ばない限り何も残らない。

**呼び出しグラフ**: `ExecutionGovernanceEngine`を実際にimportしているのは
`structural/consensus.py`・`structural/governance_pipeline.py`・
`structural/knowledge_mass.py`の3ファイルのみ。このうち`governance_pipeline.py`は
`mocka_mcp_server.py`から呼ばれており、**MCPツール実行経路には接続されている**。
しかし`anchor_update.py`・`mocka_git_safe_commit.py`・`app.py`のauto_audit_loop・
`/audit/seal`のいずれもGL7を一切importしていない。

**結論**: MoCKAには現在、構造的に独立した2つの"ゲート"が並立している。

```
Gate A: mocka_git_safe_commit.py の is_core_system_file()
        -> 実際のgit commit(seal含む)を止める唯一の機構
        -> パス除外のみ、Dry Run・Abort条件・承認確認なし

Gate B: structural/execution_governance.py(GL7)
        -> Dry Run・FORBIDDEN_EXECUTIONS・ABORT_CONDITIONSの判定ロジックを保有
        -> MCPツール実行経路(governance_pipeline.py経由)にのみ接続
        -> seal/commitパイプラインには未接続
```

GL7-UNENFORCED-CONDITIONS-BUG(TODO一次データに既存)が指す"安全条件3点が
実行経路に未接続"は、この2つのGateが統合されていないという同一の構造問題を
指していると考えられる。

## 4. Decision 1(Single Governance Gate)への設計オプション

| 案 | 内容 | 長所 | 短所 |
|---|---|---|---|
| 案1 | `mocka_git_safe_commit()`側にGate Bの判定ロジック(Dry Run/Abort条件)を統合し、
呼び出し元非依存の一元的ゲートにする | 既存の唯一の実行時ゲート(Gate A)を強化するだけで済み、
影響範囲が`mocka_git_safe_commit()`利用箇所に限定される | Gate B(GL7)との重複コードが残る、
概念が2箇所に分散したまま |
| 案2 | GL7(`ExecutionGovernanceEngine.pre_execution_check()`)を
`anchor_update.py`・`/audit/seal`から呼ぶよう配線し直す | 既存の作り込まれたロジックを
再利用でき、GL7-UNENFORCED-CONDITIONS-BUGも同時に解消する | GL7は現状MCPツール実行という
別文脈向けに設計されており、seal/commit文脈への転用に伴う挙動確認が必要(scope指定の
意味がseal文脈でも成立するか等) |
| 案3 | 新規に薄いGoverning Gate層(Decision Unit相当)を作り、Gate A/Bの両方をラップする | 将来の
呼び出し元追加にも一貫して対応できる、CHANGE_START/DONEの永続化も新設できる | 実装コストが
最大、既存2ゲートとの責務重複の整理が必要 |

## 5. Decision 2(CHANGE_START/DONE, Decision Unit)関連の追加事実

- 提案されている`Decision Unit`(change_id/actor/scope/started_at/completed_at/
  artifact_hash/seal_hash)は、既存の`record_execution`/`record_file_change`が
  非永続の空フックであるため、**そのまま呼ぶだけでは要件を満たさない**。
  永続化先(events.db経由のevent_bufferか、専用ファイルか)を新規に設計する必要がある。
- 一方、`decision_ledger.jsonl`(`data/decisions/`)は既に`decision_id`/`approved_by`/
  `approved_at`等の類似スキーマを持つ実運用中のPrimaryデータであり、Decision Unitとの
  役割重複(別スキーマの新設か、既存decision_ledgerの拡張か)を整理する必要がある。

## 6. Decision 3(anchor_update.py呼び出し制限)関連の追加事実

現状の生きた呼び出し元は`/audit/seal`の1箇所のみであるため、"Governance Gate経由のみ
許可"への変更は影響範囲が限定的(この1エンドポイントの改修のみ)。ただし
`app_bak_0501.py`のような静的バックアップファイルに同型の無防備なコードが
既に複製されている実例が確認されたため、将来的に同種のコピーが作られるリスク
(TODO_354 extension_canonical_paths確認漏れと同型)への備えとして、`anchor_update.py`
自体にimport時点でのガード(呼び出し元検証)を持たせる案も選択肢に含めるべきである。

## 7. 実装前チェック(指示事項、未実施・事実確認のみ)

- 既存seal履歴との互換性: `anchor_record.json`のスキーマ(anchor_type/external_ref/
  sealed_summary_hash/sealed_at_utc)は変更を想定していないため、Gate統合後も
  この出力形式を維持すれば後方互換は保てる見込み
- 過去artifactの再検証可能性: `calc_summary_hash.py`・`verify_all.py`はGate統合の
  影響を受けない独立スクリプトであり、再検証経路自体への影響はないと見られる
- CI影響: 本監査ではCI(GitHub Actions等)からのanchor_update.py起動は確認されていない
  (TODO_411の既存調査結果を再確認、変化なし)
- Core System File保護対象確認: `anchor_update.py`自体・`app.py`は共に
  `mocka_git_safe_commit.py`のCore System File登録済み(commit時に自動除外・
  Human Gate対象)。`/audit/seal`を含む`app.py`本体の変更は今後もCore System File
  Human Gate対象となる
- Human Gate対象範囲確認: 上記の通り、Gate統合の実装自体がCore System File変更に
  該当するため、実装着手時はhuman_gate_override_event_id相当の明示承認手続きが
  別途必要になる

## Non Actions(本調査で行っていないこと)

- `anchor_update.py`・`/audit/seal`・`execution_governance.py`のコード変更
- Gate統合の最小実装
- Decision Unit永続化スキーマの新設
- commit(本文書自体もHuman Gate裁定後にcommit判断)

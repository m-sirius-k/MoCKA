# CORE_CHANGE_PENDING_RECORD_v1.0

作成: Claude-sonnet-5(くろこ) / 2026-07-08 / Phase C-4(Deferred Human Gate Protocol、縮小版)着手時点の記録

対象: `app.py`(Core System File、`CORE_SYSTEM_FILES_EXTRA`)。working tree上に未commitの差分として存在。

## 変更目的

`/audit/seal`(MANUAL_SEAL)エンドポイントを、`scripts/ledger/anchor_update.py`を
直接subprocess実行する方式から、`governance/seal_governance_gate.py`の
`SealGovernanceGate`経由に変更する(Phase C-2、TODO_411/412/413 Gap-1是正)。
GL7(`structural/execution_governance.py`)のdry run評価を経由させ、abort判定が
出た場合は`anchor_update.py`を呼ばないようにする。`anchor_update.py`自体の
ロジックは無変更。

## diff hash

- 変更前HEAD: `28b8b8026de8001e4b17d21523d67ffc9f6b2c5f`(現在のHEAD、app.py関連の直近commitは`3bc80842edf70539c155697432e5f3580bc506ee`)
- 変更後working tree app.pyの内容ハッシュ: `sha256:82c74cc060e2ac47ea5a193f43a48f4d0a001635a977ca651fd8e9c35841e284`
- diff統計: `app.py | 36 ++++++++++++++++++++++++------------`(24 insertions, 12 deletions)
- diff範囲: `audit_seal_manual()`関数(旧`app.py:2149`付近)のみ。他関数への影響なし。

## 検証結果

- `governance/seal_governance_gate.py`は`tests/test_seal_governance_gate.py`
  (Test A/B/C)で既にsandbox検証済み(実`anchor_update.py`は呼ばれない設計)。
- `governance/shadow_seal_adapter.py`(Phase C-3)で、`anchor_update.py`の
  CLI契約(`COMMIT:`/`SUMMARY_HASH:`マーカー)・anchor schema・hash算出ロジックの
  互換性を、実行を伴わずに確認済み。
- app.py側の差分自体(`/audit/seal`ルートの呼び出し先変更)は、実HTTPリクエストに
  よる本番動作確認までは未実施。

## 待機理由

`app.py`は`governance/mocka_git_safe_commit.py`の`CORE_SYSTEM_FILES_EXTRA`に
該当するため、`human_gate_override_event_id`を伴わない限りcommit対象から
除外される仕様(TODO_347)。現時点でこのevent_idを発行する経路は、
実在性・正当性が検証されない`app.py`側`/decision/approve`系(無検証)以外に
存在しない。したがって、正規のHuman Gate機構(`phi_os/human_gate.py`、
event-sourced状態機械、現状HTTP未マウント)からの承認event発行が確定するまで、
本ファイルはcommitしない。

## 必要なHuman Gate

- 承認主体: きむら博士本人
- 承認手段: 現状未確定(TODO_429「governance/human_gate_cli.pyの制度整理」の
  裁定対象。Phase1B 3.1-3.3も未確定)
- 本Recordは`governance/human_gate_continuity.py`の`HumanGateContinuity.defer()`が
  生成する`WAITING_FOR_HUMAN_GATE`状態のPending Decision Unitと対応する
  (`change_scope=["app.py"]`)。Pending Decision Unit自体の永続化先は
  `data/decisions/pending_decision_units.jsonl`(gitignore対象、ローカル記録のみ)。

## 本Recordのcommit境界

本文書(`docs/governance/CORE_CHANGE_PENDING_RECORD_v1.0.md`)自体はCore System
Fileではないためcommit可能。ただし対象である`app.py`は本Recordとは別に、
TODO_429の裁定を経た正規のHuman Gate承認eventが発行されるまでcommitしない。

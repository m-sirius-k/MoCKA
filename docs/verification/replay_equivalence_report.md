# Replay Equivalence Report (Phase4 Step3 / Phase5基準線)

Status: PASS
Date: 2026-06-22

## 検証内容

`relay/replay_engine.py`(v1, full event scan)と`relay/replay_engine_v2.py`
(v2, snapshot+delta)の最終state(final_state)が、複数のイベント数・snapshot
境界条件において完全一致することを確認した。

## ケース一覧

| ケース | n (event数) | snapshot使用 | 結果 |
|---|---|---|---|
| zero_events | 0 | No | PASS (match) |
| below_threshold | 10 | No | PASS (match) |
| exact_boundary | 100 | Yes | PASS (match) |
| one_past_boundary | 101 | Yes | PASS (match) |
| multi_snapshot | 250 | Yes | PASS (match) |
| multi_snapshot_exact | 300 | Yes | PASS (match) |
| large_delta | 399 | Yes | PASS (match) |

全7ケースでv1.final_state == v2.final_stateが成立(AssertionError無し)。

## Replay Mode一致検証(Phase4 Step4)

`relay/replay_router.py`の3モード(LEGACY/EXPERIMENTAL/HYBRID)について、
150件ingest後にfinal_stateが全モードで一致することを確認した。

| Replay Mode | final_state一致 |
|---|---|
| LEGACY (v1) | PASS (基準) |
| EXPERIMENTAL (v2) | PASS (LEGACYと一致) |
| HYBRID (v1+v2比較) | PASS (match=True) |

## Replay Audit(Phase4.5)

`relay/replay_audit.py` ReplayAuditLogによるhybrid replay監査において:

- 正常系: match=Trueが正しく記録される。
- 異常系(意図的なv1/v2不一致を注入したテスト): match=Falseの検知、
  `REPLAY_DRIFT`の出力、audit_logへのmatch=False記録を確認。

## 結論

Replayの「実行・比較・記録」の整合性は、境界値・複数snapshot・大きいdelta
を含む全条件下で保証されている。これがPhase5(Time API以降)着手の前提条件
として満たされた。

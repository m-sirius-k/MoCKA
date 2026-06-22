# Change Plan v1 — INCIDENT_IMPORT_APP_SIDE_EFFECT

Status: DRAFT（Core System File Change Approval審査用。コード変更は未実施）
Date: 2026-06-23
対象インシデント: `docs/incidents/INCIDENT_IMPORT_APP_SIDE_EFFECT.md`
責務契約: `docs/governance/runtime_boundary_v1.md`
規約: `docs/governance/import_safety_rule_v1.md`

## 対象

`app.py`

## 追加（2件）

| 関数 | 責務 | 契約文書 |
|---|---|---|
| `initialize_runtime()` | DB初期化・Registry読込・Config検証 | `runtime_boundary_v1.md` |
| `start_background_loops()` | daemon Thread/Timer起動 | `runtime_boundary_v1.md` |

呼び出し順序: `initialize_runtime()` → `start_background_loops()` →
`app.run(...)`。いずれも`if __name__ == "__main__":`ブロック内でのみ
呼び出す。

## 移設（5件）

| # | 対象 | 現在位置 | 移設先 |
|---|---|---|---|
| 1 | `auto_process_loop`の`.start()` | `app.py:136-137` | `start_background_loops()`内 |
| 3 | `auto_audit_loop`の`.start()` | `app.py:2111-2112` | `start_background_loops()`内 |
| 4 | `init_audit_db()`呼出 | `app.py:2587-2593` | `initialize_runtime()`内 |
| 5 | `_start_overdue_loop`の`.start()` | `app.py:2695` | `start_background_loops()`内 |
| 6 | `_guidelines_loop`の`.start()` | `app.py:2823-2824` | `start_background_loops()`内 |

各対象関数自体のロジックは変更しない（呼出位置の移動のみ）。

## 削除（1件）

| # | 対象 | 現在位置 | 削除理由 |
|---|---|---|---|
| 2 | `essence_auto_updater`動的import+`start_essence_auto_loop()`呼出 | `app.py:140-148` | `MoCKA-START.bat`経由の独立プロセス起動と責務重複。機能自体は`MoCKA-START.bat`経路で継続するため、app.py内の冗長な起動経路のみ削除する |

## 変更しない

- `essence_auto_updater.py`本体（`interface/`配下）
- `init_audit_db()`本体・`cross_audit.py`のロジック
- `auto_process_loop`/`auto_audit_loop`/`_start_overdue_loop`/`_guidelines_loop`
  各関数の内部処理

## 影響範囲

- `python app.py`での直接起動・`MoCKA-START.bat`経由の起動には影響しない
  （`__main__`ブロックは従来通り実行される）。
- `import app`のみを行う操作（検証・テスト目的）からは副作用が消える
  （これが本変更の意図する効果）。
- 副次効果: `_load_pqueue()`未定義の競合状態（`INCIDENT_IMPORT_APP_SIDE_EFFECT.md`
  3.再現手順 参照）も解消される。

## ロールバック方法

1コミットのrevertで完了する。各対象関数の定義自体は削除せず残す
（#2の`essence_auto_updater`起動コードのみ実体を削除するため、その箇所は
revert時に再追加が必要）。

## 完了条件

- [x] `initialize_runtime()`/`start_background_loops()`の実装
- [x] 5件の移設完了（#1/#3/#4/#5/#6）
- [x] #2の削除完了
- [x] `runtime_boundary_v1.md`の責務契約との整合確認
- [x] `phi_os/tests/`回帰テスト実施（104件PASS、既存と同数、回帰なし）
- [x] UTF-8検証（BOM無し、issues無し）
- [x] CHANGE_DONE記録（event_id: `E20260623_148286805b00a`）
- [ ] Regression Test → Incident Closure（実機運用確認後にクローズ）

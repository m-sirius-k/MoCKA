# Phase C Core Change Request v1.0

作成: Claude-sonnet-5(くろこ) / 2026-07-08 / Human Gate提出用。app.py commit実行前の変更概要。

対象ファイル: `app.py`(Core System File、`governance/mocka_git_safe_commit.py`の
`CORE_SYSTEM_FILES_EXTRA`に登録済み)

## 変更理由

TODO_411_412_413_AUTO_SEAL_BOUNDARY_AUDIT_v1.0.mdで確認したGap-1
(`/audit/seal`エンドポイントがTODO_370/371/427と対称的なHuman Gate是正の
対象から漏れており、POST即座に`anchor_update.py`を無条件subprocess実行していた)
を是正する。既存のGate A(`mocka_git_safe_commit.py`)に加え、GL7
(`structural/execution_governance.py`)のDry Run/Abort判定を経由する
`SealGovernanceGate`(`governance/seal_governance_gate.py`、既にcommit済み
c26064cad)を、MANUAL_SEAL経路の入口として接続する。

## 変更範囲

`app.py`の`audit_seal_manual()`関数のみ(2150行目付近、`/audit/seal`ルート)。
差分は24行追加・12行削除。

### Before

```python
@app.route("/audit/seal", methods=["POST"])
def audit_seal_manual():
    import subprocess
    from pathlib import Path as _P
    seal_script = _P(str(ROOT_DIR)) / "scripts" / "ledger" / "anchor_update.py"
    seal_log    = _P(r"C:\Users\sirok\MoCKA\data\seal_log.json")
    if seal_script.exists():
        result = subprocess.run(
            ["python", str(seal_script), "MANUAL_SEAL_" + datetime.now().strftime("%Y%m%d_%H%M%S")],
            cwd=str(ROOT_DIR), capture_output=True, text=True, timeout=30
        )
        log = {"sealed_at": datetime.now().isoformat(), "result": result.stdout[:200]}
        seal_log.write_text(__import__("json").dumps(log, ensure_ascii=False), encoding="utf-8")
        return jsonify({"status": "ok", "sealed_at": log["sealed_at"]})
    return jsonify({"status": "error", "message": "seal script not found"})
```

### After

```python
@app.route("/audit/seal", methods=["POST"])
def audit_seal_manual():
    from pathlib import Path as _P
    import sys as _sys
    _sys.path.insert(0, str(_P(str(ROOT_DIR)) / "governance"))
    from seal_governance_gate import SealGovernanceGate
    seal_log = _P(r"C:\Users\sirok\MoCKA\data\seal_log.json")
    message = "MANUAL_SEAL_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    gate_result = SealGovernanceGate().execute(message=message)
    log = {
        "sealed_at": datetime.now().isoformat(),
        "approved": gate_result.approved,
        "execution_id": gate_result.execution_id,
        "aborts": gate_result.aborts,
        "result": gate_result.seal_stdout[:200] if gate_result.approved else gate_result.reason,
    }
    seal_log.write_text(__import__("json").dumps(log, ensure_ascii=False), encoding="utf-8")
    if not gate_result.approved:
        return jsonify({
            "status": "blocked", "reason": gate_result.reason,
            "aborts": gate_result.aborts, "execution_id": gate_result.execution_id,
        }), 403
    return jsonify({"status": "ok", "sealed_at": log["sealed_at"], "execution_id": gate_result.execution_id})
```

`anchor_update.py`のsubprocess呼び出し自体は`SealGovernanceGate._run_seal_script()`
(`governance/seal_governance_gate.py`)内に移設されただけであり、呼び出しコマンド
(`["python", str(SEAL_SCRIPT), message]`、`cwd=repo_root`)は変更していない。
新たに追加されたのはGL7の`pre_execution_check()`呼び出しとDecision Unit記録のみで、
`anchor_update.py`が呼ばれた場合の挙動(git add/commit/hash計算/anchor更新)は
Before/Afterで完全に同一。

## Core System File該当理由

`governance/mocka_git_safe_commit.py`の`CORE_SYSTEM_FILES_EXTRA`に`"app.py"`が
明示登録されている(2026-06-25 TODO_347/362関連事故対応、AUTO_SEAL_50EVT等の
自動処理がHuman Gateを迂回して`app.py`を無承認で変更確定させた事故の再発防止措置)。
本変更もこの保護対象に該当するため、`mocka_git_safe_commit()`は無条件で
`app.py`をstaging除外する(`human_gate_override_event_id`明示指定時のみ除外解除)。

## TODO_427/Pack1形式との比較

過去の同種commit(`3bc80842e`、2026-07-08)は以下の形式でCore System File除外を
解除していた:

```
AUTO_SEAL Pack1: 日次seal系Human Gate化(TODO_427/IC_20260708_001是正、DC_20260708_004承認)

[HUMAN_GATE_OVERRIDE:Phase1_chat_approval] event_id=E20260708_1825441396032 core_files=app.py
```

`event_id=E20260708_1825441396032`は、事前に`mocka_write_event`で記録済みの
正規イベントを指す(Phase1=チャット承認方式、2026-07-02きむら博士裁定の運用)。
本変更をcommitする際も同一形式(`[HUMAN_GATE_OVERRIDE:Phase1_chat_approval]
event_id=<正規発行event_id> core_files=app.py`)を踏襲する予定だが、
本セッションはMCPセッション不通のため`mocka_write_event`による正規event_id発行が
できない。したがって本Change Requestの時点ではevent_id欄は空欄のまま提出し、
MCP復旧後に正規発行したevent_idを埋めてからcommitする(Phase C-3 Step 2/3参照)。

## Rollback方針

- `app.py`側の変更は`audit_seal_manual()`関数1つに閉じており、Before側のコードへ
  `git checkout`(またはこの1関数のみの手動復元)で即座に戻せる
- `governance/seal_governance_gate.py`(既にcommit済み、c26064cad)を削除・
  未importにすれば、`app.py`側の変更を戻さなくても機能的には旧経路と同等の
  安全側(常にImportError->500エラー、無条件実行ではない)に倒れる
- `anchor_update.py`・`mocka_git_safe_commit.py`・`calc_summary_hash.py`は
  一切変更していないため、これらのRollbackは不要
- 万一`/audit/seal`が本番稼働中に問題を起こした場合、Flaskプロセスの再起動
  (既存の`restart_mocka.bat`)でBefore版のコードに戻せる(commit前の現状は
  working tree差分でしかないため、`git stash`または`git checkout -- app.py`
  でも即時復元可能)

## 検証結果

`tests/test_seal_governance_gate.py`(commit c26064cad、3件PASS):

| Test | 内容 | 結果 |
|---|---|---|
| Test A | GL7承認 -> モックseal実行(1回のみ) -> Decision Unit記録 | PASS |
| Test B | GL7 Abort -> モックseal実行0回 -> abort記録のみ | PASS |
| Test C | 実`app.py`・`anchor_update.py`・`decision_ledger.jsonl`・`anchor_record.json`が
  テスト前後で無変更(SHA256一致) | PASS |

`python -m py_compile app.py`による構文検証: OK。実サーバーでの動作確認
(実際に`/audit/seal`へPOSTして統合動作を見る)は、既に本番app.py(PID稼働中)への
影響を避けるため未実施。

## 現在の状態

`app.py`の変更はworking tree上の差分としてのみ存在し、commitしていない。
MCP復旧後、正規`event_id`発行 -> 本Change Request文書のevent_id欄更新 ->
`mocka_git_safe_commit(paths=['app.py'], human_gate_override_event_id=<event_id>)`
の順でcommitする(Phase C-3 Step 2/3)。

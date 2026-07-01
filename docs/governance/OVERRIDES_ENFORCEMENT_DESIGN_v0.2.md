# OVERRIDES Enforcement設計 v0.2

Artifact Type: Governance Document
Completion Evidence: 本ファイル（OVERRIDES_ENFORCEMENT_DESIGN_v0.2.md）
Verification Status: 設計完了・実装未着手・きむら博士承認待ち
Evidence Location: C:/Users/sirok/MoCKA/docs/governance/OVERRIDES_ENFORCEMENT_DESIGN_v0.2.md

---

## v0.1からの引き継ぎ（変更なし）

v0.1（TODO_401）で確定した3層構造は本設計においても変更しない。

### 3層強制保証構造（固定）

- layer_1_evaluation: Decision Policy（evaluate_override）がoverride_requestedの評価・採否決定を行う
- layer_2_constraint: event_gateがDecision Evidenceの存在を確認し、存在しない裁定結果をリジェクトする（内容検査は行わない）。DBトリガー: trg_detect_override_evidence_gap（audit_trigger.pyパターン踏襲）
- layer_3_audit: audit_triggerが裁定履歴の監査可能性を保証する記録層として機能する

### human_gate連動（固定）

機械的に解決できない競合（OVERRIDES同士の競合等）は、既存human_gate.pyのsubmit()を再利用してHuman Gateへ差し戻す。gate_type="decision_policy"で通常のGateと区別する。新規Gateは作成しない。

### カナリアテスト（固定）

テスト名: test_override_evidence_gap_is_rejected_by_event_gate
実行方式: CI定期実行（A案・常駐監視プロセス不採用）
根拠: TODO_371正本不信パターン・TODO_396 human_gate_bp死蔵と同じリスクを再発させないため

---

## v0.2 追加：カナリアテストCI実行担保

v0.1で「カナリアテストをCI定期実行する」と決定したが、「CI自体が止まっていないか」を担保する仕組みが未設計であった。v0.2ではこの「カナリアのカナリア」を設計する。

### CIワークフロー新設（軽量ガード型）

`C:/Users/sirok/MoCKA/.github/workflows/canary_overrides.yml` を新規作成する。

```yaml
name: Canary - OVERRIDES Enforcement

on:
  schedule:
    - cron: "0 3 * * 1"   # 毎週月曜3:00 UTC（週次定期実行）
  workflow_dispatch:

env:
  PYTHONIOENCODING: utf-8
  PYTHONUTF8: "1"

jobs:
  canary:
    name: canary-overrides
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r requirements-test.txt

      - name: Run canary test
        run: python -X utf8 -m pytest tests/governance/test_overrides_enforcement.py::test_override_evidence_gap_is_rejected_by_event_gate -v
        env:
          PYTHONIOENCODING: utf-8
          PYTHONUTF8: "1"

      - name: Record last run timestamp
        if: always()
        run: |
          python -X utf8 -c "
import json, datetime, pathlib, os
result = 'PASS' if os.environ.get('CI_STEP_OUTCOME', 'success') == 'success' else 'FAIL'
record = {
    'last_run': datetime.datetime.utcnow().isoformat() + 'Z',
    'result': result,
    'run_id': os.environ.get('GITHUB_RUN_ID', 'local'),
    'workflow': 'canary_overrides.yml'
}
p = pathlib.Path('data/tic/canary_overrides_last_run.json')
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
print('Recorded:', record)
"
        env:
          CI_STEP_OUTCOME: ${{ steps.canary_test.outcome }}

      - name: Upload last run record
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: canary-overrides-last-run
          path: data/tic/canary_overrides_last_run.json
          retention-days: 90
```

CIパターン選択の詳細は後述「CI YAMLパターン選択根拠」を参照。

---

### ①カナリアテスト最終実行日時の記録

#### 記録場所

`C:/Users/sirok/MoCKA/data/tic/canary_overrides_last_run.json`

このファイルはCIの「Record last run timestamp」ステップが毎回上書きする。内容例:

```json
{
  "last_run": "2026-07-07T03:42:17Z",
  "result": "PASS",
  "run_id": "12345678",
  "workflow": "canary_overrides.yml"
}
```

#### CIからmocka_write_eventへの記録方式

CIはインターネット上のGitHub Actions runnerで実行されるため、ローカルのmocka_mcp_server.py（localhost:5002）には直達できない。代わりに以下の2段階方式を採る：

**段階1（CI側）**: CIの「Record last run timestamp」ステップが`data/tic/canary_overrides_last_run.json`を更新してコミットする。

具体的には、CIジョブの末尾に以下のステップを追加する：

```yaml
      - name: Commit last run record
        if: always()
        run: |
          git config user.email "ci@mocka-bot"
          git config user.name "MoCKA CI Bot"
          git add data/tic/canary_overrides_last_run.json
          git diff --cached --quiet || git commit -m "ci: canary_overrides last_run update [skip ci]"
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**段階2（ローカルhook側）**: MoCKA-START.batが起動するhealth_check.pyの中でこのJSONファイルを読み、7日検知ロジック（後述）が起動したとき、health_check.pyのwrite_event()関数（interface/health_check.py 469行目）経由でmocka_write_eventへ記録する。

これにより「CI実行記録の書き込み」はCI側のgit commitとして残り、「MoCKA制度記録（mocka_write_event）」はhealth_check.py統合側で担う、という役割分離が成立する。

---

### ②実行停止の検知（カナリアのカナリア）

#### 統合先: interface/health_check.py

`C:/Users/sirok/MoCKA/interface/health_check.py`のHEALTH_CHECKSディクショナリに新規チェック項目として追加する。既存の`check_phi_os_audit()`（237行目）と同じパターンで実装する。

#### HEALTH_CHECKSへの追加内容

`HEALTH_CHECKS`ディクショナリ（54行目〜143行目）の末尾に以下のエントリを追加する：

```python
    "canary_overrides_liveness": {
        "method": "canary_overrides_liveness",
        "stale_days": 7,
        "last_run_path": "C:/Users/sirok/MoCKA/data/tic/canary_overrides_last_run.json",
        "optional": False,
        "risk": "カナリアテストのCI実行が停止すると、OVERRIDES enforcement強制制御の形骸化を検知できなくなる（カナリアのカナリア）",
        "opportunity": "最終実行日時の7日監視でCI死蔵を構造的に防止できる",
        "beta_candidate": "governance_integrity",
    },
```

#### チェック実装関数

`check_phi_os_audit()`（237行目）の直後に以下の関数を追加する：

```python
def check_canary_overrides_liveness(cfg: dict) -> tuple:
    """
    カナリアテスト（test_override_evidence_gap_is_rejected_by_event_gate）
    の最終CI実行日時を確認し、stale_days日以上更新がない場合にFAILを返す。
    （カナリアのカナリア。TODO_401 v0.2設計）
    """
    import datetime
    path = pathlib.Path(cfg["last_run_path"])
    stale_days = cfg.get("stale_days", 7)

    if not path.exists():
        return False, (
            f"canary_overrides_last_run.json が存在しません。"
            f"カナリアテストCIが一度も実行されていない可能性があります。"
        )

    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"last_run.json 読み込みエラー: {e}"

    last_run_str = record.get("last_run", "")
    if not last_run_str:
        return False, "last_run フィールドが不在"

    try:
        last_run = datetime.datetime.fromisoformat(last_run_str.replace("Z", "+00:00"))
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        elapsed = now_utc - last_run
    except Exception as e:
        return False, f"last_run パース失敗: {e}"

    result = record.get("result", "UNKNOWN")
    elapsed_days = elapsed.total_seconds() / 86400

    if elapsed_days > stale_days:
        return False, (
            f"カナリアテスト最終実行から {elapsed_days:.1f} 日経過（閾値: {stale_days} 日）"
            f" | last_run: {last_run_str} | result: {result}"
        )

    return True, (
        f"OK ({elapsed_days:.1f} 日前に実行済み) | result: {result} | run_id: {record.get('run_id', '?')}"
    )
```

#### run_check()への分岐追加

`run_check()`関数（432行目）のif-elif連鎖に以下を追加する（`elif method == "auth_key_drive":` の直後）：

```python
        elif method == "canary_overrides_liveness":
            ok, detail = check_canary_overrides_liveness(cfg)
```

#### 7日検知時のmocka_write_event連動

health_check.pyのメイン処理（539行目 run()関数内）では、FAIL時に`write_event()`を呼ぶ既存パス（611〜614行目）が`canary_overrides_liveness`のFAILを自動的に拾う。追加実装は不要。

#### pathlib importの確認

health_check.pyの冒頭インポートに`pathlib`が含まれているか確認する（現行コードでは`from pathlib import Path`のみ）。`check_canary_overrides_liveness()`内で`pathlib.Path`ではなく`Path`を使うよう実装する。

---

### CI YAMLパターン選択根拠

#### 選択: 軽量ガード型（mocka_guard.ymlパターン）

mocka_guard.ymlはDockerを使わず、ubuntu-latest上でシェルコマンドのみを実行する最小構成（checkout + 検証コマンド）。

本カナリアテストの実行対象である`test_override_evidence_gap_is_rejected_by_event_gate`は：
- SQLiteへのアクセスをモックするユニットテストとして設計できる（本番DBへの接続不要）
- Dockerコンテナは不要（Pythonとpip installで完結）
- ubuntu-latestのみで十分（ubuntu/windowsマトリクスはmocka_regression.ymlの再現試験のため必要だが、本カナリアはロジック検証が目的）

Docker対応型（phios_regression.ymlパターン）はdocker compose buildが必要で、起動時間が長くCI費用も増す。PHI-OSのようにブラウザ（Puppeteer）を伴う試験ではないため、Docker対応型の採用根拠がない。

よって軽量ガード型を選択する。

---

## 残存リスク・未解決事項

### R1: CIがデフォルトブランチ以外で止まっていても検知できない

`canary_overrides.yml`はmainブランチの`data/tic/canary_overrides_last_run.json`を読む。featureブランチでCIが壊れていてもmainへのpushが止まれば検知できる。ただしfork環境・draft PRでのみ壊れている場合は検知できない（許容リスク）。

### R2: mocka_write_event記録はCI実行成功時のみ

health_check.pyのwrite_event()が記録するのはcheck_canary_overrides_livenessがFAILした時のみ（既存パターン踏襲）。「正常にCI実行された」というPASS記録は30回に1回のHEALTH_OKに含まれるのみ（HEALTH_OK_INTERVAL=30の既存制約）。週次CIに対してローカルhealth_checkが30回に1回しかPASS記録しない問題は残存するが、FAIL（7日超過）は必ず記録されるため、監査目的には十分と判断する。

### R3: canary_overrides_last_run.jsonのgit commit設計が未確定

CIからのgit push（段階1）はGITHUB_TOKENの書き込み権限設定が必要。リポジトリのSettings > Actions > Workflow permissions で「Read and write permissions」が有効になっていることを実装前に確認する。

### R4: カナリアテスト本体（test_override_evidence_gap_is_rejected_by_event_gate）が未実装

本設計はカナリアテストのCI実行担保の仕組みを設計しているが、テスト本体のコードは本設計の範囲外（v0.1から引き継ぎ）。テスト実装が未完了のまま本設計を実装しても、CIは「テストが存在しない」エラーで止まる。実装順序: テスト実装 -> canary_overrides.yml追加 -> health_check.py統合 の順が正しい。

---

## 完了条件チェックリスト

- [x] カナリアテストCI実行担保の仕組みが明記されている（canary_overrides.yml設計 + 2段階記録方式）
- [x] 新規常駐監視プロセスを作っていない（health_check.pyへの統合のみ）
- [x] mocka_write_event記録の仕組みが具体的に記述されている（health_check.pyの既存write_event()パスを利用）
- [x] 7日検知の仕組みが既存プロセスへの統合として記述されている（check_canary_overrides_liveness()をHEALTH_CHECKSに追加）
- [x] Artifact Type: Governance Document
- [x] Completion Evidence: 本ファイル作成済み
- [ ] きむら博士の承認（未完了 -> awaiting_approval）

## Implementation Note

This document specifies the operational design. Implementation SHALL proceed only after the canary test has been implemented and verified. Design approval does not imply implementation completion.

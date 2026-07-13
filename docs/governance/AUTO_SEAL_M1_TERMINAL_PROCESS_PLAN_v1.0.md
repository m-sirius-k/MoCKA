# AUTO_SEAL M1 Terminal Process Plan v1.0

- Document ID: GOV-PLAN-ASM1-001
- Status: Planning + Phase 2 approval materials (implementation NOT approved)
- Date: 2026-07-13
- Author: Claude-opus-4-8 (くろこ)
- Approval owner: きむら博士
- Parent: DC_20260713_003 (Model B Approved), DC_20260713_004 (M1 Proposal submitted)
- Plan decision: DC_20260713_005
- Refs: docs/governance/AUTO_SEAL_BOUNDARY_DESIGN_v1.0.md,
  docs/governance/AUTO_SEAL_M1_IMPLEMENTATION_PROPOSAL_v1.0.md

本書は M1 を「設計」から「動く実働経路」まで運ぶための工程設計である。
各Phase境界で停止し、次工程の承認を取得する。本書作成時点で コード変更・
Migration実行・Seal経路変更は一切行っていない。以下の提案コードは承認用の
レビュー資料であり、実ファイルとしては未作成である。

目的(博士方針): 制度を完成させることではなく、動く経路を1本作り、その実績から
幅を拡張すること。よって M1 は最小実働経路に限定する。

---

## 1. 終端条件と工程全体像

終端条件: AUTO_SEAL Model B が、設計ではなく実働経路として成立した状態
(approved_by=human を伴う Decision承認から seal 監査レコードが実際に生成・検証される)。

| Phase | 内容 | 成果物 | 承認境界(停止点) |
|---|---|---|---|
| 1 | M1 Implementation Proposal + 工程設計 | 本書 + GOV-PROP-ASM1-001 | 本書提示で停止 |
| 2 | Implementation Approval待ち | 実装対象/差分/リスク/テスト/検証項目の提示 | 実装承認取得まで停止(現在ここ) |
| 3 | Implementation | 新規2ファイル(sandbox限定) | 実装完了+記録で停止 |
| 4 | Runtime Debug | テスト実行結果・検証ログ | 検証成功で停止 |
| 5 | Migration | 旧経路保持のまま接続、Migration記録 | Migration記録+Rollback可で停止 |
| 6 | Final Verification | Repo/Artifact/Seal/Audit/Ledger/履歴の確認 | 終端確認 |

各Phaseは前Phaseの承認取得後にのみ着手する。現在は Phase 1 完了・Phase 2(承認待ち)。

---

## 2. Phase 1 完全化

### 2.1 現行 Architecture (調査結果)

- seal実処理: scripts/ledger/anchor_update.py (frozen)。commit -> summary_hash -> anchor_record更新。
- 統治層: governance/seal_governance_gate.py (GL7評価 -> anchor_update.py -> Decision Unit記録)。
  現状 approved_by="system:seal_governance_gate" (GL7自動、人間不在) = RB-2。
- 台帳: data/decisions/decision_ledger.jsonl (75行)。標準行キー: decision_id/title/context/
  alternatives/decision/rationale/impact/related_events/related_documents/approved_by/approved_at/
  supersedes/superseded_by/status。SealGovernanceGate行は execution_id/artifact_hash/seal_hash 等を追加。

### 2.2 変更対象ファイル (M1)

新規追加(実装時に作成):
1. governance/seal_auth_record.py
2. tests/test_seal_auth_record.py

無変更(触らない): seal_governance_gate.py / anchor_update.py / app.py / API / port /
本番 data/decisions/decision_ledger.jsonl / events.db仕様。

### 2.3 影響範囲分析

- M1追加フィールドのうち decision_id / approved_by は既存行に存在(流用、衝突なし)。
- seal_request_id / requester / approval_timestamp / artifact_hash / seal_hash / pending_ref は
  標準行に非在の新フィールド。既存行に無くても有効(optional parse)なので後方互換。
- M1は sandbox/一時パスのみ書込み、本番台帳へ書かない。既存 seal経路からの呼出も無し。
  よって本番 seal/anchor/台帳/verify_all への影響は無い。

### 2.4 Before / After 設計 (提案コード = レビュー資料。実ファイル未作成)

Before: Auth Modelを書ける/検証できるモジュールは存在しない。approved_by=human の強制も
verify関数も無い。

After(提案): 以下2ファイルを新規追加する。既存コードには一切接続しない。

proposed: governance/seal_auth_record.py
```python
"""
governance/seal_auth_record.py
AUTO_SEAL M1: Auth Model record layer (Model B / DC_20260713_003).
sandbox/一時パス限定。既存seal経路(SealGovernanceGate/anchor_update.py)には接続しない(M2)。
本番 decision_ledger.jsonl には書かない。記録層のみ(seal/hash/commitは呼ばない)。
"""
import json
from pathlib import Path

REQUIRED_FIELDS = (
    "seal_request_id", "requester", "decision_id",
    "approved_by", "approval_timestamp",
)

def write_auth_record(ledger_path, record):
    """Auth拡張レコードを append-only JSONL で追記する(sandbox限定)。"""
    p = Path(ledger_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record

def read_auth_records(ledger_path):
    """JSONL全行を読む。旧行(拡張なし)も新行も同様に parse する(後方互換)。"""
    p = Path(ledger_path)
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out

def verify_auth_record(record):
    """
    Model B成立条件を判定する。強制(実seal停止)はしない(M2)。
    Returns (ok: bool, reasons: list[str])。
    """
    reasons = []
    for k in REQUIRED_FIELDS:
        if not record.get(k):
            reasons.append("missing:" + k)
    approved_by = str(record.get("approved_by", ""))
    if approved_by == "" or approved_by.startswith("system"):
        reasons.append("approved_by_not_human")
    requester = str(record.get("requester", ""))
    if requester.startswith("system:auto_audit_loop") and not record.get("pending_ref"):
        reasons.append("missing:pending_ref")
    return (len(reasons) == 0, reasons)

def find_duplicate_request_ids(ledger_path):
    """seal_request_id の重複を検出する(一意性チェック)。"""
    ids = [r.get("seal_request_id") for r in read_auth_records(ledger_path)
           if r.get("seal_request_id")]
    return sorted({i for i in ids if ids.count(i) > 1})
```

proposed: tests/test_seal_auth_record.py
```python
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "governance"))
from seal_auth_record import (  # noqa: E402
    write_auth_record, read_auth_records, verify_auth_record, find_duplicate_request_ids,
)

def _rec(**kw):
    base = {
        "seal_request_id": "SR_1", "requester": "kimura_hakase",
        "decision_id": "DC_x", "approved_by": "kimura_hakase",
        "approval_timestamp": "2026-07-13T00:00:00Z",
    }
    base.update(kw)
    return base

def test_backward_compat(tmp_path):
    p = tmp_path / "l.jsonl"
    write_auth_record(p, {"decision_id": "DC_old", "approved_by": "kimura_hakase"})
    write_auth_record(p, _rec())
    assert len(read_auth_records(p)) == 2

def test_approved_by_system_rejected():
    ok, r = verify_auth_record(_rec(approved_by="system:seal_governance_gate"))
    assert not ok and "approved_by_not_human" in r

def test_approved_by_human_ok():
    ok, r = verify_auth_record(_rec())
    assert ok and r == []

def test_missing_required():
    ok, r = verify_auth_record(_rec(seal_request_id=""))
    assert not ok and "missing:seal_request_id" in r

def test_pending_ref_required_for_auto():
    ok, r = verify_auth_record(_rec(requester="system:auto_audit_loop"))
    assert not ok and "missing:pending_ref" in r
    ok2, _ = verify_auth_record(
        _rec(requester="system:auto_audit_loop", pending_ref="AUTO_SEAL_PENDING_x"))
    assert ok2

def test_duplicate_request_ids(tmp_path):
    p = tmp_path / "l.jsonl"
    write_auth_record(p, _rec(seal_request_id="SR_dup"))
    write_auth_record(p, _rec(seal_request_id="SR_dup"))
    assert "SR_dup" in find_duplicate_request_ids(p)

def test_jsonl_integrity(tmp_path):
    p = tmp_path / "l.jsonl"
    write_auth_record(p, _rec())
    txt = p.read_text(encoding="utf-8")
    assert txt.endswith("\n")
    for line in txt.splitlines():
        json.loads(line)
```

### 2.5 Rollback 設計

- M1は新規ファイル追加のみ・本番データ無変更のため、Rollback = 当該2ファイルの削除で完全復旧。
- 本番 seal/anchor/台帳を変更しないため、戻し作業(データ復元)は不要。
- 実装commitは単独commitとし、revert 1回で取り消せる粒度に保つ。

### 2.6 実装後 Debug 計画 (Phase 4で実行)

| ID | テスト | 期待 |
|---|---|---|
| T1 | 後方互換(旧行+新行混在読取) | 両方parse成功 |
| T2 | approved_by=system/空 | verify不合格(approved_by_not_human) |
| T3 | approved_by=human | verify合格 |
| T4 | 必須欠落 | 各 missing:<field> で不合格 |
| T5 | seal_request_id重複 | find_duplicate_request_ids が検出 |
| T6 | AUTO由来で pending_ref欠落 | missing:pending_ref |
| T7 | append-only/JSON整合 | 有効JSONL・既存行不変 |

実行: pytest tests/test_seal_auth_record.py + 手動 write->read->verify 1件。

---

## 3. Phase 2 承認資料 (Implementation Approval Gate)

以下を提示する。承認なしに Phase 3(実装)へ進まない。

- 実装対象: 第2.2章の新規2ファイルのみ。既存seal経路は無変更。
- 変更差分: 第2.4章の proposed code(新規追加=全行 add、既存ファイルの diff は無し)。
- リスク:
  | リスク | 度合 | 緩和 |
  |---|---|---|
  | 既存台帳への誤書込 | 低 | M1はsandbox/一時パスのみ。本番ledger未接続 |
  | 既存 parse 破壊 | 低 | 追加フィールドは optional。旧行はそのまま読める(T1) |
  | verify のhuman判定漏れ | 中 | approved_by=system/空を明示不合格(T2)。テストで固定 |
  | scope 過拡大 | 低 | 強制・Gate接続はM2へ分離(Non Goals) |
- テスト計画: 第2.6章 T1-T7。
- 検証項目(Phase 4 Runtime Debug対応): 正常Decision Seal(verify合格) / approved_by検証 /
  Gate拒否動作(verifyがreasons返却) / 既存経路互換(本番未接続=無影響) /
  Anchor整合・Hash整合・Ledger整合(M1はsandboxのみのため本番side-effectなしを確認)。

Phase 4以降で扱う Anchor/Hash/Ledger の実整合検証は、M2(既存経路接続)以降で本番経路に
関わるため、M1単独では「本番へ影響しないこと」の確認に留める。

---

## 4. Phase 3-6 の工程定義 (各承認境界)

- Phase 3 Implementation: 承認取得後のみ。最小実働経路優先・既存Seal互換維持・変更範囲限定・
  各変更をCHANGE_START/CHANGE_DONEで記録。完了後停止。
- Phase 4 Runtime Debug: T1-T7実行 + 手動検証。approved_by検証・Gate拒否・既存経路互換・
  Anchor/Hash/Ledger整合(M1はsandbox、本番無影響の確認)。成功で停止。
- Phase 5 Migration: 検証成功後のみ。Rollback可能・旧経路保持・Migration記録作成。
  (M1のMigrationは「新モジュールを既存経路から呼べる状態にする準備」までを指し、実際の
   既存Gate接続=RB-2是正はM2 Proposalとして別承認。ここでも旧経路は保持する。)
- Phase 6 Final Verification: Repository状態 / Artifact整合 / Seal状態 / Audit記録 /
  Decision Ledger / 変更履歴 を確認。終端条件(Model Bが実働経路として成立)を判定。

---

## 5. Non Goals / 現時点の停止宣言

- 本書ではコードを実ファイルへ適用しない(提案コードはレビュー資料)。
- Phase 3以降は各Phaseの承認取得までは着手しない。
- 既存 SealGovernanceGate への接続・approved_by=human の強制・本番台帳書込は M1本体では行わず、
  M2 以降の別承認とする。
- app.py / API / port / events.db仕様 / anchor_update.py は全工程を通じて無変更(frozen)。

現時点の状態: Phase 1完了 / Phase 2 承認待ち(停止中)。Phase 3実装は きむら博士の実装承認後にのみ着手する。

---

## 6. History

- 2026-07-13: 初版(v1.0)。DC_20260713_003(Model B Approved)/DC_20260713_004(M1 Proposal)に基づき、
  終端(動く実働経路)までのPhase 1-6工程を承認境界付きで設計。Phase 1完全化(Before/After提案コード・
  影響範囲・Rollback・Debug計画)とPhase 2承認資料を提示。コード変更・Migration実行・Seal経路変更なし
  (DC_20260713_005)。

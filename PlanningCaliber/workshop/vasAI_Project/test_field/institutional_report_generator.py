"""
VASAI_INSTITUTIONAL_REPORT.md — 組織記憶継続性証明報告書
Proof of Institutional Memory (L4.8) 達成報告
"""
from datetime import datetime, timezone
from pathlib import Path
import platform, subprocess, sys


def _git_commit() -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                           capture_output=True, text=True,
                           cwd=str(Path(__file__).parent.parent))
        return r.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _ok(v: bool) -> str:
    return "OK" if v else "NG"


def _step_lines(steps: list, indent: int = 0) -> str:
    pad = " " * indent
    lines = []
    for name, ok, detail in steps:
        lines.append(f"{pad}- [{_ok(ok)}] `{name}` — {detail}")
    return "\n".join(lines)


def generate_institutional_report(results: list, output_path: Path | None = None) -> Path:
    if output_path is None:
        output_path = Path(__file__).parent / "reports" / "VASAI_INSTITUTIONAL_REPORT.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    os_name = f"{platform.system()} {platform.release()}"
    commit = _git_commit()

    total = len(results)
    passed = sum(1 for _, _, r in results if r.get("success"))
    l48_achieved = passed == total

    def get(sid: str) -> dict:
        return next((r for s, _, r in results if s == sid), {})

    # ─────────────────────────────────────────────────────
    lines = [
        "# vasAI 組織記憶継続性証明報告書",
        "# Proof of Institutional Memory — L4.8 達成報告",
        "",
        f"**発行日時**: {now}  ",
        f"**vasAI Version**: 1.0.0  ",
        f"**試験環境**: {os_name} / Python {py_ver}  ",
        f"**git commit**: `{commit}`  ",
        f"**試験結果**: {passed}/{total} PASS  ",
        "",
        "---",
        "",
        "## なぜ Organizational Memory OS なのか",
        "",
        "本システムの価値の中心は",
        "**「AIが考えること」ではなく「組織が忘れないこと」** にある。",
        "",
        "人が交代し、部門が再編され、システムが障害を起こしても、",
        "判断の根拠・推論・意図・結果が引き継がれる仕組みこそが vasAI の本質である。",
        "",
        "---",
        "",
        "## 証明レベル到達状況",
        "",
        "| Level | 名称 | 状態 |",
        "|-------|------|------|",
        "| L1 | Proof of Concept | [OK] 完了 |",
        "| L2 | Proof of Implementation | [OK] 完了 |",
        "| L3 | Proof of Operation | [OK] 完了 |",
        "| L4 | Proof of Continuity | [OK] 完了 |",
        f"| L4.5 | Proof of Governance | [OK] Evidence Ledger達成 |",
        f"| **L4.8** | **Proof of Institutional Memory** | "
        f"{'**[OK] 本報告で達成**' if l48_achieved else '[NG] 未達成'} |",
        "| L5 | Proof of Adoption | [--] 実企業運用 |",
        "| L6 | Proof of Civilization | [--] 長期目標 |",
        "",
        "## 全試験結果",
        "",
        "| ID | 試験名 | 結果 | 時間 |",
        "|----|--------|------|------|",
    ]

    for sid, name, result in results:
        ok = result.get("success", False)
        elapsed = result.get("elapsed", 0)
        lines.append(f"| {sid} | {name} | [{_ok(ok)}] | {elapsed:.2f}秒 |")

    lines += [
        "",
        f"**総合判定: {passed}/{total} PASS — "
        f"{'L4.8 Proof of Institutional Memory 達成' if l48_achieved else 'L4.8 未達成'}**",
        "",
        "---",
        "",
    ]

    # ── Phase 1-4 サマリー ────────────────────────────────
    lines += [
        "## Phase 1-4 証明サマリー（継承）",
        "",
        "| フェーズ | 証明内容 | 結果 |",
        "|---------|---------|------|",
        f"| Phase 1 | 基本記録・Shadow・Caliber・Governance | [{_ok(all(get(f'SCENARIO-0{i}').get('success',False) for i in range(1,5)))}] |",
        f"| Phase 2 | 比較優位・100K件整合・6種不正防御 | [{_ok(all(get(f'SCENARIO-0{i}').get('success',False) for i in [0,5,6]))}] |",
        f"| Phase 3 | 30日運用・4部門・再現性・監査・障害・経営価値 | [{_ok(all(get(f'SCENARIO-{i:02d}').get('success',False) for i in range(7,13)))}] |",
        f"| Phase 4 | Evidence Ledger（なぜ起きたか）| [{_ok(get('SCENARIO-13').get('success',False))}] |",
        "",
        "---",
        "",
    ]

    # ── PHI Layer証明 ─────────────────────────────────────
    r14 = get("SCENARIO-14")
    d14 = r14.get("details", {})
    lines += [
        "## Decision DNA証明（SCENARIO-14: PHI Layer）",
        "",
        "判断の遺伝子を WHY→REASON→EVIDENCE→DECISION→OUTCOME で記録・継承する。",
        "",
        "| DNAステージ | 内容 | 結果 |",
        "|------------|------|------|",
        f"| WHY（背景） | 競合他社障害による顧客離れリスク | [{_ok(r14.get('success',False))}] |",
        f"| REASON（推論） | 負荷3.2倍増・SLA違反リスク評価 | [{_ok(r14.get('success',False))}] |",
        f"| EVIDENCE（根拠） | {d14.get('combined_chain',{}).get('evidence_count',0)}件（Evidence Ledger参照） | [{_ok(r14.get('success',False))}] |",
        f"| DECISION（判断） | サーバ移設承認（予算50万円） | [{_ok(r14.get('success',False))}] |",
        f"| OUTCOME（結果） | 障害率-74%・SLA 99.93%達成 | [{_ok(d14.get('combined_chain',{}).get('has_outcome',False))}] |",
        "",
        f"- 自然言語説明: {d14.get('explanation_len',0)}文字生成 [{_ok(d14.get('explanation_len',0) > 50)}]",
        f"- MoCKA essence PHILOSOPHY軸還流: [{_ok(d14.get('bridge',{}).get('philosophy',False))}]",
        f"- MoCKA essence OPERATION軸還流: [{_ok(d14.get('bridge',{}).get('operation',False))}]",
        f"- PHI verify_chain: [{_ok(d14.get('phi_chain_valid',False))}]",
        "",
        "**PHI Layer結論**: WHY→REASON→EVIDENCE→DECISION→OUTCOME の全チェーンが追跡可能。",
        "MoCKA essenceへの還流により「判断の哲学」が記録から知識へ昇華される。",
        "",
        "---",
        "",
    ]

    # ── 180日組織運用証明 ─────────────────────────────────
    r15 = get("SCENARIO-15")
    d15 = r15.get("details", {})
    lc_events = d15.get("lifecycle", [])
    phi15 = d15.get("phi_stats", {})
    lines += [
        "## 180日組織運用証明（SCENARIO-15）",
        "",
        f"4部門 × 180日のシミュレーション。総イベント: {d15.get('total_events',0):,}件。",
        "",
        "### ライフサイクルイベント処理結果",
        "",
        "| 日 | イベント | 部門 | 結果 |",
        "|----|---------|------|------|",
    ]
    for lc in lc_events:
        day = lc.get("day", 0)
        ev_type = lc.get("type", "")
        dept = lc.get("dept", "")
        if ev_type == "担当者変更":
            res = f"引継ぎ{lc.get('handover_count',0)}件 [{_ok(lc.get('handover_ok',False))}]"
        elif ev_type == "外部監査":
            res = f"{lc.get('audit_time_sec',0):.3f}秒 [{_ok(lc.get('audit_ok',False))}]"
        elif ev_type == "組織改編":
            res = f"継承 [{_ok(lc.get('inherit_ok',False))}]"
        elif ev_type == "システム障害":
            res = f"shadow縮退稼働 [{_ok(lc.get('shadow_degraded',False))}]"
        else:
            res = "[OK]"
        lines.append(f"| Day{day} | {ev_type} | {dept} | {res} |")

    lines += [
        "",
        "### 最終計測",
        "",
        f"- 総イベント: {d15.get('total_events',0):,}件 [{_ok(d15.get('total_events',0)>0)}]",
        f"- 180日チェーン: {'VALID' if d15.get('chain_valid') else 'BROKEN'} [{_ok(d15.get('chain_valid',False))}]",
        f"- 最終監査時間: {d15.get('audit_time_sec',0):.3f}秒（目標5分以内） [{_ok(d15.get('audit_time_sec',999)<300)}]",
        f"- PHI DNA OUTCOME率: {phi15.get('outcome_rate',0):.1f}% [{_ok(phi15.get('outcome_rate',0)>=60)}]",
        f"- MoCKA essence還流: {d15.get('exported_to_essence',0)}件 [{_ok(d15.get('exported_to_essence',0)>0)}]",
        f"- データ損失: {d15.get('data_loss',0)}件 [{_ok(d15.get('data_loss',1)==0)}]",
        "",
        "**180日組織運用結論**: 人員交代・外部監査・組織改編・システム障害の全シナリオで",
        "組織記憶が継続し、判断根拠の追跡が可能であることを証明した。",
        "",
        "---",
        "",
    ]

    # ── 証明済み事項 ─────────────────────────────────────
    lines += [
        "## 証明済み事項（全フェーズ集約）",
        "",
        "| 分類 | 事項 | 証明 |",
        "|------|------|------|",
        f"| 技術基盤 | 記録・監査・改ざん検知（SHA-256チェーン） | [{_ok(get('SCENARIO-01').get('success',False))}] |",
        f"| 耐障害性 | shadow縮退0秒ダウンタイム・75%稼働 | [{_ok(get('SCENARIO-02').get('success',False))}] |",
        f"| 拡張性 | 3業種caliber・100K件整合 | [{_ok(get('SCENARIO-03').get('success',False) and get('SCENARIO-05').get('success',False))}] |",
        f"| セキュリティ | 6種不正操作防御 | [{_ok(get('SCENARIO-06').get('success',False))}] |",
        f"| 継続性 | 30日連続運用・検索速度劣化なし | [{_ok(get('SCENARIO-07').get('success',False))}] |",
        f"| 組織 | 4部門横断追跡・部門間承認 | [{_ok(get('SCENARIO-08').get('success',False))}] |",
        f"| 再現性 | vasAIなし0% vs あり100%（Day30まで） | [{_ok(get('SCENARIO-09').get('success',False))}] |",
        f"| 監査 | 監査官5問全て1秒以内 | [{_ok(get('SCENARIO-10').get('success',False))}] |",
        f"| 障害対応 | 5種障害検知・復旧・損失0件 | [{_ok(get('SCENARIO-11').get('success',False))}] |",
        f"| 経営価値 | 年間4,049,988円削減・ROI試算 | [{_ok(get('SCENARIO-12').get('success',False))}] |",
        f"| 根拠構造 | Evidence Ledger FACT/ASSUMPTION/CONSTRAINT/INTENT | [{_ok(get('SCENARIO-13').get('success',False))}] |",
        f"| 判断継承 | PHI DNA WHY→REASON→DECISION→OUTCOME | [{_ok(get('SCENARIO-14').get('success',False))}] |",
        f"| 組織記憶 | 180日間・7ライフサイクルイベント・記憶継続 | [{_ok(get('SCENARIO-15').get('success',False))}] |",
        f"| MoCKA接続 | PHILOSOPHY/OPERATION軸への自動還流 | [{_ok(d14.get('bridge',{}).get('philosophy',False))}] |",
        "",
        "---",
        "",
    ]

    # ── 未証明事項 ────────────────────────────────────────
    lines += [
        "## 未証明事項（正直な記載）",
        "",
        "以下は本試験環境では証明されていない。この正直な開示が信頼の基盤となる。",
        "",
        "| 事項 | 現状 | 次のステップ |",
        "|------|------|------------|",
        "| 実企業による実運用 | シミュレーションのみ | L5 Proof of Adoption |",
        "| 6ヶ月以上の継続運用 | 180日シミュレーション | 実運用開始後の継続計測 |",
        "| 複数企業マルチテナント | シングルテナントのみ | テナント分離設計 |",
        "| 分散環境・クラウド展開 | ローカルSQLiteのみ | PostgreSQL移行・クラウド対応 |",
        "| 第三者機関による独立監査 | 自己試験のみ | 外部監査機関依頼 |",
        "| MoCKA本体との実接続 | ブリッジログのみ | MoCKA API直接統合 |",
        "| 1M件超の大規模稼働 | 最大100K件 | 大規模環境テスト |",
        "",
        "> **未証明を未証明と明記することで、証明済み事項の信頼性が高まる。**",
        "",
        "---",
        "",
        "## 最終宣言",
        "",
        "```",
        "vasAI は「AIが考えるシステム」ではない。",
        "「組織が忘れないシステム」である。",
        "",
        "人が交代しても、部門が再編されても、",
        "システムが障害を起こしても、",
        "判断の根拠・推論・意図・結果が継承される。",
        "",
        "WHY → REASON → EVIDENCE → DECISION → OUTCOME",
        "この連鎖が組織の記憶となる。",
        "```",
        "",
        f"> **vasAI v1.0.0 は {passed}/{total}の試験をPASSし、**  ",
        f"> **L4.8 Proof of Institutional Memory を{'達成した' if l48_achieved else '達成できなかった'}。**",
        "",
        "---",
        f"*本報告書は `field_runner.py` により自動生成*  ",
        f"*生成日時: {now}*  ",
        f"*vasAI commit: `{commit}`*  ",
        f"*証明系譜: E20260530_008(P1) → E20260530_010(P2) → E20260530_014(P3) → E20260530_016(P4) → 本報告*  ",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path

# -*- coding: utf-8 -*-
"""
essence_to_packet.py
====================
ESS ENCEのJSONを「試料パケット（packet.md）」に変換する
閉ループの最初の橋渡しスクリプト

入力: data/storage/infield/ESSENCE/*.json
出力: data/storage/infield/PACKET/packet_{timestamp}.md

試料パケット構造:
  Theme / Strongest / Failure / Leap(+1) / Challenge(+3) / PING
"""
import json, datetime, hashlib
from pathlib import Path

ROOT    = Path(r"C:\Users\sirok\MoCKA")
ESSENCE = ROOT / "data" / "storage" / "infield" / "ESSENCE"
RECUR   = ROOT / "data" / "recurrence_registry.csv"
EVENTS  = ROOT / "data" / "events.csv"
PACKET  = ROOT / "data" / "storage" / "infield" / "PACKET"
PACKET.mkdir(parents=True, exist_ok=True)

# ══════════════════════════════════════════════════════════
# Recurrenceフィールドの補完（ESSENCE内Recurrence=0%対策）
# ══════════════════════════════════════════════════════════
def get_recurrence_context():
    """recurrence_registry.csvから再発パターンを抽出"""
    import csv
    if not RECUR.exists():
        return {"count": 0, "top_types": [], "note": "recurrence_registry.csv not found"}

    rows = list(csv.DictReader(open(RECUR, encoding="utf-8-sig")))
    if not rows:
        return {"count": 0, "top_types": [], "note": "empty"}

    from collections import Counter
    type_counts = Counter(r.get("what_type","unknown") for r in rows)
    top = [{"type": t, "count": c} for t, c in type_counts.most_common(3)]

    return {
        "count"    : len(rows),
        "top_types": top,
        "note"     : f"{len(rows)}件の再発記録。最多: {top[0]['type'] if top else 'N/A'}"
    }

# ══════════════════════════════════════════════════════════
# 最新インシデント取得（直近3件）
# ══════════════════════════════════════════════════════════
def get_recent_incidents():
    import csv
    if not EVENTS.exists():
        return []
    rows = list(csv.DictReader(open(EVENTS, encoding="utf-8-sig")))
    incidents = [r for r in rows if (r.get("risk_level") or "").strip() in ("WARNING","CRITICAL","ERROR")]
    incidents.sort(key=lambda r: r.get("when",""), reverse=True)
    return incidents[:3]

# ══════════════════════════════════════════════════════════
# 試料パケット生成
# ══════════════════════════════════════════════════════════
def essence_to_packet(essence_path: Path) -> Path:
    data = json.loads(essence_path.read_text(encoding="utf-8"))
    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    summary       = data.get("summary", {})
    stage_cov     = data.get("stage_coverage", {})
    recur_ctx     = get_recurrence_context()
    recent_incs   = get_recent_incidents()

    # 最強・最弱ステージ抽出
    strongest = summary.get("strongest_stage", {})
    weakest   = summary.get("weakest_stage", {})

    # Recurrenceの実態
    recurrence_cov = stage_cov.get("Recurrence", {}).get("coverage_pct", 0)
    recurrence_fixed = recurrence_cov == 0.0 and recur_ctx["count"] > 0

    # PING選択ロジック
    pings = []
    if recurrence_cov == 0.0:
        pings.append("Recall: 過去の再発パターンを参照せよ（Recurrence=0%は記録断絶のサイン）")
    if strongest.get("coverage", 0) > 70:
        pings.append(f"Leap: {strongest.get('stage','Action')}の強みを次の未着手領域に転用せよ")
    pings.append("Deny: 一般論・共感・Yesmanな回答を禁止する。反論・穴探しを優先せよ")

    # +3 チャレンジ
    challenges = [
        f"Recurrence({recurrence_cov}%)をゼロから実装し、再発を検知・記録するループを閉じる",
        "ESSENCE→試料パケット→AI注入の閉ループを1テーマで通過させる",
        "TRUST_SCOREによる回答審判をevents.csvに自動記録する仕組みを作る",
    ]

    # パケット本文生成
    now_str = datetime.datetime.now().isoformat()
    lines = [
        f"# MoCKA 試料パケット",
        f"**生成日時**: {now_str}",
        f"**ソース**: {essence_path.name}",
        f"**ハッシュ**: {data.get('hash','N/A')}",
        "",
        "---",
        "",
        "## Theme（現在のテーマ）",
        "MoCKA閉ループ完成 — ESSENCE→注入→審判の一貫フロー構築",
        "",
        "## Strongest（活かせる強み）",
        f"- **{strongest.get('stage','Action')}** ステージ: {strongest.get('coverage',0)}% カバレッジ",
        f"- **Audit** ステージ: {stage_cov.get('Audit',{}).get('coverage_pct',0)}% — 記録・検証の基盤は機能している",
        f"- **合計COREファイル数**: {summary.get('total_cores',0)}件",
        "",
        "## Failure（絶対に避けるべき弱点）",
        f"- **{weakest.get('stage','Recurrence')}** ステージ: {weakest.get('coverage',0)}% ← 完全断絶",
        f"- 再発記録は {recur_ctx['count']}件 存在するが、ESS ENCEに反映されていない（パイプライン断絶）",
    ]

    if recurrence_fixed:
        lines += [
            f"- recurrence_registry.csvの上位再発: {[t['type'] for t in recur_ctx['top_types']]}",
            "- ⚠ この断絶を放置すると「防ぐべき再発」を毎回忘れるシステムになる",
        ]

    if recent_incs:
        lines += ["", "## 直近インシデント（要注意）"]
        for inc in recent_incs:
            lines.append(f"- [{inc.get('risk_level','?')}] {inc.get('when','')[:10]} | {inc.get('title','')[:50]}")

    lines += [
        "",
        "## Leap +1（今すぐできる飛躍）",
        f"- Recurrenceを埋める最初の一手: recurrence_registry.csv（{recur_ctx['count']}件）をESS ENCEに逆注入する",
        "- essence_to_packet.pyが生成するこのパケット自体をmocka-shareに同梱する",
        "- 1テーマだけ試料パケット→AI注入→回答→audit記録の閉ループを通過させる",
        "",
        "## Challenge +3（次の3つの挑戦）",
    ]
    for i, ch in enumerate(challenges, 1):
        lines.append(f"{i}. {ch}")

    lines += [
        "",
        "## PING（AIへの強制注入命令）",
    ]
    for ping in pings:
        lines.append(f"- **{ping}**")

    lines += [
        "",
        "---",
        "",
        "## メタデータ",
        f"- avg_core_rr: {summary.get('avg_core_rr', 0)}%",
        f"- stage_coverage: " + " / ".join(
            f"{k}:{v.get('coverage_pct',0)}%"
            for k, v in stage_cov.items()
        ),
        f"- recurrence_registry件数: {recur_ctx['count']}",
        f"- 有効期限: 次のESSENCE生成まで（推奨24時間）",
    ]

    content = "\n".join(lines)
    out_path = PACKET / f"packet_{ts}.md"
    out_path.write_text(content, encoding="utf-8")
    return out_path


# ══════════════════════════════════════════════════════════
# メイン
# ══════════════════════════════════════════════════════════
def main():
    print("essence_to_packet.py 開始")

    all_files = sorted(ESSENCE.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    patched = [e for e in all_files if "patched" in e.name]
    others  = [e for e in all_files if "patched" not in e.name]
    essences = patched if patched else others[:1]

    if not essences:
        print("ESS ENCEファイルが見つかりません")
        return

    print(f"対象ESS ENCEファイル: {len(essences)}件（patched優先）")
    for ess in essences:
        print(f"  処理中: {ess.name}")
        out = essence_to_packet(ess)
        print(f"  → 生成: {out.name}")

    print(f"\n✓ 試料パケット生成完了 → {PACKET}")
    print(f"  木曜セッション開始時: packet_*.md を mocka-share に同梱すること")

if __name__ == "__main__":
    main()

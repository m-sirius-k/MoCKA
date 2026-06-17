#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PR-OS CLI  —  MoCKA Knowledge Distribution Layer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  python pros.py submit   <title> [file]      AI Gate 投入
  python pros.py list     [--status]           KS 一覧
  python pros.py show     <ks_id>              KS 詳細
  python pros.py publish  <ks_id> <adapter>   即時公開
  python pros.py schedule <ks_id> <adapter> <at>  予約配信
  python pros.py run      [--dry-run]          期限ジョブ実行
  python pros.py jobs     [--status]           スケジューラー一覧
  python pros.py health                        TSI ヘルスチェック
  python pros.py tsi                           TSI 詳細レポート
  python pros.py analytics [--days N]          GA4 概要
  python pros.py report   [--days N]           AI Rewriter レポート
  python pros.py setup-ga <property_id> <creds_path>  GA4 設定
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import argparse
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ADAPTERS = ["wordpress", "x", "instagram", "github_pages", "newsletter", "linkedin"]

# ── ANSI Colors ─────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    BLUE   = "\033[94m"
    CYAN   = "\033[96m"
    GRAY   = "\033[90m"
    def g(t): return f"{C.GREEN}{t}{C.RESET}"
    def y(t): return f"{C.YELLOW}{t}{C.RESET}"
    def r(t): return f"{C.RED}{t}{C.RESET}"
    def b(t): return f"{C.BLUE}{t}{C.RESET}"
    def c(t): return f"{C.CYAN}{t}{C.RESET}"
    def dim(t): return f"{C.GRAY}{t}{C.RESET}"

def _banner():
    print(f"{C.BLUE}{C.BOLD}")
    print("  ██████╗ ██████╗       ██████╗ ███████╗")
    print("  ██╔══██╗██╔══██╗     ██╔═══██╗██╔════╝")
    print("  ██████╔╝██████╔╝     ██║   ██║███████╗")
    print("  ██╔═══╝ ██╔══██╗     ██║   ██║╚════██║")
    print("  ██║     ██║  ██║     ╚██████╔╝███████║")
    print("  ╚═╝     ╚═╝  ╚═╝      ╚═════╝ ╚══════╝")
    print(f"{C.RESET}{C.GRAY}  MoCKA Knowledge Distribution Layer{C.RESET}\n")

def _sep(): print(C.dim("─" * 60))


# ── Adapter Factory ─────────────────────────────
def _get_adapter(name: str):
    n = name.lower().replace("-", "_")
    if n == "wordpress":
        from adapters.wordpress.wp_adapter import WordPressAdapter
        return WordPressAdapter()
    if n in ("x", "twitter", "x_twitter"):
        from adapters.x_twitter.x_adapter import XAdapter
        return XAdapter()
    if n in ("instagram", "ig"):
        from adapters.instagram.ig_adapter import InstagramAdapter
        return InstagramAdapter()
    if n in ("github_pages", "github", "gh"):
        from adapters.github_pages.gh_adapter import GitHubPagesAdapter
        return GitHubPagesAdapter()
    if n in ("newsletter", "nl"):
        from adapters.newsletter.nl_adapter import NewsletterAdapter
        return NewsletterAdapter()
    if n in ("linkedin", "li"):
        from adapters.linkedin.linkedin_adapter import LinkedInAdapter
        return LinkedInAdapter()
    raise ValueError(f"Unknown adapter: {name}")


# ── Commands ─────────────────────────────────────
def cmd_submit(args):
    from ai_gate.gate import process
    title = args.title
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            raw = f.read()
    else:
        print(C.dim("本文を入力 (Ctrl+Z/Ctrl+D で終了):"))
        raw = sys.stdin.read()

    tags     = [t.strip() for t in args.tags.split(",")] if args.tags else []
    category = args.category or ""

    _sep()
    result = process(title=title, raw_text=raw, tags=tags, category=category)
    _sep()
    status_color = C.g if result["status"] == "confirmed" else C.y
    print(f"  KS ID   : {C.c(result['ks_id'])}")
    print(f"  Status  : {status_color(result['status'])}")
    print(f"  Score   : {_score_str(result['score'])}")
    print(f"  Summary : {result['summary']}")
    _sep()


def cmd_list(args):
    from knowledge_store.ks_manager import list_records
    records = list_records(status=args.status or None)
    if not records:
        print(C.dim("  レコードがありません。"))
        return
    print(f"\n  {C.BOLD}{'ID':<10} {'Status':<20} {'Score':<8} Title{C.RESET}")
    _sep()
    for r in records:
        score = r["ai_gate_log"].get("score")
        s_str = _score_str(score) if score is not None else C.dim("  —  ")
        st    = _status_str(r["status"])
        print(f"  {C.c(r['id']):<10} {st:<30} {s_str:<18} {r['title']}")
    print()


def cmd_show(args):
    from knowledge_store.ks_manager import get_record
    rec = get_record(args.ks_id)
    _sep()
    print(f"  {C.BOLD}{rec['id']}{C.RESET} — {rec['title']}")
    _sep()
    print(f"  Status    : {_status_str(rec['status'])}")
    score = rec["ai_gate_log"].get("score")
    print(f"  Score     : {_score_str(score) if score else C.dim('—')}")
    print(f"  Category  : {rec.get('category') or C.dim('—')}")
    print(f"  Tags      : {', '.join(rec.get('tags', [])) or C.dim('—')}")
    print(f"  Created   : {rec['created_at'][:10]}")
    print(f"  Confirmed : {rec.get('confirmed_at', '—')[:10] if rec.get('confirmed_at') else C.dim('—')}")
    print(f"\n  {C.BOLD}配信状況{C.RESET}")
    for adapter, status in rec.get("publish_status", {}).items():
        color = C.g if status == "published" else (C.y if status in ("scheduled","pending") else C.dim)
        print(f"    {adapter:<15} {color(status)}")
    _sep()


def _load_confirmed_text(ks_id: str) -> str:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "knowledge_store", "confirmed", f"{ks_id}.md")
    with open(path, encoding="utf-8") as f:
        return f.read()


def _run_seo_center(rec: dict, text: str, force_type: str = None):
    """SEO-CENTERを通してSEOResultを返す（WordPress向け）"""
    from seo_center.seo_center import SEOCenter
    center = SEOCenter()
    return center.process(
        title          = rec["title"],
        confirmed_text = text,
        tags           = rec.get("tags", []),
        category       = rec.get("category", ""),
        summary        = rec.get("ai_gate_log", {}).get("summary"),
        force_type     = force_type,
    )


def cmd_publish(args):
    from knowledge_store.ks_manager import get_record, update_publish_status
    ks_id = args.ks_id
    rec   = get_record(ks_id)
    if rec["status"] != "confirmed":
        print(C.r(f"  [Error] {ks_id} は confirmed ではありません (status={rec['status']})"))
        sys.exit(1)

    text    = _load_confirmed_text(ks_id)
    adapter = _get_adapter(args.adapter)

    # WordPress は SEO-CENTER を通す
    use_seo = args.adapter == "wordpress" and not getattr(args, "no_seo", False)
    if use_seo:
        seo = _run_seo_center(rec, text)
        print(f"  {C.c('[SEO]')} ContentType: {seo.content_type} / Score: {C.b(str(seo.seo_score))}")
        print(f"  {C.c('[SEO]')} Slug: {seo.slug}")
        print(f"  {C.c('[SEO]')} Description: {seo.description[:80]}{'…' if len(seo.description) > 80 else ''}")
        converted = adapter.convert(rec, text, seo_result=seo)
    else:
        converted = adapter.convert(rec, text)

    result = adapter.publish(converted)

    if result.success:
        update_publish_status(ks_id, args.adapter, "published")
        from mocka_bridge import feedback_publish
        feedback_publish(ks_id, args.adapter, True, result.url)
        print(C.g(f"  [OK] Published: {ks_id} → {args.adapter}"))
        if result.url: print(f"       URL: {C.b(result.url)}")
    else:
        from mocka_bridge import feedback_publish
        feedback_publish(ks_id, args.adapter, False)
        print(C.r(f"  [NG] Failed: {result.error}"))
        sys.exit(1)


def cmd_seo(args):
    """SEO-CENTER単体実行: KSのSEO分析レポートを表示"""
    from knowledge_store.ks_manager import get_record
    ks_id = args.ks_id
    rec   = get_record(ks_id)
    text  = _load_confirmed_text(ks_id)

    print(f"\n  {C.BOLD}SEO-CENTER 分析{C.RESET}")
    _sep()

    seo = _run_seo_center(rec, text, force_type=getattr(args, "type", None))

    print(f"  KS ID        : {C.c(ks_id)}")
    print(f"  ContentType  : {C.b(seo.content_type)}")
    print(f"  Intent       : {seo.intent}")
    print(f"  Targets      : {C.g(', '.join(seo.targets))}")
    print(f"  Routing      : {C.dim(seo.routing_reason)}")
    _sep()
    print(f"  SEO Score    : {_score_str(seo.seo_score)}")
    for k, v in seo.score_breakdown.items():
        bar = "█" * int(v * 50)
        print(f"    {k:<20} {v:.3f}  {C.dim(bar)}")
    _sep()
    print(f"  Slug         : {seo.slug}")
    print(f"  Description  : {seo.description}")
    _sep()

    if getattr(args, "html", False):
        print(f"\n  {C.BOLD}生成HTML (先頭1000文字){C.RESET}")
        _sep()
        print(seo.html[:1000])
        _sep()

    if getattr(args, "route", False):
        print(f"\n  {C.BOLD}配信先 (Distribution Router){C.RESET}")
        _sep()
        for t in seo.targets:
            print(f"    → {C.g(t)}")
        _sep()
    print()


def cmd_schedule(args):
    from scheduler.scheduler import enqueue
    job = enqueue(args.ks_id, args.adapter, args.publish_at)
    print(C.g(f"  [OK] Queued: {job['job_id']}"))
    print(f"       {args.ks_id} → {args.adapter} @ {C.c(args.publish_at)}")


def cmd_run(args):
    from scheduler.scheduler import run_due
    results = run_due(dry_run=args.dry_run)
    if not results:
        print(C.dim("  実行対象ジョブがありません。"))
        return
    if args.dry_run:
        print(f"  {C.y('[Dry Run]')} {len(results)} job(s) would run:")
        for r in results:
            print(f"    - {r['job_id']} | {r['ks_id']} → {r['adapter']}")
    else:
        ok = sum(1 for r in results if r.get("success"))
        ng = len(results) - ok
        print(f"  {C.g(f'OK: {ok}')} / {C.r(f'NG: {ng}')}")


def cmd_jobs(args):
    from scheduler.scheduler import list_jobs, queue_summary
    summary = queue_summary()
    print(f"\n  Total:{summary['total']} | "
          f"Pending:{C.y(summary['pending'])} | "
          f"Done:{C.g(summary['done'])} | "
          f"Failed:{C.r(summary['failed'])}")
    _sep()
    jobs = list_jobs(status=args.status or None)
    if not jobs:
        print(C.dim("  ジョブがありません。"))
        return
    print(f"  {C.BOLD}{'Job ID':<12} {'KS ID':<10} {'Adapter':<14} {'Schedule':<22} Status{C.RESET}")
    for j in reversed(jobs):
        st = _job_status_str(j["status"])
        print(f"  {C.dim(j['job_id']):<12} {C.c(j['ks_id']):<10} "
              f"{j['adapter']:<14} {j['publish_at'][:16]:<22} {st}")
    print()


def cmd_health(args):
    from scheduler.tsi import run
    print(f"\n  {C.BOLD}TSI Health Check{C.RESET}")
    _sep()
    summary = run(verbose=True)
    _sep()
    ok, dis, err = summary["ok"], summary["disabled"], summary["error"]
    print(f"  OK:{C.g(ok)} | Disabled:{C.dim(dis)} | Error:{C.r(err)}")
    if summary["new_alerts"]:
        print(f"\n  {C.y('Alerts:')}")
        for a in summary["new_alerts"]:
            icon = {"critical":"🔴","error":"🔴","warning":"🟡"}.get(a["severity"],"·")
            print(f"    {icon} {a['message']}")
    print()


def cmd_tsi(args):
    from scheduler.tsi import get_log, get_alerts
    log    = get_log()
    alerts = get_alerts(limit=10)
    print(f"\n  {C.BOLD}TSI Log{C.RESET}")
    _sep()
    print(f"  Last run: {log.get('last_run', C.dim('未実行'))}")
    for aid, data in log.get("adapters", {}).items():
        icon = "✓" if data["status"] == "ok" else ("○" if data["status"] == "disabled" else "✗")
        changed = C.y(" [変化]") if data.get("changed") else ""
        print(f"  {icon} {aid} {data['adapter_name']:<16} [{data['status']}]{changed}")
    if alerts:
        print(f"\n  {C.BOLD}Recent Alerts{C.RESET}")
        for a in alerts:
            icon = {"critical":"🔴","error":"🔴","warning":"🟡"}.get(a["severity"],"ℹ️")
            print(f"    {icon} [{a['timestamp'][:10]}] {a['message']}")
    print()


def cmd_analytics(args):
    from analytics.ga_connector import get_overview, get_traffic_sources, status as ga_status
    days = args.days
    st   = ga_status()
    print(f"\n  {C.BOLD}Google Analytics 4{C.RESET}")
    _sep()
    if not st["enabled"]:
        print(f"  {C.y('GA未設定')} — python pros.py setup-ga <property_id> <creds_path>")
        print(f"  ライブラリ: {C.g('installed') if st['ga_library'] else C.r('未インストール: pip install google-analytics-data')}")
        return

    overview = get_overview(days=days)
    print(f"  期間: 過去{days}日間")
    print(f"  Sessions   : {overview.get('sessions', 0):,}")
    print(f"  Page Views : {overview.get('pageviews', 0):,}")
    print(f"  New Users  : {overview.get('new_users', 0):,}")
    print(f"  Bounce Rate: {overview.get('bounce_rate', 0):.1%}")
    print(f"  Avg Duration: {overview.get('avg_duration', 0):.0f}s")

    sources = get_traffic_sources(days=days)
    if sources and not sources[0].get("mock"):
        print(f"\n  {C.BOLD}流入元{C.RESET}")
        for s in sources[:5]:
            print(f"    {s.get('sessionDefaultChannelGroup','—'):<20} {int(s.get('sessions',0)):>6,} sessions")
    print()


def cmd_report(args):
    from analytics.rewriter import report
    print()
    print(report(days=args.days))


def cmd_daemon(args):
    from scheduler.daemon import run_daemon
    run_daemon(once=args.once)


def cmd_bridge(args):
    from mocka_bridge import status
    st = status()
    print(f"\n  {C.BOLD}MoCKA Bridge{C.RESET}")
    _sep()
    print(f"  ログエントリ   : {st['log_entries']}")
    print(f"  Ingest総数     : {C.g(st['total_ingested'])}")
    print(f"  Feedback総数   : {C.b(st['total_feedbacks'])}")
    print(f"  エラー         : {C.r(st['total_errors']) if st['total_errors'] else C.dim('0')}")
    print(f"  最終Ingest     : {st['last_ingest'] or C.dim('なし')}")
    print(f"  最終処理ID     : {st['last_processed_id'] or C.dim('なし')}")
    print()


def cmd_sync(args):
    from mocka_bridge import sync_from_mocka
    _sep()
    result = sync_from_mocka(args.db_path)
    _sep()
    print(f"  Processed : {C.b(result['processed'])}")
    print(f"  Confirmed : {C.g(result['confirmed'])}")
    print(f"  Pending   : {C.y(result['pending'])}")
    print(f"  Errors    : {C.r(result['errors']) if result['errors'] else C.dim('0')}")
    print()


def cmd_ingest(args):
    from mocka_bridge import ingest_from_file
    _sep()
    result = ingest_from_file(args.file_path)
    if result:
        _sep()
        status_color = C.g if result["status"] == "confirmed" else C.y
        print(f"  KS ID   : {C.c(result['ks_id'])}")
        print(f"  Status  : {status_color(result['status'])}")
        print(f"  Score   : {_score_str(result['score'])}")
        print(f"  Summary : {result['summary']}")
        _sep()


def cmd_test(args):
    import subprocess
    result = subprocess.run(
        ["python", "-X", "utf8", "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    sys.exit(result.returncode)


def cmd_setup_ga(args):
    from analytics.ga_connector import setup
    setup(args.property_id, args.creds_path)
    print(C.g("  [OK] GA4設定を保存しました。"))
    print(f"       python pros.py analytics で確認できます。")


# ── Formatters ───────────────────────────────────
def _score_str(score):
    if score is None: return C.dim("—")
    s = f"{score:.2f}"
    if score >= 0.9: return C.g(s)
    if score >= 0.8: return C.b(s)
    if score >= 0.6: return C.y(s)
    return C.r(s)

def _status_str(s):
    m = {
        "confirmed":        C.g("confirmed"),
        "draft":            C.dim("draft"),
        "pending_approval": C.y("pending_approval"),
        "rejected":         C.r("rejected"),
    }
    return m.get(s, s)

def _job_status_str(s):
    m = {
        "pending":   C.y("pending"),
        "running":   C.b("running"),
        "done":      C.g("done"),
        "failed":    C.r("failed"),
        "cancelled": C.dim("cancelled"),
    }
    return m.get(s, s)


# ── Entry Point ──────────────────────────────────
def main():
    _banner()
    p = argparse.ArgumentParser(
        prog="pros", description="PR-OS CLI — MoCKA Knowledge Distribution Layer",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("submit",   help="AI GateにINPUT → KS作成")
    s.add_argument("title"); s.add_argument("file", nargs="?")
    s.add_argument("--tags", default=""); s.add_argument("--category", default="")

    s = sub.add_parser("list",    help="KS一覧")
    s.add_argument("--status", default="")

    s = sub.add_parser("show",    help="KS詳細")
    s.add_argument("ks_id")

    s = sub.add_parser("publish", help="即時公開（WordPressはSEO-CENTER自動適用）")
    s.add_argument("ks_id"); s.add_argument("adapter", choices=ADAPTERS)
    s.add_argument("--no-seo", action="store_true", help="SEO-CENTERをスキップ（WordPress）")

    s = sub.add_parser("seo",    help="SEO-CENTER分析レポート")
    s.add_argument("ks_id")
    s.add_argument("--type", default="", help="コンテンツタイプ強制指定 (technical/thought/announcement/research/strategic)")
    s.add_argument("--html", action="store_true", help="生成HTMLを表示")
    s.add_argument("--route", action="store_true", help="配信先を表示")

    s = sub.add_parser("schedule",help="予約配信")
    s.add_argument("ks_id"); s.add_argument("adapter", choices=ADAPTERS)
    s.add_argument("publish_at")

    s = sub.add_parser("run",     help="期限ジョブ実行")
    s.add_argument("--dry-run", action="store_true")

    s = sub.add_parser("jobs",    help="スケジューラー一覧")
    s.add_argument("--status", default="")

    sub.add_parser("health",  help="TSI ヘルスチェック")
    sub.add_parser("tsi",     help="TSI 詳細ログ・アラート")

    s = sub.add_parser("analytics",help="GA4 概要")
    s.add_argument("--days", type=int, default=30)

    s = sub.add_parser("report",  help="AI Rewriter レポート")
    s.add_argument("--days", type=int, default=30)

    s = sub.add_parser("setup-ga",help="GA4 設定")
    s.add_argument("property_id"); s.add_argument("creds_path")

    s = sub.add_parser("daemon",  help="スケジューラーデーモン起動")
    s.add_argument("--once", action="store_true", help="1回だけ実行")

    s = sub.add_parser("bridge",  help="MoCKA Bridgeステータス")

    s = sub.add_parser("sync",    help="MoCKAイベントDBを同期")
    s.add_argument("db_path", help="mocka_events.db のパス")

    s = sub.add_parser("ingest",  help="ファイルをAI Gateに投入")
    s.add_argument("file_path", help="Markdownファイルパス")

    s = sub.add_parser("test",    help="テストスイート実行")

    args    = p.parse_args()
    dispatch = {
        "submit":   cmd_submit,   "list":      cmd_list,
        "show":     cmd_show,     "publish":   cmd_publish,
        "schedule": cmd_schedule, "run":       cmd_run,
        "jobs":     cmd_jobs,     "health":    cmd_health,
        "tsi":      cmd_tsi,      "analytics": cmd_analytics,
        "report":   cmd_report,   "setup-ga":  cmd_setup_ga,
        "daemon":   cmd_daemon,   "bridge":    cmd_bridge,
        "sync":     cmd_sync,     "ingest":    cmd_ingest,
        "test":     cmd_test,     "seo":       cmd_seo,
    }
    dispatch[args.cmd](args)


if __name__ == "__main__":
    main()

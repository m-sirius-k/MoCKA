# -*- coding: utf-8 -*-
"""Sync Pipeline (Phase 4-2 Reality Sync Layer) - CLI Entrypoint

usage:
    python -m reality_sync.sync_pipeline

出力:
  - Truth Status Table
  - Discrepancy Report
  - Fix Required List
  - EVIDENCE_ONLY ログ (reality_sync/logs/sync_log.jsonl)
"""

from reality_sync.sync_engine import run
from reality_sync.sync_logger import log_results


def _print_table(results):
    print("=" * 100)
    print("TRUTH STATUS TABLE")
    print("=" * 100)
    header = f"{'file_path':<45} {'reported':<10} {'actual':<8} {'discrepancy':<14} {'severity':<8} {'fix_required'}"
    print(header)
    print("-" * 100)
    for r in results:
        print(f"{r.file_path:<45} {r.reported_status:<10} {r.actual_status:<8} "
              f"{r.discrepancy_type:<14} {r.severity:<8} {r.fix_required}")


def _print_discrepancies(results):
    discrepant = [r for r in results if r.discrepancy_type != "NONE"]
    print()
    print("=" * 100)
    print(f"DISCREPANCY REPORT ({len(discrepant)} 件)")
    print("=" * 100)
    if not discrepant:
        print("差分なし。")
    for r in discrepant:
        print(f"- {r.file_path}")
        print(f"    reported : {r.reported_status} (sources: {', '.join(r.sources) or 'なし'})")
        print(f"    actual   : {r.actual_status}")
        print(f"    type     : {r.discrepancy_type} / severity={r.severity}")
        print(f"    evidence : {r.evidence}")


def _print_fix_required(results):
    fix_list = [r for r in results if r.fix_required]
    print()
    print("=" * 100)
    print(f"FIX REQUIRED LIST ({len(fix_list)} 件)")
    print("=" * 100)
    if not fix_list:
        print("修正必要ファイルなし。")
    for r in fix_list:
        print(f"- {r.file_path}  (evidence: {r.evidence})")


def main():
    results = run()
    _print_table(results)
    _print_discrepancies(results)
    _print_fix_required(results)

    log_file = log_results(results)
    print()
    print(f"EVIDENCE_ONLY ログ書き込み先: {log_file}")


if __name__ == "__main__":
    main()

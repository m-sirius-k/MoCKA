#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/seal_baseline.py -- Phase5-2 STEP5 Baseline Seal

Hash Chain開始時点を正式な基準点として記録する。
data/integrity_baseline.jsonを書き出し、対応するgit annotated tagを作成する
(tag作成のみ。pushは行わない -- pushは呼び出し側のGit運用手順に従う)。

使い方:
  python scripts/seal_baseline.py --test-summary '{"passed": N, "failed": 0, "suite": "..."}'
  python scripts/seal_baseline.py --tag   # JSON生成後にgit tagも作成する
"""

import json
import re
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "phi_os"))
sys.path.insert(0, str(_REPO_ROOT / "interface"))

import integrity  # noqa: E402
from gate_policy import POLICY_VERSION  # noqa: E402

BASELINE_PATH = _REPO_ROOT / "data" / "integrity_baseline.json"
SCHEMA_SQL_PATH = _REPO_ROOT / "data" / "mocka_schema_v1.sql"
MIGRATION_VERSION = "migrate_event_integrity_v1"
TAG_NAME = "mocka-baseline-v1.0-event-integrity"

_SCHEMA_VERSION_RE = re.compile(r"SQLite Schema v([\d.]+)")


def _git_head() -> str:
    out = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(_REPO_ROOT),
        capture_output=True, text=True, check=True
    )
    return out.stdout.strip()


def _schema_version() -> str:
    text = SCHEMA_SQL_PATH.read_text(encoding="utf-8")
    m = _SCHEMA_VERSION_RE.search(text)
    return m.group(1) if m else "unknown"


def build_baseline(test_summary: dict) -> dict:
    return integrity.seal_baseline(
        git_commit=_git_head(),
        schema_version=_schema_version(),
        gate_policy_version=POLICY_VERSION,
        migration_version=MIGRATION_VERSION,
        test_summary=test_summary,
    )


def create_tag(baseline: dict) -> str:
    message = (
        f"Phase5-2 Baseline Seal\n"
        f"git_commit={baseline['git_commit']}\n"
        f"created_at={baseline['created_at']}\n"
        f"schema_version={baseline['schema_version']}\n"
        f"gate_policy_version={baseline['gate_policy_version']}\n"
        f"signature_version={baseline['signature_version']}\n"
        f"hash_algorithm={baseline['hash_algorithm']}\n"
    )
    subprocess.run(
        ["git", "tag", "-a", TAG_NAME, "-m", message],
        cwd=str(_REPO_ROOT), check=True
    )
    return TAG_NAME


def main() -> int:
    test_summary = {"passed": 0, "failed": 0, "suite": "phi_os/tests/test_integrity.py"}
    if "--test-summary" in sys.argv:
        idx = sys.argv.index("--test-summary")
        test_summary = json.loads(sys.argv[idx + 1])

    baseline = build_baseline(test_summary)
    BASELINE_PATH.write_text(
        json.dumps(baseline, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(baseline, ensure_ascii=False, indent=2))

    if "--tag" in sys.argv:
        tag = create_tag(baseline)
        print(f"created tag: {tag}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

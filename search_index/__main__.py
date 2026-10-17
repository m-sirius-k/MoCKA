"""
CLI for the MoCKA file search index.

  python -m search_index build [--rebuild]     first full build (or --rebuild to replace atomically)
  python -m search_index update                incremental update (add / change / remove)
  python -m search_index status                show index status and scope
  python -m search_index search "query" [--ext py,md] [--kind source] [--dir mapping] [--role TEST]
                                        [--mtime-from 2026-10-01] [--mtime-to 2026-10-10] [--limit 20]
"""
import argparse
import json
import sys
import time

from . import core


def main(argv=None):
    ap = argparse.ArgumentParser(prog="search_index")
    ap.add_argument("--root", default=core.DEFAULT_ROOT)
    ap.add_argument("--db", default=core.DEFAULT_DB)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--rebuild", action="store_true")
    b.add_argument("--no-content", action="store_true")
    sub.add_parser("update")
    sub.add_parser("status")
    it = sub.add_parser("item")
    it.add_argument("path")
    s = sub.add_parser("search")
    s.add_argument("q", nargs="?", default="")
    s.add_argument("--ext", default="")
    s.add_argument("--kind", default="")
    s.add_argument("--dir", default="")
    s.add_argument("--size-min", type=int)
    s.add_argument("--size-max", type=int)
    s.add_argument("--mtime-from", default="")
    s.add_argument("--mtime-to", default="")
    s.add_argument("--role", default="")
    s.add_argument("--asset", default="")
    s.add_argument("--topic", default="")
    s.add_argument("--content", action="store_true")
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--offset", type=int, default=0)
    a = ap.parse_args(argv)

    if a.cmd in ("build", "update"):
        t0 = time.perf_counter()
        res = core.build_or_update(a.root, a.db, rebuild=(a.cmd == "build" and a.rebuild),
                                   with_content=not getattr(a, "no_content", False))
        res["elapsed_seconds"] = round(time.perf_counter() - t0, 2)
        print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
        return 0
    if a.cmd == "status":
        print(json.dumps(core.status(a.db), ensure_ascii=False, indent=1, default=str))
        return 0
    if a.cmd == "item":
        res = core.item(a.db, a.path)
        # same contract as GET /api/item: found -> the record, missing -> NOT_IN_INDEX (non-zero exit)
        print(json.dumps(res or {"error": "NOT_IN_INDEX"}, ensure_ascii=False, indent=1, default=str))
        return 0 if res else 1
    if a.cmd == "search":
        t0 = time.perf_counter()
        res = core.search(a.db, q=a.q, ext=a.ext, kind=a.kind, dir_prefix=a.dir, size_min=a.size_min,
                          size_max=a.size_max, mtime_from=a.mtime_from, mtime_to=a.mtime_to, role=a.role,
                          asset=a.asset, topic=a.topic, content=a.content, limit=a.limit, offset=a.offset)
        res["elapsed_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())

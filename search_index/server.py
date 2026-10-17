"""
Local search UI/API for the MoCKA file index. Binds to 127.0.0.1 only.
It returns metadata from the index database; it never returns file contents.

  python -m search_index.server --port 5110
"""
import argparse
import json
import os
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import core

UI_PATH = os.path.join(core.PKG_DIR, "ui.html")
_update_lock = threading.Lock()


def _int_or_none(v):
    if v in (None, ""):
        return None
    return int(v)


class Handler(BaseHTTPRequestHandler):
    server_version = "MoCKASearch/0.1"
    db_path = core.DEFAULT_DB
    root = core.DEFAULT_ROOT

    def log_message(self, fmt, *args):  # request paths only; query text and file data are not logged
        sys.stderr.write("%s %s\n" % (self.address_string(), self.path.split("?")[0]))

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        qs = {k: v[0] for k, v in urllib.parse.parse_qs(u.query, keep_blank_values=True).items()}
        try:
            if u.path == "/":
                with open(UI_PATH, "rb") as fh:
                    return self._send(200, fh.read(), "text/html; charset=utf-8")
            if u.path == "/api/status":
                return self._send(200, core.status(self.db_path))
            if u.path == "/api/search":
                limit = min(max(int(qs.get("limit", 50) or 50), 1), 200)
                offset = max(int(qs.get("offset", 0) or 0), 0)
                res = core.search(
                    self.db_path, q=qs.get("q", ""), ext=qs.get("ext", ""), kind=qs.get("kind", ""),
                    dir_prefix=qs.get("dir", ""), size_min=_int_or_none(qs.get("size_min")),
                    size_max=_int_or_none(qs.get("size_max")), mtime_from=qs.get("mtime_from", ""),
                    mtime_to=qs.get("mtime_to", ""), role=qs.get("role", ""), asset=qs.get("asset", ""),
                    topic=qs.get("topic", ""), content=qs.get("content", "") == "1", limit=limit, offset=offset)
                return self._send(200, res)
            if u.path == "/api/item":
                it = core.item(self.db_path, qs.get("path", ""))
                return self._send(200 if it else 404, it or {"error": "NOT_IN_INDEX"})
            if u.path == "/api/dir":
                d = core.directory(self.db_path, qs.get("path", "."))
                return self._send(200 if d else 404, d or {"error": "NOT_IN_INDEX"})
            return self._send(404, {"error": "NOT_FOUND"})
        except ValueError as exc:
            return self._send(400, {"error": "BAD_REQUEST", "detail": str(exc)})
        except Exception as exc:  # report, do not leak internals beyond the type
            return self._send(500, {"error": "INTERNAL", "detail": type(exc).__name__})

    def do_POST(self):
        if self.path.split("?")[0] != "/api/update":
            return self._send(404, {"error": "NOT_FOUND"})
        if not _update_lock.acquire(blocking=False):
            return self._send(409, {"error": "UPDATE_ALREADY_RUNNING"})
        try:
            res = core.build_or_update(self.root, self.db_path, rebuild=False, with_content=True)
            return self._send(200, {"status": res["status"], "stats": res["stats"], "built_at": res["meta"]["built_at"]})
        except core.BuildError as exc:
            return self._send(500, {"status": "FAILED", "detail": str(exc)[:300]})
        finally:
            _update_lock.release()


def make_server(host, port, db_path, root):
    Handler.db_path = db_path
    Handler.root = root
    if host not in ("127.0.0.1", "localhost"):
        raise SystemExit("refusing to bind to a non-loopback address")
    return ThreadingHTTPServer((host, port), Handler)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5110)
    ap.add_argument("--db", default=core.DEFAULT_DB)
    ap.add_argument("--root", default=core.DEFAULT_ROOT)
    a = ap.parse_args(argv)
    srv = make_server(a.host, a.port, a.db, a.root)
    print("MoCKA search listening on http://%s:%d/ (db: %s)" % (a.host, a.port, a.db), flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
MoCKA file search index (local, read-only against the repository).

Writes only to its own SQLite database (default: search_index/data/search_index.sqlite).
Never touches data/mocka_events.db, the Decision Ledger, Event Store, Memory data, or HG records.

Evidence kinds kept separate:
  - git_first_added : first commit that added the path (git log), only for tracked paths
  - filename_date   : a date string in the file name (not a creation date)
  - mtime           : file-system modification time (not a creation date)
Sensitive-looking names are indexed as location/metadata only; their content is never read.
"""
import collections
import csv
import datetime
import importlib.util
import json
import os
import re
import sqlite3
import subprocess
import unicodedata

TZ = datetime.timezone(datetime.timedelta(hours=9))
PKG_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.dirname(PKG_DIR)
DEFAULT_DB = os.path.join(PKG_DIR, "data", "search_index.sqlite")
SELF_DATA_DIR = os.path.join(PKG_DIR, "data")  # the index store itself is never indexed

EXCLUDED_DIRS = {".git", ".venv", "venv", "archive", "__pycache__", "node_modules"}
# Virtual-environment-like directories (e.g. .wsl_ots_venv) are excluded by name pattern.
VENV_LIKE_RX = re.compile(r"venv", re.I)
SENSITIVE_RX = re.compile(
    r"(private|secret|credential|token|password|\.pem$|\.key$|\.p12$|\.pfx$|id_rsa|\.env$|\.env\.(?!example$))",
    re.I)
TEXT_EXT = {".md", ".txt", ".py", ".json", ".jsonl", ".csv", ".yaml", ".yml", ".toml", ".ini", ".cfg",
            ".ps1", ".bat", ".cmd", ".sh", ".js", ".ts", ".html", ".sql", ".tsv"}
MAX_CONTENT_BYTES = 1_000_000
DATE_RX = re.compile(r"(?<!\d)(20[0-3]\d)(0[1-9]|1[0-2])([0-2]\d|3[01])(?!\d)")
TOPIC_TERMS = {
    "memory": "memory", "phi_os": "phi_os", "phi-os": "phi_os", "mcp": "mcp", "mocka_mcp": "mcp",
    "orchestra": "orchestra", "relay": "relay", "synapse": "synapse", "gate": "gate",
}
KIND_BY_EXT = {
    ".md": "document", ".txt": "document", ".docx": "document", ".pdf": "document", ".html": "document",
    ".py": "source", ".js": "source", ".ts": "source", ".ps1": "source", ".bat": "source", ".sh": "source", ".cmd": "source",
    ".json": "data", ".jsonl": "data", ".csv": "data", ".tsv": "data", ".db": "data", ".sqlite": "data", ".sql": "data",
    ".yaml": "config", ".yml": "config", ".toml": "config", ".ini": "config", ".cfg": "config",
    ".log": "log",
    ".png": "binary", ".jpg": "binary", ".jpeg": "binary", ".gif": "binary", ".svg": "binary", ".ico": "binary",
    ".zip": "binary", ".gz": "binary", ".tar": "binary", ".xlsx": "binary", ".pptx": "binary",
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS files(
  path TEXT PRIMARY KEY, name TEXT, name_norm TEXT, path_norm TEXT, dir TEXT, dir_norm TEXT,
  top TEXT, depth INTEGER, ext TEXT, kind TEXT, size INTEGER, mtime TEXT, mtime_date TEXT, mtime_ns INTEGER,
  git_state TEXT, role_tags TEXT, asset_id TEXT, git_first_added TEXT, filename_date TEXT,
  content_status TEXT, mapped_docs TEXT, topic_tags TEXT, indexed_at TEXT);
CREATE INDEX IF NOT EXISTS ix_files_dir ON files(dir);
CREATE INDEX IF NOT EXISTS ix_files_ext ON files(ext);
CREATE TABLE IF NOT EXISTS dirs(path TEXT PRIMARY KEY, parent TEXT, depth INTEGER,
  direct_files INTEGER, recursive_files INTEGER, asset_id TEXT);
CREATE TABLE IF NOT EXISTS scope(path TEXT PRIMARY KEY, reason TEXT, file_count INTEGER);
CREATE TABLE IF NOT EXISTS relations(src_path TEXT, dst_path TEXT, relation TEXT, evidence_kind TEXT,
  status TEXT, line TEXT, source_asset TEXT, target_asset TEXT);
CREATE INDEX IF NOT EXISTS ix_rel_src ON relations(src_path);
CREATE INDEX IF NOT EXISTS ix_rel_dst ON relations(dst_path);
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);
CREATE VIRTUAL TABLE IF NOT EXISTS content_fts USING fts5(path UNINDEXED, body, tokenize = 'unicode61');
"""


def norm(s):
    return unicodedata.normalize("NFKC", s or "").lower()


def now_iso():
    return datetime.datetime.now(TZ).isoformat(timespec="seconds")


def git(root, args):
    try:
        r = subprocess.run(["git", "-C", root] + args, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=300)
        return r.stdout if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def role_tags(path, name, ext):
    tags = []
    if ext in (".md", ".txt", ".docx", ".html", ".pdf"):
        tags.append("DOCUMENT")
    if re.search(r"(design|spec|contract|schema|architecture|proposal)", name, re.I):
        tags.append("SPEC_OR_DESIGN")
    if ext in (".py", ".js", ".ts", ".ps1", ".sh", ".bat", ".cmd"):
        tags.append("SOURCE_CODE")
    if path.startswith((".claude/", ".codex/")) or name.startswith(".env") or ext in (".toml", ".ini", ".cfg", ".yaml", ".yml") or re.search(r"(config|settings)", name, re.I):
        tags.append("CONFIG")
    if ext in (".json", ".jsonl", ".csv", ".db", ".sqlite", ".sqlite3", ".sql", ".tsv") or "ledger" in name.lower():
        tags.append("DATA_OR_LEDGER")
    if name.startswith("test_") or "/tests/" in "/" + path or "/test/" in "/" + path:
        tags.append("TEST")
    if re.search(r"(verify|validat|audit|check|reconcil|forensic)", name, re.I):
        tags.append("VERIFICATION_OR_AUDIT")
    if ext == ".log" or re.search(r"(output|generated|snapshot|dump)", name, re.I):
        tags.append("LOG_OR_GENERATED")
    if re.search(r"(backup|_bak|\.bak|_old|archive|_v\d+|_copy|\(\d+\))", name + "/" + path, re.I):
        tags.append("HISTORY_OR_ARCHIVE")
    if ext in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".zip", ".gz", ".tar", ".xlsx", ".pptx"):
        tags.append("BINARY_OR_MEDIA")
    return tags or ["UNCLASSIFIED"]


def topic_tags(path):
    low = path.lower()
    out = []
    for term, tag in TOPIC_TERMS.items():
        if term in low and tag not in out:
            out.append(tag)
    return out


def load_registry(root):
    """Read existing registry CSVs (read-only). Returns path->asset_id, and edge rows with paths."""
    gov = os.path.join(root, "docs", "governance")
    asset_path = os.path.join(gov, "MOCKA_ASSET_REGISTRY_20261010_001.csv")
    conn_path = os.path.join(gov, "MOCKA_CONNECTION_REGISTRY_20261010_001.csv")
    path_of, file_asset, dir_asset = {}, {}, {}
    status = {"asset_registry": "MISSING", "connection_registry": "MISSING"}
    if os.path.exists(asset_path):
        status["asset_registry"] = "READ"
        with open(asset_path, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                path_of[r["asset_id"]] = (r["asset_type"], r["canonical_path"])
                if r["asset_type"] == "FILE":
                    file_asset[r["canonical_path"]] = r["asset_id"]
                elif r["asset_type"] == "DIRECTORY":
                    dir_asset[r["canonical_path"]] = r["asset_id"]
    edges = []
    if os.path.exists(conn_path):
        status["connection_registry"] = "READ"
        with open(conn_path, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                s = path_of.get(r["source_id"])
                t = path_of.get(r["target_id"])
                if not s or not t:
                    continue
                if s[0] not in ("FILE", "DIRECTORY", "CLASS", "FUNCTION", "METHOD") or t[0] not in ("FILE", "DIRECTORY", "CLASS", "FUNCTION", "METHOD"):
                    continue
                if r["relation"] == "CONTAINS":
                    continue  # structural containment is already shown via the directory tree
                edges.append((s[1], t[1], r["relation"], r["evidence_kind"], r["status"], r["line"],
                              r["source_id"], r["target_id"]))
    return file_asset, dir_asset, edges, status


LINK_RX = re.compile(r"\]\(([^)\s]+)\)")
TICK_RX = re.compile(r"`([^`\s]+)`")


def load_mapping_docs(root):
    """
    Map repo-relative file path -> sorted list of mapping/*.md files that reference it.
    A reference counts only when it is a markdown link target or a backtick path that resolves
    (relative to mapping/ for links, relative to the repo root for backtick paths) to that file.
    Bare file names are not matched (they are ambiguous).
    """
    out = collections.defaultdict(set)
    mdir = os.path.join(root, "mapping")
    if not os.path.isdir(mdir):
        return out
    for f in sorted(os.listdir(mdir)):
        if not f.endswith(".md"):
            continue
        text = open(os.path.join(mdir, f), encoding="utf-8", errors="replace").read()
        for tgt in LINK_RX.findall(text):
            if tgt.startswith(("http://", "https://", "#", "mailto:")):
                continue
            tgt = tgt.split("#")[0]
            out[os.path.normpath(os.path.join("mapping", tgt)).replace("\\", "/")].add(f)
        for tok in TICK_RX.findall(text):
            if "/" in tok and not tok.startswith(("http", "/")) and "*" not in tok:
                out[os.path.normpath(tok).replace("\\", "/")].add(f)
    return out


def git_first_added(root):
    out = {}
    cur = None
    for line in git(root, ["log", "--all", "--diff-filter=A", "--name-only", "--format=@@%h %ad", "--date=short"]).splitlines():
        if line.startswith("@@"):
            parts = line[2:].split(" ", 1)
            cur = (parts[0], parts[1] if len(parts) > 1 else "")
        elif line.strip() and cur:
            out[line.strip().strip('"')] = cur  # later lines are older
    return out


class BuildError(Exception):
    pass


def _walk(root):
    """Yield (rel_path, full_path, stat) for in-scope files; record excluded dirs and unreadable dirs."""
    excluded = {}
    errors = []
    for dp, dn, fn in os.walk(root, onerror=lambda e: errors.append(str(e.filename))):
        keep = []
        for d in dn:
            full = os.path.join(dp, d)
            if d in EXCLUDED_DIRS or VENV_LIKE_RX.search(d) or os.path.abspath(full) == SELF_DATA_DIR:
                rel = os.path.relpath(full, root).replace("\\", "/")
                cnt = sum(len(f2) for _, _, f2 in os.walk(full))
                excluded[rel] = cnt
            else:
                keep.append(d)
        dn[:] = keep
        for f in fn:
            full = os.path.join(dp, f)
            rel = os.path.relpath(full, root).replace("\\", "/")
            try:
                st = os.stat(full)
            except OSError as exc:
                errors.append(rel + ": " + type(exc).__name__)
                continue
            yield rel, full, st
    return excluded, errors


def _read_content(full, rel, ext):
    """Return (status, text). Sensitive names and non-text types are never read."""
    if SENSITIVE_RX.search(rel) and not rel.endswith(".example"):
        return "NOT_INDEXED_SENSITIVE_NAME", ""
    if rel.split("/")[-1].startswith(".env"):
        return "NOT_INDEXED_SENSITIVE_NAME", ""
    if ext not in TEXT_EXT:
        return "NOT_INDEXED_TYPE", ""
    try:
        size = os.path.getsize(full)
        if size > MAX_CONTENT_BYTES:
            return "NOT_INDEXED_TOO_LARGE", ""
        with open(full, "rb") as fh:
            raw = fh.read()
    except OSError:
        return "ACCESS_ERROR", ""
    try:
        return "INDEXED", raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return "UNPARSEABLE_NOT_UTF8", ""


def build_or_update(root=DEFAULT_ROOT, db_path=DEFAULT_DB, rebuild=False, with_content=True):
    """
    Transactional update. On any failure the previous committed index is kept and meta status is FAILED.
    rebuild=True builds a fresh database in a temp file and replaces the old one atomically.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    target = db_path
    tmp = None
    if rebuild:
        tmp = db_path + ".building"
        if os.path.exists(tmp):
            os.remove(tmp)
        target = tmp
    conn = sqlite3.connect(target, timeout=30)
    try:
        conn.executescript(SCHEMA)
        conn.commit()
        result = _apply(conn, root, with_content)
        if rebuild:
            conn.close()
            conn = None
            os.replace(tmp, db_path)
        return result
    except Exception as exc:  # any failure must be visible, never reported as success
        if conn is not None:
            try:
                conn.rollback()
                conn.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('status','FAILED')")
                conn.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('last_error',?)", (str(exc)[:500],))
                conn.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('failed_at',?)", (now_iso(),))
                conn.commit()
            except sqlite3.Error:
                pass
        if rebuild and tmp and os.path.exists(tmp):
            try:
                if conn is not None:
                    conn.close()
                conn = None
                os.remove(tmp)
            except OSError:
                pass
        raise BuildError("index build failed: %s" % exc) from exc
    finally:
        if conn is not None:
            conn.close()


def _apply(conn, root, with_content):
    started = now_iso()
    file_asset, dir_asset, edges, reg_status = load_registry(root)
    mapping_texts = load_mapping_docs(root)
    head = git(root, ["rev-parse", "HEAD"]).strip()
    prev_head = conn.execute("SELECT value FROM meta WHERE key='git_head'").fetchone()
    # git history (a few seconds) is read lazily, only when an added/changed tracked file needs it
    first_added = None
    tracked = set(git(root, ["ls-files"]).splitlines())
    untracked = set(git(root, ["ls-files", "--others", "--exclude-standard"]).splitlines())

    existing = {r[0]: (r[1], r[2]) for r in conn.execute("SELECT path, size, mtime_ns FROM files")}
    seen = set()
    stats = {"scanned": 0, "added": 0, "changed": 0, "unchanged": 0, "removed": 0,
             "content_indexed": 0, "content_skipped": 0}
    walk_errors = []
    excluded, errs = {}, []
    gen = _walk(root)
    try:
        while True:
            rel, full, st = next(gen)
            stats["scanned"] += 1
            seen.add(rel)
            name = rel.split("/")[-1]
            ext = os.path.splitext(name)[1].lower()
            old = existing.get(rel)
            if old and old[0] == st.st_size and old[1] == st.st_mtime_ns:
                stats["unchanged"] += 1
                continue
            if old:
                stats["changed"] += 1
                conn.execute("DELETE FROM content_fts WHERE path=?", (rel,))
            else:
                stats["added"] += 1
            mtime = datetime.datetime.fromtimestamp(st.st_mtime, TZ)
            fd = DATE_RX.search(name)
            fdate = "%s-%s-%s" % fd.groups() if fd else ""
            if rel in tracked:
                git_state = "TRACKED"
            elif rel in untracked:
                git_state = "UNTRACKED"
            else:
                git_state = "NOT_LISTED_BY_GIT"
            cstatus = "NOT_REQUESTED"
            if with_content:
                cstatus, text = _read_content(full, rel, ext)
                if cstatus == "INDEXED":
                    conn.execute("INSERT INTO content_fts(path, body) VALUES(?,?)", (rel, text))
                    stats["content_indexed"] += 1
                else:
                    stats["content_skipped"] += 1
            d = rel.rsplit("/", 1)[0] if "/" in rel else "."
            # reached only for added/changed files (unchanged files continue above)
            if first_added is None and rel in tracked:
                first_added = git_first_added(root)
            fa = first_added.get(rel) if (first_added and rel in tracked) else None
            conn.execute(
                "INSERT OR REPLACE INTO files(path,name,name_norm,path_norm,dir,dir_norm,top,depth,ext,kind,size,"
                "mtime,mtime_date,mtime_ns,git_state,role_tags,asset_id,git_first_added,filename_date,content_status,"
                "mapped_docs,topic_tags,indexed_at) VALUES(%s)" % ",".join("?" * 23),
                (rel, name, norm(name), norm(rel), d, norm(d), rel.split("/")[0] if "/" in rel else "(root)",
                 rel.count("/"), ext, KIND_BY_EXT.get(ext, "other"), st.st_size, mtime.isoformat(timespec="seconds"),
                 mtime.date().isoformat(), st.st_mtime_ns, git_state,
                 ";".join(role_tags(rel, name, ext)), file_asset.get(rel, ""),
                 ("%s %s" % (fa[1], fa[0])).strip() if fa else "", fdate, cstatus,
                 ";".join(sorted(mapping_texts.get(rel, ()))),
                 ";".join(topic_tags(rel)), now_iso()))
    except StopIteration as stop:
        excluded, errs = stop.value if stop.value else ({}, [])
    # remove vanished files
    for rel in set(existing) - seen:
        conn.execute("DELETE FROM files WHERE path=?", (rel,))
        conn.execute("DELETE FROM content_fts WHERE path=?", (rel,))
        stats["removed"] += 1
    conn.execute("DELETE FROM dirs")
    conn.execute("DELETE FROM scope")
    conn.execute("DELETE FROM relations")
    counts = {}
    for rel, d in conn.execute("SELECT path, dir FROM files").fetchall():
        counts[d] = counts.get(d, 0) + 1
    for d, c in counts.items():
        parts = d.split("/") if d != "." else []
        for i in range(len(parts) + 1):
            anc = "/".join(parts[:i]) if i else "."
            conn.execute("INSERT OR IGNORE INTO dirs(path,parent,depth,direct_files,recursive_files,asset_id) VALUES(?,?,?,?,0,?)",
                         (anc, ("" if anc == "." else (anc.rsplit("/", 1)[0] if "/" in anc else ".")),
                          0 if anc == "." else anc.count("/") + 1, 0, dir_asset.get(anc, "")))
        conn.execute("UPDATE dirs SET direct_files = direct_files + ? WHERE path=?", (c, d))
    for anc_path, in conn.execute("SELECT path FROM dirs").fetchall():
        if anc_path == ".":
            rec = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
        else:
            prefix = anc_path + "/"  # substr comparison: no LIKE wildcard issues with _ or %
            rec = conn.execute("SELECT COUNT(*) FROM files WHERE dir=? OR substr(dir,1,?)=?",
                               (anc_path, len(prefix), prefix)).fetchone()[0]
        conn.execute("UPDATE dirs SET recursive_files=? WHERE path=?", (rec, anc_path))
    for path_, cnt in excluded.items():
        conn.execute("INSERT INTO scope(path,reason,file_count) VALUES(?,?,?)", (path_, "EXCLUDED_BY_POLICY", cnt))
    for err in errs:
        rel_err = err.replace(root, "").lstrip("/\\").replace("\\", "/").split(": ")[0]
        conn.execute("INSERT OR IGNORE INTO scope(path,reason,file_count) VALUES(?,?,?)", (rel_err, "ACCESS_ERROR_NOT_INDEXED", 0))
    for e in edges:
        if e[0] in seen or e[1] in seen:
            conn.execute("INSERT INTO relations VALUES(?,?,?,?,?,?,?,?)", e)
    conn.execute("DELETE FROM meta WHERE key IN ('status','last_error','failed_at')")
    meta = {"status": "OK", "built_at": now_iso(), "started_at": started, "root": root, "git_head": head,
            "previous_git_head": prev_head[0] if prev_head else "", "registry": json.dumps(reg_status),
            "file_count": str(conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]),
            "dir_count": str(conn.execute("SELECT COUNT(*) FROM dirs").fetchone()[0]),
            "scope_excluded_dirs": str(len(excluded)), "scope_excluded_files": str(sum(excluded.values())),
            "relations": str(conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0]),
            "walk_errors": str(len(errs)), "last_stats": json.dumps(stats)}
    for k, v in meta.items():
        conn.execute("INSERT OR REPLACE INTO meta(key,value) VALUES(?,?)", (k, v))
    conn.commit()
    return {"status": "OK", "stats": stats, "meta": meta, "walk_errors": errs[:20]}


def _tokens(q):
    return [t for t in norm(q).split() if t]


def search(db_path, q="", ext="", kind="", dir_prefix="", size_min=None, size_max=None,
           mtime_from="", mtime_to="", role="", asset="", topic="", content=False,
           limit=50, offset=0):
    conn = sqlite3.connect("file:%s?mode=ro" % db_path.replace("\\", "/"), uri=True, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        where, args = [], []
        for t in _tokens(q):
            if content:
                continue
            where.append("(instr(name_norm, ?) > 0 OR instr(path_norm, ?) > 0)")
            args += [t, t]
        if ext:
            exts = [("." + e.strip().lstrip(".").lower()) for e in ext.split(",") if e.strip()]
            where.append("ext IN (%s)" % ",".join("?" * len(exts)))
            args += exts
        if kind:
            where.append("kind = ?")
            args.append(kind)
        if dir_prefix:
            dp = norm(dir_prefix).strip("/")
            where.append("(dir_norm = ? OR instr(dir_norm, ?) = 1)")
            args += [dp, dp + "/"]
        if size_min is not None:
            where.append("size >= ?")
            args.append(int(size_min))
        if size_max is not None:
            where.append("size <= ?")
            args.append(int(size_max))
        if mtime_from:
            where.append("mtime_date >= ?")
            args.append(mtime_from)
        if mtime_to:
            where.append("mtime_date <= ?")
            args.append(mtime_to)
        if role:
            where.append("instr(';' || role_tags || ';', ?) > 0")
            args.append(";" + role + ";")
        if asset:
            where.append("asset_id = ?")
            args.append(asset)
        if topic:
            where.append("instr(';' || topic_tags || ';', ?) > 0")
            args.append(";" + topic + ";")
        if content:
            toks = _tokens(q)
            if not toks:
                raise ValueError("content search needs a query")
            match = " AND ".join('"%s"' % t.replace('"', '""') for t in toks)
            where.append("path IN (SELECT path FROM content_fts WHERE content_fts MATCH ?)")
            args.append(match)
        if not where:
            raise ValueError("指定された条件がありません。検索語またはフィルタを1つ以上指定してください。")
        wsql = " AND ".join(where)
        total = conn.execute("SELECT COUNT(*) FROM files WHERE " + wsql, args).fetchone()[0]
        rows = conn.execute(
            "SELECT path,name,dir,ext,kind,size,mtime,git_state,role_tags,asset_id,git_first_added,filename_date,"
            "content_status,mapped_docs,topic_tags FROM files WHERE " + wsql +
            " ORDER BY (name_norm = ?) DESC, length(path) ASC, path ASC LIMIT ? OFFSET ?",
            args + [norm(q), int(limit), int(offset)]).fetchall()
        items = [dict(r) for r in rows]
        for it in items:
            it["role_tags"] = it["role_tags"].split(";") if it["role_tags"] else []
            it["mapped_docs"] = [x for x in it["mapped_docs"].split(";") if x] if it["mapped_docs"] else []
            it["topic_tags"] = [x for x in it["topic_tags"].split(";") if x] if it["topic_tags"] else []
            full = _memory_trace(conn, it["path"]) if it["path"] else None
            if full is not None:
                # list view carries only the summary; full links stay on /api/item
                it["memory_trace_summary"] = {k: full.get(k) for k in ("status", "asset_id", "summary", "counts")}
        return {"total": total, "items": items, "limit": int(limit), "offset": int(offset)}
    finally:
        conn.close()


def status(db_path):
    if not os.path.exists(db_path):
        return {"status": "NOT_BUILT", "db": db_path}
    conn = sqlite3.connect("file:%s?mode=ro" % db_path.replace("\\", "/"), uri=True, timeout=30)
    try:
        meta = dict(conn.execute("SELECT key, value FROM meta").fetchall())
        meta["db"] = db_path
        meta["db_bytes"] = os.path.getsize(db_path)
        meta["scope"] = [dict(zip(("path", "reason", "file_count"), r)) for r in
                         conn.execute("SELECT path, reason, file_count FROM scope ORDER BY file_count DESC").fetchall()]
        return meta
    finally:
        conn.close()


def item(db_path, path):
    conn = sqlite3.connect("file:%s?mode=ro" % db_path.replace("\\", "/"), uri=True, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        r = conn.execute("SELECT * FROM files WHERE path=?", (path,)).fetchone()
        if r is None:
            return None
        out = dict(r)
        out["role_tags"] = out["role_tags"].split(";") if out["role_tags"] else []
        out["mapped_docs"] = [x for x in (out["mapped_docs"] or "").split(";") if x]
        out["topic_tags"] = [x for x in (out["topic_tags"] or "").split(";") if x]
        out.pop("name_norm", None), out.pop("path_norm", None), out.pop("dir_norm", None)
        out["siblings_in_dir"] = conn.execute("SELECT COUNT(*) FROM files WHERE dir=?", (out["dir"],)).fetchone()[0]
        out["relations"] = [dict(x) for x in conn.execute(
            "SELECT src_path, dst_path, relation, evidence_kind, status, line, source_asset, target_asset "
            "FROM relations WHERE src_path=? OR dst_path=? LIMIT 200", (path, path)).fetchall()]
        out["children_dirs"] = []
        out["memory_trace"] = _memory_trace(conn, out["path"])
        return out
    finally:
        conn.close()


def _memory_trace(conn, path):
    """Attach the Mapping -> Memory -> Event -> Decision Outcome trace for a Memory store file.

    Reuses scripts/mapping_memory_trace.py (loaded by file path, no sys.path change).
    Returns None for files that are not a Memory store.
    """
    if not path.replace("\\", "/").endswith("memory/data/memory_store.json"):
        return None
    row = conn.execute("SELECT value FROM meta WHERE key='root'").fetchone()
    root = row[0] if row else ""
    # the tracer ships with this code (repo containing search_index/), not with the indexed tree
    code_repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tracer_path = os.path.join(code_repo, "scripts", "mapping_memory_trace.py")
    if not root or not os.path.exists(tracer_path):
        return {"status": "TRACER_NOT_AVAILABLE"}
    spec = importlib.util.spec_from_file_location("mapping_memory_trace", tracer_path)
    tracer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tracer)
    asset_id = tracer.asset_id_for_path(root, path)
    if asset_id is None:
        return {"status": "ASSET_NOT_IN_MAPPING_INDEX", "path": path}
    return tracer.trace(root, asset_id)


def directory(db_path, path):
    conn = sqlite3.connect("file:%s?mode=ro" % db_path.replace("\\", "/"), uri=True, timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        d = conn.execute("SELECT * FROM dirs WHERE path=?", (path,)).fetchone()
        if d is None:
            return None
        out = dict(d)
        out["subdirs"] = [dict(x) for x in conn.execute(
            "SELECT path, direct_files, recursive_files, asset_id FROM dirs WHERE parent=? ORDER BY path LIMIT 500",
            (path,)).fetchall()]
        out["files"] = [dict(x) for x in conn.execute(
            "SELECT path, name, size, mtime, kind, role_tags FROM files WHERE dir=? ORDER BY name LIMIT 500",
            (path,)).fetchall()]
        return out
    finally:
        conn.close()

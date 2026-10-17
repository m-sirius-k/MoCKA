"""
Tests for the MoCKA file search index. Run from the repository root:

  python -B -m pytest -p no:cacheprovider search_index/test_search_index.py

All trees are synthetic and live under pytest's tmp_path (outside the repository).
Nothing here reads or writes data/mocka_events.db, the Decision Ledger, Event Store, Memory, or HG records.
"""
import csv
import json
import os
import threading
import urllib.error
import urllib.request

import pytest

from search_index import core, server

SECRET_VALUE = "TOPSECRET-VALUE-7f3a"


def _write(path, text, mtime=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    if mtime is not None:
        os.utime(path, (mtime, mtime))


@pytest.fixture
def tree(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _write(str(root / "mapping" / "MASTER_MAP.md"), "# MASTER\nindex of memory and gates\n")
    _write(str(root / "core" / "runtime_gate.py"), "class RuntimeGate:\n    pass\n")
    _write(str(root / "tests" / "test_gate.py"), "def test_ok():\n    assert True\n")
    _write(str(root / "データ" / "台帳メモ.md"), "日本語の本文 ledger memo\n")
    _write(str(root / "with space" / "Report File.txt"), "Fullwidth search target\n")
    _write(str(root / "archive" / "old_note.md"), "archived text ARCHIVEONLY\n")
    _write(str(root / ".wsl_ots_venv" / "lib" / "x.py"), "venvonly = 1\n")
    _write(str(root / "keys" / "operational_key.private.pem"), SECRET_VALUE + "\n")
    _write(str(root / ".env"), "API_KEY=" + SECRET_VALUE + "\n")
    _write(str(root / "data" / "big.json"), "{}\n")
    return root


@pytest.fixture
def db(tmp_path):
    return str(tmp_path / "idx" / "search.sqlite")


def build(root, db, **kw):
    return core.build_or_update(str(root), db, **kw)


def names(res):
    return sorted(i["path"] for i in res["items"])


# ---- build and basic search --------------------------------------------------

def test_full_build_indexes_text_and_records_exclusions(tree, db):
    res = build(tree, db, rebuild=True)
    assert res["status"] == "OK"
    assert res["stats"]["scanned"] >= 8
    st = core.status(db)
    assert st["status"] == "OK"
    reasons = {x["reason"] for x in st["scope"]}
    assert "EXCLUDED_BY_POLICY" in reasons
    excluded_paths = {x["path"] for x in st["scope"]}
    assert "archive" in excluded_paths
    assert any("venv" in p for p in excluded_paths)


def test_partial_name_match_is_case_and_width_insensitive(tree, db):
    build(tree, db, rebuild=True)
    assert "mapping/MASTER_MAP.md" in names(core.search(db, q="master"))
    # full-width letters fold to ASCII under NFKC
    assert "with space/Report File.txt" in names(core.search(db, q="ＲＥＰＯＲＴ"))


def test_japanese_and_spaced_paths_are_found(tree, db):
    build(tree, db, rebuild=True)
    assert "データ/台帳メモ.md" in names(core.search(db, q="台帳"))
    assert "with space/Report File.txt" in names(core.search(db, q="report file"))


def test_multi_token_is_and(tree, db):
    build(tree, db, rebuild=True)
    assert names(core.search(db, q="gate test")) == ["tests/test_gate.py"]
    assert names(core.search(db, q="gate zzzz")) == []


def test_filters_extension_kind_dir_role_and_size(tree, db):
    build(tree, db, rebuild=True)
    assert all(i["ext"] == ".py" for i in core.search(db, ext="py")["items"])
    assert "core/runtime_gate.py" in names(core.search(db, kind="source"))
    assert names(core.search(db, dir_prefix="tests")) == ["tests/test_gate.py"]
    assert "tests/test_gate.py" in names(core.search(db, role="TEST"))
    # big.json holds "{}" plus a newline, i.e. 3 bytes
    assert names(core.search(db, size_max=3, dir_prefix="data")) == ["data/big.json"]
    assert core.search(db, size_max=2, dir_prefix="data")["total"] == 0
    assert core.search(db, size_min=10**9)["total"] == 0


def test_mtime_filter_uses_observed_mtime(tree, db):
    _write(str(tree / "old" / "dated.md"), "x\n", mtime=1_600_000_000)
    build(tree, db, rebuild=True)
    got = core.search(db, q="dated", mtime_to="2021-01-01")
    assert names(got) == ["old/dated.md"]
    assert core.search(db, q="dated", mtime_from="2021-01-01")["total"] == 0


def test_empty_query_without_filter_is_rejected(tree, db):
    build(tree, db, rebuild=True)
    with pytest.raises(ValueError):
        core.search(db)


def test_pagination_limit_and_offset(tree, db):
    for i in range(12):
        _write(str(tree / "many" / ("item%02d.md" % i)), "x\n")
    build(tree, db, rebuild=True)
    first = core.search(db, q="item", limit=5, offset=0)
    second = core.search(db, q="item", limit=5, offset=5)
    assert first["total"] == 12 and len(first["items"]) == 5
    assert not set(names(first)) & set(names(second))


def test_content_search_only_indexed_text(tree, db):
    build(tree, db, rebuild=True)
    hit = core.search(db, q="ledger", content=True)
    assert "データ/台帳メモ.md" in names(hit)
    assert "mapping/MASTER_MAP.md" in names(core.search(db, q="memory", content=True))
    # excluded trees are not content-indexed
    assert core.search(db, q="ARCHIVEONLY", content=True)["total"] == 0


# ---- security: secrets never enter the index --------------------------------

def test_sensitive_names_are_located_but_content_never_indexed(tree, db):
    build(tree, db, rebuild=True)
    pem = core.item(db, "keys/operational_key.private.pem")
    env = core.item(db, ".env")
    assert pem is not None and pem["content_status"] == "NOT_INDEXED_SENSITIVE_NAME"
    assert env is not None and env["content_status"] == "NOT_INDEXED_SENSITIVE_NAME"
    assert core.search(db, q=SECRET_VALUE.lower(), content=True)["total"] == 0
    with open(db, "rb") as fh:
        assert SECRET_VALUE.encode("ascii") not in fh.read()


def test_secret_value_does_not_appear_in_status_or_errors(tree, db):
    build(tree, db, rebuild=True)
    blob = json.dumps(core.status(db), ensure_ascii=False)
    assert SECRET_VALUE not in blob


# ---- incremental update ------------------------------------------------------

def test_incremental_add_change_remove(tree, db):
    build(tree, db, rebuild=True)
    _write(str(tree / "new" / "added_note.md"), "uniqueaddedtoken\n")
    res = build(tree, db, rebuild=False)
    assert res["stats"]["added"] == 1 and res["stats"]["changed"] == 0
    assert "new/added_note.md" in names(core.search(db, q="added_note"))
    assert "new/added_note.md" in names(core.search(db, q="uniqueaddedtoken", content=True))

    _write(str(tree / "new" / "added_note.md"), "replacedtoken body\n")
    os.utime(str(tree / "new" / "added_note.md"), None)
    res = build(tree, db, rebuild=False)
    assert res["stats"]["changed"] == 1
    assert core.search(db, q="uniqueaddedtoken", content=True)["total"] == 0
    assert "new/added_note.md" in names(core.search(db, q="replacedtoken", content=True))

    os.remove(str(tree / "new" / "added_note.md"))
    res = build(tree, db, rebuild=False)
    assert res["stats"]["removed"] == 1
    assert core.search(db, q="added_note")["total"] == 0
    assert core.search(db, q="replacedtoken", content=True)["total"] == 0


def test_failed_update_keeps_previous_committed_index(tree, db, monkeypatch):
    build(tree, db, rebuild=True)
    before = core.search(db, q="gate")["total"]
    _write(str(tree / "boom.md"), "boom\n")
    real = core._read_content

    def failing(full, rel, ext):
        if rel == "boom.md":
            raise RuntimeError("injected failure")
        return real(full, rel, ext)

    monkeypatch.setattr(core, "_read_content", failing)
    with pytest.raises(core.BuildError):
        build(tree, db, rebuild=False)
    monkeypatch.undo()
    st = core.status(db)
    assert st["status"] == "FAILED"
    assert "injected failure" in st["last_error"]
    assert core.search(db, q="gate")["total"] == before  # old data still served
    assert core.search(db, q="boom")["total"] == 0  # partial update rolled back


def test_rebuild_failure_does_not_replace_existing_database(tree, db, monkeypatch):
    build(tree, db, rebuild=True)
    size_before = os.path.getsize(db)

    def boom(*a, **k):
        raise RuntimeError("injected rebuild failure")

    monkeypatch.setattr(core, "_apply", boom)
    with pytest.raises(core.BuildError):
        build(tree, db, rebuild=True)
    monkeypatch.undo()
    assert os.path.getsize(db) == size_before
    assert not os.path.exists(db + ".building")


# ---- navigation, mapping and relations ---------------------------------------

def _registry(root):
    gov = root / "docs" / "governance"
    gov.mkdir(parents=True, exist_ok=True)
    with open(str(gov / "MOCKA_ASSET_REGISTRY_20261010_001.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["asset_id", "asset_type", "name", "canonical_path"])
        w.writerow(["FILE-AAAAAAAAAA", "FILE", "runtime_gate.py", "core/runtime_gate.py"])
        w.writerow(["FILE-BBBBBBBBBB", "FILE", "test_gate.py", "tests/test_gate.py"])
        w.writerow(["DIR-CCCCCCCCCC", "DIRECTORY", "core", "core"])
    with open(str(gov / "MOCKA_CONNECTION_REGISTRY_20261010_001.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["edge_id", "source_id", "target_id", "relation", "source_path", "line", "evidence_kind", "confidence", "status", "runtime_status", "note"])
        w.writerow(["EDG-1", "FILE-BBBBBBBBBB", "FILE-AAAAAAAAAA", "IMPORTS", "tests/test_gate.py", "1", "STATIC_AST", "HIGH", "STATIC_CONFIRMED", "NOT_OBSERVED", ""])
        w.writerow(["EDG-2", "DIR-CCCCCCCCCC", "FILE-AAAAAAAAAA", "CONTAINS", "core", "", "STATIC_PATH", "HIGH", "STATIC_CONFIRMED", "NOT_OBSERVED", ""])


def test_mapping_asset_id_and_relations_come_from_existing_registry(tree, db):
    _registry(tree)
    build(tree, db, rebuild=True)
    it = core.item(db, "core/runtime_gate.py")
    assert it["asset_id"] == "FILE-AAAAAAAAAA"
    rels = it["relations"]
    assert any(r["relation"] == "IMPORTS" and r["src_path"] == "tests/test_gate.py" for r in rels)
    assert all(r["relation"] != "CONTAINS" for r in rels)  # containment is shown as the tree instead
    assert it["mapped_docs"] == []  # no mapping document mentions this path


def test_item_without_registry_has_no_invented_asset_id(tree, db):
    build(tree, db, rebuild=True)
    it = core.item(db, "core/runtime_gate.py")
    assert it["asset_id"] == ""


def test_directory_navigation(tree, db):
    build(tree, db, rebuild=True)
    d = core.directory(db, "tests")
    assert d["direct_files"] == 1
    root = core.directory(db, ".")
    assert root["recursive_files"] >= 8
    assert any(s["path"] == "tests" for s in core.directory(db, ".")["subdirs"])


def test_topic_tags_are_name_matches_only(tree, db):
    build(tree, db, rebuild=True)
    got = core.search(db, topic="gate")
    assert "core/runtime_gate.py" in names(got)


# ---- HTTP surface ------------------------------------------------------------

@pytest.fixture
def live(tree, db):
    build(tree, db, rebuild=True)
    srv = server.make_server("127.0.0.1", 0, db, str(tree))
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield "http://127.0.0.1:%d" % srv.server_address[1], srv
    srv.shutdown()
    srv.server_close()


def _get(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return r.status, r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")


def test_server_api_returns_metadata_and_never_file_content(live):
    base, _ = live
    code, body = _get(base + "/api/search?q=gate")
    assert code == 200
    data = json.loads(body)
    assert data["total"] >= 2
    code, body = _get(base + "/api/item?path=.env")
    assert code == 200 and SECRET_VALUE not in body
    code, body = _get(base + "/api/item?path=keys/operational_key.private.pem")
    assert code == 200 and SECRET_VALUE not in body


def test_server_rejects_bad_parameters_and_unknown_paths(live):
    base, _ = live
    code, body = _get(base + "/api/search?ext=py&size_min=abc")
    assert code == 400
    code, _ = _get(base + "/api/item?path=../../etc/passwd")
    assert code == 404
    code, _ = _get(base + "/nope")
    assert code == 404


def test_server_serves_ui_page(live):
    base, _ = live
    code, body = _get(base + "/")
    assert code == 200 and "MoCKA" in body


def test_server_refuses_non_loopback_bind(tree, db):
    with pytest.raises(SystemExit):
        server.make_server("0.0.0.0", 0, db, str(tree))


def test_server_update_endpoint_runs_incremental_update(live, tree):
    base, _ = live
    _write(str(tree / "via_api.md"), "apitoken\n")
    req = urllib.request.Request(base + "/api/update", method="POST", data=b"")
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode("utf-8"))
    assert data["status"] == "OK" and data["stats"]["added"] == 1
    code, body = _get(base + "/api/search?q=via_api")
    assert json.loads(body)["total"] == 1


def test_mapping_references_resolve_links_and_backticks_only(tree, db):
    _write(str(tree / "mapping" / "GUIDE.md"),
           "see [gate](../core/runtime_gate.py) and `core/runtime_gate.py`\n"
           "bare name runtime_gate.py is not a reference\n")
    build(tree, db, rebuild=True)
    it = core.item(db, "core/runtime_gate.py")
    assert it["mapped_docs"] == ["GUIDE.md"]
    assert core.item(db, "tests/test_gate.py")["mapped_docs"] == []


def _memory_trace_tree(tmp_path):
    """Synthetic repo with a Memory store, Mapping index, events, and ledger (all under tmp_path)."""
    import sqlite3
    root = tmp_path / "trace_repo"
    root.mkdir()
    _write(str(root / "mapping" / "ASSET_INDEX.json"), json.dumps({"assets": [
        {"asset_id": "A900", "path": "memory/data/memory_store.json"}]}))
    _write(str(root / "memory" / "data" / "memory_store.json"), json.dumps([
        {"memory_id": "M1", "content": {"execution_trace_id": "ETID_T1", "decision": "DEC_T1"}},
        {"memory_id": "M2", "content": {"execution_trace_id": "ETID_T2", "decision": "DEC_T2"}},
    ]))
    _write(str(root / "data" / "decisions" / "decision_ledger.jsonl"), '{"decision_id": "DEC_X"}\n')
    ev = root / "data" / "mocka_events.db"
    ev.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(ev))
    con.execute("create table events (event_id text, request_id text, free_note text)")
    con.execute("insert into events values ('E1','ETID_T1',"
                "'{\"record_type\":\"DECISION_OUTCOME\",\"outcome_id\":\"O1\",\"memory_id\":\"M1\","
                "\"match_status\":\"UNKNOWN_CONSEQUENCE\",\"actual_consequence\":\"UNKNOWN\"}')")
    con.commit()
    con.close()
    return root


def test_item_attaches_memory_trace_for_memory_store(tmp_path, db):
    root = _memory_trace_tree(tmp_path)
    build(root, db, rebuild=True)
    it = core.item(db, "memory/data/memory_store.json")
    mt = it["memory_trace"]
    assert mt["status"] == "TRACED"
    by_id = {l["memory_id"]: l for l in mt["links"]}
    assert by_id["M1"]["outcome_status"] == "MATCHED"
    assert by_id["M1"]["outcome"]["event_id"] == "E1"
    assert by_id["M2"]["outcome_status"] == "UNMATCHED"
    assert by_id["M2"]["outcome"] is None


def test_item_memory_trace_is_none_for_other_files(tmp_path, db):
    root = _memory_trace_tree(tmp_path)
    build(root, db, rebuild=True)
    assert core.item(db, "mapping/ASSET_INDEX.json")["memory_trace"] is None


def test_search_list_adds_summary_only_for_memory_store(tmp_path, db):
    root = _memory_trace_tree(tmp_path)
    _write(str(root / "notes" / "memory_store_plan.md"), "plan for memory_store\n")
    build(root, db, rebuild=True)
    res = core.search(db, q="memory_store")
    by_path = {it["path"]: it for it in res["items"]}
    mem = by_path["memory/data/memory_store.json"]["memory_trace_summary"]
    assert mem["status"] == "TRACED"
    assert mem["asset_id"] == "A900"
    assert "links" not in mem  # full links stay on /api/item
    assert "memory_trace_summary" not in by_path["notes/memory_store_plan.md"]
    assert "memory_trace" not in by_path["memory/data/memory_store.json"]


def test_list_counts_match_detail_counts(tmp_path, db):
    root = _memory_trace_tree(tmp_path)
    build(root, db, rebuild=True)
    listed = [i for i in core.search(db, q="memory_store")["items"]
              if i["path"] == "memory/data/memory_store.json"][0]["memory_trace_summary"]
    detail = core.item(db, "memory/data/memory_store.json")["memory_trace"]
    assert listed["counts"] == detail["counts"]
    assert "links" not in listed

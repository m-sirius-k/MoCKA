import importlib.util
import json
import sqlite3
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "living_context_snapshot.py"
SPEC = importlib.util.spec_from_file_location("living_context_snapshot", MODULE_PATH)
snapshot_module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(snapshot_module)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def test_build_snapshot_has_required_fields_and_never_mutates_sources(tmp_path):
    write_json(tmp_path / "data/MOCKA_OVERVIEW.json", {
        "current_phase": "Phase test",
        "current_issues": {"unknown": "needs review"},
        "next_actions": {"immediate": ["TODO_1: Human review"]},
    })
    write_json(tmp_path / "data/MOCKA_TODO.json", {
        "todos": [
            {"id": "TODO_1", "title": "Human Gate UI", "status": "進行中", "assigned_to": "Human Gate"},
            {"id": "TODO_2", "title": "Deferred", "status": "保留"},
        ],
        "completed": [{"id": "TODO_0", "title": "Done", "status": "完了"}],
    })
    write_json(tmp_path / "data/lever_essence.json", {})
    write_json(tmp_path / "runtime/main/ledger.json", [])
    (tmp_path / "gateway").mkdir()
    (tmp_path / "gateway/context_builder.py").write_text("# lineage", encoding="utf-8")
    db_path = tmp_path / "data/mocka_events.db"
    connection = sqlite3.connect(db_path)
    connection.execute("CREATE TABLE judgement_reason (id INTEGER PRIMARY KEY, event_id TEXT, decision TEXT, reason TEXT, created_at TEXT)")
    connection.execute("INSERT INTO judgement_reason VALUES (1, 'D-1', '保留', 'Human review pending', '2026-08-11T00:00:00')")
    connection.commit()
    connection.close()
    before = {path: path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}

    snapshot = snapshot_module.build_snapshot(tmp_path)

    required = {
        "schema_version", "project", "current_state", "completed", "active", "blocked",
        "decisions", "unknowns", "next_boundary", "human_gate_required",
    }
    assert required <= snapshot.keys()
    assert snapshot["schema_version"] == "MOCKA_LIVING_CONTEXT_SNAPSHOT_v1"
    assert snapshot["active"]["items"][0]["id"] == "TODO_1"
    assert snapshot["blocked"]["items"][0]["id"] == "TODO_2"
    assert snapshot["decisions"][0]["id"] == "D-1"
    assert snapshot["human_gate_required"] is True
    assert before == {path: path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}


def test_yaml_output_is_available_without_optional_dependencies(tmp_path, capsys):
    write_json(tmp_path / "data/MOCKA_OVERVIEW.json", {"current_phase": "Phase test"})
    write_json(tmp_path / "data/MOCKA_TODO.json", {"todos": [], "completed": []})
    snapshot = snapshot_module.build_snapshot(tmp_path)
    yaml_text = snapshot_module.to_yaml(snapshot)
    assert "schema_version: \"MOCKA_LIVING_CONTEXT_SNAPSHOT_v1\"" in yaml_text

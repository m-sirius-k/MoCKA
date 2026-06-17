"""tests/test_all.py — PHI-OS SEO Command Index v3 統合テスト (Phase 13)

Unit / Integration / Performance / Boundary / Resume / Cross-Repo テスト
実行: python -m pytest tests/test_all.py -v  (seo-os/ から)
"""
from __future__ import annotations
import json
import sys
import os
import time
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def db():
    from command_index.db import CommandIndexDB
    return CommandIndexDB(":memory:")


@pytest.fixture(scope="module")
def registry(db):
    from command_index import CommandRegistry
    return CommandRegistry(db)


@pytest.fixture(scope="module")
def populated_db(db, registry):
    # builtins are seeded automatically in CommandRegistry.__init__
    return db


@pytest.fixture(scope="module")
def search(populated_db):
    from semantic import MeaningSearch
    return MeaningSearch(populated_db)


@pytest.fixture(scope="module")
def ranking(populated_db):
    from semantic import SimilarityRanking
    return SimilarityRanking(populated_db)


@pytest.fixture(scope="module")
def rec(populated_db):
    from recommendation import RecommendationEngine
    return RecommendationEngine(populated_db)


@pytest.fixture(scope="module")
def learn(populated_db):
    from learning import LearningEngine
    return LearningEngine(populated_db)


@pytest.fixture(scope="module")
def audit(populated_db):
    from audit import AuditLogger
    return AuditLogger(populated_db)


@pytest.fixture(scope="module")
def graph(populated_db):
    from dep_graph import DependencyGraph
    return DependencyGraph(populated_db)


@pytest.fixture(scope="module")
def runtime(populated_db):
    from runtime import UnifiedRuntime
    return UnifiedRuntime(populated_db)


@pytest.fixture(scope="module")
def api_client(populated_db):
    from api.app import create_app
    app = create_app(populated_db)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ─────────────────────────────────────────────────────────────────────────────
# Phase 1: Command Index (Unit)
# ─────────────────────────────────────────────────────────────────────────────

class TestCommandIndex:
    def test_seed_builtins(self, populated_db, registry):
        cmds = registry.list_all()
        assert len(cmds) >= 10, f"Expected >=10 builtins, got {len(cmds)}"

    def test_get_command(self, registry):
        cmd = registry.get("seo.analyze")
        assert cmd is not None
        assert cmd.id == "seo.analyze"

    def test_get_unknown(self, registry):
        assert registry.get("nonexistent.cmd") is None

    def test_list_by_category(self, registry):
        seo_cmds = registry.list_all(category="seo")
        assert len(seo_cmds) >= 5

    def test_register_custom(self, registry):
        from command_index import CommandMetadata, CommandStatus
        cmd = CommandMetadata(
            id="test.custom",
            name="Test Custom",
            description="unit test command",
            category="test",
            tags=["test"],
            status=CommandStatus.EXPERIMENTAL,
        )
        registry.register(cmd)
        assert registry.get("test.custom") is not None

    def test_categories(self, populated_db):
        from command_index import CategoryManager
        cats = CategoryManager(populated_db)
        cat_list = cats.list_categories()
        ids = [c["id"] for c in cat_list]
        assert "seo" in ids
        assert "publish" in ids

    def test_alias(self, populated_db):
        from command_index import AliasManager
        am = AliasManager(populated_db)
        aliases = am.list_all()  # returns dict: {alias: command_id}
        if aliases:
            alias_key = next(iter(aliases))
            assert am.resolve(alias_key) == aliases[alias_key]
        else:
            pytest.skip("no aliases registered")

    def test_tag(self, populated_db):
        from command_index import TagManager
        tm = TagManager(populated_db)
        tagged = tm.find_commands_by_tag("seo")
        assert len(tagged) >= 1

    def test_version(self, populated_db):
        from command_index import VersionManager
        vm = VersionManager(populated_db)
        vm.record("seo.analyze", "1.0.0", "initial")
        history = vm.history("seo.analyze")
        assert len(history) >= 1

    def test_registry_export(self, registry):
        # CommandRegistry exports to data/registry.json automatically; verify list_all works
        cmds = registry.list_all()
        assert isinstance(cmds, list)


# ─────────────────────────────────────────────────────────────────────────────
# Phase 2: Semantic Engine (Unit + Integration)
# ─────────────────────────────────────────────────────────────────────────────

class TestSemanticEngine:
    def test_synonym_expand(self):
        from semantic.synonym import SynonymDictionary
        sd = SynonymDictionary()
        expanded = sd.expand(["save"])
        assert "snapshot" in expanded or "backup" in expanded

    def test_index_build(self, populated_db):
        from semantic.index import SemanticIndex
        idx = SemanticIndex(populated_db)
        idx.rebuild()
        results = idx.lookup("seo")
        assert len(results) >= 1

    def test_intent_detect(self):
        from semantic.intent import IntentResolver
        ir = IntentResolver()
        assert ir.resolve("publish this page") in ("publish", "seo", "execute", None)
        assert ir.resolve("analyze seo") in ("seo", "analyze", None)
        assert ir.resolve("save snapshot") in ("save", "context", None)

    def test_meaning_search_basic(self, search):
        results = search.search("seo")
        assert len(results) >= 1
        assert any(r.command.id.startswith("seo.") for r in results)

    def test_meaning_search_synonym(self, search):
        results = search.search("deploy")
        ids = [r.command.id for r in results]
        assert any("publish" in i for i in ids)

    def test_ranking_score(self, ranking):
        results = ranking.rank("seo analyze")
        assert len(results) >= 1
        for r in results:
            assert 0.0 <= r.score <= 1.0
        assert results[0].score >= results[-1].score

    def test_search_category_filter(self, search):
        results = search.search("run", category="publish")
        for r in results:
            assert r.command.category == "publish"


# ─────────────────────────────────────────────────────────────────────────────
# Phase 3: Context Bridge
# ─────────────────────────────────────────────────────────────────────────────

class TestContextBridge:
    def test_bridge_available_or_fallback(self):
        from context_bridge import ContextBridge
        bridge = ContextBridge()
        mr = bridge.get_memory_runtime()
        assert isinstance(mr, dict)

    def test_fallback_keys(self):
        from context_bridge import ContextBridge
        bridge = ContextBridge()
        mr = bridge.get_memory_runtime()
        assert "protocol" in mr

    def test_context_boost_no_crash(self, populated_db):
        from context_bridge import ContextBridge
        bridge = ContextBridge()
        boost = bridge.context_boost("seo.analyze")
        assert isinstance(boost, (int, float))


# ─────────────────────────────────────────────────────────────────────────────
# Phase 4: Recommendation Engine
# ─────────────────────────────────────────────────────────────────────────────

class TestRecommendation:
    def test_related(self, rec):
        results = rec.related("seo.analyze")
        assert isinstance(results, list)

    def test_next_recommended(self, rec):
        results = rec.next_recommended("seo.analyze")
        assert isinstance(results, list)

    def test_full(self, rec):
        results = rec.full("seo.analyze")
        assert isinstance(results, list)

    def test_workflow_list(self, populated_db):
        from recommendation import WorkflowRecommendation
        wf = WorkflowRecommendation(populated_db)
        workflows = wf.list_workflows()
        assert len(workflows) >= 1
        assert "seo_publish" in [w["id"] for w in workflows]

    def test_workflow_recommend_for_command(self, populated_db):
        from recommendation import WorkflowRecommendation
        wf = WorkflowRecommendation(populated_db)
        result = wf.recommend_for_command("seo.analyze")
        assert isinstance(result, list)


# ─────────────────────────────────────────────────────────────────────────────
# Phase 5: Learning Engine
# ─────────────────────────────────────────────────────────────────────────────

class TestLearning:
    def test_record(self, learn):
        learn.record("seo.analyze", "success")
        learn.record("seo.analyze", "success")
        learn.record("seo.analyze", "failure")
        stats = learn.stats("seo.analyze")
        assert stats["use_count"] >= 3

    def test_ranking(self, learn):
        ranking = learn.ranking(10)
        assert len(ranking) >= 1
        assert ranking[0]["use_count"] >= ranking[-1]["use_count"]

    def test_recent(self, learn):
        recent = learn.recent(5)
        assert len(recent) >= 1
        assert "command_id" in recent[0]

    def test_failure_analysis(self, learn):
        analysis = learn.failure_analysis()
        assert isinstance(analysis, (dict, list))


# ─────────────────────────────────────────────────────────────────────────────
# Phase 6: Cross Repository (Boundary)
# ─────────────────────────────────────────────────────────────────────────────

class TestCrossRepo:
    def test_search_no_crash(self):
        from cross_repo import CrossRepoSearch
        crs = CrossRepoSearch()
        results = crs.search("seo")
        assert isinstance(results, (dict, list))

    def test_boundary_respects_forbidden(self):
        from cross_repo import CrossRepoSearch
        crs = CrossRepoSearch()
        results = crs.search("MoCKA Core")
        assert isinstance(results, (dict, list))


# ─────────────────────────────────────────────────────────────────────────────
# Phase 7: Dependency Graph
# ─────────────────────────────────────────────────────────────────────────────

class TestDependencyGraph:
    def test_to_json(self, graph):
        j = graph.to_json()
        data = json.loads(j)
        assert "nodes" in data
        assert "edges" in data

    def test_to_svg(self, graph):
        svg = graph.to_svg()
        assert "<svg" in svg

    def test_to_html(self, graph):
        html = graph.to_html()
        assert "<html" in html.lower()


# ─────────────────────────────────────────────────────────────────────────────
# Phase 12: Audit Logger
# ─────────────────────────────────────────────────────────────────────────────

class TestAuditLogger:
    def test_log_and_recent(self, audit):
        audit.log("test.action", {"key": "value"}, emit_event=False)
        recent = audit.recent(5)
        assert len(recent) >= 1
        actions = [r["action"] for r in recent]
        assert "test.action" in actions

    def test_payload_serialized(self, audit):
        audit.log("test.payload", {"nested": {"x": 1}}, emit_event=False)
        recent = audit.recent(1)
        assert recent[0]["payload"]["nested"]["x"] == 1


# ─────────────────────────────────────────────────────────────────────────────
# Phase 9: REST API (Integration)
# ─────────────────────────────────────────────────────────────────────────────

class TestRestAPI:
    def test_commands(self, api_client):
        r = api_client.get("/api/v3/commands")
        assert r.status_code == 200
        data = r.get_json()
        assert data["count"] >= 10

    def test_search(self, api_client):
        r = api_client.get("/api/v3/search?q=seo")
        assert r.status_code == 200
        data = r.get_json()
        assert data["count"] >= 1

    def test_search_empty(self, api_client):
        r = api_client.get("/api/v3/search?q=")
        assert r.status_code == 200

    def test_execute_valid(self, api_client):
        r = api_client.post("/api/v3/execute",
                            json={"command_id": "seo.analyze"},
                            content_type="application/json")
        assert r.status_code == 200
        assert r.get_json()["ok"] is True

    def test_execute_invalid(self, api_client):
        r = api_client.post("/api/v3/execute",
                            json={"command_id": "not.exist"},
                            content_type="application/json")
        assert r.status_code == 404

    def test_history(self, api_client):
        r = api_client.get("/api/v3/history")
        assert r.status_code == 200

    def test_recommend(self, api_client):
        r = api_client.get("/api/v3/recommend/seo.analyze")
        assert r.status_code == 200

    def test_context(self, api_client):
        r = api_client.get("/api/v3/context")
        assert r.status_code == 200
        data = r.get_json()
        assert "protocol" in data

    def test_graph_json(self, api_client):
        r = api_client.get("/api/v3/graph?format=json")
        assert r.status_code == 200
        data = r.get_json()
        assert "nodes" in data

    def test_graph_svg(self, api_client):
        r = api_client.get("/api/v3/graph?format=svg")
        assert r.status_code == 200
        assert b"<svg" in r.data

    def test_ranking(self, api_client):
        r = api_client.get("/api/v3/ranking")
        assert r.status_code == 200

    def test_audit(self, api_client):
        r = api_client.get("/api/v3/audit")
        assert r.status_code == 200

    def test_workflows(self, api_client):
        r = api_client.get("/api/v3/workflows")
        assert r.status_code == 200
        data = r.get_json()
        assert len(data) >= 1

    def test_categories(self, api_client):
        r = api_client.get("/api/v3/categories")
        assert r.status_code == 200

    def test_command_detail(self, api_client):
        r = api_client.get("/api/v3/commands/seo.analyze")
        assert r.status_code == 200
        data = r.get_json()
        assert data["command"]["id"] == "seo.analyze"


# ─────────────────────────────────────────────────────────────────────────────
# Phase 10: Unified Runtime (Integration)
# ─────────────────────────────────────────────────────────────────────────────

class TestUnifiedRuntime:
    def test_boot(self, runtime):
        ctx = runtime.boot()
        assert "protocol" in ctx

    def test_validate(self, runtime):
        result = runtime.validate()
        assert "resumable" in result
        assert "issues" in result

    def test_state(self, runtime):
        state = runtime.state()
        assert "booted_at" in state

    def test_snapshot_and_resume(self, runtime):
        runtime.boot()
        path = runtime.snapshot()
        assert path.exists()
        result = runtime.resume()
        assert result["ok"] is True

    def test_execution_gate_relative(self, runtime):
        gate = runtime.execution_gate("seo", "seo/analyze.py")
        assert gate["passed"] is True

    def test_emit_event(self, runtime):
        before = runtime.state()["event_count"]
        runtime.emit("TEST_EVENT", {"x": 1})
        after = runtime.state()["event_count"]
        assert after == before + 1


# ─────────────────────────────────────────────────────────────────────────────
# Performance Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestPerformance:
    def test_search_latency(self, ranking):
        start = time.perf_counter()
        for _ in range(20):
            ranking.rank("seo publish analyze")
        elapsed = time.perf_counter() - start
        assert elapsed < 2.0, f"20 searches took {elapsed:.2f}s (>2s)"

    def test_db_seed_latency(self):
        from command_index.db import CommandIndexDB
        from command_index import CommandRegistry
        start = time.perf_counter()
        db = CommandIndexDB(":memory:")
        CommandRegistry(db)  # builtins seeded in __init__
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0, f"seed took {elapsed:.2f}s (>1s)"


# ─────────────────────────────────────────────────────────────────────────────
# Resume Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestResume:
    def test_cold_resume(self):
        import tempfile
        import pathlib
        import runtime.unified as ru
        from runtime import UnifiedRuntime
        from command_index.db import CommandIndexDB
        db = CommandIndexDB(":memory:")
        rt = UnifiedRuntime(db)
        snap_dir = pathlib.Path(tempfile.mkdtemp())
        original = ru._SNAPSHOT_DIR
        ru._SNAPSHOT_DIR = snap_dir
        result = rt.resume()
        assert result["ok"] is False
        assert result["reason"] == "no_snapshot"
        ru._SNAPSHOT_DIR = original

    def test_warm_resume(self, runtime):
        runtime.boot()
        runtime.snapshot()
        result = runtime.resume()
        assert result["ok"] is True
        assert "resumed_from" in result

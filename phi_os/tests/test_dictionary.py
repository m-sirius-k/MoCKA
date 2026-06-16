# phi_os/tests/test_dictionary.py
# PHI-OS語彙コア辞書 v1 単体テスト
import os
import tempfile
import pytest

from phi_os.dictionary import (
    PhiOSDictionary,
    TermOrigin,
    MeaningStatus,
    RelationType,
    ResolvedMeaning,
    DriftedTerm,
)


@pytest.fixture
def db():
    """テスト用一時DBを使う辞書インスタンス。"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    d = PhiOSDictionary(db_path=path)
    yield d
    d.close()
    os.unlink(path)


# ─── Term 登録 ────────────────────────────────────────────────

class TestRegisterTerm:
    def test_new_term_returns_true(self, db):
        assert db.register_term("event") is True

    def test_duplicate_term_returns_false(self, db):
        db.register_term("event")
        assert db.register_term("event") is False

    def test_term_exists_after_registration(self, db):
        db.register_term("artifact")
        assert db.term_exists("artifact") is True

    def test_unknown_origin(self, db):
        db.register_term("ghost_term", origin=TermOrigin.UNKNOWN)
        # 例外なく登録できること
        assert db.term_exists("ghost_term")


# ─── Meaning 追加 ─────────────────────────────────────────────

class TestAddMeaning:
    def test_add_meaning_returns_id(self, db):
        mid = db.add_meaning("event", "状態変化の記録単位", 0.8, 0.9)
        assert mid.startswith("meaning_")

    def test_version_increments(self, db):
        db.add_meaning("event", "定義v1", 0.5, 0.6)
        db.add_meaning("event", "定義v2", 0.7, 0.8)
        resolved = db.resolve("event")
        assert resolved.version == 2

    def test_old_version_deprecated(self, db):
        db.add_meaning("gate", "定義v1", 0.5, 0.6)
        db.add_meaning("gate", "定義v2", 0.7, 0.8)
        history = db.resolve_all_versions("gate")
        assert len(history) == 2
        # 最新がアクティブ
        assert history[0].status == MeaningStatus.ACTIVE.value
        # 旧版がdeprecated
        assert history[1].status == MeaningStatus.DEPRECATED.value

    def test_auto_registers_term(self, db):
        db.add_meaning("auto_term", "自動登録テスト")
        assert db.term_exists("auto_term")


# ─── Resolve ─────────────────────────────────────────────────

class TestResolve:
    def test_resolve_returns_latest(self, db):
        db.add_meaning("artifact", "定義1", 0.5, 0.5)
        db.add_meaning("artifact", "定義2", 0.9, 0.9)
        r = db.resolve("artifact")
        assert isinstance(r, ResolvedMeaning)
        assert r.definition == "定義2"
        assert r.version == 2

    def test_resolve_nonexistent_returns_none(self, db):
        assert db.resolve("nonexistent_term") is None

    def test_resolve_all_versions_order(self, db):
        db.add_meaning("ver_test", "v1")
        db.add_meaning("ver_test", "v2")
        db.add_meaning("ver_test", "v3")
        history = db.resolve_all_versions("ver_test")
        assert [h.version for h in history] == [3, 2, 1]


# ─── Gravity 更新 ─────────────────────────────────────────────

class TestUpdateGravity:
    def test_update_returns_true(self, db):
        db.add_meaning("event", "定義", 0.5, 0.5)
        assert db.update_gravity("event", 0.9, 0.95) is True

    def test_update_nonexistent_returns_false(self, db):
        assert db.update_gravity("ghost", 0.9, 0.9) is False

    def test_gravity_reflected_in_resolve(self, db):
        db.add_meaning("event", "定義", 0.5, 0.5)
        db.update_gravity("event", 0.88, 0.92)
        r = db.resolve("event")
        assert r.stability_score == pytest.approx(0.88)
        assert r.semantic_gravity == pytest.approx(0.92)

    def test_low_gravity_sets_drifted_status(self, db):
        db.add_meaning("weak_term", "定義", 0.1, 0.1)
        db.update_gravity("weak_term", 0.1, 0.05)
        r = db.resolve("weak_term")
        assert r.status == MeaningStatus.DRIFTED.value


# ─── Dependency ──────────────────────────────────────────────

class TestDependency:
    def test_add_dependency(self, db):
        dep_id = db.add_dependency("event", "artifact", RelationType.DEPENDS_ON)
        assert dep_id.startswith("dep_")

    def test_get_dependencies(self, db):
        db.add_dependency("gate", "event", RelationType.DEPENDS_ON)
        db.add_dependency("gate", "artifact", RelationType.DEPENDS_ON)
        deps = db.get_dependencies("gate")
        assert len(deps) == 2
        to_terms = {d["to_term"] for d in deps}
        assert to_terms == {"event", "artifact"}


# ─── Drift Detection ──────────────────────────────────────────

class TestDriftDetection:
    def test_detect_drifted_terms(self, db):
        db.add_meaning("stable", "定義", 0.9, 0.9)
        db.add_meaning("drifting", "定義", 0.1, 0.2)
        drifted = db.detect_drift(threshold=0.3)
        term_ids = [d.term_id for d in drifted]
        assert "drifting" in term_ids
        assert "stable" not in term_ids

    def test_no_drift_empty_result(self, db):
        db.add_meaning("solid", "定義", 0.9, 0.95)
        assert db.detect_drift(threshold=0.3) == []


# ─── Unknown 吸収 ─────────────────────────────────────────────

class TestAbsorbUnknown:
    def test_absorb_creates_term_with_low_gravity(self, db):
        db.absorb_unknown("mystery_term", "未知の概念")
        r = db.resolve("mystery_term")
        assert r is not None
        assert r.semantic_gravity == pytest.approx(0.1)
        assert r.stability_score == pytest.approx(0.0)

    def test_absorbed_term_appears_in_drift(self, db):
        db.absorb_unknown("unknown_x", "不明な語彙")
        drifted = db.detect_drift()
        assert any(d.term_id == "unknown_x" for d in drifted)


# ─── Stats ───────────────────────────────────────────────────

class TestStats:
    def test_stats_structure(self, db):
        db.add_meaning("event", "定義", 0.8, 0.9)
        db.add_meaning("gate", "定義", 0.7, 0.8)
        db.add_dependency("gate", "event", RelationType.DEPENDS_ON)
        s = db.stats()
        assert s["total_terms"] == 2
        assert s["active_meanings"] == 2
        assert s["total_dependencies"] == 1
        assert "drifted_terms" in s

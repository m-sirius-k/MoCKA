"""
PR-OS テストスイート — AI Gate & Knowledge Store
python -m pytest tests/ -v
"""
import json
import os
import sys
import shutil
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Fixtures ───────────────────────────────────────────
@pytest.fixture(autouse=True)
def reset_index(tmp_path, monkeypatch):
    """各テストで index.json をクリーンなtmp領域に差し替え"""
    import knowledge_store.ks_manager as ks
    tmp_ks = tmp_path / "knowledge_store"
    tmp_ks.mkdir()
    (tmp_ks / "confirmed").mkdir()
    (tmp_ks / "draft").mkdir()
    idx = {
        "schema_version": "1.0",
        "last_updated": "2026-06-06T00:00:00Z",
        "counter": 0,
        "records": []
    }
    idx_path = tmp_ks / "index.json"
    idx_path.write_text(json.dumps(idx), encoding="utf-8")

    monkeypatch.setattr(ks, "INDEX_PATH",    str(idx_path))
    monkeypatch.setattr(ks, "CONFIRMED_DIR", str(tmp_ks / "confirmed"))
    monkeypatch.setattr(ks, "DRAFT_DIR",     str(tmp_ks / "draft"))
    yield tmp_ks


# ═══════════════════════════════════════════════════════
# Knowledge Store
# ═══════════════════════════════════════════════════════
class TestKSManager:

    def test_create_record(self):
        from knowledge_store.ks_manager import create_record, list_records
        rec = create_record("テスト記事", tags=["test"], category="dev")
        assert rec["id"] == "KS_001"
        assert rec["status"] == "draft"
        assert list_records() == [rec]

    def test_sequential_ids(self):
        from knowledge_store.ks_manager import create_record
        r1 = create_record("記事1")
        r2 = create_record("記事2")
        assert r1["id"] == "KS_001"
        assert r2["id"] == "KS_002"

    def test_confirm_high_score(self):
        from knowledge_store.ks_manager import create_record, confirm_record
        rec = create_record("記事")
        confirmed = confirm_record(rec["id"], score=0.95, corrections=2,
                                   integrity_pass=True)
        assert confirmed["status"] == "confirmed"
        assert confirmed["ai_gate_log"]["score"] == 0.95

    def test_confirm_low_score_rejected(self):
        from knowledge_store.ks_manager import create_record, confirm_record
        rec = create_record("低品質記事")
        result = confirm_record(rec["id"], score=0.4, corrections=20,
                                integrity_pass=False)
        assert result["status"] == "rejected"

    def test_confirm_mid_score_pending(self):
        from knowledge_store.ks_manager import create_record, confirm_record
        rec = create_record("中品質記事")
        result = confirm_record(rec["id"], score=0.7, corrections=5,
                                integrity_pass=True)
        assert result["status"] == "pending_approval"

    def test_update_publish_status(self):
        from knowledge_store.ks_manager import (
            create_record, confirm_record, update_publish_status, get_record)
        rec = create_record("記事")
        confirm_record(rec["id"], 0.9, 0, True)
        update_publish_status(rec["id"], "wordpress", "published")
        updated = get_record(rec["id"])
        assert updated["publish_status"]["wordpress"] == "published"

    def test_list_with_filter(self):
        from knowledge_store.ks_manager import create_record, confirm_record, list_records
        r1 = create_record("確定記事")
        confirm_record(r1["id"], 0.95, 0, True)
        r2 = create_record("ドラフト記事")

        confirmed = list_records(status="confirmed")
        drafts    = list_records(status="draft")
        assert len(confirmed) == 1
        assert len(drafts)    == 1


# ═══════════════════════════════════════════════════════
# Proofreader
# ═══════════════════════════════════════════════════════
class TestProofreader:

    def test_whitespace_normalization(self):
        from ai_gate.proofreader import proofread
        text = "Hello\n\n\n\nWorld"
        result = proofread(text)
        assert "\n\n\n" not in result.corrected

    def test_bracket_normalization(self):
        from ai_gate.proofreader import proofread
        text = "テスト（括弧）"
        result = proofread(text)
        assert "(" in result.corrected
        assert "（" not in result.corrected

    def test_correction_count(self):
        from ai_gate.proofreader import proofread
        text = "テスト（括弧）と（もう一つ）"
        result = proofread(text)
        assert result.correction_count >= 2

    def test_clean_text_no_corrections(self):
        from ai_gate.proofreader import proofread
        text = "# 見出し\n\nきれいな本文です。\n\n- item1\n- item2\n"
        result = proofread(text)
        assert result.corrected == result.original or result.correction_count == 0


# ═══════════════════════════════════════════════════════
# Integrity Check
# ═══════════════════════════════════════════════════════
class TestIntegrityCheck:

    def test_placeholder_url_detected(self):
        from ai_gate.integrity_check import run_integrity_check
        result = run_integrity_check("詳細は https://example.com/test を見てください")
        assert not result.passed
        assert any("placeholder" in str(i).lower() or "example.com" in str(i).lower()
                   for i in result.issues)

    def test_invalid_date_detected(self):
        from ai_gate.integrity_check import run_integrity_check
        result = run_integrity_check("日付: 2019-13-45")
        assert any(i for i in result.issues if "無効" in i.get("message", ""))

    def test_clean_text_passes(self):
        from ai_gate.integrity_check import run_integrity_check
        result = run_integrity_check("MoCKAはv4です。2026-06-06リリース。")
        assert result.passed


# ═══════════════════════════════════════════════════════
# Optimizer
# ═══════════════════════════════════════════════════════
class TestOptimizer:

    def test_summary_extraction(self):
        from ai_gate.optimizer import extract_summary
        text = "# 見出し\n\nこれは要約されるべき段落です。"
        summary = extract_summary(text)
        assert "要約されるべき" in summary

    def test_frontmatter_added(self):
        from ai_gate.optimizer import optimize
        result = optimize("本文テキスト", ks_id="KS_001",
                          title="テスト", tags=["tag"])
        assert result.optimized.startswith("---")
        assert "KS_001" in result.optimized

    def test_no_duplicate_frontmatter(self):
        from ai_gate.optimizer import optimize
        text = "---\nid: existing\n---\n\n本文"
        result = optimize(text, ks_id="KS_002", title="T")
        assert result.optimized.count("---") == 2  # 開閉の2つのみ


# ═══════════════════════════════════════════════════════
# X Adapter — md_to_tweet
# ═══════════════════════════════════════════════════════
class TestXAdapter:

    def test_short_text_single_tweet(self):
        from adapters.x_twitter.x_adapter import md_to_tweet
        text = "短いテキストです。"
        tweets = md_to_tweet(text)
        assert len(tweets) == 1
        assert tweets[0] == text

    def test_long_text_thread(self):
        from adapters.x_twitter.x_adapter import md_to_tweet
        long = ("あ" * 100 + "\n\n") * 5
        tweets = md_to_tweet(long, max_chars=280)
        # スレッド番号が付く
        for t in tweets:
            assert len(t) <= 280

    def test_markdown_stripped(self):
        from adapters.x_twitter.x_adapter import md_to_tweet
        text = "# 見出し\n\n**太字**テキスト"
        tweets = md_to_tweet(text)
        assert "#" not in tweets[0]
        assert "**" not in tweets[0]

    def test_url_appended(self):
        from adapters.x_twitter.x_adapter import md_to_tweet
        text = "テスト本文"
        tweets = md_to_tweet(text, url="https://example.com")
        assert "https://example.com" in tweets[-1]


# ═══════════════════════════════════════════════════════
# WordPress Adapter — md_to_html
# ═══════════════════════════════════════════════════════
class TestWordPressAdapter:

    def test_heading_conversion(self):
        from adapters.wordpress.wp_adapter import md_to_html
        html = md_to_html("# H1\n## H2\n### H3")
        assert "<h1>H1</h1>" in html
        assert "<h2>H2</h2>" in html
        assert "<h3>H3</h3>" in html

    def test_bold_italic(self):
        from adapters.wordpress.wp_adapter import md_to_html
        html = md_to_html("**太字** *斜体*")
        assert "<strong>太字</strong>" in html
        assert "<em>斜体</em>" in html

    def test_list_conversion(self):
        from adapters.wordpress.wp_adapter import md_to_html
        html = md_to_html("- item1\n- item2\n- item3")
        assert "<ul>" in html
        assert "<li>item1</li>" in html

    def test_frontmatter_removed(self):
        from adapters.wordpress.wp_adapter import md_to_html
        md = "---\nid: KS_001\n---\n\n# タイトル"
        html = md_to_html(md)
        assert "---" not in html
        assert "id: KS_001" not in html


# ═══════════════════════════════════════════════════════
# Instagram Adapter
# ═══════════════════════════════════════════════════════
class TestInstagramAdapter:

    def test_caption_length(self):
        from adapters.instagram.ig_adapter import md_to_caption
        long_text = "あ" * 3000
        caption = md_to_caption(long_text, max_chars=2200)
        assert len(caption) <= 2200

    def test_hashtag_generation(self):
        from adapters.instagram.ig_adapter import extract_hashtags
        tags = ["mocka", "ai release", "v4"]
        ht = extract_hashtags(tags)
        assert "#mocka" in ht
        assert "#ai_release" in ht

    def test_heading_converted_to_brackets(self):
        from adapters.instagram.ig_adapter import md_to_caption
        text = "# タイトル\n\n本文"
        caption = md_to_caption(text)
        assert "【タイトル】" in caption


# ═══════════════════════════════════════════════════════
# Scheduler
# ═══════════════════════════════════════════════════════
class TestScheduler:

    @pytest.fixture(autouse=True)
    def reset_queue(self, tmp_path, monkeypatch):
        import scheduler.scheduler as sch
        q_path = tmp_path / "queue.json"
        q_path.write_text(json.dumps({
            "schema_version": "1.0",
            "last_updated": "2026-06-06T00:00:00Z",
            "queue": []
        }), encoding="utf-8")
        monkeypatch.setattr(sch, "QUEUE_PATH", str(q_path))
        yield

    def test_enqueue(self):
        from scheduler.scheduler import enqueue, list_jobs
        job = enqueue("KS_001", "wordpress", "2026-06-10T10:00:00+09:00")
        assert job["job_id"] == "JOB_0001"
        assert job["status"] == "pending"
        assert len(list_jobs()) == 1

    def test_duplicate_enqueue_raises(self):
        from scheduler.scheduler import enqueue
        enqueue("KS_001", "wordpress", "2026-06-10T10:00:00+09:00")
        with pytest.raises(ValueError):
            enqueue("KS_001", "wordpress", "2026-06-10T12:00:00+09:00")

    def test_cancel(self):
        from scheduler.scheduler import enqueue, cancel, list_jobs
        job = enqueue("KS_001", "x", "2026-06-10T10:00:00+09:00")
        assert cancel(job["job_id"])
        jobs = list_jobs(status="cancelled")
        assert len(jobs) == 1

    def test_get_due_jobs(self):
        from scheduler.scheduler import enqueue, get_due_jobs
        from datetime import datetime, timezone
        enqueue("KS_001", "wordpress", "2020-01-01T00:00:00+00:00")  # 過去
        enqueue("KS_002", "x",         "2099-01-01T00:00:00+00:00")  # 未来
        due = get_due_jobs()
        assert len(due) == 1
        assert due[0]["ks_id"] == "KS_001"

    def test_queue_summary(self):
        from scheduler.scheduler import enqueue, cancel, queue_summary
        j1 = enqueue("KS_001", "wordpress", "2026-06-10T00:00:00+00:00")
        j2 = enqueue("KS_002", "x", "2026-06-10T00:00:00+00:00")
        cancel(j2["job_id"])
        s = queue_summary()
        assert s["total"]     == 2
        assert s["pending"]   == 1
        assert s["cancelled"] == 1


# ═══════════════════════════════════════════════════════
# Analytics — Rewriter
# ═══════════════════════════════════════════════════════
class TestRewriter:

    def test_high_bounce_rate(self):
        from analytics.rewriter import analyze
        metrics = {"pageviews": 100, "bounce_rate": 0.85,
                   "avg_duration": 60.0, "new_users": 10}
        suggestions = analyze("KS_001", metrics)
        assert any(s.priority == "high" and s.category == "engagement"
                   for s in suggestions)

    def test_low_duration(self):
        from analytics.rewriter import analyze
        metrics = {"pageviews": 200, "bounce_rate": 0.3,
                   "avg_duration": 15.0, "new_users": 50}
        suggestions = analyze("KS_001", metrics)
        assert any(s.category == "length" for s in suggestions)

    def test_good_performance_low_priority(self):
        from analytics.rewriter import analyze
        metrics = {"pageviews": 500, "bounce_rate": 0.25,
                   "avg_duration": 180.0, "new_users": 100}
        suggestions = analyze("KS_001", metrics)
        if suggestions:
            assert all(s.priority == "low" for s in suggestions)

    def test_mock_metrics_skipped(self):
        from analytics.rewriter import analyze
        suggestions = analyze("KS_001", {"mock": True})
        assert suggestions == []

    def test_priority_ordering(self):
        from analytics.rewriter import analyze
        metrics = {"pageviews": 10, "bounce_rate": 0.9,
                   "avg_duration": 10.0, "new_users": 0}
        suggestions = analyze("KS_001", metrics)
        order = {"high": 0, "medium": 1, "low": 2}
        priorities = [order[s.priority] for s in suggestions]
        assert priorities == sorted(priorities)

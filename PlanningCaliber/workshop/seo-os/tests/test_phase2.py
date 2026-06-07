import pytest, os, sys, sqlite3
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import kernel.job_engine as je
je.DB_PATH = ":memory:"

from workers.base_worker import BaseWorker
from caliber.caliber_manager import list_capabilities

def test_base_worker_interface():
    with pytest.raises(TypeError):
        BaseWorker()

def test_capability_list():
    caps = list_capabilities()
    assert "publish_blog" in caps
    assert "upload_html" in caps

def test_sftp_worker_execute():
    from workers.sftp_worker import SFTPWorker
    w = SFTPWorker()
    result = w.execute({
        "id": "JTEST001", "title": "テスト",
        "target": "orchestra", "content": ""
    })
    assert result["success"] is True

def test_wordpress_worker_execute():
    from workers.wordpress_worker import WordPressWorker
    w = WordPressWorker()
    result = w.execute({
        "id": "JTEST002", "title": "テスト記事",
        "target": "wordpress", "content": "<p>test</p>"
    })
    assert result["success"] is True

def test_scheduler_capability_driven():
    from caliber.caliber_manager import request_capability
    worker = request_capability("publish_blog")
    assert worker is not None
    assert hasattr(worker, "execute")
    assert "publish_blog" in worker.capabilities

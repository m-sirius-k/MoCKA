import pytest, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__),".."))

from gate.ai_gate import AIGate
from gate.policy_engine import PolicyEngine
from kernel.artifact_manager import save, verify
import tempfile, os

def test_gate_pass_lp():
    gate = AIGate()
    job = {
        "id": "JTEST_LP",
        "type": "lp",
        "content": (
            '<meta name="viewport" content="width=device-width">'
            '<meta property="og:title" content="test">'
            "<p>" + "あ" * 600 + "</p>")
    }
    r = gate.check(job, "lp_policy")
    assert r["passed"] is True
    assert r["score"] == 100

def test_gate_fail_empty():
    gate = AIGate()
    job = {"id":"JTEST_EMPTY","type":"lp","content":""}
    r = gate.check(job, "lp_policy")
    assert r["passed"] is False

def test_gate_bot_char_limit():
    gate = AIGate()
    job = {"id":"JTEST_BOT","type":"bot",
           "content":"a" * 141}
    r = gate.check(job, "bot_policy")
    assert r["details"]["char_limit"] is False

def test_policy_auto_deploy():
    policy = PolicyEngine()
    job = {"id":"JPOL","type":"bot",
           "policy":"bot_policy","ai_draft":1}
    gate_result = {"passed":True,"score":100}
    v = policy.evaluate(job, gate_result)
    assert v["verdict"] == "auto_deploy"

def test_policy_human_gate():
    policy = PolicyEngine()
    job = {"id":"JPOL2","type":"lp",
           "policy":"lp_policy","ai_draft":0}
    gate_result = {"passed":True,"score":100}
    v = policy.evaluate(job, gate_result)
    assert v["verdict"] == "human_gate"

def test_policy_reject_low_score():
    policy = PolicyEngine()
    job = {"id":"JPOL3","type":"lp",
           "policy":"lp_policy","ai_draft":1}
    gate_result = {"passed":False,"score":50}
    v = policy.evaluate(job, gate_result)
    assert v["verdict"] == "reject"

def test_artifact_save_and_verify(tmp_path, monkeypatch):
    import kernel.artifact_manager as am
    am.ARTIFACT_DIR = str(tmp_path)
    art = save("JTEST_ART","html",
               "<html>test</html>","test.html")
    assert os.path.exists(art["path"])
    assert len(art["hash"]) == 64

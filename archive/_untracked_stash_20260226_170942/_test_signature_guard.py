# FILE: C:\Users\sirok\MoCKA\_test_signature_guard.py

print("TEST_IMPORT: src.mocka_audit.signature_guard")
from src.mocka_audit.signature_guard import guard_before_signature as g1, accept_signed_payload as a1

print("TEST_IMPORT: tools.signature_guard")
from tools.signature_guard import guard_before_signature as g2, accept_signed_payload as a2

def run(name, fn):
    try:
        fn()
        print("ALLOW:", name)
    except Exception as e:
        print("REJECT:", name, "|", str(e))

run("src guard test-key-001", lambda: g1("test-key-001"))
run("tools guard test-key-001", lambda: g2("test-key-001"))

run("src guard test-key-002", lambda: g1("test-key-002"))
run("tools guard test-key-002", lambda: g2("test-key-002"))

run("src accept key-001", lambda: a1({"key_id":"test-key-001"}))
run("tools accept key-001", lambda: a2({"key_id":"test-key-001"}))

run("src accept key-002", lambda: a1({"key_id":"test-key-002"}))
run("tools accept key-002", lambda: a2({"key_id":"test-key-002"}))

print("DONE")

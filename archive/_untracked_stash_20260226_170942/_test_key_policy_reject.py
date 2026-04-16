# FILE: C:\Users\sirok\MoCKA\_test_key_policy_reject.py
from src.mocka_audit.key_policy import assert_key_active

# revoke済み想定
assert_key_active("test-key-001")
print("SHOULD_NOT_PRINT")

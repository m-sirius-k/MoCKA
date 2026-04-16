# FILE: C:\Users\sirok\MoCKA\_test_key_policy.py
from src.mocka_audit.key_policy import assert_key_active

# 現在アクティブ想定（さっき rotate で作った新鍵）
assert_key_active("test-key-002")
print("KEY_POLICY_OK")

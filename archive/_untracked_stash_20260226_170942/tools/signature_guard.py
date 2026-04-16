# FILE: C:\Users\sirok\MoCKA\tools\signature_guard.py
# NOTE: Phase13-B wrapper (delegation to src single source of truth)
# The guard logic must live only in src.mocka_audit.signature_guard.

from src.mocka_audit.signature_guard import guard_before_signature, accept_signed_payload

__all__ = ["guard_before_signature", "accept_signed_payload"]
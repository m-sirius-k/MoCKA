# C:\Users\sirok\MoCKA\audit\ed25519\signer.py
# Phase12-A Ed25519 Signer (auto-resolve key paths, strict 32-byte raw keys)

from __future__ import annotations

from pathlib import Path
from typing import Tuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

ROOT = Path(r"C:\Users\sirok\MoCKA")

# Candidate locations (historical + canonical)
PRIVATE_CANDIDATES = [
    ROOT / "audit" / "ed25519" / "keys" / "ed25519_private.key",
    ROOT / "secrets" / "ed25519" / "ed25519_private.key",
]
PUBLIC_CANDIDATES = [
    ROOT / "audit" / "ed25519" / "keys" / "ed25519_public.key",
    ROOT / "secrets" / "ed25519" / "ed25519_public.key",
]

# Resolved paths are cached after first load
_RESOLVED_PRIVATE: Path | None = None
_RESOLVED_PUBLIC: Path | None = None


def _pick_existing(candidates: list[Path], kind: str) -> Path:
    for p in candidates:
        if p.exists():
            return p
    msg = " / ".join(str(p) for p in candidates)
    raise FileNotFoundError(f"{kind} key not found. candidates: {msg}")


def _read_key_32(path: Path, kind: str) -> bytes:
    b = path.read_bytes()
    if len(b) != 32:
        raise ValueError(f"invalid {kind} key length: {len(b)} (expected 32) path={path}")
    return b


def _resolve_paths() -> Tuple[Path, Path]:
    global _RESOLVED_PRIVATE, _RESOLVED_PUBLIC
    if _RESOLVED_PRIVATE is None:
        _RESOLVED_PRIVATE = _pick_existing(PRIVATE_CANDIDATES, "private")
    if _RESOLVED_PUBLIC is None:
        _RESOLVED_PUBLIC = _pick_existing(PUBLIC_CANDIDATES, "public")
    return _RESOLVED_PRIVATE, _RESOLVED_PUBLIC


def resolved_key_paths() -> Tuple[str, str]:
    priv, pub = _resolve_paths()
    return str(priv), str(pub)


def load_keys() -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    priv_path, pub_path = _resolve_paths()
    priv = Ed25519PrivateKey.from_private_bytes(_read_key_32(priv_path, "private"))
    pub = Ed25519PublicKey.from_public_bytes(_read_key_32(pub_path, "public"))
    return priv, pub


def sign(data: bytes) -> bytes:
    priv, _ = load_keys()
    return priv.sign(data)


def verify(data: bytes, signature: bytes) -> None:
    _, pub = load_keys()
    pub.verify(signature, data)



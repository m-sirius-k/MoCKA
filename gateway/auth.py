# -*- coding: utf-8 -*-
import os
from flask import request, abort

VALID_KEYS = set(filter(None, os.environ.get("MOCKA_API_KEYS", "").split(",")))

PUBLIC_PATHS = {"/api/v1/phase", "/api/v1/health"}


def require_api_key():
    if request.path in PUBLIC_PATHS:
        return
    key = request.headers.get("X-MoCKA-Key", "").strip()
    if not key:
        abort(401, "X-MoCKA-Key header missing")
    if VALID_KEYS and key not in VALID_KEYS:
        abort(403, "Invalid API key")

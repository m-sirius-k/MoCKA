# src/mocka_ai.py
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class AIResult:
    # Contract fields required by callers (field_player/main_loop)
    text: str
    raw: Dict[str, Any]
    usage: Optional[Dict[str, Any]] = None

    # Explicit attributes expected by callers
    provider: str = ""
    model: str = ""

    # Optional error payload; ok is derived from this
    error: Optional[Any] = None

    @property
    def ok(self) -> bool:
        return self.error is None


class ProviderError(RuntimeError):
    pass


def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name)
    if v is None:
        return default
    v = str(v)
    return v if v != "" else default


def _now_ms() -> int:
    return int(time.time() * 1000)


def _as_int(v: Optional[str], default: int) -> int:
    try:
        if v is None or v == "":
            return default
        return int(v)
    except Exception:
        return default


def _redact_secrets_text(s: str) -> str:
    if not s:
        return s
    s = re.sub(r"\bsk-[A-Za-z0-9_\-]{8,}\b", "sk-[REDACTED]", s)
    s = re.sub(r"(?i)\bBearer\s+[A-Za-z0-9_\-\.]{8,}\b", "Bearer [REDACTED]", s)
    s = re.sub(r'(?i)"api_key"\s*:\s*"[^"]+"', '"api_key":"[REDACTED]"', s)
    s = re.sub(r'(?i)"authorization"\s*:\s*"[^"]+"', '"authorization":"[REDACTED]"', s)
    s = re.sub(r'(?i)"token"\s*:\s*"[^"]+"', '"token":"[REDACTED]"', s)
    return s


def _redact_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    deny = ("authorization", "api_key", "apikey", "key", "token", "secret", "password")
    out: Dict[str, Any] = {}
    for k, v in d.items():
        lk = str(k).lower()
        if any(x in lk for x in deny):
            out[k] = "[REDACTED]"
            continue
        if isinstance(v, str):
            out[k] = _redact_secrets_text(v)
        else:
            out[k] = v
    return out


def call_ai(prompt: str, *, provider: Optional[str] = None, timeout_ms: Optional[int] = None) -> AIResult:
    provider = provider or _env("MOCKA_PROVIDER", "openai_http")
    timeout_ms = timeout_ms if timeout_ms is not None else _as_int(_env("MOCKA_AI_TIMEOUT_MS"), 30000)

    if provider == "stub":
        meta = {"provider": "stub", "model": "stub", "ts_ms": _now_ms()}
        raw = {"meta": meta, "response": {"text": prompt}}
        return AIResult(
            text="[stub] " + prompt,
            raw=raw,
            usage=None,
            provider="stub",
            model="stub",
            error=None,
        )

    if provider == "openai_http":
        return _call_openai_http(prompt, timeout_ms=timeout_ms)

    raise ProviderError("Unknown provider: " + str(provider))


def _call_openai_http(prompt: str, *, timeout_ms: int) -> AIResult:
    api_key = _env("OPENAI_API_KEY")
    if not api_key:
        raise ProviderError("OPENAI_API_KEY is not set")

    model = _env("OPENAI_MODEL", "gpt-4.1-mini")
    url = "https://api.openai.com/v1/responses"

    payload: Dict[str, Any] = {"model": model, "input": prompt}
    body = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + api_key)

    t0 = _now_ms()
    try:
        with urllib.request.urlopen(req, timeout=max(1, timeout_ms // 1000)) as resp:
            resp_bytes = resp.read()
            t1 = _now_ms()

            raw_resp = json.loads(resp_bytes.decode("utf-8"))
            text = _extract_text_from_responses(raw_resp)
            usage = raw_resp.get("usage")

            meta = {
                "provider": "openai_http",
                "model": model,
                "timing_ms": {"provider_call_ms": t1 - t0},
                "request": _redact_dict({"model": model, "timeout_ms": timeout_ms}),
            }

            raw = {"meta": meta, "response": raw_resp}
            return AIResult(
                text=text,
                raw=raw,
                usage=usage if isinstance(usage, dict) else None,
                provider="openai_http",
                model=model,
                error=None,
            )

    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            err_body = ""
        redacted = _redact_secrets_text(err_body)
        msg = "OpenAI HTTPError " + str(e.code) + ": " + redacted
        raise ProviderError(msg) from e

    except urllib.error.URLError as e:
        raise ProviderError("OpenAI URLError: " + _redact_secrets_text(str(e))) from e

    except Exception as e:
        raise ProviderError("OpenAI unknown error: " + _redact_secrets_text(str(e))) from e


def _extract_text_from_responses(raw: Dict[str, Any]) -> str:
    v = raw.get("output_text")
    if isinstance(v, str) and v:
        return v

    out = raw.get("output")
    if isinstance(out, list):
        chunks = []
        for item in out:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for c in content:
                if not isinstance(c, dict):
                    continue
                ctype = c.get("type")
                if ctype in ("output_text", "text"):
                    txt = c.get("text")
                    if isinstance(txt, str) and txt:
                        chunks.append(txt)
        if chunks:
            return "\n".join(chunks)

    try:
        return json.dumps(raw, ensure_ascii=True)
    except Exception:
        return str(raw)

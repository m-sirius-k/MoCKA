# -*- coding: utf-8 -*-
"""配信テンプレート定義。各プラットフォームのペイロード組み立てルール。"""


def build_payloads(t: dict) -> dict:
    return {
        "github": "\n\n".join([t["technical"], t["academic"], t["security"]]),
        "wordpress": "\n\n".join(t.values()),
        "linkedin": t["business"],
        "x": _summarize(t["technical"], max_chars=200),
        "devto": t["technical"],
        "substack": "\n\n".join([t["business"], t["academic"]]),
    }


def _summarize(text: str, max_chars: int = 200) -> str:
    return text[:max_chars] + "..." if len(text) > max_chars else text

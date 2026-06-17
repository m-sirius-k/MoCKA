# -*- coding: utf-8 -*-
from .transformer import transform
from .templates import build_payloads
from .platforms import github, wordpress, linkedin, x, devto, substack


def route(content: str) -> dict:
    t = transform(content)
    payloads = build_payloads(t)

    results = {}
    for name, module, key in [
        ("github", github, "github"),
        ("wordpress", wordpress, "wordpress"),
        ("linkedin", linkedin, "linkedin"),
        ("x", x, "x"),
        ("devto", devto, "devto"),
        ("substack", substack, "substack"),
    ]:
        try:
            module.publish(payloads[key])
            results[name] = "ok"
        except Exception as e:
            results[name] = f"error: {e}"

    return {"status": "distributed", "results": results}

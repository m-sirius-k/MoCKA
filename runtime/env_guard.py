import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿from runtime.env_utils import get_env

def enforce_env(mode="verify"):
    if mode == "rebuild":
        get_env("API_KEY")
    elif mode == "api":
        get_env("API_KEY")

    print(f"ENV OK ({mode})")

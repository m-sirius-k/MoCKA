import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿from runtime.env_utils import get_env

def enforce_rebuild_permission():
    role = get_env("ROLE")

    if role != "admin":
        raise Exception("REBUILD NOT ALLOWED")

    print("REBUILD AUTHORIZED")

import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿import shutil, os

def build():
    if os.path.exists("dist"):
        shutil.rmtree("dist")

    os.makedirs("dist",exist_ok=True)

    files = [
        "verify_token.py",
        "verify_ledger.py",
        "use_testkey.py"
    ]

    for f in files:
        if os.path.exists(f):
            shutil.copy(f,"dist/"+f)

    print("DIST BUILD COMPLETE")

if __name__ == "__main__":
    build()

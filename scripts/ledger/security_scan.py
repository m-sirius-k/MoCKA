import os
import re

ROOT = "."

EXCLUDE_KEYWORDS = [
    ".venv",
    "site-packages",
    "__pycache__",
    ".git",
    "archive"
]

PATTERNS = [
    r"api[_-]?key\s*=\s*['\"]",
    r"secret\s*=\s*['\"]",
    r"token\s*=\s*['\"]"
]

def should_exclude(path):
    for k in EXCLUDE_KEYWORDS:
        if k in path:
            return True
    return False

def scan():
    for root, dirs, files in os.walk(ROOT):

        if should_exclude(root):
            continue

        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)

                if should_exclude(path):
                    continue

                with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                    text = fh.read()

                    for p in PATTERNS:
                        if re.search(p, text, re.IGNORECASE):
                            print(f"SECRET RISK: {path}")
                            return 1

    print("NO HARD-CODED SECRETS")
    return 0

if __name__ == "__main__":
    exit(scan())

import os
import re
import sys

ROOT = r"C:\Users\sirok\mocka-ecosystem\MoCKA"

targets = [
    "README.md",
    "docs",
    "canon"
]

# 1) Markdownリンク: [text](path)
md_link = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

# 2) オートリンク: <path>
auto_link = re.compile(r"<([^>]+)>")

# 3) プレーンパス: docs/XXX.md など（空白境界）
plain_md = re.compile(r"(?:(?<=\s)|^)([A-Za-z0-9_\-./]+\.md)(?:(?=\s)|$)")

code_fence = re.compile(r"```.*?```", re.DOTALL)

broken = []
checked = 0

def is_ignorable(link: str) -> bool:
    if link is None:
        return True

    l = link.strip()
    if not l:
        return True

    if l.startswith("http://") or l.startswith("https://"):
        return True

    if l.startswith("#"):
        return True

    if l.startswith("mailto:"):
        return True

    # 角括弧プレースホルダ対策:
    # <filename> や <event_id> のような「拡張子もスラッシュも無い単語」はリンク扱いしない
    has_slash = ("/" in l) or ("\\" in l)
    has_dot = ("." in l)
    if (not has_slash) and (not has_dot):
        return True

    # 画像は今回は無視（必要なら外す）
    lower = l.lower()
    if lower.endswith(".png") or lower.endswith(".jpg") or lower.endswith(".jpeg") or lower.endswith(".gif") or lower.endswith(".svg") or lower.endswith(".webp"):
        return True

    return False

def normalize_target(base_file: str, link: str) -> str:
    l = link.strip()

    # クエリやアンカー除去
    if "#" in l:
        l = l.split("#", 1)[0]
    if "?" in l:
        l = l.split("?", 1)[0]
    l = l.strip()

    if not l:
        return ""

    if os.path.isabs(l):
        return os.path.normpath(l)

    return os.path.normpath(os.path.join(os.path.dirname(base_file), l))

def check_file(path: str):
    global checked

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    # コードブロックは除外（SQLや出力例の誤検出対策）
    text = code_fence.sub("", text)

    found = []
    found += md_link.findall(text)
    found += auto_link.findall(text)
    found += plain_md.findall(text)

    # 重複排除（順序維持）
    seen = set()
    uniq = []
    for x in found:
        x = x.strip()
        if x in seen:
            continue
        seen.add(x)
        uniq.append(x)

    for l in uniq:
        if is_ignorable(l):
            continue

        target = normalize_target(path, l)
        if not target:
            continue

        checked += 1

        if not os.path.exists(target):
            broken.append((path, l, target))

def walk():
    for t in targets:
        p = os.path.join(ROOT, t)
        if os.path.isfile(p):
            check_file(p)
        elif os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                for fn in files:
                    if fn.endswith(".md"):
                        check_file(os.path.join(root, fn))

def main():
    walk()

    print("LINK_CHECKED:", checked)

    if broken:
        print("BROKEN_LINKS_FOUND")
        for src, raw, resolved in broken:
            print("FILE:", src)
            print("LINK:", raw)
            print("RESOLVED:", resolved)
            print()
        sys.exit(1)

    print("NO_BROKEN_LINKS")
    sys.exit(0)

if __name__ == "__main__":
    main()

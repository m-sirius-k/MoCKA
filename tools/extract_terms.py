# extract_terms.py -- MoCKA全語彙抽出スクリプト
# 出力先: docs/reference/semantic_dictionary/raw/

import os
import re
import ast
import csv
import json
import sys
from collections import defaultdict, Counter
from pathlib import Path
from itertools import combinations

# ─── 設定 ────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent
OUT_DIR = ROOT / "docs" / "reference" / "semantic_dictionary" / "raw"

EXCLUDED_DIRS = {
    "node_modules", ".git", "__pycache__", ".pytest_cache",
    "venv", ".venv", "dist", "build",
}

TARGET_EXTS = {
    ".md", ".py", ".json", ".yaml", ".yml", ".toml",
    ".ini", ".txt", ".html", ".css", ".js", ".ts", ".tsx", ".jsx", ".svg",
}

PYTHON_KEYWORDS = {
    "if", "else", "for", "while", "def", "class", "return", "import",
    "from", "as", "try", "except", "with", "pass", "break", "continue",
    "yield", "lambda", "not", "and", "or", "in", "is", "True", "False",
    "None", "self", "cls",
}

HTML_TAGS = {
    "div", "span", "p", "a", "ul", "li", "ol", "table", "tr", "td", "th",
    "thead", "tbody", "tfoot", "form", "input", "button", "select", "option",
    "textarea", "label", "h1", "h2", "h3", "h4", "h5", "h6", "head", "body",
    "html", "script", "style", "link", "meta", "title", "header", "footer",
    "nav", "main", "section", "article", "aside", "figure", "figcaption",
    "img", "video", "audio", "canvas", "svg", "path", "rect", "circle",
    "line", "text", "g", "defs", "use", "symbol", "clipPath", "mask",
    "br", "hr", "pre", "code", "em", "strong", "small", "sup", "sub",
    "blockquote", "cite", "abbr", "del", "ins", "mark", "time", "var",
}

CSS_PROPS = {
    "color", "background", "margin", "padding", "border", "font", "display",
    "position", "width", "height", "top", "left", "right", "bottom",
    "flex", "grid", "overflow", "cursor", "opacity", "transform", "transition",
    "animation", "box", "text", "align", "justify", "content", "items",
    "gap", "radius", "shadow", "outline", "visibility", "pointer", "events",
    "float", "clear", "min", "max", "clip", "filter", "resize", "direction",
    "white", "word", "letter", "line", "vertical", "list", "style",
    "decoration", "indent", "spacing", "size", "weight", "family", "italic",
}

LICENSE_TERMS = {"MIT", "LICENSE", "Copyright", "LICENCE"}

CATEGORY_RULES = [
    ("Core Concept",  ["meaning", "institution", "authority", "gate", "binding", "artifact", "event"]),
    ("Module",        ["orchestra", "relay", "memory", "caliber", "phi_os", "phi-os", "runtime", "tic", "vasai"]),
    ("Governance",    ["governance", "compliance", "audit", "seal", "ledger", "constitution", "protocol"]),
    ("Runtime",       ["runtime", "engine", "manager", "registry", "validator"]),
    ("Architecture",  ["layer", "architecture", "structure", "pipeline", "kernel"]),
    ("Data Model",    ["schema", "dataclass", "model", "record", "payload"]),
    ("Protocol",      ["protocol", "handshake", "session", "workflow"]),
    ("API",           ["api", "endpoint", "route", "gate"]),
    ("UI",            ["ui", "html", "css", "panel", "popup"]),
    ("Database",      ["db", "sqlite", "csv", "json", "store"]),
    ("Event",         ["event", "change_start", "change_done", "incident", "audit"]),
    ("Document",      ["md", "doc", "readme", "spec", "report"]),
    ("Human Process", ["human", "gate", "review", "approval"]),
]

# ─── ユーティリティ ───────────────────────────────────────────────────────────

def classify(term: str) -> str:
    t = term.lower()
    for cat, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in t:
                return cat
    return "Unknown"


def is_excluded(term: str, dtype: str) -> bool:
    if not term or len(term) <= 2:
        return True
    if term.lower() in PYTHON_KEYWORDS:
        return True
    if term.lower() in HTML_TAGS:
        return True
    if term.lower() in CSS_PROPS:
        return True
    if term in LICENSE_TERMS:
        return True
    if re.fullmatch(r"[0-9]+", term):
        return True
    if term.startswith("http://") or term.startswith("https://"):
        return True
    return False


def walk_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # exclude dirs in-place
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for fname in filenames:
            ext = Path(fname).suffix.lower()
            if ext in TARGET_EXTS:
                yield Path(dirpath) / fname


# ─── Python AST 解析 ─────────────────────────────────────────────────────────

def extract_python_terms(filepath: Path):
    """Returns list of (term, detected_type)"""
    results = []
    try:
        source = filepath.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(filepath))
    except Exception:
        return results

    import_names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in (node.names if hasattr(node, "names") else []):
                import_names.add(alias.asname or alias.name)

    enum_classes = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                base_id = ""
                if isinstance(base, ast.Name):
                    base_id = base.id
                elif isinstance(base, ast.Attribute):
                    base_id = base.attr
                if "Enum" in base_id or "enum" in base_id:
                    enum_classes.add(node.name)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if not is_excluded(node.name, "class"):
                results.append((node.name, "class"))
            # enum members
            if node.name in enum_classes:
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for t in item.targets:
                            if isinstance(t, ast.Name) and not is_excluded(t.id, "enum"):
                                results.append((t.id, "enum"))
            # dataclass fields
            is_dc = any(
                (isinstance(d, ast.Name) and d.id == "dataclass") or
                (isinstance(d, ast.Attribute) and d.attr == "dataclass")
                for d in node.decorator_list
            )
            if is_dc:
                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        fname = item.target.id
                        if not fname.startswith("_") and not is_excluded(fname, "dataclass"):
                            results.append((fname, "dataclass"))

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name
            if not name.startswith("_") and not is_excluded(name, "function"):
                results.append((name, "function"))

    return results


# ─── 正規表現解析 ─────────────────────────────────────────────────────────────

RE_UPPER   = re.compile(r'\b([A-Z][A-Z0-9_]{2,})\b')
RE_CAMEL   = re.compile(r'\b([A-Z][a-z]+(?:[A-Z][a-z0-9]+)+)\b')
RE_SNAKE   = re.compile(r'\b([a-z][a-z0-9]+(?:_[a-z0-9]+){2,})\b')
RE_HEADER  = re.compile(r'^#{1,4}\s+(.+)', re.MULTILINE)
RE_HYPHEN  = re.compile(r'\b([A-Za-z]+-[A-Za-z]+(?:-[A-Za-z]+)*)\b')

def extract_regex_terms(filepath: Path, text: str):
    results = []

    for m in RE_UPPER.finditer(text):
        t = m.group(1)
        if not is_excluded(t, "UPPER_CASE"):
            results.append((t, "UPPER_CASE"))

    for m in RE_CAMEL.finditer(text):
        t = m.group(1)
        if not is_excluded(t, "CamelCase"):
            results.append((t, "CamelCase"))

    for m in RE_SNAKE.finditer(text):
        t = m.group(1)
        if t.lower() not in PYTHON_KEYWORDS and not is_excluded(t, "snake_case"):
            results.append((t, "snake_case"))

    for m in RE_HEADER.finditer(text):
        header_text = m.group(1).strip()
        if header_text and not is_excluded(header_text, "header"):
            results.append((header_text, "header"))

    for m in RE_HYPHEN.finditer(text):
        t = m.group(1)
        if not is_excluded(t, "hyphen"):
            results.append((t, "hyphen"))

    return results


# ─── フレーズ抽出 ─────────────────────────────────────────────────────────────

RE_WORD = re.compile(r'[A-Za-z]{2,}')

def extract_phrases(all_texts: list) -> Counter:
    phrase_counter = Counter()
    for text in all_texts:
        words = RE_WORD.findall(text)
        # filter out very common short words
        stop = {"the", "a", "an", "is", "it", "in", "on", "at", "to", "of",
                "and", "or", "not", "for", "with", "this", "that", "are",
                "be", "was", "as", "by", "do", "no", "so", "up", "if",
                "we", "he", "she", "they", "you", "me", "my", "our", "its",
                "can", "has", "had", "have", "from", "will", "been", "but"}
        words = [w for w in words if w.lower() not in stop and len(w) > 2]
        for n in (3, 4):
            for i in range(len(words) - n + 1):
                phrase = " ".join(words[i:i+n])
                phrase_counter[phrase] += 1
    return phrase_counter


# ─── メイン収集 ───────────────────────────────────────────────────────────────

# term -> {occurrences, files_set, detected_types_set}
term_data: dict[str, dict] = {}
all_texts_for_phrases = []

# file -> set of terms  (for co-occurrence)
file_terms: dict[str, set] = {}

def add_term(term: str, dtype: str, filepath: Path):
    rel = str(filepath.relative_to(ROOT))
    key = (term, dtype)
    k = f"{term}|||{dtype}"
    if k not in term_data:
        term_data[k] = {
            "term": term,
            "detected_type": dtype,
            "occurrences": 0,
            "files_set": set(),
        }
    term_data[k]["occurrences"] += 1
    term_data[k]["files_set"].add(rel)
    # also track in file_terms
    fp_str = str(filepath)
    if fp_str not in file_terms:
        file_terms[fp_str] = set()
    file_terms[fp_str].add(term)


print("Scanning files...", flush=True)
file_count = 0

for fpath in walk_files():
    file_count += 1
    if file_count % 100 == 0:
        print(f"  {file_count} files processed...", flush=True)

    try:
        text = fpath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue

    all_texts_for_phrases.append(text)

    if fpath.suffix == ".py":
        for term, dtype in extract_python_terms(fpath):
            add_term(term, dtype, fpath)

    for term, dtype in extract_regex_terms(fpath, text):
        add_term(term, dtype, fpath)

print(f"Total files scanned: {file_count}", flush=True)
print("Extracting phrases...", flush=True)

phrase_counter = extract_phrases(all_texts_for_phrases)
# keep phrases appearing 3+ times
for phrase, count in phrase_counter.items():
    if count >= 3:
        add_term(phrase, "phrase", Path(ROOT / "_phrases_synthetic"))

print(f"Unique (term, type) pairs: {len(term_data)}", flush=True)

# ─── Term リスト構築 ──────────────────────────────────────────────────────────

def build_records():
    records = []
    for k, d in term_data.items():
        files_list = sorted(d["files_set"])[:10]
        # primary directory = most common parent dir of occurrences
        dirs = [str(Path(f).parent) for f in d["files_set"]]
        dir_counter = Counter(dirs)
        primary_dir = dir_counter.most_common(1)[0][0] if dir_counter else ""

        records.append({
            "term": d["term"],
            "occurrences": d["occurrences"],
            "files": files_list,
            "directory": primary_dir,
            "category": classify(d["term"]),
            "detected_type": d["detected_type"],
            "definition": "",
            "responsibilities": "",
            "not_responsibilities": "",
            "aliases": "",
            "status": "active",
            "version": "",
        })

    records.sort(key=lambda r: -r["occurrences"])
    return records

print("Building records...", flush=True)
records = build_records()
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ─── 1. all_terms.csv ────────────────────────────────────────────────────────
csv_path = OUT_DIR / "all_terms.csv"
fieldnames = ["term","occurrences","files","directory","category","detected_type",
              "definition","responsibilities","not_responsibilities","aliases","status","version"]

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    for r in records:
        row = dict(r)
        row["files"] = "|".join(r["files"])
        w.writerow(row)

print(f"1. all_terms.csv: {len(records)} terms", flush=True)

# ─── 2. all_terms.json ───────────────────────────────────────────────────────
json_path = OUT_DIR / "all_terms.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print(f"2. all_terms.json written", flush=True)

# ─── 3. all_terms.md ─────────────────────────────────────────────────────────
md_path = OUT_DIR / "all_terms.md"
cat_groups = defaultdict(list)
for r in records:
    cat_groups[r["category"]].append(r)

with open(md_path, "w", encoding="utf-8") as f:
    f.write("# MoCKA Term Dictionary — Raw Extraction\n\n")
    for cat in sorted(cat_groups.keys()):
        f.write(f"## {cat}\n\n")
        f.write("| Term | Occurrences | Detected Type | Files |\n")
        f.write("|---|---|---|---|\n")
        for r in cat_groups[cat]:
            files_str = r["files"][0] if r["files"] else ""
            # escape pipe in term
            term_esc = r["term"].replace("|", "\\|")
            f.write(f"| {term_esc} | {r['occurrences']} | {r['detected_type']} | {files_str} |\n")
        f.write("\n")

print(f"3. all_terms.md written", flush=True)

# ─── 4. frequency.csv ────────────────────────────────────────────────────────
freq_path = OUT_DIR / "frequency.csv"
with open(freq_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["term","occurrences","category","detected_type"])
    w.writeheader()
    for r in records[:500]:
        w.writerow({
            "term": r["term"],
            "occurrences": r["occurrences"],
            "category": r["category"],
            "detected_type": r["detected_type"],
        })

print(f"4. frequency.csv: top {min(500,len(records))} terms", flush=True)

# ─── 5. duplicate_candidates.md ──────────────────────────────────────────────
dup_path = OUT_DIR / "duplicate_candidates.md"
all_term_names = [r["term"] for r in records if r["detected_type"] != "phrase"]

# group by normalized form
norm_groups = defaultdict(list)
for t in all_term_names:
    norm = t.lower().rstrip("s").rstrip("e").replace("-", "_").replace(" ", "_")
    norm_groups[norm].append(t)

with open(dup_path, "w", encoding="utf-8") as f:
    f.write("# 重複候補\n\n")
    written = 0
    for norm, variants in sorted(norm_groups.items()):
        if len(variants) > 1:
            f.write(f"- {' / '.join(sorted(set(variants)))} → 同一概念の可能性\n")
            written += 1

print(f"5. duplicate_candidates.md: {written} groups", flush=True)

# ─── 6. synonym_candidates.md ────────────────────────────────────────────────
syn_path = OUT_DIR / "synonym_candidates.md"
# terms that co-occur in the same files with similar length/structure
# simplified: same file, similar normalized form
with open(syn_path, "w", encoding="utf-8") as f:
    f.write("# 同義語候補\n\n")
    f.write("同じファイルに共存する類似語（正規化後2文字差以内）\n\n")

    # build file -> terms index (non-phrase)
    fmap = defaultdict(list)
    for r in records:
        if r["detected_type"] != "phrase":
            for fp in r["files"]:
                fmap[fp].append(r["term"])

    written_pairs = set()
    count = 0
    for fp, terms in fmap.items():
        terms_u = list(set(terms))
        for i in range(len(terms_u)):
            for j in range(i+1, len(terms_u)):
                a, b = terms_u[i], terms_u[j]
                na = re.sub(r'[^a-z0-9]', '', a.lower())
                nb = re.sub(r'[^a-z0-9]', '', b.lower())
                if abs(len(na) - len(nb)) <= 2 and na != nb and len(na) > 3:
                    # simple char overlap ratio
                    shorter = min(na, nb, key=len)
                    longer  = max(na, nb, key=len)
                    if shorter in longer or (len(shorter) > 4 and longer[:4] == shorter[:4]):
                        pair = tuple(sorted([a, b]))
                        if pair not in written_pairs:
                            written_pairs.add(pair)
                            f.write(f"- `{a}` / `{b}` （{fp}）\n")
                            count += 1
                            if count >= 500:
                                break
            if count >= 500:
                break

print(f"6. synonym_candidates.md: {count} pairs", flush=True)

# ─── 7. unused_terms.md ──────────────────────────────────────────────────────
unused_path = OUT_DIR / "unused_terms.md"
unused = [r for r in records if r["occurrences"] == 1 and r["detected_type"] != "phrase"]

with open(unused_path, "w", encoding="utf-8") as f:
    f.write("# 孤立語候補（出現回数1回）\n\n")
    f.write(f"計 {len(unused)} 語\n\n")
    f.write("| Term | Detected Type | File |\n")
    f.write("|---|---|---|\n")
    for r in unused:
        fp = r["files"][0] if r["files"] else ""
        term_esc = r["term"].replace("|", "\\|")
        f.write(f"| {term_esc} | {r['detected_type']} | {fp} |\n")

print(f"7. unused_terms.md: {len(unused)} terms", flush=True)

# ─── 8. phrase_frequency.md ──────────────────────────────────────────────────
phrase_path = OUT_DIR / "phrase_frequency.md"
phrase_records = [r for r in records if r["detected_type"] == "phrase"]
phrase_records.sort(key=lambda r: -r["occurrences"])

with open(phrase_path, "w", encoding="utf-8") as f:
    f.write("# フレーズ頻度（上位100件）\n\n")
    f.write("| Phrase | Occurrences |\n")
    f.write("|---|---|\n")
    for r in phrase_records[:100]:
        term_esc = r["term"].replace("|", "\\|")
        f.write(f"| {term_esc} | {r['occurrences']} |\n")

print(f"8. phrase_frequency.md: {len(phrase_records)} phrases", flush=True)

# ─── 9. term_relationships.md ────────────────────────────────────────────────
rel_path = OUT_DIR / "term_relationships.md"

# Co-occurrence: count pairs that appear in same file 3+ times
pair_counter = Counter()
for fpath_str, terms_set in file_terms.items():
    terms_list = [t for t in terms_set if t in {r["term"] for r in records if r["detected_type"] != "phrase"}]
    if len(terms_list) < 2:
        continue
    for a, b in combinations(sorted(terms_list), 2):
        pair_counter[(a, b)] += 1

with open(rel_path, "w", encoding="utf-8") as f:
    f.write("# Term共出現関係（上位50ペア）\n\n")
    f.write("| Term A | Term B | Co-occurrence Files |\n")
    f.write("|---|---|---|\n")
    for (a, b), cnt in pair_counter.most_common(50):
        if cnt >= 3:
            a_esc = a.replace("|", "\\|")
            b_esc = b.replace("|", "\\|")
            f.write(f"| {a_esc} | {b_esc} | {cnt} |\n")

top50 = [(p, c) for p, c in pair_counter.most_common(50) if c >= 3]
print(f"9. term_relationships.md: {len(top50)} pairs", flush=True)

# ─── 10. category_candidates.md ──────────────────────────────────────────────
cand_path = OUT_DIR / "category_candidates.md"
unknowns = [r for r in records if r["category"] == "Unknown" and r["occurrences"] >= 5]

with open(cand_path, "w", encoding="utf-8") as f:
    f.write("# 再分類候補（Unknown カテゴリ、出現5回以上）\n\n")
    f.write(f"計 {len(unknowns)} 語\n\n")
    f.write("| Term | Occurrences | Detected Type | Primary Dir |\n")
    f.write("|---|---|---|---|\n")
    for r in unknowns:
        term_esc = r["term"].replace("|", "\\|")
        f.write(f"| {term_esc} | {r['occurrences']} | {r['detected_type']} | {r['directory']} |\n")

print(f"10. category_candidates.md: {len(unknowns)} terms", flush=True)

# ─── サマリー ─────────────────────────────────────────────────────────────────
print("\n=== 完了 ===")
print(f"スキャンファイル数: {file_count}")
print(f"抽出Term総数 (unique term+type pairs): {len(records)}")
print(f"ユニークterm名 (type無視): {len(set(r['term'] for r in records))}")
print(f"出力ディレクトリ: {OUT_DIR}")

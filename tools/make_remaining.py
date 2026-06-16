# tools/make_remaining.py
# term_relationships.md と category_candidates.md を軽量生成
import json
from pathlib import Path
from collections import defaultdict, Counter

RAW = Path(r"C:\Users\sirok\MoCKA\docs\reference\semantic_dictionary\raw")

# all_terms.json を読む
terms = json.loads((RAW / "all_terms.json").read_text(encoding="utf-8"))
print(f"Total terms: {len(terms)}")

# ── term_relationships.md ────────────────────────────────────────
# 同一ファイルに共出現するTermペア（上位50件）
# 重さを避けるため、出現数上位200語のみを対象にする
top200 = sorted(terms, key=lambda t: t["occurrences"], reverse=True)[:200]
file_to_terms = defaultdict(list)
for t in top200:
    for f in t["files"]:
        file_to_terms[f].append(t["term"])

pair_count = Counter()
for fterms in file_to_terms.values():
    fterms = list(set(fterms))
    for i in range(len(fterms)):
        for j in range(i+1, len(fterms)):
            pair = tuple(sorted([fterms[i], fterms[j]]))
            pair_count[pair] += 1

top50 = pair_count.most_common(50)
lines = ["# term_relationships.md\n", "同一ファイルに共出現するTermペア（上位50件 / 上位200語内）\n\n",
         "| Term A | Term B | 共出現ファイル数 |\n", "|---|---|---|\n"]
for (a, b), cnt in top50:
    lines.append(f"| {a} | {b} | {cnt} |\n")
(RAW / "term_relationships.md").write_text("".join(lines), encoding="utf-8")
print(f"term_relationships.md: {len(top50)} pairs")

# ── category_candidates.md ──────────────────────────────────────
# Unknown カテゴリで出現5回以上
unknowns = [t for t in terms if t["category"] == "Unknown" and t["occurrences"] >= 5]
unknowns.sort(key=lambda t: t["occurrences"], reverse=True)
lines = ["# category_candidates.md\n", f"カテゴリ未分類（Unknown）で出現5回以上のTerm — {len(unknowns)}件\n\n",
         "| Term | Occurrences | Detected Type | Files (抜粋) |\n", "|---|---|---|---|\n"]
for t in unknowns:
    f = ", ".join(t["files"][:2])
    lines.append(f"| {t['term']} | {t['occurrences']} | {t['detected_type']} | {f} |\n")
(RAW / "category_candidates.md").write_text("".join(lines), encoding="utf-8")
print(f"category_candidates.md: {len(unknowns)} terms")

print("DONE")

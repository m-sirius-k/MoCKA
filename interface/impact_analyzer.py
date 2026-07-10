"""
impact_analyzer.py -- TIC Layer 3
evaluation_queue.jsonl の各エントリ(source_id)を dependency_map.json の
component と照合し、影響を受けるコンポーネント(blast_radius)を自動列挙する。

照合方法: source_id/componentを"_"でトークン分割し、共有トークン数が多い順に
候補componentを決定する（例: anthropic_api_notes -> anthropic_api、
chrome_mv3 -> chrome_mv3）。既存のimpact_componentsフィールド(手動/移行由来)は
上書きせず、analyzer_*という新規フィールドとして追加する(risk_scorer.pyが
dependency_map.jsonへrisk_score/last_verifiedを追記するのと同じ、既存フィールド
非破壊の方式)。
"""

import json
import sys
import io
from pathlib import Path

# Windows cp932 環境でも確実に出力できるよう utf-8 強制（risk_scorer.pyと同一規約）
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

MAP_PATH = Path("C:/Users/sirok/MoCKA/data/tic/dependency_map.json")
QUEUE_PATH = Path("C:/Users/sirok/MoCKA/data/tic/evaluation_queue.jsonl")
MCP_URL = "http://localhost:5002/agent/mocka_write_event"


def _tokens(s: str) -> set:
    return set(s.lower().split("_"))


def match_components(source_id: str, dependencies: list) -> list:
    """source_idのトークンと各componentのトークンの重なりで照合する。
    重なりが1つ以上あるものを候補とし、重なり数の多い順に返す（同数は
    dependency_map記載順を維持）。"""
    src_tokens = _tokens(source_id)
    scored = []
    for dep in dependencies:
        overlap = len(src_tokens & _tokens(dep["component"]))
        if overlap > 0:
            scored.append((overlap, dep))
    scored.sort(key=lambda x: -x[0])
    return [dep for _, dep in scored]


def write_event(title: str, description: str, tags: str = "tic,impact_analyzer"):
    try:
        import urllib.request
        payload = json.dumps({
            "title": title,
            "description": description,
            "tags": tags,
            "why_purpose": "TIC影響分析(impact_analyzer.py)",
            "how_trigger": "impact_analyzer.py",
        }).encode("utf-8")
        req = urllib.request.Request(
            MCP_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=12)
    except Exception:
        pass  # MoCKAサーバー未起動でも継続


def run():
    if not MAP_PATH.exists():
        print(f"[ERROR] {MAP_PATH} not found")
        sys.exit(1)
    if not QUEUE_PATH.exists():
        print(f"[ERROR] {QUEUE_PATH} not found")
        sys.exit(1)

    dep_data = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    dependencies = dep_data["dependencies"]

    raw_lines = [l for l in QUEUE_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    entries = [json.loads(l) for l in raw_lines]

    unmatched_source_ids = set()
    matched_count = 0
    for entry in entries:
        matched_deps = match_components(entry.get("source_id", ""), dependencies)
        if matched_deps:
            blast_radius = []
            for dep in matched_deps:
                for component in dep.get("blast_radius", []):
                    if component not in blast_radius:
                        blast_radius.append(component)
            entry["analyzer_matched_components"] = [d["component"] for d in matched_deps]
            entry["analyzer_blast_radius"] = blast_radius
            entry["analyzer_max_risk_score"] = max(
                (d.get("risk_score", 0) for d in matched_deps), default=None
            )
            matched_count += 1
        else:
            entry["analyzer_matched_components"] = []
            entry["analyzer_blast_radius"] = []
            entry["analyzer_max_risk_score"] = None
            unmatched_source_ids.add(entry.get("source_id", ""))

    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"[impact_analyzer] {len(entries)}件処理完了 (照合成功: {matched_count}件)")
    if unmatched_source_ids:
        print(f"[impact_analyzer] 未照合のsource_id(要人手確認): {sorted(unmatched_source_ids)}")

    write_event(
        "IMPACT_ANALYSIS_UPDATED: TIC影響分析完了",
        f"全{len(entries)}件処理、照合成功{matched_count}件、"
        f"未照合{len(unmatched_source_ids)}件({sorted(unmatched_source_ids)})",
        "tic,impact_analyzer",
    )

    return entries


if __name__ == "__main__":
    run()

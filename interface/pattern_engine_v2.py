"""
pattern_engine_v2.py  (revision 2)
MoCKA 連鎖確率観測モデル

設計変更 (2026-04-27 rev2):
  MeCab依存の3-gram方式 → キーワード部分一致方式に変更。
  テキスト中にキーワードが含まれるかどうかで DANGER/SUCCESS を判定。
  MeCab不要・フォールバックでも確実に動作。
  組み込みキーワードをBuiltin定義として持ち、DBが空でも最低限動作。
"""

import csv, json, os, re
from datetime import datetime
from pathlib import Path
from typing import Optional

BASE_DIR              = Path(os.environ.get("MOCKA_ROOT", "C:/Users/sirok/MoCKA"))
REGISTRY_PATH         = BASE_DIR / "data" / "pattern_registry.csv"
SUCCESS_PATTERNS_PATH = BASE_DIR / "data" / "success_patterns.json"
EVENTS_CSV            = BASE_DIR / "data" / "events.csv"
LOG_PATH              = BASE_DIR / "logs" / "pattern_engine_v2.log"

THRESHOLDS = {"CRITICAL": 0.85, "DANGER": 0.65, "WARNING": 0.40, "SUCCESS": 0.60}

BUILTIN_DANGER = [
    "また同じエラー","また同じ問題","また失敗",
    "なぜ動かない","なぜ動かないのか","なぜこうなる","なぜこんなに",
    "意味がわからない","意味がわからん","どういうことか",
    "何度言っても","何度やっても","全然直らない",
    "うまくいかない","うまく動かない",
    "エラーが出た","エラーが発生","動かない",
    "失敗した","失敗しました",
    "どうしてこうなる","こんなはずじゃ","おかしい",
    "ai_violation","INSTRUCTION_IGNORE",
]
BUILTIN_SUCCESS = [
    "正常に動作","動作確認できました","動作確認",
    "完了しました","完了です","テストが通",
    "ALL CHECKS PASSED","修正済み","修正完了",
    "解決しました","うまくいきました","うまくいった",
    "動いた","動きました","成功しました",
    "確認できました","記録されました","再現できました",
]


class PatternRegistry:
    FIELDNAMES = ["pattern","outcome","count","danger_rate","success_rate",
                  "tier","source","created_at","updated_at"]

    def __init__(self, path: Path = REGISTRY_PATH):
        self.path = path
        self.records: dict[str, dict] = {}
        self._load()
        self._inject_builtins()

    def _load(self):
        if not self.path.exists():
            return
        with open(self.path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                k = row.get("pattern","").strip()
                if not k or k.startswith("#"):
                    continue
                self.records[k] = {
                    "pattern":k, "outcome":row.get("outcome","NEUTRAL"),
                    "count":int(row.get("count",0)),
                    "danger_rate":float(row.get("danger_rate",0.0)),
                    "success_rate":float(row.get("success_rate",0.0)),
                    "tier":int(row.get("tier",2)),
                    "source":row.get("source","auto"),
                    "created_at":row.get("created_at",datetime.now().isoformat()),
                    "updated_at":row.get("updated_at",datetime.now().isoformat()),
                }

    def _inject_builtins(self):
        now = datetime.now().isoformat()
        for kw in BUILTIN_DANGER:
            if kw not in self.records:
                self.records[kw] = {"pattern":kw,"outcome":"DANGER","count":0,
                    "danger_rate":1.0,"success_rate":0.0,"tier":1,"source":"builtin",
                    "created_at":now,"updated_at":now}
        for kw in BUILTIN_SUCCESS:
            if kw not in self.records:
                self.records[kw] = {"pattern":kw,"outcome":"SUCCESS","count":0,
                    "danger_rate":0.0,"success_rate":1.0,"tier":1,"source":"builtin",
                    "created_at":now,"updated_at":now}

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path,"w",encoding="utf-8",newline="") as f:
            w = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
            w.writeheader()
            for rec in sorted(self.records.values(),
                               key=lambda r: (-r["count"], r["outcome"], r["pattern"])):
                w.writerow(rec)

    def update_pattern(self, keyword: str, outcome: str, source: str = "auto"):
        now = datetime.now().isoformat()
        if keyword not in self.records:
            self.records[keyword] = {"pattern":keyword,"outcome":outcome,"count":0,
                "danger_rate":0.0,"success_rate":0.0,"tier":2,"source":source,
                "created_at":now,"updated_at":now}
        rec = self.records[keyword]
        rec["count"] += 1
        a = 0.10
        rec["danger_rate"]  = (1-a)*rec["danger_rate"]  + a*(1.0 if outcome=="DANGER"  else 0.0)
        rec["success_rate"] = (1-a)*rec["success_rate"] + a*(1.0 if outcome=="SUCCESS" else 0.0)
        rec["updated_at"] = now
        if rec["tier"] >= 2:
            if rec["danger_rate"] > 0.5:   rec["outcome"] = "DANGER"
            elif rec["success_rate"] > 0.5: rec["outcome"] = "SUCCESS"

    def danger_keywords(self):
        return [r for r in self.records.values() if r["outcome"]=="DANGER"]
    def success_keywords(self):
        return [r for r in self.records.values() if r["outcome"]=="SUCCESS"]
    def lookup(self, kw):
        return self.records.get(kw)


class PatternEngine:
    def __init__(self, registry=None):
        self.registry = registry or PatternRegistry()

    def analyze(self, text: str, update_registry=False, outcome_hint=None) -> dict:
        danger_hits, success_hits = [], []
        for rec in self.registry.danger_keywords():
            if rec["pattern"] in text:
                danger_hits.append(rec)
        for rec in self.registry.success_keywords():
            if rec["pattern"] in text:
                success_hits.append(rec)

        def score(hits, key):
            if not hits: return 0.0
            ws = [2.0 if h["tier"]==1 else 1.0 for h in hits]
            return min(1.0, sum(h[key]*w for h,w in zip(hits,ws)) / sum(ws))

        danger_score  = score(danger_hits,  "danger_rate")
        success_score = score(success_hits, "success_rate")

        # Tier1ヒットで底上げ
        if any(h["tier"]==1 for h in danger_hits):
            danger_score = max(danger_score, 0.70)

        R = min(1.0, danger_score * 1.2)

        if   danger_score  >= THRESHOLDS["CRITICAL"]: verdict = "CRITICAL"
        elif danger_score  >= THRESHOLDS["DANGER"]:   verdict = "DANGER"
        elif danger_score  >= THRESHOLDS["WARNING"]:  verdict = "WARNING"
        elif success_score >= THRESHOLDS["SUCCESS"]:  verdict = "SUCCESS"
        else:                                          verdict = "NEUTRAL"

        return {
            "verdict":         verdict,
            "danger_score":    round(danger_score, 4),
            "success_score":   round(success_score, 4),
            "R":               round(R, 4),
            "matched_danger":  [{"pattern":h["pattern"],"tier":h["tier"]} for h in danger_hits],
            "matched_success": [{"pattern":h["pattern"],"tier":h["tier"]} for h in success_hits],
            "input_length":    len(text),
        }

    def register_manual(self, text: str, outcome: str, tier: int = 1):
        kw = text.strip()
        now = datetime.now().isoformat()
        self.registry.records[kw] = {"pattern":kw,"outcome":outcome,"count":1,
            "danger_rate":1.0 if outcome=="DANGER" else 0.0,
            "success_rate":1.0 if outcome=="SUCCESS" else 0.0,
            "tier":tier,"source":"manual","created_at":now,"updated_at":now}
        self.registry.save()
        return {"registered":kw,"outcome":outcome,"tier":tier}

    def batch_analyze(self, texts):
        return [self.analyze(t) for t in texts]


def _log(msg):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH,"a",encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    print(msg)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="MoCKA Pattern Engine v2 rev2")
    sub = parser.add_subparsers(dest="cmd")
    pa = sub.add_parser("analyze"); pa.add_argument("text", nargs="+")
    pr = sub.add_parser("register"); pr.add_argument("text", nargs="+")
    pr.add_argument("--outcome", choices=["SUCCESS","DANGER","NEUTRAL"], required=True)
    pr.add_argument("--tier", type=int, default=1)
    sub.add_parser("stats")
    args = parser.parse_args()
    engine = PatternEngine()

    if args.cmd == "analyze":
        text = " ".join(args.text)
        r = engine.analyze(text)
        print(json.dumps(r, ensure_ascii=False, indent=2))
        _log(f"analyze: '{text[:60]}' → {r['verdict']} (R={r['R']})")

    elif args.cmd == "register":
        text = " ".join(args.text)
        r = engine.register_manual(text, args.outcome, args.tier)
        print(json.dumps(r, ensure_ascii=False, indent=2))
        _log(f"register: '{text}' as {args.outcome}")

    elif args.cmd == "stats":
        reg = engine.registry
        total = len(reg.records)
        d = len(reg.danger_keywords()); s = len(reg.success_keywords())
        t1 = sum(1 for r in reg.records.values() if r["tier"]==1)
        print(f"pattern_registry 統計\n  総キーワード数: {total}\n  DANGER: {d}\n  SUCCESS: {s}\n  NEUTRAL: {total-d-s}\n  Tier 1: {t1}")
        top5 = sorted(reg.records.values(), key=lambda r: -r["count"])[:5]
        if top5:
            print("\n  [Top5 観測数]")
            for r in top5:
                print(f"    {r['pattern'][:35]:<35} count={r['count']} {r['outcome']}")
    else:
        parser.print_help()

"""
incident_learner.py
MoCKA Language Algorithm v1.0 - 自己進化エンジン
インシデント発生時に文脈を分解し、新たな危険因子をdanger_patterns.jsonに自動追加
API通信: なし (0円)
E20260418_017
"""
import json, re, sys, csv
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from language_detector import LanguageDetector

PATTERNS_FILE = Path(__file__).parent / "danger_patterns.json"
LEARN_LOG     = Path(__file__).parent.parent / "data" / "language_learn_log.json"

class IncidentLearner:
    def __init__(self):
        self.detector = LanguageDetector()
        self.patterns = json.loads(PATTERNS_FILE.read_text(encoding="utf-8"))
        self._all_known = self._collect_all_known()

    def _collect_all_known(self):
        known = set()
        for tier in ["tier1","tier2","tier3","escalation","silent_danger"]:
            for p in self.patterns.get(tier,{}).get("patterns",[]):
                known.add(p.lower())
        return known

    def _extract_candidates(self, text):
        candidates = []
        sentences = re.split(r"[。！？\n]+", text)
        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            if 3 <= len(sent) <= 15:
                candidates.append({"text": sent, "reason": "短文フレーズ", "suggested_tier": "tier1"})
            m = re.search(r"(なぜ|どうして|なんで|どこが|何が|何を)(.{2,10})", sent)
            if m:
                candidates.append({"text": m.group(0), "reason": "疑問詞+動詞句", "suggested_tier": "tier2"})
            m = re.search(r"[\w\u3040-\u9FFF]{2,8}(するな|やめろ|止まれ|書くな|進めるな|変えるな)", sent)
            if m:
                candidates.append({"text": m.group(0), "reason": "否定命令形", "suggested_tier": "tier1"})
            m = re.search(r"[\w\u3040-\u9FFF]{1,8}(は違う|じゃない|ではない|でない)", sent)
            if m:
                candidates.append({"text": m.group(0), "reason": "否定断定形", "suggested_tier": "tier2"})
            m = re.search(r"\d+[時間日週ヶ月年](費やし|かかった|無駄|消えた|潰れた)", sent)
            if m:
                candidates.append({"text": m.group(0), "reason": "時間コスト言及", "suggested_tier": "tier2"})
        seen = set()
        result = []
        for c in candidates:
            t = c["text"].lower()
            if t not in self._all_known and t not in seen and len(t) >= 2:
                seen.add(t)
                result.append(c)
        return result

    def _classify_tier(self, candidate, detection):
        level = detection.get("level","INFO")
        suggested = candidate.get("suggested_tier","tier3")
        if level == "CRITICAL": return "tier1"
        elif level == "DANGER": return suggested if suggested in ("tier1","tier2") else "tier2"
        return "tier3"

    def learn(self, text, incident_id=None):
        detection = self.detector.analyze(text)
        level = detection.get("level","INFO")
        if level == "INFO":
            return {"status":"SKIP","reason":"INFOは学習対象外","level":level}
        candidates = self._extract_candidates(text)
        added = []
        for c in candidates:
            tier = self._classify_tier(c, detection)
            self.patterns[tier]["patterns"].append(c["text"])
            self._all_known.add(c["text"].lower())
            added.append({"pattern":c["text"],"tier":tier,"reason":c["reason"]})
        if added:
            self.patterns.setdefault("_meta",{})["last_updated"] = datetime.now().isoformat()
            PATTERNS_FILE.write_text(json.dumps(self.patterns,ensure_ascii=False,indent=2),encoding="utf-8")
        self._append_log(text, level, added, incident_id)
        return {"status":"LEARNED" if added else "NO_NEW_PATTERNS","level":level,"added":added,"total_added":len(added)}

    def _append_log(self, text, level, added, incident_id):
        try:
            LEARN_LOG.parent.mkdir(parents=True, exist_ok=True)
            entry = {"timestamp":datetime.now().isoformat(),"incident_id":incident_id or "manual",
                     "level":level,"text_preview":text[:100],"added_patterns":[a["pattern"] for a in added]}
            with open(LEARN_LOG,"a",encoding="utf-8") as f:
                f.write(json.dumps(entry,ensure_ascii=False)+"\n")
        except Exception as e:
            print(f"[LEARNER] ログ失敗: {e}")

    def learn_from_events_csv(self, events_csv, limit=20):
        results = []
        try:
            with open(events_csv, encoding="utf-8-sig", errors="replace") as f:
                rows = list(csv.DictReader(f))
        except Exception as e:
            return {"status":"ERROR","message":str(e)}
        incident_rows = [r for r in rows
            if any(kw in (r.get("title","") + r.get("short_summary",""))
                   for kw in ["INCIDENT","エラー","インシデント","失敗","CRITICAL"])][-limit:]
        for row in incident_rows:
            text = (row.get("short_summary","") + " " + row.get("title","")).strip()
            if not text: continue
            result = self.learn(text, incident_id=row.get("event_id",""))
            if result.get("added"):
                results.append(result)
                print(f"[LEARNER] {row.get('event_id','')} -> {len(result['added'])}件追加")
        return {"status":"COMPLETE","processed":len(incident_rows),"learned":len(results)}

if __name__ == "__main__":
    learner = IncidentLearner()
    result = learner.learn("なぜそうなる？動かない。また同じ。最悪。", "test")
    print(json.dumps(result, ensure_ascii=False, indent=2))

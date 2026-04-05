
import csv
import os
import random
from datetime import datetime
from collections import defaultdict

class MoCKARouter:

    def __init__(self):
        self.log_path = "runtime/record/event_log.csv"
        os.makedirs("runtime/record", exist_ok=True)

        self.providers = ["anthropic_claude", "gpt_audit", "gemini"]

        self.goal = "maximize_score"
        self.incident_threshold = 1

    def route(self, task: str):

        history = self._load_history()

        avg_scores = {}
        for p in self.providers:
            scores = history[p]
            avg_scores[p] = sum(scores)/len(scores) if scores else 1

        safe_providers = [
            p for p in self.providers
            if avg_scores[p] >= self.incident_threshold
        ]

        if not safe_providers:
            safe_providers = self.providers

        selected = max(safe_providers, key=lambda p: avg_scores[p])

        score = random.randint(1, 5)
        incident = score <= self.incident_threshold

        result = {
            "final_answer": f"[{selected}] executed {task}",
            "score": score,
            "selected": selected,
            "avg_scores": avg_scores,
            "goal": self.goal,
            "incident": incident,
            "threshold": self.incident_threshold
        }

        self._log(task, selected, score, incident)

        return result

    def _load_history(self):
        history = defaultdict(list)

        if not os.path.exists(self.log_path):
            return history

        with open(self.log_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    selected = row[4]
                    score = int(row[5])
                    history[selected].append(score)
                except:
                    continue

        return history

    def _log(self, task, selected, score, incident):
        with open(self.log_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                "router",
                "route",
                task,
                selected,
                score,
                incident
            ])

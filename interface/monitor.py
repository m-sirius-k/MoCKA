import time

class QuotaMonitor:
    def __init__(self):
        self.cooldowns = {}
        self.DURATION = 60  # 冷却時間(秒)

    def mark_failed(self, provider):
        self.cooldowns[provider] = time.time() + self.DURATION

    def is_available(self, provider):
        if provider not in self.cooldowns:
            return True
        if time.time() > self.cooldowns[provider]:
            del self.cooldowns[provider]
            return True
        return False

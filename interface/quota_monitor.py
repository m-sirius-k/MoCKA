import time

class QuotaMonitor:

    def __init__(self):
        self.cooldowns = {}

    def is_available(self, provider):
        if provider not in self.cooldowns:
            return True

        return time.time() > self.cooldowns[provider]

    def record_failure(self, provider, cooldown=60):
        self.cooldowns[provider] = time.time() + cooldown

    def record_success(self, provider):
        if provider in self.cooldowns:
            del self.cooldowns[provider]

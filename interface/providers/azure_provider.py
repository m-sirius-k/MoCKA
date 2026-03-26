import os
from .base import BaseProvider

class AzureProvider(BaseProvider):

    def name(self): return "azure"

    def is_available(self):
        return os.getenv("AZURE_AI_KEY") is not None

    def generate(self, request):
        return {
            "provider": "azure",
            "model": "gpt",
            "status": "success",
            "output": "[Azure] " + request["prompt"]
        }

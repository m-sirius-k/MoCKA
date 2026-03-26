import os
import requests

class AzureBrain:
    def __init__(self):
        self.api_key = os.getenv("AZURE_AI_KEY")
        self.endpoint = os.getenv("AZURE_AI_ENDPOINT")
        self.is_active = True if self.api_key and self.endpoint else False

    def get_status(self) -> bool:
        return self.is_active

    def think(self, prompt: str, context: dict) -> str:
        if not self.is_active: return ""
        try:
            headers = {"Content-Type": "application/json", "api-key": self.api_key}
            # Azure OpenAI / AI Studio Serverless 共通フォーマット
            payload = {
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 800,
                "temperature": 0.7
            }
            response = requests.post(self.endpoint, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            return f"ERROR: Azure {response.status_code}"
        except Exception as e:
            return f"ERROR: Azure Exception {str(e)}"

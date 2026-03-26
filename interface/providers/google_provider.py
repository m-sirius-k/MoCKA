import os
from google import genai
from .base import BaseProvider

class GoogleProvider(BaseProvider):

    def __init__(self):
        api_key = os.getenv("GOOGLE_AI_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = None

    def name(self):
        return "google"

    def is_available(self):
        return self.client is not None

    def generate(self, request):
        prompt = str(request["prompt"])

        res = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        text = getattr(res, "text", None)

        if not text:
            try:
                text = res.candidates[0].content.parts[0].text
            except Exception:
                text = str(res)

        return {
            "provider": "google",
            "model": "gemini-2.0-flash",
            "status": "success",
            "output": text
        }

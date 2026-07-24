from .base import BaseAdapter


class BrowserAdapter(BaseAdapter):
    def parse(self, request: dict) -> dict:
        return {
            "origin": request.get("source"),
            "url": request.get("url"),
            "mode": request.get("mode"),
        }

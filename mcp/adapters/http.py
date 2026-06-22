from .base import BaseAdapter


class HTTPAdapter(BaseAdapter):
    def parse(self, request: dict) -> dict:
        return {
            "endpoint": request.get("endpoint"),
            "method": request.get("method"),
            "body": request.get("body"),
        }

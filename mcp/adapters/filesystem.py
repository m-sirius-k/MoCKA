from .base import BaseAdapter


class FileSystemAdapter(BaseAdapter):
    def parse(self, request: dict) -> dict:
        return {
            "path": request.get("path"),
            "action": request.get("action"),
        }

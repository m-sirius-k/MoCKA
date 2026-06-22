class BaseAdapter:
    def parse(self, request: dict) -> dict:
        raise NotImplementedError

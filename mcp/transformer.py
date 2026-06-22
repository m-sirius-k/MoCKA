def transform(source: str, raw: dict) -> dict:
    """
    外部入力をMoCKA Event形式へ変換する唯一の層
    """
    return {
        "source": source,
        "payload": raw
    }

# -*- coding: utf-8 -*-


def transform(content: str) -> dict:
    return {
        "technical": make_technical(content),
        "business": make_business(content),
        "security": make_security(content),
        "academic": make_academic(content),
    }


def make_technical(c: str) -> str:
    return f"[TECH]\n{c}\n実装・構造・手順に焦点を当てる。"


def make_business(c: str) -> str:
    return f"[BUSINESS]\n{c}\nROI・業務改善・意思決定価値に変換。"


def make_security(c: str) -> str:
    return f"[SECURITY]\n{c}\n監査・再現性・リスク制御の観点。"


def make_academic(c: str) -> str:
    return f"[ACADEMIC]\n{c}\n概念モデル・構造原理として解釈。"

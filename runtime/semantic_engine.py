# FILE: runtime\semantic_engine.py

import re

# 日本語対応：N-gram分割
def ngrams(text, n=2):
    text = normalize(text)
    return {text[i:i+n] for i in range(len(text)-n+1)}

def normalize(text):
    text = text.lower()
    text = re.sub(r'[^\w\sぁ-んァ-ン一-龥]', '', text)
    return text

# 類似度（Jaccard）
def similarity(a, b):
    sa = ngrams(a)
    sb = ngrams(b)

    if not sa or not sb:
        return 0.0

    return len(sa & sb) / len(sa | sb)

def is_similar(a, b, threshold=0.3):
    return similarity(a, b) >= threshold


if __name__ == "__main__":
    a = "PowerShellで実行ミス"
    b = "実行方法ミス"

    print("similarity:", similarity(a, b))
    print("is_similar:", is_similar(a, b))

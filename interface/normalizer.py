import json
import re

class MoCKANormalizer:
    @staticmethod
    def clean_output(raw_data) -> str:
        # 1. 文字列化と基本クリーニング
        text = str(raw_data) if raw_data is not None else ""
        
        # 2. 429エラーやクォータ制限の検知
        if "RESOURCE_EXHAUSTED" in text or "Quota exceeded" in text:
            return "ERROR: Provider quota exceeded."

        # 3. 再帰的な [MEMORY RECALL] や JSON 文字列からの抽出
        # 文字列の中に 'text': '...' が含まれているか探す（もっとも深い階層を優先）
        try:
            # 簡易的な正規表現で text フィールドを抽出
            match = re.search(r"'(?:text|output)':\s*'([^']*)'", text)
            if not match:
                match = re.search(r'"(?:text|output)":\s*"([^"]*)"', text)
            
            if match:
                text = match.group(1)
        except:
            pass

        # 4. エスケープ文字の復元と整形
        text = text.replace("\\n", "\n").replace("\\'", "'").replace('\\"', '"')
        
        # 5. もし抽出後も JSON の残骸がある場合はさらにもう一段階剥ぐ
        if text.startswith("[MEMORY RECALL]"):
            text = text.replace("[MEMORY RECALL] ", "")

        return text.strip()

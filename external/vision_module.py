import pyautogui
from PIL import Image
import pytesseract
import os

class VisionModule:
    def __init__(self):
        # Tesseractのパス指定（必要に応じて修正）
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        self.name = "Vision_OCR_Observer"

    def capture_and_read(self, region=None):
        """
        region: (left, top, width, height) のタプル。
        指定がない場合は全画面をキャプチャ。
        """
        try:
            # 1. 指定領域（または全画面）を撮影
            screenshot = pyautogui.screenshot(region=region)
            
            # 2. OCR実行 (日本語と英語に対応)
            text = pytesseract.image_to_string(screenshot, lang='jpn+eng')
            
            return {
                "status": "success",
                "content": text.strip(),
                "provider": "Web_Free_Route"
            }
        except Exception as e:
            return {
                "status": "error",
                "content": str(e),
                "provider": "Vision_System"
            }

    def emergency_check(self):
        # 画面上に特定のAI（ChatGPTなど）のUI要素があるか簡易チェックするロジックをここに
        pass

"""
MoCKA Browser Tool v0.1
事前条件：以下コマンドでCometをデバッグモード起動済みであること
Start-Process "C:/Users/sirok/AppData/Local/Perplexity/Comet/Application/comet.exe" --remote-debugging-port=9222
"""
from playwright.sync_api import sync_playwright
import urllib.parse
import time

def send_and_collect(prompt: str) -> str:
    url = "https://chatgpt.com/?q=" + urllib.parse.quote(prompt)
    
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = context.new_page()
        page.goto(url)
        time.sleep(3)
        
        page.keyboard.press("Enter")
        print(f"[送信] {prompt[:50]}...")
        
        time.sleep(20)
        
        response = page.inner_text("[data-turn='assistant']")
        return response

if __name__ == "__main__":
    prompt = "MoCKAテスト：一言で返答してください。あなたは何ですか？"
    result = send_and_collect(prompt)
    print("=== ChatGPT回答 ===")
    print(result)

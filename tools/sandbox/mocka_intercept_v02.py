from playwright.sync_api import sync_playwright
import json
import time
import datetime
import urllib.parse
import atexit

logs = []

def save_logs():
    with open(r"C:\Users\sirok\MoCKA\tools\intercept_log.json", "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    print(f"\n=== {len(logs)}件記録完了 ===")

atexit.register(save_logs)

p = sync_playwright().start()
browser = p.chromium.connect_over_cdp("http://localhost:9222")
context = browser.contexts[0]
page = context.new_page()

def on_response(response):
    if "backend-api/conversation" in response.url:
        try:
            body = response.text()
        except:
            body = ""
        logs.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "url": response.url,
            "status": response.status,
            "body": body[:500]
        })
        print(f"[傍受] {response.status} {response.url[:70]}")

page.on("response", on_response)

prompt = "MoCKA傍受テスト：一言で返答してください。"
page.goto("https://chatgpt.com/?q=" + urllib.parse.quote(prompt))
time.sleep(3)
page.keyboard.press("Enter")
print("[送信] 待機中...")
time.sleep(25)

page.close()
p.stop()

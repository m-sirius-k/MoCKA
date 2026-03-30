from playwright.sync_api import sync_playwright
import json
import time

intercepted = []

p = sync_playwright().start()
browser = p.chromium.connect_over_cdp("http://localhost:9222")
context = browser.contexts[0]

page = context.new_page()

# ネットワーク傍受設定
def on_request(request):
    if "api" in request.url or "completion" in request.url or "message" in request.url:
        intercepted.append({
            "type": "REQUEST",
            "url": request.url,
            "method": request.method,
            "headers": dict(request.headers)
        })
        print(f"[REQ] {request.method} {request.url[:80]}")

def on_response(response):
    if "api" in response.url or "completion" in response.url or "message" in response.url:
        intercepted.append({
            "type": "RESPONSE",
            "url": response.url,
            "status": response.status
        })
        print(f"[RES] {response.status} {response.url[:80]}")

page.on("request", on_request)
page.on("response", on_response)

# ChatGPTで傍受テスト
page.goto("https://chatgpt.com/")
time.sleep(3)
page.keyboard.press("Enter")
time.sleep(10)

print(f"\n=== 傍受結果: {len(intercepted)}件 ===")
for item in intercepted[:10]:
    print(item)

page.close()
p.stop()

import sys
from playwright.sync_api import sync_playwright
import time

title = sys.argv[1] if len(sys.argv) > 1 else "無題"
body = sys.argv[2] if len(sys.argv) > 2 else ""

p = sync_playwright().start()
browser = p.chromium.connect_over_cdp("http://localhost:9222")
context = browser.contexts[0]

# 既存のControl Panelタブを探す
page = None
for pg in context.pages:
    if "localhost:5000" in pg.url:
        page = pg
        page.bring_to_front()
        page.reload()
        break

# なければ新規作成
if not page:
    page = context.new_page()
    page.goto("http://localhost:5000")

time.sleep(2)
page.click("#btnA")
time.sleep(1)
page.click("button.s-btn:has-text('infield')")
time.sleep(1)
page.fill("#title", title)
time.sleep(0.5)
page.fill("#memo", body)
time.sleep(0.5)
page.click("#exec")
time.sleep(3)
print(f"[保存完了] {title}")
p.stop()

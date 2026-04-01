from playwright.sync_api import sync_playwright
from datetime import datetime
import os

LOG_PATH = r"C:\Users\sirok\MoCKA\runtime\record\event_log.csv"

def write_log(action):
    if not os.path.exists(LOG_PATH):
        return
    timestamp = datetime.now().isoformat()
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{timestamp},playwright,action,{action}\n")

def run_browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://example.com")
        write_log("open_example.com")

        browser.close()

def main():
    print("=== Playwright Execution ===")
    run_browser()

if __name__ == "__main__":
    main()

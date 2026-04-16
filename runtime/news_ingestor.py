import json
import time
import urllib.request

INPUT_PATH = "input.json"

URL = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"

def load_input():
    try:
        with open(INPUT_PATH, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except:
        return []

def save_input(data):
    with open(INPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def fetch_news():
    with urllib.request.urlopen(URL) as response:
        return response.read().decode("utf-8")

def extract_titles(xml):
    titles = []
    parts = xml.split("<title>")

    for p in parts[2:]:  # skip first (channel title)
        title = p.split("</title>")[0]
        titles.append(title)

    return titles[:5]

def main():
    print("=== NEWS INGESTOR START ===")

    while True:
        try:
            xml = fetch_news()
            titles = extract_titles(xml)

            current = load_input()

            for t in titles:
                current.append({
                    "text": t,
                    "score": 0
                })

            save_input(current)

            print("NEWS ADDED:", len(titles))

        except Exception as e:
            print("ERROR:", e)

        time.sleep(60)

if __name__ == "__main__":
    main()

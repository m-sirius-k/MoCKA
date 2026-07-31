"""
Notion Decision Ledger DB の重複削除 + テストデータ削除
"""
import requests, os

k = os.environ.get('NOTION_API_KEY', '')
DB_ID = '5381e156-b742-4906-9b94-7e90f2842456'
HEADERS = {
    'Authorization': 'Bearer ' + k,
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28',
}

# 全ページ取得
pages = []
cursor = None
while True:
    body = {"page_size": 100}
    if cursor:
        body["start_cursor"] = cursor
    r = requests.post(f'https://api.notion.com/v1/databases/{DB_ID}/query',
                      headers=HEADERS, json=body)
    data = r.json()
    pages.extend(data.get('results', []))
    if not data.get('has_more'):
        break
    cursor = data.get('next_cursor')

print(f"Total pages: {len(pages)}")

# Decision IDごとにグループ化
from collections import defaultdict
groups = defaultdict(list)
for p in pages:
    title_list = p.get('properties', {}).get('Decision ID', {}).get('title', [])
    title = title_list[0]['text']['content'] if title_list else ''
    groups[title].append(p['id'])

# 重複削除: 最初の1件を残してあとはアーカイブ
deleted = 0
for title, ids in groups.items():
    # テストデータは全削除
    if title in ('TEST_001', 'TEST_002', ''):
        for pid in ids:
            requests.patch(f'https://api.notion.com/v1/pages/{pid}',
                          headers=HEADERS, json={'archived': True})
            deleted += 1
            print(f"  DEL test: {title} / {pid}")
        continue
    # 重複は最初の1件を残す
    if len(ids) > 1:
        for pid in ids[1:]:
            requests.patch(f'https://api.notion.com/v1/pages/{pid}',
                          headers=HEADERS, json={'archived': True})
            deleted += 1
            print(f"  DEL dup: {title} / {pid}")

print(f"\nDeleted: {deleted}")
print(f"Remaining: {len(pages) - deleted}")

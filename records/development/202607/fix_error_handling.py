f = open('interface/mocka_notion_sync.py', encoding='utf-8')
c = f.read()
f.close()

old = '''    if NOTION_API_KEY:
            res = notion_post("pages",{"parent":{"database_id":NOTION_DB_IDS["decisions"]},"properties":props})
            return bool(res.get("id"))'''

new = '''    if NOTION_API_KEY:
            try:
                res = notion_post("pages",{"parent":{"database_id":NOTION_DB_IDS["decisions"]},"properties":props})
                return bool(res.get("id"))
            except Exception as e:
                print(f"  [SKIP] {props.get('Decision ID',{}).get('title',[{}])[0].get('text',{}).get('content','?')} -> {e}")
                return False'''

c = c.replace(old, new)

old2 = '''    if NOTION_API_KEY:
            res = notion_post("pages",{"parent":{"database_id":NOTION_DB_IDS["events"]},"properties":props})
            return bool(res.get("id"))'''

new2 = '''    if NOTION_API_KEY:
            try:
                res = notion_post("pages",{"parent":{"database_id":NOTION_DB_IDS["events"]},"properties":props})
                return bool(res.get("id"))
            except Exception as e:
                print(f"  [SKIP] {props.get('Event ID',{}).get('title',[{}])[0].get('text',{}).get('content','?')} -> {e}")
                return False'''

c = c.replace(old2, new2)

old3 = '''    if NOTION_API_KEY:
            res = notion_post("pages",{"parent":{"database_id":NOTION_DB_IDS["incidents"]},"properties":props})
            return bool(res.get("id"))'''

new3 = '''    if NOTION_API_KEY:
            try:
                res = notion_post("pages",{"parent":{"database_id":NOTION_DB_IDS["incidents"]},"properties":props})
                return bool(res.get("id"))
            except Exception as e:
                print(f"  [SKIP] incident -> {e}")
                return False'''

c = c.replace(old3, new3)

f = open('interface/mocka_notion_sync.py', 'w', encoding='utf-8')
f.write(c)
f.close()
print('done')

f = open('interface/mocka_notion_sync.py', encoding='utf-8')
lines = f.readlines()
f.close()

# 95-98行目 (0-indexed: 94-97) を try/except で包む
# 現状: 95行目が "if NOTION_API_KEY:", 96が res=..., 97が return bool...
# 目標: try/except を追加してエラーをスキップ

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # push_decision内のnotion_post呼び出し行を検出
    if 'notion_post("pages",{"parent":{"database_id":NOTION_DB_IDS["decisions"]}' in line:
        indent = '        '
        new_lines.append(indent + 'try:\n')
        new_lines.append('    ' + line)  # res = notion_post(...)
        i += 1
        if i < len(lines) and 'return bool(res.get("id"))' in lines[i]:
            new_lines.append('    ' + lines[i])  # return bool(...)
            i += 1
        new_lines.append(indent + 'except Exception as e:\n')
        new_lines.append(indent + '    print(f"  [SKIP decision] {e}")\n')
        new_lines.append(indent + '    return False\n')
        continue
    # push_event内のnotion_post呼び出し行を検出
    elif 'notion_post("pages",{"parent":{"database_id":NOTION_DB_IDS["events"]}' in line:
        indent = '        '
        new_lines.append(indent + 'try:\n')
        new_lines.append('    ' + line)
        i += 1
        if i < len(lines) and 'return bool(res.get("id"))' in lines[i]:
            new_lines.append('    ' + lines[i])
            i += 1
        new_lines.append(indent + 'except Exception as e:\n')
        new_lines.append(indent + '    print(f"  [SKIP event] {e}")\n')
        new_lines.append(indent + '    return False\n')
        continue
    # push_incident内のnotion_post呼び出し行を検出
    elif 'notion_post("pages",{"parent":{"database_id":NOTION_DB_IDS["incidents"]}' in line:
        indent = '        '
        new_lines.append(indent + 'try:\n')
        new_lines.append('    ' + line)
        i += 1
        if i < len(lines) and 'return bool(res.get("id"))' in lines[i]:
            new_lines.append('    ' + lines[i])
            i += 1
        new_lines.append(indent + 'except Exception as e:\n')
        new_lines.append(indent + '    print(f"  [SKIP incident] {e}")\n')
        new_lines.append(indent + '    return False\n')
        continue
    else:
        new_lines.append(line)
    i += 1

f = open('interface/mocka_notion_sync.py', 'w', encoding='utf-8')
f.writelines(new_lines)
f.close()
print('done - patched', sum(1 for l in new_lines if '[SKIP' in l), 'locations')

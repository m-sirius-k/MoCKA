import json
from pathlib import Path

todo = json.loads(Path(r'C:\Users\sirok\MOCKA_TODO.json').read_text('utf-8'))

print('=== 未着手・着手中 ===')
for t in todo.get('todos', []):
    print(f"[{t['status']}] {t['id']}: {t['title']} (優先度:{t.get('priority','?')})")

print(f"\n=== 完了済み: {len(todo.get('completed',[]))}件 ===")
for t in todo.get('completed', [])[-5:]:
    print(f"[完了] {t['id']}: {t['title']}")

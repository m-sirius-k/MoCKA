from pathlib import Path

APP = Path('C:/Users/sirok/MoCKA/app.py')
content = APP.read_text(encoding='utf-8')

OLD = '''@app.route('/sync/todo', methods=['POST'])
def sync_todo():
    try:
        import json as _json
        from pathlib import Path as _Path
        _TODO = _Path('C:/Users/sirok/MOCKA_TODO.json')
        _data = _json.loads(_Path(_TODO).read_text(encoding='utf-8'))
        _todos = {t['id']: t for t in _data.get('todos',[]) + _data.get('completed',[]) if 'id' in t}'''

NEW = '''@app.route('/sync/todo', methods=['POST'])
def sync_todo():
    try:
        import json as _json
        from pathlib import Path as _Path
        _TODO = _Path('C:/Users/sirok/MOCKA_TODO.json')
        with _TODO.open('r', encoding='utf-8-sig') as _f:
            _data = _json.load(_f)
        if not isinstance(_data, dict):
            raise ValueError(f'top-level must be dict, got {type(_data).__name__}')
        _raw = (_data.get('todos') or []) + (_data.get('completed') or [])
        _todos = {}
        for _t in _raw:
            if not isinstance(_t, dict): continue
            _tid = _t.get('id')
            if _tid is None: continue
            _todos[str(_tid)] = _t'''

if OLD in content:
    content = content.replace(OLD, NEW, 1)
    APP.write_text(content, encoding='utf-8')
    print('OK: sync_todo fixed with GPT recommendation')
else:
    print('NG: pattern not found')
    idx = content.find('sync_todo')
    print(content[idx:idx+300])
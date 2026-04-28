from pathlib import Path

APP = Path('C:/Users/sirok/MoCKA/app.py')
content = APP.read_text(encoding='utf-8')

OLD = '''@app.route('/sync/todo', methods=['POST'])
def sync_todo():
    try:
        import sys
        sys.path.insert(0, 'C:/Users/sirok/MoCKA/interface')
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            'mocka_firestore_sync',
            'C:/Users/sirok/MoCKA/interface/mocka_firestore_sync.py'
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        data = mod.load_local()
        todos = mod.local_map(data)
        ok = 0
        errors = []
        for tid, todo in todos.items():
            try:
                mod.fs_patch(tid, todo)
                ok += 1
            except Exception as e:
                errors.append(str(e)[:80])
        return jsonify({'status': 'ok', 'pushed': ok, 'errors': errors})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500'''

NEW = '''@app.route('/sync/todo', methods=['POST'])
def sync_todo():
    try:
        import json as _json
        from pathlib import Path as _Path
        _TODO = _Path('C:/Users/sirok/MOCKA_TODO.json')
        _data = _json.loads(_Path(_TODO).read_text(encoding='utf-8'))
        _todos = {t['id']: t for t in _data.get('todos',[]) + _data.get('completed',[]) if 'id' in t}
        import urllib.request as _req, urllib.error as _uerr
        _PROJECT = 'mocka-knowledge-gate'
        _KEY = __import__('os').environ.get('MOCKA_FIREBASE_API_KEY','')
        _ok, _errors = 0, []
        for tid, todo in _todos.items():
            try:
                _url = f'https://firestore.googleapis.com/v1/projects/{_PROJECT}/databases/(default)/documents/todos/{tid}?key={_KEY}'
                _fields = {k: ({'stringValue': str(v)} if not isinstance(v, bool) else {'booleanValue': v}) for k, v in todo.items()}
                _body = _json.dumps({'fields': _fields}).encode('utf-8')
                _r = _req.Request(_url, data=_body, method='PATCH')
                _r.add_header('Content-Type', 'application/json')
                with _req.urlopen(_r, timeout=5) as _resp:
                    _resp.read()
                _ok += 1
            except Exception as e:
                _errors.append(f'{tid}: {str(e)[:60]}')
        return jsonify({'status': 'ok', 'pushed': _ok, 'total': len(_todos), 'errors': _errors[:5]})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500'''

if OLD in content:
    content = content.replace(OLD, NEW, 1)
    APP.write_text(content, encoding='utf-8')
    print('OK: sync_todo replaced with direct implementation')
else:
    print('NG: pattern not found')
    idx = content.find('sync_todo')
    print(content[idx:idx+100])
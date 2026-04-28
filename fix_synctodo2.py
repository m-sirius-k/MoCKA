from pathlib import Path

APP = Path('C:/Users/sirok/MoCKA/app.py')
content = APP.read_text(encoding='utf-8')

OLD = '''@app.route('/sync/todo', methods=['POST'])
def sync_todo():
    try:
        import subprocess, sys
        r = subprocess.run(
            [sys.executable, 'interface/mocka_firestore_sync.py', 'push'],
            capture_output=True, text=True, timeout=30,
            cwd='C:/Users/sirok/MoCKA'
        )
        return jsonify({'status': 'ok', 'output': r.stdout[-500:], 'error': r.stderr[-200:]})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500'''

NEW = '''@app.route('/sync/todo', methods=['POST'])
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

if OLD in content:
    content = content.replace(OLD, NEW, 1)
    APP.write_text(content, encoding='utf-8')
    print('OK: sync_todo replaced')
else:
    print('NG: pattern not found')
    idx = content.find('sync_todo')
    print(f'sync_todo at: {idx}')
    print(content[idx:idx+200])
from pathlib import Path

APP = Path('C:/Users/sirok/MoCKA/app.py')
content = APP.read_text(encoding='utf-8')

if '/sync/todo' in content:
    print('- already exists')
    exit(0)

INSERT = '''
@app.route('/sync/todo', methods=['POST'])
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
        return jsonify({'status': 'error', 'message': str(e)}), 500

'''

MARKER = 'if __name__ == "__main__":'
content = content.replace(MARKER, INSERT + MARKER, 1)
APP.write_text(content, encoding='utf-8')
print('OK: /sync/todo added')
from pathlib import Path

APP = Path('C:/Users/sirok/MoCKA/app.py')
lines = APP.read_text(encoding='utf-8').splitlines()

for i, line in enumerate(lines):
    if 'def sync_todo' in line:
        lines.insert(i+1, '    print("SYNC_TODO_V3_ENTERED")')
        print(f'OK: debug print inserted at line {i+1}')
        break

APP.write_text('\n'.join(lines), encoding='utf-8')
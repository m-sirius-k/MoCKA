from pathlib import Path

APP = Path('C:/Users/sirok/MoCKA/app.py')
lines = APP.read_text(encoding='utf-8').splitlines()

for i, line in enumerate(lines):
    if '_fields = {k:' in line or ("_fields" in line and "stringValue" in line):
        print(f'Found at line {i}: {line.strip()}')
        lines[i] = '''                _fields = {}
                for _k, _v in todo.items():
                    if _v is None: continue
                    elif isinstance(_v, bool): _fields[_k] = {'booleanValue': _v}
                    elif isinstance(_v, int): _fields[_k] = {'integerValue': str(_v)}
                    elif isinstance(_v, float): _fields[_k] = {'doubleValue': _v}
                    else: _fields[_k] = {'stringValue': str(_v)}'''
        APP.write_text('\n'.join(lines), encoding='utf-8')
        print('OK: fixed')
        break
else:
    print('NG: line not found')
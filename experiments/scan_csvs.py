import csv, os

targets = [
    r'C:\Users\sirok\MoCKA\data\failure_log.csv',
    r'C:\Users\sirok\MoCKA\runtime\incident_log.csv',
    r'C:\Users\sirok\MoCKA\runtime\record\event_log.csv',
    r'C:\Users\sirok\MoCKA\runtime\master_index.csv',
    r'C:\Users\sirok\MoCKA\scripts\analysis\mocka_repo_analysis_20260328_1754.csv',
    r'C:\Users\sirok\MoCKA\mocka-governance-kernel\governance\impact_registry.csv',
    r'C:\Users\sirok\MoCKA\mocka-governance-kernel\governance\change_log.csv',
    r'C:\Users\sirok\MoCKA\governance\outfield\phase24_export_A.csv',
    r'C:\Users\sirok\MoCKA\archive\ledger_old\record\event_log.csv',
]

for path in targets:
    if not os.path.exists(path):
        continue
    size = os.path.getsize(path)
    print('')
    print('=' * 55)
    print('  ' + os.path.basename(path) + ' (' + str(size) + 'bytes)')
    print('=' * 55)
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        print('  行数: ' + str(len(lines)))
        print('  先頭3行:')
        for line in lines[:3]:
            print('  ' + line.strip()[:120])
    except Exception as e:
        print('  ERR: ' + str(e))

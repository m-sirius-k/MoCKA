import csv, os
from datetime import datetime

EVENTS_CSV = r'C:\Users\sirok\MoCKA\data\events.csv'
RECURRENCE_OUT = r'C:\Users\sirok\MoCKA\data\recurrence_registry.csv'

def safe(val):
    return (val or '').lower()

def load_events():
    events = []
    with open(EVENTS_CSV, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            events.append(row)
    return events

def find_recurrences(events):
    recurrences = []
    seen = {}
    for ev in events:
        what      = safe(ev.get('what_type'))
        note      = safe(ev.get('free_note'))
        summary   = safe(ev.get('short_summary'))
        component = safe(ev.get('where_component'))
        eid       = safe(ev.get('event_id'))
        when      = safe(ev.get('when'))

        is_incident = any(k in note+summary for k in [
            'error=1','ERROR','error:','incident','failure','failed','corrupt',
            '\u969c\u5bb3','\u30a8\u30e9\u30fc','\u5931\u6557',
            
        ])
        if not is_incident:
            continue

        key = (component, what)
        if key in seen:
            prev = seen[key]
            count = prev.get('count', 1) + 1
            recurrences.append({
                'recurrence_id': 'REC_' + str(len(recurrences)+1).zfill(4),
                'current_event_id': eid,
                'current_when': when,
                'original_event_id': prev['event_id'],
                'original_when': prev['when'],
                'component': component,
                'what_type': what,
                'recurrence_count': count,
                'note': '\u540c\u4e00\u30b3\u30f3\u30dd\u30fc\u30cd\u30f3\u30c8\u30fb\u540c\u4e00\u51e6\u7406\u30bf\u30a4\u30d7\u306e\u518d\u767a',
            })
            seen[key] = {'event_id': eid, 'when': when, 'count': count}
        else:
            seen[key] = {'event_id': eid, 'when': when, 'count': 1}
    return recurrences

print('')
print('=' * 60)
print('  Recurrence Registry \u751f\u6210')
print('=' * 60)

events = load_events()
print('  events.csv \u8aad\u8fbc: {}\u4ef6'.format(len(events)))

recurrences = find_recurrences(events)
print('  \u518d\u767a\u691c\u51fa: {}\u4ef6'.format(len(recurrences)))

if recurrences:
    with open(RECURRENCE_OUT, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=recurrences[0].keys())
        writer.writeheader()
        writer.writerows(recurrences)
    print('')
    for r in recurrences[:10]:
        print('  [REC_{:>3}] {}x | {} | {} -> {}'.format(
            r['recurrence_id'], r['recurrence_count'],
            r['component'][:20],
            r['original_event_id'][:15],
            r['current_event_id'][:15]))
    print('')
    print('  \u4fdd\u5b58: ' + RECURRENCE_OUT)
else:
    print('  \u518d\u767a\u30d1\u30bf\u30fc\u30f3\u306a\u3057')
print('=' * 60)




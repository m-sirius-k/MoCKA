import sqlite3

conn = sqlite3.connect('data/mocka_events.db')
cursor = conn.cursor()

# Get all columns with their properties
cursor.execute('PRAGMA table_info(events)')
cols = cursor.fetchall()

print("Columns with NOT NULL constraints (and no default):")
print()

not_null_no_default = []
for col_id, name, type_, notnull, dflt_value, pk in cols:
    if notnull and dflt_value is None:
        not_null_no_default.append(name)
        print(f"  {name:<20} (type: {type_}, pk: {pk})")

print()
print(f"Total: {len(not_null_no_default)} columns")

# List columns we're providing in _write
provided_cols = {
    'event_id', 'when_ts', 'who_actor', 'what_type', 'where_component',
    'where_path', 'why_purpose', 'how_trigger', 'before_state', 'after_state',
    'title', 'short_summary', 'session_id', '_source', 'channel_type',
    'lifecycle_phase', 'risk_level', 'request_id', 'free_note'
}

print()
print("Missing NOT NULL columns (not provided by _write()):")
for col in not_null_no_default:
    if col not in provided_cols:
        print(f"  - {col}")

conn.close()

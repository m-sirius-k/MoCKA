import sqlite3
import datetime
from pathlib import Path

db_path = Path('data/mocka_events.db')
con = sqlite3.connect(str(db_path))

today = datetime.date.today().strftime("%Y%m%d")

# Reset counter for today only
con.execute("DELETE FROM decision_id_counters WHERE date = ?", (today,))
con.commit()

print(f"Counter for {today} reset")

# Verify
row = con.execute("SELECT counter FROM decision_id_counters WHERE date = ?", (today,)).fetchone()
if row:
    print(f"Counter still exists: {row[0]}")
else:
    print("Counter deleted successfully")

con.close()

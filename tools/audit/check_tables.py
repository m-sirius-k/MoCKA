import sqlite3

c = sqlite3.connect("data/mocka_events.db").cursor()

for row in c.execute("select name from sqlite_master where type='table'"):
    print(row)

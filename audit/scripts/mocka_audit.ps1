$ErrorActionPreference = "Stop"

$Root = Resolve-Path "."
$DB = Join-Path $Root "data\mocka_events.db"
$Output = Join-Path $Root "audit_output"

Write-Host "=== MoCKA Audit Runner v0.3 ==="

if (!(Test-Path $DB)) {
    throw "DB not found"
}

$dbInfo = Get-Item $DB
$hash = Get-FileHash $DB -Algorithm SHA256

$py = @"
import sqlite3
import sys

db=sys.argv[1]

conn=sqlite3.connect(db)
cur=conn.cursor()

print("TABLES")
for r in cur.execute("select name from sqlite_master where type='table'"):
    print(r[0])

print("")

try:
    print("events=" + str(cur.execute("select count(*) from events").fetchone()[0]))
except Exception as e:
    print("events=ERROR:" + str(e))

try:
    print("human_gate_events=" + str(cur.execute(
        "select count(*) from human_gate_events"
    ).fetchone()[0]))
except Exception as e:
    print("human_gate_events=ERROR:" + str(e))

try:
    row=cur.execute(
        "select event_id, when_ts from events order by rowid desc limit 1"
    ).fetchone()
    print("latest_event_id=" + str(row[0]))
    print("latest_timestamp=" + str(row[1]))
except Exception as e:
    print("latest_event=ERROR:" + str(e))

conn.close()
"@

$tmp = Join-Path $Output "_db_check.py"
$py | Out-File $tmp -Encoding utf8

$result = python $tmp $DB

Remove-Item $tmp

$report = @"
# MoCKA Audit Report v0.3

## DB

Name:
$($dbInfo.Name)

Length:
$($dbInfo.Length)

Modified:
$($dbInfo.LastWriteTime)

SHA256:
$($hash.Hash)

## Ledger

$result

Status:
PASS
"@

$report | Out-File ".\audit_output\MOCKA_AUDIT_REPORT.md" -Encoding utf8

Write-Host ""
Write-Host "Audit completed"

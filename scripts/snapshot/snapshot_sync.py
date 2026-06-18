import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿import shutil
import os

SRC="runtime/snapshots"
DST="runtime/remote_snapshots"

os.makedirs(DST,exist_ok=True)

files=os.listdir(SRC)

for f in files:

    s=os.path.join(SRC,f)
    d=os.path.join(DST,f)

    if not os.path.exists(d):

        shutil.copy(s,d)

        print("SNAPSHOT SYNC",f)

print("SNAPSHOT REPLICATION DONE")

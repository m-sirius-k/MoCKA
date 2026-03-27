import shutil
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

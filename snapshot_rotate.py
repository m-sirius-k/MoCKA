import os
import time

SNAP_DIR = "runtime/snapshots"
KEEP = 50

print("SNAPSHOT ROTATION START")

while True:

    if os.path.exists(SNAP_DIR):

        files = sorted(os.listdir(SNAP_DIR))

        if len(files) > KEEP:

            remove = files[0:len(files)-KEEP]

            for f in remove:

                path = os.path.join(SNAP_DIR,f)

                try:
                    os.remove(path)
                    print("ROTATED",f)
                except:
                    pass

    time.sleep(60)


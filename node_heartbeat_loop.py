import time
import subprocess

while True:
    subprocess.run(["python","node_heartbeat.py"])
    print("heartbeat sent")
    time.sleep(30)

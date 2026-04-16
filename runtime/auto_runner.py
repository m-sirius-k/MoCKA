import time
import os
import subprocess

TARGET = "input_raw.txt"
LAST = 0

def run_pipeline():
    print("=== PIPELINE START ===")
    subprocess.run(["python", "ocr_to_intent.py"])
    subprocess.run(["python", "intent_ingestor.py"])
    subprocess.run(["python", "main_loop.py"])
    print("=== PIPELINE END ===")

while True:
    if os.path.exists(TARGET):
        t = os.path.getmtime(TARGET)
        if t != LAST:
            LAST = t
            run_pipeline()
    time.sleep(2)

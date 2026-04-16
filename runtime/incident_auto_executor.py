# FILE: runtime\incident_auto_executor.py

import subprocess
import sys

def auto_execute(fix):
    print("\n=== AUTO EXECUTION ===")

    # ルール1：.pyで実行すべきケース
    if ".py" in fix or "ファイルで実行" in fix:
        print("Re-running correctly via python file...")
        subprocess.run(["python", "runtime/run_save.py"])
        return

    print("No auto rule matched. Manual action required.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python incident_auto_executor.py <fix_text>")
        sys.exit(0)

    auto_execute(sys.argv[1])

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

def decision_hook():
    # 全統一MoCKA/tools
    steps = []
    for script in ['gen_audit_event.py', 'verify_audit_event.py', 'verify_artifact_sha256.py']:
        script_path = os.path.join(ROOT, script)
        if os.path.exists(script_path):
            try:
                subprocess.check_call([sys.executable, script_path])
                steps.append(f"OK: {script}")
            except:
                steps.append(f"FAIL: {script}")
        else:
            steps.append(f"SKIP: {script}")

    print('PHASE4 audit chain:', ' | '.join(steps))
    return 0

if __name__ == '__main__':
    decision_hook()

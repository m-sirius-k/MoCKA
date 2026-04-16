cd C:\Users\sirok\MoCKA
.\tools\kpa_update_sot_auto.ps1 -TargetPath "src\mocka_policy.py"
.\tools\execution_reconfirm_auto.ps1
.\.venv\Scripts\python.exe run_with_audit.py

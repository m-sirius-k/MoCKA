@echo off
:: Orchestra One - Native Messaging Host Launcher
:: Chromeから直接呼び出されるラッパー。Python環境を起動してホストを実行する。
set "SCRIPT_DIR=%~dp0"
python "%SCRIPT_DIR%orchestra_one_host.py"

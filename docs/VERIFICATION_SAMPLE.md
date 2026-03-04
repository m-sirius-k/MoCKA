MoCKA Verification Sample

ENGLISH VERSION

Purpose

This document shows a minimal example of how the MoCKA verification system runs.

Research Gate execution

cd C:\Users\sirok\mocka-ecosystem
powershell -ExecutionPolicy Bypass -File .\MoCKA\tools\mocka_research_run.ps1

Expected output example

RUN_EXPERIMENT: ecosystem_structure_scan
OK_EXPERIMENT: ecosystem_structure_scan

RUN_EXPERIMENT: repo_git_clean_check
OK_EXPERIMENT: repo_git_clean_check

RESEARCH_RUN: OK

Meaning

All structural experiments passed.
The ecosystem integrity is verified.

Doctor artifact example

Artifacts are generated in

MoCKA/artifacts/doctor_runs

Example files

doctor_run_YYYYMMDD_HHMMSS.json
doctor_run_YYYYMMDD_HHMMSS.sha256.txt

These files prove that the integrity scan was executed.


日本語版

目的

この文書は MoCKA の検証システムを最小手順で確認する例を示します。

Research Gate 実行

cd C:\Users\sirok\mocka-ecosystem
powershell -ExecutionPolicy Bypass -File .\MoCKA\tools\mocka_research_run.ps1

出力例

RUN_EXPERIMENT: ecosystem_structure_scan
OK_EXPERIMENT: ecosystem_structure_scan

RUN_EXPERIMENT: repo_git_clean_check
OK_EXPERIMENT: repo_git_clean_check

RESEARCH_RUN: OK

意味

すべての構造実験が成功し
エコシステムの整合性が確認された状態です。

Doctor アーティファクト

生成場所

MoCKA/artifacts/doctor_runs

生成例

doctor_run_YYYYMMDD_HHMMSS.json
doctor_run_YYYYMMDD_HHMMSS.sha256.txt

これらは検証が実行された証拠になります。


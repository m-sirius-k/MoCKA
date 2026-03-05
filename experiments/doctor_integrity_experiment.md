# Experiment: Ecosystem Integrity Check

## Purpose
Verify that the MoCKA Insight System repositories remain structurally consistent.

## Environment
Windows PowerShell

## Inputs
mocka-ecosystem root directory

## Procedure

cd C:\Users\sirok\mocka-ecosystem
powershell -ExecutionPolicy Bypass -File .\mocka_doctor.ps1

## Expected Result

SUMMARY
DIRTY GIT REPOS: NONE
BROKEN LINKS: NONE
MERMAID ISSUES: NONE

## Verification
Check doctor output summary.

## Artifacts
none

## Related Repo
MoCKA

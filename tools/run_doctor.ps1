param(
  [string]$Root = "C:\Users\sirok\mocka-ecosystem"
)

$ErrorActionPreference = "Stop"

$doctor = Join-Path $Root "mocka_doctor.ps1"
if(-not (Test-Path -LiteralPath $doctor)){
  throw "DOCTOR_NOT_FOUND: $doctor"
}

powershell -ExecutionPolicy Bypass -File $doctor

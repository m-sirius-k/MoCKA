# ============================================================
# MoCKA Repository Density Analysis
# 8 Core Repositories — Volume · File Count · Code Density
# ============================================================

$repos = @(
    @{ Name = "MoCKA";                Path = "C:\Users\sirok\MoCKA" },
    @{ Name = "MoCKA-KNOWLEDGE-GATE"; Path = "C:\Users\sirok\mocka-knowledge-gate" },
    @{ Name = "mocka-runtime";        Path = "C:\Users\sirok\mocka-runtime" },
    @{ Name = "mocka-transparency";   Path = "C:\Users\sirok\mocka-transparency" },
    @{ Name = "mocka-external-brain"; Path = "C:\Users\sirok\mocka-external-brain" },
    @{ Name = "mocka-civilization";   Path = "C:\Users\sirok\mocka-civilization" },
    @{ Name = "mocka-public";         Path = "C:\Users\sirok\mocka-public" },
    @{ Name = "mocka-outfield";       Path = "C:\Users\sirok\mocka-outfield" }
)
$codeExtensions = @(".py",".js",".ts",".json",".yaml",".yml",".md",".sh",".ps1",".html",".css")
$results = @()

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  MoCKA Core Repository Analysis  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

foreach ($repo in $repos) {
    Write-Host "Scanning: $($repo.Name) ..." -ForegroundColor Yellow
    if (-not (Test-Path $repo.Path)) {
        Write-Host "  [NOT FOUND] $($repo.Path)" -ForegroundColor Red
        $results += [PSCustomObject]@{ Name=$repo.Name; Exists=$false; TotalSizeMB=0; TotalFiles=0; CodeFiles=0; TotalLines=0; PyFiles=0; JsFiles=0; MdFiles=0; JsonFiles=0; GitCommits="N/A"; LastModified="N/A" }
        continue
    }
    $allFiles = Get-ChildItem -Path $repo.Path -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notmatch '\\\.git\\' }
    $totalSizeMB = [math]::Round((($allFiles | Measure-Object -Property Length -Sum).Sum / 1MB), 2)
    $codeFiles = $allFiles | Where-Object { $codeExtensions -contains $_.Extension.ToLower() }
    $totalLines = 0
    foreach ($f in $codeFiles) { try { $totalLines += (Get-Content $f.FullName -ErrorAction SilentlyContinue | Measure-Object -Line).Lines } catch {} }
    $gitCommits = if (Test-Path (Join-Path $repo.Path ".git")) { (& git -C $repo.Path rev-list --count HEAD 2>$null) } else { "N/A" }
    $lastMod = ($allFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime
    $results += [PSCustomObject]@{
        Name=$repo.Name; Exists=$true; TotalSizeMB=$totalSizeMB
        TotalFiles=$allFiles.Count; CodeFiles=$codeFiles.Count; TotalLines=$totalLines
        PyFiles=($allFiles | Where-Object { $_.Extension -eq ".py" }).Count
        JsFiles=($allFiles | Where-Object { $_.Extension -in ".js",".ts" }).Count
        MdFiles=($allFiles | Where-Object { $_.Extension -eq ".md" }).Count
        JsonFiles=($allFiles | Where-Object { $_.Extension -eq ".json" }).Count
        GitCommits=$gitCommits
        LastModified=if($lastMod){$lastMod.ToString("yyyy-MM-dd HH:mm")}else{"N/A"}
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  RESULTS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
$header = "{0,-26} {1,8} {2,7} {3,7} {4,9} {5,5} {6,5} {7,5} {8,7} {9,16}" -f "Repository","Size(MB)","Files","Code","Lines",".py",".js",".md","Commits","LastModified"
Write-Host $header -ForegroundColor White
Write-Host ("-" * 100) -ForegroundColor DarkGray
foreach ($r in $results) {
    $c = if ($r.Exists) { "Green" } else { "Red" }
    Write-Host ("{0,-26} {1,8} {2,7} {3,7} {4,9} {5,5} {6,5} {7,5} {8,7} {9,16}" -f $r.Name,$r.TotalSizeMB,$r.TotalFiles,$r.CodeFiles,$r.TotalLines,$r.PyFiles,$r.JsFiles,$r.MdFiles,$r.GitCommits,$r.LastModified) -ForegroundColor $c
}
Write-Host ("-" * 100) -ForegroundColor DarkGray
Write-Host ("{0,-26} {1,8} {2,7} {3,7} {4,9}" -f "TOTAL",[math]::Round(($results|Measure-Object TotalSizeMB -Sum).Sum,2),($results|Measure-Object TotalFiles -Sum).Sum,($results|Measure-Object CodeFiles -Sum).Sum,($results|Measure-Object TotalLines -Sum).Sum) -ForegroundColor Cyan

Write-Host ""
Write-Host "  DENSITY RANKING (by Lines of Code)" -ForegroundColor Cyan
Write-Host ("-" * 60) -ForegroundColor DarkGray
$rank=1
$results | Where-Object { $_.Exists } | Sort-Object TotalLines -Descending | ForEach-Object {
    $bar = "#" * [math]::Min([math]::Round($_.TotalLines/200),40)
    Write-Host ("  #{0} {1,-26} {2,7} lines  {3}" -f $rank,$_.Name,$_.TotalLines,$bar) -ForegroundColor Yellow
    $rank++
}

$csvPath = "C:\Users\sirok\MoCKA\scripts\analysis\mocka_repo_analysis_$(Get-Date -Format 'yyyyMMdd_HHmm').csv"
$results | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
Write-Host ""
Write-Host "  CSV saved: $csvPath" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

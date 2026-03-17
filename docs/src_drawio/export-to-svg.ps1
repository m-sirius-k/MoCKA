# draw.io ファイルを SVG にエクスポート

# スクリプトのディレクトリに移動
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# draw.io CLI が使用可能か確認
try {
    $drawioVersion = & npx draw.io --version 2>&1
    Write-Host "✓ draw.io CLI が見つかりました: $drawioVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ draw.io CLI がインストールされていません。インストール中..." -ForegroundColor Yellow
    npm install -g drawio
}

# ローカルの drawio ファイルを検索
$drawioFiles = Get-ChildItem -Filter "*.drawio" -File

if ($drawioFiles.Count -eq 0) {
    Write-Host "✗ .drawio ファイルが見つかりません" -ForegroundColor Red
    exit 1
}

Write-Host "`n📊 $($drawioFiles.Count) 個のファイルをエクスポート中...`n" -ForegroundColor Cyan

# 各ファイルをエクスポート
foreach ($file in $drawioFiles) {
    $outputFile = $file.BaseName + ".svg"
    Write-Host "処理中: $($file.Name) → $outputFile" -ForegroundColor Yellow
    
    try {
        & npx draw.io --export --format svg --output $outputFile $file.FullName
        Write-Host "✓ 完了: $outputFile" -ForegroundColor Green
    } catch {
        Write-Host "✗ エラー: $($file.Name)" -ForegroundColor Red
        Write-Host $_ -ForegroundColor Red
    }
}

Write-Host "`n✓ エクスポート完了！" -ForegroundColor Green
Write-Host "出力ファイル:" -ForegroundColor Cyan
Get-ChildItem -Filter "*.svg" -File | ForEach-Object {
    Write-Host "  - $($_.Name)" -ForegroundColor Green
}

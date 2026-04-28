# ==============================
# MoCKA パターン一括登録スクリプト v3
# グレイト / ヒント / インシデント 統合版
# 二重記録原則 + pattern_id自動生成対応
# ==============================

# ★ここに抽出結果を入れる★
$great_items = @(
    "AIは私の思想のバックアップであり、未来への継承者である"
)

$hint_items = @(
    "AI切り替え時の儀式を標準化する"
)

$incident_items = @(
    "APIトークンを大量消費するシステムは作ってはいけない"
)

# ==============================
# 設定（変更不要）
# ==============================
$BASE_URL  = "http://localhost:5000"
$LOG_DIR   = "C:\Users\sirok\MoCKA\data\pattern_logs"
$DATE_STR  = Get-Date -Format "yyyyMMdd"
$LOG_FILE  = "$LOG_DIR\pattern_batch_$DATE_STR.json"
$counter   = @{great=0; hint=0; incident=0}
$log_items = @()

New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null

# ==============================
# 送信関数（変更不要）
# ==============================
function Send-Pattern($text, $type, $label, $endpoint, $category) {
    $counter[$category]++
    $id_prefix = switch ($category) { "great" {"GREAT"} "hint" {"HINT"} "incident" {"INC"} }
    $pattern_id = "$id_prefix-$(Get-Date -Format 'yyyyMMdd')-$("{0:D3}" -f $counter[$category])"
    $json = ConvertTo-Json @{
        text=$text; what_type=$type; source="past_chat_batch"
        label=$label; pattern_id=$pattern_id
        timestamp=(Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
    }
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
    try {
        $req = [System.Net.HttpWebRequest]::Create("http://localhost:5000/$endpoint")
        $req.Method = "POST"
        $req.ContentType = "application/json; charset=utf-8"
        $req.ContentLength = $bytes.Length
        $s = $req.GetRequestStream()
        $s.Write($bytes, 0, $bytes.Length)
        $s.Close()
        $req.GetResponse() | Out-Null
        Write-Host "✅ [$pattern_id] $($text.Substring(0,[Math]::Min(28,$text.Length)))..."
    } catch {
        Write-Host "❌ [$pattern_id] $($text.Substring(0,20))"
    }
    Start-Sleep -Milliseconds 200
}

# ==============================
# 送信実行
# ==============================
Write-Host "`n== グレイト！送信中 =="
foreach ($t in $great_items) {
    Send-Pattern $t "success_great" "グレイト！" "success" "great"
}

Write-Host "`n== ヒント！送信中 =="
foreach ($t in $hint_items) {
    Send-Pattern $t "success_hint" "ヒント！" "success" "hint"
}

Write-Host "`n== インシデント！送信中 =="
foreach ($t in $incident_items) {
    Send-Pattern $t "incident" "インシデント！" "collect" "incident"
}

# ==============================
# ローカルログ保存（二重記録原則）
# ==============================
$log_items | ConvertTo-Json | Out-File -FilePath $LOG_FILE -Encoding UTF8
Write-Host "`n== 完了 =="
Write-Host "グレイト:     $($counter.great)件"
Write-Host "ヒント:       $($counter.hint)件"
Write-Host "インシデント: $($counter.incident)件"
Write-Host "ローカルログ: $LOG_FILE"
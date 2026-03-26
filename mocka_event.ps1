function New-MockaEvent {
    param([string]$type = "AUTO", [string]$action = "HEARTBEAT")
    
    $LEDGER = "C:\Users\sirok\MoCKA\runtime\main\ledger.json"
    
    $ledger = Get-Content $LEDGER | ConvertFrom-Json
    $last = $ledger[-1]
    $prev_hash = $last.event_hash
    
    $event_id = [System.Guid]::NewGuid().ToString()
    $timestamp = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds() / 1000.0
    
    $raw = "$event_id$timestamp$type$action$prev_hash"
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($raw)
    $hash = ($sha256.ComputeHash($bytes) | ForEach-Object { $_.ToString("x2") }) -join ""
    
    $event = [ordered]@{
        event_id   = $event_id
        type       = $type
        action     = $action
        timestamp  = $timestamp
        prev_hash  = $prev_hash
        event_hash = $hash
    }
    
    $ledger += $event
    $json = $ledger | ConvertTo-Json -Depth 10
    [System.IO.File]::WriteAllText($LEDGER, $json)
    Write-Host "EVENT RECORDED: $event_id"
}

New-MockaEvent

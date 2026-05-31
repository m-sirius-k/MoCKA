# sync_to_vps.ps1
# PC (マスター) → Sakura VPS へ MoCKA データを同期する
# 前提: WSL2 or Git Bash に rsync / ssh が入っていること
#       または Windows の OpenSSH + scp を使用

# ── 設定 ──
$VPS_IP   = "YOUR_VPS_IP"      # 例: 153.120.xxx.xxx
$VPS_USER = "YOUR_SSH_USER"    # 例: ubuntu
$VPS_HOME = "/home/$VPS_USER/mocka"
$SSH_KEY  = "$env:USERPROFILE\.ssh\id_ed25519"  # SSH 鍵パス

$LOCAL_MOCKA = "C:\Users\sirok\MoCKA"

# 同期するファイル一覧
$FILES = @(
    @{ local = "$env:USERPROFILE\MOCKA_OVERVIEW.json"; remote = "$VPS_HOME/MOCKA_OVERVIEW.json" },
    @{ local = "$env:USERPROFILE\MOCKA_TODO.json";     remote = "$VPS_HOME/MOCKA_TODO.json" },
    @{ local = "$LOCAL_MOCKA\data\mocka_events.db";    remote = "$VPS_HOME/data/mocka_events.db" },
    @{ local = "$LOCAL_MOCKA\lever_essence.json";      remote = "$VPS_HOME/lever_essence.json" }
)

Write-Host "[sync] MoCKA PC → VPS 同期開始 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

foreach ($f in $FILES) {
    if (-not (Test-Path $f.local)) {
        Write-Warning "[skip] 存在しない: $($f.local)"
        continue
    }
    Write-Host "[copy] $($f.local) → ${VPS_USER}@${VPS_IP}:$($f.remote)"
    & scp -i $SSH_KEY -o StrictHostKeyChecking=accept-new `
        $f.local "${VPS_USER}@${VPS_IP}:$($f.remote)"
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "[warn] 転送失敗: $($f.local)"
    }
}

# VPS のサービスを再起動（DB 更新を反映）
Write-Host "[restart] mocka-mcp サービス再起動..."
& ssh -i $SSH_KEY "${VPS_USER}@${VPS_IP}" "sudo systemctl restart mocka-mcp"

Write-Host "[done] 同期完了 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

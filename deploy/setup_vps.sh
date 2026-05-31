#!/bin/bash
# MoCKA MCP Server -- VPS セットアップスクリプト
# Ubuntu 22.04 / 一般ユーザー+sudo 向け
# 使い方: chmod +x setup_vps.sh && ./setup_vps.sh

set -euo pipefail

MOCKA_HOME="$HOME/mocka"
VENV="$MOCKA_HOME/.venv"
SERVICE_NAME="mocka-mcp"

echo "=== [1/7] システムパッケージ更新 ==="
sudo apt-get update -q
sudo apt-get install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx

echo "=== [2/7] mocka ディレクトリ作成 ==="
mkdir -p "$MOCKA_HOME/data"
mkdir -p "$MOCKA_HOME/logs"

echo "=== [3/7] Python 仮想環境 + 依存パッケージ ==="
python3 -m venv "$VENV"
"$VENV/bin/pip" install --upgrade pip -q
"$VENV/bin/pip" install flask flask-cors gunicorn -q

echo "=== [4/7] MCP サーバースクリプトをコピー ==="
# このスクリプトと同じディレクトリに mocka_mcp_server_vps.py がある前提
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cp "$SCRIPT_DIR/mocka_mcp_server_vps.py" "$MOCKA_HOME/"

echo "=== [5/7] systemd サービス設定 ==="
# YOUR_SSH_USER を実際のユーザー名に置き換えてコピー
sed "s/YOUR_SSH_USER/$USER/g" "$SCRIPT_DIR/mocka-mcp.service" \
    | sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

echo "=== [6/7] nginx 設定 ==="
sudo cp "$SCRIPT_DIR/nginx-mocka.conf" /etc/nginx/sites-available/mocka
sudo ln -sf /etc/nginx/sites-available/mocka /etc/nginx/sites-enabled/mocka
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

echo "=== [7/7] SSL 証明書 (Let's Encrypt) ==="
echo "次のコマンドを手動実行してください:"
echo "  sudo certbot --nginx -d mocka.nsjp.org --non-interactive --agree-tos -m nsjpkimura@gmail.com"

echo ""
echo "=== セットアップ完了 ==="
echo "サービス状態: sudo systemctl status $SERVICE_NAME"
echo "ログ確認:     journalctl -u $SERVICE_NAME -f"
echo "ヘルスチェック: curl http://localhost:5002/health"

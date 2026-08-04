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

echo "=== [4/7] MCP サーバースクリプト + PHI-OS Event Gate をコピー ==="
# このスクリプトと同じディレクトリに mocka_mcp_server_vps.py がある前提
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cp "$SCRIPT_DIR/mocka_mcp_server_vps.py" "$MOCKA_HOME/"

# v1.6.0: mocka_write_event は phi_os.event_gate.process_event() を唯一の
# events保存経路として使用する。Gateモジュール一式が MOCKA_HOME 直下に
# 存在しないと書き込みが無効化されるため、必ず配置する。
mkdir -p "$MOCKA_HOME/phi_os" "$MOCKA_HOME/interface"
for f in __init__.py event_gate.py gate_validator.py gate_schema.py integrity.py; do
    cp "$REPO_ROOT/phi_os/$f" "$MOCKA_HOME/phi_os/"
done
for f in gate_policy.py schema_audit.py; do
    cp "$REPO_ROOT/interface/$f" "$MOCKA_HOME/interface/"
done

# Gateがimport可能かをこの場で検証する（起動してから気づく事態を避ける）
MOCKA_HOME="$MOCKA_HOME" "$VENV/bin/python" -c "
import sys
sys.path.insert(0, '$MOCKA_HOME')
from phi_os.event_gate import process_event, DB_PATH
print('  Event Gate import: OK')
print('  Gate DB_PATH:', DB_PATH)
"

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

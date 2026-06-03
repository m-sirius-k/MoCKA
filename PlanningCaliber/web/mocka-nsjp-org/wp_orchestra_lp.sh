#!/bin/bash
# Orchestra LP 投稿スクリプト
# 実行前提: wp_setup.sh が完了済みであること
# 実行方法: bash wp_orchestra_lp.sh

WP="wp --path=/home/nsjp/www/mocka"

echo "========================================="
echo " Orchestra LP 投稿"
echo "========================================="

# Orchestra ページのIDを取得
PAGE_ORCH=$($WP post list \
  --post_type=page \
  --name=orchestra \
  --fields=ID \
  --format=csv | tail -1)

if [ -z "$PAGE_ORCH" ] || [ "$PAGE_ORCH" = "ID" ]; then
  echo "ERROR: Orchestra ページが見つかりません"
  echo "wp_setup.sh を先に実行してください"
  exit 1
fi

echo "Orchestra page ID: $PAGE_ORCH"

# HTMLファイルのパス（サーバーにアップロードした場所を指定）
HTML_FILE="/home/nsjp/tmp/orchestra_lp_content.html"

if [ ! -f "$HTML_FILE" ]; then
  echo "ERROR: HTMLファイルが見つかりません: $HTML_FILE"
  echo "SFTPで /home/nsjp/tmp/ にアップロードしてから再実行してください"
  exit 1
fi

# HTMLを読み込んでページを更新
HTML_CONTENT=$(cat "$HTML_FILE")

$WP post update $PAGE_ORCH \
  --post_content="$HTML_CONTENT" \
  --post_status=publish

echo ""
echo "=== 投稿結果確認 ==="
$WP post get $PAGE_ORCH --fields=ID,post_title,post_name,post_status,post_parent

echo ""
echo "確認URL: https://mocka.nsjp.org/mini-mocka/orchestra"
echo "========================================="
echo " Orchestra LP 投稿完了"
echo "========================================="

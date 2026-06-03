#!/bin/bash
# Sirius Lab — WordPress 一括セットアップスクリプト
# 実行場所: さくらサーバー SSH
# 実行方法: bash wp_setup.sh

WP="wp --path=/home/nsjp/www/mocka"

echo "========================================="
echo " Sirius Lab WP Setup Start"
echo "========================================="

# -----------------------------------------
# STEP 1: 基本設定
# -----------------------------------------
echo "[1/8] 基本設定..."
$WP option update blogname "Sirius Lab"
$WP option update blogdescription "AI Governance Architecture by MoCKA"
$WP option update permalink_structure "/%postname%/"
$WP rewrite flush

# -----------------------------------------
# STEP 2: カテゴリ作成
# -----------------------------------------
echo "[2/8] カテゴリ作成..."
$WP term create category "MoCKA"     --slug=mocka
$WP term create category "vasAI"     --slug=vasai
$WP term create category "mini MoCKA" --slug=mini-mocka
$WP term create category "Research"  --slug=research

# -----------------------------------------
# STEP 3: タグ作成
# -----------------------------------------
echo "[3/8] タグ作成..."
$WP term create post_tag "orchestra"       --slug=orchestra
$WP term create post_tag "relay"           --slug=relay
$WP term create post_tag "phi-os"          --slug=phi-os
$WP term create post_tag "memory"          --slug=memory
$WP term create post_tag "governance"      --slug=governance
$WP term create post_tag "ai"              --slug=ai
$WP term create post_tag "chrome-extension" --slug=chrome-extension
$WP term create post_tag "verification"    --slug=verification

# -----------------------------------------
# STEP 4: 固定ページ作成（親→子の順）
# -----------------------------------------
echo "[4/8] 固定ページ作成..."

# トップページ
PAGE_TOP=$($WP post create \
  --post_type=page \
  --post_title="Sirius Lab" \
  --post_name="sirius-lab" \
  --post_status=publish \
  --post_content="Sirius Lab は、AIガバナンスの構造化を研究する独立研究機関です。" \
  --porcelain)
echo "  TOP page ID: $PAGE_TOP"

# MoCKA
PAGE_MOCKA=$($WP post create \
  --post_type=page \
  --post_title="MoCKA" \
  --post_name="mocka-about" \
  --post_status=publish \
  --post_content="" \
  --porcelain)
echo "  MoCKA page ID: $PAGE_MOCKA"

# vasAI（親）
PAGE_VASAI=$($WP post create \
  --post_type=page \
  --post_title="vasAI" \
  --post_name="vasai" \
  --post_status=publish \
  --post_content="" \
  --porcelain)
echo "  vasAI page ID: $PAGE_VASAI"

# vasAI 子: Use Cases
PAGE_USECASES=$($WP post create \
  --post_type=page \
  --post_title="Use Cases" \
  --post_name="use-cases" \
  --post_status=publish \
  --post_content="" \
  --post_parent=$PAGE_VASAI \
  --porcelain)
echo "  Use Cases page ID: $PAGE_USECASES"

# vasAI 子: Docs
PAGE_DOCS=$($WP post create \
  --post_type=page \
  --post_title="Docs" \
  --post_name="docs" \
  --post_status=publish \
  --post_content="" \
  --post_parent=$PAGE_VASAI \
  --porcelain)
echo "  Docs page ID: $PAGE_DOCS"

# mini MoCKA（親）
PAGE_MINI=$($WP post create \
  --post_type=page \
  --post_title="mini MoCKA" \
  --post_name="mini-mocka" \
  --post_status=publish \
  --post_content="" \
  --porcelain)
echo "  mini MoCKA page ID: $PAGE_MINI"

# mini MoCKA 子: Orchestra
PAGE_ORCH=$($WP post create \
  --post_type=page \
  --post_title="Orchestra" \
  --post_name="orchestra" \
  --post_status=publish \
  --post_content="" \
  --post_parent=$PAGE_MINI \
  --porcelain)
echo "  Orchestra page ID: $PAGE_ORCH"

# mini MoCKA 子: Relay
PAGE_RELAY=$($WP post create \
  --post_type=page \
  --post_title="Relay" \
  --post_name="relay" \
  --post_status=publish \
  --post_content="" \
  --post_parent=$PAGE_MINI \
  --porcelain)
echo "  Relay page ID: $PAGE_RELAY"

# mini MoCKA 子: PHI-OS
PAGE_PHIOS=$($WP post create \
  --post_type=page \
  --post_title="PHI-OS" \
  --post_name="phi-os" \
  --post_status=publish \
  --post_content="" \
  --post_parent=$PAGE_MINI \
  --porcelain)
echo "  PHI-OS page ID: $PAGE_PHIOS"

# mini MoCKA 子: Memory
PAGE_MEM=$($WP post create \
  --post_type=page \
  --post_title="Memory" \
  --post_name="memory" \
  --post_status=publish \
  --post_content="" \
  --post_parent=$PAGE_MINI \
  --porcelain)
echo "  Memory page ID: $PAGE_MEM"

# Research
PAGE_RES=$($WP post create \
  --post_type=page \
  --post_title="Research" \
  --post_name="research" \
  --post_status=publish \
  --post_content="" \
  --porcelain)
echo "  Research page ID: $PAGE_RES"

# Verification
PAGE_VER=$($WP post create \
  --post_type=page \
  --post_title="Verification" \
  --post_name="verification" \
  --post_status=publish \
  --post_content="" \
  --porcelain)
echo "  Verification page ID: $PAGE_VER"

# -----------------------------------------
# STEP 5: トップページ設定
# -----------------------------------------
echo "[5/8] トップページ設定..."
$WP option update show_on_front page
$WP option update page_on_front $PAGE_TOP

# -----------------------------------------
# STEP 6: メニュー作成
# -----------------------------------------
echo "[6/8] メニュー作成..."
MENU_ID=$($WP menu create "メインメニュー" --porcelain)
echo "  Menu ID: $MENU_ID"

# Home
$WP menu item add-post $MENU_ID $PAGE_TOP --title="Home" --status=publish

# MoCKA
$WP menu item add-post $MENU_ID $PAGE_MOCKA --title="MoCKA" --status=publish

# vasAI
$WP menu item add-post $MENU_ID $PAGE_VASAI --title="vasAI" --status=publish

# mini MoCKA（親）
ITEM_MINI=$($WP menu item add-post $MENU_ID $PAGE_MINI --title="mini MoCKA" --status=publish --porcelain)
echo "  mini MoCKA menu item ID: $ITEM_MINI"

# mini MoCKA 子メニュー
$WP menu item add-post $MENU_ID $PAGE_ORCH  --title="Orchestra" --parent-id=$ITEM_MINI --status=publish
$WP menu item add-post $MENU_ID $PAGE_RELAY --title="Relay"     --parent-id=$ITEM_MINI --status=publish
$WP menu item add-post $MENU_ID $PAGE_PHIOS --title="PHI-OS"    --parent-id=$ITEM_MINI --status=publish
$WP menu item add-post $MENU_ID $PAGE_MEM   --title="Memory"    --parent-id=$ITEM_MINI --status=publish

# Research
$WP menu item add-post $MENU_ID $PAGE_RES --title="Research" --status=publish

# Verification
$WP menu item add-post $MENU_ID $PAGE_VER --title="Verification" --status=publish

# -----------------------------------------
# STEP 7: メニューをヘッダーに割り当て
# -----------------------------------------
echo "[7/8] メニュー位置の割り当て..."
# テーマのメニュー位置を確認してから割り当て
echo "  利用可能なメニュー位置:"
$WP menu location list

# 一般的な位置名で試みる（テーマによって異なる）
$WP menu location assign $MENU_ID primary   2>/dev/null && echo "  -> primary に割り当て完了" || \
$WP menu location assign $MENU_ID header    2>/dev/null && echo "  -> header に割り当て完了" || \
$WP menu location assign $MENU_ID main-menu 2>/dev/null && echo "  -> main-menu に割り当て完了" || \
echo "  !! メニュー位置を手動で確認してください（管理画面 → 外観 → メニュー）"

# -----------------------------------------
# STEP 8: 確認出力
# -----------------------------------------
echo "[8/8] 確認..."
echo ""
echo "=== 作成された固定ページ ==="
$WP post list --post_type=page --fields=ID,post_title,post_name,post_parent --format=table

echo ""
echo "=== メニュー構成 ==="
$WP menu item list $MENU_ID --fields=db_id,menu_item_parent,type,title,url --format=table

echo ""
echo "========================================="
echo " セットアップ完了"
echo " Orchestra LP を投稿するには:"
echo "   次のスクリプト wp_orchestra_lp.sh を実行してください"
echo "========================================="

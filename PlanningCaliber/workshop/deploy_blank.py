import paramiko

host = "www1003.sakura.ne.jp"
user = "nsjp"
password = "nsjpnsjp2525"
wp_path = "/home/nsjp/www/mocka"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=user, password=password)

def run(cmd):
    _, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print("OUT:", out)
    if err: print("ERR:", err)
    return out

# テーマ名取得
theme = run(f"wp --path={wp_path} eval 'echo get_template();' --allow-root")
print(f"Theme: {theme}")

theme_dir = f"/home/nsjp/www/mocka/wp-content/themes/{theme}"

# page-blank.php 作成
blank_template = '''<?php /* Template Name: Blank */ ?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head><meta charset="<?php bloginfo('charset'); ?>">
<?php wp_head(); ?>
</head>
<body>
<?php while(have_posts()):the_post();the_content();endwhile; ?>
<?php wp_footer(); ?>
</body>
</html>'''

sftp = client.open_sftp()
with sftp.open(f"{theme_dir}/page-blank.php", "w") as f:
    f.write(blank_template)
print(f"Created: {theme_dir}/page-blank.php")

# ページ61にBlankテンプレートを適用
result = run(f"wp --path={wp_path} post meta update 61 _wp_page_template page-blank.php --allow-root")
print("Template set:", result)

# 確認
result = run(f"wp --path={wp_path} post meta get 61 _wp_page_template --allow-root")
print("Current template:", result)

client.close()
print("\n完了: https://mocka.nsjp.org/?page_id=61")

import re, os

files = [
    r'F:\2023バックアップ\とにかくﾌｫﾙﾀﾞ-\ｻｰﾊﾞｰ保管庫立ち入り禁止\金庫室\一般ﾊﾞｯｸｱｯﾌﾟ\net資料\無機系廃液の処理.htm',
    r'F:\2023バックアップ\とにかくﾌｫﾙﾀﾞ-\ｻｰﾊﾞｰ保管庫立ち入り禁止\金庫室\一般ﾊﾞｯｸｱｯﾌﾟ\net資料\硝酸除去.htm',
    r'F:\2023バックアップ\とにかくﾌｫﾙﾀﾞ-\ｻｰﾊﾞｰ保管庫立ち入り禁止\金庫室\一般ﾊﾞｯｸｱｯﾌﾟ\net資料\脱窒1.htm',
    r'F:\2023バックアップ\とにかくﾌｫﾙﾀﾞ-\ｻｰﾊﾞｰ保管庫立ち入り禁止\金庫室\一般ﾊﾞｯｸｱｯﾌﾟ\net資料\ステップ脱窒.htm',
    r'F:\2023バックアップ\とにかくﾌｫﾙﾀﾞ-\ｻｰﾊﾞｰ保管庫立ち入り禁止\金庫室\一般ﾊﾞｯｸｱｯﾌﾟ\net資料\脱窒脱リン.htm',
    r'F:\2023バックアップ\とにかくﾌｫﾙﾀﾞ-\ｻｰﾊﾞｰ保管庫立ち入り禁止\金庫室\一般ﾊﾞｯｸｱｯﾌﾟ\net資料\硝化　脱硝.htm',
    r'F:\2023バックアップ\とにかくﾌｫﾙﾀﾞ-\ｻｰﾊﾞｰ保管庫立ち入り禁止\金庫室\一般ﾊﾞｯｸｱｯﾌﾟ\net資料\嫌気－好気活性汚泥法.htm',
    r'F:\2023バックアップ\とにかくﾌｫﾙﾀﾞ-\ｻｰﾊﾞｰ保管庫立ち入り禁止\金庫室\一般ﾊﾞｯｸｱｯﾌﾟ\net資料\フッ素除去.htm',
    r'F:\2023バックアップ\とにかくﾌｫﾙﾀﾞ-\ｻｰﾊﾞｰ保管庫立ち入り禁止\金庫室\一般ﾊﾞｯｸｱｯﾌﾟ\net資料\フッ素含有廃水処理汚泥の削減.htm',
]

combined = ""
for path in files:
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            html = f.read()
        text = re.sub(r'<[^>]+>', '', html)
        text = re.sub(r'\s+', ' ', text).strip()
        combined += text + "\n"
        print("OK: " + os.path.basename(path) + " " + str(len(text)) + " chars")
    except Exception as e:
        print("ERR: " + os.path.basename(path) + " " + str(e))

with open(r'C:\Users\sirok\MoCKA\experiments\net_docs_combined.txt', 'w', encoding='utf-8') as f:
    f.write(combined)
print("Total: " + str(len(combined)) + " chars")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
draw.io ファイルを SVG にエクスポート
"""

import os
import json
import base64
import urllib.request
from pathlib import Path

def convert_drawio_to_svg(drawio_file, output_file):
    """draw.io ファイルを SVG に変換"""
    
    if not os.path.exists(drawio_file):
        print(f"✗ ファイルが見つかりません: {drawio_file}")
        return False
    
    try:
        # draw.io のオンライン API を使用
        with open(drawio_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        # Base64 エンコード
        encoded = base64.b64encode(xml_content.encode()).decode()
        
        # draw.io API URL
        url = f"https://draw.io/api/export/png?xml={encoded}&format=svg"
        
        print(f"  変換中: {drawio_file} → {output_file}")
        
        # ダウンロード
        urllib.request.urlretrieve(url, output_file)
        print(f"  ✓ 完了")
        return True
        
    except Exception as e:
        print(f"  ✗ エラー: {str(e)}")
        return False

def main():
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    drawio_files = list(Path('.').glob('*.drawio'))
    
    if not drawio_files:
        print("✗ .drawio ファイルが見つかりません")
        return
    
    print(f"📊 {len(drawio_files)} 個のファイルをエクスポート中...\n")
    
    success_count = 0
    for drawio_file in drawio_files:
        output_file = drawio_file.with_suffix('.svg')
        if convert_drawio_to_svg(str(drawio_file), str(output_file)):
            success_count += 1
    
    print(f"\n✓ エクスポート完了: {success_count}/{len(drawio_files)}")

if __name__ == '__main__':
    main()

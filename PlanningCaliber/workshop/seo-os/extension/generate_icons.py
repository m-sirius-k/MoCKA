# extension/generate_icons.py
# python generate_icons.py で実行

from PIL import Image, ImageDraw, ImageFont
import os

def make_icon(size):
    img  = Image.new("RGBA", (size, size),
                     (10, 10, 26, 255))
    draw = ImageDraw.Draw(img)
    # 背景円
    margin = size // 8
    draw.ellipse(
        [margin, margin, size-margin, size-margin],
        fill=(201, 168, 76, 255))
    # 中央テキスト
    text     = "S"
    fontsize = size // 2
    try:
        font = ImageFont.truetype("arial.ttf", fontsize)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0,0), text, font=font)
    tw   = bbox[2] - bbox[0]
    th   = bbox[3] - bbox[1]
    draw.text(
        ((size-tw)//2, (size-th)//2 - size//10),
        text, fill=(10,10,26,255), font=font)
    return img

os.makedirs("icons", exist_ok=True)
for s in [16, 48, 128]:
    make_icon(s).save(f"icons/icon{s}.png")
    print(f"icon{s}.png 生成完了")

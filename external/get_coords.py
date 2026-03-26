import pyautogui
import time

print("--- MoCKA 座標特定モード ---")
print("5秒後に現在のマウス位置の座標を表示します。")
print("対象（回答エリアの左上と右下）にカーソルを合わせてください。")

try:
    while True:
        time.sleep(5)
        x, y = pyautogui.position()
        print(f"現在の座標: X={x}, Y={y}  (Ctrl+C で終了)")
except KeyboardInterrupt:
    print("\n特定終了。")

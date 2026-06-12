# conftest.py
"""phi-os は通常パッケージではないため、sys.pathに自身を追加する。
これにより `from ise...` `from verification...` `from adapter...` 等の
absolute importがテスト時にも app.py と同じ形で解決される。
"""
import sys
from pathlib import Path

_PHI_OS_DIR = Path(__file__).resolve().parent
if str(_PHI_OS_DIR) not in sys.path:
    sys.path.insert(0, str(_PHI_OS_DIR))

"""
prediction/gate.py -- TIC Prediction Gate (Phase6)

REQUIRED_TRACE_COUNT 未満のコンポーネントは予測計算しない。
"""

import sys
import io

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REQUIRED_TRACE_COUNT = 30


def check(trace_count: int) -> bool:
    """trace_count が予測に十分かどうかを返す"""
    return trace_count >= REQUIRED_TRACE_COUNT


def run():
    import provider

    components = provider.get_components()
    if not components:
        print("[gate] risk_history.jsonl が空。終了。")
        return

    for comp in components:
        series = provider.get_score_series_for(comp, window=REQUIRED_TRACE_COUNT)
        trace_count = len(series)
        if check(trace_count):
            print(f"  {comp:<20} : PASS ({trace_count} / {REQUIRED_TRACE_COUNT})")
        else:
            print(
                f"  {comp:<20} : Waiting for sufficient history "
                f"({trace_count:>2} / {REQUIRED_TRACE_COUNT})"
            )


if __name__ == "__main__":
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
    run()

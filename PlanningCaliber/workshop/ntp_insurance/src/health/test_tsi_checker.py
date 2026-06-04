"""test_tsi_checker.py — TSI Health Checker テスト"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.health.tsi_checker import calc_tsi, calc_status


def test_trusted():
    """tsi=1.0、0日経過 -> TRUSTED"""
    assert calc_status(1.0, days=0) == "TRUSTED", "0日経過はTRUSTED"


def test_warning_14days():
    """tsi=1.0、14日経過 -> 劣化後0.8 -> TRUSTED境界"""
    result = calc_tsi(1.0, days=14)
    assert result == 0.8, f"14日経過: expected 0.8, got {result}"
    assert calc_status(1.0, days=14) == "TRUSTED", "0.8はTRUSTED"


def test_warning_28days():
    """tsi=1.0、28日経過 -> 劣化後0.6 -> WARNING"""
    result = calc_tsi(1.0, days=28)
    assert result == 0.6, f"28日経過: expected 0.6, got {result}"
    assert calc_status(1.0, days=28) == "WARNING", "0.6はWARNING"


def test_danger_42days():
    """tsi=1.0、42日経過 -> 劣化後0.0 -> DEAD"""
    result = calc_tsi(1.0, days=42)
    assert result == 0.0, f"42日経過: expected 0.0, got {result}"
    assert calc_status(1.0, days=42) == "DEAD", "42日はDEAD"


def test_dead():
    """tsi=1.0、50日経過 -> DEAD"""
    assert calc_status(1.0, days=50) == "DEAD", "50日経過はDEAD"


def test_already_low():
    """tsi=0.3、0日経過 -> DANGER"""
    assert calc_status(0.3, days=0) == "DANGER", "0.3はDANGER"


def test_warning_status():
    """tsi=0.6、0日経過 -> WARNING"""
    assert calc_status(0.6, days=0) == "WARNING", "0.6はWARNING"


def test_dead_tsi_zero():
    """tsi=0.0 -> DEAD"""
    assert calc_status(0.0, days=0) == "DEAD", "0.0はDEAD"


def test_no_negative():
    """劣化後は0.0以下にならない"""
    result = calc_tsi(0.1, days=30)
    assert result >= 0.0, "TSIは0.0以上"


def test_boundary_13days():
    """13日経過は劣化なし"""
    result = calc_tsi(1.0, days=13)
    assert result == 1.0, f"13日経過: expected 1.0, got {result}"


if __name__ == "__main__":
    tests = [
        test_trusted, test_warning_14days, test_warning_28days,
        test_danger_42days, test_dead, test_already_low,
        test_warning_status, test_dead_tsi_zero, test_no_negative,
        test_boundary_13days,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print("PASS " + t.__name__)
            passed += 1
        except AssertionError as e:
            print("FAIL " + t.__name__ + " -- " + str(e))
            failed += 1
    print(f"\n{passed}/{passed+failed} passed")
    if failed:
        sys.exit(1)

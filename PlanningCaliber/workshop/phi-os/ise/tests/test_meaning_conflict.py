# test_meaning_conflict.py
"""STEP 4: MeaningConflictResolver 検証"""
from phios.meaning.state_vector import MeaningStateVector
from phios.meaning.conflict import resolve_conflict, detect_conflict


def test_conflict_high_impact_priority():
    a = MeaningStateVector(0.2, 0.9, 0.3, 0.5, 0.1)
    b = MeaningStateVector(0.2, 0.3, 0.3, 0.5, 0.1)
    result = resolve_conflict(a, b)
    assert result is a


def test_conflict_stability_priority():
    a = MeaningStateVector(0.2, 0.3, 0.3, 0.9, 0.1)
    b = MeaningStateVector(0.2, 0.3, 0.3, 0.2, 0.1)
    result = resolve_conflict(a, b)
    assert result is a


def test_conflict_default_interaction():
    a = MeaningStateVector(0.2, 0.3, 0.3, 0.5, 0.1)
    b = MeaningStateVector(0.3, 0.4, 0.4, 0.6, 0.2)
    result = resolve_conflict(a, b)
    assert result is not a
    assert result is not b
    assert isinstance(result, MeaningStateVector)


def test_detect_conflict_true():
    a = MeaningStateVector(0.1, 0.1, 0.1, 0.5, 0.1)
    b = MeaningStateVector(0.9, 0.1, 0.1, 0.5, 0.1)
    assert detect_conflict(a, b) is True


def test_detect_conflict_false():
    a = MeaningStateVector(0.3, 0.3, 0.3, 0.5, 0.1)
    b = MeaningStateVector(0.35, 0.32, 0.31, 0.55, 0.12)
    assert detect_conflict(a, b) is False

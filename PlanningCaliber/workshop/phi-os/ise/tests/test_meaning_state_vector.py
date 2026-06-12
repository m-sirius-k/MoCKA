# test_meaning_state_vector.py
"""STEP 1: MeaningStateVector 検証"""
from phios.meaning.state_vector import MeaningStateVector


def test_vector_normalization():
    v = MeaningStateVector(0.2, 0.3, 0.5, 0.5, 0.1)
    v.normalize()
    assert abs((v.intent_weight + v.impact_weight + v.urgency_weight) - 1.0) < 1e-9


def test_normalization_zero_total_safe():
    v = MeaningStateVector(0.0, 0.0, 0.0, 0.5, 0.1)
    v.normalize()
    assert v.intent_weight == 0.0
    assert v.impact_weight == 0.0
    assert v.urgency_weight == 0.0


def test_entropy_range():
    v = MeaningStateVector(0.2, 0.3, 0.5, 0.5, 0.4)
    assert 0.0 <= v.entropy <= 1.0


def test_stability_bounds():
    v = MeaningStateVector(0.2, 0.3, 0.5, 0.8, 0.1)
    assert 0.0 <= v.stability <= 1.0


def test_is_stable_true():
    v = MeaningStateVector(0.2, 0.3, 0.5, 0.8, 0.1)
    assert v.is_stable(0.7) is True


def test_is_stable_false():
    v = MeaningStateVector(0.2, 0.3, 0.5, 0.5, 0.1)
    assert v.is_stable(0.7) is False


def test_is_critical_true():
    v = MeaningStateVector(0.2, 0.9, 0.5, 0.5, 0.1)
    assert v.is_critical(0.8) is True

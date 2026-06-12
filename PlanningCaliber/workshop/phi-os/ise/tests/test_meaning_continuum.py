# test_meaning_continuum.py
"""STEP 3: MeaningContinuum 検証"""
from phios.meaning.state_vector import MeaningStateVector
from phios.meaning.continuum import MeaningContinuum


def test_continuum_evolution():
    c = MeaningContinuum()
    c.push(MeaningStateVector(0.3, 0.3, 0.4, 0.6, 0.1))
    c.push(MeaningStateVector(0.4, 0.5, 0.6, 0.8, 0.2))
    result = c.evolve()
    assert isinstance(result, MeaningStateVector)


def test_buffer_limit():
    c = MeaningContinuum(size=10)
    for i in range(15):
        c.push(MeaningStateVector(0.1, 0.1, 0.1, 0.5, i / 100))
    assert len(c.buffer) == 10
    assert c.current().entropy == 14 / 100


def test_continuum_single_vector():
    c = MeaningContinuum()
    v = MeaningStateVector(0.3, 0.3, 0.4, 0.6, 0.1)
    c.push(v)
    assert c.evolve() is v


def test_continuum_empty_returns_none():
    c = MeaningContinuum()
    assert c.evolve() is None
    assert c.current() is None


def test_entropy_trend_positive():
    c = MeaningContinuum()
    c.push(MeaningStateVector(0.3, 0.3, 0.4, 0.6, 0.1))
    c.push(MeaningStateVector(0.3, 0.3, 0.4, 0.6, 0.5))
    assert c.entropy_trend() > 0


def test_entropy_trend_negative():
    c = MeaningContinuum()
    c.push(MeaningStateVector(0.3, 0.3, 0.4, 0.6, 0.5))
    c.push(MeaningStateVector(0.3, 0.3, 0.4, 0.6, 0.1))
    assert c.entropy_trend() < 0

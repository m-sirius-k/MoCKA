# test_meaning_interaction.py
"""STEP 2: MeaningInteractionLayer 検証"""
from phios.meaning.state_vector import MeaningStateVector
from phios.meaning.interaction import interact


def test_interaction_merges_vectors():
    a = MeaningStateVector(0.2, 0.3, 0.4, 0.6, 0.1)
    b = MeaningStateVector(0.4, 0.5, 0.6, 0.8, 0.2)
    result = interact(a, b)
    assert isinstance(result, MeaningStateVector)


def test_interaction_preserves_max_impact():
    a = MeaningStateVector(0.2, 0.3, 0.4, 0.6, 0.1)
    b = MeaningStateVector(0.4, 0.9, 0.6, 0.8, 0.2)
    result = interact(a, b)
    # impact_weightは正規化前にmax(0.3,0.9)=0.9が使われる
    assert result.impact_weight >= result.intent_weight


def test_interaction_preserves_max_urgency():
    a = MeaningStateVector(0.3, 0.3, 0.2, 0.6, 0.1)
    b = MeaningStateVector(0.3, 0.3, 0.9, 0.8, 0.2)
    result = interact(a, b)
    assert result.urgency_weight >= result.intent_weight


def test_interaction_entropy_is_difference():
    a = MeaningStateVector(0.3, 0.3, 0.4, 0.6, 0.1)
    b = MeaningStateVector(0.3, 0.3, 0.4, 0.6, 0.4)
    result = interact(a, b)
    assert abs(result.entropy - 0.3) < 1e-9


def test_interaction_result_normalized():
    a = MeaningStateVector(0.2, 0.3, 0.4, 0.6, 0.1)
    b = MeaningStateVector(0.4, 0.5, 0.6, 0.8, 0.2)
    result = interact(a, b)
    total = result.intent_weight + result.impact_weight + result.urgency_weight
    assert abs(total - 1.0) < 1e-9

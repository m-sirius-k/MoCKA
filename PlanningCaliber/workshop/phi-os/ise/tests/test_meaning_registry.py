# test_meaning_registry.py
"""STEP 0: Meaning Registry / Decision Rules 検証"""
from phios.registry import meaning
from phios.registry.decision_rules import DECISION_RULES, DecisionRule, match_rule


def test_meaning_registry_get_intent_seal():
    assert meaning.get_intent("SEAL", "audit") == "validate"


def test_meaning_registry_get_intent_violation():
    assert meaning.get_intent("VIOLATION", "incident") == "recover"


def test_meaning_registry_category_fallback():
    assert meaning.get_intent("UNKNOWN_EVENT", "lifecycle") == "observe"


def test_meaning_registry_get_impact_critical():
    assert meaning.get_impact("ANYTHING", "critical") == "critical"


def test_meaning_registry_get_impact_system_event():
    assert meaning.get_impact("STATE_CHANGE", "info") == "system"


def test_meaning_registry_get_urgency_mapping():
    assert meaning.get_urgency("info") == 1
    assert meaning.get_urgency("warning") == 2
    assert meaning.get_urgency("critical") == 3


def test_decision_rules_critical_matches_first():
    rule = match_rule("critical", "observe")
    assert rule.action_type == "escalate"
    assert rule.target == "human_gate"


def test_decision_rules_match_recover():
    rule = match_rule("local", "recover")
    assert rule.action_type == "delegate"
    assert rule.target == "mock"


def test_decision_rules_fallback_noop():
    rule = match_rule("local", "transition")
    assert rule.action_type == "noop"
    assert rule.target == "ledger"


def test_decision_rules_immutable():
    rule = DECISION_RULES[0]
    assert isinstance(rule, DecisionRule)
    try:
        rule.action_type = "changed"
        assert False, "DecisionRule should be frozen"
    except AttributeError:
        pass

"""Minimal tests for MoCKA 3.0 Phase1 GLK Generator."""
import pytest

from mocka3.glk_generator import ConstraintViolation, generate_blueprint
from mocka3.meta_intent_schema import MetaIntent


def make_intent(**overrides) -> MetaIntent:
    base = dict(
        meta_intent_id="MI_20260615_001",
        target_layer_range=[0, 1, 2, 3],
        structural_goal="add new drift classification category",
        constraint_policy=["P1_no_unbounded_self_change"],
        evolution_pressure="drift_observation",
        stability_threshold=0.05,
        generation_priority=1,
    )
    base.update(overrides)
    return MetaIntent(**base)


def test_generate_blueprint_success():
    intent = make_intent()
    blueprint = generate_blueprint(intent, blueprint_id="BP_20260615_001")

    assert blueprint.source_meta_intent_id == intent.meta_intent_id
    assert blueprint.validation_status == "passed"
    assert set(blueprint.layer_definitions.keys()) == {"layer0", "layer1", "layer2", "layer3", "layer4"}

    for layer_id in range(4):
        assert blueprint.layer_definitions[f"layer{layer_id}"]["status"] == "regenerated"
    assert blueprint.layer_definitions["layer4"]["status"] == "unchanged"

    gov = blueprint.governance_loop_definition
    assert gov["stability_threshold"] == 0.05
    assert gov["drift_layer_ref"] == "layer2"
    assert gov["decision_layer_ref"] == "layer3"


def test_layer4_self_redefinition_forbidden():
    intent = make_intent(target_layer_range=[3, 4])
    with pytest.raises(ConstraintViolation):
        generate_blueprint(intent, blueprint_id="BP_20260615_002")


def test_requires_constraint_policy():
    intent = make_intent(constraint_policy=[])
    with pytest.raises(ConstraintViolation):
        generate_blueprint(intent, blueprint_id="BP_20260615_003")


def test_requires_positive_stability_threshold():
    intent = make_intent(stability_threshold=0)
    with pytest.raises(ConstraintViolation):
        generate_blueprint(intent, blueprint_id="BP_20260615_004")


def test_unaffected_layers_marked_unchanged():
    intent = make_intent(target_layer_range=[2])
    blueprint = generate_blueprint(intent, blueprint_id="BP_20260615_005")

    assert blueprint.layer_definitions["layer0"]["status"] == "unchanged"
    assert blueprint.layer_definitions["layer1"]["status"] == "unchanged"
    assert blueprint.layer_definitions["layer2"]["status"] == "regenerated"
    assert blueprint.layer_definitions["layer3"]["status"] == "unchanged"

"""MoCKA 3.0 - GLK Generator (MGL_SPEC_v1.md Phase1 minimal core).

MetaIntent -> SystemBlueprint -> GLK structure (Layer0-4 definitions).

Constraints enforced (MGL_SPEC_v1.md SS5.2):
- P2: every generation run must pass through Layer1 constraint checks.
- Layer4 (MGL) must not target itself (no recursive self-redefinition in Phase1).
"""
from __future__ import annotations

from mocka3.meta_intent_schema import MetaIntent
from mocka3.system_blueprint_schema import SystemBlueprint


class ConstraintViolation(Exception):
    pass


def check_layer1_constraints(meta_intent: MetaIntent) -> None:
    """Layer1 (Constraint Reality Layer) gate. Must run before any generation."""
    if 4 in meta_intent.target_layer_range:
        raise ConstraintViolation(
            "Layer4 (MGL) cannot be a target_layer in Phase1 - recursive self-redefinition is forbidden."
        )
    if meta_intent.stability_threshold <= 0:
        raise ConstraintViolation("stability_threshold must be > 0.")
    if not meta_intent.constraint_policy:
        raise ConstraintViolation("constraint_policy must reference at least one Layer1 policy ID.")


def build_layer_definitions(meta_intent: MetaIntent) -> dict:
    """Step 2: generate Layer0-4 structure skeletons for the targeted layers."""
    layers: dict[str, dict] = {}
    for layer_id in range(5):
        if layer_id in meta_intent.target_layer_range:
            layers[f"layer{layer_id}"] = {
                "status": "regenerated",
                "structural_goal": meta_intent.structural_goal,
            }
        else:
            layers[f"layer{layer_id}"] = {"status": "unchanged"}
    return layers


def bind_constraints(layers: dict, meta_intent: MetaIntent) -> dict:
    """Step 3: attach Layer1 constraint policy references to every regenerated layer."""
    for name, definition in layers.items():
        if definition.get("status") == "regenerated":
            definition["constraint_policy"] = list(meta_intent.constraint_policy)
    return layers


def build_governance_loop_definition(meta_intent: MetaIntent) -> dict:
    """Step 4: generate the Governance Loop definition (lifecycle, drift/decision left as refs)."""
    return {
        "lifecycle": "evolving",
        "stability_threshold": meta_intent.stability_threshold,
        "drift_layer_ref": "layer2" if 2 in meta_intent.target_layer_range else None,
        "decision_layer_ref": "layer3" if 3 in meta_intent.target_layer_range else None,
        "redefinition_layer_ref": "layer4",
    }


def generate_blueprint(meta_intent: MetaIntent, blueprint_id: str) -> SystemBlueprint:
    """Step 1-5: MetaIntent -> SystemBlueprint."""
    check_layer1_constraints(meta_intent)  # Step 1 + Layer1 gate

    layers = build_layer_definitions(meta_intent)        # Step 2
    layers = bind_constraints(layers, meta_intent)        # Step 3
    governance_loop = build_governance_loop_definition(meta_intent)  # Step 4

    blueprint = SystemBlueprint(                          # Step 5
        blueprint_id=blueprint_id,
        source_meta_intent_id=meta_intent.meta_intent_id,
        layer_definitions=layers,
        intent_schema_version="v1",
        graph_topology={"edge_types": []},
        drift_model={},
        governance_loop_definition=governance_loop,
        validation_status="passed",
    )
    return blueprint

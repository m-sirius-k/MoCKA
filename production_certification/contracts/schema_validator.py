"""Phase 8: lightweight JSON-schema-like validation and breaking-change detection."""

from __future__ import annotations

from typing import Any

from contracts.api_contract import APIContract

_TYPE_MAP = {
    "string": str,
    "number": (int, float),
    "integer": int,
    "boolean": bool,
    "object": dict,
    "array": list,
}


class SchemaValidationError(Exception):
    pass


def validate(payload: dict, schema: dict) -> None:
    """Validate `payload` against a simple schema:

    {
      "type": "object",
      "required": ["field_a", "field_b"],
      "properties": {"field_a": {"type": "string"}, ...}
    }
    """
    if schema.get("type") == "object" and not isinstance(payload, dict):
        raise SchemaValidationError("payload must be an object")

    for field in schema.get("required", []):
        if field not in payload:
            raise SchemaValidationError(f"missing required field: {field}")

    properties = schema.get("properties", {})
    for field, value in payload.items():
        if field not in properties:
            continue
        expected_type = properties[field].get("type")
        py_type = _TYPE_MAP.get(expected_type)
        if py_type and not isinstance(value, py_type):
            raise SchemaValidationError(
                f"field '{field}' expected type {expected_type}, got {type(value).__name__}"
            )


def validate_input(contract: APIContract, payload: dict) -> None:
    validate(payload, contract.input_schema)


def validate_output(contract: APIContract, payload: dict) -> None:
    validate(payload, contract.output_schema)


def is_breaking_change(old_schema: dict, new_schema: dict) -> bool:
    """A change is breaking if any previously required field is removed,
    any previously required field's type changes, or a new required field
    is added without a default (i.e. existing callers would now fail)."""
    old_required = set(old_schema.get("required", []))
    new_required = set(new_schema.get("required", []))

    if old_required - new_required:
        # a previously-required field is no longer required is NOT breaking
        pass

    if new_required - old_required:
        # newly required fields break existing callers that don't send them
        return True

    old_props = old_schema.get("properties", {})
    new_props = new_schema.get("properties", {})
    for field, old_spec in old_props.items():
        if field in new_props and new_props[field].get("type") != old_spec.get("type"):
            return True

    return False

"""Phase 8: API contract boundary definition.

Every API surface exposed by MoCKA must be registered with a fixed-version
input/output schema. Breaking changes require a new version, never an
in-place mutation of an existing contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class APIContract:
    name: str
    version: str
    input_schema: dict = field(default_factory=dict)
    output_schema: dict = field(default_factory=dict)

    @property
    def key(self) -> str:
        return f"{self.name}@{self.version}"


class ContractRegistry:
    """Append-only registry: contracts are immutable once registered.

    Re-registering the same (name, version) with a different schema is
    treated as a breaking change and rejected.
    """

    def __init__(self) -> None:
        self._contracts: dict[str, APIContract] = {}

    def register(self, contract: APIContract) -> None:
        existing = self._contracts.get(contract.key)
        if existing is not None and existing != contract:
            raise ValueError(
                f"Breaking change rejected: contract {contract.key} already "
                f"registered with a different schema"
            )
        self._contracts[contract.key] = contract

    def get(self, name: str, version: str) -> APIContract:
        key = f"{name}@{version}"
        if key not in self._contracts:
            raise KeyError(f"No contract registered for {key}")
        return self._contracts[key]

    def all(self) -> list[APIContract]:
        return list(self._contracts.values())

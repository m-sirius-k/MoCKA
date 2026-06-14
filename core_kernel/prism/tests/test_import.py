"""
prism.tests.test_import

Prismパッケージのimport・依存制約に関するテスト。
"""

import ast
from pathlib import Path

import pytest

PRISM_ROOT = Path(__file__).resolve().parent.parent

FORBIDDEN_MODULES = (
    "memory",
    "relay",
    "caliber.orchestra",
    "orchestra",
    "controller",
    "workflow",
    "tool_runner",
)


def test_prism_package_imports():
    import core_kernel.prism as prism

    assert hasattr(prism, "PrismAnalyzer")
    assert hasattr(prism, "AnalysisResult")
    assert hasattr(prism, "Context")
    assert hasattr(prism, "Observation")
    assert hasattr(prism, "SemanticAnnotation")
    assert hasattr(prism, "CognitiveState")
    assert hasattr(prism, "CognitiveStateValue")
    assert hasattr(prism, "PRISM_VERSION")


def test_prism_analyzer_public_api_only():
    from core_kernel.prism import PrismAnalyzer

    public_methods = {
        name for name in dir(PrismAnalyzer)
        if not name.startswith("_") and callable(getattr(PrismAnalyzer, name))
    }

    assert public_methods == {"analyze", "analyze_many"}


def _iter_python_files():
    for path in PRISM_ROOT.rglob("*.py"):
        yield path


def _iter_imported_module_names(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                yield node.module


@pytest.mark.parametrize("path", list(_iter_python_files()))
def test_no_forbidden_imports(path):
    for module_name in _iter_imported_module_names(path):
        for forbidden in FORBIDDEN_MODULES:
            assert not module_name.startswith(forbidden), (
                f"{path} が禁止モジュール '{module_name}' をimportしている"
            )


@pytest.mark.parametrize("path", list(_iter_python_files()))
def test_core_store_access_is_read_only(path):
    """core_store からは Registry/Lifecycle/Capability の読み取り専用APIのみ利用してよい。"""
    source = path.read_text(encoding="utf-8")
    if "core_store" not in source:
        return

    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and "core_store" in node.module:
            allowed = {
                "ModuleRegistry",
                "ModuleMetadata",
                "LifecycleManager",
                "LifecycleState",
                "CapabilityRegistry",
                "ConfigStore",
                "PersistenceBackend",
                "InMemoryBackend",
                "ModuleLoader",
            }
            for alias in node.names:
                assert alias.name in allowed, (
                    f"{path} が未許可のcore_store要素 '{alias.name}' をimportしている"
                )

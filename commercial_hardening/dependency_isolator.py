# -*- coding: utf-8 -*-
"""Dependency Isolator (Phase 6 Commercial Hardening Layer)

役割:
  - cross-layer dependency lock (許可された依存関係のみホワイトリスト化)
  - circular dependency prevention (DFSによる循環検出)
  - external coupling reduction (外部パッケージ依存の検出・警告)

このモジュールは依存関係を「実行」せず、宣言された依存グラフを検証するのみ。
"""

from dataclasses import dataclass, field

# commercial_hardening配下モジュール間で許可される依存関係 (from -> to)
ALLOWED_DEPENDENCIES = {
    "hardening_pipeline": {
        "environment_isolator",
        "dependency_isolator",
        "module_sandbox",
        "runtime_safety_guard",
        "execution_router",
        "failure_containment",
        "safe_fallback_engine",
        "degradation_controller",
        "production_mode_manager",
        "deployment_gate",
    },
    "execution_router": {"production_mode_manager", "failure_containment", "safe_fallback_engine"},
    "runtime_safety_guard": {"safe_fallback_engine"},
    "failure_containment": {"safe_fallback_engine"},
    "degradation_controller": {"production_mode_manager"},
    "deployment_gate": set(),
    "module_sandbox": {"environment_isolator"},
    "safe_fallback_engine": set(),
    "production_mode_manager": set(),
    "environment_isolator": set(),
    "dependency_isolator": set(),
}

# 外部結合として許容されるトップレベルパッケージ (標準ライブラリのみ)
ALLOWED_EXTERNAL = {"os", "sys", "time", "enum", "dataclasses", "typing", "json", "threading", "random"}


@dataclass
class IsolationReport:
    cycles: list = field(default_factory=list)
    unauthorized_edges: list = field(default_factory=list)
    external_violations: list = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.cycles and not self.unauthorized_edges and not self.external_violations


def check_edges(edges: dict) -> IsolationReport:
    """edges: {module_name: set(depends_on_module_names)} を検証する。"""
    report = IsolationReport()

    # unauthorized edges
    for src, deps in edges.items():
        allowed = ALLOWED_DEPENDENCIES.get(src, set())
        for dst in deps:
            if dst not in allowed:
                report.unauthorized_edges.append((src, dst))

    # circular dependency detection (DFS)
    visiting, visited = set(), set()

    def dfs(node, path):
        if node in visiting:
            cycle_start = path.index(node)
            report.cycles.append(path[cycle_start:] + [node])
            return
        if node in visited:
            return
        visiting.add(node)
        for dst in edges.get(node, set()):
            dfs(dst, path + [node])
        visiting.discard(node)
        visited.add(node)

    for node in edges:
        if node not in visited:
            dfs(node, [])

    return report


def check_external_imports(module_imports: dict) -> IsolationReport:
    """module_imports: {module_name: set(top_level_import_names)} を検証する。"""
    report = IsolationReport()
    for module, imports in module_imports.items():
        for imp in imports:
            if imp not in ALLOWED_EXTERNAL and imp not in ALLOWED_DEPENDENCIES:
                report.external_violations.append((module, imp))
    return report


def verify_self() -> IsolationReport:
    """ALLOWED_DEPENDENCIES自体に循環がないことを検証する(自己検証)。"""
    return check_edges(ALLOWED_DEPENDENCIES)

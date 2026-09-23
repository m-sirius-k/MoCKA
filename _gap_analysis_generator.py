#!/usr/bin/env python3
"""
MOCKA IMPLEMENTATION GAP ANALYSIS GENERATOR
Systematic audit of design vs implementation vs wiring vs enforcement vs evidence
Phase: KUROKO ONE-SHOT Audit Execution

Status Dimensions:
- DESIGN: Appears in architecture/specification documents
- SPECIFIED: Formal spec/contract exists
- IMPLEMENTED: Code exists
- WIRED: Code is called/imported at runtime
- ENFORCED: Actually prevents/validates at runtime
- TESTED: Integration/runtime tests exist
- EVIDENCED: Events/ledger/audit records generated
- OPERATIONAL: Can be used in current operations

Classification levels:
- P0: Authorization/HG decision required to enable
- P1: Runtime enforcement critical
- P2: Evidence/Test/Reliability gap
- P3: Commercial/UX/Documentation
- P4: Cosmetic/Low priority
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

BASE_PATH = Path("C:\\Users\\sirok\\MoCKA")

# ============================================================================
# ARCHITECTURE & SPEC SCANNING
# ============================================================================

def scan_architecture_documents():
    """Extract design specifications from .md documents"""
    specs = {}

    arch_files = [
        "ARCHITECTURE.md",
        "DECISION_LAYER.md",
        "GATE_ARCHITECTURE_v1.md",
        "CONSTITUTION.md",
        "LEARNING_KERNEL.md",
        "MEMORY_LAYER.md",
        "SELF_AUDIT_LAYER.md",
        "SEMANTIC_LAYER.md",
        "QUALITY_GATE.md",
    ]

    for fname in arch_files:
        fpath = BASE_PATH / fname
        if fpath.exists():
            content = fpath.read_text(encoding='utf-8', errors='ignore')
            # Extract sections, keywords, architecture
            sections = re.findall(r"^### (.+)$", content, re.MULTILINE)
            components = re.findall(r"(?:^|\n)(?:`?)([\w_/\.]+\.py)(?:`?)", content)
            classes = re.findall(r"(?:class|def|def.*\()\s+(\w+)\s*(?:\(|:)", content)

            specs[fname] = {
                "sections": sections,
                "mentioned_components": list(set(components)),
                "mentioned_classes": list(set(classes)),
                "content_length": len(content),
            }

    return specs

def scan_design_elements():
    """Extract specific design decisions from documentation"""
    design_elements = defaultdict(lambda: {"design_location": None, "description": None})

    # Key architectural elements from README, CONSTITUTION, etc
    key_docs = {
        "mocka_Movement": "README.md",
        "shadow_Movement": "README.md",
        "acceptor:infield": "README.md",
        "acceptor:outfield": "README.md",
        "Caliber": "README.md",
        "Governance Charter": "CONSTITUTION.md",
        "Decision Layer": "DECISION_LAYER.md",
        "Semantic Layer": "SEMANTIC_LAYER.md",
        "Memory Layer": "MEMORY_LAYER.md",
        "Learning Kernel": "LEARNING_KERNEL.md",
        "Self-Audit": "SELF_AUDIT_LAYER.md",
        "Gate Architecture": "GATE_ARCHITECTURE_v1.md",
        "M18 Guards": "M18_RUNTIME_ENFORCEMENT_VERIFICATION_FULL_REPORT_20260912.md",
        "M11 In-flight Reverification": "M18_RUNTIME_ENFORCEMENT_VERIFICATION_FULL_REPORT_20260912.md",
    }

    for elem, doc in key_docs.items():
        fpath = BASE_PATH / doc
        if fpath.exists():
            content = fpath.read_text(encoding='utf-8', errors='ignore')
            if elem.lower() in content.lower():
                design_elements[elem]["design_location"] = doc

    return design_elements

# ============================================================================
# CODE SCANNING
# ============================================================================

def find_python_files(pattern=None):
    """Find all Python files in the codebase"""
    py_files = list(BASE_PATH.glob("**/*.py"))
    if pattern:
        py_files = [f for f in py_files if pattern in str(f)]
    return sorted(set(py_files))

def scan_implementation():
    """Scan for actual code implementation"""
    impl = defaultdict(lambda: {"exists": False, "path": None, "lines": 0, "classes": [], "functions": []})

    for pyfile in find_python_files():
        try:
            content = pyfile.read_text(encoding='utf-8', errors='ignore')

            # Find classes
            classes = re.findall(r"^class\s+(\w+)", content, re.MULTILINE)
            functions = re.findall(r"^def\s+(\w+)", content, re.MULTILINE)

            relpath = str(pyfile.relative_to(BASE_PATH))
            impl[relpath] = {
                "exists": True,
                "path": str(pyfile),
                "lines": len(content.split('\n')),
                "classes": classes,
                "functions": functions,
            }
        except Exception as e:
            pass

    return impl

def find_runtime_wiring():
    """Determine what's actually called at runtime"""
    # Analyze imports and subprocess calls
    wiring = defaultdict(lambda: {"imported_by": [], "called_from": [], "subprocess_calls": []})

    for pyfile in find_python_files():
        try:
            content = pyfile.read_text(encoding='utf-8', errors='ignore')
            relpath = str(pyfile.relative_to(BASE_PATH))

            # Find imports of other modules
            imports = re.findall(r"from\s+([\w\.]+)\s+import|import\s+([\w\.]+)", content)
            for imp in imports:
                imported = imp[0] or imp[1]
                if imported in wiring:
                    wiring[imported]["imported_by"].append(relpath)

            # Find subprocess calls
            subproc = re.findall(r"subprocess\.(run|call|Popen)\s*\(\s*['\"]([^'\"]+)['\"]", content)
            if subproc:
                wiring[relpath]["subprocess_calls"] = [s[1] for s in subproc]

        except Exception as e:
            pass

    return wiring

def scan_tests():
    """Find test files"""
    tests = {}
    test_files = find_python_files("test")
    for tf in test_files:
        try:
            content = tf.read_text(encoding='utf-8', errors='ignore')
            test_methods = re.findall(r"def\s+(test_\w+)", content)
            tests[str(tf.relative_to(BASE_PATH))] = {
                "path": str(tf),
                "test_methods": test_methods,
                "count": len(test_methods),
            }
        except:
            pass
    return tests

def scan_event_recording():
    """Check for event/ledger recording capabilities"""
    event_patterns = {
        "mocka_write_event": [],
        "mocka_decision_write": [],
        "mocka_integrity_write": [],
        "event_bus.publish": [],
        "events.db": [],
        "ledger": [],
        "audit_log": [],
    }

    for pyfile in find_python_files():
        try:
            content = pyfile.read_text(encoding='utf-8', errors='ignore')
            relpath = str(pyfile.relative_to(BASE_PATH))

            for pattern in event_patterns:
                if pattern in content:
                    event_patterns[pattern].append(relpath)
        except:
            pass

    return event_patterns

# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def generate_gap_inventory():
    """Generate comprehensive gap inventory"""

    print("="*80)
    print("MOCKA IMPLEMENTATION GAP ANALYSIS - KUROKO ONE-SHOT")
    print(f"Date: 2026-09-13 | System State: HOLD / FAIL-CLOSED")
    print("="*80)
    print()

    print("[PHASE 1] ARCHITECTURE & DESIGN SCANNING")
    print("-" * 80)
    arch_specs = scan_architecture_documents()
    print(f"Found {len(arch_specs)} architecture documents")
    for fname, spec in arch_specs.items():
        print(f"  {fname}: {len(spec['sections'])} sections, {len(spec['mentioned_components'])} components")
    print()

    print("[PHASE 2] DESIGN ELEMENT VERIFICATION")
    print("-" * 80)
    design_elems = scan_design_elements()
    print(f"Found {len(design_elems)} major design elements")
    for elem, info in list(design_elems.items())[:20]:
        loc = info.get("design_location", "NOT_FOUND")
        print(f"  {elem}: {loc}")
    print()

    print("[PHASE 3] IMPLEMENTATION CODE SCANNING")
    print("-" * 80)
    impl = scan_implementation()
    print(f"Found {len([i for i in impl.values() if i['exists']])} Python files with implementations")

    # By directory
    by_dir = defaultdict(int)
    for path, info in impl.items():
        if info['exists']:
            dir_name = path.split('\\')[0] if '\\' in path else path.split('/')[0]
            by_dir[dir_name] += 1

    for dirname in sorted(by_dir.keys()):
        print(f"  {dirname}: {by_dir[dirname]} files")
    print()

    print("[PHASE 4] RUNTIME WIRING ANALYSIS")
    print("-" * 80)
    wiring = find_runtime_wiring()

    # Find unimported/dead code
    unimported = []
    for pyfile in find_python_files():
        relpath = str(pyfile.relative_to(BASE_PATH))
        if relpath not in wiring or not wiring[relpath]["imported_by"]:
            if "__init__" not in relpath and "test_" not in relpath:
                unimported.append(relpath)

    print(f"Found {len([w for w in wiring.values() if w['imported_by']])} imported modules")
    print(f"Found {len(unimported)} potentially unimported/dead files")
    if unimported[:10]:
        print("  Sample unimported files:")
        for uf in unimported[:10]:
            print(f"    {uf}")
    print()

    print("[PHASE 5] TEST COVERAGE SCANNING")
    print("-" * 80)
    tests = scan_tests()
    print(f"Found {len(tests)} test files")
    total_tests = sum(t.get('count', 0) for t in tests.values())
    print(f"Total test methods: {total_tests}")
    print()

    print("[PHASE 6] EVENT/EVIDENCE RECORDING")
    print("-" * 80)
    events = scan_event_recording()
    print("Event recording capabilities found in:")
    for pattern, files in events.items():
        if files:
            print(f"  {pattern}: {len(files)} files")
    print()

    print("[PHASE 7] CRITICAL GAPS FROM M18 REPORT")
    print("-" * 80)
    print("  Based on M18_RUNTIME_ENFORCEMENT_VERIFICATION_FULL_REPORT_20260912.md:")
    print("  - E01-E05 (5 paths): PROTECTED by M18")
    print("  - E06-E22 (17 paths): UNPROTECTED - NO M18 GUARD")
    print("  - M11 In-flight Reverification: NOT_PROVEN wired")
    print("  - HG → Authorization → Resolver: PARTIALLY_BOUND")
    print("  - A10 adversarial test: FAILS (direct subprocess not blocked)")
    print()

    return {
        "arch_specs": arch_specs,
        "design_elements": design_elems,
        "implementation": impl,
        "wiring": wiring,
        "tests": tests,
        "events": events,
        "unimported_files": unimported,
    }

if __name__ == "__main__":
    results = generate_gap_inventory()

    # Save results to file
    output_file = BASE_PATH / "MOCKA_GAP_ANALYSIS_SUMMARY_20260913.txt"
    print(f"\n\nAnalysis complete. Details will be used for full inventory creation.")
    print(f"Next: Create detailed gap matrix with design/spec/impl/wiring/enforce/test/evidence dimensions")

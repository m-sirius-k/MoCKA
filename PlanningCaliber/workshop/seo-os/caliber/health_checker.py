import json, os
from datetime import datetime

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "worker_registry.json")

def load_registry():
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        return json.load(f)

def check_wordpress(config: dict) -> dict:
    return {
        "worker": "wordpress",
        "enabled": config.get("enabled", False),
        "status": "ready" if config.get("enabled") else "disabled",
        "checked_at": datetime.now().isoformat()
    }

def check_sftp(config: dict) -> dict:
    return {
        "worker": "sftp",
        "enabled": config.get("enabled", False),
        "status": "ready" if config.get("enabled") else "disabled",
        "checked_at": datetime.now().isoformat()
    }

def check_x(config: dict) -> dict:
    return {
        "worker": "x",
        "enabled": config.get("enabled", False),
        "status": "disabled",
        "checked_at": datetime.now().isoformat()
    }

def check_instagram(config: dict) -> dict:
    return {
        "worker": "instagram",
        "enabled": config.get("enabled", False),
        "status": "disabled",
        "checked_at": datetime.now().isoformat()
    }

CHECKERS = {
    "wordpress": check_wordpress,
    "sftp":      check_sftp,
    "x":         check_x,
    "instagram": check_instagram,
}

def run_health_check() -> dict:
    registry = load_registry()
    results = {}
    for name, config in registry.items():
        checker = CHECKERS.get(name)
        if checker:
            results[name] = checker(config)
        else:
            results[name] = {
                "worker": name,
                "status": "unknown",
                "checked_at": datetime.now().isoformat()
            }
    return results

def get_capabilities() -> dict:
    registry = load_registry()
    cap_map = {}
    for worker_name, config in registry.items():
        if not config.get("enabled"):
            continue
        for cap in config.get("capabilities", []):
            if cap not in cap_map:
                cap_map[cap] = []
            cap_map[cap].append(worker_name)
    return cap_map

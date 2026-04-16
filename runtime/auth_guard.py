from runtime.env_utils import get_env

def enforce_rebuild_permission():
    role = get_env("ROLE")

    if role != "admin":
        raise Exception("REBUILD NOT ALLOWED")

    print("REBUILD AUTHORIZED")

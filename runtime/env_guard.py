from runtime.env_utils import get_env

def enforce_env(mode="verify"):
    if mode == "rebuild":
        get_env("API_KEY")
    elif mode == "api":
        get_env("API_KEY")

    print(f"ENV OK ({mode})")

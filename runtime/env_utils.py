import os
from dotenv import load_dotenv

load_dotenv()

def get_env(key):
    value = os.getenv(key)
    if value is None:
        raise Exception(f"Missing ENV: {key}")
    return value

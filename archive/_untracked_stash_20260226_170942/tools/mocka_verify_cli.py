import sys
from src.mocka_audit.verify_chain import verify_chain

if __name__ == "__main__":
    result = verify_chain()
    print(result)
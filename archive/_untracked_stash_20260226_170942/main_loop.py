from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def main():
    print("BASE_DIR=" + str(BASE_DIR))

if __name__ == "__main__":
    main()

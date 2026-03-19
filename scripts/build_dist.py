import shutil, os

def build():
    if os.path.exists("dist"):
        shutil.rmtree("dist")

    os.makedirs("dist",exist_ok=True)

    files = [
        "verify_token.py",
        "verify_ledger.py",
        "use_testkey.py"
    ]

    for f in files:
        if os.path.exists(f):
            shutil.copy(f,"dist/"+f)

    print("DIST BUILD COMPLETE")

if __name__ == "__main__":
    build()

import os

TARGET_FILE=r"C:\Users\sirok\MoCKA\civilization_evolution_loop.py"

def patch_file():

    if not os.path.exists(TARGET_FILE):
        print("TARGET_NOT_FOUND")
        return False

    with open(TARGET_FILE,"r",encoding="utf-8") as f:
        code=f.readlines()

    new_code=[]

    for line in code:

        if "TEST INCIDENT FROM CIVILIZATION LOOP" in line:
            new_code.append("# MoCKA repair patch applied\n")
            new_code.append("# exception disabled\n")
        else:
            new_code.append(line)

    with open(TARGET_FILE,"w",encoding="utf-8") as f:
        f.writelines(new_code)

    return True

def main():

    ok=patch_file()

    if ok:
        print("CIVILIZATION_LOOP_PATCHED")
    else:
        print("PATCH_FAILED")

if __name__=="__main__":
    main()

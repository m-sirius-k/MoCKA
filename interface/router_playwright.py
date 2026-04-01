import subprocess

def execute(task):
    if "browser" in task.lower():
        subprocess.run(
            ["python", r"C:\Users\sirok\MoCKA\interface\playwright_engine.py"]
        )
        return "[PLAYWRIGHT EXECUTED]"
    else:
        return "[NO ACTION]"

def main():
    task = "browser open test"
    result = execute(task)

    print("=== Physical Execution ===")
    print(result)

if __name__ == "__main__":
    main()

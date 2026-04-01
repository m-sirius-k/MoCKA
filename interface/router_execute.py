import subprocess

def route_and_execute(task):
    result = subprocess.run(
        ["python", r"C:\Users\sirok\MoCKA\interface\router_ai.py"],
        capture_output=True,
        text=True
    )

    if "claude_execute" in result.stdout:
        output = subprocess.run(
            ["python", r"C:\Users\sirok\MoCKA\interface\claude_sandbox.py"],
            capture_output=True,
            text=True
        )
        return output.stdout
    else:
        return "[ROUTED TO GPT AUDIT]"

def main():
    task = "test sandbox execution"
    output = route_and_execute(task)

    print("=== Routed Execution ===")
    print(output)

if __name__ == "__main__":
    main()

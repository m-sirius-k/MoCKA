from interface.router import MoCKARouter
import sys

def main():
    router = MoCKARouter()
    print("--- MoCKA Civilization OS v1.1 [SECURITY-PATCHED] ---")
    
    while True:
        try:
            prompt = input("MoCKA > ")
            if prompt.lower() in ["exit", "quit"]: break
            if not prompt.strip(): continue

            res = router.run(prompt)
            d = res['decision']
            meta = d.get('meta', {})

            print(f"\n[WINNER]    {d['provider']} (Score: {meta.get('score', 'N/A')})")
            print(f"[STABILITY] {'STABLE' if meta.get('is_unanimous') else 'DIVERGED (COLLISION!)'}")
            print(f"[OUTPUT]    {d['output']}")
            print("-" * 40)

        except KeyboardInterrupt: break
    print("\nCivilization Sleeping...")

if __name__ == "__main__":
    main()

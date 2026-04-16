from interface.router import MoCKARouter
from interface.consensus import MoCKAConsensus
from interface.memory_engine import save_consensus_result

def main():
    prompt = "compare this system"
    router = MoCKARouter()
    
    print(f"--- MO-CKA DISTRIBUTED AUDIT ---")
    # Router 内部で Google/Azure/Local を一斉実行
    res = router.run(prompt)
    decision = res.get("meta") or res.get("decision") # 以前の形式も考慮

    if not decision:
        print("ERROR: No decision reached.")
        return

    print(f"WINNER      : {decision['provider']} (Score: {decision.get('score', 'N/A')})")
    print(f"ACTIVE NODES: {', '.join(decision.get('audit_log', ['local']))}")
    print(f"STABILITY   : {'STABLE' if decision.get('is_unanimous') else 'DIVERGED'}")
    print(f"OUTPUT      : {decision['output'][:50]}...")

if __name__ == "__main__":
    main()

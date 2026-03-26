class MoCKAConsensus:
    # 権威スコアの定義
    TRUST_SCORES = {
        "security_expert": 0.95,  # 最優先：安全第一
        "memory": 1.0,           # 確定した正史
        "google": 0.9,           # 汎用知能
        "local": 0.5             # 生存維持
    }

    @staticmethod
    def resolve(results):
        if not results: return None
        
        candidates = []
        for res in results:
            # Routerから渡される各ノードの結果を解析
            out_list = res.get("analysis", {}).get("outputs", [])
            if not out_list: continue
            
            out = out_list[0]
            p = out.get("provider", "unknown")
            candidates.append({
                "text": out.get("text"),
                "provider": p,
                "score": MoCKAConsensus.TRUST_SCORES.get(p, 0.1)
            })

        if not candidates: return None

        # スコア最大の候補を WINNER とする（調停）
        winner = max(candidates, key=lambda x: x["score"])
        
        # 1つでも異なる意見があれば衝突とみなす
        is_unanimous = all(c["text"] == candidates[0]["text"] for c in candidates)
        
        return {
            "output": winner["text"],
            "provider": winner["provider"],
            "score": winner["score"],
            "is_unanimous": is_unanimous,
            "collision_detected": not is_unanimous,
            "node_count": len(candidates),
            "audit_log": [c["provider"] for c in candidates]
        }

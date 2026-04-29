# このファイルはパッチ確認用。実際の変更箇所を示す。
#
# phl_select_modules()の以下の行:
#   selected = list(dict.fromkeys(c["module"] for c in candidates))
#
# を以下に差し替える:

def phl_select_modules_v2(state):
    candidates = []

    # --- 既存のif分岐はそのまま維持 ---
    if state.get("uncertainty", 0) >= 0.6 or state.get("evidence_required", 0) >= 0.7:
        candidates.append({"module":"ghost",      "trigger":"uncertainty>=0.6 or evidence_required>=0.7"})
    if "plan" in state.get("output_format",[]) or state.get("abstraction_level",0) >= 0.6:
        candidates.append({"module":"L99",        "trigger":"plan in output_format or abstraction_level>=0.6"})
    if state.get("goal_type") == "decision" or state.get("time_pressure",0) >= 0.7:
        candidates.append({"module":"OODA",       "trigger":"goal_type==decision or time_pressure>=0.7"})
    if state.get("goal_type") in ["design","review"] and state.get("abstraction_level",0) >= 0.7:
        candidates.append({"module":"SAGE",       "trigger":"goal_type in [design,review] and abstraction_level>=0.7"})
        candidates.append({"module":"STRATEGIST", "trigger":"goal_type in [design,review] and abstraction_level>=0.7"})
    if "code" in state.get("output_format",[]) or state.get("goal_type") == "implementation":
        candidates.append({"module":"code",       "trigger":"code in output_format or goal_type==implementation"})
    if "table" in state.get("output_format",[]):
        candidates.append({"module":"artifact",   "trigger":"table in output_format"})
    if not candidates:
        candidates.append({"module":"ghost",      "trigger":"fallback:no_match"})

    # --- v2追加: スコアリングで選択・除外を決定 ---
    SCORE_THRESHOLD = 0.25  # この値以下は除外
    scored = []
    excluded = []
    for c in candidates:
        s = phl_score(c["module"], state)
        c["score"] = s
        if s >= SCORE_THRESHOLD:
            scored.append(c)
        else:
            excluded.append({"module": c["module"], "reason": f"score_below_threshold:{s:.4f}"})

    # スコア降順ソート
    scored.sort(key=lambda x: x["score"], reverse=True)

    # 競合解消（既存ルール維持）
    selected = list(dict.fromkeys(c["module"] for c in scored))
    if "OODA" in selected and "SAGE" in selected and state.get("time_pressure",0) > 0.7:
        selected.remove("SAGE")
        excluded.append({"module":"SAGE","reason":"conflict:OODA:time_pressure>0.7"})

    return selected, scored, excluded
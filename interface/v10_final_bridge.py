import json
import os
from dynamic_lever_caliber_v9 import MoCKA_DynamicLever

def execute_full_injection_v10(core_event, raw_data, trust_score=5.0):
    # 1. 動的レバーの生成
    lever = MoCKA_DynamicLever()
    lever_header = json.loads(lever.generate_packet(
        attention=core_event,
        constraints_lv="Strict",
        trust_score=trust_score,
        purpose="v10_Hybrid_Integration_Testing"
    ))

    # 2. フルインジェクション・パケットの構築
    injection_payload = {
        "CONTROL": lever_header,
        "RAW_DATA": raw_data
    }
    
    return json.dumps(injection_payload, ensure_ascii=False)

if __name__ == '__main__':
    # テスト用の「象」（本来は PILS/SACL の蓄積データ）
    sample_elephant = "THIS IS A TEST OF THE EMERGENCY MOCKA BROADCAST. " * 50
    
    payload = execute_full_injection_v10(
        core_event="Main_Fortress_Reconstruction",
        raw_data=sample_elephant,
        trust_score=5.0
    )
    
    print(f"--- MOCKA v10 HYBRID INJECTION ---")
    print(f"Payload Size: {len(payload.encode('utf-8'))} bytes")
    print(f"Header Check: {payload[:150]}...")
    
    # 成果物を保存
    output_path = r'C:\Users\sirok\MoCKA\interface\v10_injection_output.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(payload)
    print(f"Result saved to: {output_path}")

import json
from dynamic_lever_caliber_v9 import MoCKA_DynamicLever

def replay_v9_sequence():
    lever = MoCKA_DynamicLever()
    
    # 博士の指定パラメータをそのまま装填
    # R: ENFORCE_ROUTER_SAVE は目的（P）として定義し、ルーターに通知
    packet = lever.generate_packet(
        attention="REPLAY_V9_STRICT_SEQUENCE",
        constraints_lv="Strict",
        trust_score=5.0,
        purpose="ENFORCE_ROUTER_SAVE"
    )
    
    # ルーター（ファイルシステム）への強制書き込み
    output_path = r'C:\Users\sirok\MoCKA\interface\v10_router_save.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(packet)
    
    return packet

if __name__ == '__main__':
    result = replay_v9_sequence()
    print(f"--- [MOCKA] REPLAY SUCCESS ---")
    print(f"ENFORCED PACKET: {result}")
    print(f"STATUS: ROUTER_SAVE_COMPLETED")

import json

class MoCKA_DynamicLever:
    def __init__(self):
        # 1, 5, 6 は OS レベルで固定（ここでは初期値として保持）
        self.os_layer = {
            "ID": "MoCKA_CSO_Assistant",
            "TONE": "Scientific/No-AI-Fluff",
            "ETHICS": "TRDP/CreationCode_v1.0"
        }

    def generate_packet(self, attention, constraints_lv, trust_score, purpose):
        # 2, 3, 4, 7 を可変レバーとしてパケット化
        # パケットサイズを抑えるためキーを短縮
        packet = {
            "H": "MOCKA_DNA_v2",
            "A": attention,        # 2: Attention (High-Priority Anchor)
            "C": constraints_lv,   # 3: Constraints (Strict/Normal/Relaxed)
            "G": trust_score,      # 4: Grounding (1.0 - 5.0)
            "P": purpose           # 7: Purpose (Current Goal)
        }
        return json.dumps(packet, ensure_ascii=False)

if __name__ == '__main__':
    lever = MoCKA_DynamicLever()
    
    # 例：現在の「17:00 閉ループ実測モード」の実弾を生成
    # 実測値優先（G:5.0）、制約は厳格（C:Strict）
    test_packet = lever.generate_packet(
        attention="Verification of Z-Axis 0.8190",
        constraints_lv="Strict",
        trust_score=5.0,
        purpose="17:00_Closing_Loop_Validation"
    )
    
    print(f"--- MoCKA DNA v2.0 Packet ---")
    print(f"Size: {len(test_packet.encode('utf-8'))} bytes")
    print(f"Packet: {test_packet}")

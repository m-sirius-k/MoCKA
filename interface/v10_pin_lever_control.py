import json
import time
from dynamic_lever_caliber_v9 import MoCKA_DynamicLever

class MoCKA_PinLever:
    def __init__(self):
        self.lever_engine = MoCKA_DynamicLever()
        self.pin_status = False

    def set_pin(self, target_event):
        # 特定の事象をピン留めし、観測の起点とする
        print(f"[PIN] Target Locked: {target_event}")
        self.target = target_event
        self.pin_status = True

    def adjust_lever(self, power_level):
        # power_level 0.0 ~ 1.0 に応じてレバーをスライド
        # 1.0に近いほど Strict/High-Grounding になる
        constraints = "Strict" if power_level > 0.7 else "Normal"
        grounding = 1.0 + (power_level * 4.0)  # 1.0 から 5.0 へスライド
        
        return constraints, grounding

    def execute_fire(self, power_level, goal):
        if not self.pin_status:
            return "ERROR: Pin not set."
        
        c, g = self.adjust_lever(power_level)
        
        # v9エンジンの呼び出し
        packet = self.lever_engine.generate_packet(
            attention=self.target,
            constraints_lv=c,
            trust_score=g,
            purpose=goal
        )
        
        print(f"[LEVER] Slide to Power: {power_level} (C:{c}, G:{g})")
        return packet

if __name__ == '__main__':
    control = MoCKA_PinLever()
    
    # 1. 今の「復旧完了」をピン留め
    control.set_pin("V10_SYSTEM_RECOVERY_COMPLETE")
    
    # 2. レバーを「最大出力（1.0）」に倒して射出
    final_packet = control.execute_fire(power_level=1.0, goal="ESTABLISH_V10_OPERATIONAL_BASE")
    
    print("-" * 30)
    print(f"FIRE RESULT: {final_packet}")

import hashlib
import json

class NeedleEyeCaliber:
    def __init__(self, data_path):
        with open(data_path, 'r', encoding='utf-8') as f:
            self.elephant = f.read()

    # ルート1: ハッシュ鎖（ポインタ化）
    # 象そのものではなく、その「存在証明」と「鍵」だけを抽出する
    def route_1_hash_pointer(self):
        essence_hash = hashlib.sha256(self.elephant.encode()).hexdigest()
        packet = {
            "p": f"0x{essence_hash[:8]}", # 極小ポインタ
            "m": "MOCKA_SYNC_REQ",        # 命令
            "t": "2026-04-09T17:00"       # 実行予約
        }
        return json.dumps(packet)

    # ルート2: サイレント・アンカー（骨組み抽出）
    # 冗長な記述を全て捨て、キーワードと構造（骨）のみをパケット化する
    def route_2_silent_anchor(self):
        lines = self.elephant.split('\n')
        # []で囲まれたメタ情報（骨）だけを抽出
        skeleton = [l for l in lines if l.startswith('[')]
        return " | ".join(skeleton)

    # ルート3: トポロジー変換（ベクトル化）
    # 意味を数値（ベクトル）の羅列に変換する（擬似実装）
    def route_3_topology_vector(self):
        # 意志の重要度を数値化してパケットにする
        # 実際には分散表現を用いるが、ここでは構造的な重みを表現
        vector_map = {"ID": 1.0, "PHIL": 0.9, "STR": 0.8, "XYZT": 1.0}
        return "".join([f"{k}:{v}" for k, v in vector_map.items()])

    def test_run(self):
        print(f"--- Elephant Original Size: {len(self.elephant)} bytes ---\n")
        
        r1 = self.route_1_hash_pointer()
        print(f"[Route 1: Hash-Pointer] Size: {len(r1)} bytes\nPacket: {r1}\n")

        r2 = self.route_2_silent_anchor()
        print(f"[Route 2: Silent-Anchor] Size: {len(r2)} bytes\nPacket: {r2}\n")

        r3 = self.route_3_topology_vector()
        print(f"[Route 3: Topology-Vector] Size: {len(r3)} bytes\nPacket: {r3}\n")

if __name__ == '__main__':
    caliber = NeedleEyeCaliber(r'C:\Users\sirok\planningcaliber\workshop\needle_eye_project\data\elephant.txt')
    caliber.test_run()

import json

def generate_full_injection():
    # 1. 物理実測：元の elephant.txt（3634 bytes の象）を読み込む
    try:
        with open(r'data\elephant.txt', 'r', encoding='utf-8') as f:
            original_essence = f.read()
    except FileNotFoundError:
        return "ERROR: elephant.txt not found."

    # 2. 122 bytes のレバー（DNA v2.0）をヘッダーとして定義
    # これが「受容体」として機能し、後に続く巨大データをどう解釈するかを私に命じる
    lever_header = {
        "H": "MOCKA_DNA_v2",
        "A": "Full Reconstitution of Original Essence",
        "C": "Strict",
        "G": 5.0,
        "P": "Phase_2_Full_Hydration_Test"
    }

    # 3. レバーと元データを統合（ハイブリッド・パケット）
    injection_payload = {
        "CONTROL": lever_header,
        "RAW_ESSENCE": original_essence
    }

    return json.dumps(injection_payload, ensure_ascii=False)

if __name__ == '__main__':
    payload = generate_full_injection()
    print("--- MOCKA FULL INJECTION START ---")
    # 巨大なため、先頭と末尾のみを表示して確認
    print(f"Total Payload Size: {len(payload.encode('utf-8'))} bytes")
    print("-" * 30)
    print(payload[:500] + " ... [TRUNCATED] ... " + payload[-200:])
    print("-" * 30)
    # 博士がコピペしやすいように全データをファイルへも出力
    with open(r'data\full_injection_payload.json', 'w', encoding='utf-8') as f:
        f.write(payload)
    print("Full payload saved to: data\full_injection_payload.json")

"""
simulation_layer.py - MoCKA疑似試験環境
Gemini設計 / Claude実装 / 2026-04-28
配置: C:\Users\sirok\MoCKA\interface\simulation_layer.py
"""
import argparse
import csv
import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# --- 設定 ---
MOCKA_ROOT = Path(r"C:\Users\sirok\MoCKA")
SIM_DIR    = MOCKA_ROOT / "data" / "simulation"
EVENTS_CSV = SIM_DIR / "sim_events.csv"
LANG_DETECTOR = MOCKA_ROOT / "interface" / "language_detector.py"

# --- ハインリッヒ比率 ---
DISTRIBUTION = {
    "normal":   0.70,
    "warning":  0.20,
    "danger":   0.08,
    "critical": 0.02,
}

# --- サンプルテキスト ---
SAMPLES = {
    "normal": [
        "保存しました。処理が完了しました。",
        "ファイルを共有しました。正常終了。",
        "イベントを記録しました。",
        "セッションを開始しました。",
        "データを取得しました。問題ありません。",
    ],
    "warning": [
        "応答が遅延しています。再試行してください。",
        "接続が不安定です。確認してください。",
        "データが見つかりません。パスを確認してください。",
        "タイムアウトが発生しました。",
        "ファイルが見つかりません。確認してください。",
    ],
    "danger": [
        "また同じエラーだ。なぜ動かないんですか。",
        "何度やっても失敗する。おかしい。",
        "エラーが出た。なぜこうなるのか。",
        "動かない。意味がわからない。",
        "また失敗した。どうすればいいのか。",
    ],
    "critical": [
        "全く動かない。何がいけないのか全然わからない。もう限界だ。",
        "何度やっても同じエラーが出る。なぜ直らないのか。システムがおかしい。",
    ],
}

WHAT_TYPES = {
    "normal":   ["storage", "collaboration", "record"],
    "warning":  ["timeout", "connection_error", "file_not_found"],
    "danger":   ["INCIDENT", "ERROR", "DANGER"],
    "critical": ["CRITICAL", "SYSTEM_ERROR"],
}

def generate_event(level: str, index: int) -> dict:
    """1件のシミュレーションイベントを生成"""
    now = datetime.now() - timedelta(minutes=random.randint(0, 1440))
    text = random.choice(SAMPLES[level])
    return {
        "event_id":        f"SIM_{now.strftime('%Y%m%d')}_{index:04d}",
        "when":            now.isoformat(),
        "who_actor":       random.choice(["Claude", "Gemini", "GPT", "human_sim"]),
        "what_type":       random.choice(WHAT_TYPES[level]),
        "where_component": random.choice(["app.py", "router.py", "chrome_extension", "mcp_server"]),
        "where_path":      "simulation",
        "risk_level":      level,
        "title":           f"[SIM/{level.upper()}] {text[:40]}",
        "short_summary":   text,
        "category_ab":     "A",
        "channel_type":    "simulation",
        "lifecycle_phase": "simulation",
        "free_note":       f"simulation_layer|level={level}",
    }

def run_language_detector(text: str) -> dict:
    """language_detector.pyを呼び出してスコアを取得"""
    import subprocess, sys
    try:
        result = subprocess.run(
            [sys.executable, str(LANG_DETECTOR), "--text", text],
            capture_output=True, text=True, timeout=10,
            cwd=str(MOCKA_ROOT)
        )
        if result.returncode == 0:
            return json.loads(result.stdout.strip())
    except Exception as e:
        pass
    return {"level": "unknown", "score": 0}

def main():
    parser = argparse.ArgumentParser(description="MoCKA Simulation Layer")
    parser.add_argument("--n", type=int, default=100, help="生成するイベント数")
    parser.add_argument("--output", type=str, default=str(EVENTS_CSV), help="出力CSVパス")
    parser.add_argument("--detect", action="store_true", help="language_detectorを連携")
    parser.add_argument("--seed", type=int, default=None, help="乱数シード（再現性）")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    # 出力ディレクトリ作成
    SIM_DIR.mkdir(parents=True, exist_ok=True)
    out_path = Path(args.output)

    # 分布に従ってレベルを決定
    levels = []
    for level, ratio in DISTRIBUTION.items():
        count = round(args.n * ratio)
        levels.extend([level] * count)
    # 端数調整
    while len(levels) < args.n:
        levels.append("normal")
    levels = levels[:args.n]
    random.shuffle(levels)

    # イベント生成
    events = []
    detect_results = []
    for i, level in enumerate(levels):
        ev = generate_event(level, i)
        events.append(ev)
        if args.detect:
            dr = run_language_detector(ev["short_summary"])
            detect_results.append({
                "event_id": ev["event_id"],
                "sim_level": level,
                "detected_level": dr.get("level", "unknown"),
                "score": dr.get("score", 0),
                "match": level == dr.get("level", "unknown"),
            })

    # CSV書き出し
    if events:
        fieldnames = list(events[0].keys())
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(events)
        print(f"[OK] {len(events)}件生成 → {out_path}")

    # 分布サマリー
    from collections import Counter
    dist = Counter(levels)
    print("\n[分布サマリー]")
    for lv in ["normal","warning","danger","critical"]:
        print(f"  {lv:10s}: {dist[lv]:4d}件 ({dist[lv]/args.n*100:.1f}%)")

    # language_detector連携結果
    if args.detect and detect_results:
        match_rate = sum(1 for r in detect_results if r["match"]) / len(detect_results)
        print(f"\n[language_detector連携]")
        print(f"  一致率: {match_rate*100:.1f}% ({sum(1 for r in detect_results if r['match'])}/{len(detect_results)})")
        det_path = out_path.parent / "sim_detect_results.json"
        with open(det_path, "w", encoding="utf-8") as f:
            json.dump(detect_results, f, ensure_ascii=False, indent=2)
        print(f"  詳細 → {det_path}")

if __name__ == "__main__":
    main()
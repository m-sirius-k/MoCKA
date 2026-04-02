"""
mocka_condense_worker.py
MoCKA 濃縮ワーカー - RAW層を監視してREDUCED層に自動変換

実行:
  python scripts/mocka_condense_worker.py           # 常時監視モード
  python scripts/mocka_condense_worker.py --once    # 未処理ファイルを1回処理して終了
  python scripts/mocka_condense_worker.py --file X:\down\xxx.json  # 特定ファイルを処理
"""
import argparse, csv, hashlib, json, os, subprocess, time
from datetime import datetime, timezone
from pathlib import Path

ROOT     = Path(r'C:\Users\sirok\MoCKA')
RAW_DIR  = ROOT / 'data' / 'storage' / 'infield' / 'RAW'
REDUCED  = ROOT / 'data' / 'storage' / 'infield' / 'REDUCED'
DONE_DIR = ROOT / 'data' / 'storage' / 'infield' / 'RAW_DONE'
EVENTS   = ROOT / 'data' / 'events.csv'
OLLAMA   = Path(os.environ.get('LOCALAPPDATA','')) / 'Programs' / 'Ollama' / 'ollama.exe'
MODEL    = 'gemma3:4b'
CHUNK    = 3000  # 1チャンクあたりの文字数
UTC      = timezone.utc

REDUCED.mkdir(parents=True, exist_ok=True)
DONE_DIR.mkdir(parents=True, exist_ok=True)

def ask(prompt):
    r = subprocess.run(
        [str(OLLAMA), 'run', MODEL, prompt],
        capture_output=True, text=True, encoding='utf-8', timeout=120
    )
    return r.stdout.strip()

def chunk_text(text, size=CHUNK):
    return [text[i:i+size] for i in range(0, len(text), size)]

def condense_file(fpath):
    fpath = Path(fpath)
    print(f'[CONDENSE] 処理開始: {fpath.name}')

    raw    = json.load(open(fpath, encoding='utf-8'))
    text   = raw.get('text', '')
    source = raw.get('source', 'unknown')
    url    = raw.get('url', '')

    if not text:
        print(f'[SKIP] テキストなし: {fpath.name}')
        return None

    chunks   = chunk_text(text)
    all_s1   = []
    all_s2   = []
    print(f'[INFO] {len(text)}文字 / {len(chunks)}チャンク')

    for i, chunk in enumerate(chunks):
        print(f'[Step1-{i+1}/{len(chunks)}] 構造抽出中...')
        s1 = ask(f'以下のchat内容から設計・構造・重要な主張を3つ以内で箇条書き抽出せよ。\n\n{chunk}')
        all_s1.append(s1)

        print(f'[Step2-{i+1}/{len(chunks)}] リスク抽出中...')
        s2 = ask(f'以下のchat内容からリスク・問題点・注意点を3つ以内で箇条書き抽出せよ。\n\n{chunk}')
        all_s2.append(s2)

    # 全チャンクの結果を統合
    merged_s1 = '\n'.join(all_s1)
    merged_s2 = '\n'.join(all_s2)

    print('[Step3] 残差確認中...')
    s3 = ask(
        f'以下はStep1とStep2の抽出結果です。\n'
        f'Step1（構造）:\n{merged_s1[:2000]}\n\n'
        f'Step2（リスク）:\n{merged_s2[:2000]}\n\n'
        f'これらに含まれない重要な洞察があれば抽出せよ。なければ「残差なし」と答えよ。\n\n'
        f'原文冒頭:\n{text[:1000]}'
    )

    # REDUCED層に保存
    ts  = datetime.now(UTC).strftime('%Y%m%d_%H%M%S')
    eid = f'ERED_{ts}_{source[:4].upper()}'
    h   = hashlib.sha256(f'{eid}{ts}{merged_s1[:100]}'.encode()).hexdigest()[:16]

    result = {
        'event_id'       : eid,
        'source'         : source,
        'url'            : url,
        'raw_file'       : fpath.name,
        'timestamp'      : ts,
        'original_chars' : len(text),
        'chunks'         : len(chunks),
        'step1_structure': merged_s1,
        'step2_audit'    : merged_s2,
        'step3_residue'  : s3,
        'hash'           : h,
        'status'         : 'REDUCED'
    }

    out = REDUCED / f'{ts}_{eid}.json'
    json.dump(result, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'[OK] REDUCED保存: {out.name}')

    # events.csvに記録
    rows = list(csv.reader(open(EVENTS, encoding='utf-8-sig'))) if EVENTS.exists() else []
    prev = hashlib.sha256(','.join(rows[-1]).encode()).hexdigest()[:16] if rows else 'GENESIS'
    with open(EVENTS, 'a', encoding='utf-8', newline='') as f:
        csv.writer(f).writerow([
            eid, ts, 'condense_worker', 'condense', 'chat_condense',
            'mocka_condense_worker.py', fpath.name, 'worker', 'internal',
            'in_operation', 'normal', 'A', 'infield/REDUCED',
            merged_s1[:100], prev, 'condense_complete', 'REDUCED',
            'local', 'condense_pipeline', 'N/A', 'N/A',
            f'hash={h}|source={source}|chunks={len(chunks)}|chars={len(text)}'
        ])
    print(f'[OK] events.csv記録完了')

    # 処理済みファイルをRAW_DONEに移動
    fpath.rename(DONE_DIR / fpath.name)
    print(f'[OK] RAW_DONEに移動: {fpath.name}')

    return out

def get_unprocessed():
    done_names = {f.name for f in DONE_DIR.glob('*.json')}
    reduced_raws = set()
    for r in REDUCED.glob('*.json'):
        try:
            d = json.load(open(r, encoding='utf-8'))
            reduced_raws.add(d.get('raw_file',''))
        except:
            pass
    files = []
    for f in sorted(RAW_DIR.glob('*.json'), key=lambda x: x.stat().st_mtime):
        if f.name not in done_names and f.name not in reduced_raws:
            files.append(f)
    return files

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--once',  action='store_true', help='未処理を1回処理して終了')
    parser.add_argument('--file',  help='特定ファイルを処理')
    args = parser.parse_args()

    if args.file:
        condense_file(args.file)
        return

    if args.once:
        files = get_unprocessed()
        if not files:
            print('[INFO] 未処理ファイルなし')
            return
        for f in files:
            condense_file(f)
        print(f'[DONE] {len(files)}件処理完了')
        return

    # 常時監視モード
    print('[WORKER] 監視開始... Ctrl+Cで停止')
    while True:
        files = get_unprocessed()
        if files:
            print(f'[WORKER] {len(files)}件の未処理ファイルを発見')
            for f in files:
                condense_file(f)
        else:
            print(f'[WORKER] 待機中... {datetime.now(UTC).strftime("%H:%M:%S")}')
        time.sleep(60)

if __name__ == '__main__':
    main()

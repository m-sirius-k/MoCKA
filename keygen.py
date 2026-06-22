"""
Orchestra License Key Generator v2.0
=====================================
キー形式: OPR-[YYYYMMDD][serial6hex][sig16hex]  (計38文字)
         ONE-[YYYYMMDD][serial6hex][sig16hex]

有効期限ルール:
  新規購入     -> 今日 + 30日
  期限内更新   -> 既存期限 + 30日（損しない設計）
  期限切れ更新 -> 今日 + 30日

使い方:
  python keygen.py pro              # 新規Proキー (今日+30日)
  python keygen.py one              # 新規Oneキー (今日+30日)
  python keygen.py pro 20260630     # 更新: 20260630+30日=20260730
  python keygen.py one 20260630 3   # 更新Oneキー 3枚まとめて発行
  python keygen.py verify OPR-...   # キーの検証・期限確認
"""

import hmac
import hashlib
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

_ORCHESTRA_VK = '1260a44bf996eeb4eb415e2896074709de67ea0f49098db068fa0d5e812a0fdb'
SERIAL_FILE = Path(__file__).parent / 'keygen_serial.json'

def load_serial():
    if SERIAL_FILE.exists():
        return json.loads(SERIAL_FILE.read_text(encoding='utf-8')).get('next_serial', 1)
    return 1

def save_serial(n):
    SERIAL_FILE.write_text(json.dumps({'next_serial': n}), encoding='utf-8')

def next_serial_hex():
    n = load_serial()
    save_serial(n + 1)
    return format(n, '06x').upper()

def calc_expiry(current_expiry_str=None):
    today = datetime.now()
    if current_expiry_str:
        try:
            current_expiry = datetime.strptime(current_expiry_str, '%Y%m%d')
            base = current_expiry if current_expiry > today else today
        except ValueError:
            base = today
    else:
        base = today
    return (base + timedelta(days=30)).strftime('%Y%m%d')

def generate_key(plan, expiry_str):
    plan = plan.lower()
    prefix = 'OPR' if plan == 'pro' else 'ONE' if plan == 'one' else None
    if not prefix:
        raise ValueError(f"未知のプラン: {plan}")
    serial_hex = next_serial_hex()
    msg = (prefix + expiry_str + serial_hex).encode('utf-8')
    secret = _ORCHESTRA_VK.encode('utf-8')
    full_sig = hmac.new(secret, msg, hashlib.sha256).digest()
    sig_hex = full_sig[:8].hex().upper()
    return f"{prefix}-{expiry_str}{serial_hex}{sig_hex}", serial_hex, expiry_str

def verify_key(key):
    k = key.strip().upper()
    if k.startswith('OPR-'):
        prefix, plan = 'OPR', 'pro'
    elif k.startswith('ONE-'):
        prefix, plan = 'ONE', 'one'
    else:
        return {'valid': False, 'reason': '不明なプレフィックス'}
    body = k[4:]
    if len(body) != 30:
        return {'valid': False, 'reason': f'長さ不正: {len(body)}文字 (30文字必要)'}
    expiry_str = body[:8]
    serial_hex = body[8:14]
    sig_hex    = body[14:]
    try:
        expiry_date = datetime.strptime(expiry_str, '%Y%m%d')
    except ValueError:
        return {'valid': False, 'reason': '日付形式不正'}
    msg = (prefix + expiry_str + serial_hex).encode('utf-8')
    secret = _ORCHESTRA_VK.encode('utf-8')
    full_sig = hmac.new(secret, msg, hashlib.sha256).digest()
    expected_sig = full_sig[:8].hex().upper()
    if expected_sig != sig_hex:
        return {'valid': False, 'reason': 'HMAC署名不一致（改ざん検知）'}
    today = datetime.now()
    days_left = (expiry_date - today).days
    return {
        'valid': True, 'plan': plan, 'prefix': prefix,
        'serial': serial_hex, 'expiry': expiry_str,
        'expiry_display': expiry_date.strftime('%Y/%m/%d'),
        'days_left': days_left, 'expired': expiry_date < today,
    }

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    command = sys.argv[1].lower()
    if command == 'verify':
        if len(sys.argv) < 3:
            print("使い方: python keygen.py verify OPR-XXXX...")
            sys.exit(1)
        r = verify_key(sys.argv[2])
        print("\n-- キー検証結果 --")
        if r['valid']:
            status = "期限切れ" if r['expired'] else f"有効 (残{r['days_left']}日)"
            print(f"  プラン  : {r['plan'].upper()}")
            print(f"  シリアル: #{int(r['serial'], 16):06d}")
            print(f"  有効期限: {r['expiry_display']}")
            print(f"  状態    : {status}")
        else:
            print(f"  無効: {r['reason']}")
        print()
        return
    plan = command
    current_expiry = sys.argv[2] if len(sys.argv) >= 3 else None
    count = int(sys.argv[3]) if len(sys.argv) >= 4 else 1
    expiry_str = calc_expiry(current_expiry)
    expiry_display = datetime.strptime(expiry_str, '%Y%m%d').strftime('%Y/%m/%d')
    if current_expiry:
        print(f"\n-- Orchestra License Keys ({plan.upper()}) [更新: {current_expiry} + 30日 = {expiry_str}] --")
    else:
        print(f"\n-- Orchestra License Keys ({plan.upper()}) [新規: 今日+30日 = {expiry_str}] --")
    for i in range(count):
        key, serial, expiry = generate_key(plan, expiry_str)
        print(f"  {i+1:3d}.  {key}  (シリアル #{int(serial, 16):06d} / 期限 {expiry_display})")
    print(f"\n  ユーザー案内: 有効期限 {expiry_display} まで有効です\n")

if __name__ == '__main__':
    main()

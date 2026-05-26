#!/usr/bin/env python3
"""
keygen.py — Relay / Orchestra ライセンスキー手動生成ツール

使い方:
  python keygen.py --product relay   --plan pro   [--secret YOUR_SECRET]
  python keygen.py --product relay   --plan one   [--secret YOUR_SECRET]
  python keygen.py --product orchestra --plan pro [--secret YOUR_SECRET]

--secret を省略した場合は環境変数 RELAY_SECRET / ORCHESTRA_SECRET を使用。
"""

import argparse
import hashlib
import hmac
import os
import secrets
import struct
from datetime import datetime, timedelta

# ── デフォルトシークレット (本番前に環境変数で上書きすること) ──────────────────
DEFAULT_RELAY_SECRET      = 'RELAY_VK_PLACEHOLDER_REPLACE_BEFORE_PRODUCTION_DEPLOY_2026'
DEFAULT_ORCHESTRA_SECRET  = '1260a44bf996eeb4eb415e2896074709de67ea0f49098db068fa0d5e812a0fdb'


def hmac_sign(key_bytes: bytes, message: bytes) -> str:
    """HMAC-SHA256 署名を生成し、先頭8バイトを16進大文字で返す"""
    sig = hmac.new(key_bytes, message, hashlib.sha256).digest()[:8]
    return sig.hex().upper()


def calc_expiry(days: int = 30) -> str:
    """YYYYMMDD 形式で30日後の有効期限を返す"""
    d = datetime.utcnow() + timedelta(days=days)
    return d.strftime('%Y%m%d')


def next_serial() -> str:
    """6桁の疑似シリアル番号 (ランダム、本番ではKV管理が望ましい)"""
    return format(secrets.randbelow(0xFFFFFF), '06X')


def generate_relay_key(plan: str, secret: str) -> dict:
    """
    Relayキーを生成する。
    形式: RLY-P-{YYYYMMDD:8}{serial:6}{sig:16}
          RLY-O-{YYYYMMDD:8}{serial:6}{sig:16}
    """
    assert plan in ('pro', 'one', 'free'), f"Invalid plan: {plan}"
    prefix     = 'RLY-O' if plan == 'one' else 'RLY-P'
    expiry_str = calc_expiry(30)
    serial_hex = next_serial()
    key_bytes  = secret.encode()
    msg        = (prefix + expiry_str + serial_hex).encode()
    sig_hex    = hmac_sign(key_bytes, msg)
    key        = f"{prefix}-{expiry_str}{serial_hex}{sig_hex}"
    expiry_display = f"{expiry_str[:4]}/{expiry_str[4:6]}/{expiry_str[6:8]}"
    return {
        'key':            key,
        'plan':           plan,
        'prefix':         prefix,
        'expiry':         expiry_str,
        'expiry_display': expiry_display,
        'serial':         serial_hex,
    }


def generate_orchestra_key(plan: str, secret: str) -> dict:
    """
    Orchestraキーを生成する (worker.js v2形式)。
    形式: OPR-{YYYYMMDD:8}{serial:6}{sig:16}
          ONE-{YYYYMMDD:8}{serial:6}{sig:16}
    """
    assert plan in ('pro', 'one'), f"Invalid orchestra plan: {plan}"
    prefix     = 'ONE' if plan == 'one' else 'OPR'
    expiry_str = calc_expiry(30)
    serial_hex = next_serial()
    key_bytes  = secret.encode()
    msg        = (prefix + expiry_str + serial_hex).encode()
    sig_hex    = hmac_sign(key_bytes, msg)
    key        = f"{prefix}-{expiry_str}{serial_hex}{sig_hex}"
    expiry_display = f"{expiry_str[:4]}/{expiry_str[4:6]}/{expiry_str[6:8]}"
    return {
        'key':            key,
        'plan':           plan,
        'prefix':         prefix,
        'expiry':         expiry_str,
        'expiry_display': expiry_display,
        'serial':         serial_hex,
    }


def main():
    parser = argparse.ArgumentParser(
        description='Relay / Orchestra ライセンスキー手動生成',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('--product', choices=['relay', 'orchestra'], required=True,
                        help='対象プロダクト')
    parser.add_argument('--plan',    choices=['free', 'pro', 'one'],  required=True,
                        help='プランティア')
    parser.add_argument('--secret',  default=None,
                        help='HMAC署名シークレット (省略時は環境変数を使用)')
    parser.add_argument('--count',   type=int, default=1,
                        help='生成するキー数 (デフォルト: 1)')
    args = parser.parse_args()

    # シークレット解決
    if args.secret:
        secret = args.secret
    elif args.product == 'relay':
        secret = os.environ.get('RELAY_SECRET', DEFAULT_RELAY_SECRET)
        if secret == DEFAULT_RELAY_SECRET:
            print('⚠️  警告: RELAY_SECRET 環境変数が未設定です。プレースホルダーを使用中。')
            print('         本番環境では RELAY_SECRET を設定してください。\n')
    else:
        secret = os.environ.get('ORCHESTRA_SECRET', DEFAULT_ORCHESTRA_SECRET)

    print(f'Product : {args.product}')
    print(f'Plan    : {args.plan}')
    print(f'Count   : {args.count}')
    print('-' * 60)

    for i in range(args.count):
        if args.product == 'relay':
            result = generate_relay_key(args.plan, secret)
        else:
            if args.plan == 'free':
                print('⚠️  Orchestra Free キーは不要です。')
                return
            result = generate_orchestra_key(args.plan, secret)

        print(f'[{i+1:02d}] Key    : {result["key"]}')
        print(f'     Plan   : {result["plan"]}')
        print(f'     Expiry : {result["expiry_display"]}')
        print(f'     Serial : {result["serial"]}')
        if args.count > 1 and i < args.count - 1:
            print()

    print('-' * 60)
    print('✓ 生成完了')


if __name__ == '__main__':
    main()

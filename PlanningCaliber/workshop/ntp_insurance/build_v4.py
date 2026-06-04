import json, collections

with open(r'X:\down\NTP\data\insurers\master_20260604_v3.json', encoding='utf-8') as f:
    d = json.load(f)

d['generated_at'] = '2026-06-04T12:00:00'
d['version'] = '4.0'

c001 = next(c for c in d['companies'] if c['company_id'] == 'C001')

for p in c001['plans']:
    pid = p['plan_id']

    if pid == 'C001_P09':
        p['detail_url'] = 'https://www.metlife.co.jp/products/si/siwl/'
        p['pdf_url'] = 'https://spon.metlife.co.jp/document/products_sp/siwl.pdf'
        p['monthly_premium'] = {
            'M_40_S2': 5854, 'M_40_S3': 8781, 'M_40_S5': 14635,
            'M_40_P1': 3726, 'M_40_P2': 7452,
            'F_40_S2': 4696, 'F_40_S3': 7044, 'F_40_S5': 11740,
            'F_40_P1': 3375, 'F_40_P2': 6750,
            'M_50_S1': 3881, 'M_50_S2': 7762, 'M_50_S3': 11643,
            'M_50_S5': 19405, 'M_50_P1': 5575, 'M_50_P2': 11150,
            'F_50_S2': 5980, 'F_50_S3': 8970, 'F_50_S5': 14950,
            'F_50_P1': 5046, 'F_50_P2': 10092,
            'source_url': 'https://medical.life-direct.jp/smile/hosyo.html',
            'note': 'プラン別（S1/S2/S3/S5/P1/P2）。S2プランを基準に記録。'
        }
        p['conditions'] = {
            'age_min': 30, 'age_max': 80,
            'health_screening': None, 'simplified_告知': False, '告知items': None,
            'plan_variants': ['Sプラン', 'S1プラン', 'S2プラン', 'S3プラン', 'S5プラン', 'P1プラン', 'P2プラン']
        }
        p['tsi'] = 1.0
        p['tsi_status'] = 'TRUSTED'
        p['tsi_log'] = [{'date': '2026-06-04', 'score': 1.0, 'reason': 'Perplexity公式調査・保険料データ補完'}]

    elif pid == 'C001_P10':
        p['detail_url'] = 'https://www.metlife.co.jp/yakkan/provision/lswl/'
        p['pdf_url'] = 'https://spon.metlife.co.jp/document/lswl.pdf'
        p['discontinued'] = True
        p['discontinued_date'] = '2025-04-01'
        p['monthly_premium'] = {
            'M_30_5000': None, 'M_40_5000': None, 'M_50_5000': None,
            'F_30_5000': None, 'F_40_5000': None, 'F_50_5000': None,
            'M_30_10000': None, 'M_40_10000': None, 'M_50_10000': None,
            'F_30_10000': None, 'F_40_10000': None, 'F_50_10000': None,
            'M_40_1000man': 44490,
            'source_url': 'https://www.metlife.co.jp/yakkan/provision/lswl/',
            'note': '40歳男性・死亡1000万円・三大疾病払込免除なし。2025年4月販売停止'
        }
        p['conditions'] = {
            'age_min': 20, 'age_max': 70,
            'health_screening': None, 'simplified_告知': False, '告知items': None
        }
        p['tsi'] = 0.0
        p['tsi_status'] = 'DEAD'
        p['tsi_log'] = [
            {'date': '2026-06-04', 'score': 1.0, 'reason': 'Googleシート登録'},
            {'date': '2026-06-04', 'score': -1.0, 'reason': '2025年4月1日販売停止（公式確認済み）'}
        ]

    elif pid == 'C001_P11':
        p['detail_url'] = 'https://www.metlife.co.jp/products/life/'
        p['pdf_url'] = 'https://www.metlife.co.jp/giq/pdf_dl.do?x=d7'
        p['monthly_premium'] = {
            'M_30_5000': None, 'M_40_5000': None, 'M_50_5000': None,
            'F_30_5000': None, 'F_40_5000': None, 'F_50_5000': None,
            'M_30_10000': None, 'M_40_10000': None, 'M_50_10000': None,
            'F_30_10000': None, 'F_40_10000': None, 'F_50_10000': None,
            'source_url': None,
            'note': '対面販売のみ。公式サイトに保険料例非公開'
        }
        p['conditions'] = {
            'age_min': None, 'age_max': None,
            'health_screening': None, 'simplified_告知': False, '告知items': None
        }
        p['tsi'] = 0.8
        p['tsi_status'] = 'WARNING'
        p['tsi_log'] = [{'date': '2026-06-04', 'score': 0.8, 'reason': '対面販売専用・保険料データ非公開'}]

    elif pid == 'C001_P12':
        p['detail_url'] = 'https://www.metlife.co.jp/products/life/'
        p['monthly_premium'] = {
            'M_30_5000': None, 'M_40_5000': None, 'M_50_5000': None,
            'F_30_5000': None, 'F_40_5000': None, 'F_50_5000': None,
            'M_30_10000': None, 'M_40_10000': None, 'M_50_10000': None,
            'F_30_10000': None, 'F_40_10000': None, 'F_50_10000': None,
            'M_35_1000man_60sai': 39730,
            'source_url': 'https://www.metlife.co.jp/products/life/',
            'note': '35歳男性・死亡1000万・60歳満期・返戻率83%（パンフ参考値）。標準保険料表は非公開'
        }
        p['conditions'] = {
            'age_min': 18, 'age_max': 55,
            'health_screening': None, 'simplified_告知': False, '告知items': None
        }
        p['coverage'] = {
            'death': True, 'maturity_benefit': True, 'asset_formation': True,
            'no_surrender_value': False,
            'maturity_refund_rate': 0.83,
            'maturity_refund_note': '35歳・60歳満期の参考値'
        }
        p['tsi'] = 0.9
        p['tsi_status'] = 'TRUSTED'
        p['tsi_log'] = [{'date': '2026-06-04', 'score': 0.9, 'reason': '参考値のみ・正確な保険料表は非公開'}]

    elif pid == 'C001_P13':
        p['detail_url'] = 'https://www.metlife.co.jp/products/medical/'
        p['yakkan_url'] = 'https://www.metlife.co.jp/yakkan/provision/ropfih/'
        p['pdf_url'] = 'https://spon.metlife.co.jp/document/ropfihwl.pdf'
        p['monthly_premium'] = {
            'M_30_5000': 14805, 'M_40_5000': None, 'M_50_5000': None,
            'F_30_5000': 16225, 'F_40_5000': None, 'F_50_5000': None,
            'M_30_10000': None, 'M_40_10000': None, 'M_50_10000': None,
            'F_30_10000': None, 'F_40_10000': None, 'F_50_10000': None,
            'source_url': 'https://www.metlife.co.jp/yakkan/provision/ropfih/',
            'note': 'Ⅰ型5口・60歳払済・入院日額5,000円基準。生存還付給付金算定期間・繰延期間により変動あり'
        }
        p['conditions'] = {
            'age_min': 20, 'age_max': 60,
            'health_screening': None, 'simplified_告知': False, '告知items': None,
            'payment_period_options': ['55歳払済', '60歳払済', '65歳払済', '70歳払済', '75歳払済', '80歳払済', '85歳払済']
        }
        p['coverage'] = {
            'hospitalization_daily': True, 'surgery_benefit': None,
            'advanced_medical': None, 'health_return': True,
            'return_bonus': True,
            'return_bonus_note': '生存還付給付金あり（算定期間・繰延期間設定型）',
            'death': None, 'nursing_care': False,
            'asset_formation': False, 'no_surrender_value': None
        }
        p['tsi'] = 1.0
        p['tsi_status'] = 'TRUSTED'
        p['tsi_log'] = [{'date': '2026-06-04', 'score': 1.0, 'reason': 'Perplexity公式調査・保険料データ補完'}]

    elif pid == 'C001_P14':
        p['detail_url'] = 'https://www.metlife.co.jp/products/cancer/cx2/'
        p['detail_url2'] = 'https://www.metlife.co.jp/products/cancer/cx2/detail/'
        p['pdf_url'] = 'https://spon.metlife.co.jp/document/cx2.pdf'
        p['monthly_premium'] = {
            'plans': {
                '基本プラン': {
                    'M_30': 1671, 'F_30': 2279,
                    'M_40': 2197, 'F_40': 2856,
                    'M_50': 3162, 'F_50': 3287
                },
                '診断給付プラン': {
                    'M_30': 2836, 'F_30': 3569,
                    'M_40': 4022, 'F_40': 4606,
                    'M_50': 6212, 'F_50': 5527
                },
                '保障充実プラン': {
                    'M_30': 6311,  'F_30': 8619,
                    'M_40': 8757,  'F_40': 10731,
                    'M_50': 12952, 'F_50': 11982
                },
                '女性充実プラン': {
                    'M_30': None, 'F_30': 3664,
                    'M_40': None, 'F_40': 4621,
                    'M_50': None, 'F_50': 5312
                }
            },
            'source_url': 'https://www.metlife.co.jp/products/cancer/cx2/',
            'source_url2': 'https://medical.life-direct.jp/guard/hosyo.html',
            'note': '非喫煙保険料率・終身払基準。喫煙率あり。'
        }
        p['conditions'] = {
            'age_min': None, 'age_max': 70,
            'health_screening': None, 'simplified_告知': False, '告知items': None,
            'smoker_rate_available': True, 'non_smoker_rate': True,
            'age_max_note': '参考値（公式明記なし）'
        }
        p['coverage'] = {
            'cancer_lump_sum': True, 'hospitalization_daily': None,
            'surgery_benefit': None, 'advanced_medical': None,
            'death': None, 'nursing_care': False,
            'asset_formation': False, 'no_surrender_value': None
        }
        p['tsi'] = 1.0
        p['tsi_status'] = 'TRUSTED'
        p['tsi_log'] = [{'date': '2026-06-04', 'score': 1.0, 'reason': 'Perplexity公式調査・全プラン保険料補完'}]

with open(r'X:\down\NTP\data\insurers\master_20260604_v4.json', 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

print('生成完了')

# バリデーション
pids = [p['plan_id'] for c in d['companies'] for p in c['plans']]
dup = [k for k, v in collections.Counter(pids).items() if v > 1]
no_tsi = [(c['company_id'], p['plan_id']) for c in d['companies'] for p in c['plans'] if 'tsi' not in p]
dead = [(c['company_id'], p['plan_id'], p.get('discontinued'), p.get('tsi_status')) for c in d['companies'] for p in c['plans'] if p.get('tsi_status') == 'DEAD']
total_h = d['total_products']
total_a = len(pids)
print(f'total_products: header={total_h} / 実数={total_a} / {"OK" if total_h == total_a else "MISMATCH"}')
print(f'plan_id重複: {"なし OK" if not dup else dup}')
print(f'TSI欠損: {"なし OK" if not no_tsi else no_tsi}')
print(f'DEAD商品: {dead}')

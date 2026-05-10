# -*- coding: utf-8 -*-
"""
MoCKA Text-to-5W1H Parser v1.0
入力テキストを5W1H構造に自動分解する

設計思想:
- 単語の出現率ではなく「誰が・何を・どこで・いつ・なぜ・どうした」の構造で照合
- Janomeで品詞分解 → 役割推定 → 5W1Hにマッピング
- events.dbの既存5W1Hカラムと照合可能な形式で出力

使い方:
  python text_to_5w1h.py "テキストをここに入れる"
  または import して parse(text) を呼ぶ
"""
import sys, re, json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# ===== WHO辞書 — 既知のアクター =====
WHO_MAP = {
    # AI
    'claude':   'Claude', 'クロード': 'Claude',
    'gpt':      'GPT',    'chatgpt': 'GPT',
    'gemini':   'Gemini', 'ジェミニ': 'Gemini',
    'copilot':  'Copilot','コパイロット': 'Copilot',
    'perplexity': 'Perplexity',
    'ai':       'AI',
    # 人間
    'きむら':   'きむら博士', '博士': 'きむら博士',
    'sirok':    'きむら博士',
    # システム
    'mocka':    'MoCKA', 'mcp':    'MoCKA_MCP',
    'caliber':  'Caliber', 'app':  'app.py',
    'chrome':   'Chrome拡張',
}

# ===== WHERE辞書 — 既知の場所/コンポーネント =====
WHERE_MAP = {
    'events.db': 'events.db', 'sqlite': 'SQLite',
    'app.py': 'app.py', 'command center': 'COMMAND_CENTER',
    'github': 'GitHub', 'git': 'Git',
    'overleaf': 'Overleaf', 'easychair': 'EasyChair',
    'firestore': 'Firestore', 'firebase': 'Firebase',
    'powershell': 'PowerShell', 'python': 'Python',
    'x:\\': 'X_drive', 'c:\\': 'C_drive', 'a:\\': 'A_drive',
    'localhost': 'localhost', 'ngrok': 'ngrok',
    'interface': 'interface/', 'data': 'data/',
    'essence': 'essence', 'phl': 'PHL',
    'caliber_server': 'Caliber_server',
}

# ===== WHAT辞書 — 操作の種類 =====
WHAT_MAP = {
    # ファイル操作
    '保存': 'file_save', '書き込': 'file_write', '編集': 'file_edit',
    '削除': 'file_delete', 'コピー': 'file_copy', '移動': 'file_move',
    '作成': 'file_create', '生成': 'generate',
    # 実行
    '実行': 'execute', '起動': 'start', '停止': 'stop',
    '再起動': 'restart', 'インストール': 'install',
    # 記録
    '記録': 'record', '登録': 'register', '投入': 'import',
    '抽出': 'extract', '取得': 'fetch',
    # 修正
    '修正': 'fix', '更新': 'update', '変更': 'change',
    '修復': 'repair', '解消': 'resolve',
    # 確認
    '確認': 'verify', 'チェック': 'check', '検証': 'validate',
    # エラー系
    'エラー': 'error', '失敗': 'failure', '文字化け': 'encoding_error',
    'インシデント': 'incident', '再発': 'recurrence',
    # 成功系
    '完了': 'complete', '成功': 'success', '達成': 'achieve',
    '稼働': 'running', '正常': 'normal',
}

# ===== HOW辞書 — 手段・方法 =====
HOW_MAP = {
    'python': 'Python_script', 'powershell': 'PowerShell',
    'bash': 'bash', 'git': 'git_command',
    'mcp': 'MCP_tool', 'api': 'API_call',
    'スクリプト': 'script', '手動': 'manual',
    'chrome拡張': 'Chrome_extension', '自動': 'auto',
    'sqliteで': 'SQLite_direct', 'curl': 'curl',
}

# ===== WHY辞書 — 目的・理由 =====
WHY_MAP = {
    '制度': 'institution', '記録': 'record_keeping',
    '修正': 'bug_fix', '改善': 'improvement',
    '確認': 'verification', '証明': 'proof',
    '投入': 'data_import', '昇華': 'elevation',
    '論文': 'paper', '提出': 'submission',
    'テスト': 'testing', '実験': 'experiment',
    'バグ': 'bug_fix', 'インシデント': 'incident_response',
    '予防': 'prevention', '再発防止': 'recurrence_prevention',
}

def parse(text, verbose=True):
    """
    テキストを5W1H構造に分解する
    
    Returns:
        dict: {
            'who': str,
            'what': str,
            'where': str,
            'when': str,
            'why': str,
            'how': str,
            'raw_tokens': list,
            'confidence': dict,  # 各軸の確信度(0-1)
        }
    """
    text_lower = text.lower()
    
    result = {
        'who':   None,
        'what':  None,
        'where': None,
        'when':  None,
        'why':   None,
        'how':   None,
        'raw_tokens': [],
        'confidence': {},
    }
    
    # === WHO検出 ===
    for key, val in WHO_MAP.items():
        if key in text_lower:
            result['who'] = val
            result['confidence']['who'] = 0.9
            break
    # デフォルト: 主語が明示されていない場合はClaudeと推定
    if not result['who']:
        result['who'] = 'Claude'
        result['confidence']['who'] = 0.4

    # === WHERE検出 ===
    for key, val in WHERE_MAP.items():
        if key in text_lower:
            result['where'] = val
            result['confidence']['where'] = 0.8
            break
    # パス形式を検出
    path_match = re.search(r'[A-Za-z]:\\[^\s]+', text)
    if path_match and not result['where']:
        result['where'] = path_match.group(0)[:50]
        result['confidence']['where'] = 0.95

    # === WHAT検出 ===
    for key, val in WHAT_MAP.items():
        if key in text:
            result['what'] = val
            result['confidence']['what'] = 0.85
            break

    # === HOW検出 ===
    for key, val in HOW_MAP.items():
        if key in text_lower:
            result['how'] = val
            result['confidence']['how'] = 0.85
            break

    # === WHY検出 ===
    # 「〜のため」「〜するため」「〜のために」パターン
    why_match = re.search(r'(.{2,15})(のため|するため|ために|目的|理由)', text)
    if why_match:
        result['why'] = why_match.group(1)[:30]
        result['confidence']['why'] = 0.7
    else:
        for key, val in WHY_MAP.items():
            if key in text:
                result['why'] = val
                result['confidence']['why'] = 0.5
                break

    # === WHEN検出 ===
    when_match = re.search(r'(\d{4}-\d{2}-\d{2}|\d{1,2}月\d{1,2}日|今日|本日|昨日)', text)
    if when_match:
        result['when'] = when_match.group(0)
        result['confidence']['when'] = 0.9

    # === Janomeで補完 ===
    try:
        from janome.tokenizer import Tokenizer
        t = Tokenizer()
        VALID_POS = {'名詞','動詞','形容詞'}
        SKIP = {'する','ある','いる','なる','れる','させる','ます','です',
                'ない','て','し','た','を','は','が','に','で','と','も'}
        tokens = []
        for tok in t.tokenize(text):
            pos = tok.part_of_speech.split(',')[0]
            surface = tok.surface.strip()
            if pos in VALID_POS and surface not in SKIP and len(surface) > 1:
                tokens.append({'surface': surface, 'pos': pos, 'base': tok.base_form})
        result['raw_tokens'] = tokens

        # 動詞をHOWに補完
        verbs = [t['surface'] for t in tokens if t['pos'] == '動詞']
        if verbs and not result['how']:
            result['how'] = verbs[0]
            result['confidence']['how'] = 0.4

        # 名詞をWHATに補完
        nouns = [t['surface'] for t in tokens if t['pos'] == '名詞']
        if nouns and not result['what']:
            result['what'] = nouns[0]
            result['confidence']['what'] = 0.3

    except ImportError:
        pass

    # === 確信度の平均 ===
    conf_values = list(result['confidence'].values())
    result['overall_confidence'] = round(sum(conf_values)/len(conf_values), 2) if conf_values else 0

    if verbose:
        print(f"\n{'='*60}")
        print(f"【Text-to-5W1H Parser v1.0】")
        print(f"{'='*60}")
        print(f"入力: {text}")
        print(f"{'─'*60}")
        print(f"  WHO  (誰が):   {result['who']}  (確信度:{result['confidence'].get('who',0):.0%})")
        print(f"  WHAT (何を):   {result['what']}  (確信度:{result['confidence'].get('what',0):.0%})")
        print(f"  WHERE(どこで): {result['where']}  (確信度:{result['confidence'].get('where',0):.0%})")
        print(f"  WHEN (いつ):   {result['when']}  (確信度:{result['confidence'].get('when',0):.0%})")
        print(f"  WHY  (なぜ):   {result['why']}  (確信度:{result['confidence'].get('why',0):.0%})")
        print(f"  HOW  (どうやって): {result['how']}  (確信度:{result['confidence'].get('how',0):.0%})")
        print(f"  総合確信度: {result['overall_confidence']:.0%}")
        if result['raw_tokens']:
            surfaces = [t['surface'] for t in result['raw_tokens']]
            print(f"  形態素: {surfaces[:10]}")
        print(f"{'='*60}")

    return result


if __name__ == '__main__':
    if len(sys.argv) > 1:
        text = ' '.join(sys.argv[1:])
        parse(text)
    else:
        tests = [
            "PowerShellでファイルを編集します",
            "Pythonスクリプトで修正完了しました",
            "文字化けが発生してエラーになりました",
            "ClaudeがMCPでevents.dbにイベントを記録するため投入しました",
            "きむら博士がPowerShellではなくPythonで書き直すよう指摘した",
        ]
        for t in tests:
            parse(t)
            print()

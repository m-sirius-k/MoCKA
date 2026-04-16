# =========================
# FILE: runtime\run_save.py
# =========================
from save_engine import save_section, save_partial, save_incident

# NOTE: セクション保存（ここを書き換えれば自由に保存できる）
save_section(
"""第1章〜第7章
MoCKAは進化・記憶・観測・創発まで完成
次フェーズ：Intent Layer""",
"MoCKA状態引き継ぎ"
)

# NOTE: 部分保存
save_partial(
"Intent Layer導入",
"重要メモ"
)

# NOTE: インシデント保存
save_incident(
{
    "what": "PowerShellでPythonコード直接実行",
    "why": "実行方法誤り",
    "fix": "必ず.pyファイルで実行"
},
"実行ミス"
)

print("SAVE COMPLETE")

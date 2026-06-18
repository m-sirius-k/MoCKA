import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
"""
MoCKA Encoding Policy Validator
================================
Rule 1: AIはUTF-8以外のエンコーディングを明示的に指定してはならない。
Rule 2: 生成するスクリプトはEncoding Policy Validatorを通過しなければならない。
Rule 3: Encoding違反は制度違反インシデントとして記録し、再発防止策を伴ってクローズ。

使い方:
  from encoding_policy_validator import validate, safe_write

  # スクリプト文字列を検査
  result = validate(script_text)
  if not result["pass"]:
      raise EncodingPolicyViolation(result)

  # 安全な書き出し（UTF-8強制）
  safe_write(path, content)
"""

import re
import sys
import json
import datetime
from pathlib import Path

# ============================================================
# Policy定義
# ============================================================

POLICY = {
    "default_encoding": "UTF-8",
    "allow": ["UTF-8", "utf-8", "utf_8", "utf-8-sig"],
    "deny_patterns": [
        # CP932 / Shift-JIS 系
        (r"GetEncoding\s*\(\s*['\"]?932['\"]?\s*\)",        "CP932指定: GetEncoding(932)"),
        (r"GetEncoding\s*\(\s*['\"]cp932['\"]?\s*\)",        "CP932指定: GetEncoding('cp932')"),
        (r"GetEncoding\s*\(\s*['\"]shift.?jis['\"]?\s*\)",   "Shift-JIS指定"),
        (r"-Encoding\s+Default\b",                           "PowerShell -Encoding Default"),
        (r"-Encoding\s+OEM\b",                               "PowerShell -Encoding OEM"),
        (r"-Encoding\s+String\b",                            "PowerShell -Encoding String"),
        (r"Out-File(?!\s+-Encoding\s+UTF)",                  "Out-File (UTF8未指定の可能性)"),
        (r"Set-Content(?!\s+-Encoding\s+UTF)",               "Set-Content (UTF8未指定の可能性)"),
        # Python encoding省略 or 非UTF-8
        (r"open\s*\([^)]+encoding\s*=\s*['\"]cp932['\"]",   "Python open encoding=cp932"),
        (r"open\s*\([^)]+encoding\s*=\s*['\"]shift.jis['\"]","Python open encoding=shift-jis"),
    ]
}

# ============================================================
# 例外クラス
# ============================================================

class EncodingPolicyViolation(Exception):
    def __init__(self, result: dict):
        self.result = result
        super().__init__(f"Encoding Policy Violation: {result['violations']}")

# ============================================================
# Validator本体
# ============================================================

def validate(script: str, source_hint: str = "") -> dict:
    """
    スクリプト文字列を検査する。
    戻り値: {"pass": bool, "violations": [...], "source": str}
    """
    violations = []
    for pattern, label in POLICY["deny_patterns"]:
        matches = re.findall(pattern, script, re.IGNORECASE)
        if matches:
            violations.append({
                "label":   label,
                "pattern": pattern,
                "matches": matches[:3],
            })

    result = {
        "pass":       len(violations) == 0,
        "violations": violations,
        "source":     source_hint,
        "checked_at": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    return result


def validate_or_raise(script: str, source_hint: str = "") -> dict:
    """違反があればEncodingPolicyViolationを送出する。"""
    result = validate(script, source_hint)
    if not result["pass"]:
        _write_incident(result)
        raise EncodingPolicyViolation(result)
    return result


# ============================================================
# 安全な書き出し（UTF-8強制）
# ============================================================

def safe_write(path: str | Path, content: str, validate_content: bool = True) -> None:
    """
    UTF-8でファイルを書き出す。
    validate_content=True の場合、内容をポリシー検査してから書き出す。
    """
    if validate_content:
        result = validate(content, source_hint=str(path))
        if not result["pass"]:
            _write_incident(result)
            raise EncodingPolicyViolation(result)

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


# ============================================================
# インシデント自動記録
# ============================================================

INCIDENT_LOG = Path(r"C:\Users\sirok\MoCKA\data\mocka\encoding_violations.jsonl")

def _write_incident(result: dict) -> None:
    """Encoding Policy違反をインシデントログに記録する。"""
    try:
        INCIDENT_LOG.parent.mkdir(parents=True, exist_ok=True)
        incident = {
            "event_type":  "ENCODING_POLICY_VIOLATION",
            "severity":    "HIGH",
            "category":    "Encoding Policy Violation",
            "when":        result["checked_at"],
            "source":      result["source"],
            "violations":  result["violations"],
            "note":        "UTF-8以外の保存経路を検知。CHANGE_DONE禁止。再発防止策を伴ってクローズすること。",
        }
        with open(INCIDENT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(incident, ensure_ascii=False) + "\n")
        print(f"[ENCODING POLICY] INCIDENT記録: {INCIDENT_LOG}", file=sys.stderr)
    except Exception as e:
        print(f"[ENCODING POLICY] インシデント記録失敗: {e}", file=sys.stderr)


# ============================================================
# PowerShell生成ヘルパー（UTF-8強制テンプレート）
# ============================================================

def powershell_write_utf8(filepath: str, content: str) -> str:
    """
    UTF-8でファイルを書き出すPowerShellコマンドを生成する。
    このヘルパーを経由することでCP932生成を制度的に防止する。
    """
    # 内容にシングルクォートがあれば二重化（PowerShell here-string対策）
    safe_content = content.replace("'", "''")
    cmd = f"""[System.IO.File]::WriteAllText(
  '{filepath}',
  (@'
{content}
'@),
  [System.Text.Encoding]::UTF8
)"""
    # 生成したコマンド自体を検査
    result = validate(cmd, source_hint=f"powershell_write_utf8({filepath})")
    if not result["pass"]:
        raise EncodingPolicyViolation(result)
    return cmd


# ============================================================
# CLI: ファイルを検査する
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python encoding_policy_validator.py <ファイルパス>")
        sys.exit(1)

    target = Path(sys.argv[1])
    if not target.exists():
        print(f"[ERROR] ファイルが見つかりません: {target}")
        sys.exit(1)

    with open(target, encoding="utf-8", errors="replace") as f:
        content = f.read()

    result = validate(content, source_hint=str(target))

    if result["pass"]:
        print(f"[PASS] Encoding Policy: 違反なし — {target}")
    else:
        print(f"[FAIL] Encoding Policy違反 — {target}")
        for v in result["violations"]:
            print(f"  ✗ {v['label']}")
            for m in v["matches"]:
                print(f"    → {m}")
        sys.exit(1)

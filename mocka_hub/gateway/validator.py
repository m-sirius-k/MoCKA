"""
MoCKA Institution Gateway Hub -- Input Validator
=================================================
Author : Claude (R02) + GPT (R01)
Date   : 2026-07-22
Purpose: AI からの入力を MoCKA に流す前に検証・サニタイズする

Flow:
  AI output
      |
  Validator  <- PII除去 / 機密情報除去 / 形式チェック
      |
  MoCKA Core
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ValidationResult:
    valid: bool
    sanitized: Optional[str]
    errors: list[str]
    warnings: list[str]


class InputValidator:
    """
    AI からの入力を MoCKA Event 形式に変換する前に検証する。
    """

    # 検出すべき機密パターン (正規表現)
    SECRET_PATTERNS = [
        (r"secret_[a-zA-Z0-9_]{20,}", "Notion API token detected"),
        (r"sk-[a-zA-Z0-9]{40,}", "OpenAI API key detected"),
        (r"ghp_[a-zA-Z0-9]{36}", "GitHub token detected"),
        (r"AIza[a-zA-Z0-9_\-]{35}", "Google API key detected"),
    ]

    # MoCKA Event の必須フィールド
    REQUIRED_FIELDS = ["what_type", "short_summary"]

    def validate(self, payload: dict) -> ValidationResult:
        errors = []
        warnings = []

        # 必須フィールドチェック
        for field in self.REQUIRED_FIELDS:
            if field not in payload:
                errors.append(f"Missing required field: {field}")

        # 機密情報チェック
        payload_str = str(payload)
        for pattern, message in self.SECRET_PATTERNS:
            if re.search(pattern, payload_str):
                errors.append(f"Secret detected: {message}")

        # サニタイズ (エラーがない場合のみ)
        sanitized = None
        if not errors:
            sanitized = self._sanitize(payload)

        return ValidationResult(
            valid=len(errors) == 0,
            sanitized=sanitized,
            errors=errors,
            warnings=warnings,
        )

    def _sanitize(self, payload: dict) -> str:
        """
        payload を MoCKA Event 登録用の文字列に変換する。
        CP932禁止 / UTF-8厳守。
        """
        import json
        return json.dumps(payload, ensure_ascii=False)


# TODO (くろこ): AI Adapter からの出力をここに通す
# TODO (くろこ): PII 除去ロジックを追加する
# TODO (くろこ): mocka_check_utf8 と連携する

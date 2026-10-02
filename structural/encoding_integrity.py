"""
GL12: Encoding Integrity Engine

Verifies that Decision Ledger and related files are valid UTF-8 encoded.
Responsibilities:
  1. Validate file encoding is UTF-8
  2. Detect and reject BOM (Byte Order Mark)
  3. Implement fallback encoding strategy (UTF-8-SIG, CP932)
  4. Ensure all lines are valid JSON parseable
"""

import chardet
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class GL12Result:
    """GL12 encoding verification result"""
    allowed: bool
    encoding: Optional[str] = None
    has_bom: bool = False
    error_message: Optional[str] = None
    failure_reason: Optional[str] = None
    failure_code: str = "GL12_OK"


class EncodingIntegrityEngine:
    """
    GL12 Engine: Encoding Integrity

    Ensures Decision Ledger and critical files maintain UTF-8 encoding.
    Detects encoding errors and implements graceful fallback strategy.
    """

    # File encoding requirements
    REQUIRED_ENCODING = "utf-8"

    # Forbidden encodings (too strict/error-prone)
    FORBIDDEN_ENCODINGS = {"utf-16", "utf-32"}

    # Fallback encoding chain (try in order)
    FALLBACK_ENCODINGS = ["utf-8-sig", "cp932", "iso-8859-1"]

    def verify_file_encoding(self, filepath: str) -> GL12Result:
        """
        Verify that a file is properly UTF-8 encoded.

        Args:
            filepath: Path to file to verify

        Returns:
            GL12Result with allow/deny decision
        """
        try:
            path = Path(filepath)

            if not path.exists():
                return GL12Result(
                    allowed=False,
                    failure_reason=f"File does not exist: {filepath}",
                    failure_code="GL12_FAIL_1_FILE_NOT_FOUND"
                )

            # Read file as bytes
            raw_bytes = path.read_bytes()

            if not raw_bytes:
                # Empty files are OK
                return GL12Result(
                    allowed=True,
                    encoding="utf-8",
                    failure_code="GL12_OK"
                )

            # Check for BOM (forbidden in UTF-8)
            has_bom = self._check_bom(raw_bytes)

            if has_bom:
                return GL12Result(
                    allowed=False,
                    has_bom=True,
                    failure_reason="File has BOM (Byte Order Mark) - forbidden in UTF-8",
                    failure_code="GL12_FAIL_2_BOM_PRESENT"
                )

            # Try to decode as UTF-8
            try:
                raw_bytes.decode("utf-8")

                return GL12Result(
                    allowed=True,
                    encoding="utf-8",
                    failure_code="GL12_OK"
                )

            except UnicodeDecodeError as e:
                # UTF-8 decode failed, try fallback encodings
                fallback_encoding = self._try_fallback_encodings(raw_bytes)

                if fallback_encoding:
                    # Fallback succeeded
                    return GL12Result(
                        allowed=False,
                        encoding=fallback_encoding,
                        failure_reason=f"File encoded in {fallback_encoding}, not UTF-8. Decode error: {str(e)[:100]}",
                        failure_code="GL12_FAIL_3_DECODE_ERROR_FALLBACK_USED"
                    )
                else:
                    # All fallbacks failed
                    return GL12Result(
                        allowed=False,
                        encoding=None,
                        error_message=str(e),
                        failure_reason="File encoding is not UTF-8 or any supported fallback",
                        failure_code="GL12_FAIL_4_ENCODING_UNRECOVERABLE"
                    )

        except Exception as e:
            return GL12Result(
                allowed=False,
                error_message=str(e),
                failure_reason=f"Unexpected error during encoding check: {str(e)}",
                failure_code="GL12_FAIL_5_UNEXPECTED_ERROR"
            )

    def _check_bom(self, data: bytes) -> bool:
        """
        Check if byte stream has Byte Order Mark.

        Args:
            data: Raw bytes to check

        Returns:
            True if BOM detected, False otherwise
        """
        # UTF-8 BOM
        if data.startswith(b'\xef\xbb\xbf'):
            return True

        # UTF-16 BE BOM
        if data.startswith(b'\xfe\xff'):
            return True

        # UTF-16 LE BOM
        if data.startswith(b'\xff\xfe'):
            return True

        return False

    def _try_fallback_encodings(self, data: bytes) -> Optional[str]:
        """
        Try to decode with fallback encodings.

        Args:
            data: Raw bytes to decode

        Returns:
            Encoding name that worked, or None if all failed
        """
        for encoding in self.FALLBACK_ENCODINGS:
            try:
                data.decode(encoding)
                return encoding
            except (UnicodeDecodeError, LookupError):
                continue

        return None

    def detect_encoding(self, filepath: str) -> Optional[str]:
        """
        Detect file encoding using chardet library.

        Args:
            filepath: Path to file

        Returns:
            Detected encoding name or None
        """
        try:
            path = Path(filepath)
            raw_bytes = path.read_bytes()

            detection = chardet.detect(raw_bytes)
            return detection.get("encoding") if detection else None

        except Exception:
            return None

    def validate_jsonl_encoding(self, filepath: str) -> GL12Result:
        """
        Validate that a JSONL file is properly encoded and parseable.

        Args:
            filepath: Path to JSONL file

        Returns:
            GL12Result with validation status
        """
        # First check basic encoding
        encoding_result = self.verify_file_encoding(filepath)

        if not encoding_result.allowed:
            return encoding_result

        # Then check that all lines are valid JSON
        try:
            path = Path(filepath)

            with open(path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        import json
                        json.loads(line)
                    except json.JSONDecodeError as e:
                        return GL12Result(
                            allowed=False,
                            encoding="utf-8",
                            failure_reason=f"Line {line_num} is not valid JSON: {str(e)[:100]}",
                            failure_code="GL12_FAIL_6_INVALID_JSON_LINE"
                        )

        except Exception as e:
            return GL12Result(
                allowed=False,
                failure_reason=f"Error reading JSONL file: {str(e)}",
                failure_code="GL12_FAIL_7_JSONL_READ_ERROR"
            )

        # All checks passed
        return GL12Result(
            allowed=True,
            encoding="utf-8",
            failure_code="GL12_OK"
        )

    def convert_to_utf8(self, filepath: str, backup: bool = True) -> bool:
        """
        Convert file to UTF-8 encoding (remove BOM, convert from other encodings).

        Args:
            filepath: Path to file
            backup: Whether to create backup before conversion

        Returns:
            True if conversion successful
        """
        try:
            path = Path(filepath)

            # Create backup if requested
            if backup:
                backup_path = path.with_suffix(path.suffix + ".bak")
                backup_path.write_bytes(path.read_bytes())

            # Read with fallback strategy
            raw_bytes = path.read_bytes()

            # Try UTF-8 first
            try:
                content = raw_bytes.decode("utf-8")
            except UnicodeDecodeError:
                # Try fallbacks
                content = None
                for encoding in self.FALLBACK_ENCODINGS:
                    try:
                        content = raw_bytes.decode(encoding)
                        break
                    except (UnicodeDecodeError, LookupError):
                        continue

                if content is None:
                    return False

            # Write back as UTF-8 (no BOM)
            path.write_text(content, encoding="utf-8")
            return True

        except Exception:
            return False


# Singleton instance
_gl12_engine = None


def get_gl12_engine() -> EncodingIntegrityEngine:
    """Get or create GL12 engine singleton"""
    global _gl12_engine
    if _gl12_engine is None:
        _gl12_engine = EncodingIntegrityEngine()
    return _gl12_engine

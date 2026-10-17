"""
phi_os/context: 握りつぶされた例外の可視化（HG承認 2026-10-17）。

例外を握りつぶして処理を続ける箇所は、必ず log_drop() を経由して
WARNING ログを残す。制御フロー（戻り値・再試行・例外の扱い）は変更しない。
"""
import logging

logger = logging.getLogger("phi_os.context")


def log_drop(site: str, exc: BaseException) -> None:
    logger.warning("DROPPED[%s]: %s: %s", site, type(exc).__name__, exc)

"""
MoCKA 3.0 — Governance Layer 1 (GL1)
repository_policy.py

責務:
  Repository Groundingより先に確認する固定ルール。
  Repositoryの状態に依存しない制度原則。
"""

REPOSITORY_POLICY = {
    "encoding":        "UTF-8 mandatory",   # CP932禁止
    "version_control": "Git required",      # コミットなき変更禁止
    "file_write":      "No overwrite",      # 上書き前にdiff確認必須
    "new_folder":      "No new folder",     # 存在確認なしのフォルダ生成禁止
    "path_decision":   "Grounding first",   # パス決定はGrounding後
    "human_query":     "Repository first",  # Repositoryにある情報は人に聞かない
}


def get_policy() -> dict:
    return dict(REPOSITORY_POLICY)


def confirm_policy() -> list:
    """全項目をCONFIRMED状態のリストとして返す（Bootstrap Report用）。"""
    return [f"{k}: {v}" for k, v in REPOSITORY_POLICY.items()]

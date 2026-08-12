"""
Test TODO_363: Verify incident_engine.py and incident_git_sync.py
properly exclude Core System Files from git commits.
"""
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Setup path
TEST_DIR = Path(__file__).resolve().parent
ROOT_DIR = TEST_DIR.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "governance"))

from governance.mocka_git_safe_commit import is_core_system_file


class TestIncidentGitSafety:
    """Verify Core System File exclusion in incident modules."""

    def test_is_core_system_file_recognition(self):
        """Verify is_core_system_file() correctly identifies core files."""
        # Core system directories
        assert is_core_system_file("phi_os/event_gate.py")
        assert is_core_system_file("interface/cli.py")
        assert is_core_system_file("structural/schema.py")
        assert is_core_system_file("gateway/router.py")

        # Core system extra files
        assert is_core_system_file("app.py")
        assert is_core_system_file("index.html")
        assert is_core_system_file("scripts/ledger/anchor_update.py")

        # Private repo directories
        assert is_core_system_file("PlanningCaliber/workshop/test.py")
        assert is_core_system_file("PlanningCaliber/workshop/data/file.json")

        # Non-core files
        assert not is_core_system_file("runtime/incident_ledger.json")
        assert not is_core_system_file("data/events.json")
        assert not is_core_system_file("docs/README.md")

    def test_incident_ledger_not_core_file(self):
        """Verify incident_ledger.json is NOT a core system file."""
        ledger_path = "runtime/incident_ledger.json"
        assert not is_core_system_file(ledger_path)

    def test_incident_engine_paths_scoped(self):
        """Verify incident_engine.py uses scoped paths."""
        from runtime.incident_engine import git_commit

        with patch("runtime.incident_engine.mocka_git_safe_commit") as mock_commit:
            mock_commit.return_value = {
                "committed": False,
                "excluded": [],
                "commit_hash": None,
                "pushed": False,
                "error": None,
                "post_commit_files": [],
                "post_commit_violation": []
            }

            git_commit()

            # Verify mocka_git_safe_commit was called with scoped paths
            mock_commit.assert_called_once()
            call_kwargs = mock_commit.call_args[1]
            assert call_kwargs["paths"] == ["runtime/incident_ledger.json"]
            assert call_kwargs["push"] == False  # TODO_363: push should be separate step

    def test_incident_engine_checks_violation(self):
        """Verify incident_engine.py checks for post_commit_violation."""
        from runtime.incident_engine import git_commit

        with patch("runtime.incident_engine.mocka_git_safe_commit") as mock_commit:
            # Simulate core file accidentally included in commit
            mock_commit.return_value = {
                "committed": True,
                "excluded": ["app.py"],
                "commit_hash": "abc123",
                "pushed": False,
                "error": None,
                "post_commit_files": ["runtime/incident_ledger.json", "app.py"],
                "post_commit_violation": ["app.py"]  # Core file slipped through
            }

            with patch("builtins.print") as mock_print:
                git_commit()

                # Verify violation was detected
                print_calls = [str(call) for call in mock_print.call_args_list]
                violation_reported = any("GIT_SAFETY_VIOLATION" in str(call) for call in print_calls)
                assert violation_reported, "Violation should be reported"

    def test_incident_sync_paths_scoped(self):
        """Verify incident_git_sync.py uses scoped paths."""
        from runtime.incident_git_sync import commit_incident

        with patch("runtime.incident_git_sync.mocka_git_safe_commit") as mock_commit:
            mock_commit.return_value = {
                "committed": False,
                "excluded": [],
                "commit_hash": None,
                "pushed": False,
                "error": None,
                "post_commit_files": [],
                "post_commit_violation": []
            }

            commit_incident()

            # Verify mocka_git_safe_commit was called with scoped paths
            mock_commit.assert_called_once()
            call_kwargs = mock_commit.call_args[1]
            assert "incident_ledger.json" in call_kwargs["paths"][0]
            assert call_kwargs["push"] == False  # TODO_363: push should be separate step

    def test_incident_sync_checks_violation(self):
        """Verify incident_git_sync.py checks for post_commit_violation."""
        from runtime.incident_git_sync import commit_incident

        with patch("runtime.incident_git_sync.mocka_git_safe_commit") as mock_commit:
            # Simulate core file accidentally included
            mock_commit.return_value = {
                "committed": True,
                "excluded": ["app.py"],
                "commit_hash": "def456",
                "pushed": False,
                "error": None,
                "post_commit_files": ["runtime/incident_ledger.json", "app.py"],
                "post_commit_violation": ["app.py"]
            }

            with patch("builtins.print") as mock_print:
                commit_incident()

                # Verify violation was detected
                print_calls = [str(call) for call in mock_print.call_args_list]
                violation_reported = any("GIT_SAFETY_VIOLATION" in str(call) for call in print_calls)
                assert violation_reported, "Violation should be reported"

    def test_push_separated_from_commit(self):
        """Verify push is a separate step (TODO_363)."""
        from runtime.incident_engine import git_commit

        with patch("runtime.incident_engine.mocka_git_safe_commit") as mock_commit:
            with patch("runtime.incident_engine._run") as mock_run:
                mock_commit.return_value = {
                    "committed": True,
                    "excluded": [],
                    "commit_hash": "xyz789",
                    "pushed": False,
                    "error": None,
                    "post_commit_files": ["runtime/incident_ledger.json"],
                    "post_commit_violation": []
                }
                mock_run.return_value = MagicMock(returncode=0, stderr="")

                git_commit()

                # Verify push is called separately after commit
                mock_run.assert_called()
                push_calls = [call for call in mock_run.call_args_list
                              if "push" in str(call)]
                assert len(push_calls) > 0, "Push should be called separately"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""Unit tests for check_submodules_branch pre-commit hook."""
from pathlib import Path
import subprocess
from unittest import mock

import pytest

from pre_commit_hooks.check_submodules_branch import check_submodule_branch


def test_no_gitmodules_file(tmp_path: Path):
    """Test when .gitmodules doesn't exist."""
    gitmodules = tmp_path / ".gitmodules"
    assert check_submodule_branch(gitmodules, tmp_path) == 0


@pytest.mark.parametrize(
    "gitmodules_filename",
    [
        "no-branch.gitmodules",
    ],
)
def test_gitmodules_without_branches(
    gitmodules_filename: str,
    datadir: Path,
    tmp_path: Path,
):
    """Test .gitmodules with no branch fields."""
    gitmodules = tmp_path / ".gitmodules"
    gitmodules.write_text((datadir / gitmodules_filename).read_text())
    assert check_submodule_branch(gitmodules, tmp_path) == 0


@pytest.mark.parametrize(
    "gitmodules_filename",
    [
        "with-branch.gitmodules",
    ],
)
def test_submodule_dir_not_exists(
    gitmodules_filename: str,
    datadir: Path,
    tmp_path: Path,
):
    """Test when submodule directory doesn't exist."""
    gitmodules = tmp_path / ".gitmodules"
    gitmodules.write_text((datadir / gitmodules_filename).read_text())
    # Don't create the submodule directory
    assert check_submodule_branch(gitmodules, tmp_path) == 0


@mock.patch("subprocess.run")
@pytest.mark.parametrize(
    "gitmodules_filename",
    [
        "with-branch.gitmodules",
    ],
)
def test_valid_submodule_on_branch(
    mock_run,
    gitmodules_filename: str,
    datadir: Path,
    tmp_path: Path,
):
    """Test valid submodule that is on the correct branch."""
    gitmodules = tmp_path / ".gitmodules"
    gitmodules.write_text((datadir / gitmodules_filename).read_text())

    # Create submodule directory
    submodule_dir = tmp_path / "foo" / "bar"
    submodule_dir.mkdir(parents=True)

    # Mock git commands
    def mock_git_commands(*args, **kwargs):
        cmd = args[0]
        if cmd[1] == "fetch":
            return subprocess.CompletedProcess(cmd, 0)
        elif cmd[1] == "rev-parse":
            result = subprocess.CompletedProcess(cmd, 0)
            result.stdout = "abc123\n"
            return result
        elif cmd[1] == "merge-base":
            return subprocess.CompletedProcess(cmd, 0)
        return subprocess.CompletedProcess(cmd, 1)

    mock_run.side_effect = mock_git_commands

    assert check_submodule_branch(gitmodules, tmp_path) == 0


@mock.patch("subprocess.run")
@pytest.mark.parametrize(
    "gitmodules_filename",
    [
        "with-branch.gitmodules",
    ],
)
def test_invalid_submodule_not_on_branch(
    mock_run,
    gitmodules_filename: str,
    datadir: Path,
    tmp_path: Path,
):
    """Test submodule that is NOT on the correct branch."""
    gitmodules = tmp_path / ".gitmodules"
    gitmodules.write_text((datadir / gitmodules_filename).read_text())

    # Create submodule directory
    submodule_dir = tmp_path / "foo" / "bar"
    submodule_dir.mkdir(parents=True)

    # Mock git commands
    def mock_git_commands(*args, **kwargs):
        cmd = args[0]
        if cmd[1] == "fetch":
            return subprocess.CompletedProcess(cmd, 0)
        elif cmd[1] == "rev-parse":
            result = subprocess.CompletedProcess(cmd, 0)
            result.stdout = "abc123\n"
            return result
        elif cmd[1] == "merge-base":
            raise subprocess.CalledProcessError(1, cmd)
        return subprocess.CompletedProcess(cmd, 1)

    mock_run.side_effect = mock_git_commands

    assert check_submodule_branch(gitmodules, tmp_path) == 1

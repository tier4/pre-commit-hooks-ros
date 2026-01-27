"""Tests for check_gitmodules pre-commit hook."""
from pathlib import Path
import shutil
import tempfile

import pytest

from pre_commit_hooks.check_gitmodules import check_gitmodules
from pre_commit_hooks.check_gitmodules import main

# Valid test cases (expected exit code 0)
valid_cases = [
    "valid-with-branch",
    "valid-with-update-none",
    "valid-with-both",
    "valid-multiple",
]

# Invalid test cases (expected exit code 1)
invalid_cases = [
    "invalid-name-mismatch",
    "invalid-missing-branch-update",
    "invalid-update-not-none",
    "invalid-multiple-mixed",
]


@pytest.mark.parametrize("case", valid_cases)
def test_valid_gitmodules(case: str, datadir: Path, tmp_path: Path):
    """Test valid .gitmodules files that should pass validation."""
    test_file = datadir / f"{case}.gitmodules"
    gitmodules_path = tmp_path / ".gitmodules"

    shutil.copy(test_file, gitmodules_path)
    assert check_gitmodules(gitmodules_path) == 0


@pytest.mark.parametrize("case", invalid_cases)
def test_invalid_gitmodules(case: str, datadir: Path, tmp_path: Path):
    """Test invalid .gitmodules files that should fail validation."""
    test_file = datadir / f"{case}.gitmodules"
    gitmodules_path = tmp_path / ".gitmodules"

    shutil.copy(test_file, gitmodules_path)
    assert check_gitmodules(gitmodules_path) == 1


def test_no_gitmodules_file(tmp_path: Path):
    """Test when .gitmodules doesn't exist."""
    gitmodules_path = tmp_path / ".gitmodules"
    assert check_gitmodules(gitmodules_path) == 0


def test_main_function(datadir: Path):
    """Test the main function."""
    test_file = datadir / "valid-with-branch.gitmodules"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        gitmodules = tmppath / ".gitmodules"
        shutil.copy(test_file, gitmodules)

        # Change to temp directory
        import os

        old_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            assert main([]) == 0
        finally:
            os.chdir(old_cwd)

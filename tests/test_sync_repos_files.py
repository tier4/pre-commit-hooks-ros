"""Unit tests for sync_repos_files pre-commit hook."""
from pathlib import Path
from unittest import mock

import pytest
from ruamel.yaml import YAML

from pre_commit_hooks.sync_repos_files import sync_repos_files


def test_no_gitmodules_file(tmp_path: Path):
    """Test when .gitmodules doesn't exist."""
    gitmodules = tmp_path / ".gitmodules"
    repos_dir = tmp_path / "repositories"
    repos_dir.mkdir()
    assert sync_repos_files(gitmodules, repos_dir, tmp_path) == 0


def test_no_repos_dir(tmp_path: Path):
    """Test when repos directory doesn't exist."""
    gitmodules = tmp_path / ".gitmodules"
    gitmodules.write_text(
        '[submodule "src/core/pkg"]\n'
        "    path = src/core/pkg\n"
        "    url = https://github.com/example/pkg.git\n"
        "    branch = main\n",
    )
    repos_dir = tmp_path / "repositories"
    assert sync_repos_files(gitmodules, repos_dir, tmp_path) == 0


@mock.patch(
    "pre_commit_hooks.sync_repos_files.get_submodule_commit",
)
@pytest.mark.parametrize(
    ("gitmodules_filename", "repos_filename"),
    [
        ("with-branch.gitmodules", "core-empty.repos"),
    ],
)
def test_sync_creates_missing_entry(
    mock_get_commit,
    gitmodules_filename: str,
    repos_filename: str,
    datadir: Path,
    tmp_path: Path,
):
    """Test that sync creates missing repository entries."""
    mock_get_commit.return_value = "abc123def456"

    gitmodules = tmp_path / ".gitmodules"
    gitmodules.write_text((datadir / gitmodules_filename).read_text())

    repos_dir = tmp_path
    # Create empty core.repos file
    core_repos = repos_dir / "core.repos"
    core_repos.write_text((datadir / repos_filename).read_text())

    # Should return 1 (changes made)
    assert sync_repos_files(gitmodules, repos_dir, tmp_path) == 1

    # Verify the file was updated
    yaml = YAML()
    with open(core_repos) as f:
        data = yaml.load(f)

    assert "package1" in data["repositories"]
    assert data["repositories"]["package1"]["url"] == "https://github.com/example/package1.git"
    assert data["repositories"]["package1"]["version"] == "abc123def456"
    assert data["repositories"]["package1"]["branch"] == "main"


@mock.patch(
    "pre_commit_hooks.sync_repos_files.get_submodule_commit",
)
@pytest.mark.parametrize(
    ("gitmodules_filename", "repos_filename"),
    [
        ("with-branch.gitmodules", "core-with-extra.repos"),
    ],
)
def test_sync_removes_extra_entry(
    mock_get_commit,
    gitmodules_filename: str,
    repos_filename: str,
    datadir: Path,
    tmp_path: Path,
):
    """Test that sync removes extra repository entries."""
    mock_get_commit.return_value = "abc123def456"

    gitmodules = tmp_path / ".gitmodules"
    gitmodules.write_text((datadir / gitmodules_filename).read_text())

    repos_dir = tmp_path
    # Create core.repos with extra entry
    core_repos = repos_dir / "core.repos"
    core_repos.write_text((datadir / repos_filename).read_text())

    # Should return 1 (changes made)
    assert sync_repos_files(gitmodules, repos_dir, tmp_path) == 1

    # Verify the extra entry was removed
    yaml = YAML()
    with open(core_repos) as f:
        data = yaml.load(f)

    assert "package1" in data["repositories"]
    assert "extra_package" not in data["repositories"]


@mock.patch(
    "pre_commit_hooks.sync_repos_files.get_submodule_commit",
)
@pytest.mark.parametrize(
    ("gitmodules_filename", "repos_filename"),
    [
        ("with-branch.gitmodules", "core-in-sync.repos"),
    ],
)
def test_sync_already_in_sync(
    mock_get_commit,
    gitmodules_filename: str,
    repos_filename: str,
    datadir: Path,
    tmp_path: Path,
):
    """Test when repos file is already in sync."""
    mock_get_commit.return_value = "abc123def456"

    gitmodules = tmp_path / ".gitmodules"
    gitmodules.write_text((datadir / gitmodules_filename).read_text())

    repos_dir = tmp_path
    # Create core.repos that matches gitmodules
    core_repos = repos_dir / "core.repos"
    core_repos.write_text((datadir / repos_filename).read_text())

    # Should return 0 (no changes needed)
    assert sync_repos_files(gitmodules, repos_dir, tmp_path) == 0


@pytest.mark.parametrize(
    "gitmodules_filename",
    [
        "non-src-submodule.gitmodules",
    ],
)
def test_ignores_non_src_submodules(
    gitmodules_filename: str,
    datadir: Path,
    tmp_path: Path,
):
    """Test that submodules not starting with src/ are ignored."""
    gitmodules = tmp_path / ".gitmodules"
    gitmodules.write_text((datadir / gitmodules_filename).read_text())

    repos_dir = tmp_path

    # Should return 0 (nothing to sync)
    assert sync_repos_files(gitmodules, repos_dir, tmp_path) == 0


@mock.patch(
    "pre_commit_hooks.sync_repos_files.get_submodule_commit",
)
@pytest.mark.parametrize(
    ("gitmodules_filename", "repos_filename"),
    [
        ("update-none.gitmodules", "core-empty.repos"),
    ],
)
def test_update_none_has_no_branch(
    mock_get_commit,
    gitmodules_filename: str,
    repos_filename: str,
    datadir: Path,
    tmp_path: Path,
):
    """Test that update=none submodules don't have branch field."""
    mock_get_commit.return_value = "abc123def456"

    gitmodules = tmp_path / ".gitmodules"
    gitmodules.write_text((datadir / gitmodules_filename).read_text())

    repos_dir = tmp_path
    # Create empty core.repos file
    core_repos = repos_dir / "core.repos"
    core_repos.write_text((datadir / repos_filename).read_text())

    # Should return 1 (changes made)
    assert sync_repos_files(gitmodules, repos_dir, tmp_path) == 1

    # Verify the file was updated without branch field
    yaml = YAML()
    with open(core_repos) as f:
        data = yaml.load(f)

    assert "package1" in data["repositories"]
    assert "branch" not in data["repositories"]["package1"]
    assert data["repositories"]["package1"]["version"] == "abc123def456"


@mock.patch(
    "pre_commit_hooks.sync_repos_files.get_submodule_commit",
)
@pytest.mark.parametrize(
    ("gitmodules_filename", "repos_filename"),
    [
        ("with-branch.gitmodules", "core-empty.repos"),
    ],
)
def test_skips_nested_repos_files(
    mock_get_commit,
    gitmodules_filename: str,
    repos_filename: str,
    datadir: Path,
    tmp_path: Path,
):
    """Test that nested .repos files are skipped."""
    mock_get_commit.return_value = "abc123def456"

    gitmodules = tmp_path / ".gitmodules"
    gitmodules.write_text((datadir / gitmodules_filename).read_text())

    repos_dir = tmp_path
    # Create nested directory with .repos file
    nested_dir = repos_dir / "nested"
    nested_dir.mkdir()
    nested_repos = nested_dir / "core.repos"
    nested_repos.write_text((datadir / repos_filename).read_text())

    # Should return 0 (nested file is ignored)
    assert sync_repos_files(gitmodules, repos_dir, tmp_path) == 0

    # Nested file should not be modified
    yaml = YAML()
    with open(nested_repos) as f:
        data = yaml.load(f)
    assert data["repositories"] == {}

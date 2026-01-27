#!/usr/bin/env python3
"""Check submodules with branch field are on their specified branch."""
import argparse
import configparser
from pathlib import Path
import subprocess
import sys
from typing import Optional
from typing import Sequence


def check_submodule_branch(
    gitmodules_path: Path,
    submodule_path: Path,
) -> int:
    """Check if a submodule with branch field is ancestor of remote branch.

    Args:
        gitmodules_path: Path to .gitmodules file
        submodule_path: Path to the submodule directory

    Returns:
        0 if all checks pass, 1 otherwise
    """
    if not gitmodules_path.exists():
        return 0

    config = configparser.ConfigParser()
    config.read(gitmodules_path)

    retval = 0

    for section in config.sections():
        if not section.startswith('submodule "'):
            continue

        # Extract submodule name from section header
        submodule_name = section[len('submodule "') : -1]

        # Get path and branch
        if "path" not in config[section]:
            continue

        path = config[section]["path"]
        branch = config[section].get("branch")

        # Skip if no branch is specified
        if not branch:
            print(f"ℹ️  Skipping {submodule_name}: No branch specified")
            continue

        submodule_dir = submodule_path / path

        # Skip if submodule directory doesn't exist
        if not submodule_dir.exists():
            print(
                f"⚠️  Skipping {submodule_name}: Directory {path} not found",
            )
            continue

        print(f"🔍 Checking {submodule_name}: Must be on branch {branch}...")

        try:
            # Fetch the latest info from origin for this branch
            subprocess.run(
                ["git", "fetch", "origin", branch, "--quiet"],
                cwd=submodule_dir,
                check=True,
                capture_output=True,
            )

            # Get current commit
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=submodule_dir,
                check=True,
                capture_output=True,
                text=True,
            )
            current_commit = result.stdout.strip()

            # Check if current commit is an ancestor of origin/branch
            subprocess.run(
                [
                    "git",
                    "merge-base",
                    "--is-ancestor",
                    current_commit,
                    f"origin/{branch}",
                ],
                cwd=submodule_dir,
                check=True,
                capture_output=True,
            )

            print(f"✅ OK: Commit {current_commit[:8]} belongs to {branch}")

        except subprocess.CalledProcessError:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=submodule_dir,
                capture_output=True,
                text=True,
            )
            current_commit = (
                result.stdout.strip() if result.returncode == 0 else "unknown"
            )  # noqa: E501

            print(
                f"❌ ERROR: Submodule {path} is pointing to " f"{current_commit[:8]}",
            )
            print(
                f"          This commit is NOT reachable from " f"origin/{branch}",
            )
            print(f'          Fix: Run "git submodule update --remote {path}"')
            retval = 1

    return retval


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Serve as entry point for the pre-commit hook."""
    parser = argparse.ArgumentParser(
        description=("Check submodules with branch field are on their specified branch"),
    )
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames to check (typically .gitmodules)",
    )
    parser.parse_args(argv)

    # Check for .gitmodules in the current directory
    gitmodules_path = Path(".gitmodules")
    submodule_path = Path(".")

    return check_submodule_branch(gitmodules_path, submodule_path)


if __name__ == "__main__":
    sys.exit(main())

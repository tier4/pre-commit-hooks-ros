#!/usr/bin/env python3
"""Sync .repos files with gitmodules for vcstool compatibility."""
import argparse
import configparser
from pathlib import Path
import subprocess
import sys
from typing import Optional
from typing import Sequence

from ruamel.yaml import YAML


def get_submodule_commit(submodule_path: Path) -> Optional[str]:
    """Get the current commit hash of a submodule.

    Args:
        submodule_path: Path to the submodule directory

    Returns:
        Commit hash as string, or None if unable to retrieve
    """
    if not submodule_path.exists():
        return None

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=submodule_path,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def sync_repos_files(
    gitmodules_path: Path,
    repos_dir: Path,
    superproject_root: Path,
) -> int:
    """Sync .repos files with submodules that match their prefix.

    For each xxx.repos file in repos_dir (not nested), ensure it contains
    entries for all submodules whose path starts with src/xxx/.
    Each entry should have:
    - branch: the branch from .gitmodules (or absent if update=none)
    - version: the actual commit hash from the submodule

    Args:
        gitmodules_path: Path to .gitmodules file
        repos_dir: Directory containing .repos files (can be root)
        superproject_root: Root directory of the superproject

    Returns:
        0 if all checks pass and files are in sync, 1 if updates were made
    """
    if not gitmodules_path.exists():
        print("No .gitmodules file found")
        return 0

    if not repos_dir.exists():
        print(f"Directory {repos_dir} not found")
        return 0

    # Read .gitmodules
    config = configparser.ConfigParser()
    config.read(gitmodules_path)

    # Group submodules by their prefix (xxx in src/xxx/...)
    submodule_groups = {}

    for section in config.sections():
        if not section.startswith('submodule "'):
            continue

        if "path" not in config[section]:
            continue

        path = config[section]["path"]

        # Check if path starts with src/
        if not path.startswith("src/"):
            continue

        # Extract the prefix (e.g., "core" from "src/core/something")
        parts = path.split("/")
        if len(parts) < 3:  # Need at least src/xxx/something
            continue

        prefix = parts[1]  # e.g., "core", "universe", "launcher"
        relative_path = "/".join(parts[2:])  # path after src/xxx/

        if prefix not in submodule_groups:
            submodule_groups[prefix] = {}

        # Get submodule info from .gitmodules
        url = config[section].get("url", "")
        branch = config[section].get("branch")
        update_mode = config[section].get("update")

        # Get actual commit hash from submodule
        submodule_full_path = superproject_root / path
        version = get_submodule_commit(submodule_full_path)

        if version is None:
            print(f"⚠️  Cannot read commit for {path}, skipping...")
            continue

        # Store submodule info
        entry_data = {
            "url": url,
            "version": version,
        }

        # Add branch field only if not update=none
        if update_mode != "none" and branch:
            entry_data["branch"] = branch

        submodule_groups[prefix][relative_path] = entry_data

    # Process each .repos file (only direct children, not nested)
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.default_flow_style = False
    yaml.width = 4096  # Prevent line wrapping

    retval = 0

    # Only get .repos files directly in repos_dir (not nested)
    repos_files = [f for f in repos_dir.iterdir() if f.suffix == ".repos"]

    for repos_file in repos_files:
        prefix = repos_file.stem  # filename without .repos extension

        if prefix not in submodule_groups:
            print(f"ℹ️  No submodules found for {repos_file.name}")
            continue

        expected_repos = submodule_groups[prefix]

        # Load existing .repos file
        with open(repos_file) as f:
            repos_data = yaml.load(f)

        if repos_data is None:
            repos_data = {}

        if "repositories" not in repos_data:
            repos_data["repositories"] = {}

        existing_repos = repos_data["repositories"]

        # Find differences
        needs_update = False

        # Check for missing or mismatched entries
        for rel_path, info in expected_repos.items():
            if rel_path not in existing_repos:
                print(
                    f"⚠️  {repos_file.name}: Missing entry for {rel_path}",
                )
                needs_update = True
                # Add the missing entry
                entry = {
                    "type": "git",
                    "url": info["url"],
                    "version": info["version"],
                }
                if "branch" in info:
                    entry["branch"] = info["branch"]
                existing_repos[rel_path] = entry
            else:
                # Check URL
                if existing_repos[rel_path].get("url") != info["url"]:
                    print(
                        f"⚠️  {repos_file.name}: URL mismatch for {rel_path}",
                    )
                    needs_update = True
                    existing_repos[rel_path]["url"] = info["url"]

                # Check version (commit hash)
                if existing_repos[rel_path].get("version") != info["version"]:
                    print(
                        f"⚠️  {repos_file.name}: Version mismatch for " f"{rel_path}",
                    )
                    needs_update = True
                    existing_repos[rel_path]["version"] = info["version"]

                # Check branch field
                expected_branch = info.get("branch")
                current_branch = existing_repos[rel_path].get("branch")

                if expected_branch != current_branch:
                    print(
                        f"⚠️  {repos_file.name}: Branch mismatch for " f"{rel_path}",
                    )
                    needs_update = True
                    if expected_branch:
                        existing_repos[rel_path]["branch"] = expected_branch
                    elif "branch" in existing_repos[rel_path]:
                        del existing_repos[rel_path]["branch"]

        # Check for extra entries that shouldn't be there
        for rel_path in list(existing_repos.keys()):
            if rel_path not in expected_repos:
                print(
                    f"⚠️  {repos_file.name}: Extra entry for {rel_path} " f"(not in .gitmodules)",
                )
                needs_update = True
                del existing_repos[rel_path]

        if needs_update:
            print(f"🔄 Updating {repos_file.name}...")
            with open(repos_file, "w") as f:
                yaml.dump(repos_data, f)
            retval = 1
        else:
            print(f"✅ {repos_file.name} is in sync")

    return retval


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Serve as entry point for the pre-commit hook."""
    parser = argparse.ArgumentParser(
        description=("Sync .repos files with submodules for vcstool compatibility"),
    )
    parser.add_argument(
        "--repos-dir",
        default=".",
        help="Directory containing .repos files (default: current directory)",
    )
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames that triggered the hook",
    )
    args = parser.parse_args(argv)

    # Check for .gitmodules in the current directory
    gitmodules_path = Path(".gitmodules")
    repos_dir = Path(args.repos_dir)
    superproject_root = Path(".")

    return sync_repos_files(gitmodules_path, repos_dir, superproject_root)


if __name__ == "__main__":
    sys.exit(main())

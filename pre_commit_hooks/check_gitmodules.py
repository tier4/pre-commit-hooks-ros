#!/usr/bin/env python3
"""Check .gitmodules file for proper submodule configuration."""
import argparse
import configparser
from pathlib import Path
import sys
from typing import Optional
from typing import Sequence


def check_gitmodules(gitmodules_path: Path) -> int:
    """Check if .gitmodules file meets requirements.

    - Submodule name matches path
    - Either branch field is specified OR update field is set to 'none'

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

        # Get path
        if "path" not in config[section]:
            print(f"Error: Submodule '{submodule_name}' has no path")
            retval = 1
            continue

        submodule_path = config[section]["path"]

        # Check 1: Name must match path
        if submodule_name != submodule_path:
            print(
                f"Error: Submodule name '{submodule_name}' does not "
                f"match path '{submodule_path}'",
            )
            retval = 1

        # Check 2: Must have either branch OR update=none
        has_branch = "branch" in config[section]
        update_value = config[section].get("update")
        has_update_none = update_value == "none"

        if not (has_branch or has_update_none):
            print(
                f"Error: Submodule '{submodule_name}' must have "
                f"either 'branch' field or 'update = none'",
            )
            retval = 1

    return retval


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Serve as entry point for the pre-commit hook."""
    parser = argparse.ArgumentParser(
        description=("Check .gitmodules file for proper submodule configuration"),
    )
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames to check (typically .gitmodules)",
    )
    parser.parse_args(argv)

    # Check for .gitmodules in the current directory
    gitmodules_path = Path(".gitmodules")

    return check_gitmodules(gitmodules_path)


if __name__ == "__main__":
    sys.exit(main())

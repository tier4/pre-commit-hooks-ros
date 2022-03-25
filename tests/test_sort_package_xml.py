from pathlib import Path

import pytest

from pre_commit_hooks import sort_package_xml


@pytest.mark.parametrize(
    "case",
    [
        "normal",
        "no-format",
    ],
)
def test(case: str, datadir: Path, tmp_path: Path):
    input_file = datadir / f"{case}.input.xml"
    answer_file = datadir / f"{case}.answer.xml"

    # Format
    return_code = sort_package_xml.main([str(input_file)])
    print(input_file.read_text())
    assert return_code == 1
    assert input_file.read_text() == answer_file.read_text()

    # Re-format
    return_code = sort_package_xml.main([str(input_file)])
    assert return_code == 0
    assert input_file.read_text() == answer_file.read_text()

from pathlib import Path
import shutil

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

    # Create a temporary file to prevent overwriting original files
    tmp_file = tmp_path / f"{case}.input.xml"
    shutil.copy(input_file, tmp_file)

    # Format
    return_code = sort_package_xml.main([str(tmp_file)])
    print(tmp_file.read_text())
    assert return_code == 1
    assert tmp_file.read_text() == answer_file.read_text()

    # Re-format
    return_code = sort_package_xml.main([str(tmp_file)])
    assert return_code == 0
    assert tmp_file.read_text() == answer_file.read_text()

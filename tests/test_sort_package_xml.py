from pathlib import Path
import shutil

import pytest

from pre_commit_hooks import sort_package_xml

files = [
    "package.xml",
]

cases = []
for file in files:
    cases.append((Path(file), 0))
    cases.append((Path(file), 1))


@pytest.mark.parametrize(("target_file", "answer_code"), cases)
def test(target_file, answer_code, datadir):

    ok_ng = ".ng" if answer_code else ".ok"
    source_file = target_file.with_suffix(ok_ng + target_file.suffix)
    answer_file = target_file.with_suffix(".ok" + target_file.suffix)
    target_path = datadir.joinpath(target_file)
    source_path = datadir.joinpath(source_file)
    answer_path = datadir.joinpath(answer_file)
    shutil.copy(source_path, target_path)

    return_code = sort_package_xml.main([str(target_path)])
    target_text = target_path.read_text()
    answer_text = answer_path.read_text()
    assert return_code == answer_code
    assert target_text == answer_text

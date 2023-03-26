import shutil

import pytest

from pre_commit_hooks import ros_include_guard

cases_auto_fix = [
    "include/rospkg/foobar.h",
    "include/rospkg/foobar.hpp",
    "include/rospkg/nolint.hpp",
    "include/rospkg/pragma.hpp",
    "src/foo_bar_baz.hpp",
    "src/foo_bar/baz.hpp",
    "src/foo/bar_baz.hpp",
    "src/foo/bar/baz.hpp",
]

cases_no_fix = [
    ("include/rospkg/pragma.only.hpp", 0),
    ("include/rospkg/none.hpp", 1),
]


@pytest.mark.parametrize(("target_file"), cases_auto_fix)
def test_auto_fix(target_file, datadir):
    target_path = datadir.joinpath(target_file)
    right_path = target_path.with_suffix(".right" + target_path.suffix)
    wrong_path = target_path.with_suffix(".wrong" + target_path.suffix)

    # Test wrong file.
    shutil.copy(wrong_path, target_path)
    return_code = ros_include_guard.main([str(target_path)])
    assert return_code == 1
    assert target_path.read_text() == right_path.read_text()

    # Test right file.
    shutil.copy(right_path, target_path)
    return_code = ros_include_guard.main([str(target_path)])
    assert return_code == 0
    assert target_path.read_text() == right_path.read_text()


@pytest.mark.parametrize(("target_file", "answer_code"), cases_no_fix)
def test_no_fix(target_file, answer_code, datadir):
    target_path = datadir.joinpath(target_file)
    return_code = ros_include_guard.main([str(target_path)])
    assert return_code == answer_code

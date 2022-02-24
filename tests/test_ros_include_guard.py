import shutil

import pytest

from pre_commit_hooks import ros_include_guard

cases = [
    "include/rospkg/foobar.h",
    "include/rospkg/foobar.hpp",
    "include/rospkg/nolint.hpp",
    "src/foo_bar_baz.hpp",
    "src/foo_bar/baz.hpp",
    "src/foo/bar_baz.hpp",
    "src/foo/bar/baz.hpp",
]


@pytest.mark.parametrize(("target_file"), cases)
def test(target_file, datadir):

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

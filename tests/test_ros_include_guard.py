import pathlib
import pytest
from pre_commit_hooks import ros_include_guard

rospkg1 = 'tests/resources/rospkg1/'
rospkg2 = 'tests/resources/rospkg2/'
rospkg3 = 'tests/resources/rospkg3/'

files1 = [
  'include/rospkg/foobar.h',
  'include/rospkg/foobar.hpp',
  'src/foo_bar_baz.hpp',
  'src/foo_bar/baz.hpp',
  'src/foo/bar_baz.hpp',
  'src/foo/bar/baz.hpp',
]

files2 = [
  'include/rospkg/nolint.hpp',
]

cases = []
for file in files1:
  cases.append((rospkg1 + file, rospkg3 + file, 1))
  cases.append((rospkg2 + file, rospkg3 + file, 0))
for file in files2:
  cases.append((rospkg2 + file, rospkg3 + file, 0))


@pytest.mark.parametrize(('target_file', 'answer_file', 'answer_code'), cases)
def test(target_file, answer_file, answer_code):

    return_code = ros_include_guard.main([target_file])
    target_text = pathlib.Path(target_file).read_text()
    answer_text = pathlib.Path(answer_file).read_text()

    assert return_code == answer_code
    assert target_text == answer_text

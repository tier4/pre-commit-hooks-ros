import pathlib
import pytest
from pre_commit_hooks import sort_package_xml

cases = [
  ('tests/resources/rospkg1/package.xml', 'tests/resources/rospkg3/package.xml', 1),
  ('tests/resources/rospkg2/package.xml', 'tests/resources/rospkg3/package.xml', 0),
]

@pytest.mark.parametrize(('target_file', 'answer_file', 'answer_code'), cases)
def test(target_file, answer_file, answer_code):

    return_code = sort_package_xml.main([target_file])
    target_text = pathlib.Path(target_file).read_text()
    answer_text = pathlib.Path(answer_file).read_text()

    assert return_code == answer_code
    assert target_text == answer_text

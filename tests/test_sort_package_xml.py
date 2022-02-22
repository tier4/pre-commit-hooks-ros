import pathlib
import pytest
from pre_commit_hooks import sort_package_xml

cases = [
  ('package.ok.xml', 'package.ans.xml', 0),
  ('package.ng.xml', 'package.ans.xml', 1),
]

@pytest.mark.parametrize(('target_file', 'answer_file', 'answer_code'), cases)
def test(target_file, answer_file, answer_code, datadir):

  target_path = datadir.joinpath(target_file)
  answer_path = datadir.joinpath(answer_file)
  return_code = sort_package_xml.main([str(target_path)])
  target_text = pathlib.Path(target_path).read_text()
  answer_text = pathlib.Path(answer_path).read_text()

  assert return_code == answer_code
  assert target_text == answer_text

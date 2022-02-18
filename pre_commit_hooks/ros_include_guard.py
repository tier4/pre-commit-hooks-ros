# Copyright 2022 Tier IV, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import pathlib
import re


class Directive:

  def __init__(self):
    self.line = None
    self.text = None
    self.expected = None
    self.tokens = None
    self.nolint = False

  def update(self, line, text):
    self.line = line
    self.text = text

  def is_none(self):
    return self.line is None

  def mismatch(self):
    if self.nolint: return False
    return self.text != self.expected

  def overwrite(self, lines):
    if self.nolint: return
    lines[self.line] = self.expected


class OpeningDirective(Directive):

  def prepare(self, macro_name, allow_nolint):
    self.tokens = re.split(R'\b', self.text)
    if 4 <= len(self.tokens):
      self.tokens[3] = macro_name
      self.expected = ''.join(self.tokens)
    self.nolint = allow_nolint and ('NOLINT' in self.tokens)


class ClosingDirective(Directive):

  def prepare(self, macro_name, allow_nolint):
    self.tokens = re.split(R'\b', self.text)
    self.expected = '#endif  // {}'.format(macro_name)
    self.nolint = allow_nolint and ('NOLINT' in self.tokens)


class IncludeGuard:

  def __init__(self):
    self.ifndef = OpeningDirective()
    self.define = OpeningDirective()
    self.endif  = ClosingDirective()
    self.pragma = False

  def items(self):
    yield self.ifndef
    yield self.define
    yield self.endif

  def is_none(self):
    return any(item.is_none() for item in self.items())

  def mismatch(self):
    return any(item.mismatch() for item in self.items())

  def overwrite(self, lines):
    return any(item.overwrite(lines) for item in self.items())

  def prepare(self, macro_name, allow_nolint):
    for item in self.items(): item.prepare(macro_name, allow_nolint)


def get_include_guard_info(lines):

  guard = IncludeGuard()
  for line, text in enumerate(lines):
    if text.startswith('#pragma once'):
      guard.pragma = True
    if text.startswith('#ifndef') and guard.ifndef.is_none():
      guard.ifndef.update(line, text)
    if text.startswith('#define') and guard.define.is_none():
      guard.define.update(line, text)
    if text.startswith('#endif'):
      guard.endif.update(line, text)
  return guard


def get_parts_after(parts: list, targets: set):
  result = []
  for part in reversed(parts):
    if part in targets:
      break
    result.append(part)
  return reversed(result)


def get_include_guard_macro_name(filepath: pathlib.Path):
  targets = {'include', 'src', 'test'}
  for path in filepath.parents:
      if path.joinpath('package.xml').exists():
          parts = get_parts_after(filepath.relative_to(path).parts, targets)
          return '__'.join(parts).replace('.', '_').upper() + '_'
  return None


def main(argv=None):

  parser = argparse.ArgumentParser()
  parser.add_argument('filenames', nargs='*', help='Filenames to fix')
  parser.add_argument('--allow-nolint', action='store_true', help='Allow nolint comment')
  args = parser.parse_args(argv)

  return_code = 0
  for filename in args.filenames:
    filepath = pathlib.Path(filename)
    macro_name = get_include_guard_macro_name(filepath)
    if macro_name:
      lines = filepath.read_text().split('\n')
      guard = get_include_guard_info(lines)
      if guard.pragma:
        continue
      if guard.is_none():
        return_code = 1
        print('No include guard in {}'.format(filepath))
        continue
      guard.prepare(macro_name, args.allow_nolint)
      if guard.mismatch():
        return_code = 1
        print('Fix include guard in {}'.format(filepath))
        guard.overwrite(lines)
        filepath.write_text('\n'.join(lines))
        continue

  return return_code


if __name__ == '__main__':
  exit(main())

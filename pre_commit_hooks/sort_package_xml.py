#!/usr/bin/env python

# Copyright 2021 TIER IV, Inc. All rights reserved.
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

# Copyright (c) 2014 pre-commit dev team: Anthony Sottile, Ken Struys

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import argparse
import re
from typing import List
from typing import Optional
from typing import Sequence

# Closing bracket absent as conditions can be present within the xml tag
TAGS = [
    "<build_depend",
    "<build_export_depend",
    "<buildtool_depend",
    "<buildtool_export_depend",
    "<exec_depend",
    "<depend",
    "<doc_depend",
    "<test_depend",
]


def sort(lines: List[str]) -> List[str]:
    """Sort a XML file in alphabetical order, keeping blocks together.

    :param lines: array of strings
    :return: sorted array of strings
    """
    # make a copy of lines since we will clobber it
    lines = list(lines)
    new_lines = []

    for block in parse_blocks(lines):
        new_lines.extend(sorted(block, key=parse_content))

    return new_lines


def parse_block(lines: List[str], tag: str) -> List[str]:
    block_lines = []
    for line in lines:
        if line.strip().startswith(tag):
            block_lines.append(line)
    for line in block_lines:
        lines.remove(line)
    return block_lines


def parse_tag(line: str) -> str:
    for tag in TAGS:
        if line.startswith(tag):
            return tag
    return ""


def parse_blocks(lines: List[str]) -> List[List[str]]:
    """Parse and return all possible blocks, popping off the start of `lines`.

    :param lines: list of lines
    :return: list of blocks, where each block is a list of lines
    """
    blocks = []

    while lines:
        tag = parse_tag(lines[0].strip())
        if tag:
            blocks.append(parse_block(lines, tag))
        else:
            blocks.append([lines.pop(0)])

    return blocks


def parse_content(line: str) -> str:
    reg_obj = re.compile(r"<[^>]*?>")
    return reg_obj.sub("", line)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", help="Filenames to fix")
    args = parser.parse_args(argv)

    ret_val = 0
    for filename in args.filenames:
        with open(filename, "r+") as f:
            lines = [line.rstrip() for line in f.readlines()]
            new_lines = sort(lines)

            if lines != new_lines:
                print(f"Fixing file `{filename}`")
                f.seek(0)
                f.write("\n".join(new_lines) + "\n")
                ret_val = 1

    return ret_val


if __name__ == "__main__":
    exit(main())

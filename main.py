#!/usr/bin/env python3

import glob
import itertools
import os
import re
from typing import Iterable
from typing import Iterator
from typing import Tuple
from typing import Generator


NOTES_DIR = "~/Documents/Brain/Daily"
LINK_PATTERN = re.compile(r'(?<=\[\[)[^]]*(?=\]\])')


def files(path: str = NOTES_DIR) -> Iterator[str]:
    """Return iterator over all the filepaths."""
    expanded_path = os.path.expanduser(path)
    path_pattern = os.path.join(expanded_path, "**", "*.md")

    return glob.iglob(path_pattern, recursive=True)


def read_file(path: str) -> Tuple[str, list[str]]:
    datestring, _ = os.path.splitext(os.path.basename(path))
    with open(path, "r") as file:

        return datestring, file.readlines()


def handle_content(datestr: str, lines: list[str]) -> Generator[Tuple[str, str], None, None]:
    current_path = [datestr]
    for line in lines:
        if line[0] == '#':
            header_indicator, heading = line.rstrip().split(' ', maxsplit=1)
            header_level = len(header_indicator) - 1  # Zerobased levels

            del current_path[header_level:]
            current_path.append(heading)

        else:
            yield from (("/".join(current_path), m)
                        for m in LINK_PATTERN.findall(line))


def group_by_date(tuples: Iterable[Tuple[str, str]]) -> None:
    current_set: set[str] = set()
    current_date: str = ""

    for header_path, link in sorted(tuples):
        datestr, *_ = header_path.split('/', maxsplit=1)

        if current_date != datestr:
            if current_set:
                display_by_date(current_date, current_set)

            current_date = datestr
            current_set = set()

        current_set.add(link)


def display_by_date(datestr: str, links: Iterable[str]):
    print(f"\n- {datestr}")
    for link in sorted(links):
        print(f"  - {link}")


def main() -> None:
    paths = files(path=NOTES_DIR)
    file_content = (read_file(path) for path in paths)
    filtered_content = (handle_content(*file_result) for file_result in file_content)

    group_by_date(itertools.chain(*filtered_content))


if __name__ == "__main__":
    main()

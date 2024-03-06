#!/usr/bin/env python3

import argparse
import glob
import itertools
import os
import re
import sys
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


def date_key(element: Tuple[str, str]) -> str:

    return element[0].split('/', maxsplit=1)[0]


def group_by_date(tuples: Iterable[Tuple[str, str]]) -> None:
    sorted_tuples = sorted(tuples, key=date_key)
    grouped_tuples = itertools.groupby(sorted_tuples, key=date_key)

    for datestr, group in grouped_tuples:
        unique_links = set(link for _, link in group)
        display_as_tree(datestr, unique_links)

    return


def link_key(element: Tuple[str, str]) -> str:

    return element[1]


def group_by_link(tuples: Iterable[Tuple[str, str]]) -> None:
    sorted_tuples = sorted(tuples, key=link_key)
    grouped_tuples = itertools.groupby(sorted_tuples, key=link_key)

    for linkstr, group in grouped_tuples:
        unique_dates = set(map(date_key, group))
        display_as_tree(linkstr, unique_dates)

    return


def display_as_tree(mainitem: str, subitems: Iterable[str]):
    print(f"\n- {mainitem}")
    for link in sorted(subitems):
        print(f"  - {link}")


class argument_converter:
    """Convenience class to wrap argument conversions."""

    def __init__(self, **conversions):
        self.conversions = conversions

    def convert(self, arg) -> None:
        conversions = self.conversions

        if arg in conversions:

            return conversions[arg]

        message = "invalid choice: {!r} ( choose from {})"
        choices = ", ".join(sorted(repr(choice) for choice in conversions.keys()))

        raise argparse.ArgumentTypeError(message.format(arg, choices))

    def __iter__(self):
        yield from self.conversions.keys()


def parse_arguments(args) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    output_group = parser.add_argument_group('output')

    group_by_alternatives = argument_converter(date=group_by_date, link=group_by_link)
    output_group.add_argument('--group-by', default='date',
                              choices=group_by_alternatives)

    result = parser.parse_args(args)
    result.group_by = group_by_alternatives.convert(result.group_by)

    return result


def main() -> None:
    options = parse_arguments(args=sys.argv[1:])
    print(options.group_by)

    paths = files(path=NOTES_DIR)
    file_content = (read_file(path) for path in paths)
    filtered_content = (handle_content(*file_result) for file_result in file_content)

    options.group_by(itertools.chain(*filtered_content))


if __name__ == "__main__":
    main()

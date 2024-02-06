#!/usr/bin/env python3
"""App to spell-check a file. Inspired by Brooke."""

import logging
from pathlib import Path
from string import punctuation

import click

FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging_args = {
    "format": FORMAT,
    "level": logging.INFO,
    "datefmt": "%Y-%m-%d %H:%M:%S",
    "encoding": "utf-8",
}
logging.basicConfig(**logging_args)
logger = logging.getLogger()

SPLITTER = set(f" {punctuation}") - {'_'}

# pylint: disable=logging-fstring-interpolation


def delete_range(lines, r=None):
    """
    >>> a = list(range(10))
    >>> delete_range(a, (1, 3))
    [0, 4, 5, 6, 7, 8, 9]
    r = r or (0, len(lines))
    """
    r = r or (0, len(lines))
    return replace_range(lines, [], (r[0], r[1] + 1))


def insert_range(lines, line_no, new_lines):
    """
    >>> a = list(range(10))
    >>> b = list(range(11, 13))
    >>> insert_range(a, 3, b)
    [0, 1, 2, 11, 12, 3, 4, 5, 6, 7, 8, 9]
    >>> insert_range(a, 0, b)
    [11, 12, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> insert_range(a, 9, b)
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 9]
    """
    return replace_range(lines, new_lines, (line_no, line_no))


def append_range(lines, line_no, new_lines):
    """
    >>> a = list(range(10))
    >>> b = list(range(11, 13))
    >>> append_range(a, 3, b)
    [0, 1, 2, 3, 11, 12, 4, 5, 6, 7, 8, 9]
    >>> append_range(a, 0, b)
    [0, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> append_range(a, 9, b)
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12]
    """
    return replace_range(lines, new_lines, (line_no + 1, line_no + 1))


def replace_range(old_lines, new_lines, r=None):
    """
    >>> a = list(range(10))
    >>> b = list(range(11, 13))
    >>> replace_range(a, b, (0, 2))
    [11, 12, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> replace_range(a, b, (8, 10))
    [0, 1, 2, 3, 4, 5, 6, 7, 11, 12]
    >>> replace_range(a, b, (0, 10))
    [11, 12]
    >>> replace_range(a, [], (0, 10))
    []
    >>> replace_range(a, [], (0, 9))
    [9]
    """
    start, end = r or (0, len(old_lines))
    assert 0 <= start <= end <= len(old_lines)
    return old_lines[:start] + new_lines + old_lines[end:]


class StreamEditor:
    """Class to edit a file programmatically."""
    def __init__(self, filename):
        """Init the object."""
        # logger.debug(f"StreamEditor({filename})")
        self.filename = filename
        self.changes = 0
        with open(filename, encoding="utf-8") as handle:
            self.lines = [line.rstrip() for line in handle]

    def save(self):
        """Save the file with changes."""
        if self.changes:
            msg = f"Saving {self.filename}: {self.changes} changes\n"
            logger.debug(msg)
            with open(self.filename, "w", encoding="utf-8") as handle:
                handle.write("\n".join(self.lines) + "\n")
            self.changes = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()

    def replace_range(self, loc, new_lines):
        """Replace a range of lines with a new set of lines."""
        self.lines = replace_range(self.lines, new_lines, loc)
        self.changes += 1

    def insert_range(self, loc, new_lines):
        """Insert a set of lines at loc."""
        self.lines = insert_range(self.lines, new_lines, loc)
        self.changes += 1

    def append_range(self, loc, new_lines):
        """Append a set of lines at loc."""
        self.lines = append_range(self.lines, new_lines, loc)
        self.changes += 1

    def delete_range(self, loc):
        """Delete the lines at loc."""
        self.lines = delete_range(self.lines, loc)
        self.changes += 1


def words(line: str):
    """
    Convert line to a sequence of words.
    Strange: string.split and re.split do not work the way I would expect or want.
    """
    start = 0
    for i, c in enumerate(line):
        if c in SPLITTER:
            if i > start:
                yield line[start:i].lower()
            start = i + 1
    if start != len(line):
        yield line[start:].lower()


def spell_check_file(filename: str, dictionary: set[str]):
    """Spell check a single file."""
    with StreamEditor(filename) as se:
        for i, line in enumerate(se.lines):
            for word in words(line):
                if word not in dictionary:
                    # logger.info(f"file {filename} line {i + 1} {line = } {word = }")
                    print(f"{'-' * 10} {filename} line {i + 1}")
                    print(f"{line}")
                    response = input(f"Replace {word}? y/n/s/a ")
                    if response == 'a':
                        # Add the word to the in-memory dictionary
                        logger.debug(f"Adding {word} to dictionary")
                        dictionary.add(word)
                    elif response == 'y':
                        # Perform a replacement
                        new_word = input("Replacement word? ")
                        dictionary.add(new_word)
                        new_line = line.replace(word, new_word)
                        se.replace_range((i, i + 1), [new_line])
                    elif response == 's':
                        # Skip the rest of the file
                        return


def load_dict(dict_filename: str) -> set[str]:
    """Load desired dictionary from file."""
    logger.info(f"dictionary file: {dict_filename}")
    with open(dict_filename, encoding='utf-8') as handle:
        return {word.strip() for word in handle}


def spell_check_files(dictionary: set[set]):
    """Spell-check file(s) against the dictionary."""
    logger.info(f"main: {len(dictionary)} words")
    for filename in Path(".").rglob("*"):
        spell_check_file(str(filename), dictionary)


@click.command()
@click.option(
    '-d', '--dict_filename',
    default='/usr/share/dict/words',
    required=False,
    type=str,
)
def main(dict_filename):
    """Main driver."""
    dictionary: set[str] = load_dict(dict_filename)
    spell_check_files(dictionary)


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter

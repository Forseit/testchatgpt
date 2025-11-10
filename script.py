"""
script.py

This script generates a text file whose name consists of a random sequence of
letters, digits and punctuation characters (excluding whitespace) with a
``.txt`` suffix.  The file contains a table of integers with exactly four
numbers per line separated by spaces.  The number of lines and the values
themselves are randomised to ensure a mixture of multi‑digit and single‑digit
entries.

When executed as a standalone program, the script writes the table to the
randomly named file in the current working directory and prints the filename
to standard output.  The filename can then be captured by other programs
(e.g., ``main.py``) to locate and process the generated data.
"""

import random
import string
from pathlib import Path


def generate_filename(length: int = 8) -> str:
    """Return a random filename consisting of ``length`` random characters.

    The characters are chosen from all ASCII letters, digits and punctuation
    characters.  A ``.txt`` suffix is appended to create a text file name.

    Args:
        length: Number of characters to generate before appending ``.txt``.
    Returns:
        A random filename string ending in ``.txt``.
    """
    # Build a character set that avoids characters illegal or problematic in
    # filenames.  Characters such as '/' and '\\' are directory separators
    # and must not appear in the filename.  Colons, asterisks, question marks,
    # quotes and angle brackets are also removed because they are reserved
    # on many operating systems.  We start with all punctuation and then
    # filter out the unwanted ones.
    unsafe = set('/\\:*?"<>|')
    allowed_punctuation = ''.join(ch for ch in string.punctuation if ch not in unsafe)
    chars = string.ascii_letters + string.digits + allowed_punctuation
    name = ''.join(random.choice(chars) for _ in range(length))
    return f"{name}.txt"


def generate_number(min_digits: int = 1, max_digits: int = 6) -> int:
    """Generate a random integer with between ``min_digits`` and ``max_digits`` digits.

    Leading zeros are avoided for numbers with more than one digit to ensure
    predictable length when converted to a string.

    Args:
        min_digits: Minimum number of digits the number should have.
        max_digits: Maximum number of digits the number should have.
    Returns:
        An integer with a random number of digits in the given range.
    """
    if min_digits < 1 or max_digits < min_digits:
        raise ValueError("Digit range is invalid")
    num_digits = random.randint(min_digits, max_digits)
    # For a single digit number, include zero as a valid value.
    if num_digits == 1:
        return random.randint(0, 9)
    # First digit cannot be zero for multi‑digit numbers.
    first_digit = random.randint(1, 9)
    remaining = ''.join(str(random.randint(0, 9)) for _ in range(num_digits - 1))
    return int(f"{first_digit}{remaining}")


def generate_table(rows: int, cols: int = 4) -> list[list[int]]:
    """Generate a table of integers with the specified number of rows and columns.

    Args:
        rows: The number of rows to generate.
        cols: The number of integers per row (default 4).
    Returns:
        A list of lists of integers where each inner list represents a row.
    """
    table = []
    for _ in range(rows):
        row = [generate_number() for _ in range(cols)]
        table.append(row)
    return table


def write_table_to_file(table: list[list[int]], filename: str) -> None:
    """Write the given table of integers to a file as space‑separated values.

    Each row of the table is written on its own line with the numbers
    separated by single spaces.

    Args:
        table: The table of integers to write.
        filename: The name of the file to create.
    """
    path = Path(filename)
    with path.open("w", encoding="utf-8") as f:
        for row in table:
            f.write(' '.join(str(num) for num in row))
            f.write("\n")


def main() -> None:
    """Entry point for script execution.

    Generates a random filename and a table of integers, writes the table to
    that file and prints the filename so that other programs can locate it.
    """
    # Generate 16k lines (16_000) with 4 numbers per line.
    table = generate_table(rows=16_000, cols=4)
    filename = generate_filename()
    write_table_to_file(table, filename)
    # Print the filename for consumption by the caller.
    print(filename)


if __name__ == "__main__":
    main()

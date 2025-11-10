"""Utilities for generating and processing pseudo-random numeric datasets."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Iterable


def run_script(script_path: str = "script.py") -> str:
    """Execute *script_path* with the current interpreter and return the last line.

    Parameters
    ----------
    script_path:
        The path to the script that is expected to print the name of the file
        containing the generated dataset.
    """

    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("No filename returned")
    return lines[-1]


def row_ok(nums: Iterable[int]) -> bool:
    """Return ``True`` when *nums* looks like a valid row from ``script.py``.

    The dataset writer emits rows of four integers with at least one single
    digit value and otherwise multi-digit positive numbers.  The validation is
    intentionally lightweight – the caller only needs a quick sanity check
    before the row contributes to the aggregate.
    """

    numbers = list(nums)
    if len(numbers) != len(set(numbers)):
        return False

    if not numbers:
        return False

    largest = max(numbers)
    if sum(numbers) <= 3 * largest:
        return False

    return any(0 <= number <= 9 for number in numbers)


def process_file(filename: str, *, encoding: str = "utf-8") -> int:
    """Return the sum of all valid rows inside *filename*.

    A *valid* row is one that consists of four integers, passes :func:`row_ok`
    and therefore resembles the data produced by ``script.py``.
    """

    total = 0
    path = Path(filename)
    with path.open(encoding=encoding) as f:
        for line in f:
            parts = line.split()
            if len(parts) != 4:
                continue

            try:
                nums = [int(part) for part in parts]
            except ValueError:
                continue

            if row_ok(nums):
                total += sum(nums)
    return total


def build_parser() -> argparse.ArgumentParser:
    """Create the command line interface for :func:`main`."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--file",
        help="Process an existing dataset instead of running the generator",
    )
    parser.add_argument(
        "--script",
        default="script.py",
        help="Path to the generator script (default: %(default)s)",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Text encoding used when reading the dataset (default: %(default)s)",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> None:
    """Entry point used by the ``__main__`` module and the tests."""

    parser = build_parser()
    args = parser.parse_args(argv)

    filename = args.file or run_script(args.script)
    total = process_file(filename, encoding=args.encoding)
    print(total)


if __name__ == "__main__":
    main()

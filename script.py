"""Sample solution script for the interactive test runner.

The program reads an integer ``n`` that represents the number of values to
follow. It then reads ``n`` integers, one per line or separated by whitespace,
and checks whether the sum of the first two values is strictly greater than the
sum of the remaining values.  The script prints ``"yes"`` when the condition
holds and ``"no"`` otherwise.  The implementation serves as an example target
for the generated tests driven by ``main.py``.

Feel free to replace the implementation with your own solution when using the
GUI runner.
"""
from __future__ import annotations

import sys
import typing


def read_numbers(stream: typing.TextIO) -> list[int]:
    """Return a list of integers from *stream*.

    The first value denotes how many numbers follow.  The remaining values are
    collected regardless of whether they are separated by whitespace or
    newlines.
    """

    content = stream.read().strip()
    if not content:
        raise ValueError("Empty input provided")

    raw_numbers = content.split()
    if len(raw_numbers) < 1:
        raise ValueError("Expected at least one number in the input")

    try:
        count = int(raw_numbers[0])
    except ValueError as exc:
        raise ValueError("The first value must be an integer specifying the count") from exc

    numbers: list[int] = []
    for token in raw_numbers[1:1 + count]:
        try:
            numbers.append(int(token))
        except ValueError as exc:
            raise ValueError(f"Failed to convert '{token}' to int") from exc

    if len(numbers) != count:
        raise ValueError(
            f"Expected {count} numbers after the length prefix, got {len(numbers)}"
        )

    return numbers


def main() -> None:
    numbers = read_numbers(sys.stdin)
    if len(numbers) < 2:
        raise ValueError("Expected at least two numbers to compare their sums")

    first_two_sum = numbers[0] + numbers[1]
    remaining_sum = sum(numbers[2:])
    print("yes" if first_two_sum > remaining_sum else "no")


if __name__ == "__main__":
    main()

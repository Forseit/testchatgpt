"""Dataset generator used by :mod:`main`."""

from __future__ import annotations

import argparse
import random
import string
from pathlib import Path
from typing import Iterable

SAFE_PUNCTUATION = "".join(ch for ch in string.punctuation if ch not in "/\\:*?\"<>|")
DEFAULT_CHARSET = string.ascii_letters + string.digits + SAFE_PUNCTUATION


def generate_filename(length: int = 8, *, rng: random.Random | None = None) -> str:
    """Return a random filename composed of safe ASCII characters."""

    generator = rng or random
    return "".join(generator.choice(DEFAULT_CHARSET) for _ in range(length)) + ".txt"


def generate_row(*, rng: random.Random | None = None) -> list[int]:
    """Create a single row of four integers following the original heuristics."""

    generator = rng or random
    row: list[int] = []
    for _ in range(4):
        digits = generator.randint(1, 6)
        if digits == 1:
            row.append(generator.randint(0, 9))
        else:
            first = generator.randint(1, 9)
            row.append(
                int(
                    str(first)
                    + "".join(str(generator.randint(0, 9)) for _ in range(digits - 1))
                )
            )
    return row


def write_dataset(path: Path, rows: int, *, rng: random.Random | None = None) -> None:
    """Write *rows* generated rows to *path*."""

    generator = rng or random
    with path.open("w", encoding="utf-8") as handle:
        for _ in range(rows):
            row = generate_row(rng=generator)
            handle.write(" ".join(str(number) for number in row) + "\n")


def build_parser() -> argparse.ArgumentParser:
    """Return an :class:`~argparse.ArgumentParser` for the CLI."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rows",
        type=int,
        default=16_000,
        help="Number of rows to generate (default: %(default)s)",
    )
    parser.add_argument(
        "--length",
        type=int,
        default=8,
        help="Length of the generated filename (default: %(default)s)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Seed for the RNG, useful for reproducible datasets",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd(),
        help="Directory where the dataset should be written (default: current directory)",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> None:
    """CLI entry point that creates the dataset and prints the filename."""

    parser = build_parser()
    args = parser.parse_args(argv)

    rng = random.Random(args.seed) if args.seed is not None else random

    args.output_dir.mkdir(parents=True, exist_ok=True)
    filename = generate_filename(args.length, rng=rng if args.seed is not None else None)
    path = args.output_dir / filename
    write_dataset(path, args.rows, rng=rng if args.seed is not None else None)
    print(str(path))


if __name__ == "__main__":
    main()

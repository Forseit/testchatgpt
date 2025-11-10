from __future__ import annotations

import random
from pathlib import Path

import script


def test_generate_filename_length() -> None:
    rng = random.Random(1)
    name = script.generate_filename(length=12, rng=rng)
    assert len(name) == 16  # length plus the ".txt" suffix
    assert name.endswith(".txt")


def test_generate_row_structure() -> None:
    rng = random.Random(2)
    row = script.generate_row(rng=rng)
    assert len(row) == 4
    assert any(0 <= value <= 9 for value in row)


def test_write_dataset(tmp_path: Path) -> None:
    rng = random.Random(3)
    path = tmp_path / "dataset.txt"
    script.write_dataset(path, 10, rng=rng)
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 10
    assert all(len(line.split()) == 4 for line in lines)

from __future__ import annotations

from pathlib import Path

import pytest

import main


def test_row_ok_accepts_valid_rows() -> None:
    assert main.row_ok([500, 498, 497, 7]) is True


def test_row_ok_rejects_duplicates() -> None:
    assert main.row_ok([5, 5, 10, 11]) is False


def test_row_ok_rejects_low_sum() -> None:
    assert main.row_ok([1, 2, 3, 4]) is False


def test_process_file_filters_invalid_lines(tmp_path: Path) -> None:
    dataset = tmp_path / "data.txt"
    dataset.write_text(
        "\n".join(
            [
                "500 498 497 7",  # valid
                "1 2 3",  # not enough columns
                "7 a 1 2",  # invalid integer
                "7 7 7 9",  # duplicates
                "9 12 15 6",  # too small sum
            ]
        ),
        encoding="utf-8",
    )

    assert main.process_file(str(dataset)) == 1502


def test_main_reads_from_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    dataset = tmp_path / "data.txt"
    dataset.write_text("500 498 497 7\n", encoding="utf-8")

    main.main(["--file", str(dataset)])
    captured = capsys.readouterr()
    assert captured.out.strip() == "1502"

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Optional

__all__ = ["TestCase", "ParseError", "parse_cases"]


@dataclass(slots=True)
class TestCase:
    """Representation of a single test case."""

    index: int
    label: str
    input_data: str
    expected_output: Optional[str] = None

    def normalized_input(self) -> str:
        return self.input_data.strip()

    def normalized_expected(self) -> Optional[str]:
        if self.expected_output is None:
            return None
        return self.expected_output.strip()


class ParseError(ValueError):
    """Raised when user-provided test definitions cannot be parsed."""


_COMMENT_PREFIXES = ("#", "//")
_SEPARATOR_TOKENS = {
    "=>",
    "->",
    "EXPECTED:",
    "OUTPUT:",
    "ОЖИДАЕМО:",
    "ОТВЕТ:",
    "ANS:",
    "---",
}


def _split_blocks(raw_text: str) -> List[str]:
    stripped = raw_text.strip()
    if not stripped:
        return []
    return [block.strip() for block in re.split(r"(?:\r?\n){2,}", stripped) if block.strip()]


def _is_comment(line: str) -> bool:
    stripped = line.strip()
    return any(stripped.startswith(prefix) for prefix in _COMMENT_PREFIXES)


def _extract_label(lines: Iterable[str]) -> Optional[str]:
    for line in lines:
        stripped = line.strip()
        for prefix in _COMMENT_PREFIXES:
            if stripped.startswith(prefix):
                value = stripped[len(prefix) :].strip()
                if value:
                    return value
    return None


def _split_input_output(lines: List[str]) -> tuple[List[str], Optional[List[str]]]:
    for index, line in enumerate(lines):
        if line.strip().upper() in _SEPARATOR_TOKENS:
            return lines[:index], lines[index + 1 :]
    return lines, None


def parse_cases(raw_text: str) -> List[TestCase]:
    """Parse raw text describing a suite of tests.

    Each test case is separated by one or more blank lines.  Lines that begin
    with ``#`` or ``//`` are treated as comments and are used to derive the test
    label.  To provide an expected output, insert a separator line containing
    one of the tokens defined in ``_SEPARATOR_TOKENS`` (for example ``=>`` or
    ``EXPECTED:``).  Content after the separator becomes the expected output.
    """

    blocks = _split_blocks(raw_text)
    cases: List[TestCase] = []

    for index, block in enumerate(blocks, start=1):
        lines = [line.rstrip("\n") for line in block.splitlines()]
        label = _extract_label(lines) or f"Тест {index}"

        payload_lines = [line for line in lines if not _is_comment(line)]
        input_lines, expected_lines = _split_input_output(payload_lines)
        input_data = "\n".join(line.rstrip() for line in input_lines).strip()

        if not input_data:
            raise ParseError(
                f"Тест {index} не содержит входных данных. Добавьте хотя бы одну строку входа."
            )

        expected_output = None
        if expected_lines is not None:
            expected_output = "\n".join(line.rstrip() for line in expected_lines).strip()
            if expected_output == "":
                expected_output = None

        # Ensure there is a trailing newline so subprocess input behaves as expected.
        if not input_data.endswith("\n"):
            input_data = f"{input_data}\n"

        if expected_output is not None and not expected_output.endswith("\n"):
            expected_output = f"{expected_output}\n"

        cases.append(
            TestCase(
                index=index,
                label=label,
                input_data=input_data,
                expected_output=expected_output,
            )
        )

    return cases

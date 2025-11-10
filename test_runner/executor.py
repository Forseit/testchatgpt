from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from .cases import TestCase

__all__ = ["TestResult", "run_test_cases"]


@dataclass(slots=True)
class TestResult:
    case: TestCase
    status: str
    stdout: str
    stderr: str
    elapsed: float
    message: str

    @property
    def has_error(self) -> bool:
        return self.status in {"error", "failed"}


def _normalize(text: str) -> str:
    return text.strip()


def run_test_cases(
    test_cases: Iterable[TestCase],
    script_path: Path,
    *,
    timeout: float | None = None,
) -> List[TestResult]:
    results: List[TestResult] = []
    script = script_path.resolve()

    for case in test_cases:
        start = time.perf_counter()
        try:
            completed = subprocess.run(
                [sys.executable, str(script)],
                input=case.input_data,
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False,
            )
            elapsed = time.perf_counter() - start
        except subprocess.TimeoutExpired:
            message = "Превышено время ожидания"
            results.append(
                TestResult(
                    case=case,
                    status="error",
                    stdout="",
                    stderr="",
                    elapsed=timeout if timeout is not None else float("nan"),
                    message=message,
                )
            )
            continue

        stdout = completed.stdout
        stderr = completed.stderr
        normalized_stdout = _normalize(stdout)

        if completed.returncode != 0:
            status = "error"
            message = (
                "Скрипт завершился с ошибкой. "
                f"Код выхода: {completed.returncode}."
            )
        elif case.expected_output is not None:
            expected = _normalize(case.expected_output)
            if normalized_stdout == expected:
                status = "passed"
                message = "Вывод совпадает с ожидаемым"
            else:
                status = "failed"
                message = "Вывод отличается от ожидаемого"
        else:
            status = "executed"
            message = "Скрипт выполнен успешно"

        results.append(
            TestResult(
                case=case,
                status=status,
                stdout=stdout,
                stderr=stderr,
                elapsed=elapsed,
                message=message,
            )
        )

    return results

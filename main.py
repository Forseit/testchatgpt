"""
main.py

This program orchestrates execution of ``script.py`` and post‑processes the
generated data.  It spawns ``script.py`` as a subprocess to generate a
randomly named table file, captures the filename from the child process
output, reads the file, and computes the sum of rows that satisfy a set of
conditions:

1. The sum of all numbers in the row is strictly greater than three times
   the largest number in that row.
2. No numbers are repeated within the row (all four numbers are distinct).
3. At least one of the numbers in the row is a single‑digit integer.

If a row meets all three criteria, its numbers are added together and
contributed to the total.  After processing all rows, the total is printed
to standard output.
"""

import subprocess
import sys
from pathlib import Path


def run_script(script_path: str = "script.py") -> str:
    """Execute the given script and return the filename it outputs.

    The script is expected to print the name of the file it generates on
    standard output.  Only the last line of stdout is interpreted as the
    filename.  If the script fails or produces no output, a RuntimeError
    is raised.

    Args:
        script_path: Path to the script to execute.
    Returns:
        The filename printed by the script.
    """
    # Run the script using the same Python interpreter that runs this program.
    result = subprocess.run([
        sys.executable,
        script_path,
    ], capture_output=True, text=True)

    if result.returncode != 0:
        # Include stderr in the exception to aid debugging.
        raise RuntimeError(f"Error running {script_path}: {result.stderr.strip()}")

    # Extract the filename from the last non‑empty line of stdout.
    stdout_lines = [line for line in result.stdout.splitlines() if line.strip()]
    if not stdout_lines:
        raise RuntimeError(f"{script_path} did not produce any output")
    filename = stdout_lines[-1].strip()
    return filename


def row_qualifies(numbers: list[int]) -> bool:
    """Determine whether a row meets the specified criteria.

    Conditions checked:

    1. Total sum is greater than three times the maximum value.
    2. All numbers in the row are distinct (no repeats).
    3. At least one number is a single‑digit integer (0 through 9).

    Args:
        numbers: List of integers representing a row.
    Returns:
        True if the row satisfies all criteria, False otherwise.
    """
    if not numbers:
        return False
    max_val = max(numbers)
    total = sum(numbers)
    # Condition 1: sum of row > 3 * maximum value
    if not (total > 3 * max_val):
        return False
    # Condition 2: all numbers are distinct
    if len(set(numbers)) != len(numbers):
        return False
    # Condition 3: at least one single‑digit number
    if not any(0 <= n <= 9 for n in numbers):
        return False
    return True


def process_file(filename: str) -> int:
    """Read the table from ``filename`` and sum qualifying rows.

    Args:
        filename: Path to the file containing space‑separated numbers.
    Returns:
        The total sum of all numbers from rows that meet the criteria.
    """
    path = Path(filename)
    if not path.is_file():
        raise FileNotFoundError(f"Cannot find generated file: {filename}")

    total_sum = 0
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            # Skip empty lines or lines with the wrong number of columns
            if len(parts) != 4:
                continue
            try:
                numbers = [int(part) for part in parts]
            except ValueError:
                # Ignore lines containing non‑numeric data
                continue
            if row_qualifies(numbers):
                total_sum += sum(numbers)
    return total_sum


def main() -> None:
    """Main entry point of the program.

    Runs ``script.py`` to generate the data file, processes the file to
    compute the required total and prints the result.
    """
    filename = run_script()
    total = process_file(filename)
    print(total)


if __name__ == "__main__":
    main()
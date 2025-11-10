import subprocess
import sys
from pathlib import Path


def run_script(script_path: str = 'script.py') -> str:
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    lines = [l for l in result.stdout.splitlines() if l.strip()]
    if not lines:
        raise RuntimeError('No filename returned')
    return lines[-1].strip()


def row_ok(nums: list[int]) -> bool:
    m = max(nums)
    if sum(nums) <= 3 * m:
        return False
    if len(set(nums)) != len(nums):
        return False
    return any(0 <= n <= 9 for n in nums)


def process_file(filename: str) -> int:
    total = 0
    path = Path(filename)
    with path.open() as f:
        for line in f:
            parts = line.split()
            if len(parts) != 4:
                continue
            try:
                nums = [int(p) for p in parts]
            except ValueError:
                continue
            if row_ok(nums):
                total += sum(nums)
    return total


def main() -> None:
    fname = run_script()
    total = process_file(fname)
    print(total)


if __name__ == '__main__':
    main()
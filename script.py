import random
import string
from pathlib import Path


def generate_filename(length: int = 8) -> str:
    safe_punctuation = ''.join(ch for ch in string.punctuation if ch not in '/\\:*?"<>|')
    chars = string.ascii_letters + string.digits + safe_punctuation
    return ''.join(random.choice(chars) for _ in range(length)) + '.txt'


def generate_row() -> list[int]:
    row = []
    for _ in range(4):
        digits = random.randint(1, 6)
        if digits == 1:
            row.append(random.randint(0, 9))
        else:
            first = random.randint(1, 9)
            row.append(int(str(first) + ''.join(str(random.randint(0, 9)) for _ in range(digits - 1))))
    return row


def main() -> None:
    filename = generate_filename()
    with Path(filename).open('w', encoding='utf-8') as f:
        for _ in range(16_000):
            row = generate_row()
            f.write(' '.join(str(n) for n in row) + '\n')
    print(filename)


if __name__ == '__main__':
    main()
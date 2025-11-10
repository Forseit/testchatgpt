from __future__ import annotations

import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Optional, Sequence, Tuple

from test_runner import (
    TestCase,
    TestResult,
    ensure_pytest_available,
    generate_pytest_file,
    parse_cases,
    run_test_cases,
)
from test_runner.cases import ParseError

WINDOW_MIN_WIDTH = 960
WINDOW_MIN_HEIGHT = 720
DEFAULT_TIMEOUT = 5.0


class Application(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Генератор тестов для Python-скриптов")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        cwd = Path.cwd()
        default_script = cwd / "script.py"
        default_tests_dir = cwd / "tests"

        self.script_path_var = tk.StringVar(value=str(default_script.resolve()))
        self.tests_dir_var = tk.StringVar(value=str(default_tests_dir.resolve()))
        self.test_filename_var = tk.StringVar(value="test_generated.py")
        self.timeout_var = tk.DoubleVar(value=DEFAULT_TIMEOUT)

        self.case_count_var = tk.IntVar(value=3)
        self.sequence_length_var = tk.IntVar(value=5)
        self.start_value_var = tk.IntVar(value=1)
        self.step_var = tk.IntVar(value=1)
        self.arrangement_var = tk.StringVar()
        self.include_length_var = tk.BooleanVar(value=True)
        self.include_expected_var = tk.BooleanVar(value=True)

        self._arrangement_options = {
            "column": "По одному в строке",
            "space": "Через пробел",
            "comma": "Через запятую",
        }
        self.arrangement_var.set(self._arrangement_options["column"])

        self._build_layout()
        self._generate_sample_tests()

    # ------------------------------------------------------------------ UI
    def _build_layout(self) -> None:
        container = ttk.Frame(self, padding=12)
        container.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)

        self._build_file_section(container)
        self._build_generator_section(container)
        self._build_text_section(container)
        self._build_buttons(container)

    def _build_file_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Файлы", padding=10)
        frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0, 12))
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Скрипт с решением:").grid(row=0, column=0, sticky="w")
        entry = ttk.Entry(frame, textvariable=self.script_path_var)
        entry.grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(frame, text="Обзор", command=self._choose_script).grid(row=0, column=2)

        ttk.Label(frame, text="Папка для test.py:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        dir_entry = ttk.Entry(frame, textvariable=self.tests_dir_var)
        dir_entry.grid(row=1, column=1, sticky="ew", padx=8, pady=(8, 0))
        ttk.Button(frame, text="Выбрать", command=self._choose_directory).grid(row=1, column=2, pady=(8, 0))

        ttk.Label(frame, text="Имя файла тестов:").grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(frame, textvariable=self.test_filename_var).grid(row=2, column=1, sticky="ew", padx=8, pady=(8, 0))

        ttk.Label(frame, text="Тайм-аут (сек):").grid(row=3, column=0, sticky="w", pady=(8, 0))
        ttk.Spinbox(frame, textvariable=self.timeout_var, from_=0.0, to=60.0, increment=0.5, width=8).grid(
            row=3, column=1, sticky="w", padx=8, pady=(8, 0)
        )

    def _build_generator_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Настройки генератора", padding=10)
        frame.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        for col in range(4):
            frame.columnconfigure(col, weight=1)

        ttk.Label(frame, text="Количество тестов:").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(frame, from_=1, to=1000, textvariable=self.case_count_var, width=6).grid(
            row=0, column=1, sticky="w", padx=(0, 12)
        )

        ttk.Label(frame, text="Чисел в тесте:").grid(row=0, column=2, sticky="w")
        ttk.Spinbox(frame, from_=1, to=1000, textvariable=self.sequence_length_var, width=6).grid(
            row=0, column=3, sticky="w"
        )

        ttk.Label(frame, text="Начальное число:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Spinbox(frame, from_=-10_000, to=10_000, textvariable=self.start_value_var, width=8).grid(
            row=1, column=1, sticky="w", padx=(0, 12), pady=(8, 0)
        )

        ttk.Label(frame, text="Шаг:").grid(row=1, column=2, sticky="w", pady=(8, 0))
        ttk.Spinbox(frame, from_=-1000, to=1000, textvariable=self.step_var, width=6).grid(
            row=1, column=3, sticky="w", pady=(8, 0)
        )

        ttk.Label(frame, text="Формат чисел:").grid(row=2, column=0, sticky="w", pady=(8, 0))
        menu = ttk.OptionMenu(
            frame,
            self.arrangement_var,
            self._arrangement_options["column"],
            *self._arrangement_options.values(),
        )
        menu.grid(row=2, column=1, sticky="w", padx=(0, 12), pady=(8, 0))

        ttk.Checkbutton(
            frame,
            text="Добавлять количество чисел в первой строке",
            variable=self.include_length_var,
        ).grid(row=2, column=2, columnspan=2, sticky="w", pady=(8, 0))

        ttk.Checkbutton(
            frame,
            text="Добавлять ожидаемый ответ (сумма)",
            variable=self.include_expected_var,
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(8, 0))

        ttk.Button(frame, text="Сгенерировать примеры", command=self._generate_sample_tests).grid(
            row=3, column=2, columnspan=2, sticky="e", pady=(8, 0)
        )

    def _build_text_section(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Определение тестов", padding=10)
        frame.grid(row=2, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        description = (
            "Каждый тест отделяется пустой строкой. Строки, начинающиеся с #,"
            " используются как комментарии и имя теста. Чтобы указать ожидаемый"
            " ответ, добавьте строку '=>' и поместите вывод ниже. Пример:\n\n"
            "# Тест 1\n5\n1\n0\n1\n2\n0\n=>\n3\n"
        )
        ttk.Label(frame, text=description, justify="left", wraplength=WINDOW_MIN_WIDTH - 80).grid(
            row=0, column=0, sticky="w"
        )

        text_frame = ttk.Frame(frame)
        text_frame.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        self.tests_text = tk.Text(text_frame, wrap=tk.NONE, font=("Fira Code", 11))
        self.tests_text.grid(row=0, column=0, sticky="nsew")

        y_scroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.tests_text.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll = ttk.Scrollbar(text_frame, orient="horizontal", command=self.tests_text.xview)
        x_scroll.grid(row=1, column=0, sticky="ew")

        self.tests_text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

    def _build_buttons(self, parent: ttk.Frame) -> None:
        frame = ttk.Frame(parent)
        frame.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        frame.columnconfigure(0, weight=1)

        ttk.Button(frame, text="Создать test.py и запустить", command=self._generate_and_run).grid(
            row=0, column=1, sticky="e"
        )
        ttk.Button(frame, text="Выход", command=self.destroy).grid(row=0, column=2, padx=(12, 0))

    # ----------------------------------------------------------------- events
    def _choose_script(self) -> None:
        path = filedialog.askopenfilename(
            title="Выберите script.py",
            filetypes=[("Python", "*.py"), ("Все файлы", "*.*")],
        )
        if path:
            self.script_path_var.set(path)

    def _choose_directory(self) -> None:
        path = filedialog.askdirectory(title="Папка для файла test.py")
        if path:
            self.tests_dir_var.set(path)

    def _generate_sample_tests(self) -> None:
        count = max(1, self.case_count_var.get())
        length = max(1, self.sequence_length_var.get())
        start = self.start_value_var.get()
        step = self.step_var.get() or 1
        arrangement_key = next(
            (key for key, label in self._arrangement_options.items() if label == self.arrangement_var.get()),
            "column",
        )

        lines = []
        current = start
        for index in range(count):
            lines.append(f"# Тест {index + 1}")
            if self.include_length_var.get():
                lines.append(str(length))

            numbers = [str(current + offset * step) for offset in range(length)]
            current += length * step

            if arrangement_key == "column":
                lines.extend(numbers)
            elif arrangement_key == "space":
                lines.append(" ".join(numbers))
            else:
                lines.append(",".join(numbers))

            if self.include_expected_var.get():
                values = [int(value) for value in numbers]
                lines.append("=>")
                if len(values) >= 2:
                    first_two_sum = values[0] + values[1]
                    remaining_sum = sum(values[2:])
                    expected = "yes" if first_two_sum > remaining_sum else "no"
                else:
                    expected = "<недостаточно данных>"
                lines.append(expected)

            lines.append("")

        text = "\n".join(lines).strip() + "\n"
        self.tests_text.delete("1.0", tk.END)
        self.tests_text.insert(tk.END, text)

    def _generate_and_run(self) -> None:
        script_path = Path(self.script_path_var.get()).expanduser()
        if not script_path.exists():
            messagebox.showerror("Ошибка", f"Файл {script_path} не найден")
            return

        tests_dir = Path(self.tests_dir_var.get()).expanduser()
        tests_dir.mkdir(parents=True, exist_ok=True)

        filename = self.test_filename_var.get().strip()
        if not filename:
            messagebox.showerror("Ошибка", "Укажите имя файла тестов")
            return

        if not filename.endswith(".py"):
            filename += ".py"

        test_file = tests_dir / filename

        timeout_value = self.timeout_var.get()
        timeout = timeout_value if timeout_value > 0 else None

        raw_text = self.tests_text.get("1.0", tk.END)
        try:
            test_cases = parse_cases(raw_text)
        except ParseError as exc:
            messagebox.showerror("Ошибка разбора", str(exc))
            return

        if not test_cases:
            messagebox.showwarning("Нет тестов", "Добавьте хотя бы один тест")
            return

        try:
            ensure_pytest_available()
        except Exception as exc:  # pragma: no cover - GUI feedback
            messagebox.showerror(
                "pytest",
                "Не удалось установить pytest автоматически.\n"
                f"{exc}",
            )
            return

        try:
            generate_pytest_file(test_cases, script_path, test_file, timeout=timeout)
        except Exception as exc:
            messagebox.showerror("Ошибка", f"Не удалось создать файл тестов:\n{exc}")
            return

        try:
            results = run_test_cases(test_cases, script_path, timeout=timeout)
        except Exception as exc:
            messagebox.showerror("Ошибка выполнения", str(exc))
            return

        pytest_data = self._run_pytest_if_needed(test_cases, test_file)
        ResultsWindow(self, results, test_file, pytest_data)

    def _run_pytest_if_needed(
        self, test_cases: Sequence[TestCase], test_file: Path
    ) -> Optional[Tuple[int, str]]:
        if not any(case.expected_output for case in test_cases):
            return None

        try:
            completed = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_file)],
                capture_output=True,
                text=True,
            )
        except Exception as exc:  # pragma: no cover - GUI feedback
            messagebox.showwarning("pytest", f"Не удалось запустить pytest: {exc}")
            return None

        output = completed.stdout + "\n" + completed.stderr
        return completed.returncode, output


class ResultsWindow(tk.Toplevel):
    def __init__(
        self,
        master: tk.Tk,
        results: Sequence[TestResult],
        test_file: Path,
        pytest_data: Optional[Tuple[int, str]],
    ) -> None:
        super().__init__(master)
        self.title("Результаты тестирования")
        self.geometry("960x640")

        self._results = list(results)
        self._pytest_data = pytest_data

        container = ttk.Frame(self, padding=12)
        container.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        ttk.Label(container, text=f"Создан файл: {test_file}").grid(row=0, column=0, sticky="w")

        self._build_table(container)
        self._build_details(container)
        if pytest_data is not None:
            self._build_pytest(container)

    def _build_table(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Сводка", padding=10)
        frame.grid(row=1, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        columns = ("label", "status", "time", "stdout", "message")
        self.tree: ttk.Treeview = ttk.Treeview(
            frame,
            columns=columns,
            show="tree headings",
            height=12,
        )
        self.tree.heading("#0", text="№")
        self.tree.column("#0", width=50, anchor=tk.CENTER)

        headers = {
            "label": "Название",
            "status": "Статус",
            "time": "Время (с)",
            "stdout": "Вывод",
            "message": "Комментарий",
        }

        widths = {
            "label": 220,
            "status": 120,
            "time": 100,
            "stdout": 260,
            "message": 260,
        }

        for column in columns:
            self.tree.heading(column, text=headers[column])
            self.tree.column(column, width=widths[column], anchor=tk.W)

        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        x_scroll.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")

        for result in self._results:
            stdout_preview = result.stdout.strip().replace("\n", " ⏎ ")
            if len(stdout_preview) > 60:
                stdout_preview = stdout_preview[:57] + "…"
            self.tree.insert(
                "",
                "end",
                text=str(result.case.index),
                values=(
                    result.case.label,
                    self._translate_status(result.status),
                    f"{result.elapsed:.4f}",
                    stdout_preview,
                    result.message,
                ),
            )

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        if self._results:
            first_item = self.tree.get_children()[0]
            self.tree.selection_set(first_item)
            self.tree.focus(first_item)
            self._on_select()

    def _build_details(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Детали", padding=10)
        frame.grid(row=2, column=0, sticky="nsew", pady=(12, 0))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        self.detail_text = tk.Text(frame, wrap=tk.NONE, height=10, font=("Fira Code", 11))
        self.detail_text.grid(row=0, column=0, sticky="nsew")

        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=self.detail_text.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.detail_text.xview)
        x_scroll.grid(row=1, column=0, sticky="ew")

        self.detail_text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.detail_text.configure(state="disabled")

    def _build_pytest(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="pytest", padding=10)
        frame.grid(row=3, column=0, sticky="nsew", pady=(12, 0))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        text = tk.Text(frame, wrap=tk.NONE, height=10, font=("Fira Code", 11))
        text.grid(row=0, column=0, sticky="nsew")

        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=text.xview)
        x_scroll.grid(row=1, column=0, sticky="ew")
        text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        assert self._pytest_data is not None
        exit_code, output = self._pytest_data
        text.insert(tk.END, f"Код выхода: {exit_code}\n\n{output.strip()}\n")
        text.configure(state="disabled")

    def _on_select(self, _event: Optional[tk.Event] = None) -> None:
        selection = self.tree.selection()
        if not selection:
            return

        index = self.tree.index(selection[0])
        result = self._results[index]
        lines = [
            f"Тест №{result.case.index}: {result.case.label}",
            f"Статус: {self._translate_status(result.status)}",
            f"Время выполнения: {result.elapsed:.4f} с",
            "",
            "Входные данные:",
            result.case.input_data.rstrip() or "<пусто>",
            "",
            "Вывод скрипта:",
            result.stdout.rstrip() or "<пусто>",
            "",
            "Стандартная ошибка:",
            result.stderr.rstrip() or "<пусто>",
            "",
            "Комментарий:",
            result.message,
        ]
        if result.case.expected_output:
            lines.extend(
                [
                    "",
                    "Ожидаемый вывод:",
                    result.case.expected_output.rstrip(),
                ]
            )

        self.detail_text.configure(state="normal")
        self.detail_text.delete("1.0", tk.END)
        self.detail_text.insert(tk.END, "\n".join(lines))
        self.detail_text.configure(state="disabled")

    @staticmethod
    def _translate_status(status: str) -> str:
        mapping = {
            "passed": "Совпадает",
            "failed": "Не совпадает",
            "error": "Ошибка",
            "executed": "Выполнено",
        }
        return mapping.get(status, status)


def main() -> None:
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()

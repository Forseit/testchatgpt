# testchatgpt

Utilities for generating random numeric datasets and aggregating them.

## Usage

### Generating a dataset

```
python script.py --rows 500 --seed 1234
```

The command prints the absolute path to the generated file.  Additional useful
flags:

* `--length`: length of the random filename (default `8`).
* `--output-dir`: directory where the file should be stored.
* `--seed`: make generation deterministic.

### Processing a dataset

```
python main.py --file /path/to/dataset.txt
```

If the `--file` argument is omitted the program executes `script.py` (or the
path provided via `--script`) and expects the generator to print the dataset
filename.

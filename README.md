# pdf-chunker

Splits a large PDF into parts no bigger than a size limit (30 MB by default), breaking only on page boundaries. Output files are named `<name>_part001.pdf`, `<name>_part002.pdf`, ...

## Install

```bash
git clone https://github.com/<your-username>/pdf-chunker.git
cd pdf-chunker
pip install pypdf
```

## Usage

```bash
python pdf-chunker.py [-o OUT_DIR] [-m MAX_MB] <input.pdf>
```

- `-o`, `--out-dir`: output directory (default: next to the input)
- `-m`, `--max-mb`: max size per part in MB (default: `30`)

Example:

```bash
python pdf-chunker.py big.pdf -o out -m 10
```

#!/usr/bin/env python3
"""Split a PDF into chunks of at most N MB each.

Output files are named: <name>_part001.pdf, <name>_part002.pdf, ...

Usage:
    python split_pdf.py big.pdf
    python split_pdf.py big.pdf -o out_dir -m 30

Requires: pip install pypdf
"""

import argparse
import io
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter


def build_chunk(reader, start, end):
    """Serialize pages [start, end) into an in-memory PDF and return the bytes."""
    writer = PdfWriter()
    for i in range(start, end):
        writer.add_page(reader.pages[i])
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def split_pdf(src, out_dir, max_mb=30.0):
    src = Path(src)
    out_dir = Path(out_dir) if out_dir else src.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    limit = int(max_mb * 1024 * 1024)
    reader = PdfReader(str(src))
    total = len(reader.pages)
    if total == 0:
        sys.exit("PDF has no pages.")

    # Initial guess of bytes/page from the whole file (refined after each chunk).
    bytes_per_page = max(src.stat().st_size / total, 1)
    width = max(3, len(str(total)))  # zero-pad part numbers
    start, part = 0, 1
    written = []

    while start < total:
        # Aim a bit under the limit, since pages share resources unevenly.
        count = max(1, min(total - start, int(limit * 0.9 / bytes_per_page)))

        while True:
            data = build_chunk(reader, start, start + count)
            if len(data) <= limit:
                break
            if count == 1:
                print(
                    f"WARNING: page {start + 1} alone is "
                    f"{len(data) / 1024 / 1024:.1f} MB (> {max_mb} MB); "
                    f"writing it as its own part anyway.",
                    file=sys.stderr,
                )
                break
            # Shrink proportionally to how far over we were, always by >= 1 page.
            count = max(1, min(count - 1, int(count * limit * 0.95 / len(data))))

        out = out_dir / f"{src.stem}_part{part:0{width}d}.pdf"
        out.write_bytes(data)
        written.append(out)
        print(
            f"{out.name}: pages {start + 1}-{start + count} "
            f"({len(data) / 1024 / 1024:.2f} MB)"
        )

        bytes_per_page = max(len(data) / count, 1)
        start += count
        part += 1

    print(f"Done: {len(written)} part(s) written to {out_dir}")
    return written


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Split a PDF into <= N MB chunks.")
    p.add_argument("pdf", help="input PDF file")
    p.add_argument("-o", "--out-dir", help="output directory (default: next to input)")
    p.add_argument(
        "-m",
        "--max-mb",
        type=float,
        default=30.0,
        help="max size per chunk in MB (default: 30)",
    )
    a = p.parse_args()
    split_pdf(a.pdf, a.out_dir, a.max_mb)

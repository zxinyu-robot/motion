#!/usr/bin/env python3
"""Generate Ca patent disclosure Word document (wrapper for batch script)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_patent_packages import CASES, generate_docx  # noqa: E402


def main() -> int:
    case = next(c for c in CASES if c.key == "Ca")
    generate_docx(case)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

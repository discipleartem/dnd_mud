#!/usr/bin/env python3
"""CLI: валидация YAML-каталогов против JSON Schema v1."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_data_schema.py",
            "-q",
        ],
        cwd=root,
        check=False,
    )
    return int(result.returncode)


if __name__ == "__main__":
    raise SystemExit(main())

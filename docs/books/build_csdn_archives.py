from __future__ import annotations

import runpy
from pathlib import Path


NEW_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "archives" / "build_csdn_archives.py"


if __name__ == "__main__":
    runpy.run_path(str(NEW_SCRIPT), run_name="__main__")

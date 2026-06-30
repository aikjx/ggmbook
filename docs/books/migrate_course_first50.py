from __future__ import annotations

from pathlib import Path


LEGACY_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "archives" / "legacy" / "migrate_course_first50.py"


raise SystemExit(
    "DEPRECATED: `docs/books/migrate_course_first50.py` 已废弃。"
    f"如需参考旧实现，请查看 `{LEGACY_SCRIPT}`，并优先收敛到正式命令体系。"
)

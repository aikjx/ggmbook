from __future__ import annotations

from pathlib import Path


LEGACY_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "archives" / "legacy" / "copy_articles.py"


raise SystemExit(
    "DEPRECATED: `docs/books/copy_articles.py` 已废弃。"
    f"历史脚本已迁移到 `{LEGACY_SCRIPT}`，禁止继续作为正式入口执行。"
)

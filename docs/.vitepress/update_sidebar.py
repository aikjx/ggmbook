from __future__ import annotations

from pathlib import Path


LEGACY_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "archives" / "legacy" / "update_sidebar.py"


raise SystemExit(
    "DEPRECATED: `docs/.vitepress/update_sidebar.py` 已废弃。"
    f"历史脚本已迁移到 `{LEGACY_SCRIPT}`，当前项目禁止再通过该脚本改写 `config.ts`。"
)

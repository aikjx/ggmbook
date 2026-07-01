from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


def load_archives_module():
    module_path = Path(__file__).resolve().with_name("build_csdn_archives.py")
    spec = importlib.util.spec_from_file_location("build_csdn_archives_impl", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载归档脚本：{module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


archives = load_archives_module()


def collect_existing_ids() -> list[str]:
    ids: set[str] = set()
    for key in archives.CATEGORIES:
        archive_dir = archives.ZH_BOOKS_DIR / key / "articles"
        if not archive_dir.exists():
            continue
        for child in archive_dir.iterdir():
            if not child.is_dir():
                continue
            if not child.name.isdigit():
                continue
            if not (child / "index.md").exists():
                continue
            ids.add(child.name)
    return sorted(ids, key=int)


def main() -> None:
    only_ids = collect_existing_ids()
    print(f"selected={len(only_ids)}")
    archives.build_archives(
        limit=None,
        only_ids=only_ids,
        download_images=False,
        purge=True,
        progress_every=20,
    )


if __name__ == "__main__":
    main()

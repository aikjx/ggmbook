from __future__ import annotations

import build_csdn_archives as archives


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
        purge=False,
        progress_every=20,
    )


if __name__ == "__main__":
    main()

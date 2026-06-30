from __future__ import annotations

import argparse
import re
from pathlib import Path

import build_csdn_archives as archives


LECTURE_MIN = 1
LECTURE_MAX = 50


def extract_article_id(path: Path) -> int | None:
    match = re.search(r"-(\d+)\.md$", path.name)
    if not match:
        return None
    return int(match.group(1))


def extract_lecture_number(content: str) -> int | None:
    match = re.search(r"第\s*(\d{1,3})\s*讲", content)
    if not match:
        return None
    return int(match.group(1))


def select_course_ids(*, skip_existing: bool) -> tuple[list[str], list[int]]:
    chosen: dict[int, tuple[int, Path]] = {}
    all_detected_lectures: set[int] = set()
    existing_ids: set[str] = set()
    if skip_existing:
        archive_dir = archives.ZH_BOOKS_DIR / "course" / "articles"
        if archive_dir.exists():
            existing_ids = {item.name for item in archive_dir.iterdir() if item.is_dir()}
    for path in sorted(archives.SOURCE_DIR.glob("*.md")):
        content = archives.read_text(path)
        if "人类文明进阶200讲" not in content and "全域数学vs传统数学" not in content:
            continue
        lecture = extract_lecture_number(content)
        article_id = extract_article_id(path)
        if lecture is None or article_id is None:
            continue
        if not (LECTURE_MIN <= lecture <= LECTURE_MAX):
            continue
        all_detected_lectures.add(lecture)
        if skip_existing and str(article_id) in existing_ids:
            continue
        current = chosen.get(lecture)
        if current is None or article_id > current[0]:
            chosen[lecture] = (article_id, path)

    missing = [lecture for lecture in range(LECTURE_MIN, LECTURE_MAX + 1) if lecture not in all_detected_lectures]
    only_ids = [str(chosen[lecture][0]) for lecture in sorted(chosen)]
    return only_ids, missing


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-download-images", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    only_ids, missing = select_course_ids(skip_existing=args.skip_existing)
    print(f"selected={len(only_ids)}")
    if missing:
        print("missing=" + ",".join(str(item) for item in missing))
    archives.build_archives(
        limit=None,
        only_ids=only_ids,
        download_images=not args.no_download_images,
        purge=False,
        progress_every=10,
    )


if __name__ == "__main__":
    main()

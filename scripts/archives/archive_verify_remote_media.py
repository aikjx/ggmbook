from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


REMOTE_MEDIA_PATTERN = re.compile(
    r"!\[[^\]]*\]\((?:https?://|//)[^)]+\)"
    r"|<img[^>]*\ssrc=['\"](?:https?://|//)[^'\"]+['\"]"
    r"|<video[^>]*\ssrc=['\"](?:https?://|//)[^'\"]+['\"]"
    r"|<audio[^>]*\ssrc=['\"](?:https?://|//)[^'\"]+['\"]"
    r"|<source[^>]*\ssrc=['\"](?:https?://|//)[^'\"]+['\"]"
    r"|^\s*\[[^\]]+\]:\s*(?:https?://|//)\S+"
    r"|<a[^>]*\shref=['\"](?:https?://|//)[^'\"]+\.(?:mp4|webm|mov|m4v|mp3|wav|ogg|m4a)(?:\?[^'\"]*)?['\"]"
    r"|\[[^\]]+\]\((?:https?://|//)[^)]+\.(?:mp4|webm|mov|m4v|mp3|wav|ogg|m4a)(?:\?[^)]*)?\)"
    r"|\b(?:cover|poster)=['\"](?:https?://|//)[^'\"]+['\"]",
    re.IGNORECASE | re.MULTILINE,
)


def iter_markdown_files(targets: list[Path]) -> list[Path]:
    files: set[Path] = set()
    for target in targets:
        if target.is_file() and target.suffix.lower() == ".md":
            files.add(target.resolve())
            continue
        if target.is_dir():
            for path in target.rglob("*.md"):
                if path.is_file():
                    files.add(path.resolve())
    return sorted(files)


def main(args: argparse.Namespace | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="扫描 Markdown 页面中的远程媒体引用，覆盖图片、视频、音频、封面与媒体链接。"
    )
    parser.add_argument(
        "targets",
        nargs="*",
        help="需要扫描的目录或 Markdown 文件，默认扫描 docs/zh/books。",
    )
    parser.add_argument(
        "--allow-nonzero",
        action="store_true",
        help="即使发现远程媒体也返回 0，适合纯统计场景。",
    )
    if args is None:
        args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    default_target = repo_root / "docs" / "zh" / "books"
    targets = [Path(item).resolve() for item in args.targets] or [default_target]
    markdown_files = iter_markdown_files(targets)

    matched_files: list[tuple[Path, int]] = []
    total_occurrences = 0

    for path in markdown_files:
        content = path.read_text(encoding="utf-8", errors="ignore")
        count = len(REMOTE_MEDIA_PATTERN.findall(content))
        if count <= 0:
            continue
        matched_files.append((path, count))
        total_occurrences += count

    print(f"scanned_files={len(markdown_files)}")
    print(f"files_with_remote_media={len(matched_files)}")
    print(f"remote_media_occurrences={total_occurrences}")

    for path, count in matched_files[:200]:
        print(f"{path} :: {count}")

    if matched_files and not args.allow_nonzero:
        sys.exit(1)


if __name__ == "__main__":
    main()

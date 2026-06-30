from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import time

from build_csdn_archives import (
    CATEGORIES,
    DEFAULT_RETRIES,
    DEFAULT_TIMEOUT_SEC,
    DOCS_DIR,
    localize_images_in_markdown,
    log_line,
    read_frontmatter_title,
    render_article_page,
)


REMOTE_IMAGE_PATTERN = re.compile(
    r"!\[[^\]]*\]\((?:https?://|//)[^)]+\)"
    r"|<img[^>]*\ssrc=['\"](?:https?://|//)[^'\"]+['\"]"
    r"|^\s*\[[^\]]+\]:\s*(?:https?://|//)\S+",
    re.IGNORECASE | re.MULTILINE,
)


def iter_markdown_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("index.md") if path.is_file())


def safe_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)


def parse_generated_article_page(content: str) -> tuple[object, str, str, str] | None:
    match = re.search(
        r'<ArchiveCopyPanel article-id="(?P<article_id>[^"]+)" />\n'
        r'<div class="gg-copy-payload" data-article-id="[^"]+">.*?</div>\n\n'
        r'(?P<body>[\s\S]*)\Z',
        content,
    )
    if not match:
        return None

    article_id = match.group("article_id")
    body = match.group("body")
    lines = body.splitlines()
    if len(lines) < 5:
        return None

    category_match = re.match(r"^> 分类：(.+?)\s{2,}$", lines[0].strip())
    original_match = re.match(r"^> 原始文件：`(.+)`\s{2,}$", lines[2].strip())
    if not category_match or not original_match:
        return None

    category_name = category_match.group(1).strip()
    category = next((item for item in CATEGORIES.values() if item.zh_name == category_name), None)
    if category is None:
        return None

    content_start = 0
    for idx, line in enumerate(lines):
        if not line.strip():
            content_start = idx + 1
            break

    article_content = "\n".join(lines[content_start:]).strip()
    return category, article_id, original_match.group(1).strip(), article_content


def localize_file(
    markdown_path: Path,
    *,
    timeout_sec: int,
    retries: int,
    purge_assets: bool,
) -> tuple[bool, int, int]:
    original = markdown_path.read_text(encoding="utf-8")
    if not REMOTE_IMAGE_PATTERN.search(original):
        return False, 0, 0

    assets_root = markdown_path.parent / "assets"
    if purge_assets and assets_root.exists():
        shutil.rmtree(assets_root)

    parsed_article = parse_generated_article_page(original)
    if parsed_article:
        category, article_id, original_name, article_content = parsed_article
        localized_content, downloaded_count, total_count = localize_images_in_markdown(
            article_content,
            assets_root,
            download=True,
            timeout_sec=timeout_sec,
            retries=retries,
        )
        title = read_frontmatter_title(markdown_path)
        rewritten = render_article_page(category, article_id, original_name, title, localized_content)
    else:
        rewritten, downloaded_count, total_count = localize_images_in_markdown(
            original,
            assets_root,
            download=True,
            timeout_sec=timeout_sec,
            retries=retries,
        )

    if rewritten != original:
        safe_write_text(markdown_path, rewritten)
        return True, downloaded_count, total_count

    return False, downloaded_count, total_count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="为现有 VitePress 页面执行图片本地化，并将远程引用改写为同级 assets 相对路径。"
    )
    parser.add_argument(
        "targets",
        nargs="*",
        help="需要处理的目录或 Markdown 文件，默认扫描 docs/zh/books。",
    )
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SEC)
    parser.add_argument("--retries", type=int, default=DEFAULT_RETRIES)
    parser.add_argument(
        "--purge-assets",
        action="store_true",
        help="处理前清理目标页面同级 assets 目录，确保输出整洁。",
    )
    args = parser.parse_args()

    targets = [Path(target).resolve() for target in args.targets] or [DOCS_DIR / "zh" / "books"]
    markdown_files: list[Path] = []
    for target in targets:
        if target.is_file():
            markdown_files.append(target)
        elif target.is_dir():
            markdown_files.extend(iter_markdown_files(target))

    unique_files = sorted({path.resolve() for path in markdown_files})
    started_at = time.time()
    scanned_count = 0
    changed_count = 0
    total_remote_refs = 0
    total_downloaded = 0

    log_line("=== 现有页面图片本地化开始 ===")
    for idx, markdown_path in enumerate(unique_files, start=1):
        scanned_count += 1
        changed, downloaded_count, total_count = localize_file(
            markdown_path,
            timeout_sec=args.timeout,
            retries=args.retries,
            purge_assets=args.purge_assets,
        )
        total_remote_refs += total_count
        total_downloaded += downloaded_count
        if changed:
            changed_count += 1
            message = (
                f"[{idx}/{len(unique_files)}] 已本地化: {markdown_path} | "
                f"下载 {downloaded_count}/{total_count}"
            )
            print(message)
            log_line(message)

    elapsed = time.time() - started_at
    summary = (
        f"扫描文件 {scanned_count} 个，改写页面 {changed_count} 个，"
        f"远程图片引用 {total_remote_refs} 个，成功下载 {total_downloaded} 个，"
        f"耗时 {elapsed:.1f}s"
    )
    print(summary)
    log_line(summary)
    log_line("=== 现有页面图片本地化结束 ===")


if __name__ == "__main__":
    main()

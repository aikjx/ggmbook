from __future__ import annotations

from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
import argparse
import hashlib
import mimetypes
from pathlib import Path
import re
import shutil
import time
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


DOCS_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = DOCS_DIR / "aa" / "CSDN博文备份"
ZH_BOOKS_DIR = DOCS_DIR / "zh" / "books"
EN_BOOKS_DIR = DOCS_DIR / "en" / "books"
LOG_PATH = DOCS_DIR / "books" / "archive_build.log"

DEFAULT_TIMEOUT_SEC = 20
DEFAULT_RETRIES = 2
DEFAULT_USER_AGENT = "ggbook-archive-bot/1.0"


@dataclass(frozen=True)
class Category:
    key: str
    zh_name: str
    en_name: str
    zh_route: str
    en_route: str
    zh_book_route: str
    en_book_route: str
    zh_description: str
    en_description: str
    keywords: tuple[str, ...]


CATEGORIES = {
    "math": Category(
        key="math",
        zh_name="全域数学",
        en_name="Universal Mathematics",
        zh_route="/zh/books/math/articles/",
        en_route="/en/books/articles/",
        zh_book_route="/zh/books/math/",
        en_book_route="/en/books/math/",
        zh_description="涵盖全域数学、统一场论、光速螺旋、物理与跨学科延展等内容。",
        en_description="Covers Universal Mathematics, unified field theory, speed-of-light spiral, physics, and cross-disciplinary topics.",
        keywords=(
            "全域数学",
            "统一场论",
            "光速螺旋",
            "vc",
            "引力",
            "电磁",
            "量子",
            "黑洞",
            "拓扑",
            "维度",
            "超球体",
            "人工场",
            "张祥前",
            "场计算机",
            "ai",
            "信息场",
            "经济",
            "金融",
            "密码",
            "哈希",
            "navier-stokes",
            "黎曼",
            "分形",
            "射影",
            "套娃",
            "算子",
            "泛函",
        ),
    ),
    "goldbach": Category(
        key="goldbach",
        zh_name="哥德巴赫猜想",
        en_name="Goldbach Conjecture",
        zh_route="/zh/books/goldbach/articles/",
        en_route="/en/books/articles/",
        zh_book_route="/zh/books/goldbach/",
        en_book_route="/en/books/goldbach/",
        zh_description="集中收录哥德巴赫猜想、孪生素数、素数网格与数论相关研究。",
        en_description="Collects Goldbach conjecture, twin primes, prime grids, and related number theory research.",
        keywords=(
            "哥德巴赫",
            "孪生素数",
            "素数",
            "质数",
            "数论",
            "解析数论",
            "平行素数",
            "离散解析数论",
        ),
    ),
    "shushu": Category(
        key="shushu",
        zh_name="数术工坊",
        en_name="Shushu Workshop",
        zh_route="/zh/books/shushu/articles/",
        en_route="/en/books/articles/",
        zh_book_route="/zh/books/shushu/",
        en_book_route="/en/books/shushu/",
        zh_description="收录易经、河图洛书、太极五行、道德经与传统数术方向文章。",
        en_description="Collects articles on Yijing, Hetu-Luoshu, Taiji-Wuxing, Daodejing, and traditional numerology.",
        keywords=(
            "数术",
            "易经",
            "河图洛书",
            "河图",
            "洛书",
            "太极",
            "五行",
            "八卦",
            "阴阳",
            "道德经",
            "佛教",
            "心经",
            "华夏",
        ),
    ),
    "course": Category(
        key="course",
        zh_name="文明进阶200讲",
        en_name="Civilization Course",
        zh_route="/zh/books/course/articles/",
        en_route="/en/books/articles/",
        zh_book_route="/zh/books/course/",
        en_book_route="/en/books/course/",
        zh_description="收录“全域数学 vs 传统数学：人类文明进阶200讲”系列及其通俗课程内容。",
        en_description="Collects the 'Universal Mathematics vs Traditional Mathematics: 200 Lectures' series and related course content.",
        keywords=(
            "全域数学vs传统数学",
            "人类文明进阶200讲",
            "第1讲",
            "第2讲",
            "第3讲",
            "第4讲",
            "第5讲",
            "第6讲",
            "第7讲",
            "第8讲",
            "第9讲",
            "第10讲",
            "第11讲",
            "第12讲",
            "第13讲",
            "第14讲",
            "第15讲",
            "第16讲",
            "第17讲",
            "第18讲",
            "第19讲",
            "第20讲",
            "第21讲",
            "第22讲",
            "第23讲",
            "第24讲",
            "第25讲",
            "第26讲",
            "第27讲",
            "第28讲",
            "第29讲",
            "小学通俗版",
            "初中",
        ),
    ),
}

PRIORITY = {"course": 0, "goldbach": 1, "shushu": 2, "math": 3}
ENCODINGS = ("utf-8", "utf-8-sig", "gbk", "gb2312", "big5", "utf-16")


class MarkdownArchiveParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.list_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag in {"p", "div", "section", "article", "blockquote"}:
            self.parts.append("\n\n")
        elif tag in {"br"}:
            self.parts.append("\n")
        elif tag in {"ul", "ol"}:
            self.parts.append("\n")
            self.list_depth += 1
        elif tag == "li":
            self.parts.append("\n- ")
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(tag[1])
            self.parts.append(f"\n\n{'#' * level} ")
        elif tag == "hr":
            self.parts.append("\n\n---\n\n")
        elif tag == "img":
            src = attrs_dict.get("src") or ""
            alt = attrs_dict.get("alt") or "image"
            if src:
                self.parts.append(f"\n\n![{alt}]({src})\n\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"p", "div", "section", "article", "blockquote"}:
            self.parts.append("\n\n")
        elif tag in {"ul", "ol"}:
            self.parts.append("\n")
            self.list_depth = max(0, self.list_depth - 1)
        elif tag == "li":
            self.parts.append("\n")
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append("\n\n")

    def handle_data(self, data: str) -> None:
        if data:
            self.parts.append(data)

    def handle_entityref(self, name: str) -> None:
        self.parts.append(unescape(f"&{name};"))

    def handle_charref(self, name: str) -> None:
        self.parts.append(unescape(f"&#{name};"))

    def get_markdown(self) -> str:
        return "".join(self.parts)


def read_text(path: Path) -> str:
    for encoding in ENCODINGS:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="ignore")


def extract_article_id(path: Path) -> str:
    match = re.search(r"-(\d+)$", path.stem)
    if match:
        return match.group(1)
    fallback = re.sub(r"[^0-9A-Za-z_-]+", "-", path.stem).strip("-")
    return fallback or "article"


def clean_title(path: Path) -> str:
    title = re.sub(r"-\d+$", "", path.stem)
    title = re.sub(r"\s+", " ", title).strip()
    return title


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def normalize_http_url(url: str) -> str:
    url = url.strip()
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("http://"):
        return "https://" + url[len("http://") :]
    return url


def is_http_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://") or url.startswith("//")


def classify_image_host(url: str) -> str:
    parsed = urlparse(normalize_http_url(url))
    netloc = (parsed.netloc or "").lower()
    if "csdnimg" in netloc or netloc.endswith("csdn.net") or "csdn" in netloc:
        return "csdnimg"
    return "external"


def guess_extension(url: str, content_type: str | None) -> str:
    parsed = urlparse(normalize_http_url(url))
    path = parsed.path or ""
    match = re.search(r"\.([A-Za-z0-9]{1,5})$", path)
    if match:
        ext = "." + match.group(1).lower()
        if ext in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}:
            return ".jpg" if ext == ".jpeg" else ext

    if content_type:
        mime = content_type.split(";")[0].strip().lower()
        ext = mimetypes.guess_extension(mime) or ""
        if ext in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}:
            return ".jpg" if ext == ".jpeg" else ext

    return ".png"


def safe_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_bytes(data)
    tmp_path.replace(path)


def log_line(message: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as fp:
        fp.write(message.rstrip() + "\n")


def fetch_image_bytes(url: str, *, timeout_sec: int, retries: int) -> tuple[bytes | None, str | None]:
    url = normalize_http_url(url)
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            req = Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
            with urlopen(req, timeout=timeout_sec) as resp:
                data = resp.read()
                content_type = resp.headers.get("Content-Type")
                if not data:
                    return None, content_type
                return data, content_type
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            last_error = exc
            time.sleep(0.6 * (attempt + 1))
    if last_error:
        print(f"图片拉取失败: {url} ({type(last_error).__name__})")
    return None, None


def download_image(url: str, dest_path: Path, *, timeout_sec: int, retries: int) -> bool:
    if dest_path.exists() and dest_path.stat().st_size > 0:
        return True
    data, _ = fetch_image_bytes(url, timeout_sec=timeout_sec, retries=retries)
    if not data:
        return False
    safe_write_bytes(dest_path, data)
    return True


def parse_markdown_image_url(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1].strip()
    raw = raw.strip('"').strip("'")
    parts = raw.split()
    return parts[0] if parts else raw


def localize_images_in_markdown(
    content: str,
    assets_root: Path,
    *,
    download: bool,
    timeout_sec: int,
    retries: int,
) -> tuple[str, int, int]:
    md_image_pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
    html_img_pattern = re.compile(r"(<img[^>]*?\ssrc=)(['\"])([^'\"]+)(\2)", re.IGNORECASE)
    md_ref_pattern = re.compile(r"(^\s*\[[^\]]+\]:\s*)(\S+)(.*$)", re.MULTILINE)
    url_map: dict[str, str] = {}
    downloaded_count = 0
    total_count = 0

    def build_local_ref(norm_url: str, *, prefer_content_type: str | None) -> str:
        nonlocal downloaded_count, total_count
        total_count += 1
        if not download:
            return norm_url

        data, content_type = fetch_image_bytes(norm_url, timeout_sec=timeout_sec, retries=retries)
        if not data:
            return norm_url

        host_group = classify_image_host(norm_url)
        ext = guess_extension(norm_url, content_type or prefer_content_type)
        ext_dir = ext.lstrip(".") or "bin"
        digest = hashlib.sha1(norm_url.encode("utf-8")).hexdigest()[:16]
        filename = f"{digest}{ext}"
        host_dir = assets_root / host_group / ext_dir
        host_dir.mkdir(parents=True, exist_ok=True)
        safe_write_bytes(host_dir / filename, data)
        downloaded_count += 1
        return f"./assets/{host_group}/{ext_dir}/{filename}"

    def get_rewritten_url(url: str) -> str:
        if not is_http_url(url):
            return url
        norm_url = normalize_http_url(url)
        if norm_url not in url_map:
            url_map[norm_url] = build_local_ref(norm_url, prefer_content_type=None)
        return url_map[norm_url]

    def replace_md_image(match: re.Match[str]) -> str:
        nonlocal downloaded_count, total_count
        alt_text = match.group(1)
        raw_target = match.group(2)
        url = parse_markdown_image_url(raw_target)
        rewritten_url = get_rewritten_url(url)
        if rewritten_url == url:
            return match.group(0)
        return f"![{alt_text}]({rewritten_url})"

    def replace_html_img(match: re.Match[str]) -> str:
        prefix = match.group(1)
        quote = match.group(2)
        src = match.group(3)
        suffix_quote = match.group(4)
        rewritten_url = get_rewritten_url(src)
        return f"{prefix}{quote}{rewritten_url}{suffix_quote}"

    def replace_md_ref(match: re.Match[str]) -> str:
        prefix = match.group(1)
        url = match.group(2)
        suffix = match.group(3)
        rewritten_url = get_rewritten_url(url)
        return f"{prefix}{rewritten_url}{suffix}"

    rewritten = md_image_pattern.sub(replace_md_image, content)
    rewritten = html_img_pattern.sub(replace_html_img, rewritten)
    rewritten = md_ref_pattern.sub(replace_md_ref, rewritten)
    return rewritten, downloaded_count, total_count


def sanitize_content(content: str) -> str:
    parser = MarkdownArchiveParser()
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    try:
        parser.feed(normalized)
        parser.close()
        text = parser.get_markdown()
    except Exception:
        text = normalized

    text = unescape(text)
    filtered_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.search(
            r"\\(boldsymbol|frac|dfrac|vec|mathcal|nabla|sum|prod|int|lim|min|max|cdot|to|ge|le|mid|otimes|cong|rho|Omega|partial|sim|ln|pi|infty|text)",
            stripped,
        ):
            continue
        filtered_lines.append(line)
    text = "\n".join(filtered_lines)
    text = text.replace("{", "&#123;").replace("}", "&#125;")
    text = re.sub(r"\n[ \t]+\n", "\n\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def score_category(title: str, sample: str, category: Category) -> int:
    title_lower = title.lower()
    sample_lower = sample.lower()
    score = 0
    for keyword in category.keywords:
        keyword_lower = keyword.lower()
        if keyword_lower in title_lower:
            score += 10
        elif keyword_lower in sample_lower:
            score += 3
    return score


def classify_article(title: str, content: str) -> str:
    sample = content[:4000]
    best_key = "math"
    best_score = -1
    for key, category in CATEGORIES.items():
        score = score_category(title, sample, category)
        if score > best_score:
            best_key = key
            best_score = score
            continue
        if score == best_score and PRIORITY[key] < PRIORITY[best_key]:
            best_key = key
    return best_key if best_score > 0 else "math"


def render_article_page(category: Category, article_id: str, original_name: str, title: str, content: str) -> str:
    return (
        "---\n"
        f"title: {yaml_quote(title)}\n"
        "---\n\n"
        f"> 分类：{category.zh_name}  \n"
        f"> 编号：`{article_id}`  \n"
        f"> 原始文件：`{original_name}`  \n"
        f"> 返回：[本书归档]({category.zh_route}) · [总入口](/zh/books/articles/)\n\n"
        f"{content.strip()}\n"
    )


def render_category_index(category: Category, articles: list[dict[str, str]]) -> str:
    lines = [
        f"# {category.zh_name}博文归档",
        "",
        f"已从 `docs/aa/CSDN博文备份` 自动分类收录，共 **{len(articles)}** 篇。",
        "",
        f"- [返回本书首页]({category.zh_book_route})",
        "- [返回总入口](/zh/books/articles/)",
        "",
        "## 说明",
        "",
        f"- {category.zh_description}",
        "- 文件按原始标题自动分类，正文保留原始 Markdown/HTML 内容，适合站内在线阅读。",
        "",
        "## 文章列表",
        "",
    ]
    for article in articles:
        lines.append(f"- [{article['title']}]({category.zh_route}{article['id']}/)")
    lines.append("")
    return "\n".join(lines)


def render_overview_zh(grouped: dict[str, list[dict[str, str]]], recent_articles: list[dict[str, str]]) -> str:
    total = sum(len(items) for items in grouped.values())
    lines = [
        "# CSDN博文归档",
        "",
        "已将 `docs/aa/CSDN博文备份` 自动分析并分流到不同书籍目录，可在站点内直接阅读。",
        "",
        "## 分类入口",
        "",
        "| 书籍 | 文章数 | 入口 |",
        "| --- | ---: | --- |",
    ]
    for key in ("math", "goldbach", "shushu", "course"):
        category = CATEGORIES[key]
        lines.append(f"| {category.zh_name} | {len(grouped[key])} | [进入归档]({category.zh_route}) |")
    lines.extend(
        [
            f"| **总计** | **{total}** | - |",
            "",
            "## 最新收录",
            "",
        ]
    )
    for article in recent_articles:
        lines.append(f"- [{article['title']}]({article['route']}) · {article['category_name']}")
    lines.extend(
        [
            "",
            "## 分类说明",
            "",
            "- 文明进阶200讲：优先识别“全域数学vs传统数学”“人类文明进阶200讲”“第X讲”等课程特征。",
            "- 哥德巴赫猜想：识别哥德巴赫、孪生素数、素数、质数、数论等关键词。",
            "- 数术工坊：识别易经、河图洛书、太极、五行、道德经、佛教等传统数术关键词。",
            "- 其余默认归入全域数学。",
            "",
        ]
    )
    return "\n".join(lines)


def render_overview_en(grouped: dict[str, list[dict[str, str]]]) -> str:
    total = sum(len(items) for items in grouped.values())
    lines = [
        "# CSDN Blog Archive",
        "",
        "The articles from `docs/aa/CSDN博文备份` are automatically classified into book-specific Chinese archives for online reading.",
        "",
        "## Archive Entry Points",
        "",
        "| Book | Articles | Archive |",
        "| --- | ---: | --- |",
    ]
    for key in ("math", "goldbach", "shushu", "course"):
        category = CATEGORIES[key]
        lines.append(f"| {category.en_name} | {len(grouped[key])} | [Open Chinese Archive]({category.zh_route}) |")
    lines.extend(
        [
            f"| **Total** | **{total}** | - |",
            "",
            "## Notes",
            "",
            "- These archived posts are Chinese-language originals from the CSDN backup directory.",
            "- Classification is based on filename and article content keywords.",
            "- Use the links above to browse the book-specific archives directly.",
            "",
        ]
    )
    return "\n".join(lines)


def ensure_archive_dirs(*, purge: bool) -> None:
    for key in CATEGORIES:
        archive_dir = ZH_BOOKS_DIR / key / "articles"
        if purge and archive_dir.exists():
            for child in archive_dir.iterdir():
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    child.unlink()
        archive_dir.mkdir(parents=True, exist_ok=True)

    (ZH_BOOKS_DIR / "articles").mkdir(parents=True, exist_ok=True)
    (EN_BOOKS_DIR / "articles").mkdir(parents=True, exist_ok=True)


def read_frontmatter_title(md_path: Path) -> str:
    try:
        lines = md_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return md_path.parent.name
    if not lines or lines[0].strip() != "---":
        return md_path.parent.name
    for i in range(1, min(len(lines), 30)):
        line = lines[i].strip()
        if line == "---":
            break
        match = re.match(r'^title:\s*"(.*)"\s*$', line)
        if match:
            return match.group(1).strip() or md_path.parent.name
        match = re.match(r"^title:\s*(.*)\s*$", line)
        if match:
            raw = match.group(1).strip().strip('"').strip("'")
            if raw:
                return raw
    return md_path.parent.name


def build_indexes_from_generated() -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {key: [] for key in CATEGORIES}
    for key, category in CATEGORIES.items():
        archive_dir = ZH_BOOKS_DIR / key / "articles"
        if not archive_dir.exists():
            continue
        for child in archive_dir.iterdir():
            if not child.is_dir():
                continue
            article_id = child.name
            index_md = child / "index.md"
            if not index_md.exists():
                continue
            grouped[key].append(
                {
                    "id": article_id,
                    "title": read_frontmatter_title(index_md),
                    "route": f"{category.zh_route}{article_id}/",
                    "category_name": category.zh_name,
                }
            )
        grouped[key].sort(key=lambda item: int(item["id"]) if item["id"].isdigit() else 0, reverse=True)
        (archive_dir / "index.md").write_text(render_category_index(category, grouped[key]), encoding="utf-8")

    recent_articles: list[dict[str, str]] = []
    for items in grouped.values():
        recent_articles.extend(items)
    recent_articles.sort(key=lambda item: int(item["id"]) if item["id"].isdigit() else 0, reverse=True)

    (ZH_BOOKS_DIR / "articles" / "index.md").write_text(
        render_overview_zh(grouped, recent_articles[:20]),
        encoding="utf-8",
    )
    (EN_BOOKS_DIR / "articles" / "index.md").write_text(
        render_overview_en(grouped),
        encoding="utf-8",
    )
    return grouped


def build_archives(
    *,
    limit: int | None,
    only_ids: list[str],
    download_images: bool,
    purge: bool,
    progress_every: int,
) -> None:
    if purge:
        LOG_PATH.write_text("", encoding="utf-8")

    ensure_archive_dirs(purge=purge)

    source_files: list[Path]
    if only_ids:
        selected: list[Path] = []
        for article_id in only_ids:
            selected.extend(sorted(SOURCE_DIR.glob(f"*-{article_id}.md")))
        seen: set[Path] = set()
        source_files = []
        for file_path in selected:
            if file_path not in seen:
                source_files.append(file_path)
                seen.add(file_path)
    else:
        source_files = sorted(SOURCE_DIR.glob("*.md"))
        if limit is not None:
            source_files = source_files[:limit]

    total_images = 0
    downloaded_images = 0

    for idx, path in enumerate(source_files, start=1):
        title = clean_title(path)
        raw_content = read_text(path).strip()
        content = sanitize_content(raw_content)
        category_key = classify_article(title, content)
        category = CATEGORIES[category_key]
        article_id = extract_article_id(path)
        article_dir = ZH_BOOKS_DIR / category_key / "articles" / article_id
        if article_dir.exists():
            shutil.rmtree(article_dir)
        assets_root = article_dir / "assets"
        localized, dl_count, img_count = localize_images_in_markdown(
            content,
            assets_root,
            download=download_images,
            timeout_sec=DEFAULT_TIMEOUT_SEC,
            retries=DEFAULT_RETRIES,
        )
        total_images += img_count
        downloaded_images += dl_count
        article_dir.mkdir(parents=True, exist_ok=True)
        (article_dir / "index.md").write_text(
            render_article_page(category, article_id, path.name, title, localized),
            encoding="utf-8",
        )
        if progress_every > 0 and idx % progress_every == 0:
            log_line(
                f"进度 {idx}/{len(source_files)}: {path.name} | 图片 {downloaded_images}/{total_images}"
            )

    grouped = build_indexes_from_generated()
    total = sum(len(items) for items in grouped.values())
    log_line(f"已生成 {total} 篇归档文章")
    for key in ("math", "goldbach", "shushu", "course"):
        log_line(f"  {key}: {len(grouped[key])} 篇")
    log_line(f"图片引用: {total_images}，已下载: {downloaded_images}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--only-id", action="append", default=[])
    parser.add_argument("--no-download-images", action="store_true")
    parser.add_argument("--purge", action="store_true")
    parser.add_argument("--progress-every", type=int, default=25)
    args = parser.parse_args()
    build_archives(
        limit=args.limit,
        only_ids=args.only_id,
        download_images=not args.no_download_images,
        purge=args.purge,
        progress_every=args.progress_every,
    )
